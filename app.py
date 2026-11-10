import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def home():
    return "<h1>JARVIS Cloud is Online 24/7</h1><p>Laptop can be shut down now.</p>"

@app.route('/command', methods=['POST'])
def command():
    user_text = request.json.get('text', '')
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": user_text}],
            model="llama-3.3-70b-versatile"
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
