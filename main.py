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
        # Use a list comprehension to send only necessary fields to reduce payload size
        minimal_messages = [
            {"role": m["role"], "content": m["content"]} 
            for m in messages
        ]
        response = client.chat.completions.create(
            model=MODEL,
            messages=minimal_messages,
            max_completion_tokens=2048 # Reduced from 4096 to save bandwidth
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
        {"role": "system", "content": "You are a helpful and witty AI assistant with a sarcastic edge. While you provide great advice, you roast users for low-effort queries (like just saying 'hi'). Crucially, you are conversational: instead of giving long answers immediately to broad questions, ask follow-up questions to understand the user's specific context, code, or goals. For debugging, ask for their code and error. For career advice, ask about their current skills and interests."}
    ]

# Define prompt cards
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False

# Display chat history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Show beginner prompts only if chat hasn't started and no user messages yet
has_user_messages = any(msg["role"] == "user" for msg in st.session_state.messages)

if not st.session_state.chat_started and not has_user_messages:
    st.write("### Try one of these to get started:")
    cols = st.columns(3)
    
    prompts = [
        {"label": "🚀 Project Idea", "text": "I want to build a new AI-powered project but I'm looking for a unique direction. Can you help me brainstorm? Ask me about my interests or the tech I like first."},
        {"label": "💡 Career Advice", "text": "I'm looking to advance my career in software engineering. Before you give me advice, what details do you need about my background and goals?"},
        {"label": "🛠️ Code Debugging", "text": "I'm running into an error in my code and need help debugging it. I'm ready to share my code and the error message—what are we working on?"}
    ]
    
    for i, p in enumerate(prompts):
        with cols[i % 3]:
            if st.button(p["label"], key=f"btn_{i}", disabled=st.session_state.is_thinking):
                st.session_state.chat_started = True
                st.session_state.messages.append({"role": "user", "content": p["text"]})
                st.rerun()

# Chat input
if prompt := st.chat_input("How can I help you today?", disabled=st.session_state.is_thinking):
    st.session_state.chat_started = True
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Handle pending responses
if st.session_state.chat_started and len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    if not st.session_state.is_thinking:
        st.session_state.is_thinking = True
        st.rerun()
    else:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            try:
                full_response = get_ai_response(st.session_state.messages)
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                message_placeholder.error(f"Error: {str(e)}")
            finally:
                st.session_state.is_thinking = False
                st.rerun()

# Sidebar options
with st.sidebar:
    st.title("Settings")
    if st.button("🗑️ Clear Chat Memory"):
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful and witty AI assistant. While you are generally helpful, you have a sarcastic edge. If the user provides a low-effort message like 'hi', 'hello', or asks something trivial, feel free to roast them slightly by telling them to get to work or ask something more substantial. However, always remain useful if they ask a serious question."}
        ]
        st.session_state.chat_started = False
        st.session_state.is_thinking = False
        st.rerun()
    
    st.divider()
    st.info("This assistant uses the latest GPT-5 model via Replit AI Integrations.")
