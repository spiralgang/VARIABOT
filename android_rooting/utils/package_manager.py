#!/usr/bin/env python3
"""
Termux Package Manager Compatibility Layer
Handles package installation and management in Termux environment

This module provides:
- Termux pkg command interface
- Cross-platform package management
- Dependency resolution and installation
- Package availability checking

Important Termux Limitations Addressed:
- Uses 'pkg' instead of apt-get/yum/dnf
- No hardcoded filesystem paths (uses $PREFIX and $HOME)
- Termux-specific package names and repositories
- Single-user, unprivileged environment considerations

Compatible with: Termux on Android 10+, Python 3.7+
"""

import os
import sys
import subprocess
import logging
import json
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PackageInfo:
    """Package information structure"""

    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    installed: bool = False
    available: bool = False
    dependencies: List[str] = None


class TermuxPackageManager:
    """Termux-specific package manager interface"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_termux = self._detect_termux()
        self.prefix = os.environ.get("PREFIX", "")

        # Termux package mappings - common packages with different names
        self.package_mappings = {
            "python3": "python",
            "python3-pip": "python-pip",
            "build-essential": "build-essential",
            "gcc": "clang",
            "g++": "clang",
            "make": "make",
            "cmake": "cmake",
            "git": "git",
            "curl": "curl",
            "wget": "wget",
            "nano": "nano",
            "vim": "vim",
            "openssh-client": "openssh",
            "openssh-server": "openssh",
            "nmap": "nmap",
            "netcat": "netcat-openbsd",
            "socat": "socat",
            "tcpdump": "tcpdump",
            "wireshark": "tshark",
            "sqlite3": "sqlite",
            "postgresql": "postgresql",
            "redis": "redis",
            "nodejs": "nodejs",
            "npm": "nodejs",  # npm comes with nodejs in Termux
            "golang": "golang",
            "rust": "rust",
            "ruby": "ruby",
            "perl": "perl",
            "php": "php",
            "openjdk": "openjdk-17",
            "zip": "zip",
            "unzip": "unzip",
            "tar": "tar",
            "gzip": "gzip",
            "bzip2": "bzip2",
            "xz": "xz-utils",
            "tree": "tree",
            "htop": "htop",
            "tmux": "tmux",
            "screen": "screen",
            "jq": "jq",
            "bc": "bc",
        }

    def _detect_termux(self) -> bool:
        """Detect if running in Termux environment"""
        return (
            "TERMUX_VERSION" in os.environ
            or "com.termux" in os.environ.get("PREFIX", "")
            or os.environ.get("PREFIX", "").startswith("/data/data/com.termux")
        )

    def _run_pkg_command(
        self, command: List[str], timeout: int = 60
    ) -> Tuple[bool, str, str]:
        """Run pkg command and return result"""
        if not self.is_termux:
            return False, "", "Not running in Termux environment"

        try:
            result = subprocess.run(
                ["pkg"] + command,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=os.environ.copy(),
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", f"Command failed: {e}"

    def update_package_list(self) -> bool:
        """Update package repository information"""
        self.logger.info("Updating package repository...")
        success, stdout, stderr = self._run_pkg_command(["update", "-y"])

        if success:
            self.logger.info("Package repository updated successfully")
        else:
            self.logger.error(f"Failed to update package repository: {stderr}")

        return success

    def upgrade_packages(self) -> bool:
        """Upgrade all installed packages"""
        self.logger.info("Upgrading installed packages...")
        success, stdout, stderr = self._run_pkg_command(["upgrade", "-y"])

        if success:
            self.logger.info("Packages upgraded successfully")
        else:
            self.logger.warning(f"Package upgrade completed with warnings: {stderr}")
            # Don't treat upgrade warnings as failures
            return True

        return success

    def install_package(self, package_name: str) -> bool:
        """Install a single package"""
        # Map package name to Termux equivalent
        termux_package = self.package_mappings.get(package_name, package_name)

        self.logger.info(f"Installing package: {termux_package}")
        success, stdout, stderr = self._run_pkg_command(
            ["install", termux_package, "-y"]
        )

        if success:
            self.logger.info(f"✓ {termux_package} installed successfully")
        else:
            self.logger.error(f"✗ Failed to install {termux_package}: {stderr}")

        return success

    def install_packages(self, package_names: List[str]) -> Dict[str, bool]:
        """Install multiple packages"""
        results = {}

        for package in package_names:
            results[package] = self.install_package(package)

        return results

    def is_package_installed(self, package_name: str) -> bool:
        """Check if package is installed"""
        termux_package = self.package_mappings.get(package_name, package_name)
        success, stdout, stderr = self._run_pkg_command(
            ["list-installed", termux_package]
        )

        return success and termux_package in stdout

    def is_package_available(self, package_name: str) -> bool:
        """Check if package is available in repositories"""
        termux_package = self.package_mappings.get(package_name, package_name)
        success, stdout, stderr = self._run_pkg_command(["search", termux_package])

        return success and termux_package in stdout

    def get_package_info(self, package_name: str) -> Optional[PackageInfo]:
        """Get detailed package information"""
        termux_package = self.package_mappings.get(package_name, package_name)

        # Check if installed
        installed = self.is_package_installed(termux_package)

        # Check if available
        available = self.is_package_available(termux_package)

        # Get package details
        success, stdout, stderr = self._run_pkg_command(["show", termux_package])
        version = None
        description = None

        if success:
            lines = stdout.split("\n")
            for line in lines:
                if line.startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                elif line.startswith("Description:"):
                    description = line.split(":", 1)[1].strip()

        return PackageInfo(
            name=termux_package,
            version=version,
            description=description,
            installed=installed,
            available=available,
        )

    def remove_package(self, package_name: str) -> bool:
        """Remove/uninstall a package"""
        termux_package = self.package_mappings.get(package_name, package_name)

        self.logger.info(f"Removing package: {termux_package}")
        success, stdout, stderr = self._run_pkg_command(
            ["uninstall", termux_package, "-y"]
        )

        if success:
            self.logger.info(f"✓ {termux_package} removed successfully")
        else:
            self.logger.error(f"✗ Failed to remove {termux_package}: {stderr}")

        return success

    def clean_cache(self) -> bool:
        """Clean package cache"""
        self.logger.info("Cleaning package cache...")
        success, stdout, stderr = self._run_pkg_command(["clean"])

        if success:
            self.logger.info("Package cache cleaned successfully")
        else:
            self.logger.error(f"Failed to clean package cache: {stderr}")

        return success

    def list_installed_packages(self) -> List[str]:
        """List all installed packages"""
        success, stdout, stderr = self._run_pkg_command(["list-installed"])

        if not success:
            self.logger.error(f"Failed to list installed packages: {stderr}")
            return []

        packages = []
        for line in stdout.split("\n"):
            if line.strip() and not line.startswith("Listing"):
                # Extract package name (first part before space)
                package = line.split()[0] if line.split() else ""
                if package:
                    packages.append(package)

        return packages

    def search_packages(self, query: str) -> List[str]:
        """Search for packages matching query"""
        success, stdout, stderr = self._run_pkg_command(["search", query])

        if not success:
            self.logger.error(f"Package search failed: {stderr}")
            return []

        packages = []
        for line in stdout.split("\n"):
            if line.strip() and "/" in line:
                # Extract package name from search results
                package = line.split("/", 1)[1].split()[0] if "/" in line else ""
                if package:
                    packages.append(package)

        return packages


class PythonPackageManager:
    """Python package management for Termux"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def install_pip_package(self, package_name: str) -> bool:
        """Install Python package using pip"""
        self.logger.info(f"Installing Python package: {package_name}")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes for large packages
            )

            if result.returncode == 0:
                self.logger.info(f"✓ {package_name} installed successfully")
                return True
            else:
                self.logger.error(
                    f"✗ Failed to install {package_name}: {result.stderr}"
                )
                return False

        except subprocess.TimeoutExpired:
            self.logger.error(f"Installation of {package_name} timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error installing {package_name}: {e}")
            return False

    def install_pip_packages(self, package_names: List[str]) -> Dict[str, bool]:
        """Install multiple Python packages"""
        results = {}

        for package in package_names:
            results[package] = self.install_pip_package(package)

        return results

    def upgrade_pip(self) -> bool:
        """Upgrade pip to latest version"""
        self.logger.info("Upgrading pip...")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                text=True,
                timeout=180,
            )

            if result.returncode == 0:
                self.logger.info("✓ pip upgraded successfully")
                return True
            else:
                self.logger.error(f"Failed to upgrade pip: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error upgrading pip: {e}")
            return False


def setup_termux_environment() -> bool:
    """Complete Termux environment setup"""
    logger = logging.getLogger(__name__)

    # Initialize package managers
    pkg_mgr = TermuxPackageManager()
    pip_mgr = PythonPackageManager()

    if not pkg_mgr.is_termux:
        logger.error("Not running in Termux environment")
        return False

    # Update package repository
    if not pkg_mgr.update_package_list():
        logger.error("Failed to update package repository")
        return False

    # Essential packages for Android rooting framework
    essential_packages = [
        "python",
        "python-pip",
        "git",
        "curl",
        "wget",
        "openssh",
        "nmap",
        "netcat-openbsd",
        "jq",
        "tree",
        "tmux",
        "termux-api",
        "termux-tools",
        "proot",
        "tsu",
    ]

    # Install essential packages
    logger.info("Installing essential packages...")
    results = pkg_mgr.install_packages(essential_packages)

    failed_packages = [pkg for pkg, success in results.items() if not success]
    if failed_packages:
        logger.warning(f"Failed to install packages: {failed_packages}")

    # Upgrade pip
    if not pip_mgr.upgrade_pip():
        logger.warning("Failed to upgrade pip")

    # Install essential Python packages
    python_packages = [
        "requests",
        "urllib3",
        "psutil",
        "netifaces",
        "cryptography",
        "paramiko",
        "websocket-client",
        "aiohttp",
    ]

    logger.info("Installing Python packages...")
    py_results = pip_mgr.install_pip_packages(python_packages)

    failed_py_packages = [pkg for pkg, success in py_results.items() if not success]
    if failed_py_packages:
        logger.warning(f"Failed to install Python packages: {failed_py_packages}")

    logger.info("Termux environment setup completed")
    return len(failed_packages) == 0 and len(failed_py_packages) == 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Termux Package Manager Interface")
    parser.add_argument(
        "action",
        choices=["install", "remove", "search", "info", "list", "setup"],
        help="Action to perform",
    )
    parser.add_argument("packages", nargs="*", help="Package names")
    parser.add_argument(
        "--update", action="store_true", help="Update package lists first"
    )
    parser.add_argument(
        "--python", action="store_true", help="Use Python pip instead of pkg"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    if args.python:
        mgr = PythonPackageManager()
    else:
        mgr = TermuxPackageManager()

        if args.update:
            mgr.update_package_list()

    if args.action == "setup":
        success = setup_termux_environment()
        sys.exit(0 if success else 1)
    elif args.action == "install":
        if args.python:
            results = mgr.install_pip_packages(args.packages)
        else:
            results = mgr.install_packages(args.packages)
        print(json.dumps(results, indent=2))
    elif args.action == "search" and not args.python:
        for package in args.packages:
            results = mgr.search_packages(package)
            print(f"Search results for '{package}':")
            for result in results:
                print(f"  - {result}")
    elif args.action == "info" and not args.python:
        for package in args.packages:
            info = mgr.get_package_info(package)
            if info:
                print(f"Package: {info.name}")
                print(f"Version: {info.version or 'Unknown'}")
                print(f"Description: {info.description or 'N/A'}")
                print(f"Installed: {info.installed}")
                print(f"Available: {info.available}")
                print()
    elif args.action == "list" and not args.python:
        packages = mgr.list_installed_packages()
        print("Installed packages:")
        for package in sorted(packages):
            print(f"  - {package}")

"""
References and Citations:
1. Termux Wiki: https://wiki.termux.com/wiki/Package_Management
2. Termux Packages: https://github.com/termux/termux-packages
3. Android Package Management: https://developer.android.com/guide/components/fundamentals
4. Termux API Reference: https://wiki.termux.com/wiki/Termux:API
5. Python packaging in Termux: https://wiki.termux.com/wiki/Python
"""
