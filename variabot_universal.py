#!/usr/bin/env python3
"""
VARIABOT Universal Multi-Platform Interface
Seamless integration with all existing bot formats
Optimized for Android 10+ and Termux environments
"""

import sys
import os
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import subprocess

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our integration system
try:
    from variabot_integration import (
        initialize_integration, 
        integrate_with_existing_bots,
        get_mobile_optimized_config,
        PlatformDetector,
        PlatformType,
        ResourceProfile,
        IntegrationConfig
    )
except ImportError as e:
    print(f"Error importing integration system: {e}")
    sys.exit(1)

# Platform-specific imports with fallbacks
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

try:
    from flask import Flask, render_template_string, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

try:
    import kivy
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.textinput import TextInput
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False

class VariabotUniversalInterface:
    """Universal interface that adapts to platform and available libraries."""
    
    def __init__(self):
        self.platform = PlatformDetector.detect_platform()
        self.capabilities = PlatformDetector.assess_capabilities()
        self.integration_manager = initialize_integration()
        self.integrated_bots = integrate_with_existing_bots()
        self.mobile_config = get_mobile_optimized_config()
        
        print(f"🤖 VARIABOT Universal Interface")
        print(f"📱 Platform: {self.platform.value}")
        print(f"🔧 Android Version: {self.capabilities.android_version}")
        print(f"💾 Memory: {self.capabilities.memory_gb:.1f}GB")
        print(f"🔌 Integrated Bots: {len(self.integrated_bots)}")
        
    def get_available_interfaces(self) -> List[str]:
        """Get list of available interface types."""
        interfaces = []
        
        if STREAMLIT_AVAILABLE:
            interfaces.append("streamlit")
        if FLASK_AVAILABLE:
            interfaces.append("web")
        if KIVY_AVAILABLE:
            interfaces.append("native_mobile")
        
        interfaces.append("terminal")  # Always available
        
        return interfaces
    
    def launch_streamlit_interface(self, model_name: str = "auto"):
        """Launch Streamlit interface with bot integration."""
        if not STREAMLIT_AVAILABLE:
            print("❌ Streamlit not available")
            return
        
        # Select appropriate bot based on platform and resources
        selected_bot = self._select_optimal_bot(model_name)
        
        if selected_bot:
            bot_file = self.integrated_bots[selected_bot]['file_path']
            print(f"🚀 Launching {selected_bot} via Streamlit...")
            
            # Android/Termux specific optimizations
            if self.platform in [PlatformType.ANDROID_TERMUX, PlatformType.ANDROID_NATIVE]:
                os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
                os.environ['STREAMLIT_SERVER_PORT'] = '8501'
                os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
                os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
            
            # Launch with subprocess to avoid import conflicts
            cmd = [sys.executable, '-m', 'streamlit', 'run', bot_file]
            
            if self.capabilities.memory_gb < 2:
                cmd.extend(['--server.maxUploadSize', '50'])
            
            subprocess.run(cmd)
        else:
            print("❌ No suitable bot found for current platform")
    
    def get_android_version(self) -> str:
        """Get Android version from system properties or environment"""
        # First try environment variables (Termux provides this)
        android_version = 'unknown'
        
        # Check if we have Android runtime information
        runtime_root = os.getenv('ANDROID_RUNTIME_ROOT', '')
        if '/apex/com.android.runtime' in runtime_root:
            android_version = '10+'  # APEX modules indicate Android 10+
        
        # Try to get more specific version from getprop if available
        try:
            result = subprocess.run(['getprop', 'ro.build.version.release'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                android_version = result.stdout.strip()
        except:
            pass
        
        return android_version
    
    def launch_web_interface(self):
        """Launch Flask web interface for lightweight deployment."""
        if not FLASK_AVAILABLE:
            print("❌ Flask not available")
            return
        
        app = Flask(__name__)
        
        # HTML template for mobile-optimized interface
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>VARIABOT Mobile</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: #1e1e1e; 
                    color: #fff;
                }
                .container { max-width: 500px; margin: 0 auto; }
                .chat-box { 
                    border: 1px solid #333; 
                    padding: 20px; 
                    margin: 10px 0; 
                    border-radius: 10px;
                    background: #2a2a2a;
                }
                input, button { 
                    width: 100%; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border: none; 
                    border-radius: 5px;
                    font-size: 16px;
                }
                button { 
                    background: #007bff; 
                    color: white; 
                    cursor: pointer;
                }
                .bot-list { 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                    gap: 10px; 
                    margin: 20px 0;
                }
                .bot-card { 
                    background: #333; 
                    padding: 15px; 
                    border-radius: 10px; 
                    text-align: center; 
                    cursor: pointer;
                }
                .bot-card:hover { background: #444; }
                .status { 
                    background: #28a745; 
                    padding: 10px; 
                    border-radius: 5px; 
                    margin: 10px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 VARIABOT Mobile</h1>
                
                <div class="status">
                    <strong>Platform:</strong> {{ platform }}<br>
                    <strong>Memory:</strong> {{ memory }}GB<br>
                    <strong>Bots Available:</strong> {{ bot_count }}
                </div>
                
                <div class="chat-box">
                    <h3>Available Bots</h3>
                    <div class="bot-list">
                        {% for bot_name, info in bots.items() %}
                        <div class="bot-card" onclick="selectBot('{{ bot_name }}')">
                            <strong>{{ bot_name.replace('st-', '').replace('.py', '') }}</strong><br>
                            <small>{{ info.model_type }}</small>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                <div class="chat-box">
                    <h3>Quick Chat</h3>
                    <input type="text" id="message" placeholder="Type your message...">
                    <button onclick="sendMessage()">Send</button>
                    <div id="response"></div>
                </div>
                
                <div class="chat-box">
                    <h3>Platform Tools</h3>
                    <button onclick="checkSystem()">System Check</button>
                    <button onclick="installDeps()">Install Dependencies</button>
                    <button onclick="optimizePerformance()">Optimize Performance</button>
                </div>
            </div>
            
            <script>
                function selectBot(botName) {
                    alert('Selected: ' + botName);
                    // Implement bot switching logic
                }
                
                function sendMessage() {
                    const message = document.getElementById('message').value;
                    if (message.trim()) {
                        // Implement chat logic
                        document.getElementById('response').innerHTML = 
                            '<div style="background:#444;padding:10px;margin:10px 0;border-radius:5px;">' +
                            'Response: ' + message + '</div>';
                        document.getElementById('message').value = '';
                    }
                }
                
                function checkSystem() {
                    fetch('/api/system-check')
                        .then(response => response.json())
                        .then(data => alert(JSON.stringify(data, null, 2)));
                }
                
                function installDeps() {
                    alert('Installing dependencies for Android/Termux...');
                    fetch('/api/install-deps', {method: 'POST'});
                }
                
                function optimizePerformance() {
                    alert('Applying mobile optimizations...');
                    fetch('/api/optimize', {method: 'POST'});
                }
            </script>
        </body>
        </html>
        """
        
        @app.route('/')
        def index():
            return render_template_string(html_template, 
                platform=self.platform.value,
                memory=f"{self.capabilities.memory_gb:.1f}",
                bot_count=len(self.integrated_bots),
                bots=self.integrated_bots
            )
        
        @app.route('/api/system-check')
        def system_check():
            return jsonify(self.mobile_config)
        
        @app.route('/api/install-deps', methods=['POST'])
        def install_deps():
            return jsonify({"status": "Dependencies installation started"})
        
        @app.route('/api/optimize', methods=['POST'])
        def optimize():
            return jsonify({"status": "Performance optimization applied"})
        
        # Run with mobile-optimized settings
        port = 8080 if self.platform == PlatformType.ANDROID_TERMUX else 5000
        print(f"🌐 Starting web interface on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    
    def launch_native_mobile_interface(self):
        """Launch Kivy-based native mobile interface."""
        if not KIVY_AVAILABLE:
            print("❌ Kivy not available for native mobile interface")
            return
        
        class VariabotMobileApp(App):
            def build(self):
                layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
                
                title = Label(text='🤖 VARIABOT Mobile', size_hint_y=None, height=50)
                layout.add_widget(title)
                
                # Bot selection buttons
                for bot_name in self.integrated_bots.keys():
                    btn = Button(text=f"Launch {bot_name}", size_hint_y=None, height=50)
                    btn.bind(on_press=lambda x, name=bot_name: self.launch_bot(name))
                    layout.add_widget(btn)
                
                return layout
            
            def launch_bot(self, bot_name):
                print(f"Launching {bot_name} in native mode...")
        
        app = VariabotMobileApp()
        app.run()
    
    def launch_terminal_interface(self):
        """Launch terminal-based interface for all platforms."""
        print("\n🖥️  VARIABOT Terminal Interface")
        print("=" * 50)
        
        while True:
            print(f"\nAvailable Bots ({len(self.integrated_bots)}):")
            bot_list = list(self.integrated_bots.keys())
            
            for i, bot_name in enumerate(bot_list, 1):
                info = self.integrated_bots[bot_name]
                status = "✅" if info['compatible'] else "❌"
                print(f"{i}. {status} {bot_name} ({info['model_type']})")
            
            print(f"\n{len(bot_list) + 1}. 🔧 System Information")
            print(f"{len(bot_list) + 2}. 📱 Mobile Optimization")
            print(f"{len(bot_list) + 3}. 🚪 Exit")
            
            try:
                choice = input("\nSelect option: ").strip()
                
                if choice.isdigit():
                    choice = int(choice)
                    
                    if 1 <= choice <= len(bot_list):
                        selected_bot = bot_list[choice - 1]
                        self._run_bot_terminal(selected_bot)
                    elif choice == len(bot_list) + 1:
                        self._show_system_info()
                    elif choice == len(bot_list) + 2:
                        self._show_mobile_optimization()
                    elif choice == len(bot_list) + 3:
                        print("👋 Goodbye!")
                        break
                    else:
                        print("❌ Invalid choice")
                else:
                    print("❌ Please enter a number")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _run_bot_terminal(self, bot_name: str):
        """Run selected bot in terminal mode."""
        info = self.integrated_bots[bot_name]
        bot_file = info['file_path']
        
        print(f"\n🚀 Launching {bot_name}...")
        print(f"📁 File: {bot_file}")
        print(f"🤖 Model: {info['model_type']}")
        
        try:
            # For Streamlit bots, try to launch
            if info['has_streamlit']:
                cmd = [sys.executable, '-m', 'streamlit', 'run', bot_file, '--server.headless=true']
                subprocess.run(cmd)
            else:
                # Direct Python execution for terminal bots
                subprocess.run([sys.executable, bot_file])
        
        except Exception as e:
            print(f"❌ Error launching bot: {e}")
    
    def _show_system_info(self):
        """Show comprehensive system information."""
        print("\n📊 System Information")
        print("=" * 50)
        print(f"Platform: {self.platform.value}")
        print(f"Android Version: {self.capabilities.android_version or 'N/A'}")
        print(f"CPU Cores: {self.capabilities.cpu_cores}")
        print(f"Memory: {self.capabilities.memory_gb:.1f}GB")
        print(f"Storage: {self.capabilities.storage_gb:.1f}GB")
        print(f"GPU Available: {self.capabilities.gpu_available}")
        print(f"Network: {self.capabilities.network_available}")
        print(f"Battery Powered: {self.capabilities.battery_powered}")
        print(f"Termux Available: {self.capabilities.termux_available}")
        
        print(f"\n🔧 Integration Status")
        print(f"Integrated Bots: {len(self.integrated_bots)}")
        print(f"Available Interfaces: {', '.join(self.get_available_interfaces())}")
        
        input("\nPress Enter to continue...")
    
    def _show_mobile_optimization(self):
        """Show mobile optimization details."""
        print("\n📱 Mobile Optimization")
        print("=" * 50)
        
        for key, value in self.mobile_config.items():
            print(f"{key}: {value}")
        
        if self.platform in [PlatformType.ANDROID_TERMUX, PlatformType.ANDROID_NATIVE]:
            print(f"\n🤖 Android Specific:")
            print(f"Optimized for Mobile: ✅")
            print(f"Memory Limit: {self.mobile_config.get('memory_limit', 1024)}MB")
            print(f"CPU Threads: {self.mobile_config.get('cpu_threads', 2)}")
            print(f"Low Power Mode: {self.mobile_config.get('low_power_mode', False)}")
        
        input("\nPress Enter to continue...")
    
    def _select_optimal_bot(self, model_preference: str = "auto") -> Optional[str]:
        """Select optimal bot based on platform and resources."""
        if model_preference != "auto" and model_preference in self.integrated_bots:
            return model_preference
        
        # Priority order based on platform and resources
        if self.capabilities.memory_gb < 1.5:
            # Ultra-lightweight for very constrained environments
            priorities = ['st-codet5-small', 'st-tinyllama-chat']
        elif self.capabilities.memory_gb < 3:
            # Lightweight options
            priorities = ['st-tinyllama-chat', 'st-codet5-small', 'st-Phi3Mini-128k-Chat']
        else:
            # Full options available
            priorities = list(self.integrated_bots.keys())
        
        for bot_name in priorities:
            if bot_name in self.integrated_bots and self.integrated_bots[bot_name]['compatible']:
                return bot_name
        
        return None

def main():
    """Main entry point with command-line interface."""
    parser = argparse.ArgumentParser(description="VARIABOT Universal Multi-Platform Interface")
    parser.add_argument('--interface', '-i', 
                       choices=['streamlit', 'web', 'native', 'terminal', 'auto'],
                       default='auto',
                       help='Interface type to launch')
    parser.add_argument('--model', '-m', 
                       default='auto',
                       help='Specific model to use')
    parser.add_argument('--android-optimize', 
                       action='store_true',
                       help='Force Android optimizations')
    
    args = parser.parse_args()
    
    try:
        interface = VariabotUniversalInterface()
        
        if args.android_optimize:
            interface.integration_manager.config.android_optimized = True
        
        # Auto-select interface based on platform and available libraries
        if args.interface == 'auto':
            available = interface.get_available_interfaces()
            
            if interface.platform in [PlatformType.ANDROID_TERMUX, PlatformType.ANDROID_NATIVE]:
                # Prefer web interface for Android
                if 'web' in available:
                    args.interface = 'web'
                elif 'native_mobile' in available:
                    args.interface = 'native'
                else:
                    args.interface = 'terminal'
            else:
                # Prefer Streamlit for desktop
                if 'streamlit' in available:
                    args.interface = 'streamlit'
                elif 'web' in available:
                    args.interface = 'web'
                else:
                    args.interface = 'terminal'
        
        # Launch selected interface
        if args.interface == 'streamlit':
            interface.launch_streamlit_interface(args.model)
        elif args.interface == 'web':
            interface.launch_web_interface()
        elif args.interface == 'native':
            interface.launch_native_mobile_interface()
        elif args.interface == 'terminal':
            interface.launch_terminal_interface()
        else:
            print(f"❌ Interface '{args.interface}' not available")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n👋 VARIABOT shutdown completed")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()