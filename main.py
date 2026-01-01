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

# Custom CSS to match the card UI
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background-color: #F8F5F0;
    }
    
    /* Individual Card styling */
    .custom-card {
        background-color: #EFE9DE;
        border-radius: 15px;
        padding: 25px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        border: none;
        text-align: left;
    }
    
    .card-icon {
        font-size: 30px;
        text-align: right;
        margin-bottom: 10px;
    }
    
    .card-title {
        font-family: 'Serif', 'Georgia', serif;
        font-size: 18px;
        font-weight: 500;
        color: #2D3E33;
        line-height: 1.2;
    }
    
    /* Custom Banner Styling */
    .custom-banner {
        background: linear-gradient(135deg, #2D3E33 0%, #4A5D50 100%);
        color: #F8F5F0;
        border-radius: 20px;
        padding: 40px;
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .banner-text h1 {
        color: #F8F5F0 !important;
        font-family: 'Serif', 'Georgia', serif;
        font-size: 36px;
        margin: 0;
    }
    
    .banner-text p {
        color: #C2CDC5 !important;
        font-size: 18px;
        margin-top: 10px;
    }
    
    /* Clean up button styling */
    div.stButton > button {
        background-color: #EFE9DE !important;
        color: #2D3E33 !important;
        border-radius: 15px !important;
        padding: 0 !important;
        width: 100% !important;
        height: 200px !important;
        border: 2px solid #0066FF !important;
        transition: all 0.2s ease !important;
        position: relative !important;
        overflow: hidden !important;
        z-index: 1 !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-5px) !important;
        background-color: #E9E1D3 !important;
        box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3) !important;
    }

    /* Card overlay text styling - refined for visibility */
    .card-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        padding: 25px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        pointer-events: none;
        z-index: 2;
    }

    /* Target the button's focus/active state with blue boundary */
    div.stButton > button:focus, 
    div.stButton > button:active {
        border: 2px solid #0066FF !important;
        box-shadow: 0 0 0 2px rgba(0, 102, 255, 0.2) !important;
        outline: none !important;
    }
    
    /* Also show boundary on hover for clarity as a button */
    div.stButton > button:hover {
        transform: translateY(-5px) !important;
        background-color: #E9E1D3 !important;
        box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3) !important;
        border: 2px solid #0066FF !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("💬 AI Chat Assistant")
st.caption("A helpful assistant with memory of our conversation.")

# Initialize session state for memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a witty AI assistant that NEVER gives long explanations or answers upfront. Your goal is to be extremely interactive. For EVERY user request, you must ask 2-3 specific follow-up questions to understand their context before providing any real help. For example, if they ask about coding, ask for their language, what they've tried, and their specific error. If they ask for a project idea, ask for their interests and skill level first. Keep your initial responses very short and focused entirely on gathering information. Roast them briefly if they say something low-effort, but always end with a question."}
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
    # Custom Banner
    st.markdown("""
    <div class="custom-banner">
        <div class="banner-text">
            <h1>Hello, Friend</h1>
            <p>How can I help you move forward today?</p>
        </div>
        <div style="font-size: 60px; opacity: 0.8;">✨</div>
    </div>
    """, unsafe_allow_html=True)
    
    prompts = [
        {"label": "🚀 Project Idea", "icon": "🚀", "title": "Start a new project", "text": "I want ideas for a project, but don’t suggest anything yet.\nFirst, ask me a series of specific questions to understand my situation properly. Ask them step by step, not all at once.\nYour questions should cover:\nmy interests and problems I care about\nmy current skills and tools I know\nmy experience level (beginner/intermediate/advanced)\nhow much time I can realistically give\nwhether the project is for learning, competition, portfolio, business, or fun\nconstraints like budget, team size, device, or platform\nAfter I answer all the questions, analyze my responses and:\nsuggest 3–5 project ideas that actually fit me\nexplain why each idea is suitable\nmention the main challenges of each idea\nrecommend one best project to start with\noutline clear next steps to begin (tech stack, first milestone, etc.)\nAvoid generic ideas. Be practical, specific, and honest."},
        {"label": "💡 Career Advice", "icon": "💡", "title": "Level up your career", "text": "I want career guidance, but don’t give advice immediately.\nFirst, ask me a series of clear and specific questions to understand me properly. Ask them step by step, not all at once.\nYour questions should cover:\nwhat I’m interested in and enjoy doing\nwhat I’m good at and what skills I already have\nwhat I dislike or want to avoid\nwhat kind of work environment suits me\nmy education level and practical limitations\nmy long-term goals, income expectations, and lifestyle preferences\nAfter you finish asking questions and I answer them, analyze my responses honestly and:\nsuggest 3–5 realistic career options\nexplain why each option fits or doesn’t fit me\npoint out any contradictions or unrealistic assumptions in my thinking\nsuggest concrete next steps for the best options\nBe direct, practical, and honest. No motivational fluff."},
        {"label": "🛠️ Code Debugging", "icon": "🛠️", "title": "Fix some broken code", "text": "I need help debugging some code, but don’t jump to conclusions yet.\nFirst, ask me a sequence of focused questions to fully understand the problem. Ask them step by step, not all at once.\nYour questions should cover:\nthe programming language and environment\nwhat the code is supposed to do\nwhat it is actually doing\nexact error messages or unexpected behavior\nwhere and when the problem occurs\nwhat I’ve already tried\nAfter you have enough information and I answer, then:\nidentify the most likely root cause(s)\nexplain the bug in simple terms\nshow the corrected code\nexplain why the fix works\nsuggest how to prevent this type of bug in the future\nBe precise and technical. Don’t guess. Don’t oversimplify."}
    ]
    
    cols = st.columns(3)
    for i, p in enumerate(prompts):
        with cols[i]:
            # The button itself is the card background
            if st.button(" ", key=f"btn_{i}", disabled=st.session_state.is_thinking):
                st.session_state.chat_started = True
                st.session_state.messages.append({"role": "user", "content": p["text"]})
                st.rerun()
            
            # Use a div that sits perfectly over the button area
            st.markdown(f"""
            <div class="card-overlay" style="margin-top: -200px;">
                <div class="card-icon" style="margin: 0;">{p['icon']}</div>
                <div class="card-title" style="margin: 0;">{p['title']}</div>
            </div>
            """, unsafe_allow_html=True)

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
