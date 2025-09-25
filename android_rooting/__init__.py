"""
Android Rooting Framework
Production-grade Android rooting tools with bot integration and Kali Linux support
"""

__version__ = "1.2.0"
__author__ = "VARIABOT Team"
__description__ = "Production-grade Android rooting framework with live bot integration, Kali Linux tools, Android system exploitation, and AI-powered analysis"

from .core.root_detector import RootDetector, RootStatus
from .core.magisk_manager import MagiskManager, MagiskStatus
from .core.android_pentest import AndroidPentestFramework
from .core.kali_integration import KaliIntegration
from .core.android_system_exploit import AndroidSystemExploit, SystemAppPermission, ExploitPayload
from .bots.error_handler_bot import ErrorHandlerBot, ErrorEvent, ErrorSeverity
from .utils.termux_compat import TermuxEnvironment, get_termux_compatibility_info
from .utils.logging_system import get_logger, setup_logging, RootingLogger

__all__ = [
    "RootDetector",
    "RootStatus", 
    "MagiskManager",
    "MagiskStatus",
    "AndroidPentestFramework",
    "KaliIntegration",
    "AndroidSystemExploit",
    "SystemAppPermission",
    "ExploitPayload",
    "ErrorHandlerBot",
    "ErrorEvent",
    "ErrorSeverity",
    "TermuxEnvironment",
    "get_termux_compatibility_info",
    "get_logger",
    "setup_logging",
    "RootingLogger",
]
