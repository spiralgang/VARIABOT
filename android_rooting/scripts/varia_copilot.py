#!/usr/bin/env python3
"""
VariaCopilot: Mini-Grok for VARIABOT - Orchestrates 30 pimped Copilot tasks.
Root probes, AI chat hooks, security scans, doc syncs, all Termux-native.
Usage: ./varia_copilot.py --task [task_name] [--json] [--daemon]
"""

import os
import sys
import json
import time
import subprocess
import argparse
import logging
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

# Logging: Audit trail, VARIABOT-style
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/varia_copilot.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class VariaCopilot:
    def __init__(self, daemon=False):
        self.daemon = daemon
        self.hf_token = os.getenv("HF_TOKEN", "")
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        
        # Use /tmp for broader compatibility instead of hardcoded Termux paths
        self.output_dir = "/tmp/varia_output"
        Path(self.output_dir).mkdir(exist_ok=True)
        
        self.state = {
            "last_task": None,
            "errors": [],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "daemon": daemon
        }

    def run_command(self, cmd: str, timeout: int = 10) -> tuple:
        """Execute shell cmd, return (stdout, stderr, rc)."""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except subprocess.TimeoutExpired:
            return "", "Timeout", 1

    def save_output(self, data: Any, filename: str) -> None:
        """Dump JSON to output dir."""
        filepath = Path(self.output_dir) / filename
        with open(filepath, "w") as f:
            if isinstance(data, (dict, list)):
                json.dump(data, f, indent=2)
            else:
                f.write(str(data))

    def queue_error_bot(self, error_data: Dict) -> None:
        """Inject errors to VARIABOT's error-bot."""
        error_file = f"{self.output_dir}/error_queue.json"
        self.save_output(error_data, "error_queue.json")
        
        # Try to use existing error-bot script
        error_bot_path = Path(__file__).parent / "error-bot"
        if error_bot_path.exists():
            self.run_command(f"python3 {error_bot_path} --inject {error_file}")
            logger.info("Errors queued to error-bot.")
        else:
            logger.warning("error-bot script not found, errors saved to file only")

    # Communicate Effectively (5 Tasks)
    def extract_issues(self, repo: str = "spiralgang/VARIABOT", keyword: str = "SELinux") -> List[Dict]:
        """Extract root-related issues from GitHub."""
        if not self.github_token:
            logger.warning("GITHUB_TOKEN not set, using mock data")
            issues = [{"title": f"Mock issue with {keyword}", "number": 1, "state": "open"}]
        else:
            try:
                headers = {"Authorization": f"token {self.github_token}"}
                response = requests.get(f"https://api.github.com/repos/{repo}/issues", headers=headers)
                issues = response.json() if response.status_code == 200 else []
                
                if isinstance(issues, list):
                    issues = [issue for issue in issues if keyword.lower() in issue.get("title", "").lower()]
                else:
                    issues = []
            except Exception as e:
                logger.error(f"Failed to fetch issues: {e}")
                issues = []
                
        self.state["issues"] = issues
        self.save_output(issues, "issues.json")
        return issues

    def synthesize_research(self, sources: List[Dict]) -> str:
        """Markdown summary for root research."""
        md = "# VARIA Research Synthesis\n\n"
        for src in sources:
            md += f"## {src.get('name', 'Unknown')}\n"
            md += f"- URL: {src.get('url', 'N/A')}\n"
            md += f"- Insight: {src.get('insight', 'No insight provided')}\n\n"
        
        self.save_output(md, "research.md")
        return md

    def create_diagram(self) -> str:
        """Mermaid diagram for root flow."""
        diagram = """
graph TD
    A[Termux Install] --> B[curl termux_setup.sh | bash]
    B --> C[Deps: pip install -r requirements.txt]
    C --> D[root-detect --json]
    D --> E{Enforcing?} -->|Yes| F[setenforce 0]
    E -->|No| G[Magisk Modules Load]
    G --> H[error-bot --daemon]
"""
        self.save_output(diagram, "root_flow.mmd")
        return diagram

    def generate_table(self, modules: List[Dict]) -> str:
        """Markdown table for Magisk modules."""
        table = "| Module | Version | Status | VARIA Hook |\n|--------|---------|--------|------------|\n"
        for mod in modules:
            table += f"| {mod.get('name', 'Unknown')} | {mod.get('version', 'N/A')} | {mod.get('status', 'Unknown')} | {mod.get('hook', 'None')} |\n"
        
        self.save_output(table, "modules.md")
        return table

    def streamlit_config(self) -> str:
        """Streamlit app for Qwen chat."""
        code = f"""
import streamlit as st
import requests
import json

# VariaCopilot Streamlit Integration
st.title("VARIA Chat")
st.sidebar.title("Mini-Grok Controls")

# Chat interface
prompt = st.text_input("Root query?", placeholder="Ask about Android rooting...")

if st.button("Query VARIA"):
    if prompt:
        # Mock HF API call - replace with actual implementation
        with st.spinner("Querying..."):
            response = {{"response": f"Mock response for: {{prompt}}"}}
            st.write("**Response:**")
            st.write(response.get("response", "No response"))
    else:
        st.warning("Please enter a query")

# Task runner
st.sidebar.subheader("Available Tasks")
task_list = [
    "root_health", "extract_issues", "debug_json", 
    "create_diagram", "generate_table"
]

selected_task = st.sidebar.selectbox("Select Task", task_list)
if st.sidebar.button("Run Task"):
    st.sidebar.success(f"Running {{selected_task}}...")
"""
        self.save_output(code, "st_varia_chat.py")
        return code

    # Debugging Code (4 Tasks)
    def debug_json(self, json_string: str) -> Optional[Dict]:
        """Fix invalid JSON from root-detect."""
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            # Try common fixes
            fixed = json_string.replace("'", '"').replace("True", "true").replace("False", "false")
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                self.state["errors"].append(f"JSON debug fail: {e}")
                self.queue_error_bot(self.state)
                return None

    def handle_api_retries(self, prompt: str, max_retries: int = 3) -> Optional[Dict]:
        """Retry HF API with backoff."""
        for i in range(max_retries):
            try:
                # Mock API call for demo - replace with actual HF API
                response = {"response": f"Mock response for: {prompt}"}
                return response
            except Exception as e:
                if i < max_retries - 1:
                    wait_time = 2 ** i
                    logger.warning(f"API retry {i+1} after {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    self.state["errors"].append("HF API retries exhausted")
                    self.queue_error_bot(self.state)
        return None

    def debug_su(self, cmd: str) -> str:
        """Debug su command failures."""
        out, err, rc = self.run_command(f"su -c '{cmd}'" if os.getuid() != 0 else cmd)
        if rc != 0:
            self.state["errors"].append(f"su fail: {err}")
            self.queue_error_bot(self.state)
        return out

    def extract_dmesg(self) -> str:
        """Extract SELinux denials.""" 
        out, _, _ = self.run_command("dmesg | grep -i avc | tail -20")
        if not out:
            out = "No SELinux denials found in dmesg"
        
        self.save_output({"denials": out}, "dmesg.json")
        return out

    # Functionality Analysis (3 Tasks)
    def explore_features(self, status: str) -> List[str]:
        """Explore root recovery options."""
        fixes = {
            "partial": ["Reboot + magisk --install", "SELinux permissive"],
            "no_root": ["Run android-root", "Check bootloader unlock"],
            "unrooted": ["Install Magisk", "Use exploit methods"]
        }
        result = fixes.get(status, ["Check root status", "Review logs"])
        self.save_output(result, "fixes.json")
        return result

    def analyze_feedback(self, issue_text: str) -> str:
        """Incorporate GitHub issue feedback."""
        if "slow streamlit" in issue_text.lower():
            return "Optimize Gradio_client with caching"
        elif "root fail" in issue_text.lower():
            return "Check Magisk installation and SELinux status"
        
        self.state["errors"].append("Feedback queued to error-bot")
        self.queue_error_bot(self.state)
        return "Feedback processed"

    def improve_readability(self, code_snippet: str) -> str:
        """Add docstrings and clean code."""
        return f'"""VARIA: Enhanced function with documentation"""\n{code_snippet}'

    # Refactoring Code (8 Tasks)
    def fix_lint(self) -> str:
        """Pre-commit hook for Black."""
        config = """
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        files: ^android_rooting/scripts/
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]
"""
        self.save_output(config, "pre-commit-config.yaml")
        return config

    def optimize_performance(self) -> str:
        """Optimize dmesg scan."""
        code = """def fast_dmesg():
    \"\"\"Optimized dmesg scanning for VARIA\"\"\"
    import subprocess
    return subprocess.getoutput("dmesg | tail -n 100 | grep -i avc")"""
        
        self.save_output(code, "fast_dmesg.py")
        return code

    def singleton_bot(self) -> str:
        """Singleton for error-bot."""
        code = """
class ErrorBot:
    \"\"\"Singleton Error Bot for VARIA\"\"\"
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def report_error(self, error):
        print(f"ErrorBot: {error}")
"""
        self.save_output(code, "singleton_bot.py")
        return code

    def decouple_data(self) -> str:
        """Decouple Magisk queries."""
        code = """
class MagiskRepo:
    \"\"\"Decoupled Magisk data access\"\"\"
    
    def get_modules(self):
        import subprocess
        return subprocess.getoutput("magisk --list 2>/dev/null || echo 'No modules'")
        
    def get_status(self):
        import subprocess
        return subprocess.getoutput("magisk --version 2>/dev/null || echo 'Not installed'")
"""
        self.save_output(code, "magisk_repo.py")
        return code

    def decouple_ui(self) -> str:
        """Separate Streamlit UI from logic."""
        code = """
# VARIA UI/Logic Separation

# core.py
def chat_response(prompt): 
    \"\"\"Core chat logic\"\"\"
    return f"Response to: {prompt}"

# st-chat.py  
def render_chat_ui():
    \"\"\"Streamlit UI rendering\"\"\"
    import streamlit as st
    prompt = st.text_input("Query:")
    if st.button("Submit"):
        response = chat_response(prompt)
        st.write(response)
"""
        self.save_output(code, "ui_logic.py")
        return code

    def cross_cutting(self) -> str:
        """Logging mixin."""
        code = """
import logging

class Logged:
    \"\"\"VARIA logging mixin\"\"\"
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def log(self, msg): 
        self.logger.info(f"VARIA: {msg}")

class RootChecker(Logged):
    \"\"\"Root checker with logging\"\"\"
    
    def check(self): 
        self.log("Probing root status...")
        return "unrooted"
"""
        self.save_output(code, "logging_mixin.py")
        return code

    def simplify_inheritance(self) -> str:
        """Flat bot hierarchy."""
        code = """
# VARIA Simplified Bot Hierarchy

class BaseBot: 
    \"\"\"Base bot functionality\"\"\"
    def __init__(self):
        self.status = "inactive"

class ErrorBot(BaseBot): 
    \"\"\"Error handling bot\"\"\"
    def handle_error(self, error):
        print(f"Handling: {error}")

class RootBot(BaseBot):
    \"\"\"Root operations bot\"\"\"
    def check_root(self):
        return "checking..."
"""
        self.save_output(code, "flat_bot.py")
        return code

    def fix_deadlocks(self) -> str:
        """SQLite transaction lock-proofing."""
        code = """
import sqlite3
from contextlib import contextmanager

@contextmanager
def db_txn(db_path):
    \"\"\"VARIA database transaction context\"\"\"
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
"""
        self.save_output(code, "db_txn.py")
        return code

    # Documenting Code (4 Tasks)
    def doc_legacy(self) -> str:
        """Document legacy su code."""
        code = """
def legacy_su(cmd):
    \"\"\"
    Legacy: Raw su exec, pre-VARIA queue. 
    
    DEPRECATED: Use root-detect or varia_copilot instead.
    This function directly executes su commands without
    error handling or recovery mechanisms.
    
    Args:
        cmd: Command to execute with su
        
    Returns:
        Exit code from os.system
    \"\"\"
    import os
    return os.system(f"su -c '{cmd}'")
"""
        self.save_output(code, "legacy_su.py")
        return code

    def explain_legacy(self) -> str:
        """Explain termux_setup.sh."""
        md = """
## Legacy Setup Explainer

### termux_setup.sh Analysis
- **Line 10**: `apt update` - Ensures Termux package freshness
- **Line 20**: `pip install -r requirements.txt` - VARIA dependencies installation
- **Line 30**: Package verification and integrity checks
- **Line 40**: Environment variable setup for Android compatibility

### Migration Path
- Old: Direct package installs
- New: VariaCopilot orchestrated setup with error recovery
"""
        self.save_output(md, "setup_explainer.md")
        return md

    def explain_algorithm(self) -> str:
        """Document Qwen streaming."""
        code = """
def stream_chat(prompt):
    \"\"\"
    Complex: Gradio chunks response, buffers for Termux low-mem.
    
    Algorithm:
    1. Send prompt to HuggingFace API
    2. Receive streaming response chunks
    3. Buffer chunks for memory efficiency
    4. Yield processed chunks to UI
    
    Memory optimization for Termux ARM64 environments.
    \"\"\"
    buffer = []
    chunk_size = 512  # Optimized for mobile
    
    # Mock streaming - replace with actual HF client
    response = f"Streaming response for: {prompt}"
    for i in range(0, len(response), chunk_size):
        chunk = response[i:i+chunk_size]
        buffer.append(chunk)
        if len(buffer) >= 3:  # Flush buffer
            yield ''.join(buffer)
            buffer = []
    
    if buffer:  # Final flush
        yield ''.join(buffer)
"""
        self.save_output(code, "stream_chat.py")
        return code

    def sync_docs(self) -> str:
        """Auto-update README."""
        code = """
def sync_readme():
    \"\"\"Auto-sync README with new VARIA features\"\"\"
    import os
    from datetime import datetime
    
    readme_path = "README.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    update_line = f"\\n## Latest Update: {timestamp}\\n"
    update_line += f"- Added: {__file__} - VariaCopilot Mini-Grok Framework\\n"
    update_line += "- 30 task orchestration system\\n"
    update_line += "- Termux-native Android rooting integration\\n"
    
    if os.path.exists(readme_path):
        with open(readme_path, "a") as f:
            f.write(update_line)
    
    return update_line
"""
        self.save_output(code, "sync_readme.py")
        return code

    # Testing Code (3 Tasks)
    def unit_tests(self) -> str:
        """Pytest for root-detect."""
        code = """
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@patch('subprocess.run')
def test_root_detect(mock_run):
    \"\"\"Test root detection functionality\"\"\"
    # Mock successful root detection
    mock_run.return_value = MagicMock(
        stdout="uid=0(root) gid=0(root)",
        stderr="",
        returncode=0
    )
    
    from android_rooting.core.root_detector import RootDetector
    detector = RootDetector()
    status, results = detector.detect_root_status()
    
    assert status.value in ["unrooted", "partial", "full"]
    assert "timestamp" in results

@patch('subprocess.run')  
def test_varia_copilot_tasks(mock_run):
    \"\"\"Test VariaCopilot task execution\"\"\"
    from varia_copilot import VariaCopilot
    
    copilot = VariaCopilot()
    result = copilot.create_diagram()
    
    assert "Termux Install" in result
    assert isinstance(result, str)
"""
        self.save_output(code, "test_root.py")
        return code

    def mock_objects(self) -> str:
        """Mock su for tests."""
        code = """
from unittest.mock import MagicMock, patch
import subprocess

# VARIA Test Mocks

class MockSU:
    \"\"\"Mock su command for testing\"\"\"
    
    @staticmethod
    def mock_su_success():
        return MagicMock(
            stdout="uid=0(root)",
            stderr="", 
            returncode=0
        )
    
    @staticmethod 
    def mock_su_failure():
        return MagicMock(
            stdout="",
            stderr="su: permission denied",
            returncode=1
        )

# Usage in tests:
# with patch('subprocess.run', return_value=MockSU.mock_su_success()):
#     result = test_function()
"""
        self.save_output(code, "mock_su.py")
        return code

    def e2e_tests(self) -> str:
        """Cypress for Streamlit."""
        code = """
// VARIA E2E Tests for Streamlit Interface

describe('VARIA Chat Interface', () => {
  beforeEach(() => {
    cy.visit('http://localhost:8501');
  });

  it('should load chat interface', () => {
    cy.contains('VARIA Chat');
    cy.get('input[type="text"]').should('be.visible');
  });

  it('should handle root status query', () => {
    cy.get('input[type="text"]').type('What is my root status?');
    cy.contains('Query VARIA').click();
    cy.contains('Response:', { timeout: 10000 });
  });

  it('should run tasks from sidebar', () => {
    cy.get('.sidebar').within(() => {
      cy.contains('Available Tasks');
      cy.get('select').select('root_health');
      cy.contains('Run Task').click();
      cy.contains('Running root_health...', { timeout: 5000 });
    });
  });
});
"""
        self.save_output(code, "cypress_varia.js")
        return code

    # Security Analysis (3 Tasks)
    def secure_repo(self) -> str:
        """Secure .gitignore."""
        config = """
# VARIA Security - Sensitive Files
*.token
*.key
hf_token.py
github_token.txt

# Runtime sensitive data
/tmp/error_queue.json
/tmp/varia_output/*.json
varia_copilot.log

# Environment files
.env
.env.local
termux_secrets.sh

# Temporary files
*.tmp
*.cache
__pycache__/
*.pyc

# Build artifacts
dist/
build/
*.egg-info/
"""
        self.save_output(config, "gitignore_secure")
        return config

    def dependabot(self) -> str:
        """Dependabot for deps."""
        config = """
version: 2
updates:
  - package-ecosystem: pip
    directory: /
    schedule:
      interval: daily
      time: "04:00"
    open-pull-requests-limit: 5
    reviewers:
      - "spiralgang"
    labels:
      - "dependencies"
      - "security"
    
  - package-ecosystem: pip  
    directory: /android_rooting
    schedule:
      interval: weekly
    allow:
      - dependency-type: security
    commit-message:
      prefix: "security"
      include: "scope"
"""
        self.save_output(config, "dependabot.yml")
        return config

    def scan_vulns(self) -> str:
        """Scan for hardcoded tokens."""
        code = '''import re
import os
from pathlib import Path

def scan_secrets(directory="."):
    """Scan for hardcoded secrets in VARIA codebase"""
    # Simple patterns to detect common secret patterns
    patterns = [
        "hf_token.*=.*hf_",
        "github_token.*=.*gh",
        "api_key.*=.*[A-Za-z0-9]{20,}",
        "password.*=.*[A-Za-z0-9]{8,}"
    ]
    
    vulnerabilities = []
    
    for root, dirs, files in os.walk(directory):
        # Skip sensitive directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
        
        for file in files:
            if file.endswith(('.py', '.sh', '.js', '.yml', '.yaml')):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    for line_num, line in enumerate(lines, 1):
                        for pattern in patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                vulnerabilities.append({
                                    'file': str(file_path),
                                    'line': line_num,
                                    'pattern': pattern,
                                    'match': line.strip()
                                })
                                
                except Exception as e:
                    print(f'Error scanning {file_path}: {e}')
    
    return vulnerabilities

if __name__ == "__main__":
    vulns = scan_secrets()
    if vulns:
        print("🚨 Security vulnerabilities found:")
        for vuln in vulns:
            print(f"  {vuln['file']}:{vuln['line']} - {vuln['match']}")
    else:
        print("✅ No hardcoded secrets found")
'''
        self.save_output(code, "scan_secrets.py")
        return code

    def root_health(self) -> Dict:
        """Reuse root_health.py logic from existing root_detector."""
        try:
            # Use the existing root_detector.py
            root_detector_path = Path(__file__).parent.parent / "core" / "root_detector.py"
            
            if root_detector_path.exists():
                out, err, rc = self.run_command(f"python3 {root_detector_path} --json")
                if rc == 0:
                    root_data = json.loads(out)
                    self.state.update(root_data)
                    return root_data
            
            # Fallback manual check
            health_data = {
                "timestamp": datetime.now().isoformat(),
                "root_status": "unknown",
                "magisk_version": None,
                "selinux_status": "unknown",
                "modules": [],
                "errors": [],
                "recovery_hints": []
            }
            
            # Basic root check
            out, err, rc = self.run_command("which su")
            if rc == 0:
                out, err, rc = self.run_command("su -c 'id -u'")
                if rc == 0 and "0" in out:
                    health_data["root_status"] = "full_root"
                else:
                    health_data["root_status"] = "partial_root"
            else:
                health_data["root_status"] = "no_root"
                health_data["errors"].append("su binary not found")
            
            # SELinux check
            out, err, rc = self.run_command("getenforce")
            if rc == 0:
                health_data["selinux_status"] = out.strip()
            
            self.state.update(health_data)
            self.save_output(health_data, "root_health.json")
            return health_data
            
        except Exception as e:
            error_data = {"error": str(e), "timestamp": datetime.now().isoformat()}
            self.state["errors"].append(str(e))
            return error_data

    def run_task(self, task_name: str, *args) -> Any:
        """Execute specified task."""
        tasks = {
            # Communicate Effectively (5 tasks)
            "extract_issues": self.extract_issues,
            "synthesize_research": self.synthesize_research, 
            "create_diagram": self.create_diagram,
            "generate_table": self.generate_table,
            "streamlit_config": self.streamlit_config,
            
            # Debugging Code (4 tasks)
            "debug_json": self.debug_json,
            "handle_api_retries": self.handle_api_retries,
            "debug_su": self.debug_su,
            "extract_dmesg": self.extract_dmesg,
            
            # Functionality Analysis (3 tasks)
            "explore_features": self.explore_features,
            "analyze_feedback": self.analyze_feedback,
            "improve_readability": self.improve_readability,
            
            # Refactoring Code (8 tasks)
            "fix_lint": self.fix_lint,
            "optimize_performance": self.optimize_performance,
            "singleton_bot": self.singleton_bot,
            "decouple_data": self.decouple_data,
            "decouple_ui": self.decouple_ui,
            "cross_cutting": self.cross_cutting,
            "simplify_inheritance": self.simplify_inheritance,
            "fix_deadlocks": self.fix_deadlocks,
            
            # Documenting Code (4 tasks)
            "doc_legacy": self.doc_legacy,
            "explain_legacy": self.explain_legacy,
            "explain_algorithm": self.explain_algorithm,
            "sync_docs": self.sync_docs,
            
            # Testing Code (3 tasks)
            "unit_tests": self.unit_tests,
            "mock_objects": self.mock_objects,
            "e2e_tests": self.e2e_tests,
            
            # Security Analysis (3 tasks)
            "secure_repo": self.secure_repo,
            "dependabot": self.dependabot,
            "scan_vulns": self.scan_vulns,
            
            # Root health from existing system
            "root_health": self.root_health,
        }
        
        task = tasks.get(task_name)
        if not task:
            self.state["errors"].append(f"Unknown task: {task_name}")
            self.queue_error_bot(self.state)
            return None
            
        try:
            result = task(*args)
            self.state["last_task"] = task_name
            self.save_output(self.state, "state.json")
            logger.info(f"Task '{task_name}' completed successfully")
            return result
        except Exception as e:
            error_msg = f"Task '{task_name}' failed: {str(e)}"
            self.state["errors"].append(error_msg)
            self.queue_error_bot(self.state)
            logger.error(error_msg)
            return None

    def daemon_loop(self, task_name: str, *args) -> None:
        """Run task in daemon mode."""
        logger.info(f"Starting daemon mode for task: {task_name}")
        
        while True:
            try:
                self.run_task(task_name, *args)
                logger.info(f"Task {task_name} cycle complete")
                time.sleep(60)  # 60 second intervals
            except KeyboardInterrupt:
                logger.info("Daemon stopped by user")
                break
            except Exception as e:
                logger.error(f"Daemon error: {e}")
                time.sleep(30)  # Shorter retry on error

    def list_tasks(self) -> List[str]:
        """List all available tasks."""
        return [
            # Communicate Effectively
            "extract_issues", "synthesize_research", "create_diagram", 
            "generate_table", "streamlit_config",
            
            # Debugging Code  
            "debug_json", "handle_api_retries", "debug_su", "extract_dmesg",
            
            # Functionality Analysis
            "explore_features", "analyze_feedback", "improve_readability",
            
            # Refactoring Code
            "fix_lint", "optimize_performance", "singleton_bot", "decouple_data",
            "decouple_ui", "cross_cutting", "simplify_inheritance", "fix_deadlocks",
            
            # Documenting Code
            "doc_legacy", "explain_legacy", "explain_algorithm", "sync_docs",
            
            # Testing Code
            "unit_tests", "mock_objects", "e2e_tests",
            
            # Security Analysis
            "secure_repo", "dependabot", "scan_vulns",
            
            # Core functionality
            "root_health"
        ]


def main():
    parser = argparse.ArgumentParser(description="VariaCopilot: Mini-Grok for VARIABOT")
    parser.add_argument("--task", help="Task to run (use --list to see all tasks)")
    parser.add_argument("--list", action="store_true", help="List all available tasks")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode")
    parser.add_argument("--args", nargs="*", help="Additional arguments for the task")
    
    args = parser.parse_args()

    copilot = VariaCopilot(daemon=args.daemon)
    
    if args.list:
        tasks = copilot.list_tasks()
        if args.json:
            print(json.dumps({"available_tasks": tasks}, indent=2))
        else:
            print("Available VariaCopilot Tasks:")
            print("=" * 40)
            categories = {
                "Communicate Effectively": tasks[0:5],
                "Debugging Code": tasks[5:9], 
                "Functionality Analysis": tasks[9:12],
                "Refactoring Code": tasks[12:20],
                "Documenting Code": tasks[20:24],
                "Testing Code": tasks[24:27],
                "Security Analysis": tasks[27:30],
                "Core Features": tasks[30:]
            }
            
            for category, category_tasks in categories.items():
                print(f"\n{category}:")
                for task in category_tasks:
                    print(f"  • {task}")
        return 0
    
    if not args.task:
        parser.print_help()
        return 1
        
    if args.daemon:
        logger.info(f"Starting daemon for task: {args.task}")
        copilot.daemon_loop(args.task, *(args.args or []))
    else:
        result = copilot.run_task(args.task, *(args.args or []))
        if args.json and result:
            print(json.dumps(result, indent=2, default=str))
        elif result and not args.json:
            if isinstance(result, (dict, list)):
                print(json.dumps(result, indent=2, default=str))
            else:
                print(result)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())