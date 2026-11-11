import requests
import time
import subprocess
import os
from groq import Groq

CLOUD_URL = "https://jarvis-cloud-yka4.onrender.com" # Apna Render link daal
GROQ_API_KEY = "gsk_..." # Apni API key daal
client = Groq(api_key=GROQ_API_KEY)

print("J.A.R.V.I.S. Master Worker Online. Waiting for commands from Phone...")

while True:
    try:
        # 1. Cloud se command maango
        res = requests.get(f"{CLOUD_URL}/get_cmd", timeout=10)
        data = res.json()
        cmd = data.get("command")

        if cmd:
            print(f"\n[+] Command Received: {cmd}")
            requests.post(f"{CLOUD_URL}/update_status", json={"status": "Running", "log": f"Executing: {cmd}", "output": ""})

            # 2. Terminal me command run karo
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output = process.stdout + process.stderr

            # 3. Agar error aaya, toh AI se fix karwao
            if process.returncode != 0 and output.strip() != "":
                requests.post(f"{CLOUD_URL}/update_status", json={"status": "Running", "log": "Error detected. AI is analyzing and fixing...", "output": output})
                
                fix_prompt = f"The command '{cmd}' failed with error:\n{output}\n\nPlease provide the exact PowerShell command to fix this. Output ONLY the command."
                fix_response = client.chat.completions.create(
                    messages=[{"role": "user", "content": fix_prompt}],
                    model="openai/gpt-oss-120b",
                    max_tokens=500
                )
                fixed_cmd = fix_response.choices[0].message.content.strip()
                
                requests.post(f"{CLOUD_URL}/update_status", json={"status": "Running", "log": f"Auto-Fix applied: {fixed_cmd}", "output": output})
                process = subprocess.run(fixed_cmd, shell=True, capture_output=True, text=True)
                output += "\n\n--- AFTER AUTO-FIX ---\n" + process.stdout + process.stderr

            # 4. Final result cloud pe bhejo
            requests.post(f"{CLOUD_URL}/update_status", json={"status": "Completed", "log": "Command Executed Successfully.", "output": output})
            print("[+] Job Done.")

        time.sleep(3)

    except Exception as e:
        print(f"[-] Connection Error: {e}")
        time.sleep(5)
