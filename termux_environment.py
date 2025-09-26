#!/usr/bin/env python3
"""
Termux Environment Detection and Optimization Module
Specifically designed for Termux 0.119.0-beta.3 environment detection and optimization
"""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

class TermuxEnvironment:
    """Comprehensive Termux environment detection and optimization"""
    
    def __init__(self):
        self.env_vars = os.environ.copy()
        self.termux_detected = self._detect_termux()
        self.android_info = self._get_android_info()
        self.termux_info = self._get_termux_info()
        self.optimization_profile = self._determine_optimization_profile()
    
    def _detect_termux(self) -> bool:
        """Detect if running in Termux environment"""
        termux_indicators = [
            'TERMUX_VERSION' in self.env_vars,
            'TERMUX_APP__PACKAGE_NAME' in self.env_vars,
            'PREFIX' in self.env_vars and '/data/data/com.termux/files/usr' in self.env_vars.get('PREFIX', ''),
            'TERMUX__HOME' in self.env_vars,
            'TERMUX__ROOTFS_DIR' in self.env_vars,
            Path('/data/data/com.termux/files').exists(),
            'libtermux-exec-ld-preload.so' in self.env_vars.get('LD_PRELOAD', '')
        ]
        return any(termux_indicators)
    
    def _get_android_info(self) -> Dict[str, Any]:
        """Extract Android system information"""
        android_info = {
            'runtime_root': self.env_vars.get('ANDROID_RUNTIME_ROOT', ''),
            'external_storage': self.env_vars.get('EXTERNAL_STORAGE', '/sdcard'),
            'system_server_classpath': self.env_vars.get('SYSTEMSERVERCLASSPATH', ''),
            'dex2oat_bootclasspath': self.env_vars.get('DEX2OATBOOTCLASSPATH', ''),
            'is_external_storage': self.env_vars.get('TERMUX_APP__IS_INSTALLED_ON_EXTERNAL_STORAGE', 'false') == 'true'
        }
        
        # Determine Android version from runtime paths
        android_info['android_version'] = self._detect_android_version()
        android_info['sdk_version'] = self._extract_sdk_version()
        
        return android_info
    
    def _get_termux_info(self) -> Dict[str, Any]:
        """Extract Termux-specific information"""
        if not self.termux_detected:
            return {}
        
        return {
            'version': self.env_vars.get('TERMUX_VERSION', 'unknown'),
            'package_name': self.env_vars.get('TERMUX_APP__PACKAGE_NAME', 'com.termux'),
            'app_version': self.env_vars.get('TERMUX_APP__APP_VERSION_NAME', 'unknown'),
            'pid': self.env_vars.get('TERMUX_APP__PID', ''),
            'se_info': self.env_vars.get('TERMUX_APP__SE_INFO', ''),
            'home': self.env_vars.get('TERMUX__HOME', '/data/data/com.termux/files/home'),
            'rootfs': self.env_vars.get('TERMUX__ROOTFS_DIR', '/data/data/com.termux/files'),
            'prefix': self.env_vars.get('PREFIX', '/data/data/com.termux/files/usr'),
            'shell': self.env_vars.get('SHELL', '/data/data/com.termux/files/usr/bin/bash'),
            'java_home': self.env_vars.get('JAVA_HOME', ''),
            'colorterm': self.env_vars.get('COLORTERM', ''),
            'lang': self.env_vars.get('LANG', 'en_US.UTF-8')
        }
    
    def _detect_android_version(self) -> str:
        """Detect Android version from environment"""
        try:
            # Try to get Android version from system properties
            result = subprocess.run(['getprop', 'ro.build.version.release'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        
        # Fallback: analyze runtime paths
        runtime_root = self.env_vars.get('ANDROID_RUNTIME_ROOT', '')
        if 'apex' in runtime_root:
            return '10+'  # Android 10+ uses APEX modules
        
        return 'unknown'
    
    def _extract_sdk_version(self) -> int:
        """Extract target SDK version from SE info"""
        se_info = self.env_vars.get('TERMUX_APP__SE_INFO', '')
        if 'targetSdkVersion=' in se_info:
            try:
                sdk_part = se_info.split('targetSdkVersion=')[1].split(':')[0]
                return int(sdk_part)
            except:
                pass
        return 28  # Default from the provided environment
    
    def _determine_optimization_profile(self) -> Dict[str, Any]:
        """Determine optimal performance profile for current environment"""
        profile = {
            'memory_limit': '1GB',  # Conservative for mobile
            'cpu_threads': 2,       # Limited for mobile
            'model_size_limit': '1.5GB',
            'battery_optimization': True,
            'ui_optimization': 'mobile',
            'storage_optimization': True
        }
        
        if self.termux_detected:
            profile.update({
                'termux_optimized': True,
                'package_management': 'pkg',
                'python_path': f"{self.termux_info.get('prefix', '')}/bin/python",
                'pip_path': f"{self.termux_info.get('prefix', '')}/bin/pip",
                'storage_path': self.termux_info.get('home', '/data/data/com.termux/files/home'),
                'temp_path': f"{self.termux_info.get('home', '')}/tmp"
            })
        
        # Adjust based on Android version
        android_version = self.android_info.get('android_version', 'unknown')
        if android_version.startswith('1'):  # Android 10+
            if int(android_version.split('.')[0]) >= 13:
                profile['memory_limit'] = '2GB'
                profile['cpu_threads'] = 4
            elif int(android_version.split('.')[0]) >= 11:
                profile['memory_limit'] = '1.5GB'
                profile['cpu_threads'] = 3
        
        return profile
    
    def get_optimal_model_config(self) -> Dict[str, Any]:
        """Get optimal AI model configuration for current environment"""
        if not self.termux_detected:
            return {
                'model_size': 'standard',
                'quantization': False,
                'device': 'cpu'
            }
        
        return {
            'model_size': 'small',  # Force small models for Termux
            'quantization': True,   # Enable quantization for memory efficiency
            'device': 'cpu',        # Force CPU for compatibility
            'max_memory': self.optimization_profile['memory_limit'],
            'max_threads': self.optimization_profile['cpu_threads'],
            'fp16': True,           # Use half-precision for memory efficiency
            'cache_size': '100MB'   # Limited cache for storage efficiency
        }
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get optimal UI configuration for current environment"""
        base_config = {
            'responsive': True,
            'touch_friendly': True,
            'dark_mode': True,      # Better for mobile battery
            'minimal_ui': True,     # Reduced complexity for mobile
            'auto_refresh': False   # Prevent battery drain
        }
        
        if self.termux_detected:
            base_config.update({
                'terminal_mode': True,
                'web_interface': True,
                'port': 8080,           # Standard port for Termux
                'host': '127.0.0.1',    # Local only for security
                'compact_layout': True,
                'gesture_support': True
            })
        
        return base_config
    
    def get_installation_commands(self) -> List[str]:
        """Get platform-specific installation commands"""
        if not self.termux_detected:
            return [
                "# Standard Linux installation",
                "pip install -r requirements.txt",
                "python variabot_universal.py --setup"
            ]
        
        return [
            "# Termux-specific installation",
            "pkg update && pkg upgrade -y",
            "pkg install python python-pip git -y",
            "pkg install build-essential cmake -y",
            "pkg install libzmq-dev libjpeg-turbo-dev -y",
            "pip install --upgrade pip setuptools wheel",
            "pip install -r requirements_enhanced.txt",
            "python variabot_universal.py --setup --termux"
        ]
    
    def apply_optimizations(self) -> Dict[str, str]:
        """Apply environment-specific optimizations"""
        optimizations = {}
        
        if self.termux_detected:
            # Set Termux-specific environment variables
            optimizations.update({
                'PYTHONPATH': f"{self.termux_info['prefix']}/lib/python3.10/site-packages",
                'TMPDIR': f"{self.termux_info['home']}/tmp",
                'VARIABOT_TERMUX': 'true',
                'VARIABOT_MOBILE_OPTIMIZED': 'true',
                'VARIABOT_MEMORY_LIMIT': self.optimization_profile['memory_limit'],
                'VARIABOT_CPU_THREADS': str(self.optimization_profile['cpu_threads']),
                'STREAMLIT_SERVER_PORT': '8080',
                'STREAMLIT_SERVER_ADDRESS': '127.0.0.1',
                'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
                'STREAMLIT_SERVER_FILE_WATCHER_TYPE': 'none'  # Reduce resource usage
            })
            
            # Create required directories
            for dir_path in [
                f"{self.termux_info['home']}/tmp",
                f"{self.termux_info['home']}/.variabot",
                f"{self.termux_info['home']}/.variabot/models",
                f"{self.termux_info['home']}/.variabot/cache"
            ]:
                os.makedirs(dir_path, exist_ok=True)
        
        return optimizations
    
    def generate_launch_script(self) -> str:
        """Generate optimized launch script for current environment"""
        if not self.termux_detected:
            return """#!/bin/bash
# Standard launch script
python variabot_universal.py --interface auto
"""
        
        return f"""#!/data/data/com.termux/files/usr/bin/bash
# Termux-optimized launch script for VARIABOT
# Generated for Termux {self.termux_info.get('version', 'unknown')}

export VARIABOT_TERMUX=true
export VARIABOT_MOBILE_OPTIMIZED=true
export VARIABOT_MEMORY_LIMIT={self.optimization_profile['memory_limit']}
export VARIABOT_CPU_THREADS={self.optimization_profile['cpu_threads']}
export TMPDIR={self.termux_info['home']}/tmp
export STREAMLIT_SERVER_PORT=8080
export STREAMLIT_SERVER_ADDRESS=127.0.0.1
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Ensure required directories exist
mkdir -p {self.termux_info['home']}/tmp
mkdir -p {self.termux_info['home']}/.variabot/{{models,cache,logs}}

# Launch VARIABOT with Termux optimizations
cd {self.termux_info['home']}/VARIABOT
python variabot_universal.py --interface web --android-optimize --termux

echo "VARIABOT launched for Termux on Android {self.android_info.get('android_version', 'unknown')}"
echo "Access at: http://127.0.0.1:8080"
"""
    
    def get_environment_report(self) -> Dict[str, Any]:
        """Generate comprehensive environment report"""
        return {
            'platform': {
                'system': platform.system(),
                'machine': platform.machine(),
                'python_version': platform.python_version(),
                'termux_detected': self.termux_detected
            },
            'android_info': self.android_info,
            'termux_info': self.termux_info,
            'optimization_profile': self.optimization_profile,
            'model_config': self.get_optimal_model_config(),
            'ui_config': self.get_ui_config(),
            'installation_commands': self.get_installation_commands(),
            'launch_script': self.generate_launch_script(),
            'environment_variables': {k: v for k, v in self.env_vars.items() 
                                    if k.startswith(('TERMUX', 'ANDROID', 'PREFIX', 'HOME', 'JAVA'))}
        }

def main():
    """Main function for testing environment detection"""
    env = TermuxEnvironment()
    report = env.get_environment_report()
    
    print("VARIABOT Environment Detection Report")
    print("=" * 50)
    print(f"Termux Detected: {report['platform']['termux_detected']}")
    print(f"Android Version: {report['android_info']['android_version']}")
    print(f"Termux Version: {report['termux_info'].get('version', 'N/A')}")
    print(f"Optimization Profile: {report['optimization_profile']}")
    
    if env.termux_detected:
        print("\nTermux-Specific Information:")
        print(f"  Home: {report['termux_info']['home']}")
        print(f"  Prefix: {report['termux_info']['prefix']}")
        print(f"  Java Home: {report['termux_info'].get('java_home', 'Not set')}")
        
        print("\nOptimal Model Configuration:")
        model_config = report['model_config']
        print(f"  Model Size: {model_config['model_size']}")
        print(f"  Memory Limit: {model_config['max_memory']}")
        print(f"  CPU Threads: {model_config['max_threads']}")
        
        # Apply optimizations
        optimizations = env.apply_optimizations()
        print(f"\nApplied {len(optimizations)} environment optimizations")
        
        # Generate launch script
        script_path = f"{env.termux_info['home']}/launch_variabot.sh"
        with open(script_path, 'w') as f:
            f.write(env.generate_launch_script())
        os.chmod(script_path, 0o755)
        print(f"Generated launch script: {script_path}")

if __name__ == "__main__":
    main()