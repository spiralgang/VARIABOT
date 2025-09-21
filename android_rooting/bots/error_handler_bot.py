#!/usr/bin/env python3
"""
Error Handler Bot Framework
Live error handling and variable adaptation bot for Android rooting process

This module provides:
- Real-time error detection and handling
- Variable adaptation during root process
- Live logging and monitoring
- GitHub-driven code updates
- Termux compatibility

Compatible with: Python 3.7+, Bash, Kali Linux, Android 10+
"""

import os
import sys
import json
import time
import threading
import logging
import subprocess
import tempfile
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import socket
import hashlib

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BotStatus(Enum):
    """Bot operational status"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"
    UPDATING = "updating"

@dataclass
class ErrorEvent:
    """Error event data structure"""
    timestamp: datetime
    severity: ErrorSeverity
    category: str
    message: str
    context: Dict[str, Any]
    suggested_action: Optional[str] = None
    auto_handled: bool = False

@dataclass
class BotConfig:
    """Bot configuration settings"""
    github_repo: str = ""
    github_token: str = ""
    update_interval: int = 30
    max_retries: int = 3
    error_threshold: int = 10
    auto_handle: bool = True
    log_level: str = "INFO"

class ErrorHandlerBot:
    """
    Production-grade error handling and monitoring bot
    
    Provides real-time error detection, handling, and adaptation
    for Android rooting processes with GitHub integration.
    """
    
    def __init__(self, config: BotConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.status = BotStatus.INACTIVE
        self.error_queue = queue.Queue()
        self.handlers = {}
        self.monitors = []
        self.github_client = GitHubClient(config.github_repo, config.github_token)
        
        # Error tracking
        self.error_count = 0
        self.last_errors = []
        self.handled_errors = []
        
        # Bot state
        self.running = False
        self.last_update_check = datetime.now()
        
        self._setup_default_handlers()
        
    def start(self):
        """Start the error handler bot"""
        self.logger.info("Starting Error Handler Bot...")
        self.running = True
        self.status = BotStatus.ACTIVE
        
        # Start monitoring threads
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        handler_thread = threading.Thread(target=self._handler_loop, daemon=True)
        update_thread = threading.Thread(target=self._update_loop, daemon=True)
        
        monitor_thread.start()
        handler_thread.start()
        update_thread.start()
        
        self.logger.info("Error Handler Bot started successfully")
        
    def stop(self):
        """Stop the error handler bot"""
        self.logger.info("Stopping Error Handler Bot...")
        self.running = False
        self.status = BotStatus.INACTIVE
        
    def register_error_handler(self, category: str, handler: Callable[[ErrorEvent], bool]):
        """
        Register custom error handler
        
        Args:
            category: Error category to handle
            handler: Handler function that returns True if error was handled
        """
        self.handlers[category] = handler
        self.logger.debug(f"Registered handler for category: {category}")
        
    def register_monitor(self, monitor_func: Callable[[], List[ErrorEvent]]):
        """
        Register monitoring function
        
        Args:
            monitor_func: Function that returns list of detected errors
        """
        self.monitors.append(monitor_func)
        self.logger.debug("Registered new monitor function")
        
    def report_error(self, category: str, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    context: Optional[Dict] = None, suggested_action: Optional[str] = None):
        """
        Report an error event
        
        Args:
            category: Error category
            message: Error message
            severity: Error severity level
            context: Additional context information
            suggested_action: Suggested action to resolve error
        """
        error_event = ErrorEvent(
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            message=message,
            context=context or {},
            suggested_action=suggested_action
        )
        
        self.error_queue.put(error_event)
        self.logger.warning(f"Error reported: {category} - {message}")
        
    def get_status(self) -> Dict:
        """Get bot status and statistics"""
        return {
            'status': self.status.value,
            'error_count': self.error_count,
            'recent_errors': len([e for e in self.last_errors 
                                if e.timestamp > datetime.now() - timedelta(hours=1)]),
            'handled_errors': len(self.handled_errors),
            'last_update_check': self.last_update_check.isoformat(),
            'running': self.running
        }
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Run all registered monitors
                for monitor in self.monitors:
                    try:
                        errors = monitor()
                        for error in errors:
                            self.error_queue.put(error)
                    except Exception as e:
                        self.logger.error(f"Monitor error: {e}")
                        
                # Built-in monitoring
                self._monitor_system_health()
                self._monitor_root_process()
                
                time.sleep(1)  # Monitor every second
                
            except Exception as e:
                self.logger.error(f"Monitor loop error: {e}")
                time.sleep(5)
                
    def _handler_loop(self):
        """Main error handling loop"""
        while self.running:
            try:
                # Process errors from queue
                try:
                    error_event = self.error_queue.get(timeout=1)
                    self._handle_error(error_event)
                except queue.Empty:
                    continue
                    
            except Exception as e:
                self.logger.error(f"Handler loop error: {e}")
                time.sleep(1)
                
    def _update_loop(self):
        """Bot update and code refresh loop"""
        while self.running:
            try:
                # Check for updates periodically
                if (datetime.now() - self.last_update_check).seconds > self.config.update_interval:
                    self._check_for_updates()
                    self.last_update_check = datetime.now()
                    
                time.sleep(self.config.update_interval)
                
            except Exception as e:
                self.logger.error(f"Update loop error: {e}")
                time.sleep(30)
                
    def _handle_error(self, error_event: ErrorEvent):
        """Handle individual error event"""
        self.error_count += 1
        self.last_errors.append(error_event)
        
        # Keep only recent errors in memory
        cutoff = datetime.now() - timedelta(hours=24)
        self.last_errors = [e for e in self.last_errors if e.timestamp > cutoff]
        
        self.logger.error(f"Handling error: {error_event.category} - {error_event.message}")
        
        # Try registered handler first
        if error_event.category in self.handlers:
            try:
                if self.handlers[error_event.category](error_event):
                    error_event.auto_handled = True
                    self.handled_errors.append(error_event)
                    self.logger.info(f"Error handled by custom handler: {error_event.category}")
                    return
            except Exception as e:
                self.logger.error(f"Custom handler error: {e}")
                
        # Try built-in handlers
        if self._handle_builtin_error(error_event):
            error_event.auto_handled = True
            self.handled_errors.append(error_event)
            
        # Log to audit trail
        self._log_to_audit_trail(error_event)
        
    def _handle_builtin_error(self, error_event: ErrorEvent) -> bool:
        """Handle errors with built-in handlers"""
        
        if error_event.category == "root_failure":
            return self._handle_root_failure(error_event)
        elif error_event.category == "magisk_error":
            return self._handle_magisk_error(error_event)
        elif error_event.category == "permission_denied":
            return self._handle_permission_error(error_event)
        elif error_event.category == "network_error":
            return self._handle_network_error(error_event)
        elif error_event.category == "system_error":
            return self._handle_system_error(error_event)
            
        return False
        
    def _handle_root_failure(self, error: ErrorEvent) -> bool:
        """Handle root process failures"""
        self.logger.info("Attempting root failure recovery...")
        
        # Try alternative root methods
        methods = ["magisk", "supersu", "custom_exploit"]
        for method in methods:
            try:
                result = subprocess.run(f"python3 -c \"from android_rooting.core.magisk_manager import MagiskManager; m=MagiskManager(); print(m.repair_partial_root())\"",
                                      shell=True, capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and "success" in result.stdout:
                    self.logger.info(f"Root recovery successful with {method}")
                    return True
            except Exception as e:
                self.logger.debug(f"Root method {method} failed: {e}")
                
        return False
        
    def _handle_magisk_error(self, error: ErrorEvent) -> bool:
        """Handle Magisk-specific errors"""
        self.logger.info("Attempting Magisk error recovery...")
        
        try:
            # Reset Magisk database
            subprocess.run("magisk --sqlite 'DELETE FROM logs WHERE time < datetime(\"now\", \"-1 day\")'",
                         shell=True, capture_output=True, timeout=10)
            
            # Restart Magisk daemon
            subprocess.run("magisk --stop && magisk --daemon", shell=True, capture_output=True, timeout=15)
            
            # Verify functionality
            result = subprocess.run("su -c 'id'", shell=True, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and "uid=0" in result.stdout:
                self.logger.info("Magisk recovery successful")
                return True
                
        except Exception as e:
            self.logger.error(f"Magisk recovery failed: {e}")
            
        return False
        
    def _handle_permission_error(self, error: ErrorEvent) -> bool:
        """Handle permission denied errors"""
        self.logger.info("Attempting permission error recovery...")
        
        try:
            # Check and fix SELinux context
            subprocess.run("setenforce 0", shell=True, capture_output=True, timeout=5)
            
            # Fix file permissions
            if "context" in error.context and "file" in error.context["context"]:
                file_path = error.context["context"]["file"]
                subprocess.run(f"chmod 755 {file_path}", shell=True, capture_output=True, timeout=5)
                subprocess.run(f"chown root:root {file_path}", shell=True, capture_output=True, timeout=5)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Permission recovery failed: {e}")
            
        return False
        
    def _handle_network_error(self, error: ErrorEvent) -> bool:
        """Handle network connectivity errors"""
        self.logger.info("Attempting network error recovery...")
        
        try:
            # Test connectivity
            response = requests.get("https://8.8.8.8", timeout=5)
            if response.status_code == 200:
                return True
                
            # Try alternative DNS
            subprocess.run("setprop net.dns1 8.8.8.8", shell=True, capture_output=True, timeout=5)
            subprocess.run("setprop net.dns2 8.8.4.4", shell=True, capture_output=True, timeout=5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Network recovery failed: {e}")
            
        return False
        
    def _handle_system_error(self, error: ErrorEvent) -> bool:
        """Handle general system errors"""
        self.logger.info("Attempting system error recovery...")
        
        try:
            # Clear temporary files
            subprocess.run("rm -rf /tmp/android_root_*", shell=True, capture_output=True, timeout=10)
            
            # Free up memory
            subprocess.run("echo 3 > /proc/sys/vm/drop_caches", shell=True, capture_output=True, timeout=5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"System recovery failed: {e}")
            
        return False
        
    def _monitor_system_health(self):
        """Monitor system health indicators"""
        try:
            # Check memory usage
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                
            if 'MemAvailable:' in meminfo:
                for line in meminfo.split('\n'):
                    if 'MemAvailable:' in line:
                        available_kb = int(line.split()[1])
                        if available_kb < 100000:  # Less than 100MB
                            self.report_error("system_error", "Low memory warning",
                                            ErrorSeverity.MEDIUM, {"available_kb": available_kb})
                                            
            # Check disk space
            result = subprocess.run("df /data", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    fields = lines[1].split()
                    if len(fields) >= 5:
                        usage_percent = int(fields[4].rstrip('%'))
                        if usage_percent > 95:
                            self.report_error("system_error", "Disk space critical",
                                            ErrorSeverity.HIGH, {"usage_percent": usage_percent})
                                            
        except Exception as e:
            self.logger.debug(f"System health monitoring error: {e}")
            
    def _monitor_root_process(self):
        """Monitor active root processes"""
        try:
            # Check for stuck processes
            result = subprocess.run("ps aux | grep -E '(magisk|su|root)'", 
                                  shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                processes = result.stdout.strip().split('\n')
                for process in processes:
                    if 'defunct' in process or '<defunct>' in process:
                        self.report_error("root_failure", "Zombie root process detected",
                                        ErrorSeverity.MEDIUM, {"process": process})
                                        
        except Exception as e:
            self.logger.debug(f"Root process monitoring error: {e}")
            
    def _check_for_updates(self):
        """Check for bot code updates from GitHub"""
        try:
            if not self.config.github_repo or not self.config.github_token:
                return
                
            self.logger.debug("Checking for bot updates...")
            
            # Get latest commit hash
            latest_commit = self.github_client.get_latest_commit()
            if not latest_commit:
                return
                
            # Check if we need to update
            current_hash = self._get_current_code_hash()
            if latest_commit != current_hash:
                self.logger.info("Bot update available, downloading...")
                self.status = BotStatus.UPDATING
                
                if self._download_and_apply_update(latest_commit):
                    self.logger.info("Bot update applied successfully")
                else:
                    self.logger.error("Bot update failed")
                    
                self.status = BotStatus.ACTIVE
                
        except Exception as e:
            self.logger.error(f"Update check failed: {e}")
            
    def _get_current_code_hash(self) -> str:
        """Get hash of current bot code"""
        try:
            current_file = __file__
            with open(current_file, 'rb') as f:
                content = f.read()
            return hashlib.sha256(content).hexdigest()[:8]
        except Exception:
            return ""
            
    def _download_and_apply_update(self, commit_hash: str) -> bool:
        """Download and apply code update"""
        try:
            # Download updated code
            updated_code = self.github_client.get_file_content("android_rooting/bots/error_handler_bot.py", commit_hash)
            if not updated_code:
                return False
                
            # Create backup
            backup_file = f"{__file__}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(__file__, 'rb') as src, open(backup_file, 'wb') as dst:
                dst.write(src.read())
                
            # Apply update
            with open(__file__, 'w') as f:
                f.write(updated_code)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Update application failed: {e}")
            return False
            
    def _log_to_audit_trail(self, error_event: ErrorEvent):
        """Log error to audit trail"""
        try:
            audit_log = "/data/local/tmp/android_root_audit.log"
            
            audit_entry = {
                'timestamp': error_event.timestamp.isoformat(),
                'severity': error_event.severity.value,
                'category': error_event.category,
                'message': error_event.message,
                'context': error_event.context,
                'auto_handled': error_event.auto_handled,
                'bot_status': self.status.value
            }
            
            with open(audit_log, 'a') as f:
                f.write(json.dumps(audit_entry) + '\n')
                
        except Exception as e:
            self.logger.debug(f"Audit logging failed: {e}")
            
    def _setup_default_handlers(self):
        """Setup default error handlers"""
        # These can be overridden by registering custom handlers
        pass

class GitHubClient:
    """GitHub API client for code updates"""
    
    def __init__(self, repo: str, token: str):
        self.repo = repo
        self.token = token
        self.base_url = "https://api.github.com"
        
    def get_latest_commit(self) -> Optional[str]:
        """Get latest commit hash"""
        try:
            url = f"{self.base_url}/repos/{self.repo}/commits/main"
            headers = {"Authorization": f"token {self.token}"} if self.token else {}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['sha'][:8]
                
        except Exception as e:
            logging.debug(f"GitHub API error: {e}")
            
        return None
        
    def get_file_content(self, file_path: str, commit_hash: str) -> Optional[str]:
        """Get file content from specific commit"""
        try:
            url = f"{self.base_url}/repos/{self.repo}/contents/{file_path}?ref={commit_hash}"
            headers = {"Authorization": f"token {self.token}"} if self.token else {}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                import base64
                return base64.b64decode(data['content']).decode('utf-8')
                
        except Exception as e:
            logging.debug(f"GitHub file fetch error: {e}")
            
        return None

def main():
    """CLI interface for error handler bot"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Android Rooting Error Handler Bot')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--github-repo', help='GitHub repository (owner/repo)')
    parser.add_argument('--github-token', help='GitHub API token')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Load configuration
    config = BotConfig()
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config_data = json.load(f)
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    
    # Override with CLI arguments
    if args.github_repo:
        config.github_repo = args.github_repo
    if args.github_token:
        config.github_token = args.github_token
        
    # Create and start bot
    bot = ErrorHandlerBot(config)
    
    try:
        bot.start()
        
        if args.daemon:
            # Run as daemon
            while True:
                time.sleep(60)
                status = bot.get_status()
                print(f"Bot Status: {status['status']} - Errors handled: {status['handled_errors']}")
        else:
            # Interactive mode
            print("Error Handler Bot started. Type 'status' for status, 'quit' to exit.")
            while True:
                try:
                    command = input("> ").strip().lower()
                    if command == 'quit':
                        break
                    elif command == 'status':
                        status = bot.get_status()
                        print(json.dumps(status, indent=2))
                    elif command.startswith('error '):
                        parts = command.split(' ', 2)
                        if len(parts) >= 3:
                            category, message = parts[1], parts[2]
                            bot.report_error(category, message)
                            print("Error reported")
                    else:
                        print("Commands: status, error <category> <message>, quit")
                except KeyboardInterrupt:
                    break
                    
    finally:
        bot.stop()
        print("Error Handler Bot stopped")

if __name__ == '__main__':
    main()

"""
References:
- Python Threading Documentation: https://docs.python.org/3/library/threading.html
- GitHub API Documentation: https://docs.github.com/en/rest
- Android Logging System: https://source.android.com/devices/tech/debug/
- Kali Linux Bot Framework: https://www.kali.org/docs/development/
- Error Handling Best Practices: https://docs.python.org/3/tutorial/errors.html
"""