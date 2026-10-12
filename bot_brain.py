"""Padankan pertanyaan dengan katalog yang disahkan."""
from bot_payment import payment_answer
from bot_sop import unknown_answer


def answer(question, knowledge):
    text = question.casefold().strip()
    name = knowledge.get("company_name") or "Syarikat kami"
    products = knowledge.get("products", [])
    if any(phrase in text for phrase in ("bayar", "pembayaran", "transfer", "pindahan bank", "kad kredit", "kad debit", "otp", "resit", "transaksi")):
        return payment_answer(knowledge)
    price_words = ("harga", "berapa", "kos", "bayaran", "yuran", "rm", "pakej")
    wants_price = any(word in text for word in price_words)
    matches = [p for p in products if any(alias.casefold() in text for alias in
               [p.get("name", "")] + p.get("aliases", []) if alias.strip())]
    if len(matches) > 1:
        return "Setiap sistem ada harga sendiri. Boleh pilih satu sistem yang nak ditanya?"
    if matches:
        product = matches[0]
        product_name = product["name"]
        if wants_price:
            return product.get("pricing", "").strip() or f"Harga {product_name} belum disahkan. Sila hubungi pasukan kami."
        if any(word in text for word in ("beli", "daftar", "langgan")):
            return product.get("how_to_buy", "").strip() or f"Cara membeli {product_name} belum disahkan. Sila hubungi pasukan kami."
        return product.get("description", "").strip() or f"Maklumat {product_name} belum disahkan. Sila hubungi pasukan kami."
    if wants_price:
        names = [p.get("name", "").strip() for p in products if p.get("name", "").strip()]
        return ("Harga berbeza mengikut sistem dan pakej. Sistem mana yang tuan/puan maksudkan: "
                + ", ".join(names) + "?") if names else "Saya belum ada maklumat harga yang disahkan."
    if any(word in text for word in ("beli", "daftar", "langgan")):
        contact = knowledge.get("contact_method", "").strip()
        return f"Kalau nak dapatkan produk {name}, {contact}" if contact else "Cara mendapatkan produk belum disahkan. Boleh hubungi pasukan kami."
    if any(word in text for word in ("waktu", "jam", "operasi")):
        return knowledge.get("business_hours", "").strip() or "Waktu operasi belum disahkan."
    if any(word in text for word in ("produk", "servis", "perkhidmatan")):
        names = [p.get("name", "").strip() for p in products if p.get("name", "").strip()]
        return "Antara sistem kami: " + ", ".join(names) + "." if names else "Senarai produk belum dimasukkan."
    if any(word in text for word in ("syarikat", "siapa", "tentang")):
        return knowledge.get("company_description", "").strip() or f"Nama syarikat kami ialah {name}. Penerangan lanjut belum disahkan."
    return unknown_answer()