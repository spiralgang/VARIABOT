#!/bin/bash
#
# Termux Setup Script for Android Rooting Framework
# Prepares Termux environment for Android rooting operations
#
# This script provides:
# - Termux environment setup and configuration
# - Required package installation
# - Python environment preparation
# - Bot framework deployment
# - Networking and privilege setup
#
# Compatible with: Termux on Android 10+, ARM64 architecture
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Set up basic paths first
SETUP_DIR="$HOME/.android_rooting_setup"
LOG_FILE="$HOME/termux_setup_$(date +%Y%m%d_%H%M%S).log"

# Logging functions - Define after LOG_FILE
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }

# Configuration - Use environment variables for Termux paths
TERMUX_PREFIX="${PREFIX:-}"
if [[ -z "$TERMUX_PREFIX" ]]; then
    log_error "PREFIX environment variable not set - not running in Termux?"
    exit 1
fi

# Error handling
cleanup() {
    local exit_code=$?
    log_info "Setup cleanup completed with exit code: $exit_code"
    exit $exit_code
}

trap cleanup EXIT
trap 'log_error "Setup interrupted"; exit 130' INT TERM

# Check if running in Termux
check_termux_environment() {
    log_info "Checking Termux environment..."
    
    if [[ -z "${TERMUX_VERSION:-}" ]]; then
        log_error "This script must be run in Termux environment"
        echo -e "${RED}Please install and run this script from Termux${NC}"
        echo "Download Termux: https://f-droid.org/packages/com.termux/"
        return 1
    fi
    
    log_info "Termux version: $TERMUX_VERSION"
    log_info "Termux prefix: $TERMUX_PREFIX"
    
    # Check Android version
    local android_version=$(getprop ro.build.version.release 2>/dev/null || echo "unknown")
    log_info "Android version: $android_version"
    
    # Check architecture
    local arch=$(getprop ro.product.cpu.abi 2>/dev/null || echo "unknown")
    log_info "CPU architecture: $arch"
    
    if [[ "$arch" != *"arm64"* ]] && [[ "$arch" != *"aarch64"* ]]; then
        log_warn "This setup is optimized for ARM64 architecture"
    fi
    
    return 0
}

# Update Termux packages
update_termux_packages() {
    log_info "Updating Termux packages..."
    
    # Update package lists
    if ! pkg update -y; then
        log_error "Failed to update package lists"
        return 1
    fi
    
    # Upgrade existing packages
    if ! pkg upgrade -y; then
        log_warn "Some packages failed to upgrade (continuing anyway)"
    fi
    
    log_info "Termux packages updated successfully"
    return 0
}

# Install required packages using proper Termux package manager
install_required_packages() {
    log_info "Installing required packages using Termux pkg manager..."
    
    # Use our proper package manager instead of hardcoded commands
    if python3 "$HOME/android_rooting/utils/package_manager.py" setup; then
        log_info "✓ Essential packages installed successfully"
    else
        log_error "Failed to install some essential packages"
        log_warn "Some functionality may be limited - check package_manager.log"
        return 1
    fi
    
    # Verify critical packages
    local critical_packages=("python" "git" "curl")
    local missing_packages=()
    
    for package in "${critical_packages[@]}"; do
        if ! command -v "$package" &>/dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [[ ${#missing_packages[@]} -gt 0 ]]; then
        log_error "Critical packages missing: ${missing_packages[*]}"
        return 1
    fi
    
    log_info "Package installation completed successfully"
    return 0
}

# Setup Python environment using proper package manager
setup_python_environment() {
    log_info "Setting up Python environment..."
    
    # Use our Python package manager instead of direct pip calls
    local python_packages=(
        "requests"        # HTTP library
        "urllib3"         # URL handling  
        "psutil"         # System utilities
        "netifaces"      # Network interface info
        "cryptography"   # Cryptographic library
        "paramiko"       # SSH client
        "websocket-client" # WebSocket client
        "aiohttp"        # Async HTTP client
    )
    
    log_info "Installing Python packages using proper Termux environment..."
    for package in "${python_packages[@]}"; do
        log_info "Installing Python package: $package"
        if python3 "$HOME/android_rooting/utils/package_manager.py" install "$package" --python; then
            log_info "✓ $package installed successfully"
        else
            log_warn "✗ Failed to install $package"
        fi
    done
    
    # Verify Python installation with essential imports
    if python3 -c "
import sys, os, subprocess, threading, json, logging
import requests, urllib3, psutil
print('✓ Python environment verification successful')
print(f'Python version: {sys.version}')
print(f'Python executable: {sys.executable}')
print(f'Platform: {sys.platform}')
"; then
        log_info "✓ Python environment setup completed successfully"
    else
        log_error "Python environment verification failed"
        return 1
    fi
    
    return 0
}

# Setup Android rooting framework
setup_rooting_framework() {
    log_info "Setting up Android rooting framework..."
    
    # Create setup directory
    mkdir -p "$SETUP_DIR"
    
    # Check if framework is already installed
    if [[ -d "$HOME/android_rooting" ]]; then
        log_info "Android rooting framework already exists"
        read -p "Do you want to update it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Skipping framework setup"
            return 0
        fi
    fi
    
    # Clone or copy framework
    local framework_source="/data/data/com.termux/files/home/VARIABOT/android_rooting"
    
    if [[ -d "$framework_source" ]]; then
        log_info "Copying framework from local source..."
        cp -r "$framework_source" "$HOME/"
    else
        log_info "Cloning framework from GitHub..."
        if git clone https://github.com/spiralgang/VARIABOT.git "$HOME/VARIABOT"; then
            cp -r "$HOME/VARIABOT/android_rooting" "$HOME/"
            rm -rf "$HOME/VARIABOT"
        else
            log_error "Failed to clone framework"
            return 1
        fi
    fi
    
    # Make scripts executable
    find "$HOME/android_rooting" -name "*.sh" -exec chmod +x {} \;
    find "$HOME/android_rooting" -name "*.py" -exec chmod +x {} \;
    
    # Create symlinks for easy access
    ln -sf "$HOME/android_rooting/scripts/android_root_complete.sh" "$PREFIX/bin/android-root"
    ln -sf "$HOME/android_rooting/core/root_detector.py" "$PREFIX/bin/root-detect"
    ln -sf "$HOME/android_rooting/core/magisk_manager.py" "$PREFIX/bin/magisk-manage"
    ln -sf "$HOME/android_rooting/bots/error_handler_bot.py" "$PREFIX/bin/error-bot"
    
    log_info "✓ Android rooting framework setup completed"
    return 0
}

# Setup Termux services
setup_termux_services() {
    log_info "Setting up Termux services..."
    
    # Setup SSH daemon
    if command -v sshd &> /dev/null; then
        log_info "Configuring SSH daemon..."
        
        # Generate SSH keys if they don't exist
        if [[ ! -f "$HOME/.ssh/id_rsa" ]]; then
            ssh-keygen -t rsa -b 4096 -f "$HOME/.ssh/id_rsa" -N ""
            log_info "SSH keys generated"
        fi
        
        # Setup authorized_keys
        cat "$HOME/.ssh/id_rsa.pub" >> "$HOME/.ssh/authorized_keys"
        chmod 600 "$HOME/.ssh/authorized_keys"
        
        # Start SSH daemon
        if sshd; then
            log_info "✓ SSH daemon started"
            log_info "SSH port: 8022 (default Termux SSH port)"
        else
            log_warn "Failed to start SSH daemon"
        fi
    fi
    
    # Setup Termux API
    if command -v termux-setup-storage &> /dev/null; then
        log_info "Setting up Termux storage access..."
        termux-setup-storage || log_warn "Storage setup may require user interaction"
    fi
    
    return 0
}

# Setup networking utilities
setup_networking() {
    log_info "Setting up networking utilities..."
    
    # Create networking scripts directory
    mkdir -p "$HOME/.android_rooting/network"
    
    # Create network testing script
    cat > "$HOME/.android_rooting/network/test_connectivity.sh" << 'EOF'
#!/bin/bash
# Network connectivity testing script

echo "=== Network Connectivity Test ==="

# Test DNS resolution
echo "Testing DNS resolution..."
if nslookup google.com &>/dev/null; then
    echo "✓ DNS resolution working"
else
    echo "✗ DNS resolution failed"
fi

# Test HTTP connectivity
echo "Testing HTTP connectivity..."
if curl -s --max-time 5 http://httpbin.org/ip &>/dev/null; then
    echo "✓ HTTP connectivity working"
else
    echo "✗ HTTP connectivity failed"
fi

# Test HTTPS connectivity
echo "Testing HTTPS connectivity..."
if curl -s --max-time 5 https://httpbin.org/ip &>/dev/null; then
    echo "✓ HTTPS connectivity working"
else
    echo "✗ HTTPS connectivity failed"
fi

# Show network interfaces
echo "Network interfaces:"
ip addr show 2>/dev/null || ifconfig 2>/dev/null || echo "Interface info not available"

# Show routing table
echo "Routing table:"
ip route show 2>/dev/null || route 2>/dev/null || echo "Route info not available"
EOF

    chmod +x "$HOME/.android_rooting/network/test_connectivity.sh"
    ln -sf "$HOME/.android_rooting/network/test_connectivity.sh" "$PREFIX/bin/test-network"
    
    # Create port scanning script
    cat > "$HOME/.android_rooting/network/port_scan.sh" << 'EOF'
#!/bin/bash
# Simple port scanning script

target="${1:-127.0.0.1}"
ports="${2:-22,80,443,8080,8022}"

echo "Scanning $target for ports: $ports"

IFS=',' read -ra PORT_ARRAY <<< "$ports"
for port in "${PORT_ARRAY[@]}"; do
    if timeout 1 bash -c "echo >/dev/tcp/$target/$port" 2>/dev/null; then
        echo "✓ Port $port is open"
    else
        echo "✗ Port $port is closed or filtered"
    fi
done
EOF

    chmod +x "$HOME/.android_rooting/network/port_scan.sh"
    ln -sf "$HOME/.android_rooting/network/port_scan.sh" "$PREFIX/bin/port-scan"
    
    log_info "✓ Networking utilities setup completed"
    return 0
}

# Create configuration files
create_config_files() {
    log_info "Creating configuration files..."
    
    # Create main configuration
    cat > "$HOME/.android_rooting/config.json" << EOF
{
    "termux_version": "${TERMUX_VERSION}",
    "setup_date": "$(date -Iseconds)",
    "android_version": "$(getprop ro.build.version.release 2>/dev/null || echo 'unknown')",
    "device_model": "$(getprop ro.product.model 2>/dev/null || echo 'unknown')",
    "cpu_arch": "$(getprop ro.product.cpu.abi 2>/dev/null || echo 'unknown')",
    "framework_path": "$HOME/android_rooting",
    "log_directory": "$HOME/.android_rooting/logs",
    "bot_config": {
        "enabled": true,
        "github_repo": "spiralgang/VARIABOT",
        "update_interval": 30,
        "auto_handle": true
    },
    "network_config": {
        "ssh_port": 8022,
        "api_timeout": 30,
        "retry_attempts": 3
    }
}
EOF

    # Create environment setup script
    cat > "$HOME/.android_rooting/setup_env.sh" << 'EOF'
#!/bin/bash
# Environment setup script - source this in your shell

export ANDROID_ROOTING_HOME="$HOME/android_rooting"
export ANDROID_ROOT_LOGS="$HOME/.android_rooting/logs"
export ANDROID_ROOT_CONFIG="$HOME/.android_rooting/config.json"

# Add rooting tools to PATH
export PATH="$ANDROID_ROOTING_HOME/scripts:$ANDROID_ROOTING_HOME/core:$ANDROID_ROOTING_HOME/bots:$PATH"

# Create aliases
alias root-status='python3 $ANDROID_ROOTING_HOME/core/root_detector.py'
alias magisk-status='python3 $ANDROID_ROOTING_HOME/core/magisk_manager.py status'
alias root-complete='$ANDROID_ROOTING_HOME/scripts/android_root_complete.sh'
alias start-bot='python3 $ANDROID_ROOTING_HOME/bots/error_handler_bot.py --daemon'

echo "Android Rooting Framework environment loaded"
echo "Available commands: root-status, magisk-status, root-complete, start-bot"
echo "Available tools: android-root, root-detect, magisk-manage, error-bot, test-network, port-scan"
EOF

    chmod +x "$HOME/.android_rooting/setup_env.sh"
    
    # Add to shell profile
    if [[ -f "$HOME/.bashrc" ]]; then
        if ! grep -q "android_rooting" "$HOME/.bashrc"; then
            echo "source $HOME/.android_rooting/setup_env.sh" >> "$HOME/.bashrc"
            log_info "Added environment setup to .bashrc"
        fi
    fi
    
    if [[ -f "$HOME/.zshrc" ]]; then
        if ! grep -q "android_rooting" "$HOME/.zshrc"; then
            echo "source $HOME/.android_rooting/setup_env.sh" >> "$HOME/.zshrc"
            log_info "Added environment setup to .zshrc"
        fi
    fi
    
    # Create logs directory
    mkdir -p "$HOME/.android_rooting/logs"
    
    log_info "✓ Configuration files created"
    return 0
}

# Setup documentation
setup_documentation() {
    log_info "Setting up documentation..."
    
    mkdir -p "$HOME/.android_rooting/docs"
    
    # Create quick start guide
    cat > "$HOME/.android_rooting/docs/QUICK_START.md" << 'EOF'
# Android Rooting Framework - Quick Start Guide

## Overview
This framework provides production-grade Android rooting capabilities with integrated bot monitoring and error handling.

## Quick Commands

### Check Root Status
```bash
root-status
# or
android-root --status
```

### Complete Root Process
```bash
root-complete
# or
android-root
```

### Manage Magisk
```bash
magisk-manage status
magisk-manage repair
magisk-manage modules list
```

### Start Error Handler Bot
```bash
start-bot
# or
error-bot --daemon
```

### Network Testing
```bash
test-network
port-scan 192.168.1.1 22,80,443
```

## File Locations

- Framework: `~/android_rooting/`
- Config: `~/.android_rooting/config.json`
- Logs: `~/.android_rooting/logs/`
- Documentation: `~/.android_rooting/docs/`

## Environment

The framework automatically sets up environment variables and aliases.
Reload your shell or run:
```bash
source ~/.android_rooting/setup_env.sh
```

## Troubleshooting

1. **Permission Denied**: Ensure Termux has storage permissions
2. **Network Issues**: Check connectivity with `test-network`
3. **Root Failures**: Check logs in `~/.android_rooting/logs/`
4. **Bot Issues**: Verify Python packages are installed

## Support

- GitHub: https://github.com/spiralgang/VARIABOT
- Documentation: Check `docs/` directory
- Logs: Always check log files for detailed error information
EOF

    # Create troubleshooting guide
    cat > "$HOME/.android_rooting/docs/TROUBLESHOOTING.md" << 'EOF'
# Troubleshooting Guide

## Common Issues

### 1. Python Import Errors
```bash
# Reinstall Python packages
pkg install python python-pip -y
pip install requests urllib3 psutil
```

### 2. Permission Denied Errors
```bash
# Setup Termux storage access
termux-setup-storage

# Check file permissions
ls -la ~/android_rooting/scripts/
chmod +x ~/android_rooting/scripts/*.sh
```

### 3. Network Connectivity Issues
```bash
# Test network
test-network

# Check DNS
nslookup google.com

# Reset network settings
setprop net.dns1 8.8.8.8
setprop net.dns2 8.8.4.4
```

### 4. Root Detection Failures
```bash
# Manual root check
su -c "id"

# Check Magisk status
magisk --version

# Verify system access
mount | grep system
```

### 5. Bot Framework Issues
```bash
# Check bot logs
tail -f ~/.android_rooting/logs/bot.log

# Restart bot
pkill -f error_handler_bot.py
start-bot
```

## Log Analysis

Check these log files for detailed information:
- `~/.android_rooting/logs/android_root_*.log` - Main rooting logs
- `~/.android_rooting/logs/bot.log` - Bot framework logs
- `~/.android_rooting/logs/audit.log` - Audit trail

## Recovery Procedures

### Reset Framework
```bash
rm -rf ~/android_rooting ~/.android_rooting
# Re-run setup script
```

### Emergency Root Repair
```bash
magisk-manage repair
# or
android-root --force-repair
```
EOF

    log_info "✓ Documentation setup completed"
    return 0
}

# Generate setup report
generate_setup_report() {
    log_info "Generating setup report..."
    
    local report_file="$HOME/.android_rooting/setup_report_$(date +%Y%m%d_%H%M%S).json"
    
    # Collect system information
    local android_version=$(getprop ro.build.version.release 2>/dev/null || echo "unknown")
    local device_model=$(getprop ro.product.model 2>/dev/null || echo "unknown")
    local cpu_arch=$(getprop ro.product.cpu.abi 2>/dev/null || echo "unknown")
    
    # Check installations
    local python_version=$(python --version 2>&1 | cut -d' ' -f2 || echo "unknown")
    local git_version=$(git --version 2>&1 | cut -d' ' -f3 || echo "unknown")
    
    cat > "$report_file" << EOF
{
    "setup_timestamp": "$(date -Iseconds)",
    "termux_info": {
        "version": "${TERMUX_VERSION}",
        "prefix": "${TERMUX_PREFIX}",
        "home": "${HOME}"
    },
    "device_info": {
        "android_version": "$android_version",
        "device_model": "$device_model",
        "cpu_architecture": "$cpu_arch"
    },
    "installed_tools": {
        "python_version": "$python_version",
        "git_version": "$git_version",
        "framework_installed": $(test -d "$HOME/android_rooting" && echo "true" || echo "false"),
        "symlinks_created": $(test -L "$PREFIX/bin/android-root" && echo "true" || echo "false")
    },
    "network_status": {
        "ssh_configured": $(test -f "$HOME/.ssh/id_rsa" && echo "true" || echo "false"),
        "storage_access": $(test -d "$HOME/storage" && echo "true" || echo "false")
    },
    "setup_log": "$LOG_FILE",
    "config_file": "$HOME/.android_rooting/config.json"
}
EOF
    
    log_info "Setup report generated: $report_file"
    
    # Display summary
    echo -e "\n${BLUE}=== TERMUX SETUP COMPLETION SUMMARY ===${NC}"
    echo -e "Termux Version: $TERMUX_VERSION"
    echo -e "Device: $device_model (Android $android_version)"
    echo -e "Architecture: $cpu_arch"
    echo -e "Python Version: $python_version"
    echo -e "Framework: ${GREEN}Installed${NC}"
    echo -e "Tools: ${GREEN}Available${NC}"
    echo -e "Documentation: ${GREEN}Ready${NC}"
    echo -e "\nSetup Log: $LOG_FILE"
    echo -e "Config: $HOME/.android_rooting/config.json"
    echo -e "Report: $report_file"
    echo -e "\n${GREEN}Setup completed successfully!${NC}"
    echo -e "\nTo start using the framework:"
    echo -e "  ${YELLOW}source ~/.android_rooting/setup_env.sh${NC}"
    echo -e "  ${YELLOW}root-status${NC} (check current root status)"
    echo -e "  ${YELLOW}android-root${NC} (complete root process)"
    echo -e "${BLUE}===========================================${NC}\n"
}

# Main setup function
main() {
    echo -e "${BLUE}Termux Setup for Android Rooting Framework${NC}"
    echo -e "${BLUE}Production-grade rooting environment setup${NC}\n"
    
    log_info "Starting Termux setup process..."
    
    # Step 1: Check Termux environment
    if ! check_termux_environment; then
        exit 1
    fi
    
    # Step 2: Update packages
    if ! update_termux_packages; then
        log_error "Package update failed"
        exit 1
    fi
    
    # Step 3: Install required packages
    if ! install_required_packages; then
        log_error "Package installation failed"
        exit 1
    fi
    
    # Step 4: Setup Python environment
    if ! setup_python_environment; then
        log_error "Python environment setup failed"
        exit 1
    fi
    
    # Step 5: Setup rooting framework
    if ! setup_rooting_framework; then
        log_error "Framework setup failed"
        exit 1
    fi
    
    # Step 6: Setup Termux services
    setup_termux_services
    
    # Step 7: Setup networking utilities
    setup_networking
    
    # Step 8: Create configuration files
    create_config_files
    
    # Step 9: Setup documentation
    setup_documentation
    
    # Step 10: Generate setup report
    generate_setup_report
    
    log_info "${GREEN}Termux setup completed successfully${NC}"
}

# Script entry point
if [[ "${BASH_SOURCE[0]:-$0}" == "${0}" ]]; then
    main "$@"
fi

# References:
# - Termux Documentation: https://termux.com/docs/
# - Termux API: https://github.com/termux/termux-api
# - Android Package Management: https://source.android.com/devices/tech/config/
# - Python in Termux: https://wiki.termux.com/wiki/Python
# - SSH in Termux: https://wiki.termux.com/wiki/Remote_Access