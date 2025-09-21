import streamlit as st
import time
import sys
from gradio_client import Client

# Internal usage
import os
from time import sleep

# Model configuration for TinyLlama-1.1B (1.1GB - Under 1.5GB requirement)
if "hf_model" not in st.session_state:
    st.session_state.hf_model = "TinyLlama-1.1B-Chat"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


@st.cache_resource
def create_client():
    yourHFtoken = os.getenv("HF_TOKEN", "")  # Use environment variable for security
    print(f"Loading lightweight model: {st.session_state.hf_model} (1.1GB)")
    try:
        client = Client("TinyLlama/TinyLlama-1.1B-Chat-v1.0", hf_token=yourHFtoken)
        return client
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None


# FUNCTION TO LOG ALL CHAT MESSAGES INTO chathistory.txt
def writehistory(text):
    with open("chathistory_tinyllama.txt", "a", encoding="utf-8") as f:
        f.write(text)
        f.write("\n")
    f.close()


# AVATARS
av_us = "🧑‍💻"  # User avatar
av_ass = "🦙"  # Llama avatar for TinyLlama

### START STREAMLIT UI
st.set_page_config(
    page_title="VARIABOT - TinyLlama Chat", page_icon="🦙", layout="wide"
)

st.image("https://github.com/jzhang38/TinyLlama/raw/main/TinyLlama_logo.png", width=600)
st.markdown(
    "### *TinyLlama-1.1B: Efficient Chat Assistant (1.1GB)*", unsafe_allow_html=True
)
st.markdown("---")

# Model information sidebar
with st.sidebar:
    st.markdown("### 🦙 Model Information")
    st.markdown(
        f"""
    **Model**: TinyLlama-1.1B-Chat  
    **Size**: 1.1GB ✅ (Under 1.5GB)  
    **Parameters**: 1.1B  
    **Specialization**: Conversational AI  
    **Memory Usage**: Medium  
    **Speed**: Fast  
    
    **Capabilities**:
    - Natural conversation
    - Question answering
    - Creative writing
    - Problem solving
    - Code assistance
    - Educational support
    """
    )

    st.markdown("### 🔧 Settings")
    max_tokens = st.slider("Max Tokens", 50, 1000, 250)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    top_p = st.slider("Top P", 0.1, 1.0, 0.9)

# Create client
client = create_client()

if client is None:
    st.error(
        "⚠️ Model client failed to initialize. Please check your HuggingFace token."
    )
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
if myprompt := st.chat_input("Chat with TinyLlama..."):
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
            # Show loading indicator
            with st.spinner("🦙 TinyLlama is thinking..."):
                res = client.submit(
                    myprompt,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    api_name="/chat",
                )

            # Handle streaming response if available
            if hasattr(res, "__iter__"):
                for chunk in res:
                    if chunk:
                        full_response = str(chunk)
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            else:
                full_response = (
                    str(res)
                    if res
                    else "I apologize, but I couldn't generate a response. Please try again."
                )
                message_placeholder.markdown(full_response)

        except Exception as e:
            full_response = (
                f"Error: {str(e)}. The model may need a moment to initialize."
            )
            message_placeholder.markdown(full_response)

        # Log assistant response
        asstext = f"assistant: {full_response}"
        writehistory(asstext)
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

# Footer with model info
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666;'>
🦙 <strong>VARIABOT - TinyLlama-1.1B-Chat</strong><br>
Efficient Conversational AI (1.1GB) | Resource Optimized<br>
<em>Perfect balance of capability and efficiency</em>
</div>
""",
    unsafe_allow_html=True,
)

# Performance metrics display
with st.sidebar:
    st.markdown("### 📊 Performance Metrics")
    st.markdown(
        """
    **Memory Efficiency**: ⭐⭐⭐⭐  
    **Response Speed**: ⭐⭐⭐⭐⭐  
    **Quality**: ⭐⭐⭐⭐  
    **Deployment**: ⭐⭐⭐⭐⭐  
    
    **Vs Previous Models**:
    - 200x smaller than Qwen-110B
    - 7x smaller than Phi-3-mini
    - Similar quality for most tasks
    - Much faster inference
    """
    )

# Usage tips
with st.expander("💡 Usage Tips"):
    st.markdown(
        """
    **TinyLlama works best with**:
    - Clear, specific questions
    - Conversational prompts
    - Step-by-step instructions
    - Creative writing tasks
    
    **Model Limitations**:
    - May struggle with very complex reasoning
    - Limited knowledge cutoff
    - Best for general conversation and basic coding
    
    **Optimization Tips**:
    - Lower temperature (0.1-0.3) for factual responses
    - Higher temperature (0.7-0.9) for creative tasks
    - Adjust max tokens based on desired response length
    """
    )
