import json
import os
import threading
import unittest
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from web_demo import DemoHandler, find_aisyah_voice


class BrowserDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_home_page_labels_demo_and_language(self):
        with urlopen(self.base) as result:
            page = result.read().decode("utf-8")
        self.assertIn('lang="ms-MY"', page)
        self.assertIn("bukan panggilan telefon", page)
        self.assertIn("Leea Bot", page)
        self.assertIn("60183172114", page)
        self.assertIn('id="end"', page)
        self.assertIn('id="call"', page)
        self.assertNotIn('<textarea', page)
        self.assertIn('audio.createOscillator()', page)
        self.assertNotIn('Hai, saya Leea Bot, pembantu maya Architech Systems. Ada apa yang boleh saya bantu?', page)
        self.assertIn("const greeting = 'Helo, saya Leea Bot. Ada apa yang boleh saya bantu?';", page)
        self.assertIn('response.textContent = greeting;', page)
        self.assertIn('speak(greeting, () => { if (!typedMode) listen();', page)
        self.assertIn("fetch('/api/tts'", page)
        self.assertIn('detail.error || `Servis suara gagal (HTTP ${result.status}).`', page)
        self.assertIn('browserVoice(text, after, token, error.message', page)
        self.assertIn('utterance.lang = \'ms-MY\'', page)
        self.assertIn('id="text-fallback"', page)
        self.assertIn("showFallback();", page)
        self.assertIn("fallback.onsubmit", page)

    def test_microphone_errors_offer_specific_guidance(self):
        with urlopen(self.base) as result:
            page = result.read().decode("utf-8")
        for detail in ("not-allowed", "audio-capture", "no-speech", "network", "Chrome atau Edge biasa"):
            with self.subTest(detail=detail):
                self.assertIn(detail, page)

    def test_api_keeps_product_prices_separate(self):
        for question, present, absent in (
            ("Harga Gerak Gempur?", "RM39.90", "RM130/bulan"),
            ("Harga bot WhatsApp?", "RM130/bulan", "RM39.90"),
            ("Harga AI Call Center?", "Coming Soon", "RM39.90"),
        ):
            with self.subTest(question=question):
                request = Request(self.base + "/api/answer", data=json.dumps({"question": question}).encode(),
                                  headers={"Content-Type": "application/json"})
                with urlopen(request) as result:
                    answer = json.load(result)["answer"]
                self.assertIn(present, answer)
                self.assertNotIn(absent, answer)

    def test_invalid_question_is_rejected(self):
        request = Request(self.base + "/api/answer", data=b'{"question":""}',
                          headers={"Content-Type": "application/json"})
        with self.assertRaises(HTTPError) as error:
            urlopen(request)
        self.assertEqual(error.exception.code, 400)
        error.exception.close()

    def test_tts_requires_configuration(self):
        request = Request(self.base + "/api/tts", data=b'{"text":"Hai"}',
                          headers={"Content-Type": "application/json"})
        with patch.dict(os.environ, {"CARTESIA_API_KEY": "", "CARTESIA_VOICE_ID": ""}):
            with self.assertRaises(HTTPError) as error:
                urlopen(request)
        self.assertEqual(error.exception.code, 503)
        error.exception.close()

    def test_tts_sends_malay_text_without_exposing_key(self):
        request = Request(self.base + "/api/tts", data=json.dumps({"text": "Apa khabar?"}).encode(),
                          headers={"Content-Type": "application/json"})
        class AudioResponse:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self, *_): return b"RIFFdemo"

        with patch.dict(os.environ, {"CARTESIA_API_KEY": "test-secret", "CARTESIA_VOICE_ID": "test-voice"}), \
             patch("web_demo.urlopen", return_value=AudioResponse()) as upstream:
            with urlopen(request) as result:
                self.assertEqual(result.headers["Content-Type"], "audio/wav")
                self.assertEqual(result.read(), b"RIFFdemo")
        sent = upstream.call_args.args[0]
        self.assertEqual(sent.get_header("Authorization"), "Bearer test-secret")
        self.assertEqual(json.loads(sent.data)["language"], "ms")

    def test_resolves_exact_aisyah_voice(self):
        class VoiceResponse:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self, *_):
                return json.dumps({"data": [
                    {"name": "Aisyah", "id": "aisyah-id", "status": "active"},
                    {"name": "Aisyah 2", "id": "other-id", "status": "active"},
                ]}).encode()

        with patch("web_demo.urlopen", return_value=VoiceResponse()) as upstream:
            self.assertEqual(find_aisyah_voice("test-secret"), "aisyah-id")
        self.assertIn("q=Aisyah", upstream.call_args.args[0].full_url)
        self.assertEqual(upstream.call_args.args[0].get_header("Authorization"), "Bearer test-secret")

    def test_ambiguous_aisyah_voice_is_rejected(self):
        class VoiceResponse:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self, *_):
                return json.dumps({"data": [
                    {"name": "Aisyah", "id": "one", "status": "active"},
                    {"name": "aisyah", "id": "two", "status": "active"},
                ]}).encode()

        with patch("web_demo.urlopen", return_value=VoiceResponse()):
            with self.assertRaises(ValueError):
                find_aisyah_voice("test-secret")


if __name__ == "__main__":
    unittest.main()