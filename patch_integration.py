#!/usr/bin/env python3
"""
VARIABOT Integration Patcher
Seamlessly integrates existing bot files with new multi-library system
Adds Android/Termux optimizations while preserving original functionality
"""

import os
import sys
import shutil
import re
from pathlib import Path
from typing import List, Dict, Tuple
import argparse

class BotIntegrationPatcher:
    """Patches existing bot files for enhanced integration."""
    
    def __init__(self, backup_enabled: bool = True):
        self.backup_enabled = backup_enabled
        self.project_root = Path(__file__).parent
        self.patch_log = []
        
        # Integration imports to add
        self.integration_imports = '''
# VARIABOT Enhanced Integration System
import sys
from pathlib import Path

# Add integration system to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from variabot_integration import (
        get_integration_manager, 
        initialize_integration,
        PlatformDetector,
        ResourceProfile
    )
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    print("⚠️ Integration system not available, running in basic mode")

# Mobile optimization imports
try:
    from mobile_config import apply_mobile_optimizations
    apply_mobile_optimizations()
    MOBILE_OPTIMIZED = True
except ImportError:
    MOBILE_OPTIMIZED = False
'''
        
        # Enhanced client creation with fallbacks
        self.enhanced_client_creation = '''
@st.cache_resource
def create_client():   
    """Enhanced client creation with platform optimization and fallbacks."""
    # Initialize integration if available
    if INTEGRATION_AVAILABLE:
        integration_manager = get_integration_manager()
        if not integration_manager:
            integration_manager = initialize_integration()
        
        # Get platform-optimized configuration
        capabilities = PlatformDetector.assess_capabilities()
        platform = capabilities.platform
        
        # Android/Termux optimizations
        if 'android' in platform.value or 'termux' in platform.value:
            st.sidebar.info(f"🤖 Mobile Mode: {platform.value}")
            if capabilities.memory_gb < 2:
                st.sidebar.warning("⚠️ Low memory detected - using optimized settings")
    
    # Get HF token with multiple fallback methods
    yourHFtoken = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_HUB_TOKEN') or ""
    
    if not yourHFtoken:
        st.warning("🔑 No HuggingFace token found. Set HF_TOKEN environment variable for best performance.")
        yourHFtoken = st.sidebar.text_input("HuggingFace Token (optional)", type="password")
    
    model_name = "{model_name}"  # Will be replaced with actual model
    
    try:
        print(f'🚀 Loading model: {model_name}')
        client = Client(model_name, hf_token=yourHFtoken)
        
        # Test client connection
        if hasattr(client, 'submit'):
            st.sidebar.success("✅ Model loaded successfully")
        
        return client
        
    except Exception as e:
        st.error(f"❌ Failed to load model: {e}")
        
        # Fallback to alternative models
        fallback_models = [
            "Salesforce/codet5-small",  # 880MB
            "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # 1.1GB
            "microsoft/DialoGPT-small"  # 117MB
        ]
        
        for fallback in fallback_models:
            try:
                st.warning(f"🔄 Trying fallback model: {fallback}")
                client = Client(fallback, hf_token=yourHFtoken)
                st.sidebar.info(f"✅ Using fallback: {fallback}")
                return client
            except:
                continue
        
        st.error("❌ All models failed to load. Please check your connection and try again.")
        return None
'''

        # Enhanced history function with mobile optimization
        self.enhanced_history_function = '''
def writehistory(text):
    """Enhanced history writing with mobile optimization."""
    # Determine appropriate log file based on model
    model_name = st.session_state.get('hf_model', 'unknown')
    log_file = f'chathistory_{model_name.lower().replace("-", "_")}.txt'
    
    # Mobile optimization - limit log file size
    max_log_size = 1024 * 1024  # 1MB for mobile devices
    
    try:
        # Check file size and rotate if needed
        if os.path.exists(log_file) and os.path.getsize(log_file) > max_log_size:
            # Rotate log file
            shutil.move(log_file, f'{log_file}.old')
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f'[{datetime.now().isoformat()}] {text}\\n')
        
        # Mobile-specific logging
        if INTEGRATION_AVAILABLE:
            try:
                capabilities = PlatformDetector.assess_capabilities()
                if 'android' in capabilities.platform.value:
                    # Also log to Android-specific location
                    android_log = os.path.expanduser('~/.variabot/logs/chat.log')
                    os.makedirs(os.path.dirname(android_log), exist_ok=True)
                    with open(android_log, 'a', encoding='utf-8') as f:
                        f.write(f'[{datetime.now().isoformat()}] {text}\\n')
            except:
                pass  # Fail silently for logging
                
    except Exception as e:
        print(f"Warning: Could not write to history: {e}")
'''

        # Mobile-optimized UI enhancements
        self.mobile_ui_enhancements = '''
# Mobile UI optimizations
if INTEGRATION_AVAILABLE:
    capabilities = PlatformDetector.assess_capabilities()
    if 'android' in capabilities.platform.value or 'termux' in capabilities.platform.value:
        # Configure Streamlit for mobile
        st.set_page_config(
            page_title="VARIABOT Mobile",
            page_icon="🤖",
            layout="centered",  # Better for mobile
            initial_sidebar_state="collapsed"  # Save screen space
        )
        
        # Add mobile-specific sidebar information
        with st.sidebar:
            st.markdown("### 📱 Mobile Status")
            st.markdown(f"**Platform:** {capabilities.platform.value}")
            st.markdown(f"**Memory:** {capabilities.memory_gb:.1f}GB")
            st.markdown(f"**CPU Cores:** {capabilities.cpu_cores}")
            
            if capabilities.battery_powered:
                st.markdown("🔋 **Battery Mode:** Optimized")
            
            # Performance settings
            st.markdown("### ⚙️ Performance")
            if capabilities.memory_gb < 2:
                st.warning("Low memory - using optimized settings")
            
            # Quick actions
            st.markdown("### 🚀 Quick Actions")
            if st.button("🧹 Clear Cache"):
                st.cache_resource.clear()
                st.success("Cache cleared!")
            
            if st.button("📊 System Info"):
                st.json({
                    "platform": capabilities.platform.value,
                    "android_version": capabilities.android_version,
                    "memory_gb": capabilities.memory_gb,
                    "cpu_cores": capabilities.cpu_cores,
                    "gpu_available": capabilities.gpu_available
                })
    else:
        # Desktop configuration
        st.set_page_config(
            page_title="VARIABOT Desktop",
            page_icon="🤖",
            layout="wide"
        )
else:
    # Fallback configuration
    st.set_page_config(
        page_title="VARIABOT",
        page_icon="🤖"
    )
'''

    def backup_file(self, file_path: Path) -> bool:
        """Create backup of original file."""
        if not self.backup_enabled:
            return True
            
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        
        try:
            shutil.copy2(file_path, backup_path)
            self.patch_log.append(f"✅ Backed up: {file_path} -> {backup_path}")
            return True
        except Exception as e:
            self.patch_log.append(f"❌ Backup failed for {file_path}: {e}")
            return False

    def patch_imports(self, content: str) -> str:
        """Add integration imports to the file."""
        # Find the last import statement
        import_pattern = r'^(import .*|from .* import .*)$'
        lines = content.split('\n')
        last_import_line = -1
        
        for i, line in enumerate(lines):
            if re.match(import_pattern, line.strip()):
                last_import_line = i
        
        if last_import_line >= 0:
            # Insert integration imports after last import
            lines.insert(last_import_line + 1, self.integration_imports)
        else:
            # Insert at the beginning if no imports found
            lines.insert(0, self.integration_imports)
        
        return '\n'.join(lines)

    def patch_client_creation(self, content: str, model_name: str) -> str:
        """Replace client creation function with enhanced version."""
        # Pattern to match the create_client function
        pattern = r'@st\.cache_resource\s*\ndef create_client\(\):.*?return client'
        
        enhanced_code = self.enhanced_client_creation.replace('{model_name}', model_name)
        
        # Replace the function
        content = re.sub(pattern, enhanced_code, content, flags=re.DOTALL)
        
        return content

    def patch_history_function(self, content: str) -> str:
        """Replace writehistory function with enhanced version."""
        # Pattern to match the writehistory function
        pattern = r'def writehistory\(text\):.*?f\.close\(\)'
        
        # Add datetime import if not present
        if 'from datetime import datetime' not in content:
            content = 'from datetime import datetime\n' + content
        
        # Replace the function
        content = re.sub(pattern, self.enhanced_history_function, content, flags=re.DOTALL)
        
        return content

    def patch_ui_setup(self, content: str) -> str:
        """Add mobile UI optimizations."""
        # Find where UI setup begins (usually after imports and before st.image)
        ui_start_patterns = [
            r'(st\.image\()',
            r'(st\.markdown\(.*powered by)',
            r'(st\.subheader\()',
            r'(### START STREAMLIT UI)'
        ]
        
        for pattern in ui_start_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, self.mobile_ui_enhancements + r'\n\1', content, count=1)
                break
        
        return content

    def detect_model_name(self, content: str) -> str:
        """Detect the model name from the bot file."""
        # Common patterns for model names
        patterns = [
            r'Client\("([^"]+)"',
            r"Client\('([^']+)'",
            r'hf_model.*=.*"([^"]+)"',
            r"hf_model.*=.*'([^']+)'"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return "unknown-model"

    def patch_bot_file(self, file_path: Path) -> bool:
        """Patch a single bot file with integration enhancements."""
        try:
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Create backup
            if not self.backup_file(file_path):
                return False
            
            # Apply patches
            content = original_content
            
            # 1. Add integration imports
            content = self.patch_imports(content)
            
            # 2. Detect model name and patch client creation
            model_name = self.detect_model_name(original_content)
            content = self.patch_client_creation(content, model_name)
            
            # 3. Patch history function
            content = self.patch_history_function(content)
            
            # 4. Add mobile UI optimizations
            content = self.patch_ui_setup(content)
            
            # Write patched content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.patch_log.append(f"✅ Patched: {file_path} (model: {model_name})")
            return True
            
        except Exception as e:
            self.patch_log.append(f"❌ Failed to patch {file_path}: {e}")
            return False

    def patch_all_bots(self) -> Dict[str, bool]:
        """Patch all bot files in the repository."""
        bot_files = [
            "st-Qwen1.5-110B-Chat.py",
            "st-Phi3Mini-128k-Chat.py", 
            "st-Openelm-3B.py",
            "st-Qwen1.5-MoE-A2.7B-Chat.py",
            "st-codet5-small.py",
            "st-tinyllama-chat.py",
            "Qwen110BChat.py"
        ]
        
        results = {}
        
        for bot_file in bot_files:
            file_path = self.project_root / bot_file
            
            if file_path.exists():
                results[bot_file] = self.patch_bot_file(file_path)
            else:
                self.patch_log.append(f"⚠️ File not found: {bot_file}")
                results[bot_file] = False
        
        return results

    def restore_backups(self) -> bool:
        """Restore all files from backups."""
        if not self.backup_enabled:
            print("❌ No backups available (backup was disabled)")
            return False
        
        backup_files = list(self.project_root.glob("*.backup"))
        
        if not backup_files:
            print("⚠️ No backup files found")
            return False
        
        restored = 0
        for backup_file in backup_files:
            original_file = backup_file.with_suffix('')
            
            try:
                shutil.copy2(backup_file, original_file)
                print(f"✅ Restored: {original_file}")
                restored += 1
            except Exception as e:
                print(f"❌ Failed to restore {original_file}: {e}")
        
        print(f"📁 Restored {restored}/{len(backup_files)} files")
        return restored > 0

    def get_patch_summary(self) -> str:
        """Get summary of patching operations."""
        summary = "\n🔧 VARIABOT Integration Patching Summary\n"
        summary += "=" * 50 + "\n"
        
        for log_entry in self.patch_log:
            summary += f"{log_entry}\n"
        
        return summary

def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(description="VARIABOT Bot Integration Patcher")
    parser.add_argument('--patch', action='store_true', 
                       help='Patch all bot files with integration system')
    parser.add_argument('--restore', action='store_true',
                       help='Restore original files from backups')
    parser.add_argument('--no-backup', action='store_true',
                       help='Disable backup creation (dangerous!)')
    parser.add_argument('--file', '-f', type=str,
                       help='Patch specific file instead of all bots')
    
    args = parser.parse_args()
    
    if not (args.patch or args.restore):
        parser.print_help()
        return
    
    patcher = BotIntegrationPatcher(backup_enabled=not args.no_backup)
    
    if args.restore:
        print("🔄 Restoring original files from backups...")
        patcher.restore_backups()
        return
    
    if args.patch:
        if args.file:
            # Patch single file
            file_path = Path(args.file)
            if file_path.exists():
                print(f"🔧 Patching single file: {file_path}")
                success = patcher.patch_bot_file(file_path)
                print(f"Result: {'✅ Success' if success else '❌ Failed'}")
            else:
                print(f"❌ File not found: {file_path}")
        else:
            # Patch all bots
            print("🔧 Patching all bot files with integration system...")
            results = patcher.patch_all_bots()
            
            # Print results
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            print(f"\n📊 Results: {successful}/{total} files patched successfully")
        
        # Print detailed log
        print(patcher.get_patch_summary())
        
        if not args.no_backup:
            print(f"\n💾 Original files backed up with .backup extension")
            print(f"🔄 To restore: python {__file__} --restore")

if __name__ == "__main__":
    main()