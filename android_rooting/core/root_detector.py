#!/usr/bin/env python3
"""
Android Root Detection and Status Checker
Production-grade root detection for Android 13 ARM64 tablets

This module provides comprehensive root detection capabilities including:
- Binary detection (su, busybox)
- Package manager checks (Magisk, SuperSU)
- System partition analysis
- Selinux policy verification
- Build properties validation

Compatible with: Android 10+, Termux, Kali Linux environments
"""

import os
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from enum import Enum


class RootStatus(Enum):
    """Root status enumeration"""

    UNROOTED = "unrooted"
    PARTIAL = "partial"
    FULL = "full"
    UNKNOWN = "unknown"


class RootDetector:
    """
    Comprehensive Android root detection system

    Implements multiple detection methods following Android security standards
    and Kali Linux penetration testing best practices.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.detection_methods = []
        self.root_indicators = {
            "binaries": [],
            "packages": [],
            "properties": {},
            "selinux": {},
            "partitions": [],
        }

    def detect_root_status(self) -> Tuple[RootStatus, Dict]:
        """
        Primary root detection method

        Returns:
            Tuple of (RootStatus, detection_details)
        """
        self.logger.info("Starting comprehensive root detection...")

        # Execute all detection methods
        binary_check = self._check_root_binaries()
        package_check = self._check_root_packages()
        property_check = self._check_build_properties()
        selinux_check = self._check_selinux_status()
        partition_check = self._check_system_partitions()

        # Compile results
        detection_results = {
            "binaries": binary_check,
            "packages": package_check,
            "properties": property_check,
            "selinux": selinux_check,
            "partitions": partition_check,
            "timestamp": subprocess.check_output(["date", "-Iseconds"])
            .decode()
            .strip(),
        }

        # Determine overall status
        status = self._analyze_root_status(detection_results)

        self.logger.info(f"Root detection complete. Status: {status.value}")
        return status, detection_results

    def _check_root_binaries(self) -> Dict[str, bool]:
        """Check for common root binaries"""
        self.logger.debug("Checking root binaries...")

        root_binaries = [
            "/system/bin/su",
            "/system/xbin/su",
            "/sbin/su",
            "/su/bin/su",
            "/system/app/Superuser.apk",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su",
            "/su/xbin/su",
        ]

        busybox_paths = [
            "/system/bin/busybox",
            "/system/xbin/busybox",
            "/sbin/busybox",
            "/data/local/xbin/busybox",
        ]

        results = {}

        # Check su binaries
        for binary in root_binaries:
            results[binary] = os.path.exists(binary) and os.access(binary, os.X_OK)

        # Check busybox
        for busybox in busybox_paths:
            results[busybox] = os.path.exists(busybox) and os.access(busybox, os.X_OK)

        return {k: v for k, v in results.items() if v}

    def _check_root_packages(self) -> Dict[str, Dict]:
        """Check for root management packages"""
        self.logger.debug("Checking root packages...")

        root_packages = [
            "com.topjohnwu.magisk",
            "com.noshufou.android.su",
            "com.noshufou.android.su.elite",
            "eu.chainfire.supersu",
            "com.koushikdutta.superuser",
            "com.thirdparty.superuser",
            "com.yellowes.su",
        ]

        results = {}

        for package in root_packages:
            try:
                # Check if package is installed
                cmd = f"pm path {package}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    results[package] = {
                        "installed": True,
                        "path": result.stdout.strip(),
                        "version": self._get_package_version(package),
                    }
            except Exception as e:
                self.logger.debug(f"Error checking package {package}: {e}")

        return results

    def _check_build_properties(self) -> Dict[str, str]:
        """Check Android build properties for root indicators"""
        self.logger.debug("Checking build properties...")

        properties_to_check = [
            "ro.debuggable",
            "ro.secure",
            "ro.build.type",
            "ro.build.tags",
            "ro.kernel.qemu",
            "service.adb.root",
        ]

        results = {}

        for prop in properties_to_check:
            try:
                cmd = f"getprop {prop}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    results[prop] = result.stdout.strip()
            except Exception as e:
                self.logger.debug(f"Error checking property {prop}: {e}")

        return results

    def _check_selinux_status(self) -> Dict[str, str]:
        """Check SELinux enforcement status"""
        self.logger.debug("Checking SELinux status...")

        results = {}

        try:
            # Check getenforce
            result = subprocess.run(
                "getenforce", shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                results["enforcement"] = result.stdout.strip()

            # Check selinux policy
            if os.path.exists("/sys/fs/selinux/policy"):
                results["policy_exists"] = True
            else:
                results["policy_exists"] = False

        except Exception as e:
            self.logger.debug(f"Error checking SELinux: {e}")

        return results

    def _check_system_partitions(self) -> List[Dict]:
        """Check system partition mount status"""
        self.logger.debug("Checking system partitions...")

        results = []

        try:
            with open("/proc/mounts", "r") as f:
                mounts = f.readlines()

            system_partitions = ["/system", "/vendor", "/boot"]

            for mount_line in mounts:
                parts = mount_line.split()
                if len(parts) >= 4:
                    mount_point = parts[1]
                    if mount_point in system_partitions:
                        results.append(
                            {
                                "device": parts[0],
                                "mount_point": mount_point,
                                "filesystem": parts[2],
                                "options": parts[3],
                                "writable": "rw" in parts[3],
                            }
                        )

        except Exception as e:
            self.logger.debug(f"Error checking partitions: {e}")

        return results

    def _get_package_version(self, package: str) -> Optional[str]:
        """Get version of installed package"""
        try:
            cmd = f"dumpsys package {package} | grep versionName"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                version_line = result.stdout.strip()
                return version_line.split("=")[-1] if "=" in version_line else None
        except Exception:
            pass
        return None

    def _analyze_root_status(self, results: Dict) -> RootStatus:
        """Analyze detection results to determine root status"""

        # Check for full root indicators
        has_su = bool(results["binaries"])
        has_root_packages = bool(results["packages"])
        selinux_permissive = results["selinux"].get("enforcement") == "Permissive"
        system_writable = any(
            p.get("writable", False)
            for p in results["partitions"]
            if p["mount_point"] == "/system"
        )

        # Full root: su binary + root package + (permissive selinux OR writable system)
        if has_su and has_root_packages and (selinux_permissive or system_writable):
            return RootStatus.FULL

        # Partial root: some indicators but not complete
        if has_su or has_root_packages or selinux_permissive or system_writable:
            return RootStatus.PARTIAL

        # Check for development builds (may indicate unlocked bootloader)
        build_type = results["properties"].get("ro.build.type", "")
        debuggable = results["properties"].get("ro.debuggable", "0")

        if build_type in ["userdebug", "eng"] or debuggable == "1":
            return RootStatus.PARTIAL

        return RootStatus.UNROOTED


def main():
    """CLI interface for root detection"""
    import argparse

    parser = argparse.ArgumentParser(description="Android Root Detection Tool")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Run detection
    detector = RootDetector()
    status, results = detector.detect_root_status()

    if args.json:
        output = {"status": status.value, "details": results}
        print(json.dumps(output, indent=2))
    else:
        print(f"Root Status: {status.value}")
        print(f"Detection completed at: {results['timestamp']}")


if __name__ == "__main__":
    main()

"""
References:
- Android Security Model: https://source.android.com/security/overview/
- Magisk Documentation: https://github.com/topjohnwu/Magisk
- SELinux for Android: https://source.android.com/security/selinux/
- Android Penetration Testing: https://github.com/tanprathan/MobileApp-Pentest-Cheatsheet
- Kali Linux Mobile Testing: https://www.kali.org/docs/nethunter/
"""
