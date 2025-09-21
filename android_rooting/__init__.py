"""
Android Rooting Framework
Production-grade Android rooting tools with bot integration
"""

__version__ = "1.0.0"
__author__ = "VARIABOT Team"
__description__ = "Production-grade Android rooting framework with live bot integration"

from .core.root_detector import RootDetector, RootStatus
from .core.magisk_manager import MagiskManager, MagiskStatus
from .bots.error_handler_bot import ErrorHandlerBot, ErrorEvent, ErrorSeverity
from .utils.termux_compat import TermuxEnvironment, get_termux_compatibility_info
from .utils.logging_system import get_logger, setup_logging, RootingLogger

__all__ = [
    'RootDetector',
    'RootStatus', 
    'MagiskManager',
    'MagiskStatus',
    'ErrorHandlerBot',
    'ErrorEvent',
    'ErrorSeverity',
    'TermuxEnvironment',
    'get_termux_compatibility_info',
    'get_logger',
    'setup_logging',
    'RootingLogger'
]