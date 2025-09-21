import streamlit as st
import time
import sys
from gradio_client import Client
# Internal usage
import os
from time import sleep

# Model configuration for CodeT5-Small (880MB - Under 1.5GB requirement)
if "hf_model" not in st.session_state:
    st.session_state.hf_model = "CodeT5-Small"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_resource
def create_client():   
    yourHFtoken = os.getenv('HF_TOKEN', '')  # Use environment variable for security
    print(f'Loading lightweight model: {st.session_state.hf_model} (880MB)')
    try:
        client = Client("Salesforce/codet5-small", hf_token=yourHFtoken)
        return client
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None

# FUNCTION TO LOG ALL CHAT MESSAGES INTO chathistory.txt
def writehistory(text):
    with open('chathistory_codet5.txt', 'a', encoding='utf-8') as f:
        f.write(text)
        f.write('\n')
    f.close()

#AVATARS
av_us = '🧑‍💻'  # Developer avatar
av_ass = "🤖"    # AI assistant avatar

### START STREAMLIT UI
st.set_page_config(
    page_title="VARIABOT - CodeT5-Small", 
    page_icon="🤖",
    layout="wide"
)

st.image('https://github.com/fabiomatricardi/ChatBOTMastery/raw/main/codet5logo.png', width=600)
st.markdown("### *CodeT5-Small: Lightweight Code Assistant (880MB)*", unsafe_allow_html=True)
st.markdown('---')

# Model information sidebar
with st.sidebar:
    st.markdown("### 🤖 Model Information")
    st.markdown(f"""
    **Model**: CodeT5-Small  
    **Size**: 880MB ✅ (Under 1.5GB)  
    **Parameters**: 220M  
    **Specialization**: Code Generation  
    **Memory Usage**: Low  
    **Speed**: Fast  
    
    **Capabilities**:
    - Python code generation
    - Code completion
    - Documentation generation
    - Bug fixing suggestions
    - Code explanation
    """)
    
    st.markdown("### 🔧 Settings")
    max_tokens = st.slider("Max Tokens", 50, 500, 150)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.1)

# Create client
client = create_client()

if client is None:
    st.error("⚠️ Model client failed to initialize. Please check your HuggingFace token.")
    st.stop()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message(message["role"], avatar=av_us):
            st.markdown(message["content"])
    else:
        with st.chat_message(message["role"], avatar=av_ass):
            st.markdown(message["content"])

# Accept user input
if myprompt := st.chat_input("Ask me to help with your code..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": myprompt})
    
    # Display user message in chat message container
    with st.chat_message("user", avatar=av_us):
        st.markdown(myprompt)
        usertext = f"user: {myprompt}"
        writehistory(usertext)
        
    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar=av_ass):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Show loading indicator for lightweight model
            with st.spinner("🧠 CodeT5-Small is thinking..."):
                res = client.submit(
                    myprompt,
                    max_length=max_tokens,
                    temperature=temperature,
                    api_name="/predict"
                )
            
            # Handle response
            if res:
                full_response = str(res)
                message_placeholder.markdown(full_response)
            else:
                full_response = "I apologize, but I couldn't generate a response. Please try again."
                message_placeholder.markdown(full_response)
                
        except Exception as e:
            full_response = f"Error: {str(e)}. The lightweight model may need a moment to initialize."
            message_placeholder.markdown(full_response)
        
        # Log assistant response
        asstext = f"assistant: {full_response}"
        writehistory(asstext)       
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer with model info
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
🤖 <strong>VARIABOT - CodeT5-Small</strong><br>
Lightweight AI Code Assistant (880MB) | Efficient & Fast<br>
<em>Optimized for resource-constrained environments</em>
</div>
""", unsafe_allow_html=True)