"""Antara muka teks Leea Bot untuk demo CLI dan browser."""

from bot_brain import answer
from bot_company_profile import load_knowledge
from bot_engine import conversational_answer


if __name__ == "__main__":
    data = load_knowledge()
    print("Demo teks Architech Systems (taip 'keluar' untuk tamat).")
    while True:
        message = input("Anda: ").strip()
        if message.casefold() == "keluar":
            break
        print("Pembantu maya:", conversational_answer(message, data))