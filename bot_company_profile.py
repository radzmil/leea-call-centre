"""Profil setempat bagi satu klien."""
import json
from pathlib import Path

KNOWLEDGE_PATH = Path(__file__).with_name("knowledge.json")


def load_knowledge(path=KNOWLEDGE_PATH):
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict) or not isinstance(data.get("products"), list):
        raise ValueError("knowledge.json mesti mengandungi objek dan senarai products")
    if any(not isinstance(p, dict) for p in data["products"]):
        raise ValueError("Setiap produk mesti objek")
    return data