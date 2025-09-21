#!/usr/bin/env python3
"""
Termux Compatibility Layer
Provides compatibility functions for Android/Termux environments

This module provides:
- Termux-specific path handling
- Android property access
- Permission management
- Storage access utilities
- Network configuration helpers

Compatible with: Termux on Android 10+, Python 3.7+
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
import tempfile
import shutil


class TermuxEnvironment:
    """Termux environment detection and management"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_termux = self._detect_termux()
        # Always use $PREFIX and $HOME from environment - never hardcode paths
        self.prefix = os.environ.get("PREFIX", "")
        self.home = os.environ.get("HOME", "")

        # Validate Termux environment variables
        if not self.prefix or not self.home:
            self.logger.warning(
                "PREFIX or HOME not set - may not be in Termux environment"
            )

    def _detect_termux(self) -> bool:
        """Detect if running in Termux environment"""
        return (
            "TERMUX_VERSION" in os.environ
            or "com.termux" in os.environ.get("PREFIX", "")
            or os.environ.get("PREFIX", "").startswith("/data/data/com.termux")
        )

    def get_termux_info(self) -> Dict[str, str]:
        """Get Termux environment information"""
        info = {
            "is_termux": self.is_termux,
            "version": os.environ.get("TERMUX_VERSION", "unknown"),
            "prefix": self.prefix,
            "home": self.home,
            "shell": os.environ.get("SHELL", f"{self.prefix}/bin/bash"),
            "path": os.environ.get("PATH", ""),
        }

        if self.is_termux:
            try:
                # Get additional Termux info
                result = subprocess.run(["termux-info"], capture_output=True, text=True)
                if result.returncode == 0:
                    info["termux_info"] = result.stdout
            except Exception:
                pass

        return info

    def get_android_info(self) -> Dict[str, str]:
        """Get Android system information"""
        info = {}

        # Android properties
        properties = [
            "ro.build.version.release",
            "ro.build.version.sdk",
            "ro.product.model",
            "ro.product.manufacturer",
            "ro.product.cpu.abi",
            "ro.kernel.version",
        ]

        for prop in properties:
            try:
                result = subprocess.run(
                    ["getprop", prop], capture_output=True, text=True
                )
                if result.returncode == 0:
                    info[prop] = result.stdout.strip()
            except Exception:
                info[prop] = "unknown"

        return info


class AndroidProperty:
    """Android system property management"""

    @staticmethod
    def get(property_name: str, default: str = "") -> str:
        """Get Android system property"""
        try:
            result = subprocess.run(
                ["getprop", property_name], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return default

    @staticmethod
    def set(property_name: str, value: str) -> bool:
        """Set Android system property (requires root)"""
        try:
            result = subprocess.run(
                ["setprop", property_name, value], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def list_all() -> Dict[str, str]:
        """List all Android properties"""
        properties = {}
        try:
            result = subprocess.run(
                ["getprop"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if ":" in line and "[" in line and "]" in line:
                        # Parse format: [property]: [value]
                        parts = line.strip().split("]: [")
                        if len(parts) == 2:
                            prop = parts[0].lstrip("[")
                            value = parts[1].rstrip("]")
                            properties[prop] = value
        except Exception:
            pass
        return properties


class StorageManager:
    """Termux storage access management"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.termux_env = TermuxEnvironment()

    def setup_storage_access(self) -> bool:
        """Setup Termux storage access"""
        if not self.termux_env.is_termux:
            self.logger.warning("Not running in Termux, storage setup skipped")
            return False

        try:
            # Check if storage is already setup
            storage_path = os.path.join(self.termux_env.home, "storage")
            if os.path.exists(storage_path):
                self.logger.info("Termux storage already configured")
                return True

            # Setup storage access
            result = subprocess.run(
                ["termux-setup-storage"], capture_output=True, timeout=30
            )

            if result.returncode == 0:
                self.logger.info("Termux storage access configured")
                return True
            else:
                self.logger.error(f"Storage setup failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Storage setup error: {e}")
            return False

    def get_storage_paths(self) -> Dict[str, str]:
        """Get available storage paths"""
        paths = {
            "home": self.termux_env.home,
            "tmp": (
                os.path.join(self.termux_env.prefix, "tmp")
                if self.termux_env.prefix
                else tempfile.gettempdir()
            ),
            "cache": (
                os.path.join(self.termux_env.home, ".cache")
                if self.termux_env.home
                else tempfile.gettempdir()
            ),
        }

        if self.termux_env.is_termux:
            storage_base = os.path.join(self.termux_env.home, "storage")
            if os.path.exists(storage_base):
                # Add Termux storage paths
                termux_paths = {
                    "shared": os.path.join(storage_base, "shared"),
                    "downloads": os.path.join(storage_base, "downloads"),
                    "dcim": os.path.join(storage_base, "dcim"),
                    "pictures": os.path.join(storage_base, "pictures"),
                    "music": os.path.join(storage_base, "music"),
                    "movies": os.path.join(storage_base, "movies"),
                }
                paths.update(termux_paths)

        return paths

    def create_temp_dir(self, prefix: str = "android_root") -> str:
        """Create temporary directory"""
        try:
            temp_dir = tempfile.mkdtemp(prefix=f"{prefix}_")
            self.logger.debug(f"Created temp directory: {temp_dir}")
            return temp_dir
        except Exception as e:
            self.logger.error(f"Failed to create temp directory: {e}")
            # Fallback to basic temp path
            # Use system temp directory as fallback
            fallback_dir = os.path.join(
                tempfile.gettempdir(), f"{prefix}_{os.getpid()}"
            )
            os.makedirs(fallback_dir, exist_ok=True)
            return fallback_dir


class PackageManager:
    """Termux package management utilities"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.termux_env = TermuxEnvironment()

    def is_package_installed(self, package_name: str) -> bool:
        """Check if package is installed"""
        if not self.termux_env.is_termux:
            # On regular Android, check if binary exists
            return shutil.which(package_name) is not None

        try:
            result = subprocess.run(
                ["pkg", "list-installed", package_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0 and package_name in result.stdout
        except Exception:
            return False

    def install_package(self, package_name: str) -> bool:
        """Install package via pkg"""
        if not self.termux_env.is_termux:
            self.logger.warning("Package installation only available in Termux")
            return False

        try:
            self.logger.info(f"Installing package: {package_name}")
            result = subprocess.run(
                ["pkg", "install", package_name, "-y"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                self.logger.info(f"Package {package_name} installed successfully")
                return True
            else:
                self.logger.error(f"Package installation failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Package installation error: {e}")
            return False

    def update_packages(self) -> bool:
        """Update all packages"""
        if not self.termux_env.is_termux:
            return False

        try:
            self.logger.info("Updating package lists...")
            result = subprocess.run(
                ["pkg", "update", "-y"], capture_output=True, text=True, timeout=300
            )

            if result.returncode == 0:
                self.logger.info("Package update completed")
                return True
            else:
                self.logger.error(f"Package update failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Package update error: {e}")
            return False


class NetworkHelper:
    """Network configuration helpers for Android/Termux"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.android_props = AndroidProperty()

    def get_network_info(self) -> Dict[str, Union[str, List[str]]]:
        """Get network configuration information"""
        info = {}

        try:
            # Get network interfaces
            result = subprocess.run(
                ["ip", "addr", "show"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                info["interfaces"] = self._parse_ip_output(result.stdout)

            # Get routing information
            result = subprocess.run(
                ["ip", "route", "show"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                info["routes"] = result.stdout.strip().split("\n")

            # Get DNS configuration
            dns_servers = []
            for i in range(1, 5):
                dns = self.android_props.get(f"net.dns{i}")
                if dns and dns != "0.0.0.0":
                    dns_servers.append(dns)
            info["dns_servers"] = dns_servers

            # Get WiFi information (if available)
            if shutil.which("termux-wifi-connectioninfo"):
                result = subprocess.run(
                    ["termux-wifi-connectioninfo"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    try:
                        info["wifi"] = json.loads(result.stdout)
                    except json.JSONDecodeError:
                        pass

        except Exception as e:
            self.logger.error(f"Network info gathering error: {e}")

        return info

    def _parse_ip_output(self, output: str) -> List[Dict[str, str]]:
        """Parse ip addr show output"""
        interfaces = []
        current_interface = None

        for line in output.split("\n"):
            line = line.strip()
            if line and not line.startswith(" "):
                # New interface
                if ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        current_interface = {
                            "name": parts[1].strip(),
                            "status": "UP" if "UP" in line else "DOWN",
                            "addresses": [],
                        }
                        interfaces.append(current_interface)
            elif current_interface and "inet" in line:
                # IP address line
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "inet" and i + 1 < len(parts):
                        current_interface["addresses"].append(parts[i + 1])

        return interfaces

    def configure_dns(self, primary: str, secondary: str = "") -> bool:
        """Configure DNS servers"""
        try:
            if self.android_props.set("net.dns1", primary):
                self.logger.info(f"Set primary DNS to {primary}")

                if secondary and self.android_props.set("net.dns2", secondary):
                    self.logger.info(f"Set secondary DNS to {secondary}")

                return True
            else:
                self.logger.error("Failed to set DNS (requires root)")
                return False

        except Exception as e:
            self.logger.error(f"DNS configuration error: {e}")
            return False

    def test_connectivity(self, host: str = "8.8.8.8") -> Dict[str, Union[bool, str]]:
        """Test network connectivity"""
        result = {"ping": False, "dns": False, "http": False, "error": None}

        try:
            # Test ping
            ping_result = subprocess.run(
                ["ping", "-c", "1", "-W", "3", host], capture_output=True, timeout=10
            )
            result["ping"] = ping_result.returncode == 0

            # Test DNS resolution
            dns_result = subprocess.run(
                ["nslookup", "google.com"], capture_output=True, timeout=10
            )
            result["dns"] = dns_result.returncode == 0

            # Test HTTP connectivity (if curl available)
            if shutil.which("curl"):
                http_result = subprocess.run(
                    ["curl", "-s", "--max-time", "5", "http://httpbin.org/ip"],
                    capture_output=True,
                    timeout=10,
                )
                result["http"] = http_result.returncode == 0

        except Exception as e:
            result["error"] = str(e)

        return result


class PermissionManager:
    """Android permission and privilege management"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def check_root_access(self) -> bool:
        """Check if root access is available"""
        try:
            result = subprocess.run(
                ["su", "-c", "id"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0 and "uid=0" in result.stdout
        except Exception:
            return False

    def check_file_permissions(self, file_path: str) -> Dict[str, Union[bool, str]]:
        """Check file permissions and ownership"""
        info = {
            "exists": False,
            "readable": False,
            "writable": False,
            "executable": False,
            "owner": "unknown",
            "group": "unknown",
            "mode": "unknown",
        }

        try:
            path = Path(file_path)
            if path.exists():
                info["exists"] = True
                info["readable"] = os.access(file_path, os.R_OK)
                info["writable"] = os.access(file_path, os.W_OK)
                info["executable"] = os.access(file_path, os.X_OK)

                # Get detailed info
                stat_result = path.stat()
                info["mode"] = oct(stat_result.st_mode)[-3:]

                # Try to get owner/group info
                try:
                    import pwd
                    import grp

                    info["owner"] = pwd.getpwuid(stat_result.st_uid).pw_name
                    info["group"] = grp.getgrgid(stat_result.st_gid).gr_name
                except Exception:
                    info["owner"] = str(stat_result.st_uid)
                    info["group"] = str(stat_result.st_gid)

        except Exception as e:
            self.logger.error(f"Permission check error for {file_path}: {e}")

        return info

    def request_termux_permissions(self) -> bool:
        """Request necessary Termux permissions"""
        permissions_requested = True

        try:
            # Storage permission
            if shutil.which("termux-setup-storage"):
                subprocess.run(["termux-setup-storage"], timeout=30)

            # Other permissions can be requested here
            # termux-camera-info, termux-location, etc.

        except Exception as e:
            self.logger.error(f"Permission request error: {e}")
            permissions_requested = False

        return permissions_requested


def get_termux_compatibility_info() -> Dict:
    """Get comprehensive Termux compatibility information"""
    termux_env = TermuxEnvironment()
    storage_mgr = StorageManager()
    pkg_mgr = PackageManager()
    net_helper = NetworkHelper()
    perm_mgr = PermissionManager()

    info = {
        "environment": termux_env.get_termux_info(),
        "android": termux_env.get_android_info(),
        "storage_paths": storage_mgr.get_storage_paths(),
        "network": net_helper.get_network_info(),
        "permissions": {
            "root_access": perm_mgr.check_root_access(),
            "storage_access": os.path.exists(os.path.join(termux_env.home, "storage")),
        },
        "required_packages": {
            "python": pkg_mgr.is_package_installed("python"),
            "git": pkg_mgr.is_package_installed("git"),
            "curl": pkg_mgr.is_package_installed("curl"),
            "openssh": pkg_mgr.is_package_installed("openssh"),
        },
    }

    return info


def main():
    """CLI interface for Termux compatibility utilities"""
    import argparse

    parser = argparse.ArgumentParser(description="Termux Compatibility Utilities")
    parser.add_argument(
        "action",
        choices=["info", "test-network", "setup-storage", "check-packages"],
        help="Action to perform",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    if args.action == "info":
        info = get_termux_compatibility_info()
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print("=== Termux Compatibility Information ===")
            print(f"Termux Environment: {info['environment']['is_termux']}")
            print(
                f"Android Version: {info['android'].get('ro.build.version.release', 'unknown')}"
            )
            print(
                f"Architecture: {info['android'].get('ro.product.cpu.abi', 'unknown')}"
            )
            print(f"Root Access: {info['permissions']['root_access']}")
            print(f"Storage Access: {info['permissions']['storage_access']}")

    elif args.action == "test-network":
        net_helper = NetworkHelper()
        result = net_helper.test_connectivity()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("=== Network Connectivity Test ===")
            print(f"Ping: {'✓' if result['ping'] else '✗'}")
            print(f"DNS: {'✓' if result['dns'] else '✗'}")
            print(f"HTTP: {'✓' if result['http'] else '✗'}")
            if result["error"]:
                print(f"Error: {result['error']}")

    elif args.action == "setup-storage":
        storage_mgr = StorageManager()
        success = storage_mgr.setup_storage_access()
        print(f"Storage setup: {'Success' if success else 'Failed'}")

    elif args.action == "check-packages":
        pkg_mgr = PackageManager()
        packages = ["python", "git", "curl", "wget", "openssh", "nano"]

        print("=== Package Status ===")
        for package in packages:
            status = "✓" if pkg_mgr.is_package_installed(package) else "✗"
            print(f"{status} {package}")


if __name__ == "__main__":
    main()

"""
References:
- Termux Documentation: https://termux.com/docs/
- Android Properties: https://source.android.com/devices/architecture/configuration/
- Android Permissions: https://developer.android.com/guide/topics/permissions/overview
- Linux File Permissions: https://www.gnu.org/software/coreutils/manual/html_node/File-permissions.html
- Python pathlib: https://docs.python.org/3/library/pathlib.html
"""
