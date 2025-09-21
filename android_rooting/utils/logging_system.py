#!/usr/bin/env python3
"""
Comprehensive Logging System for Android Rooting Framework
Production-grade logging with audit trail and compliance features

This module provides:
- Multi-level logging with rotation
- Audit trail for security events
- Compliance logging for forensics
- Real-time log monitoring
- Log analysis and reporting

Compatible with: Python 3.7+, Android 10+, Termux
"""

import os
import sys
import json
import logging
import logging.handlers
import threading
import time
import hashlib
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import queue


class LogLevel(Enum):
    """Custom log levels for rooting operations"""

    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    AUDIT = 60
    SECURITY = 70


class EventType(Enum):
    """Event types for audit logging"""

    ROOT_ATTEMPT = "root_attempt"
    ROOT_SUCCESS = "root_success"
    ROOT_FAILURE = "root_failure"
    PERMISSION_CHANGE = "permission_change"
    FILE_ACCESS = "file_access"
    NETWORK_ACCESS = "network_access"
    SYSTEM_MODIFICATION = "system_modification"
    ERROR_RECOVERY = "error_recovery"
    BOT_ACTION = "bot_action"
    SECURITY_VIOLATION = "security_violation"


@dataclass
class AuditEvent:
    """Audit event data structure"""

    timestamp: datetime
    event_type: EventType
    severity: LogLevel
    source: str
    user: str
    description: str
    details: Dict[str, Any]
    hash: str = ""

    def __post_init__(self):
        """Generate event hash for integrity"""
        if not self.hash:
            event_data = f"{self.timestamp.isoformat()}{self.event_type.value}{self.source}{self.description}"
            self.hash = hashlib.sha256(event_data.encode()).hexdigest()[:16]


class SecurityLogger:
    """Security-focused logger for audit events"""

    def __init__(self, log_dir: Optional[str] = None):
        """Initialize logging system with Termux-compatible paths"""
        if log_dir is None:
            # Use Termux-compatible default paths
            if "PREFIX" in os.environ and "HOME" in os.environ:
                # Running in Termux - use HOME directory
                log_dir = os.path.join(os.environ["HOME"], ".android_root_logs")
            else:
                # Fallback for non-Termux environments
                log_dir = os.path.join(tempfile.gettempdir(), "android_root_logs")
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.audit_file = self.log_dir / "audit.log"
        self.security_file = self.log_dir / "security.log"
        self.compliance_file = self.log_dir / "compliance.log"

        self._setup_audit_logger()
        self._setup_security_logger()
        self._setup_compliance_logger()

    def _setup_audit_logger(self):
        """Setup audit event logger"""
        self.audit_logger = logging.getLogger("audit")
        self.audit_logger.setLevel(logging.INFO)

        # Rotating file handler for audit logs
        handler = logging.handlers.RotatingFileHandler(
            self.audit_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding="utf-8",
        )

        # JSON formatter for structured audit logs
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        self.audit_logger.addHandler(handler)

    def _setup_security_logger(self):
        """Setup security event logger"""
        self.security_logger = logging.getLogger("security")
        self.security_logger.setLevel(logging.WARNING)

        handler = logging.handlers.RotatingFileHandler(
            self.security_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=20,
            encoding="utf-8",
        )

        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        self.security_logger.addHandler(handler)

    def _setup_compliance_logger(self):
        """Setup compliance logger"""
        self.compliance_logger = logging.getLogger("compliance")
        self.compliance_logger.setLevel(logging.INFO)

        handler = logging.handlers.TimedRotatingFileHandler(
            self.compliance_file,
            when="midnight",
            interval=1,
            backupCount=365,  # Keep 1 year of compliance logs
            encoding="utf-8",
        )

        formatter = ComplianceFormatter()
        handler.setFormatter(formatter)
        self.compliance_logger.addHandler(handler)

    def log_audit_event(self, event: AuditEvent):
        """Log audit event with integrity protection"""
        event_dict = asdict(event)
        event_dict["timestamp"] = event.timestamp.isoformat()
        event_dict["event_type"] = event.event_type.value
        event_dict["severity"] = event.severity.name

        self.audit_logger.info("AUDIT_EVENT", extra={"audit_data": event_dict})

        # Also log to security if it's a security-related event
        if event.severity.value >= LogLevel.SECURITY.value:
            self.security_logger.warning(
                "SECURITY_EVENT", extra={"audit_data": event_dict}
            )

        # Log to compliance for all events
        self.compliance_logger.info(
            "COMPLIANCE_EVENT", extra={"audit_data": event_dict}
        )


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra data if present
        if hasattr(record, "audit_data"):
            log_entry["audit_data"] = record.audit_data

        if hasattr(record, "context"):
            log_entry["context"] = record.context

        return json.dumps(log_entry, ensure_ascii=False)


class ComplianceFormatter(logging.Formatter):
    """Compliance-focused formatter with detailed context"""

    def format(self, record):
        # Create compliance entry with required fields
        compliance_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "event_id": getattr(record, "event_id", f"EVT_{int(record.created)}"),
            "severity": record.levelname,
            "source": record.name,
            "message": record.getMessage(),
            "process_id": os.getpid(),
            "thread_id": threading.get_ident(),
            "user_context": self._get_user_context(),
            "system_context": self._get_system_context(),
        }

        # Add audit data if present
        if hasattr(record, "audit_data"):
            compliance_entry.update(record.audit_data)

        return json.dumps(compliance_entry, ensure_ascii=False)

    def _get_user_context(self) -> Dict[str, str]:
        """Get user context information"""
        try:
            return {
                "uid": str(os.getuid()),
                "gid": str(os.getgid()),
                "user": os.environ.get("USER", "unknown"),
                "home": os.environ.get("HOME", "unknown"),
                "shell": os.environ.get("SHELL", "unknown"),
            }
        except Exception:
            return {"error": "could_not_determine_user_context"}

    def _get_system_context(self) -> Dict[str, str]:
        """Get system context information"""
        try:
            return {
                "hostname": subprocess.check_output(["hostname"], text=True).strip(),
                "kernel": subprocess.check_output(["uname", "-r"], text=True).strip(),
                "platform": sys.platform,
                "python_version": sys.version.split()[0],
                "working_directory": os.getcwd(),
            }
        except Exception:
            return {"error": "could_not_determine_system_context"}


class RootingLogger:
    """Main logging system for Android rooting operations"""

    def __init__(
        self,
        log_dir: str = "/data/local/tmp/android_root_logs",
        log_level: LogLevel = LogLevel.INFO,
        enable_console: bool = True,
        enable_audit: bool = True,
    ):

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_level = log_level
        self.enable_console = enable_console
        self.enable_audit = enable_audit

        # Initialize loggers
        self.main_logger = self._setup_main_logger()

        if enable_audit:
            self.security_logger = SecurityLogger(str(self.log_dir))

        # Performance monitoring
        self.performance_data = []
        self.start_time = time.time()

        # Log monitoring
        self.log_monitors = []
        self.monitor_queue = queue.Queue()
        self._start_log_monitoring()

        # Initial log entry
        self.info("Android Rooting Logger initialized")

    def _setup_main_logger(self) -> logging.Logger:
        """Setup main application logger"""
        logger = logging.getLogger("android_rooting")
        logger.setLevel(self.log_level.value)

        # Clear existing handlers
        logger.handlers.clear()

        # File handler with rotation
        file_handler = logging.handlers.TimedRotatingFileHandler(
            self.log_dir / "android_rooting.log",
            when="H",  # Hourly rotation
            interval=1,
            backupCount=168,  # Keep 1 week (24*7 hours)
            encoding="utf-8",
        )

        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler (if enabled)
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = ColoredFormatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "errors.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)

        return logger

    def _start_log_monitoring(self):
        """Start background log monitoring"""
        monitor_thread = threading.Thread(target=self._monitor_logs, daemon=True)
        monitor_thread.start()

    def _monitor_logs(self):
        """Background log monitoring for real-time analysis"""
        while True:
            try:
                # Check for log events
                if not self.monitor_queue.empty():
                    event = self.monitor_queue.get_nowait()
                    for monitor in self.log_monitors:
                        try:
                            monitor(event)
                        except Exception as e:
                            self.error(f"Log monitor error: {e}")

                # Check log file sizes
                self._check_log_file_sizes()

                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                print(f"Log monitoring error: {e}", file=sys.stderr)
                time.sleep(10)

    def _check_log_file_sizes(self):
        """Monitor log file sizes and alert if too large"""
        max_size = 50 * 1024 * 1024  # 50MB warning threshold

        for log_file in self.log_dir.glob("*.log"):
            try:
                if log_file.stat().st_size > max_size:
                    self.warning(
                        f"Log file {log_file.name} is large: {log_file.stat().st_size / 1024 / 1024:.1f}MB"
                    )
            except Exception:
                pass

    def add_log_monitor(self, monitor_func: Callable[[Dict], None]):
        """Add log monitoring function"""
        self.log_monitors.append(monitor_func)

    def trace(self, message: str, **kwargs):
        """Log trace message"""
        self.main_logger.log(LogLevel.TRACE.value, message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.main_logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self.main_logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.main_logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self.main_logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.main_logger.critical(message, extra=kwargs)

    def audit(
        self,
        event_type: EventType,
        description: str,
        details: Optional[Dict] = None,
        severity: LogLevel = LogLevel.AUDIT,
    ):
        """Log audit event"""
        if not self.enable_audit:
            return

        user = os.environ.get("USER", "unknown")
        source = f"{os.path.basename(sys.argv[0])}:{threading.current_thread().name}"

        audit_event = AuditEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            severity=severity,
            source=source,
            user=user,
            description=description,
            details=details or {},
        )

        self.security_logger.log_audit_event(audit_event)

        # Also log to main logger
        self.main_logger.log(
            severity.value,
            f"AUDIT: {event_type.value} - {description}",
            extra={"audit_event": asdict(audit_event)},
        )

        # Queue for monitors
        self.monitor_queue.put(
            {"type": "audit", "event": audit_event, "timestamp": time.time()}
        )

    def log_performance(
        self, operation: str, duration: float, details: Optional[Dict] = None
    ):
        """Log performance metrics"""
        perf_data = {
            "timestamp": time.time(),
            "operation": operation,
            "duration": duration,
            "details": details or {},
        }

        self.performance_data.append(perf_data)

        # Keep only recent performance data
        cutoff = time.time() - 3600  # Last hour
        self.performance_data = [
            p for p in self.performance_data if p["timestamp"] > cutoff
        ]

        self.info(
            f"PERFORMANCE: {operation} completed in {duration:.3f}s",
            extra={"performance": perf_data},
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.performance_data:
            return {}

        operations = {}
        for perf in self.performance_data:
            op = perf["operation"]
            if op not in operations:
                operations[op] = []
            operations[op].append(perf["duration"])

        stats = {}
        for op, durations in operations.items():
            stats[op] = {
                "count": len(durations),
                "avg": sum(durations) / len(durations),
                "min": min(durations),
                "max": max(durations),
            }

        return {
            "total_operations": len(self.performance_data),
            "uptime": time.time() - self.start_time,
            "operations": stats,
        }

    def get_log_summary(self) -> Dict[str, Any]:
        """Get logging system summary"""
        summary = {
            "log_directory": str(self.log_dir),
            "log_level": self.log_level.name,
            "audit_enabled": self.enable_audit,
            "console_enabled": self.enable_console,
            "monitors_active": len(self.log_monitors),
            "uptime": time.time() - self.start_time,
        }

        # Log file information
        log_files = {}
        for log_file in self.log_dir.glob("*.log"):
            try:
                stat = log_file.stat()
                log_files[log_file.name] = {
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            except Exception:
                pass

        summary["log_files"] = log_files

        return summary

    def compress_old_logs(self, days_old: int = 7):
        """Compress old log files"""
        cutoff_time = time.time() - (days_old * 24 * 3600)

        for log_file in self.log_dir.glob("*.log.*"):
            try:
                if (
                    log_file.stat().st_mtime < cutoff_time
                    and not log_file.name.endswith(".gz")
                ):
                    # Compress the file
                    with open(log_file, "rb") as f_in:
                        with gzip.open(f"{log_file}.gz", "wb") as f_out:
                            f_out.writelines(f_in)

                    # Remove original
                    log_file.unlink()
                    self.info(f"Compressed old log file: {log_file.name}")

            except Exception as e:
                self.error(f"Failed to compress {log_file}: {e}")

    def cleanup_old_logs(self, days_old: int = 30):
        """Remove very old log files"""
        cutoff_time = time.time() - (days_old * 24 * 3600)

        for log_file in self.log_dir.glob("*.log.*.gz"):
            try:
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.info(f"Removed old log file: {log_file.name}")

            except Exception as e:
                self.error(f"Failed to remove {log_file}: {e}")


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset_color = self.COLORS["RESET"]

        # Create colored message
        colored_record = logging.makeLogRecord(record.__dict__)
        colored_record.levelname = f"{log_color}{record.levelname}{reset_color}"

        return super().format(colored_record)


# Global logger instance
_global_logger: Optional[RootingLogger] = None


def get_logger(
    log_dir: Optional[str] = None,
    log_level: LogLevel = LogLevel.INFO,
    enable_console: bool = True,
    enable_audit: bool = True,
) -> RootingLogger:
    """Get or create global logger instance"""
    global _global_logger

    if _global_logger is None:
        _global_logger = RootingLogger(
            log_dir=log_dir,
            log_level=log_level,
            enable_console=enable_console,
            enable_audit=enable_audit,
        )

    return _global_logger


def setup_logging(
    log_dir: Optional[str] = None,
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_audit: bool = True,
) -> RootingLogger:
    """Setup logging system with configuration"""
    level_mapping = {
        "TRACE": LogLevel.TRACE,
        "DEBUG": LogLevel.DEBUG,
        "INFO": LogLevel.INFO,
        "WARNING": LogLevel.WARNING,
        "ERROR": LogLevel.ERROR,
        "CRITICAL": LogLevel.CRITICAL,
    }

    log_level_enum = level_mapping.get(log_level.upper(), LogLevel.INFO)

    return get_logger(
        log_dir=log_dir,
        log_level=log_level_enum,
        enable_console=enable_console,
        enable_audit=enable_audit,
    )


def main():
    """CLI interface for logging system"""
    import argparse

    parser = argparse.ArgumentParser(description="Android Rooting Logging System")
    parser.add_argument(
        "action",
        choices=["test", "analyze", "cleanup", "compress"],
        help="Action to perform",
    )
    # Default log directory - Termux compatible
    default_log_dir = os.path.join(
        os.environ.get("HOME", tempfile.gettempdir()), ".android_root_logs"
    )

    parser.add_argument("--log-dir", default=default_log_dir, help="Log directory path")
    parser.add_argument(
        "--days", type=int, default=7, help="Days for cleanup/compress operations"
    )
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    logger = setup_logging(log_dir=args.log_dir, enable_console=True)

    if args.action == "test":
        # Test logging functionality
        logger.info("Testing logging system...")
        logger.debug("Debug message test")
        logger.warning("Warning message test")
        logger.error("Error message test")

        # Test audit logging
        logger.audit(
            EventType.ROOT_ATTEMPT,
            "Test root attempt",
            {"method": "test", "target": "localhost"},
        )

        # Test performance logging
        import time

        start = time.time()
        time.sleep(0.1)
        logger.log_performance("test_operation", time.time() - start)

        print("Logging test completed. Check log files in:", args.log_dir)

    elif args.action == "analyze":
        # Analyze logs
        summary = logger.get_log_summary()
        perf_stats = logger.get_performance_stats()

        if args.json:
            result = {"summary": summary, "performance": perf_stats}
            print(json.dumps(result, indent=2))
        else:
            print("=== Log Analysis ===")
            print(f"Log Directory: {summary['log_directory']}")
            print(f"Log Level: {summary['log_level']}")
            print(f"Uptime: {summary['uptime']:.1f}s")
            print(f"Log Files: {len(summary['log_files'])}")
            print(f"Performance Operations: {perf_stats.get('total_operations', 0)}")

    elif args.action == "cleanup":
        logger.cleanup_old_logs(args.days)
        print(f"Cleaned up logs older than {args.days} days")

    elif args.action == "compress":
        logger.compress_old_logs(args.days)
        print(f"Compressed logs older than {args.days} days")


if __name__ == "__main__":
    main()

"""
References:
- Python Logging Documentation: https://docs.python.org/3/library/logging.html
- Security Logging Best Practices: https://owasp.org/www-project-application-security-verification-standard/
- Audit Trail Standards: https://www.nist.gov/publications/guide-computer-security-log-management
- JSON Logging: https://github.com/madzak/python-json-logger
- Log Rotation: https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler
"""
