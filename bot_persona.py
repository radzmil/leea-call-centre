"""Persona Leea Bot; fakta sentiasa datang daripada bot_brain."""


def present(question, factual, knowledge):
    text = question.casefold().strip()
    if text in ("hai", "hi", "hello", "helo", "assalamualaikum", "salam"):
        return "Hai! Saya Leea Bot, pembantu maya Architech Systems. Nak tanya tentang sistem yang mana satu?"
    if factual.startswith("Harga berbeza"):
        return "Boleh, saya bantu semak. Setiap sistem ada harga sendiri. " + factual.split(". ", 1)[-1]
    if factual.startswith("Setiap sistem ada harga sendiri"):
        return "Boleh, saya bantu semak. " + factual
    if factual.startswith("Saya belum ada maklumat"):
        return "Maaf ya, saya tak nak main agak-agak. " + factual
    if not factual:
        return factual
    if factual.startswith(("Kalau", "Antara")):
        return "Baik, " + factual[0].lower() + factual[1:]
    return "Baik, saya bantu jelaskan. " + factual