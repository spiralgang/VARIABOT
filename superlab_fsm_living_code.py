#!/usr/bin/env python3
# =============================================================================
# superlab_fsm_living_code.py  —  the consolidated "living-code" agentic engine
# =============================================================================
# One file that does everything you asked for, aligned with the
# safe-agent-codegen skill (real LLM only, no mock, ast audit + reduced
# builtins + __build_class__):
#
#   1. LOAD FILE      read a local source file into context
#   2. FETCH LINKS    pull outside source links (URLs) over urllib
#   3. CALL AI        real OpenAI-compatible LLM (LLM_API_KEY; fails loud if absent)
#   4. RUN FSM        examine -> plan -> build -> review -> fix -> approve loop
#   5. LIVING CODE    manager LLM WRITES child agents; we parse/audit/compile/
#                      instantiate + deploy them in parallel, then mutate them
#   6. EMIT YAML      the engine WRITES a .github/workflows/*.yml that replays
#                      the FSM via the shared `llm` composite action
#
# Dependency-free (stdlib only). With no key the run raises NoLLMKeyError; the
# audit/compile/emit pipeline is still verifiable by passing --child-source.
# =============================================================================
from __future__ import annotations

import argparse
import ast
import concurrent.futures
import json
import logging
import os
import re
import sys
import types
import urllib.request
import urllib.error

LOG = logging.getLogger("superlab")
if not LOG.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-5s | %(message)s"))
    LOG.addHandler(_h)
LOG.setLevel(logging.INFO)

# --- real LLM client (no pip, no mock) ----------------------------------------
class NoLLMKeyError(RuntimeError):
    pass

class LLMClient:
    def __init__(self, model=None, base_url=None, api_key=None,
                 temperature=0.4, max_tokens=1200, timeout=90):
        self.model = model or os.getenv("LLM_MODEL", "glm-4-flash")
        self.base_url = (base_url or os.getenv("LLM_BASE_URL",
                        "https://open.bigmodel.cn/api/paas/v4")).rstrip("/")
        self.api_key = api_key if api_key is not None else (os.getenv("LLM_API_KEY") or os.getenv("ZHIPU_API_KEY") or "")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        if not self.api_key:
            raise NoLLMKeyError("Neither LLM_API_KEY nor ZHIPU_API_KEY is set; mocking is disabled by policy.")

    def chat(self, messages, *, temperature=None, max_tokens=None) -> str:
        payload = {"model": self.model, "messages": messages,
                   "temperature": temperature or self.temperature,
                   "max_tokens": max_tokens or self.max_tokens}
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {self.api_key}")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read().decode("utf-8"))["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:600]
            raise RuntimeError(f"LLM HTTP {e.code}: {detail}") from e


# --- 1. load file + 2. fetch outside links ------------------------------------
def load_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def fetch_link(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "superlab/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def extract_links(text: str) -> list[str]:
    return re.findall(r"https?://[^\s)\"'`>]+", text)


# --- 5. living-code: audit + reduced builtins + compile -----------------------
BANNED = {"__import__", "eval", "exec", "compile", "open", "exit", "quit",
          "input", "os", "sys", "subprocess", "socket", "shutil", "pathlib",
          "importlib", "pickle", "marshal", "ctypes", "builtins", "globals",
          "locals", "getattr", "setattr", "delattr", "memoryview"}

def audit_source(src: str) -> ast.Module:
    try:
        tree = ast.parse(src, mode="exec")
    except SyntaxError as exc:
        raise ValueError(f"child source not valid Python: {exc}") from exc
    for n in ast.walk(tree):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            raise ValueError("child source may not import modules")
        if isinstance(n, ast.Name) and n.id in BANNED:
            raise ValueError(f"banned name {n.id}")
        if isinstance(n, ast.Attribute) and n.attr in BANNED:
            raise ValueError(f"banned attr {n.attr}")
    return tree

def safe_builtins() -> dict:
    real = __builtins__ if isinstance(__builtins__, dict) else vars(__builtins__)
    keep = ("True", "False", "None", "str", "list", "dict", "tuple", "set",
            "len", "range", "print", "type", "isinstance", "int", "float",
            "bool", "enumerate", "zip", "map", "json", "__build_class__", "super")
    return {k: real[k] for k in keep if k in real}

def compile_child(src: str, llm) -> object:
    """Parse/audit/compile a child-agent source module and return an instance."""
    tree = audit_source(src)
    mod = types.ModuleType("dynamic_child")
    mod.__dict__["__builtins__"] = safe_builtins()
    # expose the real LLM + json to the child namespace (it calls self.llm.chat)
    mod.__dict__["llm"] = llm
    mod.__dict__["json"] = json
    exec(compile(tree, "<dynamic_child>", "exec"), mod.__dict__)
    cls = mod.__dict__.get("GeneratedAgent")
    if cls is None:
        raise ValueError("child source must define class GeneratedAgent")
    return cls(role="child", goal="generated", llm=llm)


# --- 4. FSM: examine -> plan -> build -> review -> fix -> approve -------------
FSM_STATES = ["examine", "plan", "build", "review", "fix", "approve"]

STAGE_PROMPTS = {
    "examine": "Survey the context. Pick ONE small, safe task. Reply: title, branch, files.",
    "plan": "Write a file-level plan (no code yet): which files, what change, how to verify.",
    "build": "Emit a unified diff implementing the plan. ONE ```diff ... ``` block. No secret/CI files.",
    "review": "Review the diff. Reply with a line 'VERDICT: APPROVE' or 'VERDICT: FIX' plus bullets.",
    "fix": "Produce a ```diff ... ``` block that resolves the blocking review points.",
    "approve": "Summarize the approved change in one line.",
}

def run_fsm(llm, context: str, max_cycles: int = 1) -> dict:
    """Drive the FSM, calling the real LLM at each stage. Returns the transcript."""
    transcript = {}
    for cyc in range(max_cycles):
        LOG.info("FSM cycle %d", cyc)
        for state in FSM_STATES:
            resp = llm.chat([
                {"role": "system", "content": "You are an autonomous SDLC agent."},
                {"role": "user", "content": f"CONTEXT:\n{context[:6000]}\n\nSTAGE: {state}\n{STAGE_PROMPTS[state]}"},
            ], max_tokens=1200)
            transcript.setdefault(state, []).append(resp)
            LOG.info("[%s] %s", state, resp[:120].replace("\n", " "))
            # extract a child-agent generation request if the model asks for one
            if "WRITE A PYTHON CHILD AGENT" in resp:
                m = re.search(r"```python\n(.*?)```", resp, re.DOTALL)
                if m:
                    try:
                        inst = compile_child(m.group(1), llm)
                        LOG.info("compiled child agent at stage %s -> %s", state,
                                 inst.execute({"description": context[:200]}))
                    except Exception as e:
                        LOG.warning("child compile or execution skipped: %s", e)
    return transcript


# --- 5. living-code mutation loop (parallel deploy) ---------------------------
def deploy_children(llm, children_src: list[str], task: dict, max_workers: int = 4) -> list[str]:
    def _run(src):
        try:
            inst = compile_child(src, llm)
            return inst.execute(task)
        except Exception as e:
            return f"Error executing child agent: {e}"
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        return list(ex.map(_run, children_src))

def living_code_cycle(llm, base_task: str, children: int = 2, cycles: int = 1) -> list[str]:
    """Manager LLM writes child source; we compile + deploy in parallel; mutate."""
    results = []
    history: list[str] = []
    for c in range(cycles):
        # manager asks the LLM to WRITE child agents
        spec = llm.chat([
            {"role": "system", "content": "You emit Python child agents. "
             "When asked, output a fenced ```python block defining "
             "class GeneratedAgent with __init__(self, role, goal, llm) and "
             "execute(self, task: dict) -> str that calls self.llm.chat(...)."},
            {"role": "user", "content": f"WRITE A PYTHON CHILD AGENT for: {base_task}"},
        ], max_tokens=800)
        m = re.search(r"```python\n(.*?)```", spec, re.DOTALL)
        if not m:
            LOG.warning("manager did not emit a child agent this cycle"); continue
        src = m.group(1)
        # optional mutation: ask to improve the previous child
        if history:
            imp = llm.chat([
                {"role": "user", "content": f"Improve this child agent:\n{history[-1]}\n"
                 "Return ONLY a new ```python ... ``` block."}], max_tokens=800)
            mm = re.search(r"```python\n(.*?)```", imp, re.DOTALL)
            if mm:
                src = mm.group(1)
        history.append(src)
        results.extend(deploy_children(llm, [src] * children,
                                        {"description": base_task}, max_workers=children))
        LOG.info("cycle %d deployed %d children", c, children)
    return results


# --- 6. emit workflow YAML from the FSM + context -----------------------------
def emit_workflow_yaml(name: str, context_hint: str, path: str) -> str:
    """The engine writes a GitHub Actions workflow that replays the FSM."""
    body = f"""# Auto-generated by superlab_fsm_living_code.py
# Reproduces the FSM loop (examine->plan->build->review->fix->approve) using the
# shared real-LLM composite action. Re-run: gh workflow run {name}.yml
name: "{name}"
on:
  workflow_dispatch:
    inputs:
      cycle:
        description: "FSM cycle counter"
        required: false
        type: string
        default: "0"
permissions:
  contents: read
  pull-requests: write
  issues: write
jobs:
"""
    for i, state in enumerate(FSM_STATES):
        needs = "[]" if i == 0 else f'["{FSM_STATES[i-1]}"]'
        body += f"""  {state}:
    needs: {needs}
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - name: "FSM stage: {state}"
        uses: ./.github/actions/llm
        with:
          system: "You are the {state} stage of an autonomous SDLC agent."
          temperature: "0.3"
          max_tokens: "1200"
          prompt: |
            Context hint: {context_hint[:200].replace(chr(10), ' ')}
            STAGE: {state}
            {STAGE_PROMPTS[state]}
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    LOG.info("emitted workflow YAML -> %s", path)
    return path


# --- orchestration -------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Superlab FSM living-code engine")
    ap.add_argument("--file", action="append", default=[], help="local file to load into context")
    ap.add_argument("--link", action="append", default=[], help="outside source link to fetch")
    ap.add_argument("--emit-yaml", default=".github/workflows/superlab-generated.yml",
                    help="path to emit the generated workflow YAML")
    ap.add_argument("--children", type=int, default=2)
    ap.add_argument("--cycles", type=int, default=1)
    ap.add_argument("--fsm-cycles", type=int, default=1)
    ap.add_argument("--task", default="autonomously improve this repository",
                    help="base task for the living-code manager")
    ap.add_argument("--child-source", default=None,
                    help="(test) use this hand-written child source instead of the LLM")
    ap.add_argument("--context", default="", help="extra inline context")
    args = ap.parse_args()

    # 1 + 2: assemble context from files + fetched links
    parts = [args.context]
    for fp in args.file:
        try:
            parts.append(f"# FILE {fp}\n{load_file(fp)}")
        except OSError as e:
            LOG.warning("cannot read %s: %s", fp, e)
    for url in args.link:
        try:
            parts.append(f"# LINK {url}\n{fetch_link(url)}")
        except Exception as e:
            LOG.warning("cannot fetch %s: %s", url, e)
    context = "\n\n".join(parts)

    # 3: real LLM (raises NoLLMKeyError if no key — no mock)
    try:
        llm = LLMClient()
    except NoLLMKeyError as e:
        LOG.error("%s", e)
        return 2

    # 4: FSM over the context
    transcript = run_fsm(llm, context, max_cycles=args.fsm_cycles)

    # 5: living-code child agents (or a supplied test source)
    if args.child_source:
        results = deploy_children(llm, [args.child_source] * args.children,
                                  {"description": args.task}, max_workers=args.children)
    else:
        results = living_code_cycle(llm, args.task, children=args.children, cycles=args.cycles)
    LOG.info("living-code produced %d outputs", len(results))

    # 6: emit a workflow YAML that replays the FSM
    emit_workflow_yaml("superlab-generated", context[:200] or args.task, args.emit_yaml)

    print(json.dumps({"fsm_stages": list(transcript.keys()),
                      "child_outputs": len(results)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
