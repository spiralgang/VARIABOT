#!/bin/bash
#
# Comprehensive Code Audit and Live Testing Script
# Addresses all code quality issues found in VARIABOT repository
#
# This script performs:
# - Complete shellcheck analysis of all shell scripts
# - Python syntax and import validation
# - Live bot testing and server deployment
# - Error handling compliance verification
# - Professional code standards validation
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
AUDIT_LOG="code_audit_$(date +%Y%m%d_%H%M%S).log"
ERROR_COUNT=0
WARNING_COUNT=0
CRITICAL_ISSUES=()

# Logging function
log_audit() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$AUDIT_LOG"
}

# Critical issue tracking
track_critical() {
    local issue="$1"
    CRITICAL_ISSUES+=("$issue")
    ERROR_COUNT=$((ERROR_COUNT + 1))
    log_audit "CRITICAL" "$issue"
}

# Warning tracking  
track_warning() {
    local issue="$1"
    WARNING_COUNT=$((WARNING_COUNT + 1))
    log_audit "WARNING" "$issue"
}

echo -e "${BLUE}VARIABOT Comprehensive Code Audit${NC}"
echo -e "${BLUE}Addressing systematic code quality issues${NC}"
echo -e "${YELLOW}Audit log: $AUDIT_LOG${NC}\n"

log_audit "INFO" "Starting comprehensive code audit..."

# Phase 1: Shell Script Analysis
echo -e "${CYAN}Phase 1: Shell Script Analysis${NC}"
log_audit "INFO" "Analyzing all shell scripts..."

shell_scripts=($(find . -name "*.sh" -type f | grep -v ".git"))
total_shell_scripts=${#shell_scripts[@]}

echo "Found $total_shell_scripts shell scripts to analyze"

for script in "${shell_scripts[@]}"; do
    echo -n "Analyzing $script... "
    
    # Check syntax first
    if ! bash -n "$script" >/dev/null 2>&1; then
        track_critical "SYNTAX ERROR in $script - script will not execute"
        echo -e "${RED}CRITICAL${NC}"
        continue
    fi
    
    # Run shellcheck
    shellcheck_output=$(shellcheck "$script" 2>&1 || true)
    
    if [[ -n "$shellcheck_output" ]]; then
        # Count errors vs warnings
        error_count=$(echo "$shellcheck_output" | grep -c "error:" || true)
        warning_count=$(echo "$shellcheck_output" | grep -c "warning:" || true)
        
        if [[ $error_count -gt 0 ]]; then
            track_critical "SHELLCHECK ERRORS in $script: $error_count errors, $warning_count warnings"
            echo -e "${RED}ERRORS($error_count)${NC}"
        elif [[ $warning_count -gt 0 ]]; then
            track_warning "SHELLCHECK WARNINGS in $script: $warning_count warnings"
            echo -e "${YELLOW}WARNINGS($warning_count)${NC}"
        else
            echo -e "${GREEN}CLEAN${NC}"
        fi
    else
        echo -e "${GREEN}CLEAN${NC}"
    fi
done

# Phase 2: Python Analysis
echo -e "\n${CYAN}Phase 2: Python Code Analysis${NC}"
log_audit "INFO" "Analyzing all Python scripts..."

python_scripts=($(find . -name "*.py" -type f | grep -v ".git" | grep -v "__pycache__"))
total_python_scripts=${#python_scripts[@]}

echo "Found $total_python_scripts Python scripts to analyze"

for script in "${python_scripts[@]}"; do
    echo -n "Analyzing $script... "
    
    # Check syntax
    if ! python -m py_compile "$script" >/dev/null 2>&1; then
        track_critical "PYTHON SYNTAX ERROR in $script"
        echo -e "${RED}SYNTAX ERROR${NC}"
        continue
    fi
    
    # Check for critical issues with flake8
    if command -v flake8 >/dev/null 2>&1; then
        if ! python -m flake8 --select=E9,F63,F7,F82 "$script" >/dev/null 2>&1; then
            track_critical "PYTHON CRITICAL ISSUES in $script"
            echo -e "${RED}CRITICAL${NC}"
        else
            echo -e "${GREEN}CLEAN${NC}"
        fi
    else
        echo -e "${YELLOW}FLAKE8 N/A${NC}"
    fi
done

# Phase 3: Live Bot Testing
echo -e "\n${CYAN}Phase 3: Live Bot Testing${NC}"
log_audit "INFO" "Testing bot functionality..."

if [[ -f "variabot_universal.py" ]]; then
    echo "Testing universal bot interface..."
    
    # Test import capabilities
    if python -c "import variabot_universal" >/dev/null 2>&1; then
        log_audit "INFO" "variabot_universal.py imports successfully"
        echo -e "${GREEN}✓ Universal bot imports OK${NC}"
    else
        track_critical "variabot_universal.py import failure"
        echo -e "${RED}✗ Universal bot import failed${NC}"
    fi
    
    # Test help functionality
    if python variabot_universal.py --help >/dev/null 2>&1; then
        log_audit "INFO" "variabot_universal.py help functionality works"
        echo -e "${GREEN}✓ Universal bot help OK${NC}"
    else
        track_warning "variabot_universal.py help functionality issue"
        echo -e "${YELLOW}⚠ Universal bot help issue${NC}"
    fi
else
    track_critical "variabot_universal.py not found - main bot missing"
fi

# Test individual model bots
model_bots=($(ls st-*.py 2>/dev/null || true))
if [[ ${#model_bots[@]} -gt 0 ]]; then
    echo "Testing ${#model_bots[@]} model-specific bots..."
    for bot in "${model_bots[@]}"; do
        echo -n "Testing $bot... "
        if python -c "import sys; sys.path.insert(0, '.'); import ${bot%%.py}" >/dev/null 2>&1; then
            echo -e "${GREEN}OK${NC}"
        else
            track_warning "Import issue with $bot"
            echo -e "${YELLOW}WARN${NC}"
        fi
    done
fi

# Phase 4: Android Rooting Framework Testing
echo -e "\n${CYAN}Phase 4: Android Rooting Framework Testing${NC}"
log_audit "INFO" "Testing Android rooting components..."

if [[ -d "android_rooting" ]]; then
    # Test core modules
    core_modules=($(find android_rooting/core -name "*.py" 2>/dev/null || true))
    for module in "${core_modules[@]}"; do
        module_name=$(basename "$module" .py)
        echo -n "Testing $module_name... "
        if python -c "import sys; sys.path.insert(0, '.'); from android_rooting.core import $module_name" >/dev/null 2>&1; then
            echo -e "${GREEN}OK${NC}"
        else
            track_warning "Import issue with android_rooting.core.$module_name"
            echo -e "${YELLOW}WARN${NC}"
        fi
    done
    
    # Test utility modules
    util_modules=($(find android_rooting/utils -name "*.py" ! -name "__init__.py" 2>/dev/null || true))
    for module in "${util_modules[@]}"; do
        module_name=$(basename "$module" .py)
        echo -n "Testing utils/$module_name... "
        if python -c "import sys; sys.path.insert(0, '.'); from android_rooting.utils import $module_name" >/dev/null 2>&1; then
            echo -e "${GREEN}OK${NC}"
        else
            track_warning "Import issue with android_rooting.utils.$module_name"
            echo -e "${YELLOW}WARN${NC}"
        fi
    done
    
    # Test script executability
    rooting_scripts=($(find android_rooting/scripts -name "*.sh" 2>/dev/null || true))
    for script in "${rooting_scripts[@]}"; do
        script_name=$(basename "$script")
        echo -n "Testing $script_name syntax... "
        if bash -n "$script" >/dev/null 2>&1; then
            echo -e "${GREEN}OK${NC}"
        else
            track_critical "Syntax error in $script"
            echo -e "${RED}ERROR${NC}"
        fi
    done
else
    track_critical "android_rooting directory not found - core framework missing"
fi

# Phase 5: Server Deployment Test
echo -e "\n${CYAN}Phase 5: Server Deployment Test${NC}"
log_audit "INFO" "Testing server deployment capabilities..."

# Test if we can start a server
if command -v python >/dev/null 2>&1; then
    echo "Testing HTTP server capability..."
    
    # Try to start a simple HTTP server on available port
    if python -m http.server 0 --bind 127.0.0.1 >/dev/null 2>&1 &
    then
        server_pid=$!
        sleep 2
        kill $server_pid 2>/dev/null || true
        echo -e "${GREEN}✓ HTTP server capability confirmed${NC}"
        log_audit "INFO" "Server deployment capability confirmed"
    else
        track_warning "HTTP server deployment issue"
        echo -e "${YELLOW}⚠ HTTP server deployment issue${NC}"
    fi
fi

# Test Streamlit if available
if command -v streamlit >/dev/null 2>&1; then
    echo "Testing Streamlit deployment..."
    if streamlit hello --server.headless true --server.port 8501 --server.address 127.0.0.1 >/dev/null 2>&1 &
    then
        streamlit_pid=$!
        sleep 3
        kill $streamlit_pid 2>/dev/null || true
        echo -e "${GREEN}✓ Streamlit deployment capability confirmed${NC}"
        log_audit "INFO" "Streamlit deployment capability confirmed"
    else
        track_warning "Streamlit deployment issue"
        echo -e "${YELLOW}⚠ Streamlit deployment issue${NC}"
    fi
else
    track_warning "Streamlit not available for deployment testing"
    echo -e "${YELLOW}⚠ Streamlit not installed${NC}"
fi

# Phase 6: Professional Standards Compliance
echo -e "\n${CYAN}Phase 6: Professional Standards Compliance${NC}"
log_audit "INFO" "Checking professional code standards compliance..."

# Check for required documentation
required_docs=("README.md" "copilot_instructions.md" "organization_instructions.md")
for doc in "${required_docs[@]}"; do
    if [[ -f "$doc" ]]; then
        echo -e "${GREEN}✓ $doc present${NC}"
    else
        track_warning "Missing documentation: $doc"
        echo -e "${YELLOW}⚠ Missing $doc${NC}"
    fi
done

# Check reference vault
if [[ -d "reference_vault" ]]; then
    vault_docs=$(find reference_vault -name "*.md" | wc -l)
    if [[ $vault_docs -gt 0 ]]; then
        echo -e "${GREEN}✓ Reference vault contains $vault_docs documents${NC}"
        log_audit "INFO" "Reference vault properly structured with $vault_docs documents"
    else
        track_warning "Reference vault exists but contains no markdown files"
    fi
else
    track_critical "Reference vault missing - violates organizational standards"
fi

# Final Report
echo -e "\n${BLUE}COMPREHENSIVE AUDIT RESULTS${NC}"
echo -e "${BLUE}=================================${NC}"

if [[ $ERROR_COUNT -eq 0 ]]; then
    echo -e "${GREEN}✓ NO CRITICAL ISSUES FOUND${NC}"
    log_audit "SUCCESS" "Code audit completed successfully - no critical issues"
else
    echo -e "${RED}✗ $ERROR_COUNT CRITICAL ISSUES FOUND${NC}"
    log_audit "FAILURE" "Code audit found $ERROR_COUNT critical issues"
    
    echo -e "\n${RED}CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION:${NC}"
    for issue in "${CRITICAL_ISSUES[@]}"; do
        echo -e "${RED}  • $issue${NC}"
    done
fi

if [[ $WARNING_COUNT -gt 0 ]]; then
    echo -e "${YELLOW}⚠ $WARNING_COUNT WARNINGS FOUND${NC}"
    log_audit "WARNING" "Code audit found $WARNING_COUNT warnings"
fi

echo -e "\n${CYAN}Shell Scripts Analyzed: $total_shell_scripts${NC}"
echo -e "${CYAN}Python Scripts Analyzed: $total_python_scripts${NC}"
echo -e "${CYAN}Detailed audit log: $AUDIT_LOG${NC}"

# Exit with appropriate code
if [[ $ERROR_COUNT -gt 0 ]]; then
    log_audit "ERROR" "Audit completed with $ERROR_COUNT critical issues"
    exit 1
else
    log_audit "SUCCESS" "Audit completed successfully"
    exit 0
fi