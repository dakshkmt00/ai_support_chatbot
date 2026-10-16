"""Lightweight local NLP: normalization, tokenization, optional stemming, FAQ similarity and context."""
import json, re
from pathlib import Path

FAQ_PATH = Path(__file__).resolve().parent / "data" / "faqs.json"
try:
    from nltk.stem import PorterStemmer
    _stemmer = PorterStemmer()
except ImportError:
    _stemmer = None

with FAQ_PATH.open(encoding="utf-8") as f:
    FAQS = json.load(f)

STOPWORDS = {"a","an","the","is","are","am","to","of","for","in","on","at","it","i","you","me","my","do","does","can","could","would","please","what","how","when","where","and","or","with","your","we","our"}

def tokenize(text):
    words = re.findall(r"[a-z0-9']+", text.lower())
    words = [w for w in words if w not in STOPWORDS]
    if _stemmer:
        words = [_stemmer.stem(w) for w in words]
    return words

def similarity(query_tokens, candidate_tokens):
    q, c = set(query_tokens), set(candidate_tokens)
    if not q or not c:
        return 0.0
    overlap = len(q & c)
    # Dice coefficient rewards shared terms while discouraging very broad matches.
    return (2 * overlap) / (len(q) + len(c))

def best_faq(message):
    q = tokenize(message)
    best, score = None, 0.0
    for faq in FAQS:
        candidates = [faq["question"], *faq.get("examples", [])]
        local = max((similarity(q, tokenize(candidate)) for candidate in candidates), default=0.0)
        if local > score:
            best, score = faq, local
    return best, score

def generate_reply(message, history=None):
    normalized = message.lower().strip()
    if normalized in {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}:
        return "Hello! 👋 I’m your support assistant. Ask me about orders, returns, payments, delivery, or account help.", "greeting", 1.0
    if history:
        # A simple contextual follow-up: interpret short follow-ups using the most recent topic.
        recent_user = next((m for m in reversed(history) if m.get("role") == "user"), None)
        if recent_user and len(tokenize(message)) <= 3 and normalized in {"tell me more", "more details", "explain", "why", "and then"}:
            prior, prior_score = best_faq(recent_user["content"])
            if prior and prior_score >= 0.22:
                return prior["answer"] + "\n\nIf you tell me what part you need help with, I can narrow it down.", prior["intent"], prior_score
    faq, score = best_faq(message)
    if faq and score >= 0.22:
        return faq["answer"], faq["intent"], score
    return ("I’m sorry, I couldn’t confidently match that to my current FAQs. "
            "Try asking about order tracking, returns, refunds, payment methods, delivery, or account access. "
            "For a real support case, please contact the support team."), "fallback", score
