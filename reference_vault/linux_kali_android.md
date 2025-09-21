# Linux, Kali, and Android Platform Deployment Guide

**Document Version:** 1.0.0  
**Last Updated:** 2024-09-21  
**Review Date:** 2024-12-21  
**Owner:** SpiralGang Development Team

## 📋 Overview

This document provides comprehensive deployment, configuration, and optimization guides for running VARIABOT on Linux distributions, Kali Linux, and Android platforms. Each platform has specific requirements, security considerations, and performance optimizations.

## 🐧 Linux Distribution Support

### Supported Linux Distributions

#### Production Tier (Fully Tested and Supported)
- **Ubuntu 20.04 LTS / 22.04 LTS**
  - Python 3.8+ native support
  - Streamlit compatible
  - Docker CE/EE supported
  - Enterprise security features

- **CentOS 8 / RHEL 8+**
  - Enterprise-grade stability
  - SELinux integration
  - Corporate firewall compatibility
  - Long-term support lifecycle

- **Debian 11 (Bullseye) / 12 (Bookworm)**
  - Lightweight and stable
  - Minimal attack surface
  - Excellent containerization support
  - Strong security posture

#### Development Tier (Community Tested)
- **Fedora 36+**
  - Cutting-edge packages
  - Latest Python versions
  - Good for development environments

- **openSUSE Leap 15.4+**
  - YaST configuration tools
  - Btrfs filesystem support
  - Stable rolling release model

- **Arch Linux**
  - Rolling release model
  - Latest software packages
  - Customizable installation

### Ubuntu Deployment Guide

#### Prerequisites Installation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install system dependencies
sudo apt install -y curl wget git build-essential

# Install optional monitoring tools
sudo apt install -y htop iotop nethogs
```

#### Virtual Environment Setup
```bash
# Create dedicated user for VARIABOT
sudo useradd -m -s /bin/bash variabot
sudo usermod -aG docker variabot  # If using Docker

# Switch to variabot user
sudo su - variabot

# Create virtual environment
python3 -m venv /home/variabot/venv
source /home/variabot/venv/bin/activate

# Upgrade pip and install requirements
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### Systemd Service Configuration
```ini
# /etc/systemd/system/variabot-qwen.service
[Unit]
Description=VARIABOT Qwen Model Interface
After=network.target
Wants=network.target

[Service]
Type=simple
User=variabot
Group=variabot
WorkingDirectory=/home/variabot/VARIABOT
Environment=PATH=/home/variabot/venv/bin
Environment=HF_TOKEN=your_huggingface_token_here
ExecStart=/home/variabot/venv/bin/streamlit run st-Qwen1.5-110B-Chat.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### Service Management Commands
```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable variabot-qwen.service
sudo systemctl start variabot-qwen.service

# Check service status
sudo systemctl status variabot-qwen.service

# View logs
sudo journalctl -u variabot-qwen.service -f

# Restart service
sudo systemctl restart variabot-qwen.service
```

#### Nginx Reverse Proxy Configuration
```nginx
# /etc/nginx/sites-available/variabot
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Proxy to Streamlit
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # WebSocket support for Streamlit
    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### Firewall Configuration (UFW)
```bash
# Basic firewall setup
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Streamlit (if direct access needed)
sudo ufw allow from 10.0.0.0/8 to any port 8501

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

### CentOS/RHEL Deployment Guide

#### Prerequisites Installation
```bash
# Update system packages
sudo dnf update -y

# Install EPEL repository
sudo dnf install -y epel-release

# Install Python and development tools
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y python3 python3-pip python3-devel

# Install additional dependencies
sudo dnf install -y curl wget git nginx
```

#### SELinux Configuration
```bash
# Check SELinux status
sestatus

# Allow Streamlit to bind to port 8501
sudo setsebool -P httpd_can_network_connect 1
sudo semanage port -a -t http_port_t -p tcp 8501

# Create SELinux policy for VARIABOT (if needed)
sudo sealert -a /var/log/audit/audit.log
```

#### Firewalld Configuration
```bash
# Check firewalld status
sudo firewall-cmd --state

# Add HTTP and HTTPS services
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# Add custom port for Streamlit (if needed)
sudo firewall-cmd --permanent --add-port=8501/tcp --zone=internal

# Reload firewall rules
sudo firewall-cmd --reload

# List active rules
sudo firewall-cmd --list-all
```

## 🔒 Kali Linux Deployment Guide

### Kali-Specific Considerations

#### Security-Focused Installation
```bash
# Update Kali packages
sudo apt update && sudo apt full-upgrade -y

# Install Python development environment
sudo apt install -y python3-pip python3-venv python3-dev

# Install penetration testing specific tools (if needed)
sudo apt install -y nmap wireshark tcpdump netcat-traditional

# Install Docker for containerized deployment
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

#### Enhanced Security Configuration
```bash
# Create isolated environment for VARIABOT
sudo useradd -m -s /bin/bash -G docker variabot

# Set up restricted permissions
sudo chmod 750 /home/variabot
sudo chown variabot:variabot /home/variabot

# Configure AppArmor profile (if available)
sudo aa-genprof /home/variabot/venv/bin/streamlit
```

#### Network Security Setup
```bash
# Configure iptables for strict access control
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

# Save iptables rules
sudo iptables-save > /etc/iptables/rules.v4
```

#### Tor Integration (Optional)
```bash
# Install Tor for enhanced privacy
sudo apt install -y tor

# Configure Tor for VARIABOT traffic
echo "SOCKSPort 9050" | sudo tee -a /etc/tor/torrc
echo "HTTPTunnelPort 8118" | sudo tee -a /etc/tor/torrc

# Start Tor service
sudo systemctl enable tor
sudo systemctl start tor

# Configure Python requests to use Tor
# Add to your Python code:
# proxies = {
#     'http': 'socks5://127.0.0.1:9050',
#     'https': 'socks5://127.0.0.1:9050'
# }
```

#### VPN Integration
```bash
# Install OpenVPN client
sudo apt install -y openvpn

# Example configuration for VPN usage
# /etc/openvpn/client.conf
echo "client
dev tun
proto udp
remote your-vpn-server.com 1194
resolv-retry infinite
nobind
persist-key
persist-tun
ca ca.crt
cert client.crt
key client.key
verb 3" | sudo tee /etc/openvpn/client.conf

# Start VPN connection
sudo systemctl enable openvpn@client
sudo systemctl start openvpn@client
```

### Kali Penetration Testing Integration

#### Network Analysis Tools
```bash
# Monitor VARIABOT network traffic
sudo tcpdump -i any -n port 8501

# Analyze API communication
sudo wireshark &

# Port scanning for security assessment
nmap -sV -sC localhost

# SSL/TLS analysis
sslscan your-domain.com
testssl.sh your-domain.com
```

#### Security Testing Scripts
```bash
#!/bin/bash
# security_test.sh - Basic security tests for VARIABOT

echo "Running VARIABOT Security Assessment..."

# Check for open ports
echo "=== Port Scan ==="
nmap -sT localhost

# Check SSL configuration
echo "=== SSL Analysis ==="
if command -v testssl.sh &> /dev/null; then
    testssl.sh localhost:443
fi

# Check for common vulnerabilities
echo "=== Web Vulnerability Scan ==="
if command -v nikto &> /dev/null; then
    nikto -h http://localhost:8501
fi

# Check Python dependencies for vulnerabilities
echo "=== Dependency Security Scan ==="
if command -v safety &> /dev/null; then
    safety check
fi

echo "Security assessment complete."
```

## 📱 Android Platform Support

### Android Deployment Options

#### Option 1: Termux Environment
```bash
# Install Termux from F-Droid or Google Play
# Update package repositories
pkg update && pkg upgrade

# Install Python and required packages
pkg install python python-pip git

# Install additional dependencies
pkg install clang make libjpeg-turbo libpng

# Clone VARIABOT repository
git clone https://github.com/spiralgang/VARIABOT.git
cd VARIABOT

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run VARIABOT
python st-Qwen1.5-110B-Chat.py
```

#### Option 2: Docker on Android (via UserLAnd)
```bash
# Install UserLAnd app from Google Play Store
# Set up Ubuntu environment in UserLAnd

# Install Docker
sudo apt update
sudo apt install -y docker.io

# Build VARIABOT container
docker build -t variabot .

# Run container
docker run -p 8501:8501 -e HF_TOKEN=$HF_TOKEN variabot
```

#### Option 3: Native Android App (Future Development)
```xml
<!-- Android manifest considerations for future native app -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    
    <application
        android:allowBackup="true"
        android:usesCleartextTraffic="false"
        android:networkSecurityConfig="@xml/network_security_config">
        
        <activity android:name=".MainActivity"
                  android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

### Android Performance Optimization

#### Memory Management
```python
# Android-specific memory optimization
import gc
import psutil

def optimize_for_android():
    """Optimize memory usage for Android devices."""
    # Limit memory usage
    max_memory_mb = 512  # Adjust based on device capabilities
    
    # Monitor memory usage
    process = psutil.Process()
    memory_info = process.memory_info()
    
    if memory_info.rss > max_memory_mb * 1024 * 1024:
        # Force garbage collection
        gc.collect()
        
        # Implement memory pressure handling
        logger.warning(f"High memory usage: {memory_info.rss / 1024 / 1024:.1f}MB")

def configure_for_mobile():
    """Configure application for mobile environment."""
    # Reduce concurrent connections
    import requests
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=5,  # Reduced from default
        pool_maxsize=10      # Reduced from default
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session
```

#### Battery Optimization
```python
# Battery-aware operation
import time
import threading

class BatteryAwareScheduler:
    """Schedule operations based on battery level and charging status."""
    
    def __init__(self):
        self.is_charging = self._check_charging_status()
        self.battery_level = self._get_battery_level()
    
    def _check_charging_status(self):
        """Check if device is charging (Android-specific)."""
        try:
            # This would require Android-specific implementation
            # For now, assume always charging in development
            return True
        except:
            return True
    
    def _get_battery_level(self):
        """Get current battery level (Android-specific)."""
        try:
            # This would require Android-specific implementation
            # For now, return 100% in development
            return 100
        except:
            return 100
    
    def should_process_request(self):
        """Determine if request should be processed based on battery."""
        if self.is_charging:
            return True
        
        if self.battery_level < 20:
            return False  # Skip non-essential processing
        
        return True
```

## 🔧 Platform-Specific Optimizations

### Linux System Tuning

#### Kernel Parameters
```bash
# /etc/sysctl.d/99-variabot.conf
# Network optimizations
net.core.rmem_max = 268435456
net.core.wmem_max = 268435456
net.ipv4.tcp_rmem = 4096 65536 268435456
net.ipv4.tcp_wmem = 4096 65536 268435456

# File system optimizations
fs.file-max = 65536
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# Apply changes
sudo sysctl -p /etc/sysctl.d/99-variabot.conf
```

#### CPU Scheduling
```bash
# Set CPU governor for performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Set process priority for VARIABOT
sudo renice -10 $(pgrep -f streamlit)

# Use taskset for CPU affinity (on multi-core systems)
taskset -c 0,1 streamlit run st-Qwen1.5-110B-Chat.py
```

#### Memory Management
```bash
# Configure huge pages for performance
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled

# Adjust OOM killer settings
echo -1000 | sudo tee /proc/$(pgrep -f streamlit)/oom_score_adj
```

### Container Optimizations

#### Multi-Stage Docker Build
```dockerfile
# Optimized Dockerfile for different platforms
ARG PLATFORM=linux/amd64
FROM --platform=$PLATFORM python:3.9-slim as builder

# Install build dependencies only in builder stage
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM --platform=$PLATFORM python:3.9-slim

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r variabot && useradd -r -g variabot variabot

# Set working directory and copy application
WORKDIR /app
COPY --chown=variabot:variabot . .

# Switch to non-root user
USER variabot

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "st-Qwen1.5-110B-Chat.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Platform-Specific Docker Compose
```yaml
# docker-compose.yml with platform-specific configurations
version: '3.8'

services:
  variabot:
    build:
      context: .
      platforms:
        - linux/amd64
        - linux/arm64
        - linux/arm/v7
    image: spiralgang/variabot:latest
    ports:
      - "8501:8501"
    environment:
      - HF_TOKEN=${HF_TOKEN}
    volumes:
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 📊 Monitoring and Logging

### System Monitoring Setup

#### Prometheus Node Exporter
```bash
# Install Node Exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
sudo cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/

# Create systemd service
sudo tee /etc/systemd/system/node_exporter.service << EOF
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter
```

#### Log Aggregation
```bash
# Install rsyslog for centralized logging
sudo apt install -y rsyslog

# Configure VARIABOT logging
sudo tee /etc/rsyslog.d/99-variabot.conf << EOF
# VARIABOT application logs
if \$programname startswith "variabot" then /var/log/variabot.log
& stop
EOF

# Restart rsyslog
sudo systemctl restart rsyslog
```

#### Logrotate Configuration
```bash
# /etc/logrotate.d/variabot
/var/log/variabot.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 syslog syslog
    postrotate
        systemctl reload rsyslog
    endscript
}
```

## 🚨 Troubleshooting Guide

### Common Issues and Solutions

#### Python Environment Issues
```bash
# Problem: ImportError or package conflicts
# Solution: Clean virtual environment recreation
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Problem: Permission denied errors
# Solution: Fix ownership and permissions
sudo chown -R variabot:variabot /home/variabot/VARIABOT
chmod +x /home/variabot/VARIABOT/*.py
```

#### Network Connectivity Issues
```bash
# Test HuggingFace API connectivity
curl -I https://huggingface.co/api/models

# Test DNS resolution
nslookup huggingface.co

# Check proxy settings (if applicable)
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Test from behind firewall
telnet huggingface.co 443
```

#### Performance Issues
```bash
# Check system resources
htop
iotop
nethogs

# Monitor Python process
strace -p $(pgrep -f streamlit)

# Check memory usage
cat /proc/meminfo
free -h

# Monitor network usage
ss -tulpn | grep :8501
```

#### Platform-Specific Troubleshooting

##### Ubuntu/Debian
```bash
# Check package dependencies
apt list --installed | grep python3
dpkg -l | grep streamlit

# Fix broken packages
sudo apt --fix-broken install
sudo dpkg --configure -a
```

##### CentOS/RHEL
```bash
# Check SELinux issues
sudo sealert -a /var/log/audit/audit.log

# Check package dependencies
rpm -qa | grep python3
dnf list installed | grep streamlit

# Fix SELinux contexts
sudo restorecon -R /home/variabot/VARIABOT
```

##### Kali Linux
```bash
# Check Kali-specific issues
apt list --upgradable
apt autoremove

# Verify security tools don't interfere
ps aux | grep -E "(snort|suricata|fail2ban)"
```

##### Android/Termux
```bash
# Check Termux-specific issues
pkg list-installed | grep python
termux-info

# Fix storage permissions
termux-setup-storage

# Check available space
df -h $PREFIX
```

---

**Platform Support Matrix:**

| Feature | Ubuntu | CentOS | Kali | Android |
|---------|--------|--------|------|---------|
| Production Ready | ✅ | ✅ | ⚠️ | ⚠️ |
| Container Support | ✅ | ✅ | ✅ | ⚠️ |
| Security Features | ✅ | ✅ | ✅ | ⚠️ |
| Performance Tuning | ✅ | ✅ | ✅ | ⚠️ |
| Monitoring Tools | ✅ | ✅ | ✅ | ❌ |

**Legend:** ✅ Full Support, ⚠️ Limited Support, ❌ Not Supported