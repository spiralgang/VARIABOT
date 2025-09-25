#!/data/data/com.termux/files/usr/bin/bash
# Termux-optimized launch script for VARIABOT
# Auto-configured for Termux 0.119.0-beta.3 environment
# Supports Android 10+ with specialized mobile optimizations

set -e  # Exit on any error

# Color codes for better terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Termux environment detection and validation
echo -e "${CYAN}VARIABOT Termux Launcher v1.0${NC}"
echo -e "${CYAN}=================================${NC}"

# Validate Termux environment
if [ -z "$TERMUX_VERSION" ]; then
    echo -e "${RED}ERROR: Not running in Termux environment${NC}"
    echo -e "${YELLOW}This script is specifically designed for Termux${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Termux detected: $TERMUX_VERSION${NC}"
echo -e "${GREEN}✓ Android environment validated${NC}"

# Extract environment information
TERMUX_HOME="${TERMUX__HOME:-/data/data/com.termux/files/home}"
TERMUX_PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
ANDROID_VERSION=$(getprop ro.build.version.release 2>/dev/null || echo "unknown")
DEVICE_MODEL=$(getprop ro.product.model 2>/dev/null || echo "unknown")

echo -e "${BLUE}Environment Details:${NC}"
echo -e "  Termux Home: $TERMUX_HOME"
echo -e "  Termux Prefix: $TERMUX_PREFIX"
echo -e "  Android Version: $ANDROID_VERSION"
echo -e "  Device Model: $DEVICE_MODEL"

# Set Termux-specific optimizations
export VARIABOT_TERMUX=true
export VARIABOT_MOBILE_OPTIMIZED=true
export VARIABOT_ANDROID_VERSION="$ANDROID_VERSION"
export VARIABOT_DEVICE_MODEL="$DEVICE_MODEL"

# Memory and performance optimizations based on Android version
case "$ANDROID_VERSION" in
    13*|14*|15*)
        export VARIABOT_MEMORY_LIMIT="2GB"
        export VARIABOT_CPU_THREADS=4
        export VARIABOT_PERFORMANCE_PROFILE="high"
        echo -e "${GREEN}✓ High performance profile (Android $ANDROID_VERSION)${NC}"
        ;;
    11*|12*)
        export VARIABOT_MEMORY_LIMIT="1.5GB"
        export VARIABOT_CPU_THREADS=3
        export VARIABOT_PERFORMANCE_PROFILE="medium"
        echo -e "${YELLOW}✓ Medium performance profile (Android $ANDROID_VERSION)${NC}"
        ;;
    10*)
        export VARIABOT_MEMORY_LIMIT="1GB"
        export VARIABOT_CPU_THREADS=2
        export VARIABOT_PERFORMANCE_PROFILE="conservative"
        echo -e "${YELLOW}✓ Conservative performance profile (Android $ANDROID_VERSION)${NC}"
        ;;
    *)
        export VARIABOT_MEMORY_LIMIT="800MB"
        export VARIABOT_CPU_THREADS=2
        export VARIABOT_PERFORMANCE_PROFILE="minimal"
        echo -e "${RED}⚠ Minimal performance profile (Android $ANDROID_VERSION)${NC}"
        ;;
esac

# Streamlit optimizations for mobile
export STREAMLIT_SERVER_PORT=8080
export STREAMLIT_SERVER_ADDRESS=127.0.0.1
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
export STREAMLIT_THEME_BASE="dark"
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true

# Python optimizations for mobile
export PYTHONOPTIMIZE=1
export PYTHONUNBUFFERED=1
export TMPDIR="$TERMUX_HOME/tmp"

# Create required directories
echo -e "${BLUE}Setting up directories...${NC}"
mkdir -p "$TERMUX_HOME/tmp"
mkdir -p "$TERMUX_HOME/.variabot"
mkdir -p "$TERMUX_HOME/.variabot/models"
mkdir -p "$TERMUX_HOME/.variabot/cache"
mkdir -p "$TERMUX_HOME/.variabot/logs"

# Ensure we're in the VARIABOT directory
if [ ! -f "variabot_universal.py" ]; then
    echo -e "${YELLOW}Searching for VARIABOT installation...${NC}"
    
    # Common installation locations
    VARIABOT_LOCATIONS=(
        "$TERMUX_HOME/VARIABOT"
        "$TERMUX_HOME/variabot"
        "$TERMUX_HOME/HFChatAPI/VARIABOT"
        "$(pwd)"
    )
    
    FOUND=false
    for location in "${VARIABOT_LOCATIONS[@]}"; do
        if [ -f "$location/variabot_universal.py" ]; then
            cd "$location"
            echo -e "${GREEN}✓ Found VARIABOT at: $location${NC}"
            FOUND=true
            break
        fi
    done
    
    if [ "$FOUND" = false ]; then
        echo -e "${RED}ERROR: VARIABOT installation not found${NC}"
        echo -e "${YELLOW}Please clone VARIABOT to $TERMUX_HOME/VARIABOT${NC}"
        echo -e "${YELLOW}Command: git clone https://github.com/spiralgang/VARIABOT.git${NC}"
        exit 1
    fi
fi

# Check Python and dependencies
echo -e "${BLUE}Checking dependencies...${NC}"

if ! command -v python &> /dev/null; then
    echo -e "${RED}ERROR: Python not found${NC}"
    echo -e "${YELLOW}Install with: pkg install python${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python found: $(python --version)${NC}"

# Check for required Python packages
REQUIRED_PACKAGES=(
    "streamlit"
    "gradio_client"
    "transformers"
    "torch"
)

MISSING_PACKAGES=()
for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python -c "import $package" &> /dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    echo -e "${YELLOW}Missing packages: ${MISSING_PACKAGES[*]}${NC}"
    echo -e "${BLUE}Installing missing packages...${NC}"
    pip install --upgrade "${MISSING_PACKAGES[@]}"
fi

echo -e "${GREEN}✓ All dependencies satisfied${NC}"

# Function to launch specific interface
launch_interface() {
    local interface=$1
    local extra_args=$2
    
    echo -e "${PURPLE}Launching VARIABOT with $interface interface...${NC}"
    echo -e "${CYAN}Access URL: http://127.0.0.1:8080${NC}"
    echo -e "${CYAN}Press Ctrl+C to stop${NC}"
    echo ""
    
    case "$interface" in
        "universal")
            python variabot_universal.py --interface web --android-optimize --termux "$extra_args"
            ;;
        "streamlit")
            # Auto-select best available model for device
            if [ -f "st-codet5-small.py" ]; then
                streamlit run st-codet5-small.py --server.port 8080 --server.address 127.0.0.1
            elif [ -f "st-tinyllama-chat.py" ]; then
                streamlit run st-tinyllama-chat.py --server.port 8080 --server.address 127.0.0.1
            elif [ -f "st-Phi3Mini-128k-Chat.py" ]; then
                streamlit run st-Phi3Mini-128k-Chat.py --server.port 8080 --server.address 127.0.0.1
            else
                echo -e "${RED}ERROR: No suitable Streamlit interface found${NC}"
                exit 1
            fi
            ;;
        "terminal")
            python variabot_universal.py --interface terminal --termux "$extra_args"
            ;;
        *)
            echo -e "${RED}ERROR: Unknown interface: $interface${NC}"
            exit 1
            ;;
    esac
}

# Parse command line arguments
INTERFACE="universal"
EXTRA_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --interface|-i)
            INTERFACE="$2"
            shift 2
            ;;
        --model|-m)
            EXTRA_ARGS="$EXTRA_ARGS --model $2"
            shift 2
            ;;
        --help|-h)
            echo "VARIABOT Termux Launcher"
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -i, --interface INTERFACE  Interface type (universal, streamlit, terminal)"
            echo "  -m, --model MODEL         Specific model to use"
            echo "  -h, --help               Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                       # Launch with universal interface"
            echo "  $0 -i streamlit          # Launch with Streamlit"
            echo "  $0 -i terminal           # Launch terminal interface"
            echo "  $0 -m codet5-small       # Launch with specific model"
            exit 0
            ;;
        *)
            echo -e "${RED}ERROR: Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Environment detection and automatic model selection
echo -e "${BLUE}Detecting optimal configuration...${NC}"

# Run environment detection if available
if [ -f "termux_environment.py" ]; then
    python termux_environment.py > /dev/null 2>&1
    echo -e "${GREEN}✓ Environment optimizations applied${NC}"
fi

# Check available memory and select appropriate model
AVAILABLE_MEMORY=$(free -m 2>/dev/null | awk 'NR==2{printf "%.0f", $7/1024}' || echo "unknown")
if [ "$AVAILABLE_MEMORY" != "unknown" ] && [ "$AVAILABLE_MEMORY" -lt 2 ]; then
    echo -e "${YELLOW}⚠ Limited memory detected (${AVAILABLE_MEMORY}GB)${NC}"
    echo -e "${YELLOW}  Recommending lightweight models only${NC}"
    EXTRA_ARGS="$EXTRA_ARGS --force-small-model"
fi

# Final launch
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  VARIABOT Ready for Termux Launch     ${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${BLUE}Configuration:${NC}"
echo -e "  Interface: $INTERFACE"
echo -e "  Memory Limit: $VARIABOT_MEMORY_LIMIT"
echo -e "  CPU Threads: $VARIABOT_CPU_THREADS"
echo -e "  Performance: $VARIABOT_PERFORMANCE_PROFILE"
echo -e "  Android Version: $ANDROID_VERSION"
echo ""

# Launch with error handling
if ! launch_interface "$INTERFACE" "$EXTRA_ARGS"; then
    echo -e "${RED}ERROR: Failed to launch VARIABOT${NC}"
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo -e "  1. Check if all dependencies are installed"
    echo -e "  2. Ensure sufficient storage space (>1GB free)"
    echo -e "  3. Try with --interface terminal for minimal resource usage"
    echo -e "  4. Check logs in $TERMUX_HOME/.variabot/logs/"
    exit 1
fi