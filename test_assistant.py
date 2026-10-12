import unittest

from assistant import answer, conversational_answer, load_knowledge


class AssistantTests(unittest.TestCase):
    def test_company_persona_and_payment_do_not_invent_facts(self):
        data = load_knowledge()
        self.assertIn("Leea Bot", conversational_answer("Hai", data))
        self.assertIn("Architech Systems", conversational_answer("Hai", data))
        self.assertIn("Pembayaran melalui telefon tidak dibenarkan", answer("Macam mana nak bayar?", data))
        self.assertEqual(answer("Cara bayar?", {**data, "payment_method": "Portal rasmi"}),
                         answer("Cara bayar?", data))

    def test_phone_payment_requests_never_turn_into_price_or_purchase_answers(self):
        data = load_knowledge()
        for question in ("Boleh bayar Gerak Gempur sekarang?", "Nak bayar bot WhatsApp guna kad kredit",
                         "Saya sudah transfer, sahkan resit transaksi", "Boleh bagi OTP untuk pembayaran?"):
            with self.subTest(question=question):
                reply = conversational_answer(question, data)
                self.assertIn("Pembayaran melalui telefon tidak dibenarkan", reply)
                self.assertIn("tidak boleh menerima bayaran atau mengesahkan transaksi", reply)

    def test_catalog_uses_published_information_without_inventing_hours(self):
        data = load_knowledge()
        self.assertIn("Gerak Gempur Cikgu Leea", answer("Apa produk?", data))
        self.assertIn("Sistem Leea", answer("Apa produk?", data))
        self.assertIn("Contact", answer("Macam mana nak beli?", data))
        self.assertEqual(answer("Waktu operasi?", data), "Waktu operasi belum disahkan.")
        self.assertIn("produk berasingan", answer("Info Gerak Gempur Cikgu Leea", data))
        self.assertIn("harga semasa", answer("Nak beli Gerak Gempur Cikgu Leea", data))
        self.assertIn("mod AI/manusia", answer("Info Sistem Leea & Bot WhatsApp", data))
        self.assertIn("jika akses serta sambungan berfungsi", answer("Info Sistem Leea & Bot WhatsApp", data))
        self.assertIn("tempat versi 1 sudah penuh", answer("Info Gerak Gempur Cikgu Leea", data))
        self.assertIn("belum disahkan", answer("Nak beli Gerak Gempur Cikgu Leea", data))

    def test_pricing_is_isolated_per_system(self):
        data = load_knowledge()
        leea = answer("Harga bot WhatsApp?", data)
        school = answer("Harga Gerak Gempur?", data)
        calls = answer("Harga AI Call Center?", data)
        self.assertIn("setup RM149", leea)
        self.assertNotIn("RM39.90", leea)
        self.assertIn("RM39.90", school)
        self.assertIn("bayaran sekali", school)
        self.assertIn("Coming Soon", calls)
        self.assertIn("belum tersedia", answer("Nak beli AI Call Center", data))
        self.assertIn("Sistem mana", answer("Berapa harga?", data))
        self.assertIn("satu sistem", answer("Harga bot WhatsApp dan Gerak Gempur?", data))

    def test_only_uses_supplied_product_details(self):
        data = {"company_name": "Contoh", "products": [
            {"name": "Produk A", "description": "Penerangan sah", "how_to_buy": "Hubungi jualan"}
        ]}
        self.assertEqual(answer("Info Produk A", data), "Penerangan sah")
        self.assertEqual(answer("Nak beli Produk A", data), "Hubungi jualan")
        self.assertIn("Produk A", answer("Berapa harga?", data))
        self.assertIn("belum disahkan", answer("Harga Produk A?", data))

    def test_conversational_persona_preserves_facts_and_uncertainty(self):
        data = load_knowledge()
        self.assertIn("pembantu maya", conversational_answer("Hai", data))
        self.assertIn("Leea Bot", conversational_answer("Hai", data))
        self.assertTrue(conversational_answer("Harga Gerak Gempur?", data).startswith("Baik, saya bantu jelaskan."))
        self.assertIn("RM39.90", conversational_answer("Harga Gerak Gempur?", data))
        self.assertNotIn("RM130/bulan", conversational_answer("Harga Gerak Gempur?", data))
        self.assertIn("Coming Soon", conversational_answer("Harga AI Call Center?", data))
        self.assertIn("Sistem mana", conversational_answer("Berapa harga?", data))
        self.assertIn("tak nak main agak-agak", conversational_answer("Ada integrasi satelit?", data))

    def test_gaya_bahasa_melayu_malaysia(self):
        data = load_knowledge()
        samples = [conversational_answer(q, data) for q in (
            "Hai", "Apa produk?", "Berapa harga?", "Harga Gerak Gempur?",
            "Harga bot WhatsApp dan Gerak Gempur?", "Ada integrasi satelit?",
        )]
        self.assertIn("Nak tanya", samples[0])
        self.assertIn("Boleh pilih", samples[4])
        for reply in samples:
            for term in ("silakan", "anda bisa", "nggak", "biaya", "hubungi kami segera"):
                self.assertNotIn(term, reply.casefold())


if __name__ == "__main__":
    unittest.main()