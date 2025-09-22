#!/data/data/com.termux/files/usr/bin/bash
#
# Environment Detection Utility
# Production-grade environment detection for Android/Termux/Kali contexts
#
# This script provides:
# - Comprehensive environment detection
# - Platform capability assessment
# - Privilege level detection
# - Tool availability checking
#
# Compatible with: Termux, Android 10+, Kali Linux, Standard Linux
#

set -euo pipefail

# Global variables
ENV_TYPE="unknown"
PRIVILEGE_LEVEL="unknown"
CAPABILITIES=()
PLATFORM_INFO=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Detect environment type
detect_environment() {
    if [[ -n "${PREFIX:-}" && "$PREFIX" == *"termux"* ]]; then
        ENV_TYPE="termux"
        PLATFORM_INFO="Termux Android Environment"
    elif [[ -d "/data/data/com.termux" ]]; then
        ENV_TYPE="termux"
        PLATFORM_INFO="Termux Android Environment (detected)"
    elif [[ -f "/etc/debian_version" ]] && command -v kali-tweaks >/dev/null 2>&1; then
        ENV_TYPE="kali"
        PLATFORM_INFO="Kali Linux"
    elif [[ -f "/etc/debian_version" ]]; then
        ENV_TYPE="debian"
        PLATFORM_INFO="Debian-based Linux"
    elif [[ -f "/etc/redhat-release" ]]; then
        ENV_TYPE="redhat"
        PLATFORM_INFO="Red Hat-based Linux"
    elif [[ -f "/system/build.prop" ]]; then
        ENV_TYPE="android"
        PLATFORM_INFO="Android System"
    elif [[ "$(uname -s)" == "Linux" ]]; then
        ENV_TYPE="linux"
        PLATFORM_INFO="Generic Linux"
    else
        ENV_TYPE="unknown"
        PLATFORM_INFO="Unknown Environment"
    fi
}

# Detect privilege level
detect_privileges() {
    # Check for root access
    if [[ "$EUID" -eq 0 ]] || id | grep -q "uid=0"; then
        PRIVILEGE_LEVEL="root"
        CAPABILITIES+=("full_root")
        return
    fi
    
    # Check for su access
    if command -v su >/dev/null 2>&1 && su -c "id" 2>/dev/null | grep -q "uid=0"; then
        PRIVILEGE_LEVEL="su_available"
        CAPABILITIES+=("su_access")
        return
    fi
    
    # Check for sudo access
    if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
        PRIVILEGE_LEVEL="sudo_available"
        CAPABILITIES+=("sudo_access")
        return
    fi
    
    # Check for Magisk
    if command -v magisk >/dev/null 2>&1; then
        PRIVILEGE_LEVEL="magisk_available"
        CAPABILITIES+=("magisk_root")
        return
    fi
    
    # Check for partial root indicators
    local partial_indicators=(
        "/system/bin/su"
        "/system/xbin/su"
        "/data/local/tmp/su"
        "/sbin/su"
    )
    
    for indicator in "${partial_indicators[@]}"; do
        if [[ -f "$indicator" ]]; then
            PRIVILEGE_LEVEL="partial_root"
            CAPABILITIES+=("partial_access")
            return
        fi
    done
    
    PRIVILEGE_LEVEL="user"
}

# Check tool availability
check_tool_availability() {
    local tools=(
        "python3:python"
        "python:python"
        "bash:shell"
        "sh:shell"
        "curl:network"
        "wget:network"
        "git:development"
        "pkg:termux_package_manager"
        "apt:debian_package_manager"
        "yum:redhat_package_manager"
        "proot:container"
        "proot-distro:kali_support"
        "chroot:container"
        "magisk:android_root"
        "busybox:embedded_tools"
        "adb:android_debug"
        "fastboot:android_flash"
        "nmap:network_scan"
        "netcat:network_tools"
        "nc:network_tools"
    )
    
    for tool_spec in "${tools[@]}"; do
        local tool="${tool_spec%:*}"
        local category="${tool_spec#*:}"
        
        if command -v "$tool" >/dev/null 2>&1; then
            CAPABILITIES+=("${category}_${tool}")
        fi
    done
}

# Check Android-specific capabilities
check_android_capabilities() {
    if [[ "$ENV_TYPE" == "termux" || "$ENV_TYPE" == "android" ]]; then
        # Check Android version
        if [[ -f "/system/build.prop" ]]; then
            local android_version
            android_version=$(grep "ro.build.version.release" /system/build.prop 2>/dev/null | cut -d'=' -f2 || echo "unknown")
            PLATFORM_INFO="${PLATFORM_INFO} (Android ${android_version})"
            CAPABILITIES+=("android_version_${android_version}")
        fi
        
        # Check architecture
        local arch
        arch=$(uname -m)
        CAPABILITIES+=("arch_${arch}")
        
        # Check for SELinux
        if [[ -f "/sys/fs/selinux/enforce" ]]; then
            local selinux_status
            selinux_status=$(cat /sys/fs/selinux/enforce 2>/dev/null || echo "unknown")
            if [[ "$selinux_status" == "0" ]]; then
                CAPABILITIES+=("selinux_permissive")
            elif [[ "$selinux_status" == "1" ]]; then
                CAPABILITIES+=("selinux_enforcing")
            fi
        fi
        
        # Check for important directories
        local android_dirs=(
            "/data/local/tmp:writable_tmp"
            "/sdcard:external_storage"
            "/system:system_partition"
            "/data/data:app_data"
        )
        
        for dir_spec in "${android_dirs[@]}"; do
            local dir="${dir_spec%:*}"
            local capability="${dir_spec#*:}"
            
            if [[ -d "$dir" ]]; then
                CAPABILITIES+=("has_${capability}")
                
                # Check if writable
                if [[ -w "$dir" ]]; then
                    CAPABILITIES+=("writable_${capability}")
                fi
            fi
        done
    fi
}

# Check Kali-specific capabilities
check_kali_capabilities() {
    if [[ "$ENV_TYPE" == "kali" ]]; then
        # Check for penetration testing tools
        local kali_tools=(
            "metasploit-framework:metasploit"
            "nmap:network_scanner"
            "burpsuite:web_proxy"
            "sqlmap:sql_injection"
            "aircrack-ng:wireless"
            "john:password_cracking"
            "hashcat:gpu_cracking"
            "wireshark:packet_analysis"
        )
        
        for tool_spec in "${kali_tools[@]}"; do
            local tool="${tool_spec%:*}"
            local capability="${tool_spec#*:}"
            
            if command -v "$tool" >/dev/null 2>&1; then
                CAPABILITIES+=("kali_${capability}")
            fi
        done
    fi
}

# Check container capabilities
check_container_capabilities() {
    # Check for proot/chroot capabilities
    if command -v proot >/dev/null 2>&1; then
        CAPABILITIES+=("proot_container")
    fi
    
    if command -v chroot >/dev/null 2>&1; then
        CAPABILITIES+=("chroot_container")
    fi
    
    # Check for existing chroot environments
    local chroot_paths=(
        "/data/local/nhsystem"
        "/data/data/com.termux/files/home/kali-chroot"
        "/opt/kali"
        "/chroot/kali"
    )
    
    for path in "${chroot_paths[@]}"; do
        if [[ -d "$path" ]]; then
            CAPABILITIES+=("existing_kali_chroot")
            break
        fi
    done
}

# Generate capability report
generate_report() {
    local format="${1:-human}"
    
    if [[ "$format" == "json" ]]; then
        # JSON output
        cat << EOF
{
    "environment": {
        "type": "$ENV_TYPE",
        "platform_info": "$PLATFORM_INFO",
        "privilege_level": "$PRIVILEGE_LEVEL"
    },
    "capabilities": [$(printf '"%s",' "${CAPABILITIES[@]}" | sed 's/,$//')],
    "timestamp": "$(date -Iseconds)",
    "hostname": "$(hostname 2>/dev/null || echo 'unknown')",
    "architecture": "$(uname -m)",
    "kernel": "$(uname -r 2>/dev/null || echo 'unknown')"
}
EOF
    else
        # Human-readable output
        echo "🔍 Environment Detection Report"
        echo "================================="
        echo
        echo "Environment Type: $ENV_TYPE"
        echo "Platform Info: $PLATFORM_INFO"
        echo "Privilege Level: $PRIVILEGE_LEVEL"
        echo "Architecture: $(uname -m)"
        echo "Kernel: $(uname -r 2>/dev/null || echo 'unknown')"
        echo
        echo "Capabilities Detected:"
        if [[ ${#CAPABILITIES[@]} -eq 0 ]]; then
            echo "  - None detected"
        else
            for capability in "${CAPABILITIES[@]}"; do
                echo "  ✓ $capability"
            done
        fi
        echo
        echo "Timestamp: $(date)"
    fi
}

# Check if environment is suitable for rooting
check_rooting_suitability() {
    local suitability_score=0
    local recommendations=()
    
    # Check environment type
    case "$ENV_TYPE" in
        "termux"|"android")
            suitability_score=$((suitability_score + 30))
            ;;
        "kali")
            suitability_score=$((suitability_score + 20))
            ;;
        *)
            recommendations+=("Consider using Termux or Kali Linux for better compatibility")
            ;;
    esac
    
    # Check privilege level
    case "$PRIVILEGE_LEVEL" in
        "root"|"su_available")
            suitability_score=$((suitability_score + 40))
            ;;
        "magisk_available"|"partial_root")
            suitability_score=$((suitability_score + 30))
            recommendations+=("Root access partially available - may need completion")
            ;;
        *)
            recommendations+=("No root access detected - full rooting process required")
            ;;
    esac
    
    # Check for essential tools
    local essential_tools=("python" "shell" "network")
    for tool_category in "${essential_tools[@]}"; do
        if printf '%s\n' "${CAPABILITIES[@]}" | grep -q "$tool_category"; then
            suitability_score=$((suitability_score + 10))
        else
            recommendations+=("Missing essential tool category: $tool_category")
        fi
    done
    
    # Output suitability assessment
    echo
    echo "🎯 Rooting Suitability Assessment"
    echo "=================================="
    echo "Suitability Score: $suitability_score/100"
    
    if [[ $suitability_score -ge 80 ]]; then
        echo -e "Status: ${GREEN}EXCELLENT${NC} - Environment is highly suitable for rooting"
    elif [[ $suitability_score -ge 60 ]]; then
        echo -e "Status: ${YELLOW}GOOD${NC} - Environment is suitable with minor limitations"
    elif [[ $suitability_score -ge 40 ]]; then
        echo -e "Status: ${YELLOW}FAIR${NC} - Environment may work but has significant limitations"
    else
        echo -e "Status: ${RED}POOR${NC} - Environment is not well-suited for rooting"
    fi
    
    if [[ ${#recommendations[@]} -gt 0 ]]; then
        echo
        echo "Recommendations:"
        for rec in "${recommendations[@]}"; do
            echo "  • $rec"
        done
    fi
}

# Main execution
main() {
    local output_format="human"
    local show_suitability=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --json)
                output_format="json"
                shift
                ;;
            --suitability)
                show_suitability=true
                shift
                ;;
            --help|-h)
                cat << EOF
Environment Detection Utility

Usage: $0 [OPTIONS]

Options:
    --json          Output in JSON format
    --suitability   Show rooting suitability assessment
    --help, -h      Show this help message

Examples:
    $0                    # Standard human-readable output
    $0 --json            # JSON output for scripts
    $0 --suitability     # Include rooting assessment
EOF
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Perform detection
    detect_environment
    detect_privileges
    check_tool_availability
    check_android_capabilities
    check_kali_capabilities
    check_container_capabilities
    
    # Generate output
    generate_report "$output_format"
    
    if [[ "$show_suitability" == true && "$output_format" == "human" ]]; then
        check_rooting_suitability
    fi
}

# Export functions for sourcing
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
else
    # Being sourced - export key functions
    export -f detect_environment detect_privileges generate_report
fi

# References:
# - Internal: /reference_vault/linux_kali_android.md#environment-detection
# - Internal: /reference_vault/PRODUCTION_GRADE_STANDARDS.md#modularity
# - External: Android Security Model — https://source.android.com/security/overview/