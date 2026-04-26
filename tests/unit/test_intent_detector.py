from src.intent.intent_detector import IntentDetector


def test_detect_intent_semantic():
    detector = IntentDetector()
    intent = detector.detect_intent("What is machine learning?")
    assert intent == "semantic"


def test_detect_intent_relationship():
    detector = IntentDetector()
    intent = detector.detect_intent("How are Alice and Bob related?")
    assert intent == "relationship"


def test_detect_intent_hybrid():
    detector = IntentDetector()
    intent = detector.detect_intent("Explain how Alice and Bob are connected in the system")
    assert intent == "hybrid"
