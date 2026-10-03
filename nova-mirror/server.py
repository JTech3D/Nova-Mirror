import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import base64
from urllib.parse import urlparse, parse_qs

PORT = 5000
CONFIG_FILE = "config.json"
SPOTIFY_SECRETS_FILE = "spotify_secrets.json"


def load_spotify_secrets():
    with open(SPOTIFY_SECRETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_spotify_secrets(data):
    with open(SPOTIFY_SECRETS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def spotify_token_request(params, secrets):
    body = urllib.parse.urlencode(params).encode("utf-8")
    auth = base64.b64encode(f"{secrets['client_id']}:{secrets['client_secret']}".encode()).decode()

    request = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=body,
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


class NovaMirrorHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/config":
            self.send_config()
        elif parsed.path == "/spotify/login":
            self.spotify_login()
        elif parsed.path == "/spotify/callback":
            self.spotify_callback(parsed)
        elif parsed.path == "/api/spotify/now-playing":
            self.spotify_now_playing()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/config":
            self.save_config()
        else:
            self.send_error(404, "Unbekannter Endpunkt")

    def send_json(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

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

    def spotify_login(self):
        secrets = load_spotify_secrets()
        params = {
            "client_id": secrets["client_id"],
            "response_type": "code",
            "redirect_uri": secrets["redirect_uri"],
            "scope": "user-read-currently-playing"
        }
        url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)

        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()

    def spotify_callback(self, parsed):
        code = parse_qs(parsed.query).get("code", [None])[0]
        if not code:
            self.send_error(400, "Kein Code von Spotify erhalten")
            return

        secrets = load_spotify_secrets()
        result = spotify_token_request({
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": secrets["redirect_uri"]
        }, secrets)

        secrets["refresh_token"] = result["refresh_token"]
        save_spotify_secrets(secrets)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("<html><body><h1>Spotify verbunden ✓</h1><p>Dieses Fenster kannst du jetzt schließen.</p></body></html>".encode("utf-8"))

    def spotify_now_playing(self):
        try:
            secrets = load_spotify_secrets()
        except FileNotFoundError:
            self.send_json({"connected": False})
            return

        if not secrets.get("refresh_token"):
            self.send_json({"connected": False})
            return

        try:
            token_result = spotify_token_request({
                "grant_type": "refresh_token",
                "refresh_token": secrets["refresh_token"]
            }, secrets)

            request = urllib.request.Request(
                "https://api.spotify.com/v1/me/player/currently-playing",
                headers={"Authorization": f"Bearer {token_result['access_token']}"}
            )

            with urllib.request.urlopen(request) as response:
                if response.status == 204:
                    self.send_json({"connected": True, "playing": False})
                    return
                data = json.loads(response.read())

            item = data.get("item") if data else None
            if not item:
                self.send_json({"connected": True, "playing": False})
                return

            images = item["album"]["images"]
            self.send_json({
                "connected": True,
                "playing": data.get("is_playing", False),
                "track": item["name"],
                "artist": ", ".join(a["name"] for a in item["artists"]),
                "image": images[0]["url"] if images else None
            })
        except Exception:
            self.send_json({"connected": False, "error": True})


with socketserver.TCPServer(("", PORT), NovaMirrorHandler) as httpd:
    print(f"Server läuft auf http://localhost:{PORT}")
    httpd.serve_forever()