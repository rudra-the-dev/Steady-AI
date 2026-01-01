import streamlit as st
import os
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

# Constants from Replit AI Integrations
AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")

# newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
MODEL = "gpt-5"

# Initialize OpenAI client
client = OpenAI(
    api_key=AI_INTEGRATIONS_OPENAI_API_KEY,
    base_url=AI_INTEGRATIONS_OPENAI_BASE_URL
)

def is_rate_limit_error(exception: BaseException) -> bool:
    error_msg = str(exception)
    return (
        "429" in error_msg
        or "RATELIMIT_EXCEEDED" in error_msg
        or "quota" in error_msg.lower()
        or "rate limit" in error_msg.lower()
        or (isinstance(exception, Exception) and hasattr(exception, "status_code") and getattr(exception, "status_code") == 429)
    )

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception(is_rate_limit_error),
    reraise=True
)
def get_ai_response(messages):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_completion_tokens=4096
        )
        content = response.choices[0].message.content
        return content if content is not None else ""
    except Exception as e:
        if "FREE_CLOUD_BUDGET_EXCEEDED" in str(e):
            st.error("Cloud budget exceeded. Please check your Replit account.")
            return "Error: Cloud budget exceeded."
        raise e

# Streamlit UI Configuration
st.set_page_config(page_title="AI Chat Assistant", page_icon="💬", layout="centered")

st.title("💬 AI Chat Assistant")
st.caption("A helpful assistant with memory of our conversation.")

# Initialize session state for memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful and friendly AI assistant. You remember the context of the conversation to provide better assistance."}
    ]

# Display chat history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to memory
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        full_response = get_ai_response(st.session_state.messages)
        
        message_placeholder.markdown(full_response)
    
    # Add assistant response to memory
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Sidebar options
with st.sidebar:
    st.title("Memory Management")
    if st.button("Clear Chat Memory"):
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful and friendly AI assistant. You remember the context of the conversation to provide better assistance."}
        ]
        st.rerun()
    
    st.divider()
    st.info("This assistant uses the latest GPT-5 model via Replit AI Integrations.")
