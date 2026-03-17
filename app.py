from flask import Flask, render_template
import os
import socket

app = Flask(__name__)

@app.route('/')
def home():
    # Inside GKE, the hostname is the Pod's name!
    pod_name = socket.gethostname()
    
    return render_template('index.html', pod_name=pod_name)

# A health check endpoint - Gemini Cloud Assist and GKE love this for monitoring!
@app.route('/health')
def health_check():
    return {"status": "healthy", "pod": socket.gethostname()}, 200

if __name__ == '__main__':
    # Gunicorn will actually handle the serving in production, but this is good for local testing
    app.run(host='0.0.0.0', port=8080)