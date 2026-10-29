"""Core 'intelligence': intent classification, priority scoring, routing and auto-resolution."""
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from training_data import TRAINING

# intent -> (team, base priority, auto-resolvable?)
INTENTS = {
    "password_reset":    ("IT Helpdesk",   "P3", True),
    "vpn_issue":         ("Network Ops",   "P3", True),
    "software_install":  ("Desktop Support", "P4", False),
    "hardware_issue":    ("Desktop Support", "P3", False),
    "access_request":    ("IAM Team",      "P4", False),
    "network_issue":     ("Network Ops",   "P2", False),
    "application_error": ("App Support",   "P2", False),
    "security_incident": ("Security SOC",  "P1", False),
}

SLA_HOURS = {"P1": 1, "P2": 4, "P3": 24, "P4": 72}

# Knowledge base used for instant self-service answers.
KNOWLEDGE_BASE = {
    "password_reset": "Reset your password at https://selfservice.example.com/reset. "
                      "Locked accounts unlock automatically after 15 minutes.",
    "vpn_issue": "1) Restart the VPN client. 2) Check your internet connection. "
                 "3) Update the client to the latest version. If it still fails, "
                 "reply and a network engineer will pick this up.",
}

URGENT_WORDS = {"urgent", "asap", "immediately", "critical", "down", "outage",
                "production", "everyone", "all users", "blocked", "deadline"}

CONFIDENCE_THRESHOLD = 0.35

_texts, _labels = zip(*TRAINING)
_model = make_pipeline(
    TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True),
    LogisticRegression(max_iter=1000, C=10),
).fit(_texts, _labels)


def classify_intent(text: str):
    """Return (intent, confidence). Low confidence -> 'general' for manual triage."""
    probs = _model.predict_proba([text])[0]
    idx = probs.argmax()
    intent, conf = _model.classes_[idx], float(probs[idx])
    if conf < CONFIDENCE_THRESHOLD:
        return "general", conf
    return intent, conf


def bump_priority(priority: str, steps: int) -> str:
    return f"P{max(1, int(priority[1]) - steps)}"


def process_request(title: str, description: str = "") -> dict:
    """Run the full automation pipeline for one service request."""
    text = f"{title}. {description}".strip()
    intent, conf = classify_intent(text)
    team, priority, auto = INTENTS.get(intent, ("Service Desk", "P4", False))

    lowered = text.lower()
    urgent = any(re.search(rf"\b{re.escape(w)}\b", lowered) for w in URGENT_WORDS)
    if urgent:
        priority = bump_priority(priority, 1)

    reply, status = None, "assigned"
    if auto and conf >= 0.5 and not urgent:
        reply, status = KNOWLEDGE_BASE[intent], "auto_resolved"

    return {
        "intent": intent,
        "confidence": round(conf, 2),
        "team": team,
        "priority": priority,
        "sla_hours": SLA_HOURS[priority],
        "status": status,
        "auto_reply": reply,
    }
