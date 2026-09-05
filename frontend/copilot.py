from ai.intent_parser import parse_intent
from ai.response_generator import verified_response

def classify_question(question: str):
    return parse_intent(question)
