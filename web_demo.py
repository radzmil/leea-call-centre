"""Demo browser setempat; bukan sistem telefoni atau perkhidmatan awam."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlencode

from assistant import conversational_answer, load_knowledge


PAGE = Path(__file__).with_name("index.html")
MAX_BODY = 8192
MAX_AUDIO = 10 * 1024 * 1024
VERSION = "2026-08-14"


def find_aisyah_voice(key):
    """Resolve the exact Aisyah voice visible to this Cartesia account."""
    request = Request("https://api.cartesia.ai/voices?" + urlencode({"q": "Aisyah", "limit": 100}),
                      headers={"Authorization": f"Bearer {key}", "Cartesia-Version": VERSION})
    with urlopen(request, timeout=10) as result:
        voices = json.load(result).get("data", [])
    matches = [voice for voice in voices if voice.get("name", "").casefold() == "aisyah"
               and voice.get("status") == "active"]
    if len(matches) != 1:
        raise ValueError("Suara Aisyah tidak ditemui secara unik.")
    return matches[0]["id"]


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        body = PAGE.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path not in ("/api/answer", "/api/tts"):
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_BODY:
                raise ValueError("Saiz soalan tidak sah.")
            payload = json.loads(self.rfile.read(size))
            field = "question" if self.path == "/api/answer" else "text"
            text = payload.get(field)
            if not isinstance(text, str) or not text.strip() or len(text) > 1000:
                raise ValueError("Sila masukkan teks ringkas.")
        except (ValueError, TypeError, AttributeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": str(exc)})
            return
        if self.path == "/api/answer":
            self.send_json(200, {"answer": conversational_answer(text, load_knowledge())})
            return
        key = os.environ.get("CARTESIA_API_KEY")
        if not key:
            self.send_json(503, {"error": "Kunci Cartesia belum dikonfigurasi pada pelayan."})
            return
        try:
            voice = os.environ.get("CARTESIA_VOICE_ID") or find_aisyah_voice(key)
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError, OSError):
            self.send_json(503, {"error": "Suara Aisyah tidak ditemui. Tetapkan CARTESIA_VOICE_ID pada pelayan."})
            return
        request = Request("https://api.cartesia.ai/tts/bytes", data=json.dumps({
            "model_id": "sonic-3.6", "transcript": text,
            "voice": voice, "language": "ms",
            "output_format": {"container": "wav", "encoding": "pcm_s16le", "sample_rate": 44100},
        }).encode("utf-8"), headers={
            "Authorization": f"Bearer {key}", "Cartesia-Version": VERSION,
            "Content-Type": "application/json",
        }, method="POST")
        try:
            with urlopen(request, timeout=20) as result:
                audio = result.read(MAX_AUDIO + 1)
                if len(audio) > MAX_AUDIO or not audio:
                    raise ValueError("Audio tidak sah.")
        except (HTTPError, URLError, TimeoutError, ValueError, OSError):
            self.send_json(502, {"error": "Suara Cartesia tidak tersedia. Jawapan teks masih boleh dibaca."})
            return
        self.send_response(200)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(audio)))
        self.end_headers()
        self.wfile.write(audio)

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8765), DemoHandler)
    print("Demo browser: http://127.0.0.1:8765/ (Ctrl+C untuk tamat)")
    server.serve_forever()