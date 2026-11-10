import os
import time
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Global Memory for current job
job = {"status": "Idle", "progress": 0, "log": "Waiting for command...", "result": ""}

HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS MOBILE STUDIO</title>
    <style>
        body { background: #0a0a0a; color: #00ffff; font-family: 'Courier New', monospace; text-align: center; padding: 20px; margin: 0; }
        h1 { text-shadow: 0 0 10px #00ffff; }
        input { width: 90%; padding: 15px; margin: 10px 0; background: #111; border: 1px solid #00ffff; color: #00ffff; border-radius: 5px; font-size: 16px; }
        .btn-group { display: flex; justify-content: center; gap: 10px; }
        button { padding: 15px; background: #00ffff; color: #000; font-weight: bold; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; flex: 1; max-width: 150px;}
        button:disabled { background: #333; color: #666; }
        .progress-container { width: 90%; background: #222; border: 1px solid #00ffff; border-radius: 10px; margin: 20px auto; overflow: hidden; height: 25px; }
        .progress-bar { width: 0%; height: 100%; background: #00ffff; transition: width 0.5s; text-align: center; color: #000; font-weight: bold; line-height: 25px; font-size: 14px;}
        #log { text-align: left; background: #050505; padding: 15px; border: 1px solid #333; height: 200px; overflow-y: auto; font-size: 14px; width: 85%; margin: 0 auto; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>J.A.R.V.I.S. STUDIO</h1>
    <p>Remote Game Builder</p>
    
    <input type="text" id="prompt" placeholder="Example: Make a 3D Dino game">
    <div class="btn-group">
        <button id="btnAuto" onclick="startJob('auto')">AUTO BUILD</button>
        <button id="btnManual" onclick="startJob('manual')">MANUAL</button>
    </div>
    
    <div class="progress-container"><div class="progress-bar" id="progress">0%</div></div>
    <div id="log">Status: Idle</div>

    <script>
        function startJob(mode) {
            const prompt = document.getElementById('prompt').value;
            if(!prompt) return alert("Enter a game idea first!");
            
            document.getElementById('btnAuto').disabled = true;
            document.getElementById('btnManual').disabled = true;
            
            fetch('/start_job', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: prompt, mode: mode})
            }).then(() => {
                document.getElementById('log').innerText = "Sending command to Laptop...\n";
                pollProgress();
            });
        }

        function pollProgress() {
            fetch('/get_progress').then(res => res.json()).then(data => {
                document.getElementById('progress').style.width = data.progress + '%';
                document.getElementById('progress').innerText = data.progress + '%';
                document.getElementById('log').innerText = "STATUS: " + data.status + "\\n\\nLOG:\\n" + data.log;
                
                if (data.progress < 100 && data.progress > 0) {
                    setTimeout(pollProgress, 2000);
                } else {
                    document.getElementById('btnAuto').disabled = false;
                    document.getElementById('btnManual').disabled = false;
                }
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_UI)

# Phone calls this to start
@app.route('/start_job', methods=['POST'])
def start_job():
    global job
    data = request.json
    job = {"status": "Pending", "progress": 1, "log": f"Received {data['mode']} command: {data['prompt']}", "result": ""}
    return jsonify({"status": "ok"})

# Laptop calls this to get the job
@app.route('/get_job', methods=['GET'])
def get_job():
    global job
    if job["status"] == "Pending":
        job["status"] = "Running"
        return jsonify({"prompt": job["log"].split(": ")[1], "mode": "auto"}) # Simplified for now
    return jsonify({"prompt": ""})

# Laptop calls this to update progress
@app.route('/update_progress', methods=['POST'])
def update_progress():
    global job
    data = request.json
    job["progress"] = data.get("progress", job["progress"])
    job["status"] = data.get("status", job["status"])
    job["log"] = data.get("log", job["log"])
    job["result"] = data.get("result", job["result"])
    return jsonify({"status": "ok"})

# Phone checks this
@app.route('/get_progress', methods=['GET'])
def get_progress():
    return jsonify(job)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
