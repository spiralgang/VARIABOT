#!/usr/bin/env python3
"""Pick the first working free/OpenAI-compatible LLM provider from available env secrets.

Candidates (in order): custom LLM_BASE_URL/LLM_API_KEY, Zhipu GLM-4-flash (free),
NVIDIA NIM (free tier). Prints <PREFIX>BASE_URL/API_KEY/MODEL lines (default prefix LLM_RESOLVED_)
suitable for >> "$GITHUB_ENV" (a distinct name, since workflow env would win over GITHUB_ENV).
Exit 1 if none respond.
"""
import json, os, sys, urllib.request, urllib.error

ZHIPU = "https://open.bigmodel.cn/api/paas/v4"
NVIDIA = "https://integrate.api.nvidia.com/v1"

def candidates():
    e = os.environ.get
    seen = set()
    for base, key, model in [
        (e("LLM_BASE_URL") or ZHIPU, e("LLM_API_KEY"), e("LLM_MODEL") or "glm-4-flash"),
        (ZHIPU, e("ZHIPU_API_KEY"), "glm-4-flash"),
        (ZHIPU, e("LLM_API_KEY"), "glm-4-flash"),
        (NVIDIA, e("NVIDIA_API_KEY"), "meta/llama-3.3-70b-instruct"),
    ]:
        if key and (base, key) not in seen:
            seen.add((base, key)); yield base.rstrip("/"), key, model

def probe(base, key, model):
    body = json.dumps({"model": model, "max_tokens": 4,
                       "messages": [{"role": "user", "content": "ping"}]}).encode()
    req = urllib.request.Request(base + "/chat/completions", data=body, method="POST",
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return "choices" in json.loads(r.read().decode())
    except Exception as ex:
        print(f"provider {base} ({model}) unavailable: {str(ex)[:120]}", file=sys.stderr)
        return False

def main():
    for base, key, model in candidates():
        if probe(base, key, model):
            print(f"::add-mask::{key}", file=sys.stderr)
            p = sys.argv[1] if len(sys.argv) > 1 else "LLM_RESOLVED_"
            print(f"{p}BASE_URL={base}\n{p}API_KEY={key}\n{p}MODEL={model}")
            print(f"using LLM provider {base} model {model}", file=sys.stderr)
            return 0
    print("::error::No working LLM provider (checked LLM_*, ZHIPU_API_KEY, NVIDIA_API_KEY).", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(main())
