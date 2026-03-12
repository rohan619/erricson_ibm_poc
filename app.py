from http.server import BaseHTTPRequestHandler, HTTPServer

def greet(name="world"):
    return f"Hello, {name}!"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        message = greet()
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode())

def run():
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("Server running on port 8000...")
    server.serve_forever()

if __name__ == "__main__":
    run()