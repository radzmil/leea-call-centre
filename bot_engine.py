"""Aliran soalan -> fakta -> persona."""
from bot_brain import answer
from bot_persona import present


def conversational_answer(question, knowledge):
    return present(question, answer(question, knowledge), knowledge)