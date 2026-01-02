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
            max_completion_tokens=2048
        )
        content = response.choices[0].message.content
        return content if content is not None else ""
    except Exception as e:
        if "FREE_CLOUD_BUDGET_EXCEEDED" in str(e):
            st.error("Cloud budget exceeded. Please check your Replit account.")
            return "Error: Cloud budget exceeded."
        raise e

st.set_page_config(page_title="AI Chat Assistant", page_icon="💬", layout="centered")

# Custom Styling and Logic from Reference
st.markdown("""
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    .stApp { background-color: #f5f1e8; }
    .container { width: 100%; max-width: 1200px; margin: 0 auto; }
    .cards-wrapper { position: relative; overflow: hidden; margin-bottom: 30px; }
    .cards-container { display: flex; gap: 20px; transition: transform 0.3s ease-out; }
    
    .card {
        background: #f9f6f0;
        border-radius: 16px;
        padding: 40px 30px;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid #0066FF !important;
        position: relative;
        text-align: left;
        overflow: hidden;
        width: 100%;
        user-select: none;
        -webkit-user-select: none;
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border-color: #0066FF;
    }

    .icon {
        position: absolute;
        top: 20px;
        right: 20px;
        font-size: 48px;
        line-height: 1;
        pointer-events: none;
        z-index: 2;
        transition: transform 0.3s ease;
    }

    .card:hover .icon {
        transform: scale(1.1);
    }

    .card-title {
        position: absolute;
        bottom: 20px;
        left: 20px;
        font-size: 24px;
        font-weight: 500;
        color: #4a4a4a;
        line-height: 1.4;
        margin: 0;
        max-width: 85%;
        pointer-events: none;
        z-index: 2;
        font-family: inherit;
    }

    @media (min-width: 769px) {
        .cards-container { display: grid; grid-template-columns: repeat(3, 1fr); }
        .card { flex: none; width: 100%; }
        .dots { display: none; }
    }

    @media (max-width: 768px) {
        .cards-wrapper { padding: 0 20px; }
        .cards-container { gap: 20px; padding: 0; }
        .card { flex: 0 0 calc(100vw - 40px); }
        .dots { display: flex; justify-content: center; gap: 8px; margin-top: 20px; }
        .dot { width: 8px; height: 8px; border-radius: 50%; background-color: #d4cfc4; transition: all 0.3s ease; cursor: pointer; }
        .dot.active { background-color: #8b7f6f; width: 24px; border-radius: 4px; }
    }

    /* Invisible Streamlit Buttons */
    div.stButton {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 5 !important;
    }
    div.stButton > button {
        background: transparent !important;
        border: none !important;
        width: 100% !important;
        height: 100% !important;
        color: transparent !important;
        box-shadow: none !important;
        display: block !important;
    }
    div.stButton > button:hover, 
    div.stButton > button:active, 
    div.stButton > button:focus {
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .custom-banner {
        background: linear-gradient(135deg, #2D3E33 0%, #4A5D50 100%);
        color: #F8F5F0;
        border-radius: 20px;
        padding: 40px;
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</style>

<script>
    function goToSlide(index) {
        if (window.innerWidth <= 768) {
            const cardsContainer = window.parent.document.querySelector('.cards-container');
            if (cardsContainer) {
                const cardWidth = cardsContainer.querySelector('.card').offsetWidth;
                const gap = 20;
                const offset = -(index * (cardWidth + gap));
                cardsContainer.style.transform = `translateX(${offset}px)`;
                const dots = window.parent.document.querySelectorAll('.dot');
                dots.forEach((dot, i) => dot.classList.toggle('active', i === index));
            }
        }
    }
    
    document.addEventListener('DOMContentLoaded', () => {
        const container = window.parent.document.querySelector('.cards-wrapper');
        if (container) {
            let startX = 0;
            let currentSlide = 0;
            container.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; });
            container.addEventListener('touchend', (e) => {
                const endX = e.changedTouches[0].clientX;
                const diff = startX - endX;
                if (Math.abs(diff) > 50) {
                    if (diff > 0 && currentSlide < 2) currentSlide++;
                    else if (diff < 0 && currentSlide > 0) currentSlide--;
                    goToSlide(currentSlide);
                }
            });
        }
    });
</script>
""", unsafe_allow_html=True)

st.title("💬 AI Chat Assistant")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a witty AI assistant. For EVERY request, ask 2-3 specific follow-up questions first. Roast them briefly for low-effort messages."}
    ]
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False
if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False

# Display history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Beginner prompts
if not st.session_state.chat_started and not any(m["role"] == "user" for m in st.session_state.messages):
    st.markdown("""
    <div class="custom-banner">
        <div class="banner-text">
            <h1 style="color:white; margin:0;">Hello, Friend</h1>
            <p style="color:#C2CDC5;">How can I help you move forward today?</p>
        </div>
        <div style="font-size: 60px; opacity: 0.8;">✨</div>
    </div>
    """, unsafe_allow_html=True)
    
    prompts = [
        {"icon": "🚀", "title": "Project Idea", "text": "I want ideas for a project, but don’t suggest anything yet.\nFirst, ask me a series of specific questions to understand my situation properly. Ask them step by step, not all at once.\nYour questions should cover:\nmy interests and problems I care about\nmy current skills and tools I know\nmy experience level (beginner/intermediate/advanced)\nhow much time I can realistically give\nwhether the project is for learning, competition, portfolio, business, or fun\nconstraints like budget, team size, device, or platform\nAfter I answer all the questions, analyze my responses and:\nsuggest 3–5 project ideas that actually fit me\nexplain why each idea is suitable\nmention the main challenges of each idea\nrecommend one best project to start with\noutline clear next steps to begin (tech stack, first milestone, etc.)\nAvoid generic ideas. Be practical, specific, and honest."},
        {"icon": "💡", "title": "Career Advice", "text": "I want career guidance, but don’t give advice immediately.\nFirst, ask me a series of clear and specific questions to understand me properly. Ask them step by step, not all at once.\nYour questions should cover:\nwhat I’m interested in and enjoy doing\nwhat I’m good at and what skills I already have\nwhat I dislike or want to avoid\nwhat kind of work environment suits me\nmy education level and practical limitations\nmy long-term goals, income expectations, and lifestyle preferences\nAfter you finish asking questions and I answer them, analyze my responses honestly and:\nsuggest 3–5 realistic career options\nexplain why each option fits or doesn’t fit me\npoint out any contradictions or unrealistic assumptions in my thinking\nsuggest concrete next steps for the best options\nBe direct, practical, and honest. No motivational fluff."},
        {"icon": "🛠️", "title": "Code Debugging", "text": "I need help debugging some code, but don’t jump to conclusions yet.\nFirst, ask me a sequence of focused questions to fully understand the problem. Ask them step by step, not all at once.\nYour questions should cover:\nthe programming language and environment\nwhat the code is supposed to do\nwhat it is actually doing\nexact error messages or unexpected behavior\nwhere and when the problem occurs\nwhat I’ve already tried\nAfter you have enough information and I answer, then:\nidentify the most likely root cause(s)\nexplain the bug in simple terms\nshow the corrected code\nexplain why the fix works\nsuggest how to prevent this type of bug in the future\nBe precise and technical. Don’t guess. Don’t oversimplify."}
    ]
    
    st.markdown('<div class="container"><div class="cards-wrapper"><div class="cards-container">', unsafe_allow_html=True)
    
    # Use standard Streamlit columns for the grid layout to ensure proper rendering
    cols = st.columns(3)
    for i, p in enumerate(prompts):
        with cols[i]:
            # The card visual container
            st.markdown(f'<div class="card"><div class="icon">{p["icon"]}</div><h2 class="card-title">{p["title"]}</h2>', unsafe_allow_html=True)
            # The invisible button that covers the card and handles the click
            if st.button(" ", key=f"btn_{i}"):
                st.session_state.chat_started = True
                st.session_state.messages.append({"role": "user", "content": p["text"]})
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Dots and swipe container for mobile - correctly nested according to reference
    st.markdown("""
        <div class="dots">
            <div class="dot active" onclick="goToSlide(0)"></div>
            <div class="dot" onclick="goToSlide(1)"></div>
            <div class="dot" onclick="goToSlide(2)"></div>
        </div>
    </div></div>
    """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("How can I help you today?", disabled=st.session_state.is_thinking):
    st.session_state.chat_started = True
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# Processing
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
                st.error(str(e))
            finally:
                st.session_state.is_thinking = False
                st.rerun()

with st.sidebar:
    st.title("Settings")
    if st.button("🗑️ Clear Chat Memory"):
        st.session_state.messages = [{"role": "system", "content": "You are a witty AI assistant."}]
        st.session_state.chat_started = False
        st.rerun()
