import datetime
import os
import platform
import socket
import sys
from collections import deque

import psutil
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
APP_START_TIME = datetime.datetime.utcnow()
METRICS_HISTORY = deque(maxlen=120)
REQUEST_COUNT = 0


def _get_pod_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except OSError:
        return "Unknown"


def _collect_metrics(sample_cpu=True):
    cpu_percent = psutil.cpu_percent(interval=0.1) if sample_cpu else psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    uptime_seconds = int((datetime.datetime.utcnow() - APP_START_TIME).total_seconds())

    load_1m = None
    if hasattr(os, "getloadavg"):
        load_1m = round(os.getloadavg()[0], 2)

    metric = {
        "cpu": round(cpu_percent, 1),
        "memory": round(memory.percent, 1),
        "disk": round(disk.percent, 1),
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
        "load_1m": load_1m,
        "requests_served": REQUEST_COUNT,
    }
    METRICS_HISTORY.append(metric)
    return metric


@app.before_request
def _track_requests():
    global REQUEST_COUNT
    if request.endpoint != "static":
        REQUEST_COUNT += 1


@app.route('/')
def home():
    pod_name = socket.gethostname()
    system_info = {
        "os": platform.system(),
        "release": platform.release(),
        "python_version": sys.version.split(' ')[0],
        "time": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "platform": platform.platform(),
        "service": os.environ.get("SERVICE_NAME", "erricson-ibm-poc"),
    }

    boot_info = {
        "start_time": APP_START_TIME.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "requests": REQUEST_COUNT,
    }

    return render_template(
        'index.html',
        pod_name=pod_name,
        pod_ip=_get_pod_ip(),
        system_info=system_info,
        boot_info=boot_info,
    )


@app.route('/api/metrics')
def metrics():
    return jsonify(_collect_metrics())


@app.route('/api/history')
def metrics_history():
    if not METRICS_HISTORY:
        _collect_metrics(sample_cpu=False)
    return jsonify({"points": list(METRICS_HISTORY)})


@app.route('/api/system')
def system_snapshot():
    return jsonify({
        "hostname": socket.gethostname(),
        "pod_ip": _get_pod_ip(),
        "python_version": sys.version.split(' ')[0],
        "platform": platform.platform(),
        "service": os.environ.get("SERVICE_NAME", "erricson-ibm-poc"),
        "uptime_seconds": int((datetime.datetime.utcnow() - APP_START_TIME).total_seconds()),
        "requests_served": REQUEST_COUNT,
    })


@app.route('/api/insights')
def insights():
    if not METRICS_HISTORY:
        current = _collect_metrics(sample_cpu=False)
    else:
        current = METRICS_HISTORY[-1]

    score = max(0, 100 - int((current["cpu"] * 0.5) + (current["memory"] * 0.3) + (current["disk"] * 0.2)))
    state = "stable"
    if score < 45:
        state = "critical"
    elif score < 70:
        state = "watch"

    return jsonify({
        "state": state,
        "stability_score": score,
        "current": current,
    })


@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "pod": socket.gethostname(),
        "uptime_seconds": int((datetime.datetime.utcnow() - APP_START_TIME).total_seconds()),
    }, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
