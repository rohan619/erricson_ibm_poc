from http.server import BaseHTTPRequestHandler, HTTPServer

def greet():
    return "Hello from Docker + Kubernetes + ArgoCD!"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(greet().encode())

def run():
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("Server running on port 8000...")
    server.serve_forever()

if __name__ == "__main__":
    run()