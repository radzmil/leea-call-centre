import base64
import hashlib
import hmac
import os
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from phone_server import PhoneHandler


class PhoneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), PhoneHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path, params, signature=True):
        url = "https://example.test" + path
        value = url + "".join(k + params[k] for k in sorted(params))
        digest = base64.b64encode(hmac.new(b"test-token", value.encode(), hashlib.sha1).digest()).decode()
        return Request(self.url + path, data=urlencode(params).encode(), headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Twilio-Signature": digest if signature else "invalid",
        })

    def test_incoming_and_reply(self):
        with patch.dict(os.environ, {"PUBLIC_BASE_URL": "https://example.test", "TWILIO_AUTH_TOKEN": "test-token"}):
            with urlopen(self.request("/voice/incoming", {"CallSid": "CA123"})) as response:
                root = ElementTree.fromstring(response.read())
            self.assertIn("Leea Bot", root.find("Gather/Say").text)
            self.assertEqual(root.find("Gather").get("action"), "/voice/respond")
            with urlopen(self.request("/voice/respond", {"CallSid": "CA123", "SpeechResult": "Harga Gerak Gempur?"})) as response:
                root = ElementTree.fromstring(response.read())
            self.assertIn("RM39.90", root.find("Gather/Say").text)
            with urlopen(self.request("/voice/respond", {"SpeechResult": "tamat"})) as response:
                root = ElementTree.fromstring(response.read())
            self.assertIsNotNone(root.find("Hangup"))

    def test_rejects_unsigned_requests(self):
        with patch.dict(os.environ, {"PUBLIC_BASE_URL": "https://example.test", "TWILIO_AUTH_TOKEN": "test-token"}):
            with self.assertRaises(HTTPError) as error:
                urlopen(self.request("/voice/incoming", {"CallSid": "CA123"}, False))
            self.assertEqual(error.exception.code, 403)
            error.exception.close()


if __name__ == "__main__":
    unittest.main()