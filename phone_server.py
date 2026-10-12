"""Webhook Twilio Voice untuk panggilan masuk Leea Bot (turn-based)."""

import base64
import hashlib
import hmac
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs
from xml.etree.ElementTree import Element, SubElement, tostring

from assistant import conversational_answer, load_knowledge


MAX_BODY = 8192


def signed(url, params, signature, token):
    """Twilio form POST: URL diikuti kunci parameter tersusun dan nilainya."""
    if not token or not signature:
        return False
    value = url + "".join(key + item for key in sorted(params) for item in params[key])
    expected = base64.b64encode(hmac.new(token.encode(), value.encode(), hashlib.sha1).digest()).decode()
    return hmac.compare_digest(expected, signature)


def twiml(message, language="ms-MY", finish=False):
    root = Element("Response")
    if finish:
        SubElement(root, "Say", {"language": language}).text = message
        SubElement(root, "Hangup")
    else:
        gather = SubElement(root, "Gather", {"input": "speech", "action": "/voice/respond",
                                            "method": "POST", "language": language,
                                            "speechTimeout": "auto", "timeout": "6"})
        SubElement(gather, "Say", {"language": language}).text = message
        SubElement(root, "Say", {"language": language}).text = "Tiada jawapan diterima. Sila hubungi semula."
        SubElement(root, "Hangup")
    return b'<?xml version="1.0" encoding="UTF-8"?>' + tostring(root, encoding="utf-8")


class PhoneHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/health":
            self.send_error(404)
            return
        self.reply(200, b"ok", "text/plain; charset=utf-8")

    def do_POST(self):
        if self.path not in ("/voice/incoming", "/voice/respond"):
            self.send_error(404)
            return
        base = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")
        token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        if not base.startswith("https://") or not token:
            self.send_error(503)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_BODY or self.headers.get("Content-Type", "").split(";", 1)[0] != "application/x-www-form-urlencoded":
                raise ValueError("Invalid form")
            params = parse_qs(self.rfile.read(size).decode("utf-8"), keep_blank_values=True, strict_parsing=True)
        except (ValueError, UnicodeDecodeError):
            self.send_error(400)
            return
        if not signed(base + self.path, params, self.headers.get("X-Twilio-Signature", ""), token):
            self.send_error(403)
            return
        language = os.environ.get("TWILIO_LANGUAGE", "ms-MY")
        if self.path == "/voice/incoming":
            message = "Hai! Saya Leea Bot, pembantu maya Architech Systems. Apa yang boleh saya bantu?"
            body = twiml(message, language)
        else:
            speech = params.get("SpeechResult", [""])[0].strip()
            if len(speech) > 1000:
                self.send_error(400)
                return
            if speech.casefold() in ("tamat", "selamat tinggal", "bye"):
                body = twiml("Terima kasih kerana menghubungi Architech Systems. Selamat tinggal.", language, True)
            else:
                message = (conversational_answer(speech, load_knowledge()) if speech else
                           "Maaf, saya tidak dengar soalan tadi. Sila ulang sekali lagi.")
                body = twiml(message, language)
        self.reply(200, body, "text/xml; charset=utf-8")

    def reply(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    if not os.environ.get("PUBLIC_BASE_URL", "").startswith("https://") or not os.environ.get("TWILIO_AUTH_TOKEN"):
        raise SystemExit("Set PUBLIC_BASE_URL (https) dan TWILIO_AUTH_TOKEN pada pelayan dahulu.")
    port = int(os.environ.get("PORT", "8765"))
    ThreadingHTTPServer(("0.0.0.0", port), PhoneHandler).serve_forever()