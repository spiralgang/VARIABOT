# Networking and Deployment Cheatsheet

**Document Version:** 1.0.0  
**Last Updated:** 2024-09-21  
**Review Date:** 2024-12-21  
**Owner:** SpiralGang Development Team

## 📋 Overview

This document provides comprehensive networking configurations, deployment architectures, and operational procedures for the VARIABOT platform. It serves as a quick reference for infrastructure setup, troubleshooting, and optimization.

## 🏗️ System Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │────│   Web Servers   │────│  AI Model APIs  │
│   (nginx/HAProxy)│    │   (Streamlit)   │    │ (HuggingFace)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Monitoring    │    │   Application   │    │   API Gateway   │
│   (Prometheus)  │    │    Logs         │    │   (Rate Limit)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Network Topology
```
Internet
   │
   ▼
┌─────────────────┐
│ Reverse Proxy   │  (Port 80/443)
│ (SSL Termination)│
└─────────────────┘
   │
   ▼
┌─────────────────┐
│ Load Balancer   │  (Internal)
│ (Health Checks) │
└─────────────────┘
   │
   ├─────────────────┬─────────────────┐
   ▼                 ▼                 ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ App Server 1│ │ App Server 2│ │ App Server N│
│ (Port 8501) │ │ (Port 8501) │ │ (Port 8501) │
└─────────────┘ └─────────────┘ └─────────────┘
```

## 🐳 Docker Deployment

### Production Dockerfile
```dockerfile
# Multi-stage build for production
FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txt

# Production stage
FROM python:3.9-slim

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r variabot && useradd -r -g variabot variabot

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=variabot:variabot src/ ./src/
COPY --chown=variabot:variabot reference_vault/ ./reference_vault/

# Switch to non-root user
USER variabot

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "src/st-Qwen1.5-110B-Chat.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  variabot-qwen:
    build:
      context: .
      dockerfile: docker/Dockerfile.qwen
    ports:
      - "8501:8501"
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    networks:
      - variabot-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  variabot-phi3:
    build:
      context: .
      dockerfile: docker/Dockerfile.phi3
    ports:
      - "8502:8501"
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    networks:
      - variabot-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - variabot-qwen
      - variabot-phi3
    networks:
      - variabot-network
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    networks:
      - variabot-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana
    networks:
      - variabot-network
    restart: unless-stopped

networks:
  variabot-network:
    driver: bridge

volumes:
  grafana-storage:
```

## ☸️ Kubernetes Deployment

### Namespace Configuration
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: variabot
  labels:
    name: variabot
    environment: production
```

### Deployment Configuration
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: variabot-qwen
  namespace: variabot
  labels:
    app: variabot-qwen
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: variabot-qwen
  template:
    metadata:
      labels:
        app: variabot-qwen
        version: v1.0.0
    spec:
      containers:
      - name: variabot-qwen
        image: spiralgang/variabot-qwen:1.0.0
        ports:
        - containerPort: 8501
          name: http
        env:
        - name: HF_TOKEN
          valueFrom:
            secretKeyRef:
              name: variabot-secrets
              key: hf-token
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 5
          periodSeconds: 10
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
```

### Service Configuration
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: variabot-qwen-service
  namespace: variabot
  labels:
    app: variabot-qwen
spec:
  selector:
    app: variabot-qwen
  ports:
  - name: http
    port: 80
    targetPort: 8501
    protocol: TCP
  type: ClusterIP
```

### Ingress Configuration
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: variabot-ingress
  namespace: variabot
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - variabot.example.com
    secretName: variabot-tls
  rules:
  - host: variabot.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: variabot-qwen-service
            port:
              number: 80
```

### Secrets Management
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: variabot-secrets
  namespace: variabot
type: Opaque
data:
  hf-token: <base64-encoded-huggingface-token>
```

## 🔧 Nginx Configuration

### Production Nginx Config
```nginx
# nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private must-revalidate pre-check=0 post-check=0;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/json
        application/xml+rss;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # Upstream servers
    upstream variabot_qwen {
        least_conn;
        server variabot-qwen:8501 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream variabot_phi3 {
        least_conn;
        server variabot-phi3:8501 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Main server block
    server {
        listen 80;
        server_name variabot.example.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name variabot.example.com;

        ssl_certificate /etc/nginx/ssl/variabot.crt;
        ssl_certificate_key /etc/nginx/ssl/variabot.key;

        # Security headers
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss:";

        # Rate limiting
        limit_req zone=api burst=20 nodelay;

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Qwen model interface
        location /qwen/ {
            rewrite ^/qwen/(.*) /$1 break;
            proxy_pass http://variabot_qwen;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # Phi3 model interface
        location /phi3/ {
            rewrite ^/phi3/(.*) /$1 break;
            proxy_pass http://variabot_phi3;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # Default to Qwen
        location / {
            proxy_pass http://variabot_qwen;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # Static files caching
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Security.txt
        location /.well-known/security.txt {
            return 200 "Contact: security@example.com\nExpires: 2025-12-31T23:59:59.000Z\n";
            add_header Content-Type text/plain;
        }
    }
}
```

## 📊 Monitoring and Observability

### Prometheus Configuration
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'variabot-qwen'
    static_configs:
      - targets: ['variabot-qwen:8501']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Alert Rules
```yaml
# monitoring/alert_rules.yml
groups:
- name: variabot.rules
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} for {{ $labels.instance }}"

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }}s for {{ $labels.instance }}"

  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service is down"
      description: "{{ $labels.instance }} has been down for more than 1 minute"

  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage"
      description: "Memory usage is {{ $value | humanizePercentage }} on {{ $labels.instance }}"

  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage"
      description: "CPU usage is {{ $value }}% on {{ $labels.instance }}"
```

### Grafana Dashboard Configuration
```json
{
  "dashboard": {
    "id": null,
    "title": "VARIABOT Monitoring",
    "tags": ["variabot", "monitoring"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{ instance }}"
          }
        ]
      },
      {
        "id": 2,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

## 🔐 Security Configuration

### SSL/TLS Setup
```bash
# Generate SSL certificate with Let's Encrypt
certbot certonly --webroot \
  --webroot-path=/var/www/html \
  --email admin@example.com \
  --agree-tos \
  --no-eff-email \
  -d variabot.example.com

# Set up automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

### Firewall Rules (UFW)
```bash
# Basic firewall setup
ufw default deny incoming
ufw default allow outgoing

# Allow SSH
ufw allow ssh

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow monitoring (internal only)
ufw allow from 10.0.0.0/8 to any port 9090
ufw allow from 10.0.0.0/8 to any port 3000

# Enable firewall
ufw enable
```

### Security Headers
```nginx
# Additional security headers in nginx
add_header Referrer-Policy "strict-origin-when-cross-origin";
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()";
add_header Cross-Origin-Embedder-Policy "require-corp";
add_header Cross-Origin-Opener-Policy "same-origin";
add_header Cross-Origin-Resource-Policy "same-origin";
```

## 🌐 Network Troubleshooting

### Common Network Issues

#### Connection Timeouts
```bash
# Test connectivity to HuggingFace API
curl -I https://huggingface.co/api/models
curl -w "@curl-format.txt" -o /dev/null -s https://api-inference.huggingface.co/models/Qwen/Qwen1.5-110B-Chat

# Check DNS resolution
nslookup huggingface.co
dig huggingface.co

# Test from within container
docker exec -it variabot-qwen curl -I https://huggingface.co/
```

#### Port Connectivity
```bash
# Check if ports are listening
netstat -tlnp | grep :8501
ss -tlnp | grep :8501

# Test port connectivity
telnet localhost 8501
nc -zv localhost 8501

# Check Docker network
docker network ls
docker network inspect variabot-network
```

#### Performance Analysis
```bash
# Network latency testing
ping -c 10 huggingface.co
traceroute huggingface.co
mtr --report huggingface.co

# Bandwidth testing
iperf3 -c huggingface.co -p 443 -t 30

# HTTP performance testing
ab -n 1000 -c 10 https://variabot.example.com/
wrk -t4 -c100 -d30s https://variabot.example.com/
```

### Network Optimization

#### TCP Tuning
```bash
# Optimize TCP settings for high-performance networking
echo 'net.core.rmem_max = 268435456' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 268435456' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem = 4096 65536 268435456' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem = 4096 65536 268435456' >> /etc/sysctl.conf
echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf
sysctl -p
```

#### Connection Pooling
```python
# Optimize HTTP connection pooling in Python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(
    pool_connections=100,
    pool_maxsize=100,
    max_retries=retry_strategy
)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

## 📈 Performance Optimization

### Resource Limits
```yaml
# Kubernetes resource optimization
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Caching Strategy
```nginx
# Nginx caching configuration
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=variabot_cache:10m max_size=1g inactive=60m use_temp_path=off;

location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    proxy_cache variabot_cache;
    proxy_cache_valid 200 1h;
    proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
    add_header X-Cache-Status $upstream_cache_status;
}
```

### Database Connection Optimization
```python
# Database connection pooling (if using database)
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## 🚨 Disaster Recovery

### Backup Procedures
```bash
# Database backup
pg_dump -h localhost -U username -d variabot > backup_$(date +%Y%m%d_%H%M%S).sql

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  /etc/nginx/ \
  /etc/ssl/ \
  /opt/variabot/config/

# Docker image backup
docker save spiralgang/variabot-qwen:1.0.0 | gzip > variabot-qwen-1.0.0.tar.gz
```

### Recovery Procedures
```bash
# Service restoration
kubectl rollout restart deployment/variabot-qwen -n variabot

# Database restoration
psql -h localhost -U username -d variabot < backup_20241201_120000.sql

# Configuration restoration
tar -xzf config_backup_20241201.tar.gz -C /
systemctl reload nginx
```

---

**Quick Reference Commands:**

```bash
# Status checks
kubectl get pods -n variabot
docker-compose ps
systemctl status nginx

# Logs
kubectl logs -f deployment/variabot-qwen -n variabot
docker-compose logs -f variabot-qwen
tail -f /var/log/nginx/access.log

# Scaling
kubectl scale deployment variabot-qwen --replicas=5 -n variabot
docker-compose up --scale variabot-qwen=3
```