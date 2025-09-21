#!/data/data/com.termux/files/usr/bin/bash
#
# VARIABOT Android/Termux Installation Script
# Comprehensive setup for Android 10+ and Termux environments
# Handles restricted environment operations and mobile device constraints
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Detect environment
detect_environment() {
    log "Detecting environment..."
    
    if [[ -n "$PREFIX" && "$PREFIX" == *"com.termux"* ]]; then
        ENV_TYPE="termux"
        log "Detected: Termux environment"
    elif [[ -f "/system/build.prop" ]]; then
        ENV_TYPE="android_native"
        log "Detected: Native Android environment"
    else
        ENV_TYPE="linux"
        log "Detected: Linux environment"
    fi
    
    # Get Android version
    if [[ "$ENV_TYPE" == "termux" ]] || [[ "$ENV_TYPE" == "android_native" ]]; then
        if command -v termux-info >/dev/null 2>&1; then
            ANDROID_VERSION=$(termux-info | grep -o '"android_version": [0-9]*' | grep -o '[0-9]*')
            log "Android version: $ANDROID_VERSION"
        else
            ANDROID_VERSION="unknown"
            warn "Could not determine Android version"
        fi
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Python
    if ! command -v python >/dev/null 2>&1; then
        error "Python not found. Please install Python 3.8+"
    fi
    
    PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log "Python version: $PYTHON_VERSION"
    
    # Check if Python version is adequate
    if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l 2>/dev/null || echo "0") -eq 0 ]]; then
        error "Python 3.8+ required. Current version: $PYTHON_VERSION"
    fi
    
    # Check available storage
    AVAILABLE_SPACE=$(df -BM . | awk 'NR==2 {print $4}' | sed 's/M//')
    log "Available storage: ${AVAILABLE_SPACE}MB"
    
    if [[ "$AVAILABLE_SPACE" -lt 500 ]]; then
        error "Insufficient storage. Need at least 500MB, available: ${AVAILABLE_SPACE}MB"
    fi
    
    # Check memory
    if [[ "$ENV_TYPE" == "termux" ]]; then
        # Termux-specific memory check
        MEM_INFO=$(cat /proc/meminfo | grep MemTotal | awk '{print $2}')
        MEM_GB=$((MEM_INFO / 1024 / 1024))
        log "Available memory: ${MEM_GB}GB"
        
        if [[ "$MEM_GB" -lt 2 ]]; then
            warn "Low memory detected (${MEM_GB}GB). Will use lightweight configuration."
            USE_LIGHTWEIGHT=true
        fi
    fi
}

# Install Termux packages
install_termux_packages() {
    if [[ "$ENV_TYPE" != "termux" ]]; then
        return
    fi
    
    log "Installing Termux packages..."
    
    # Update package lists
    pkg update -y || warn "Package update failed"
    
    # Essential packages
    TERMUX_PACKAGES=(
        "python"
        "python-pip"
        "git"
        "wget"
        "curl"
        "openssh"
        "termux-api"
        "build-essential"
        "libffi"
        "openssl"
        "libjpeg-turbo"
        "libpng"
        "freetype"
        "pkg-config"
    )
    
    for package in "${TERMUX_PACKAGES[@]}"; do
        log "Installing $package..."
        pkg install -y "$package" || warn "Failed to install $package"
    done
    
    # Install additional tools for AI/ML
    log "Installing additional tools..."
    pkg install -y clang cmake rust || warn "Some build tools failed to install"
}

# Setup Python environment
setup_python_environment() {
    log "Setting up Python environment..."
    
    # Upgrade pip
    python -m pip install --upgrade pip || error "Failed to upgrade pip"
    
    # Create virtual environment for isolation
    if [[ ! -d "venv" ]]; then
        log "Creating virtual environment..."
        python -m venv venv || warn "Virtual environment creation failed, continuing without isolation"
    fi
    
    # Activate virtual environment if it exists
    if [[ -d "venv" ]]; then
        source venv/bin/activate || warn "Could not activate virtual environment"
        log "Virtual environment activated"
    fi
    
    # Install wheel and setuptools for better package compilation
    python -m pip install wheel setuptools || warn "Failed to install build tools"
}

# Install Python dependencies with mobile optimizations
install_python_dependencies() {
    log "Installing Python dependencies..."
    
    # Base requirements for all environments
    BASE_DEPS=(
        "streamlit>=1.24.0"
        "gradio-client>=0.16.0"
        "huggingface_hub>=0.17.0"
        "requests>=2.31.0"
        "numpy>=1.21.0"
        "pandas>=1.3.0"
        "pillow>=8.0.0"
        "python-dotenv>=0.19.0"
        "loguru>=0.6.0"
        "psutil>=5.8.0"
        "click>=8.0.0"
        "pyyaml>=6.0"
    )
    
    # Lightweight dependencies for constrained environments
    LIGHTWEIGHT_DEPS=(
        "streamlit==1.24.0"
        "gradio-client==0.16.0"
        "huggingface_hub==0.17.0"
        "requests==2.31.0"
        "numpy==1.21.6"
        "pillow==8.4.0"
        "loguru==0.6.0"
    )
    
    # Mobile-specific dependencies
    MOBILE_DEPS=(
        "kivy>=2.1.0"
        "plyer>=2.1.0"
        "flask>=2.0.0"
    )
    
    # Android/Termux specific dependencies
    ANDROID_DEPS=(
        "pyjnius>=1.4.0"
        "buildozer>=1.4.0"
    )
    
    # Choose dependency set based on environment and resources
    if [[ "$USE_LIGHTWEIGHT" == "true" ]] || [[ "$ANDROID_VERSION" -lt 12 ]]; then
        DEPS_TO_INSTALL=("${LIGHTWEIGHT_DEPS[@]}")
        log "Using lightweight dependency set"
    else
        DEPS_TO_INSTALL=("${BASE_DEPS[@]}")
        log "Using full dependency set"
    fi
    
    # Install base dependencies
    for dep in "${DEPS_TO_INSTALL[@]}"; do
        log "Installing $dep..."
        python -m pip install "$dep" --no-cache-dir || warn "Failed to install $dep"
    done
    
    # Install mobile dependencies if on Android
    if [[ "$ENV_TYPE" == "termux" ]] || [[ "$ENV_TYPE" == "android_native" ]]; then
        log "Installing mobile-specific dependencies..."
        for dep in "${MOBILE_DEPS[@]}"; do
            python -m pip install "$dep" --no-cache-dir || warn "Failed to install mobile dependency $dep"
        done
        
        # Try to install Android-specific packages
        for dep in "${ANDROID_DEPS[@]}"; do
            log "Installing Android dependency $dep..."
            python -m pip install "$dep" --no-cache-dir || warn "Failed to install Android dependency $dep"
        done
    fi
    
    # Install PyTorch with mobile optimizations
    install_pytorch_mobile
}

# Install PyTorch optimized for mobile
install_pytorch_mobile() {
    log "Installing PyTorch for mobile..."
    
    if [[ "$ENV_TYPE" == "termux" ]]; then
        # Use CPU-only PyTorch for Termux
        python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir || {
            warn "Failed to install full PyTorch, trying lightweight version..."
            python -m pip install torch==1.13.1+cpu torchvision==0.14.1+cpu --index-url https://download.pytorch.org/whl/cpu --no-cache-dir || {
                warn "PyTorch installation failed, will use transformers without torch backend"
            }
        }
    else
        # Standard PyTorch installation
        python -m pip install torch torchvision torchaudio --no-cache-dir || warn "PyTorch installation failed"
    fi
}

# Configure environment variables
configure_environment() {
    log "Configuring environment variables..."
    
    # Create .env file if it doesn't exist
    if [[ ! -f ".env" ]]; then
        cat > .env << EOF
# VARIABOT Environment Configuration
# Generated on $(date)

# Platform Configuration
VARIABOT_PLATFORM=$ENV_TYPE
VARIABOT_ANDROID_VERSION=$ANDROID_VERSION

# Performance Configuration
VARIABOT_LIGHTWEIGHT_MODE=$USE_LIGHTWEIGHT
VARIABOT_MAX_MEMORY_MB=1024
VARIABOT_MAX_THREADS=2

# Streamlit Configuration
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_SERVER_FILE_WATCHER_TYPE=none

# HuggingFace Configuration
HF_HOME=${HOME}/.cache/huggingface
TRANSFORMERS_CACHE=${HOME}/.cache/transformers

# Security Configuration
VARIABOT_ENABLE_CORS=true
VARIABOT_API_RATE_LIMIT=100

EOF
        log "Created .env configuration file"
    fi
    
    # Set Termux-specific environment variables
    if [[ "$ENV_TYPE" == "termux" ]]; then
        export TMPDIR="$PREFIX/tmp"
        export PYTHONPATH="$PREFIX/lib/python3.11/site-packages:$PYTHONPATH"
        log "Set Termux-specific environment variables"
    fi
}

# Setup storage and permissions
setup_storage_permissions() {
    if [[ "$ENV_TYPE" != "termux" ]]; then
        return
    fi
    
    log "Setting up storage and permissions..."
    
    # Request storage permissions
    termux-setup-storage || warn "Could not setup storage access"
    
    # Create necessary directories
    mkdir -p "$HOME/.cache/huggingface"
    mkdir -p "$HOME/.cache/transformers"
    mkdir -p "$HOME/.variabot/logs"
    mkdir -p "$HOME/.variabot/models"
    mkdir -p "$HOME/.variabot/config"
    
    log "Created application directories"
}

# Optimize for mobile performance
optimize_mobile_performance() {
    if [[ "$ENV_TYPE" != "termux" ]] && [[ "$ENV_TYPE" != "android_native" ]]; then
        return
    fi
    
    log "Applying mobile performance optimizations..."
    
    # Create mobile-optimized configuration
    cat > mobile_config.py << 'EOF'
"""
Mobile performance optimizations for VARIABOT
Auto-applied for Android/Termux environments
"""

import os
import gc
import sys

# Memory management
def optimize_memory():
    """Aggressive memory optimization for mobile devices."""
    gc.collect()
    
    # Set garbage collection thresholds for frequent cleanup
    gc.set_threshold(400, 5, 5)
    
    # Limit tensor operations memory
    try:
        import torch
        torch.set_num_threads(2)
        if hasattr(torch.backends, 'cudnn'):
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

# CPU optimization
def optimize_cpu():
    """Optimize CPU usage for mobile devices."""
    # Limit OpenMP threads
    os.environ['OMP_NUM_THREADS'] = '2'
    os.environ['MKL_NUM_THREADS'] = '2'
    os.environ['NUMEXPR_NUM_THREADS'] = '2'

# Network optimization
def optimize_network():
    """Optimize network usage for mobile data."""
    # Disable automatic model downloads
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['HF_DATASETS_OFFLINE'] = '1'

# Apply all optimizations
def apply_mobile_optimizations():
    """Apply all mobile optimizations."""
    optimize_memory()
    optimize_cpu()
    optimize_network()
    
    print("🔧 Mobile optimizations applied")

# Auto-apply if running on mobile
if any(indicator in os.environ.get('PREFIX', '') for indicator in ['termux', 'android']):
    apply_mobile_optimizations()
EOF
    
    log "Created mobile optimization module"
}

# Test installation
test_installation() {
    log "Testing installation..."
    
    # Test Python imports
    python -c "
import sys
print(f'Python version: {sys.version}')

# Test core dependencies
try:
    import streamlit
    print('✅ Streamlit imported successfully')
except ImportError as e:
    print(f'❌ Streamlit import failed: {e}')

try:
    from gradio_client import Client
    print('✅ Gradio client imported successfully')
except ImportError as e:
    print(f'❌ Gradio client import failed: {e}')

try:
    import numpy
    print('✅ NumPy imported successfully')
except ImportError as e:
    print(f'❌ NumPy import failed: {e}')

try:
    from variabot_integration import initialize_integration
    print('✅ VARIABOT integration system imported successfully')
except ImportError as e:
    print(f'❌ VARIABOT integration import failed: {e}')

print('🧪 Installation test completed')
" || error "Installation test failed"
    
    # Test VARIABOT universal interface
    if [[ -f "variabot_universal.py" ]]; then
        python variabot_universal.py --interface terminal --help >/dev/null 2>&1 && {
            log "✅ VARIABOT universal interface working"
        } || {
            warn "❌ VARIABOT universal interface test failed"
        }
    fi
}

# Create launcher scripts
create_launchers() {
    log "Creating launcher scripts..."
    
    # Create main launcher
    cat > launch_variabot.sh << 'EOF'
#!/bin/bash
#
# VARIABOT Launcher Script
# Auto-detects best interface for current platform
#

cd "$(dirname "$0")"

# Load environment
if [[ -f ".env" ]]; then
    source .env
fi

# Activate virtual environment if available
if [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
fi

# Apply mobile optimizations
python -c "
try:
    from mobile_config import apply_mobile_optimizations
    apply_mobile_optimizations()
except ImportError:
    pass
"

# Launch VARIABOT
python variabot_universal.py "$@"
EOF
    
    chmod +x launch_variabot.sh
    
    # Create Termux-specific launcher
    if [[ "$ENV_TYPE" == "termux" ]]; then
        cat > launch_termux.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
#
# Termux-optimized VARIABOT launcher
#

# Setup Termux environment
export TMPDIR="$PREFIX/tmp"
export PYTHONPATH="$PREFIX/lib/python3.11/site-packages:$PYTHONPATH"

# Launch with web interface (best for Termux)
./launch_variabot.sh --interface web --android-optimize
EOF
        
        chmod +x launch_termux.sh
        log "Created Termux-specific launcher"
    fi
    
    log "Created launcher scripts"
}

# Main installation function
main() {
    log "🤖 VARIABOT Android/Termux Installation Starting..."
    log "================================================="
    
    detect_environment
    check_requirements
    
    if [[ "$ENV_TYPE" == "termux" ]]; then
        install_termux_packages
    fi
    
    setup_python_environment
    install_python_dependencies
    configure_environment
    setup_storage_permissions
    optimize_mobile_performance
    create_launchers
    test_installation
    
    log "================================================="
    log "🎉 VARIABOT Installation Completed Successfully!"
    log ""
    log "📱 Platform: $ENV_TYPE"
    log "🤖 Android Version: $ANDROID_VERSION"
    log "💾 Lightweight Mode: $USE_LIGHTWEIGHT"
    log ""
    log "🚀 Quick Start:"
    log "   ./launch_variabot.sh --interface auto"
    log ""
    if [[ "$ENV_TYPE" == "termux" ]]; then
        log "📱 Termux Optimized:"
        log "   ./launch_termux.sh"
        log ""
    fi
    log "🔧 For more options:"
    log "   ./launch_variabot.sh --help"
    log ""
    log "📚 Documentation: reference_vault/"
    log "🐛 Issues: Check logs in ~/.variabot/logs/"
}

# Run main installation
main "$@"