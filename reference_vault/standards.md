# Development and Documentation Standards

**Document Version:** 1.0.0  
**Last Updated:** 2024-09-21  
**Review Date:** 2024-12-21  
**Owner:** SpiralGang Development Team

## 📖 Overview

This document outlines the development and documentation standards for the VARIABOT project. These standards ensure code quality, maintainability, and consistency across all development activities.

## 🐍 Python Development Standards

### Code Style and Formatting

#### PEP 8 Compliance
All Python code must adhere to PEP 8 standards with the following tools:

```bash
# Code formatting
black --line-length 88 *.py

# Import sorting
isort --profile black *.py

# Linting
pylint --rcfile=.pylintrc *.py
flake8 --max-line-length=88 *.py
```

#### Configuration Files
```ini
# .pylintrc
[MASTER]
disable=C0114,C0115,C0116  # Docstring warnings handled separately

[FORMAT]
max-line-length=88

# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
multi_line_output = 3
```

### Type Annotations
All functions must include type hints:

```python
from typing import List, Dict, Optional, Union
import streamlit as st
from gradio_client import Client

def create_client(token: str, model_name: str) -> Client:
    """Create and return a Gradio client instance.
    
    Args:
        token: HuggingFace API token
        model_name: Name of the model to connect to
        
    Returns:
        Configured Gradio client instance
        
    Raises:
        ConnectionError: If unable to connect to the model
    """
    try:
        client = Client(model_name, hf_token=token)
        return client
    except Exception as e:
        raise ConnectionError(f"Failed to create client: {e}")
```

### Error Handling and Logging

#### Exception Handling
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def safe_model_call(client: Client, prompt: str) -> Optional[str]:
    """Safely call model with proper error handling."""
    try:
        response = client.submit(prompt, api_name="/chat")
        return response
    except ConnectionError as e:
        logger.error(f"Connection failed: {e}")
        return None
    except TimeoutError as e:
        logger.warning(f"Request timeout: {e}")
        return None
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        raise
```

#### Logging Configuration
```python
import logging
import sys

def setup_logging(level: str = "INFO") -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("variabot.log")
        ]
    )
```

### Documentation Standards

#### Docstring Format (Google Style)
```python
def process_chat_message(
    message: str, 
    model_type: str, 
    max_tokens: int = 800
) -> Dict[str, Union[str, int]]:
    """Process a chat message through the specified AI model.
    
    Args:
        message: User input message to process
        model_type: Type of AI model ('qwen', 'phi3', 'openelm')
        max_tokens: Maximum tokens for response generation
        
    Returns:
        Dictionary containing:
            - response: Generated response text
            - tokens_used: Number of tokens consumed
            - model: Model identifier used
            
    Raises:
        ValueError: If model_type is not supported
        RuntimeError: If model fails to generate response
        
    Example:
        >>> result = process_chat_message("Hello", "qwen")
        >>> print(result['response'])
        "Hello! How can I help you today?"
    """
    pass
```

## 🏗️ Project Structure Standards

### Directory Organization
```
VARIABOT/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── qwen.py
│   │   ├── phi3.py
│   │   └── openelm.py
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── streamlit_ui.py
│   │   └── terminal_ui.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── logging.py
│   └── utils/
│       ├── __init__.py
│       ├── validators.py
│       └── helpers.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docs/
├── reference_vault/
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── docker/
├── scripts/
├── .github/
└── configs/
```

### File Naming Conventions
- **Python modules:** lowercase with underscores (`model_interface.py`)
- **Classes:** PascalCase (`ModelInterface`)
- **Functions/variables:** snake_case (`create_client`)
- **Constants:** UPPER_SNAKE_CASE (`MAX_TOKENS`)
- **Config files:** lowercase with hyphens (`docker-compose.yml`)

## 🧪 Testing Standards

### Test Structure and Organization
```python
# tests/unit/test_qwen_model.py
import pytest
from unittest.mock import Mock, patch
from src.models.qwen import QwenModel

class TestQwenModel:
    """Test suite for QwenModel class."""
    
    @pytest.fixture
    def mock_client(self):
        """Provide mock Gradio client."""
        return Mock()
    
    @pytest.fixture
    def qwen_model(self, mock_client):
        """Provide QwenModel instance with mock client."""
        return QwenModel(client=mock_client)
    
    def test_model_initialization(self, qwen_model):
        """Test proper model initialization."""
        assert qwen_model.is_ready()
        assert qwen_model.model_name == "qwen"
    
    def test_generate_response_success(self, qwen_model, mock_client):
        """Test successful response generation."""
        mock_client.submit.return_value = "Test response"
        response = qwen_model.generate("Hello")
        assert response == "Test response"
        mock_client.submit.assert_called_once()
    
    @patch('src.models.qwen.logger')
    def test_generate_response_failure(self, mock_logger, qwen_model, mock_client):
        """Test response generation failure handling."""
        mock_client.submit.side_effect = Exception("API Error")
        response = qwen_model.generate("Hello")
        assert response is None
        mock_logger.error.assert_called_once()
```

### Test Coverage Requirements
- **Minimum Coverage:** 80% line coverage
- **Critical Paths:** 100% coverage for security and data handling
- **Integration Tests:** All API endpoints and UI interactions

### Testing Tools Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

## 📝 Documentation Standards

### README Structure
Every module and package must include a README.md with:

1. **Purpose and Overview**
2. **Installation Instructions**
3. **Usage Examples**
4. **API Reference**
5. **Contributing Guidelines**
6. **License Information**

### Code Comments
```python
# Good: Explain why, not what
def calculate_token_limit(model_type: str) -> int:
    # Different models have varying context windows
    # Qwen supports up to 128k tokens, while others are limited
    if model_type == "qwen":
        return 128000
    elif model_type == "phi3":
        return 128000
    else:
        return 4096  # Safe default for most models
```

### API Documentation
Use OpenAPI 3.0 specification for REST APIs:

```yaml
# docs/api.yaml
openapi: 3.0.0
info:
  title: VARIABOT API
  version: 1.0.0
  description: Multi-model chatbot interface API

paths:
  /chat:
    post:
      summary: Send chat message
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: User message
                model:
                  type: string
                  enum: [qwen, phi3, openelm]
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  response:
                    type: string
                  model_used:
                    type: string
```

## 🔧 Configuration Management

### Environment Configuration
```python
# src/config/settings.py
import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for AI model connections."""
    hf_token: str
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> 'ModelConfig':
        """Create config from environment variables."""
        token = os.getenv('HF_TOKEN')
        if not token:
            raise ValueError("HF_TOKEN environment variable required")
        
        return cls(
            hf_token=token,
            timeout=int(os.getenv('MODEL_TIMEOUT', '30')),
            max_retries=int(os.getenv('MODEL_RETRIES', '3'))
        )

@dataclass
class AppConfig:
    """Main application configuration."""
    debug: bool = False
    log_level: str = "INFO"
    model_config: ModelConfig = None
    
    @classmethod
    def load(cls) -> 'AppConfig':
        """Load configuration from environment."""
        return cls(
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO').upper(),
            model_config=ModelConfig.from_env()
        )
```

### Secrets Management
```python
# Never commit secrets to version control
# Use environment variables or secret management systems

# Good
hf_token = os.getenv('HF_TOKEN')

# Bad - Never do this
hf_token = "hf_xxxxxxxxxxxxxxxxxxxx"
```

## 🚀 Deployment Standards

### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txt

COPY src/ ./src/
COPY reference_vault/ ./reference_vault/

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "src/interfaces/streamlit_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Environment Files
```bash
# .env.example
HF_TOKEN=your_huggingface_token_here
DEBUG=false
LOG_LEVEL=INFO
MODEL_TIMEOUT=30
MODEL_RETRIES=3
```

## 📊 Code Quality Metrics

### Quality Gates
Before any code is merged:

1. **Linting:** All linting checks pass
2. **Type Checking:** mypy validation successful
3. **Tests:** All tests pass with >80% coverage
4. **Security:** No critical vulnerabilities detected
5. **Documentation:** All public APIs documented

### Automated Quality Checks
```yaml
# .github/workflows/quality.yml
name: Code Quality
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements/dev.txt
      
      - name: Lint with pylint
        run: pylint src/
      
      - name: Check formatting
        run: black --check src/
      
      - name: Type checking
        run: mypy src/
      
      - name: Security scan
        run: bandit -r src/
      
      - name: Run tests
        run: pytest --cov=src --cov-fail-under=80
```

## 🔄 Continuous Integration Standards

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        args: [--max-line-length=88]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
```

### Branch Protection Rules
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- Restrict pushes to main branch

## 📋 Code Review Standards

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] Breaking changes identified

### Review Process
1. **Self-Review:** Developer reviews own changes
2. **Peer Review:** At least one team member review
3. **Technical Review:** Senior developer approval for complex changes
4. **Security Review:** Security team review for sensitive changes

---

**Document Maintenance:**
- Update standards as technology evolves
- Regular review of effectiveness
- Community feedback incorporation
- Alignment with industry best practices