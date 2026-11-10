import os
import time
import threading
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Global variables to track progress
progress_data = {"percent": 0, "status": "Idle", "game_html": ""}

HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>J.A.R.V.I.S. MOBILE</title>
    <style>
        body { background-color: #0a0a0a; color: #00ffff; font-family: 'Courier New', monospace; text-align: center; padding: 20px; margin: 0; }
        h1 { text-shadow: 0 0 10px #00ffff; font-size: 24px; }
        input { width: 90%; padding: 12px; margin: 10px 0; background: #111; border: 1px solid #00ffff; color: #00ffff; border-radius: 5px; font-size: 16px; }
        button { padding: 12px 20px; background: #00ffff; color: #000; font-weight: bold; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin-top: 10px; }
        button:disabled { background: #333; color: #666; }
        .progress-container { width: 90%; background: #222; border: 1px solid #00ffff; border-radius: 10px; margin: 20px auto; overflow: hidden; height: 20px; }
        .progress-bar { width: 0%; height: 100%; background: #00ffff; transition: width 0.5s; }
        #log { text-align: left; background: #050505; padding: 10px; border: 1px solid #333; height: 100px; overflow-y: auto; font-size: 12px; width: 90%; margin: 0 auto; }
        #game-container { display: none; width: 100%; height: 70vh; border: 2px solid #00ffff; margin-top: 20px; }
        iframe { width: 100%; height: 100%; border: none; }
    </style>
</head>
<body>
    <h1>J.A.R.V.I.S.</h1>
    <p>Mobile Command Center</p>
    
    <input type="text" id="prompt" placeholder="Example: Make a 3D Dino game">
    <br>
    <button id="buildBtn" onclick="buildGame()">BUILD GAME</button>
    
    <div class="progress-container"><div class="progress-bar" id="progress"></div></div>
    <p id="status">Status: Idle</p>
    
    <div id="log"></div>

    <div id="game-container">
        <iframe id="game-iframe"></iframe>
    </div>

    <script>
        function buildGame() {
            const prompt = document.getElementById('prompt').value;
            if(!prompt) return alert("Enter a prompt!");
            
            document.getElementById('buildBtn').disabled = true;
            document.getElementById('game-container').style.display = 'none';
            document.getElementById('log').innerHTML = "";
            
            fetch('/build', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: prompt})
            }).then(res => res.json()).then(data => {
                pollProgress();
            });
        }

        function pollProgress() {
            fetch('/progress').then(res => res.json()).then(data => {
                document.getElementById('progress').style.width = data.percent + '%';
                document.getElementById('status').innerText = "Status: " + data.status;
                
                if (data.percent < 100) {
                    setTimeout(pollProgress, 1000);
                } else {
                    document.getElementById('buildBtn').disabled = false;
                    document.getElementById('game-container').style.display = 'block';
                    document.getElementById('game-iframe').srcdoc = data.game_html;
                }
            });
        }
    </script>
</body>
</html>
"""

def build_process(prompt):
    global progress_data
    try:
        progress_data["percent"] = 10
        progress_data["status"] = "Analyzing Request..."
        time.sleep(2)
        
        progress_data["percent"] = 30
        progress_data["status"] = "Writing Game Code (AI)..."
        
        system_prompt = """You are J.A.R.V.I.S. Write a complete, playable HTML/CSS/JS game using Three.js (CDN: https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js). 
        Requirements: 
        1. Single HTML file. 
        2. Start Menu. 
        3. No external models (use shapes). 
        4. Add lights. 
        Output ONLY the raw HTML code."""
        
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=4000
        )
        
        progress_data["percent"] = 80
        progress_data["status"] = "Compiling Game..."
        
        raw_html = response.choices[0].message.content
        # Extract HTML
        if "```html" in raw_html:
            raw_html = raw_html.split("```html")[1].split("```")[0]
        elif "```" in raw_html:
            raw_html = raw_html.split("```")[1].split("```")[0]
            
        progress_data["game_html"] = raw_html.strip()
        progress_data["percent"] = 100
        progress_data["status"] = "Game Built Successfully!"
        
    except Exception as e:
        progress_data["status"] = f"Error: {str(e)}"
        progress_data["percent"] = 0

@app.route('/')
def home():
    return render_template_string(HTML_UI)

@app.route('/build', methods=['POST'])
def build():
    global progress_data
    prompt = request.json.get('prompt')
    progress_data = {"percent": 0, "status": "Starting...", "game_html": ""}
    threading.Thread(target=build_process, args=(prompt,)).start()
    return jsonify({"status": "started"})

@app.route('/progress')
def progress():
    return jsonify(progress_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
