# Termux Environment Limitations and Best Practices

## Critical Understanding: Termux is NOT Standard Linux

Termux is a terminal emulator and Linux environment that runs as a **single, unprivileged user** within its own isolated sandbox on Android. This creates fundamental differences from standard Linux distributions that must be respected in all code.

## 1. Filesystem Hierarchy and Pathing

### ❌ What NOT to do:
```bash
# NEVER use hardcoded standard Linux paths
ls /bin
ls /usr/bin  
ls /etc
ls /tmp
ls /home/$USER

# These paths DO NOT EXIST in Termux
```

### ✅ What to do instead:
```bash
# Always use Termux environment variables
ls $PREFIX/bin          # Instead of /bin or /usr/bin
ls $PREFIX/etc          # Instead of /etc  
ls $HOME               # User home (NOT /home/$USER)
ls $TMPDIR             # Temporary directory

# For cross-platform scripts, use variables
BIN_DIR="${PREFIX}/bin"
CONFIG_DIR="${PREFIX}/etc"
USER_HOME="$HOME"
TEMP_DIR="${TMPDIR:-/tmp}"
```

### Python Path Handling:
```python
import os
import tempfile

# ❌ WRONG - Hardcoded paths
log_dir = "/tmp/myapp"
config_file = "/etc/myapp.conf"
binary_path = "/usr/bin/myapp"

# ✅ CORRECT - Environment-aware paths
prefix = os.environ.get('PREFIX', '')
home = os.environ.get('HOME', '')
temp_dir = tempfile.gettempdir()

log_dir = os.path.join(home, '.myapp', 'logs')
config_file = os.path.join(prefix, 'etc', 'myapp.conf') 
binary_path = os.path.join(prefix, 'bin', 'myapp')
```

## 2. Package Management

### ❌ What NOT to do:
```bash
# NEVER use standard Linux package managers
apt-get install package
yum install package  
dnf install package
pacman -S package

# NEVER try to install .deb files manually
dpkg -i package.deb
```

### ✅ What to do instead:
```bash
# Use Termux's pkg command
pkg install package
pkg update
pkg upgrade
pkg search package
pkg show package
pkg uninstall package

# Check if running in Termux first
if [[ -n "$TERMUX_VERSION" ]]; then
    pkg install python
else
    # Handle non-Termux environments
    echo "Not running in Termux"
fi
```

### Package Name Mappings:
Common packages have different names in Termux:

| Standard Linux | Termux Equivalent |
|----------------|-------------------|
| `python3` | `python` |
| `python3-pip` | `python-pip` |
| `gcc` | `clang` |
| `g++` | `clang` |
| `openssh-client` | `openssh` |
| `openssh-server` | `openssh` |
| `netcat` | `netcat-openbsd` |
| `openjdk-11-jdk` | `openjdk-17` |

### Proper Package Manager Implementation:
```python
def install_package(package_name: str) -> bool:
    """Install package with Termux compatibility"""
    
    # Package name mappings
    mappings = {
        'python3': 'python',
        'gcc': 'clang',
        'netcat': 'netcat-openbsd'
    }
    
    # Check if in Termux
    if 'TERMUX_VERSION' not in os.environ:
        print("Not running in Termux")
        return False
    
    # Map package name
    termux_package = mappings.get(package_name, package_name)
    
    # Use pkg command
    result = subprocess.run(['pkg', 'install', termux_package, '-y'], 
                          capture_output=True)
    return result.returncode == 0
```

## 3. User and Permissions Model

### ❌ What NOT to do:
```bash
# NEVER assume multiple users or root access
sudo command
su - otheruser
useradd newuser
chown root:root file

# These commands don't work in Termux's single-user model
```

### ✅ What to do instead:
```bash
# Termux runs as a single user in its own sandbox
# No sudo/su needed for Termux operations
# For root access to Android system, use tsu:

# Check if root access available
if command -v tsu &>/dev/null; then
    tsu -c "command"  # Execute with Android root
else
    echo "No root access available"
fi

# Set file permissions (within Termux sandbox)
chmod 755 file
chmod +x script.sh
```

## 4. Network and Services

### ❌ What NOT to do:
```bash
# NEVER assume standard service management
systemctl start service
service nginx start
/etc/init.d/service start

# These don't exist in Termux
```

### ✅ What to do instead:
```bash
# Start services manually in Termux
sshd  # SSH daemon (custom port 8022)
httpd # HTTP server
nginx # If installed

# Check service status
pgrep sshd
ps aux | grep service_name

# Termux services run as the Termux user
```

## 5. Storage Access

### ❌ What NOT to do:
```bash
# NEVER assume direct filesystem access
ls /sdcard
ls /storage/emulated/0
touch /sdcard/file.txt

# May not work without proper setup
```

### ✅ What to do instead:
```bash
# Setup storage access first
termux-setup-storage

# Then use Termux storage links
ls ~/storage/shared        # Access to shared storage
ls ~/storage/downloads     # Downloads folder
ls ~/storage/dcim         # Camera files

# Check if storage is setup
if [[ -d "$HOME/storage" ]]; then
    echo "Storage access configured"
else
    termux-setup-storage
fi
```

## 6. Cross-Platform Code Patterns

### Environment Detection:
```python
def detect_environment():
    """Detect runtime environment"""
    if 'TERMUX_VERSION' in os.environ:
        return 'termux'
    elif os.path.exists('/etc/debian_version'):
        return 'debian'
    elif os.path.exists('/etc/redhat-release'):
        return 'redhat'
    else:
        return 'unknown'

def get_package_manager():
    """Get appropriate package manager"""
    env = detect_environment()
    
    if env == 'termux':
        return ['pkg']
    elif env == 'debian':
        return ['apt-get']
    elif env == 'redhat':
        return ['yum']
    else:
        return None
```

### Path Utilities:
```python
def get_system_paths():
    """Get system paths for current environment"""
    if 'PREFIX' in os.environ:  # Termux
        return {
            'bin': os.path.join(os.environ['PREFIX'], 'bin'),
            'etc': os.path.join(os.environ['PREFIX'], 'etc'),
            'tmp': os.environ.get('TMPDIR', tempfile.gettempdir()),
            'home': os.environ['HOME']
        }
    else:  # Standard Linux
        return {
            'bin': '/usr/bin',
            'etc': '/etc', 
            'tmp': '/tmp',
            'home': os.path.expanduser('~')
        }
```

## 7. Termux-Specific Commands and APIs

### Available Termux Commands:
```bash
# Termux-specific utilities
termux-setup-storage    # Setup storage access
termux-info            # System information
termux-battery-status  # Battery information
termux-notification    # Send notifications
termux-toast          # Show toast messages
termux-vibrate        # Device vibration
termux-location       # GPS location
termux-sensor         # Device sensors
termux-camera-photo   # Take photos
termux-microphone-record # Record audio
```

### Using Termux APIs:
```python
import subprocess
import json

def get_battery_status():
    """Get battery status using Termux API"""
    try:
        result = subprocess.run(['termux-battery-status'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except:
        pass
    return None

def send_notification(title, content):
    """Send notification using Termux API"""
    subprocess.run(['termux-notification', '--title', title, '--content', content])
```

## 8. Testing Termux Compatibility

### Environment Validation:
```bash
#!/bin/bash
# Termux compatibility check script

check_termux_environment() {
    echo "=== Termux Environment Check ==="
    
    # Check essential variables
    if [[ -z "$TERMUX_VERSION" ]]; then
        echo "❌ TERMUX_VERSION not set"
        return 1
    fi
    
    if [[ -z "$PREFIX" ]]; then
        echo "❌ PREFIX not set" 
        return 1
    fi
    
    if [[ -z "$HOME" ]]; then
        echo "❌ HOME not set"
        return 1
    fi
    
    echo "✅ Termux version: $TERMUX_VERSION"
    echo "✅ Prefix: $PREFIX"
    echo "✅ Home: $HOME"
    
    # Check essential commands
    local commands=("pkg" "python" "git")
    for cmd in "${commands[@]}"; do
        if command -v "$cmd" &>/dev/null; then
            echo "✅ $cmd available"
        else
            echo "❌ $cmd not found"
        fi
    done
    
    return 0
}
```

## 9. Common Mistakes to Avoid

1. **Hardcoded Paths**: Never use `/bin`, `/usr`, `/etc`, `/tmp` directly
2. **Wrong Package Manager**: Never use `apt-get`, `yum`, `dnf` in Termux
3. **Root Assumptions**: Don't assume `sudo` or multi-user capabilities
4. **Service Management**: Don't use `systemctl` or `/etc/init.d`
5. **Standard Directories**: Don't assume standard Linux directory structure
6. **Package Names**: Don't assume standard Linux package names
7. **File Permissions**: Don't assume standard Unix permission model
8. **Network Services**: Don't assume standard service ports or configurations

## 10. Best Practices Summary

1. **Always check environment** before executing platform-specific code
2. **Use environment variables** (`$PREFIX`, `$HOME`, `$TMPDIR`) instead of hardcoded paths  
3. **Map package names** to Termux equivalents
4. **Use `pkg` command** for package management in Termux
5. **Test on actual Termux** before deployment
6. **Provide fallbacks** for non-Termux environments
7. **Document Termux-specific requirements** clearly
8. **Use Termux APIs** for Android integration when available

## References

1. [Termux Wiki](https://wiki.termux.com/)
2. [Termux Packages](https://github.com/termux/termux-packages)
3. [Termux API](https://wiki.termux.com/wiki/Termux:API)
4. [Android App Sandbox](https://developer.android.com/guide/components/activities/activity-lifecycle)
5. [Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html)