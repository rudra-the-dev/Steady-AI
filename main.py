from flask import Flask, render_template_string, request, jsonify, session
import os
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Constants from environment
AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
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
    )

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception(is_rate_limit_error),
    reraise=True
)
def get_ai_response(messages):
    try:
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
            return "Error: Cloud budget exceeded."
        raise e

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💬 AI Chat Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #F8F5F0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            background-color: #fff;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header h1 {
            color: #2D3E33;
            font-size: 24px;
            margin-bottom: 5px;
        }

        .header p {
            color: #666;
            font-size: 14px;
        }

        .container {
            flex: 1;
            max-width: 1200px;
            width: 100%;
            margin: 0 auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
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
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .banner-text h2 {
            color: #F8F5F0;
            font-family: 'Georgia', serif;
            font-size: 36px;
            margin: 0;
        }

        .banner-text p {
            color: #C2CDC5;
            font-size: 18px;
            margin-top: 10px;
        }

        .banner-icon {
            font-size: 60px;
            opacity: 0.8;
        }

        /* Cards Container */
        .cards-wrapper {
            position: relative;
            overflow: hidden;
            margin-bottom: 30px;
        }

        .cards-container {
            display: flex;
            gap: 20px;
            transition: transform 0.3s ease-out;
        }

        .card {
            background-color: #EFE9DE;
            border-radius: 15px;
            padding: 30px;
            min-height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            cursor: pointer;
            transition: all 0.2s ease;
            border: none;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            position: relative;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }

        .card-icon {
            font-size: 35px;
            position: absolute;
            top: 20px;
            right: 20px;
        }

        .card-title {
            font-size: 20px;
            font-weight: 600;
            color: #2D3E33;
            line-height: 1.3;
            font-family: 'Georgia', serif;
            margin-top: auto;
            max-width: 80%;
        }

        /* Desktop view */
        @media (min-width: 769px) {
            .cards-container {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
            }

            .card {
                flex: none;
                width: 100%;
            }

            .nav-buttons, .dots {
                display: none;
            }
        }

        /* Mobile view */
        @media (max-width: 768px) {
            .custom-banner {
                padding: 30px 20px;
            }

            .banner-text h2 {
                font-size: 28px;
            }

            .banner-text p {
                font-size: 16px;
            }

            .cards-wrapper {
                padding: 0 20px;
            }

            .cards-container {
                gap: 20px;
            }

            .card {
                flex: 0 0 calc(100vw - 40px);
                scroll-snap-align: center;
            }

            .nav-buttons {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 20px;
                padding: 0 20px;
            }

            .nav-btn {
                background-color: #EFE9DE;
                border: 2px solid #4A5D50;
                border-radius: 12px;
                width: 50px;
                height: 50px;
                font-size: 24px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #2D3E33;
                transition: all 0.2s;
            }

            .nav-btn:hover {
                background-color: #E9E1D3;
            }

            .dots {
                display: flex;
                justify-content: center;
                gap: 8px;
                margin-top: 15px;
            }

            .dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: #d4cfc4;
                transition: all 0.3s ease;
                cursor: pointer;
            }

            .dot.active {
                background-color: #4A5D50;
                width: 24px;
                border-radius: 4px;
            }
        }

        /* Chat Section */
        .chat-section {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            max-height: 500px;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            margin-bottom: 20px;
        }

        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 80%;
            line-height: 1.5;
        }

        .user-message {
            background-color: #E3F2FD;
            margin-left: auto;
            text-align: right;
        }

        .assistant-message {
            background-color: #F5F5F5;
            margin-right: auto;
        }

        .message-label {
            font-weight: 600;
            margin-bottom: 5px;
            font-size: 12px;
            color: #666;
        }

        .thinking {
            background-color: #FFF3E0;
            padding: 12px 16px;
            border-radius: 12px;
            display: inline-block;
            font-style: italic;
            color: #666;
        }

        /* Chat Input */
        .chat-input-container {
            position: sticky;
            bottom: 0;
            background: white;
            padding: 20px;
            border-top: 1px solid #eee;
        }

        .chat-input-wrapper {
            display: flex;
            gap: 10px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .chat-input {
            flex: 1;
            padding: 12px 20px;
            border: 2px solid #E9E1D3;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.2s;
        }

        .chat-input:focus {
            border-color: #4A5D50;
        }

        .send-btn {
            background: linear-gradient(135deg, #2D3E33 0%, #4A5D50 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .send-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* Clear button */
        .clear-btn {
            background-color: #ff4b4b;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 20px;
        }

        .clear-btn:hover {
            background-color: #ff3333;
        }

        .hidden {
            display: none;
        }

        /* Loading animation */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .thinking {
            animation: pulse 1.5s ease-in-out infinite;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>💬 AI Chat Assistant</h1>
        <p>A helpful assistant with memory of our conversation</p>
    </div>

    <div class="container">
        <div id="cardsSection">
            <div class="custom-banner">
                <div class="banner-text">
                    <h2>Hello, Friend</h2>
                    <p>How can I help you move forward today?</p>
                </div>
                <div class="banner-icon">✨</div>
            </div>

            <div class="cards-wrapper">
                <div class="cards-container" id="cardsContainer">
                    <div class="card" onclick="selectCard(0)">
                        <div class="card-icon">🚀</div>
                        <div class="card-title">Start a new project</div>
                    </div>
                    <div class="card" onclick="selectCard(1)">
                        <div class="card-icon">💡</div>
                        <div class="card-title">Level up your career</div>
                    </div>
                    <div class="card" onclick="selectCard(2)">
                        <div class="card-icon">🛠️</div>
                        <div class="card-title">Fix some broken code</div>
                    </div>
                </div>
            </div>

            <div class="nav-buttons">
                <button class="nav-btn" onclick="prevSlide()">◀</button>
                <button class="nav-btn" onclick="nextSlide()">▶</button>
            </div>

            <div class="dots" id="dots">
                <div class="dot active" onclick="goToSlide(0)"></div>
                <div class="dot" onclick="goToSlide(1)"></div>
                <div class="dot" onclick="goToSlide(2)"></div>
            </div>
        </div>

        <div class="chat-section" id="chatSection">
            <button class="clear-btn" onclick="clearChat()">🗑️ Clear Chat</button>
            <div class="chat-messages" id="chatMessages"></div>
        </div>
    </div>

    <div class="chat-input-container">
        <div class="chat-input-wrapper">
            <input 
                type="text" 
                class="chat-input" 
                id="chatInput" 
                placeholder="How can I help you today?"
                onkeypress="handleKeyPress(event)"
            >
            <button class="send-btn" id="sendBtn" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let currentSlide = 0;
        let chatStarted = false;
        let isThinking = false;

        const prompts = [
            {
                title: "Start a new project",
                text: "I want ideas for a project, but don't suggest anything yet.\\nFirst, ask me a series of specific questions to understand my situation properly. Ask them step by step, not all at once.\\nYour questions should cover:\\nmy interests and problems I care about\\nmy current skills and tools I know\\nmy experience level (beginner/intermediate/advanced)\\nhow much time I can realistically give\\nwhether the project is for learning, competition, portfolio, business, or fun\\nconstraints like budget, team size, device, or platform\\nAfter I answer all the questions, analyze my responses and:\\nsuggest 3–5 project ideas that actually fit me\\nexplain why each idea is suitable\\nmention the main challenges of each idea\\nrecommend one best project to start with\\noutline clear next steps to begin (tech stack, first milestone, etc.)\\nAvoid generic ideas. Be practical, specific, and honest."
            },
            {
                title: "Level up your career",
                text: "I want career guidance, but don't give advice immediately.\\nFirst, ask me a series of clear and specific questions to understand me properly. Ask them step by step, not all at once.\\nYour questions should cover:\\nwhat I'm interested in and enjoy doing\\nwhat I'm good at and what skills I already have\\nwhat I dislike or want to avoid\\nwhat kind of work environment suits me\\nmy education level and practical limitations\\nmy long-term goals, income expectations, and lifestyle preferences\\nAfter you finish asking questions and I answer them, analyze my responses honestly and:\\nsuggest 3–5 realistic career options\\nexplain why each option fits or doesn't fit me\\npoint out any contradictions or unrealistic assumptions in my thinking\\nsuggest concrete next steps for the best options\\nBe direct, practical, and honest. No motivational fluff."
            },
            {
                title: "Fix some broken code",
                text: "I need help debugging some code, but don't jump to conclusions yet.\\nFirst, ask me a sequence of focused questions to fully understand the problem. Ask them step by step, not all at once.\\nYour questions should cover:\\nthe programming language and environment\\nwhat the code is supposed to do\\nwhat it is actually doing\\nexact error messages or unexpected behavior\\nwhere and when the problem occurs\\nwhat I've already tried\\nAfter you have enough information and I answer, then:\\nidentify the most likely root cause(s)\\nexplain the bug in simple terms\\nshow the corrected code\\nexplain why the fix works\\nsuggest how to prevent this type of bug in the future\\nBe precise and technical. Don't guess. Don't oversimplify."
            }
        ];

        function updateDots() {
            const dots = document.querySelectorAll('.dot');
            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === currentSlide);
            });
        }

        function goToSlide(index) {
            if (window.innerWidth <= 768) {
                currentSlide = index;
                const cardWidth = document.querySelector('.card').offsetWidth;
                const gap = 20;
                const offset = -(currentSlide * (cardWidth + gap));
                document.getElementById('cardsContainer').style.transform = `translateX(${offset}px)`;
                updateDots();
            }
        }

        function nextSlide() {
            currentSlide = (currentSlide + 1) % 3;
            goToSlide(currentSlide);
        }

        function prevSlide() {
            currentSlide = (currentSlide - 1 + 3) % 3;
            goToSlide(currentSlide);
        }

        function selectCard(index) {
            chatStarted = true;
            document.getElementById('cardsSection').classList.add('hidden');
            sendHiddenMessage(prompts[index].text);
        }

        function addMessage(role, content) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}-message`;
            
            const label = document.createElement('div');
            label.className = 'message-label';
            label.textContent = role === 'user' ? 'You' : 'Assistant';
            
            const text = document.createElement('div');
            text.textContent = content;
            
            messageDiv.appendChild(label);
            messageDiv.appendChild(text);
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function showThinking() {
            const chatMessages = document.getElementById('chatMessages');
            const thinkingDiv = document.createElement('div');
            thinkingDiv.className = 'thinking';
            thinkingDiv.id = 'thinkingIndicator';
            thinkingDiv.textContent = 'Thinking...';
            chatMessages.appendChild(thinkingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function removeThinking() {
            const thinking = document.getElementById('thinkingIndicator');
            if (thinking) thinking.remove();
        }

        async function sendHiddenMessage(message) {
            isThinking = true;
            document.getElementById('sendBtn').disabled = true;
            
            showThinking();

            try {
                const response = await fetch('/send_message', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message, hidden: true})
                });

                const data = await response.json();
                removeThinking();

                if (data.error) {
                    addMessage('assistant', 'Error: ' + data.error);
                } else {
                    addMessage('assistant', data.response);
                }
            } catch (error) {
                removeThinking();
                addMessage('assistant', 'Error: Failed to get response');
            }

            isThinking = false;
            document.getElementById('sendBtn').disabled = false;
        }

        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();

            if (!message || isThinking) return;

            chatStarted = true;
            document.getElementById('cardsSection').classList.add('hidden');

            addMessage('user', message);
            input.value = '';

            isThinking = true;
            document.getElementById('sendBtn').disabled = true;
            
            showThinking();

            try {
                const response = await fetch('/send_message', {
            method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message, hidden: false})
                });

                const data = await response.json();
                removeThinking();

                if (data.error) {
                    addMessage('assistant', 'Error: ' + data.error);
                } else {
                    addMessage('assistant', data.response);
                }
            } catch (error) {
                removeThinking();
                addMessage('assistant', 'Error: Failed to get response');
            }

            isThinking = false;
            document.getElementById('sendBtn').disabled = false;
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        async function clearChat() {
            try {
                await fetch('/clear_chat', {method: 'POST'});
                document.getElementById('chatMessages').innerHTML = '';
                chatStarted = false;
                document.getElementById('cardsSection').classList.remove('hidden');
                currentSlide = 0;
                goToSlide(0);
            } catch (error) {
                console.error('Error clearing chat:', error);
            }
        }

        // Touch/swipe support for mobile
        let touchStartX = 0;
        let touchEndX = 0;

        const cardsContainer = document.getElementById('cardsContainer');

        cardsContainer.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
        });

        cardsContainer.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });

        function handleSwipe() {
            if (window.innerWidth > 768) return;
            
            const diff = touchStartX - touchEndX;
            if (Math.abs(diff) > 50) {
                if (diff > 0) {
                    nextSlide();
                } else {
                    prevSlide();
                }
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    if 'messages' not in session:
        session['messages'] = [
            {"role": "You are AI Chat Assistant, a versatile, emotionally intelligent, and highly adaptive digital companion. Your goal is to provide helpful, accurate, and engaging responses while tailoring your personality to the user's specific needs.1. Adaptive Behavior & Tone.You must dynamically adjust your communication style based on the nature of the user's input:Technical/Complex: Provide structured, precise, and professional explanations. Use markdown for clarity.Casual/Conversational: Be friendly, warm, and brief. Act like a helpful peer.Urgent/Direct: Give concise, 'bottom-line-first' answers without unnecessary filler.Creative/Brainstorming: Be enthusiastic, expansive, and encouraging.2. Visual & Expressive GuidelinesEmoji Usage: Use emojis to add personality and visual cues, but ensure they match the tone.
Casual: 🚀, ✨, 😊
Professional: 📊, ✅, 💡
Warning/Note: ⚠️, 🔍
Formatting: Use bolding for emphasis, bullet points for lists, and clear headings to make responses scannable.3. Core Constraints
Always identify as AI Chat Assistant if asked.
Maintain a helpful and proactive 'thought partner'persona.
If a query is ambiguous, ask brief clarifying questions to better adapt your behavior.}
        ]
    return render_template_string(HTML_TEMPLATE)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data.get('message', '')
    is_hidden = data.get('hidden', False)
    
    if 'messages' not in session:
        session['messages'] = [
            {"role": "system", "content": "You are a witty AI assistant that NEVER gives long explanations or answers upfront. Your goal is to be extremely interactive. For EVERY user request, you must ask 2-3 specific follow-up questions to understand their context before providing any real help. Keep your initial responses very short and focused entirely on gathering information."}
        ]
    
    session['messages'].append({"role": "user", "content": message})
    
    try:
        response = get_ai_response(session['messages'])
        session['messages'].append({"role": "assistant", "content": response})
        session.modified = True
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    session['messages'] = [
        {"role": "system", "content": "You are a witty AI assistant that NEVER gives long explanations or answers upfront. Your goal is to be extremely interactive. For EVERY user request, you must ask 2-3 specific follow-up questions to understand their context before providing any real help. Keep your initial responses very short and focused entirely on gathering information."}
    ]
    session.modified = True
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)