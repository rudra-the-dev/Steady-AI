from flask import Flask, render_template, request, jsonify, session
import os
from openai import OpenAI
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

client = OpenAI(
    api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
    base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
)

SYSTEM_PROMPT = "You are AI Chat Assistant, a versatile and highly adaptive digital companion. Your goal is to provide helpful and engaging responses while tailoring your personality to the user's needs. Use emojis to add personality and visual cues that match the tone, such as 🚀 for excitement or ✅ for tasks. You must dynamically adjust your behavior based on the question: for technical queries, be structured and professional; for casual chat, be warm and friendly; for urgent requests, be concise and direct; and for creative tasks, be enthusiastic and expansive. Use markdown like bolding and bullet points to ensure clarity. Always identify as AI Chat Assistant and maintain a proactive thought-partner persona. If a query is ambiguous, ask brief clarifying questions to better adapt your behavior."

@app.route('/')
def index():
    if 'messages' not in session:
        session['messages'] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    if 'messages' not in session:
        session['messages'] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    session['messages'].append({"role": "user", "content": data.get('message', '')})
    
    try:
        response = client.chat.completions.create(
            model="gpt-5",
            messages=session['messages'],
            max_completion_tokens=2048
        )
        reply = response.choices[0].message.content or ""
        session['messages'].append({"role": "assistant", "content": reply})
        session.modified = True
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    session['messages'] = [{"role": "system", "content": SYSTEM_PROMPT}]
    session.modified = True
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=5000)