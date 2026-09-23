import http.server
import socketserver
import json

PORT = 5000
CONFIG_FILE = "config.json"


class NovaMirrorHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/config":
            self.send_config()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/config":
            self.save_config()
        else:
            self.send_error(404, "Unbekannter Endpunkt")

    def send_config(self):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = f.read()
        except FileNotFoundError:
            data = "{}"

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data.encode("utf-8"))

    def save_config(self):
        length = int(self.headers["Content-Length"])
        body = self.rfile.read(length)

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, "Ungültiges JSON")
            return

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')


with socketserver.TCPServer(("", PORT), NovaMirrorHandler) as httpd:
    print(f"Server läuft auf http://localhost:{PORT}")
    httpd.serve_forever()