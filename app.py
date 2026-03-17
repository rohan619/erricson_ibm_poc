from flask import Flask, render_template, jsonify
import os
import socket
import platform
import psutil
import datetime
import sys

app = Flask(__name__)

@app.route('/')
def home():
    # Gather GKE Pod & System metrics
    pod_name = socket.gethostname()
    try:
        pod_ip = socket.gethostbyname(pod_name)
    except:
        pod_ip = "Unknown"
        
    system_info = {
        "os": platform.system(),
        "release": platform.release(),
        "python_version": sys.version.split(' ')[0],
        "time": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }
    
    return render_template('index.html', 
                           pod_name=pod_name, 
                           pod_ip=pod_ip,
                           system_info=system_info)

# Live data endpoint for our dashboard to fetch every second!
@app.route('/api/metrics')
def metrics():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=0.1),
        "memory": psutil.virtual_memory().percent
    })

# Kubernetes Health Check
@app.route('/health')
def health_check():
    return {"status": "healthy", "pod": socket.gethostname()}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)