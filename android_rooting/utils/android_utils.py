#!/usr/bin/env python3
"""
Android System Utilities
See: /reference_vault/PRODUCTION_GRADE_STANDARDS.md#android-utils

Comprehensive Android system information and utilities for rooting operations.
Platform: Android 10-14, Termux environment
Security: System analysis and environment detection
Performance: Lightweight system calls and efficient data collection
"""

import os
import subprocess
import json
import logging
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class AndroidVersion(Enum):
    """Android version enumeration"""
    UNKNOWN = "unknown"
    ANDROID_10 = "10"
    ANDROID_11 = "11" 
    ANDROID_12 = "12"
    ANDROID_13 = "13"
    ANDROID_14 = "14"

@dataclass
class SystemInfo:
    """Android system information structure"""
    android_version: str
    api_level: int
    device_model: str
    manufacturer: str
    architecture: str
    kernel_version: str
    build_type: str
    security_patch: str
    bootloader_version: str
    radio_version: str

@dataclass
class TermuxInfo:
    """Termux environment information"""
    termux_version: str
    termux_home: str
    termux_prefix: str
    shell: str
    java_home: Optional[str]
    api_package: bool

@dataclass
class MemoryInfo:
    """Memory and resource information"""
    total_memory: int
    available_memory: int
    used_memory: int
    memory_percentage: float
    swap_total: int
    swap_used: int

class AndroidSystemInfo:
    """
    Comprehensive Android system information collector.
    
    Provides detailed system analysis for Android rooting operations with
    Termux environment detection and resource monitoring.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._system_info: Optional[SystemInfo] = None
        self._termux_info: Optional[TermuxInfo] = None
        self._memory_info: Optional[MemoryInfo] = None
        
        # Initialize system information
        self._collect_system_info()
    
    def _collect_system_info(self):
        """Collect comprehensive system information"""
        try:
            self._system_info = self._get_android_system_info()
            self._termux_info = self._get_termux_info()
            self._memory_info = self._get_memory_info()
        except Exception as e:
            self.logger.warning(f"Failed to collect system info: {str(e)}")
    
    def _get_android_system_info(self) -> SystemInfo:
        """Collect Android system information"""
        try:
            return SystemInfo(
                android_version=self._get_property("ro.build.version.release", "unknown"),
                api_level=int(self._get_property("ro.build.version.sdk", "0")),
                device_model=self._get_property("ro.product.model", "unknown"),
                manufacturer=self._get_property("ro.product.manufacturer", "unknown"),
                architecture=platform.machine(),
                kernel_version=platform.release(),
                build_type=self._get_property("ro.build.type", "unknown"),
                security_patch=self._get_property("ro.build.version.security_patch", "unknown"),
                bootloader_version=self._get_property("ro.bootloader", "unknown"),
                radio_version=self._get_property("ro.baseband", "unknown")
            )
        except Exception as e:
            self.logger.warning(f"Failed to get Android system info: {str(e)}")
            return SystemInfo("unknown", 0, "unknown", "unknown", "unknown", 
                            "unknown", "unknown", "unknown", "unknown", "unknown")
    
    def _get_termux_info(self) -> TermuxInfo:
        """Collect Termux environment information"""
        try:
            return TermuxInfo(
                termux_version=os.environ.get("TERMUX_VERSION", "unknown"),
                termux_home=os.environ.get("TERMUX__HOME", "/data/data/com.termux/files/home"),
                termux_prefix=os.environ.get("PREFIX", "/data/data/com.termux/files/usr"),
                shell=os.environ.get("SHELL", "/bin/bash"),
                java_home=os.environ.get("JAVA_HOME"),
                api_package=self._check_termux_api()
            )
        except Exception as e:
            self.logger.warning(f"Failed to get Termux info: {str(e)}")
            return TermuxInfo("unknown", "unknown", "unknown", "unknown", None, False)
    
    def _get_memory_info(self) -> MemoryInfo:
        """Collect memory and resource information"""
        try:
            # Read /proc/meminfo
            meminfo = {}
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        # Extract numeric value (remove kB and whitespace)
                        numeric_value = ''.join(filter(str.isdigit, value))
                        meminfo[key.strip()] = int(numeric_value) if numeric_value else 0
            
            total_memory = meminfo.get('MemTotal', 0) * 1024  # Convert from kB to bytes
            available_memory = meminfo.get('MemAvailable', 0) * 1024
            used_memory = total_memory - available_memory
            memory_percentage = (used_memory / total_memory * 100) if total_memory > 0 else 0
            
            return MemoryInfo(
                total_memory=total_memory,
                available_memory=available_memory,
                used_memory=used_memory,
                memory_percentage=memory_percentage,
                swap_total=meminfo.get('SwapTotal', 0) * 1024,
                swap_used=(meminfo.get('SwapTotal', 0) - meminfo.get('SwapFree', 0)) * 1024
            )
        except Exception as e:
            self.logger.warning(f"Failed to get memory info: {str(e)}")
            return MemoryInfo(0, 0, 0, 0.0, 0, 0)
    
    def _get_property(self, prop_name: str, default: str = "") -> str:
        """Get Android system property"""
        try:
            result = subprocess.run(
                ["getprop", prop_name],
                capture_output=True,
                text=True,
                timeout=3
            )
            return result.stdout.strip() if result.returncode == 0 else default
        except Exception:
            return default
    
    def _check_termux_api(self) -> bool:
        """Check if Termux:API is installed"""
        try:
            result = subprocess.run(
                ["termux-info"],
                capture_output=True,
                text=True,
                timeout=3
            )
            return result.returncode == 0
        except Exception:
            return False
    
    # Public interface methods
    
    def get_android_version(self) -> str:
        """Get Android version string"""
        return self._system_info.android_version if self._system_info else "unknown"
    
    def get_android_api_level(self) -> int:
        """Get Android API level"""
        return self._system_info.api_level if self._system_info else 0
    
    def get_device_model(self) -> str:
        """Get device model"""
        return self._system_info.device_model if self._system_info else "unknown"
    
    def get_manufacturer(self) -> str:
        """Get device manufacturer"""
        return self._system_info.manufacturer if self._system_info else "unknown"
    
    def get_architecture(self) -> str:
        """Get device architecture"""
        return self._system_info.architecture if self._system_info else "unknown"
    
    def get_termux_version(self) -> str:
        """Get Termux version"""
        return self._termux_info.termux_version if self._termux_info else "unknown"
    
    def get_termux_home(self) -> str:
        """Get Termux home directory"""
        return self._termux_info.termux_home if self._termux_info else "/data/data/com.termux/files/home"
    
    def get_termux_prefix(self) -> str:
        """Get Termux prefix directory"""
        return self._termux_info.termux_prefix if self._termux_info else "/data/data/com.termux/files/usr"
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information as dictionary"""
        if not self._memory_info:
            return {}
        
        return {
            "total_memory_mb": self._memory_info.total_memory // (1024 * 1024),
            "available_memory_mb": self._memory_info.available_memory // (1024 * 1024),
            "used_memory_mb": self._memory_info.used_memory // (1024 * 1024),
            "memory_percentage": round(self._memory_info.memory_percentage, 2),
            "swap_total_mb": self._memory_info.swap_total // (1024 * 1024),
            "swap_used_mb": self._memory_info.swap_used // (1024 * 1024)
        }
    
    def check_root_status(self) -> Dict[str, Any]:
        """Quick root status check"""
        root_indicators = {
            "su_binary": False,
            "superuser_app": False,
            "magisk": False,
            "write_access": False,
            "selinux_permissive": False
        }
        
        # Check for SU binary
        su_paths = ["/system/bin/su", "/system/xbin/su", "/vendor/bin/su"]
        for path in su_paths:
            if os.path.exists(path):
                root_indicators["su_binary"] = True
                break
        
        # Check for Magisk
        magisk_paths = ["/data/adb/magisk", "/sbin/.magisk"]
        for path in magisk_paths:
            if os.path.exists(path):
                root_indicators["magisk"] = True
                break
        
        # Check SELinux status
        try:
            result = subprocess.run(
                ["getenforce"],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0 and "permissive" in result.stdout.lower():
                root_indicators["selinux_permissive"] = True
        except:
            pass
        
        # Check write access to system
        try:
            test_file = "/system/.write_test"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            root_indicators["write_access"] = True
        except:
            pass
        
        return root_indicators
    
    def is_android_version_supported(self, min_version: str = "10") -> bool:
        """Check if Android version meets minimum requirements"""
        try:
            current_version = self.get_android_version()
            return current_version >= min_version
        except:
            return False
    
    def is_termux_environment(self) -> bool:
        """Check if running in Termux environment"""
        termux_indicators = [
            os.environ.get("TERMUX_APP__PACKAGE_NAME") == "com.termux",
            "termux" in os.environ.get("PREFIX", "").lower(),
            os.path.exists("/data/data/com.termux/files")
        ]
        return any(termux_indicators)
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive system summary"""
        return {
            "android": {
                "version": self.get_android_version(),
                "api_level": self.get_android_api_level(),
                "device": f"{self.get_manufacturer()} {self.get_device_model()}",
                "architecture": self.get_architecture()
            },
            "termux": {
                "version": self.get_termux_version(),
                "environment": self.is_termux_environment(),
                "home": self.get_termux_home(),
                "prefix": self.get_termux_prefix()
            },
            "resources": self.get_memory_info(),
            "root_indicators": self.check_root_status(),
            "supported": self.is_android_version_supported()
        }
    
    def optimize_for_device(self) -> Dict[str, Any]:
        """Get device-specific optimization recommendations"""
        recommendations = {
            "memory_optimization": [],
            "cpu_optimization": [],
            "storage_optimization": [],
            "performance_profile": "conservative"
        }
        
        memory_info = self.get_memory_info()
        total_memory_gb = memory_info.get("total_memory_mb", 0) / 1024
        
        # Memory-based recommendations
        if total_memory_gb < 2:
            recommendations["memory_optimization"] = [
                "Use lightweight models only",
                "Enable swap space",
                "Limit concurrent operations",
                "Use memory compression"
            ]
            recommendations["performance_profile"] = "minimal"
        elif total_memory_gb < 4:
            recommendations["memory_optimization"] = [
                "Monitor memory usage closely",
                "Use medium-sized models",
                "Enable background app limits"
            ]
            recommendations["performance_profile"] = "conservative"
        else:
            recommendations["memory_optimization"] = [
                "Full featured models supported",
                "Parallel operations allowed"
            ]
            recommendations["performance_profile"] = "high_performance"
        
        # Android version specific optimizations
        android_version = self.get_android_version()
        if android_version >= "13":
            recommendations["cpu_optimization"] = [
                "Use latest Android APIs",
                "Enable GPU acceleration if available",
                "Utilize background processing"
            ]
        elif android_version >= "11":
            recommendations["cpu_optimization"] = [
                "Use compatible APIs",
                "Moderate background processing"
            ]
        else:
            recommendations["cpu_optimization"] = [
                "Use legacy-compatible methods",
                "Minimal background processing"
            ]
        
        return recommendations

def check_termux_environment() -> bool:
    """Standalone function to check Termux environment"""
    return AndroidSystemInfo().is_termux_environment()

def get_android_info() -> Dict[str, Any]:
    """Standalone function to get Android information"""
    return AndroidSystemInfo().get_system_summary()

def optimize_for_mobile() -> Dict[str, Any]:
    """Standalone function to get mobile optimization recommendations"""
    return AndroidSystemInfo().optimize_for_device()

# References
# [1] Internal: /reference_vault/PRODUCTION_GRADE_STANDARDS.md#android-utils
# [2] Internal: /reference_vault/COPILOT_CORE_INSTRUCTIONS.md#system-analysis
# [3] External: Android Developer Documentation - System information APIs
# [4] Standard: Linux /proc filesystem documentation