"""
Test suite for VariaCopilot Mini-Grok Framework
Validates the 30-task orchestration system functionality
"""

import pytest
import json
import subprocess
import sys
import os
from pathlib import Path

# Add the scripts directory to the path for direct imports
SCRIPT_PATH = Path(__file__).parent / "android_rooting" / "scripts" / "varia_copilot.py"


def run_varia_copilot(args):
    """Helper function to run varia_copilot.py with given arguments"""
    cmd = [sys.executable, str(SCRIPT_PATH)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result


def test_help_functionality():
    """Test that help message is displayed correctly"""
    result = run_varia_copilot(["--help"])
    assert result.returncode == 0
    assert "VariaCopilot: Mini-Grok for VARIABOT" in result.stdout
    assert "--task" in result.stdout
    assert "--json" in result.stdout
    assert "--daemon" in result.stdout


def test_list_tasks():
    """Test listing all available tasks"""
    result = run_varia_copilot(["--list"])
    assert result.returncode == 0
    assert "Available VariaCopilot Tasks:" in result.stdout
    assert "Communicate Effectively:" in result.stdout
    assert "root_health" in result.stdout


def test_list_tasks_json():
    """Test listing tasks in JSON format"""
    result = run_varia_copilot(["--list", "--json"])
    assert result.returncode == 0
    
    data = json.loads(result.stdout)
    assert "available_tasks" in data
    assert len(data["available_tasks"]) == 31  # 30 + root_health
    assert "root_health" in data["available_tasks"]
    assert "create_diagram" in data["available_tasks"]


def test_root_health_task():
    """Test the root_health integration task"""
    result = run_varia_copilot(["--task", "root_health", "--json"])
    assert result.returncode == 0
    
    # Should output valid JSON
    data = json.loads(result.stdout)
    assert "status" in data or "root_status" in data


def test_create_diagram_task():
    """Test the create_diagram task"""
    result = run_varia_copilot(["--task", "create_diagram"])
    assert result.returncode == 0
    assert "Termux Install" in result.stdout
    assert "graph TD" in result.stdout


def test_streamlit_config_task():
    """Test the streamlit_config task"""
    result = run_varia_copilot(["--task", "streamlit_config"])
    assert result.returncode == 0
    assert "import streamlit as st" in result.stdout
    assert "VARIA Chat" in result.stdout


def test_unit_tests_task():
    """Test the unit_tests generation task"""
    result = run_varia_copilot(["--task", "unit_tests"])
    assert result.returncode == 0
    assert "import pytest" in result.stdout
    assert "test_root_detect" in result.stdout


def test_secure_repo_task():
    """Test the secure_repo .gitignore generation"""
    result = run_varia_copilot(["--task", "secure_repo"])
    assert result.returncode == 0
    assert "*.token" in result.stdout
    assert "# VARIA Security" in result.stdout


def test_explore_features_with_args():
    """Test explore_features task with arguments"""
    result = run_varia_copilot(["--task", "explore_features", "--args", "partial", "--json"])
    assert result.returncode == 0
    
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) > 0


def test_invalid_task():
    """Test handling of invalid task names"""
    result = run_varia_copilot(["--task", "nonexistent_task"])
    assert result.returncode == 0  # Should not crash
    assert result.stdout.strip() == "null" or "error" in result.stderr.lower()


def test_output_files_generated():
    """Test that output files are created in the correct location"""
    # Run a task that generates files
    result = run_varia_copilot(["--task", "create_diagram"])
    assert result.returncode == 0
    
    # Check if output file exists
    output_file = Path("/tmp/varia_output/root_flow.mmd")
    assert output_file.exists()
    
    # Check content
    content = output_file.read_text()
    assert "graph TD" in content
    assert "Termux Install" in content


def test_scan_vulns_task():
    """Test the security vulnerability scanning task"""
    result = run_varia_copilot(["--task", "scan_vulns"])
    assert result.returncode == 0
    assert "scan_secrets" in result.stdout
    assert "import re" in result.stdout


@pytest.mark.parametrize("task_name", [
    "extract_issues", "synthesize_research", "generate_table",
    "debug_json", "handle_api_retries", "extract_dmesg",
    "analyze_feedback", "improve_readability",
    "fix_lint", "optimize_performance", "singleton_bot",
    "doc_legacy", "explain_algorithm", "sync_docs",
    "mock_objects", "e2e_tests", "dependabot"
])
def test_individual_tasks(task_name):
    """Test that individual tasks execute without crashing"""
    result = run_varia_copilot(["--task", task_name])
    assert result.returncode == 0
    # Task should complete and output something
    assert len(result.stdout) > 0 or len(result.stderr) > 0


def test_logging_functionality():
    """Test that logging is working"""
    # Run a task and check if log file is created
    result = run_varia_copilot(["--task", "create_diagram"])
    assert result.returncode == 0
    
    log_file = Path("/tmp/varia_copilot.log")
    if log_file.exists():
        log_content = log_file.read_text()
        assert "INFO" in log_content
        assert "create_diagram" in log_content


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])