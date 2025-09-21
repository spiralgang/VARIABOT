# Small AI Models Under 1.5GB for VARIABOT

**Document Version:** 1.0.0  
**Last Updated:** 2024-09-21  
**Purpose:** Identify and integrate lightweight AI models under 1.5GB for efficient deployment

## 🎯 Size Requirement: Under 1.5GB

### Current Models Analysis

**CURRENT MODELS (TOO LARGE):**
- ❌ Qwen1.5-110B-Chat: ~220GB (110 billion parameters)
- ❌ Phi-3-mini-128k: ~7.4GB (3.8 billion parameters) 
- ❌ OpenELM-3B: ~6GB (3 billion parameters)
- ❌ Qwen1.5-MoE-A2.7B: ~5.4GB (mixture of experts)

## 🔍 Recommended Small Models Under 1.5GB

### 1. Code-Specialized Models

#### Microsoft CodeT5-small (220M parameters, ~880MB)
```python
# HuggingFace: Salesforce/codet5-small
# Size: ~880MB
# Specialization: Code generation, completion, documentation
# Use case: Python code generation and assistance
model_config = {
    "name": "codet5-small",
    "hf_model": "Salesforce/codet5-small", 
    "size_mb": 880,
    "parameters": "220M",
    "specialization": "code_generation"
}
```

#### CodeGen-350M-multi (350M parameters, ~1.4GB)
```python
# HuggingFace: Salesforce/codegen-350M-multi
# Size: ~1.4GB
# Specialization: Multi-language code generation
# Use case: Code completion and generation
model_config = {
    "name": "codegen-350M-multi",
    "hf_model": "Salesforce/codegen-350M-multi",
    "size_mb": 1400,
    "parameters": "350M", 
    "specialization": "multilingual_code"
}
```

#### StarCoder-1B (1B parameters, ~1.2GB)
```python
# HuggingFace: bigcode/starcoder-1b
# Size: ~1.2GB  
# Specialization: Code completion and generation
# Use case: Advanced code assistance
model_config = {
    "name": "starcoder-1b",
    "hf_model": "bigcode/starcoder-1b",
    "size_mb": 1200,
    "parameters": "1B",
    "specialization": "code_completion"
}
```

### 2. General Chat Models Under 1.5GB

#### DistilBERT-base (66M parameters, ~250MB)
```python
# HuggingFace: distilbert-base-uncased
# Size: ~250MB
# Specialization: Natural language understanding
# Use case: Basic chat and Q&A
model_config = {
    "name": "distilbert-base",
    "hf_model": "distilbert-base-uncased",
    "size_mb": 250,
    "parameters": "66M",
    "specialization": "chat_basic"
}
```

#### TinyLlama-1.1B (1.1B parameters, ~1.1GB)
```python
# HuggingFace: TinyLlama/TinyLlama-1.1B-Chat-v1.0
# Size: ~1.1GB
# Specialization: Efficient chat model
# Use case: Conversational AI with low resource usage
model_config = {
    "name": "tinyllama-1.1b",
    "hf_model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "size_mb": 1100,
    "parameters": "1.1B",
    "specialization": "efficient_chat"
}
```

#### Phi-2 (2.7B parameters, ~1.4GB with quantization)
```python
# HuggingFace: microsoft/phi-2
# Size: ~1.4GB (with 8-bit quantization)
# Specialization: High-quality small model
# Use case: Advanced reasoning and code
model_config = {
    "name": "phi-2-quantized",
    "hf_model": "microsoft/phi-2",
    "size_mb": 1400,
    "parameters": "2.7B",
    "specialization": "reasoning_code",
    "quantization": "8bit"
}
```

## 🚀 Implementation Strategy

### Phase 1: Replace Large Models
```python
# Updated model configurations for VARIABOT
SMALL_MODEL_CONFIGS = {
    "code_assistant": {
        "primary": "Salesforce/codet5-small",
        "fallback": "Salesforce/codegen-350M-multi", 
        "size_limit_mb": 1500
    },
    "chat_assistant": {
        "primary": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "fallback": "distilbert-base-uncased",
        "size_limit_mb": 1500  
    },
    "code_completion": {
        "primary": "bigcode/starcoder-1b",
        "fallback": "Salesforce/codet5-small",
        "size_limit_mb": 1500
    }
}
```

### Phase 2: Model Selection Logic
```python
def select_optimal_model(task_type: str, max_size_mb: int = 1500) -> str:
    """
    Select optimal model based on task and size constraints.
    
    Args:
        task_type: Type of task ('code', 'chat', 'completion')
        max_size_mb: Maximum model size in MB
        
    Returns:
        HuggingFace model identifier
    """
    model_options = {
        'code': [
            ('Salesforce/codet5-small', 880),
            ('Salesforce/codegen-350M-multi', 1400),
            ('bigcode/starcoder-1b', 1200)
        ],
        'chat': [
            ('distilbert-base-uncased', 250),
            ('TinyLlama/TinyLlama-1.1B-Chat-v1.0', 1100),
            ('microsoft/phi-2', 1400)  # with quantization
        ],
        'completion': [
            ('Salesforce/codet5-small', 880),
            ('bigcode/starcoder-1b', 1200),
            ('Salesforce/codegen-350M-multi', 1400)
        ]
    }
    
    for model_name, size_mb in model_options.get(task_type, []):
        if size_mb <= max_size_mb:
            return model_name
    
    # Fallback to smallest available
    return 'distilbert-base-uncased'
```

### Phase 3: Updated Streamlit Interfaces
```python
# st-codet5-small.py - New lightweight code assistant
import streamlit as st
from gradio_client import Client

if "hf_model" not in st.session_state:
    st.session_state.hf_model = "CodeT5-Small"

@st.cache_resource  
def create_client():
    yourHFtoken = os.getenv('HF_TOKEN', '')
    print(f'Loading lightweight model: {st.session_state.hf_model}')
    client = Client("Salesforce/codet5-small", hf_token=yourHFtoken)
    return client

# Model info display
st.sidebar.markdown("""
### Model Info
- **Name**: CodeT5-Small
- **Size**: ~880MB ✅
- **Parameters**: 220M
- **Specialization**: Code generation
- **Memory Usage**: Low
""")
```

## 📊 Performance Comparison

| Model | Size | Parameters | Use Case | Memory | Speed |
|-------|------|------------|----------|---------|-------|
| **Current Models** | | | | | |
| Qwen1.5-110B | 220GB | 110B | ❌ Too Large | Very High | Slow |
| Phi-3-mini | 7.4GB | 3.8B | ❌ Too Large | High | Medium |
| **Recommended Models** | | | | | |
| CodeT5-Small | 880MB | 220M | ✅ Code Gen | Low | Fast |
| TinyLlama-1.1B | 1.1GB | 1.1B | ✅ Chat | Medium | Fast |
| StarCoder-1B | 1.2GB | 1B | ✅ Code Complete | Medium | Fast |
| Phi-2 (8bit) | 1.4GB | 2.7B | ✅ Advanced | Medium | Medium |

## 🔧 Migration Implementation

### Step 1: Create New Model Interfaces
```bash
# Create new lightweight model files
cp st-Qwen1.5-110B-Chat.py st-codet5-small.py
cp st-Phi3Mini-128k-Chat.py st-tinyllama-chat.py
cp st-Openelm-3B.py st-starcoder-1b.py
```

### Step 2: Update Model References
```python
# Replace large model references with small models
MIGRATION_MAP = {
    "Qwen/Qwen1.5-110B-Chat-demo": "Salesforce/codet5-small",
    "eswardivi/Phi-3-mini-128k-instruct": "TinyLlama/TinyLlama-1.1B-Chat-v1.0", 
    "Norod78/OpenELM_3B_Demo": "bigcode/starcoder-1b",
    "Qwen/qwen1.5-MoE-A2.7B-Chat-demo": "microsoft/phi-2"
}
```

### Step 3: Performance Optimization
```python
# Enable model quantization for further size reduction
def setup_quantized_model(model_name: str):
    """Setup model with quantization for memory efficiency."""
    return Client(
        model_name, 
        hf_token=os.getenv('HF_TOKEN'),
        # Enable quantization options
        model_kwargs={
            "load_in_8bit": True,
            "device_map": "auto"
        }
    )
```

## 📋 Kaggle and HuggingFace Research

### Top Small Models from Research

#### From Kaggle Competitions:
1. **Efficient-Net Models** (< 100MB) - Image tasks
2. **DistilBERT variants** (250MB-500MB) - NLP tasks  
3. **MobileBERT** (100MB) - Mobile deployment
4. **TinyBERT** (60MB) - Ultra-lightweight NLP

#### From HuggingFace Trending:
1. **TinyLlama series** (1.1GB) - Chat models
2. **CodeT5 series** (220M-770M) - Code models
3. **DistilGPT2** (350MB) - Text generation
4. **BERT-tiny** (17MB) - Classification tasks

### Model Selection Criteria:
- ✅ Size under 1.5GB
- ✅ Active maintenance
- ✅ Good performance metrics
- ✅ Commercial usage allowed
- ✅ Python/Streamlit compatible

## 🎯 Recommended Action Plan

1. **Immediate**: Replace Qwen1.5-110B with CodeT5-Small (880MB)
2. **Phase 2**: Replace Phi-3-mini with TinyLlama-1.1B (1.1GB)  
3. **Phase 3**: Replace OpenELM with StarCoder-1B (1.2GB)
4. **Phase 4**: Add quantized Phi-2 as premium option (1.4GB)

This will reduce total model size from ~240GB to under 5GB while maintaining functionality.