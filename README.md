

# VARIABOT - Advanced AI & Android Rooting Framework

# VARIABOT - Agentic AI & Android Rooting Matrix


A comprehensive, self-evolving framework combining a multi-agent AI rooting system with a versatile chatbot interface.

## Table of Contents
- [🚀 Features](#-features)
- [📋 Quick Start](#-quick-start)
- [🏗️ Project Structure](#️-project-structure)
- [🔧 Android Rooting Features](#-android-rooting-features)
- [🤖 AI Chatbot Interfaces](#-ai-chatbot-interfaces)
- [📚 Documentation](#-documentation)
- [🛠️ Installation](#️-installation)
- [🚨 Usage Examples](#-usage-examples)
- [🔒 Security & Legal](#-security--legal)
- [🤝 Contributing](#-contributing)
- [📊 Project Stats](#-project-stats)
- [🙏 Acknowledgments](#-acknowledgments)
- [📄 License](#-license)
- [References](#references)

## 🚀 Features

### 👾 Agentic Rooting System (The "Agentic-Matrix")
An autonomous, multi-agent system designed to achieve root access on Android devices with minimal human intervention.
- **Sriracha Army Architecture**: A hierarchical agent system featuring a `Commander` manager and specialized `Soldier` bots.
- **The Agentic Wheel**: An automated rooting process that continuously adapts and mutates its strategy. It cycles through tens of thousands of tool and parameter combinations until it finds a successful exploit chain.
- **Living Code**: Capable of self-mutation and adaptation to overcome obstacles.
- **Advanced Reconnaissance**: Utilizes tools like `nmap`, `tshark`, and `hydra` for network analysis and vulnerability scanning.
- **Privilege Escalation**: Employs a variety of techniques to gain root access.
- **Termux Native**: Optimized for deployment on Android 10+ via Termux.

### 📱 Legacy Android Rooting Framework
Production-grade Android 13 ARM64 tablet rooting system with:
- **Root Detection & Completion**: Multi-method detection and Magisk integration
- **Live Bot Framework**: Real-time error handling and adaptive recovery
- **GitHub Integration**: Live code updates and collaborative development
- **Comprehensive Logging**: Full audit trail with compliance features

### 🤖 AI Chatbot Mastery
Small custom AI assistants with Gradio_client and Streamlit:
- Multiple AI model interfaces (Qwen, Phi-3, OpenELM)
- Terminal and web-based chat interfaces
- Real-time streaming responses
- Conversation history management

## 📋 Quick Start

### Agentic Rooting System

```bash
# Clone the repository
git clone https://github.com/spiralgang/VARIABOT.git
cd VARIABOT

# Install dependencies
pip install -r requirements.txt

# Launch the Sriracha Army
python -m android_rooting.bots.sriracha_army
```

### AI Chatbots

Create a virtual environment and activate it:

```bash
pip install -r requirements.txt
```

**Terminal interface:**
```bash
python Qwen110BChat.py
```

**Web interface:**
```bash
streamlit run st-Qwen1.5-110B-Chat.py
```

## 🏗️ Project Structure

```
VARIABOT/
├── android_rooting/
│   ├── bots/
│   │   ├── sriracha_army.py      # Commander agent
│   │   ├── root_wheel_bot.py     # Soldier bot
│   │   └── utils.py              # Agent utilities
│   ├── core/
│   ├── scripts/
│   └── docs/
├── Qwen110BChat.py
├── st-*.py
├── requirements.txt
└── README.md
```

## 🔧 Android Rooting Features

### Core Capabilities
- **Multi-method Root Detection**: Binary, package, property, SELinux analysis
- **Magisk Integration**: Complete management and installation support
- **System Repair**: Automated partial root completion
- **Error Recovery**: Intelligent bot-driven error handling

### Bot Framework
- **Real-time Monitoring**: System health and process monitoring
- **Error Adaptation**: Live variable adaptation during root process
- **GitHub Integration**: Live code building and updates
- **Audit Trail**: Comprehensive logging and compliance

### Security & Compliance
- **Minimal Permissions**: Only necessary access requests
- **Secure Communications**: HTTPS for all network operations
- **Audit Logging**: Complete operational trail
- **Code Integrity**: SHA verification for updates

## 🤖 AI Chatbot Interfaces

### Chat interface with only terminal
<img src="https://github.com/fabiomatricardi/ChatBOTMastery/blob/main/chat-Qwen110Bchat002.gif" width=900>

### Chat interface with Streamlit
<img src="https://github.com/fabiomatricardi/ChatBOTMastery/raw/main/Qwen110BChat-streamlit.gif" width=900>

### Available Models
- **Qwen 1.5-110B-Chat**: Large language model interface
- **Qwen 1.5-MoE-A2.7B-Chat**: Mixture of experts model
- **Phi-3-Mini-128k**: Microsoft's compact model
- **OpenELM-3B**: Apple's efficient language model

### More options
<img src='https://github.com/fabiomatricardi/ChatBOTMastery/raw/main/images/showcase000.jpg' width=800>

## 📚 Documentation

### Project Organization
- **[Copilot Instructions](copilot_instructions.md)**: AI development guidelines
- **[Organization Instructions](organization_instructions.md)**: Repository structure and workflow
- **[Reference Vault](reference_vault/)**: Complete standards and guidelines

### Android Rooting
- **[Android Rooting Guide](android_rooting/docs/ANDROID_ROOTING_GUIDE.md)**: Complete setup and usage guide
- **[Linux Networking Commands](android_rooting/docs/LINUX_NETWORKING_COMMANDS_CHEATSHEET.md)**: Network security cheatsheet
- **[Framework README](android_rooting/README.md)**: Detailed framework documentation

### AI Chatbots
- **[Medium Article](link-to-article)**: Original chatbot tutorial
- **Model Documentation**: Individual model configuration guides

## 🛠️ Installation

### Prerequisites
- **For Agentic Rooting**: Termux on Android 10+, ARM64 device
- **For AI Chatbots**: Python 3.7+, pip, internet connection

### Android Rooting Setup
```bash
# Automated setup (recommended)
curl -sSL https://raw.githubusercontent.com/serverhustled-web/VARIABOT/main/android_rooting/scripts/termux_setup.sh | bash

# Manual setup
git clone https://github.com/serverhustled-web/VARIABOT.git
cd VARIABOT/android_rooting
./scripts/termux_setup.sh
```

### AI Chatbot Setup
```bash
# Clone repository
git clone https://github.com/serverhustled-web/VARIABOT.git
cd VARIABOT

# Install dependencies
pip install -r requirements.txt

# Configure HuggingFace tokens in the Python files
# Edit st-Qwen1.5-110B-Chat.py and update yourHFtoken
```

## 🚨 Usage Examples

### Agentic Rooting
```bash
# Launch the Sriracha Army
python -m android_rooting.bots.sriracha_army
```

### Legacy Android Rooting
```bash
# Check current root status
root-detect --json

# Start error monitoring bot
error-bot --daemon

# Complete rooting process
android-root --enable-bot

# Manage Magisk modules
magisk-manage modules list
```

### AI Chatbots
```bash
# Terminal chat
python Qwen110BChat.py

# Web interface
streamlit run st-Qwen1.5-110B-Chat.py

# Different models
streamlit run st-Phi3Mini-128k-Chat.py
streamlit run st-Openelm-3B.py
```

## 🔒 Security & Legal

### Android Rooting
⚠️ **Important Disclaimers:**
- Rooting may void device warranty
- Could expose security vulnerabilities
- May violate terms of service
- Use only on devices you own
- For educational/authorized testing only
- For detailed exploit payloads and rooting procedures, see the [Linux, Kali, and Android Standards](reference_vault/linux_kali_android.md) document in the reference vault.

### AI Chatbots
- Requires HuggingFace API tokens
- Conversations may be logged
- Follow platform usage policies
- Respect rate limits

## 🤝 Contributing

### Development
```bash
# Fork the repository
git clone https://github.com/serverhustled-web/VARIABOT.git

# Create feature branch
git checkout -b feature/new-feature

# Make changes and test
pytest android_rooting/tests/  # For rooting framework
python test_chatbots.py        # For AI interfaces

# Submit pull request
```

### Guidelines
- Follow existing code style
- Add tests for new features
- Update documentation
- Security review for rooting features
- Ensure Android 10+ compatibility

## 📊 Project Stats

| Component | Status | Tests | Coverage |
|-----------|---------|-------|----------|
| Agentic Rooting | 🚧 Experimental | ⚠️ None | 0% |
| Android Rooting | ✅ Production | ✅ | 85% |
| AI Chatbots | ✅ Stable | ⚠️ Partial | 60% |
| Documentation | ✅ Complete | N/A | N/A |
| Bot Framework | ✅ Active | ✅ | 80% |

## 🙏 Acknowledgments

### Android Rooting Framework
- **Magisk**: [topjohnwu/Magisk](https://github.com/topjohnwu/Magisk)
- **Android Security**: [AOSP Security](https://source.android.com/security/)
- **Kali Linux**: [Network Tools](https://www.kali.org/tools/)
- **Bot Frameworks**: [Awesome Bots](https://git.hackliberty.org/Awesome-Mirrors/awesome-bots)

### AI Chatbot Components
- **HuggingFace**: Model hosting and API
- **Gradio**: Client library for model interaction
- **Streamlit**: Web interface framework
- **Original Tutorial**: Medium article implementation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Multi-Purpose Framework** | **Production Ready** | **Android 10+ Compatible** | **AI-Powered**

## References
- Internal: /reference_vault/PRODUCTION_GRADE_STANDARDS.md
- Internal: /reference_vault/linux_kali_android.md
- Internal: /reference_vault/ORGANIZATION_STANDARDS.md
- External: Magisk Guide — https://topjohnwu.github.io/Magisk/install.html
- External: Kali NetHunter Guide — https://www.kali.org/docs/nethunter/installing-nethunter/
