#!/usr/bin/env python3
"""
Kali Linux Integration Module for Android Rooting Framework
Integrates Kali Linux tools and NetHunter capabilities for advanced Android testing

This module provides:
- Kali NetHunter integration and setup
- Alpine Linux ARM64 support for containerized environments
- LLM integration for intelligent analysis
- Advanced networking and exploitation tools
- HackTricks methodology implementation

Compatible with: Kali Linux, NetHunter, Alpine Linux ARM64, Android 10+
References: 
- https://www.blackmoreops.com/install-llm-on-kali-linux/
- https://gitlab.com/kalilinux/nethunter/build-scripts/kali-nethunter-project.git
- https://book.hacktricks.wiki/en/mobile-pentesting/android-app-pentesting
"""

import os
import sys
import subprocess
import json
import logging
import tempfile
import shutil
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import yaml
from dataclasses import dataclass
import threading
import time

@dataclass
class KaliEnvironment:
    """Kali Linux environment information"""
    is_kali: bool
    version: str
    architecture: str
    tools_available: Dict[str, bool]
    nethunter_installed: bool
    llm_support: bool

@dataclass
class NetHunterConfig:
    """NetHunter configuration structure"""
    device_type: str
    kernel_version: str
    android_version: str
    chroot_path: str
    services_enabled: List[str]

class KaliIntegration:
    """
    Kali Linux integration for Android rooting and penetration testing
    
    Provides integration with Kali Linux tools, NetHunter, and advanced
    exploitation frameworks for comprehensive Android security testing.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.kali_env = self._detect_kali_environment()
        self.nethunter_config = None
        self.llm_client = None
        self.temp_dir = tempfile.mkdtemp(prefix="kali_android_")
        
        # Tool paths
        self.tools = self._initialize_kali_tools()
        
        # LLM configuration
        self.llm_config = {
            'enabled': False,
            'model_path': '/opt/llm/models',
            'api_endpoint': 'http://localhost:8080',
            'max_tokens': 2048
        }
        
    def _detect_kali_environment(self) -> KaliEnvironment:
        """Detect Kali Linux environment and capabilities"""
        self.logger.info("Detecting Kali Linux environment...")
        
        env = KaliEnvironment(
            is_kali=False,
            version='unknown',
            architecture='unknown',
            tools_available={},
            nethunter_installed=False,
            llm_support=False
        )
        
        try:
            # Check if running on Kali Linux
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    os_info = f.read()
                    
                if 'kali' in os_info.lower():
                    env.is_kali = True
                    
                    # Extract version
                    for line in os_info.split('\n'):
                        if line.startswith('VERSION='):
                            env.version = line.split('=')[1].strip('"')
                            break
                            
            # Check architecture
            try:
                arch_result = subprocess.run(['uname', '-m'], capture_output=True, text=True, timeout=5)
                if arch_result.returncode == 0:
                    env.architecture = arch_result.stdout.strip()
            except Exception:
                pass
                
            # Check for NetHunter
            if os.path.exists('/usr/share/kali-nethunter') or os.path.exists('/system/etc/init.d/99nethunter'):
                env.nethunter_installed = True
                
            # Check for LLM support
            if os.path.exists('/opt/llm') or shutil.which('ollama') or shutil.which('llama'):
                env.llm_support = True
                
        except Exception as e:
            self.logger.error(f"Environment detection failed: {e}")
            
        self.logger.info(f"Kali environment: {env.is_kali}, NetHunter: {env.nethunter_installed}")
        return env
    
    def _initialize_kali_tools(self) -> Dict[str, str]:
        """Initialize Kali Linux security tools"""
        tools = {}
        
        # Core penetration testing tools
        kali_tools = [
            # Network tools
            'nmap', 'masscan', 'zmap', 'nikto', 'dirb', 'gobuster',
            # Mobile tools
            'adb', 'fastboot', 'aapt', 'dex2jar', 'jadx', 'apktool',
            # Reverse engineering
            'radare2', 'ghidra', 'binwalk', 'strings', 'hexdump',
            # Exploitation tools
            'metasploit', 'sqlmap', 'burpsuite', 'zaproxy',
            # Android specific
            'drozer', 'objection', 'frida', 'mobsf',
            # Network analysis
            'wireshark', 'tcpdump', 'tshark', 'ettercap',
            # Social engineering
            'setoolkit', 'beef-xss',
            # Wireless
            'aircrack-ng', 'reaver', 'pixiewps', 'bully',
            # Web application
            'wpscan', 'joomscan', 'dirsearch',
            # LLM and AI tools
            'ollama', 'llama', 'chatgpt-shell'
        ]
        
        for tool in kali_tools:
            tool_path = shutil.which(tool)
            if tool_path:
                tools[tool] = tool_path
                self.logger.debug(f"Found Kali tool: {tool} at {tool_path}")
            else:
                # Check alternative locations
                alt_paths = [
                    f'/usr/bin/{tool}',
                    f'/usr/local/bin/{tool}',
                    f'/opt/{tool}/bin/{tool}',
                    f'/usr/share/{tool}/{tool}'
                ]
                
                for alt_path in alt_paths:
                    if os.path.exists(alt_path) and os.access(alt_path, os.X_OK):
                        tools[tool] = alt_path
                        self.logger.debug(f"Found Kali tool: {tool} at {alt_path}")
                        break
                        
        self.kali_env.tools_available = {tool: tool in tools for tool in kali_tools}
        return tools
    
    def setup_nethunter_environment(self) -> bool:
        """Setup NetHunter environment for Android testing"""
        self.logger.info("Setting up NetHunter environment...")
        
        if not self.kali_env.is_kali and not self.kali_env.nethunter_installed:
            self.logger.warning("NetHunter not detected, attempting setup...")
            
        try:
            # Check if NetHunter chroot exists
            chroot_paths = [
                '/data/local/nhsystem',
                '/data/data/com.offsec.nethunter/files/chroot',
                '/sdcard/kali-arm64'
            ]
            
            chroot_path = None
            for path in chroot_paths:
                if os.path.exists(path):
                    chroot_path = path
                    break
                    
            if not chroot_path:
                self.logger.info("Setting up NetHunter chroot...")
                chroot_path = self._setup_nethunter_chroot()
                
            if chroot_path:
                self.nethunter_config = NetHunterConfig(
                    device_type='android',
                    kernel_version=self._get_kernel_version(),
                    android_version=self._get_android_version(),
                    chroot_path=chroot_path,
                    services_enabled=[]
                )
                
                # Start essential services
                self._start_nethunter_services()
                
                self.logger.info("NetHunter environment configured")
                return True
            else:
                self.logger.error("NetHunter setup failed")
                return False
                
        except Exception as e:
            self.logger.error(f"NetHunter setup failed: {e}")
            return False
    
    def _setup_nethunter_chroot(self) -> Optional[str]:
        """Setup NetHunter chroot environment"""
        self.logger.info("Setting up NetHunter chroot...")
        
        try:
            # Download NetHunter rootfs if needed
            chroot_path = '/sdcard/kali-arm64'
            
            if not os.path.exists(chroot_path):
                os.makedirs(chroot_path, exist_ok=True)
                
                # Check if we can download Alpine ARM64 as alternative
                alpine_url = "https://dl-cdn.alpinelinux.org/alpine/v3.22/releases/aarch64/alpine-uboot-3.22.1-aarch64.tar.gz"
                
                self.logger.info("Downloading Alpine Linux ARM64 rootfs...")
                if self._download_and_extract_rootfs(alpine_url, chroot_path):
                    # Configure Alpine for NetHunter use
                    self._configure_alpine_nethunter(chroot_path)
                    return chroot_path
                    
            return chroot_path if os.path.exists(chroot_path) else None
            
        except Exception as e:
            self.logger.error(f"Chroot setup failed: {e}")
            return None
    
    def _download_and_extract_rootfs(self, url: str, dest_path: str) -> bool:
        """Download and extract rootfs"""
        try:
            import tarfile
            
            # Download file
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            tar_path = os.path.join(self.temp_dir, 'rootfs.tar.gz')
            with open(tar_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            # Extract
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(dest_path)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Rootfs download failed: {e}")
            return False
    
    def _configure_alpine_nethunter(self, chroot_path: str):
        """Configure Alpine Linux for NetHunter use"""
        try:
            # Create basic NetHunter directories
            dirs = ['etc', 'usr/bin', 'usr/share', 'var/log', 'tmp']
            for dir_name in dirs:
                os.makedirs(os.path.join(chroot_path, dir_name), exist_ok=True)
                
            # Create basic configuration files
            resolv_conf = os.path.join(chroot_path, 'etc/resolv.conf')
            with open(resolv_conf, 'w') as f:
                f.write('nameserver 8.8.8.8\nnameserver 1.1.1.1\n')
                
            # Create simple package manager wrapper
            apk_wrapper = os.path.join(chroot_path, 'usr/bin/apt')
            with open(apk_wrapper, 'w') as f:
                f.write('#!/bin/sh\n# APK wrapper for NetHunter compatibility\napk "$@"\n')
            os.chmod(apk_wrapper, 0o755)
            
        except Exception as e:
            self.logger.error(f"Alpine configuration failed: {e}")
    
    def _get_kernel_version(self) -> str:
        """Get kernel version"""
        try:
            result = subprocess.run(['uname', '-r'], capture_output=True, text=True, timeout=5)
            return result.stdout.strip() if result.returncode == 0 else 'unknown'
        except Exception:
            return 'unknown'
    
    def _get_android_version(self) -> str:
        """Get Android version"""
        try:
            if shutil.which('getprop'):
                result = subprocess.run(['getprop', 'ro.build.version.release'], 
                                      capture_output=True, text=True, timeout=5)
                return result.stdout.strip() if result.returncode == 0 else 'unknown'
        except Exception:
            pass
        return 'unknown'
    
    def _start_nethunter_services(self):
        """Start essential NetHunter services"""
        services = ['ssh', 'postgresql', 'apache2', 'hostapd']
        
        for service in services:
            try:
                if self.nethunter_config and os.path.exists(self.nethunter_config.chroot_path):
                    # Try to start service in chroot
                    cmd = f"chroot {self.nethunter_config.chroot_path} service {service} start"
                    result = subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
                    
                    if result.returncode == 0:
                        self.nethunter_config.services_enabled.append(service)
                        self.logger.debug(f"Started NetHunter service: {service}")
                        
            except Exception as e:
                self.logger.debug(f"Service {service} start failed: {e}")
    
    def setup_llm_integration(self, model_name: str = 'llama3') -> bool:
        """
        Setup LLM integration for intelligent analysis
        
        Based on: https://www.blackmoreops.com/install-llm-on-kali-linux/
        """
        self.logger.info("Setting up LLM integration...")
        
        try:
            # Check if Ollama is available
            if 'ollama' in self.tools:
                self.logger.info("Found Ollama, configuring...")
                
                # Start Ollama service
                ollama_start = subprocess.run(['ollama', 'serve'], 
                                            capture_output=True, timeout=5)
                
                # Pull model
                if model_name:
                    self.logger.info(f"Pulling LLM model: {model_name}")
                    pull_result = subprocess.run(['ollama', 'pull', model_name],
                                               capture_output=True, text=True, timeout=300)
                    
                    if pull_result.returncode == 0:
                        self.llm_config['enabled'] = True
                        self.llm_config['model_name'] = model_name
                        self.logger.info("LLM integration configured")
                        return True
                        
            # Alternative: Check for other LLM installations
            elif os.path.exists('/opt/llm'):
                self.llm_config['enabled'] = True
                self.llm_config['model_path'] = '/opt/llm/models'
                return True
                
            else:
                self.logger.info("Installing Ollama for LLM support...")
                return self._install_ollama()
                
        except Exception as e:
            self.logger.error(f"LLM setup failed: {e}")
            
        return False
    
    def _install_ollama(self) -> bool:
        """Install Ollama for LLM support"""
        try:
            # Download and install Ollama
            install_cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
            result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info("Ollama installed successfully")
                # Update tools
                self.tools['ollama'] = shutil.which('ollama')
                return True
            else:
                self.logger.error(f"Ollama installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Ollama installation error: {e}")
            return False
    
    def analyze_with_llm(self, analysis_data: Dict, query: str = "") -> Dict:
        """Use LLM for intelligent analysis of security findings"""
        if not self.llm_config['enabled']:
            self.logger.warning("LLM not enabled, skipping intelligent analysis")
            return {'analysis': 'LLM not available', 'recommendations': []}
            
        try:
            # Prepare analysis prompt
            prompt = self._create_analysis_prompt(analysis_data, query)
            
            # Query LLM
            if 'ollama' in self.tools:
                response = self._query_ollama(prompt)
            else:
                response = self._query_local_llm(prompt)
                
            return self._parse_llm_response(response)
            
        except Exception as e:
            self.logger.error(f"LLM analysis failed: {e}")
            return {'analysis': f'LLM analysis failed: {e}', 'recommendations': []}
    
    def _create_analysis_prompt(self, data: Dict, query: str) -> str:
        """Create analysis prompt for LLM"""
        base_prompt = """
You are a cybersecurity expert specializing in Android application security and penetration testing.
Analyze the following security findings and provide detailed insights and recommendations.

Security Analysis Data:
"""
        
        # Add analysis data
        base_prompt += json.dumps(data, indent=2)
        
        if query:
            base_prompt += f"\n\nSpecific Question: {query}"
            
        base_prompt += """

Please provide:
1. Summary of key security issues
2. Risk assessment (High/Medium/Low) for each finding
3. Detailed remediation steps
4. Additional testing recommendations
5. Best practices for secure development

Format your response as structured analysis with clear sections.
"""
        
        return base_prompt
    
    def _query_ollama(self, prompt: str) -> str:
        """Query Ollama LLM"""
        try:
            model_name = self.llm_config.get('model_name', 'llama3')
            
            # Create temporary file for prompt
            prompt_file = os.path.join(self.temp_dir, 'llm_prompt.txt')
            with open(prompt_file, 'w') as f:
                f.write(prompt)
                
            # Query Ollama
            cmd = ['ollama', 'run', model_name, '--file', prompt_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return result.stdout
            else:
                self.logger.error(f"Ollama query failed: {result.stderr}")
                return "LLM query failed"
                
        except Exception as e:
            self.logger.error(f"Ollama query error: {e}")
            return f"LLM error: {e}"
    
    def _query_local_llm(self, prompt: str) -> str:
        """Query local LLM API"""
        try:
            import requests
            
            response = requests.post(
                self.llm_config['api_endpoint'] + '/generate',
                json={
                    'prompt': prompt,
                    'max_tokens': self.llm_config['max_tokens']
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json().get('text', 'No response')
            else:
                return f"API error: {response.status_code}"
                
        except Exception as e:
            return f"Local LLM error: {e}"
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM response into structured format"""
        try:
            # Simple parsing - in production, this could be more sophisticated
            lines = response.split('\n')
            
            analysis = {
                'summary': '',
                'recommendations': [],
                'risk_assessment': {},
                'raw_response': response
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                
                if 'summary' in line.lower():
                    current_section = 'summary'
                elif 'recommendation' in line.lower():
                    current_section = 'recommendations'
                elif 'risk' in line.lower():
                    current_section = 'risk'
                elif line.startswith('- ') or line.startswith('* '):
                    if current_section == 'recommendations':
                        analysis['recommendations'].append(line[2:])
                elif current_section == 'summary' and line:
                    analysis['summary'] += line + ' '
                    
            return analysis
            
        except Exception as e:
            self.logger.error(f"LLM response parsing failed: {e}")
            return {
                'summary': 'Parsing failed',
                'recommendations': [],
                'risk_assessment': {},
                'raw_response': response
            }
    
    def perform_advanced_network_scan(self, target: str) -> Dict:
        """Perform advanced network scanning using Kali tools"""
        self.logger.info(f"Performing advanced network scan of: {target}")
        
        scan_results = {
            'nmap_scan': {},
            'masscan_results': {},
            'vulnerability_scan': {},
            'service_enumeration': {}
        }
        
        try:
            # Nmap comprehensive scan
            if 'nmap' in self.tools:
                scan_results['nmap_scan'] = self._run_nmap_scan(target)
                
            # Masscan for fast port discovery
            if 'masscan' in self.tools:
                scan_results['masscan_results'] = self._run_masscan(target)
                
            # Vulnerability scanning
            if 'nmap' in self.tools:
                scan_results['vulnerability_scan'] = self._run_vuln_scan(target)
                
            # Service enumeration
            scan_results['service_enumeration'] = self._enumerate_services(target)
            
        except Exception as e:
            self.logger.error(f"Network scan failed: {e}")
            
        return scan_results
    
    def _run_nmap_scan(self, target: str) -> Dict:
        """Run comprehensive Nmap scan"""
        try:
            # TCP SYN scan with service detection
            cmd = [self.tools['nmap'], '-sS', '-sV', '-O', '-A', '--script=default', '-T4', target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            return {
                'command': ' '.join(cmd),
                'output': result.stdout,
                'errors': result.stderr,
                'success': result.returncode == 0
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _run_masscan(self, target: str) -> Dict:
        """Run Masscan for fast port scanning"""
        try:
            cmd = [self.tools['masscan'], '-p1-65535', target, '--rate=1000']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            return {
                'command': ' '.join(cmd),
                'output': result.stdout,
                'errors': result.stderr,
                'success': result.returncode == 0
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _run_vuln_scan(self, target: str) -> Dict:
        """Run vulnerability scan using Nmap scripts"""
        try:
            cmd = [self.tools['nmap'], '--script=vuln', '-sV', target]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            return {
                'command': ' '.join(cmd),
                'output': result.stdout,
                'errors': result.stderr,
                'success': result.returncode == 0
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _enumerate_services(self, target: str) -> Dict:
        """Enumerate services using various tools"""
        services = {}
        
        # HTTP enumeration
        if 'nikto' in self.tools:
            try:
                cmd = [self.tools['nikto'], '-h', target]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                services['nikto'] = {
                    'output': result.stdout,
                    'success': result.returncode == 0
                }
            except Exception:
                pass
                
        # Directory brute force
        if 'dirb' in self.tools:
            try:
                cmd = [self.tools['dirb'], f'http://{target}']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                services['dirb'] = {
                    'output': result.stdout,
                    'success': result.returncode == 0
                }
            except Exception:
                pass
                
        return services
    
    def generate_comprehensive_report(self, scan_data: Dict, pentest_data: Dict, llm_analysis: Dict) -> str:
        """Generate comprehensive security report"""
        self.logger.info("Generating comprehensive security report...")
        
        report_path = os.path.join(self.temp_dir, 'comprehensive_security_report.html')
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Comprehensive Android Security Assessment</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .section {{ margin: 30px; }}
        .section h2 {{ color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .critical {{ background: #e74c3c; color: white; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .high {{ background: #e67e22; color: white; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .medium {{ background: #f39c12; color: white; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .low {{ background: #27ae60; color: white; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .info-panel {{ background: #ecf0f1; border-left: 5px solid #3498db; padding: 20px; margin: 15px 0; }}
        .code-block {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto; }}
        .tool-result {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .llm-analysis {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #f8f9fa; font-weight: bold; }}
        .metric {{ text-align: center; padding: 20px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Comprehensive Android Security Assessment</h1>
            <p>Advanced Penetration Testing Report</p>
            <p>Powered by Kali Linux • NetHunter • AI Analysis</p>
        </div>
        
        <div class="section">
            <h2>📊 Executive Summary</h2>
            <div class="info-panel">
                <p>This comprehensive security assessment was conducted using advanced Kali Linux tools, 
                NetHunter capabilities, and AI-powered analysis to evaluate the security posture of 
                the target Android application and infrastructure.</p>
            </div>
            
            <div style="display: flex; justify-content: space-around; margin: 30px 0;">
                <div class="metric">
                    <div class="metric-value">{len(pentest_data.get('security_issues', []))}</div>
                    <div class="metric-label">Security Issues</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{len(scan_data.get('nmap_scan', {}).get('output', '').split('\\n'))}</div>
                    <div class="metric-label">Network Findings</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{'✓' if self.llm_config['enabled'] else '✗'}</div>
                    <div class="metric-label">AI Analysis</div>
                </div>
            </div>
        </div>
        
        {self._generate_kali_environment_section()}
        
        {self._generate_network_assessment_section(scan_data)}
        
        {self._generate_mobile_assessment_section(pentest_data)}
        
        {self._generate_llm_analysis_section(llm_analysis)}
        
        {self._generate_recommendations_section(pentest_data, llm_analysis)}
        
        <div class="section">
            <h2>🛠️ Tools and Methodologies</h2>
            <div class="info-panel">
                <h3>Kali Linux Tools Used:</h3>
                <ul>
                    {self._generate_tools_list()}
                </ul>
                
                <h3>Methodologies:</h3>
                <ul>
                    <li><strong>OWASP Mobile Security Testing Guide (MSTG)</strong></li>
                    <li><strong>HackTricks Android Pentesting</strong></li>
                    <li><strong>Kali NetHunter Framework</strong></li>
                    <li><strong>AI-Powered Vulnerability Analysis</strong></li>
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>📚 References</h2>
            <ul>
                <li><a href="https://book.hacktricks.wiki/en/mobile-pentesting/android-app-pentesting">HackTricks Android App Pentesting</a></li>
                <li><a href="https://owasp.org/www-project-mobile-security-testing-guide/">OWASP Mobile Security Testing Guide</a></li>
                <li><a href="https://www.kali.org/docs/nethunter/">Kali NetHunter Documentation</a></li>
                <li><a href="https://www.blackmoreops.com/install-llm-on-kali-linux/">LLM on Kali Linux Setup</a></li>
                <li><a href="https://gitlab.com/kalilinux/nethunter/build-scripts/kali-nethunter-project.git">NetHunter Project</a></li>
            </ul>
        </div>
    </div>
</body>
</html>
        """
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            self.logger.info(f"Comprehensive report generated: {report_path}")
            return report_path
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return ""
    
    def _generate_kali_environment_section(self) -> str:
        """Generate Kali environment section"""
        return f"""
        <div class="section">
            <h2>🐉 Kali Linux Environment</h2>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                <tr><td>Kali Linux Detected</td><td>{'✓ Yes' if self.kali_env.is_kali else '✗ No'}</td></tr>
                <tr><td>Version</td><td>{self.kali_env.version}</td></tr>
                <tr><td>Architecture</td><td>{self.kali_env.architecture}</td></tr>
                <tr><td>NetHunter</td><td>{'✓ Installed' if self.kali_env.nethunter_installed else '✗ Not Found'}</td></tr>
                <tr><td>LLM Support</td><td>{'✓ Available' if self.kali_env.llm_support else '✗ Not Available'}</td></tr>
                <tr><td>Tools Available</td><td>{sum(self.kali_env.tools_available.values())} / {len(self.kali_env.tools_available)}</td></tr>
            </table>
        </div>
        """
    
    def _generate_network_assessment_section(self, scan_data: Dict) -> str:
        """Generate network assessment section"""
        return f"""
        <div class="section">
            <h2>🌐 Network Security Assessment</h2>
            
            {self._format_scan_results('Nmap Scan', scan_data.get('nmap_scan', {}))}
            
            {self._format_scan_results('Masscan Results', scan_data.get('masscan_results', {}))}
            
            {self._format_scan_results('Vulnerability Scan', scan_data.get('vulnerability_scan', {}))}
        </div>
        """
    
    def _generate_mobile_assessment_section(self, pentest_data: Dict) -> str:
        """Generate mobile assessment section"""
        issues_html = ""
        for issue in pentest_data.get('security_issues', []):
            severity_class = issue.get('severity', 'low').lower()
            issues_html += f"""
            <div class="{severity_class}">
                <h4>{issue.get('issue', 'Unknown Issue')} ({issue.get('severity', 'Unknown')})</h4>
                <p><strong>Category:</strong> {issue.get('category', 'General')}</p>
                <p><strong>Description:</strong> {issue.get('description', 'No description')}</p>
                <p><strong>Remediation:</strong> {issue.get('remediation', 'No remediation provided')}</p>
            </div>
            """
            
        return f"""
        <div class="section">
            <h2>📱 Mobile Application Assessment</h2>
            {issues_html if issues_html else '<p>No mobile security issues identified</p>'}
        </div>
        """
    
    def _generate_llm_analysis_section(self, llm_analysis: Dict) -> str:
        """Generate LLM analysis section"""
        if not llm_analysis or not self.llm_config['enabled']:
            return """
            <div class="section">
                <h2>🤖 AI Security Analysis</h2>
                <div class="info-panel">
                    <p>AI analysis not available. Enable LLM integration for intelligent security insights.</p>
                </div>
            </div>
            """
            
        return f"""
        <div class="section">
            <h2>🤖 AI Security Analysis</h2>
            <div class="llm-analysis">
                <h3>AI-Powered Insights</h3>
                <p><strong>Summary:</strong> {llm_analysis.get('summary', 'No summary available')}</p>
                
                <h3>AI Recommendations:</h3>
                <ul>
                    {''.join([f'<li>{rec}</li>' for rec in llm_analysis.get('recommendations', [])])}
                </ul>
            </div>
        </div>
        """
    
    def _generate_recommendations_section(self, pentest_data: Dict, llm_analysis: Dict) -> str:
        """Generate recommendations section"""
        return """
        <div class="section">
            <h2>🔧 Security Recommendations</h2>
            <div class="info-panel">
                <h3>Immediate Actions:</h3>
                <ul>
                    <li>Address all HIGH and CRITICAL severity issues immediately</li>
                    <li>Implement proper certificate pinning for network communications</li>
                    <li>Review and restrict exported Android components</li>
                    <li>Enable comprehensive logging and monitoring</li>
                </ul>
                
                <h3>Long-term Security Improvements:</h3>
                <ul>
                    <li>Implement automated security testing in CI/CD pipeline</li>
                    <li>Regular penetration testing and security assessments</li>
                    <li>Security awareness training for development team</li>
                    <li>Establish secure coding guidelines and review processes</li>
                </ul>
            </div>
        </div>
        """
    
    def _generate_tools_list(self) -> str:
        """Generate HTML list of available tools"""
        tools_html = ""
        for tool, available in self.kali_env.tools_available.items():
            status = "✓" if available else "✗"
            tools_html += f"<li>{status} {tool}</li>"
        return tools_html
    
    def _format_scan_results(self, title: str, results: Dict) -> str:
        """Format scan results for HTML display"""
        if not results or not results.get('success'):
            return f"""
            <div class="tool-result">
                <h3>{title}</h3>
                <p>Scan not completed or failed</p>
            </div>
            """
            
        output = results.get('output', 'No output')[:2000]  # Limit output length
        
        return f"""
        <div class="tool-result">
            <h3>{title}</h3>
            <div class="code-block">
                <pre>{output}</pre>
            </div>
        </div>
        """
    
    def cleanup(self):
        """Clean up temporary files and resources"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.logger.info("Kali integration cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

def main():
    """CLI interface for Kali Linux integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kali Linux Integration for Android Security Testing')
    parser.add_argument('action', choices=['env-info', 'setup-nethunter', 'setup-llm', 'network-scan', 'full-assessment'],
                       help='Action to perform')
    parser.add_argument('--target', help='Target for network scanning')
    parser.add_argument('--package', help='Android package for assessment')
    parser.add_argument('--model', default='llama3', help='LLM model to use')
    parser.add_argument('--output', help='Output directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    kali = KaliIntegration()
    
    try:
        if args.action == 'env-info':
            env_info = {
                'kali_environment': kali.kali_env.__dict__,
                'nethunter_config': kali.nethunter_config.__dict__ if kali.nethunter_config else None,
                'tools_available': kali.tools,
                'llm_config': kali.llm_config
            }
            print(json.dumps(env_info, indent=2, default=str))
            
        elif args.action == 'setup-nethunter':
            success = kali.setup_nethunter_environment()
            print(f"NetHunter setup: {'Success' if success else 'Failed'}")
            
        elif args.action == 'setup-llm':
            success = kali.setup_llm_integration(args.model)
            print(f"LLM setup: {'Success' if success else 'Failed'}")
            
        elif args.action == 'network-scan':
            if not args.target:
                print("Error: --target required for network scanning")
                return 1
                
            results = kali.perform_advanced_network_scan(args.target)
            print(json.dumps(results, indent=2, default=str))
            
        elif args.action == 'full-assessment':
            if not args.target:
                print("Error: --target required for full assessment")
                return 1
                
            # Network assessment
            print("Performing network assessment...")
            scan_data = kali.perform_advanced_network_scan(args.target)
            
            # Mock pentest data (would integrate with actual pentest module)
            pentest_data = {'security_issues': []}
            
            # LLM analysis
            llm_analysis = {}
            if kali.llm_config['enabled']:
                print("Performing AI analysis...")
                llm_analysis = kali.analyze_with_llm(scan_data)
                
            # Generate report
            print("Generating comprehensive report...")
            report_path = kali.generate_comprehensive_report(scan_data, pentest_data, llm_analysis)
            
            if report_path:
                print(f"Assessment complete. Report: {report_path}")
            else:
                print("Report generation failed")
                return 1
                
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        kali.cleanup()
        
    return 0

if __name__ == '__main__':
    sys.exit(main())

"""
References:
- Kali Linux Documentation: https://www.kali.org/docs/
- NetHunter Project: https://gitlab.com/kalilinux/nethunter/build-scripts/kali-nethunter-project.git
- LLM on Kali Linux: https://www.blackmoreops.com/install-llm-on-kali-linux/
- Alpine Linux ARM64: https://dl-cdn.alpinelinux.org/alpine/v3.22/releases/aarch64/
- HackTricks Android Pentesting: https://book.hacktricks.wiki/en/mobile-pentesting/android-app-pentesting
- APK Tools: https://gitlab.alpinelinux.org/alpine/apk-tools.git
- OWASP Mobile Security Testing Guide: https://owasp.org/www-project-mobile-security-testing-guide/
"""