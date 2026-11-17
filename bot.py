"""Lightweight NLP FAQ matching using NLTK."""

import re
from nltk.stem import PorterStemmer
from knowledge_base import FAQS

stemmer = PorterStemmer()
STOP_WORDS = {
    "a", "an", "the", "is", "are", "am", "i", "me", "my", "you", "your",
    "to", "for", "of", "in", "on", "and", "or", "do", "does", "how", "what",
    "can", "could", "please", "about", "it", "this", "that",
}

def tokenize(text):
    """Lowercase, tokenize, remove common words, and stem the remaining words."""
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {stemmer.stem(word) for word in words if word not in STOP_WORDS}

def answer_question(message, previous_topic=None):
    """Return an answer and topic label using keyword overlap."""
    user_tokens = tokenize(message)
    best_item = None
    best_score = 0

    for item in FAQS:
        faq_tokens = tokenize(item["question"] + " " + " ".join(item["keywords"]))
        if not faq_tokens:
            continue
        overlap = len(user_tokens & faq_tokens)
        # Normalize so longer FAQ entries do not win just because they have more words.
        score = overlap / max(1, len(user_tokens))
        if score > best_score:
            best_score, best_item = score, item

    # A short follow-up such as "what about weekends?" can refer to the previous topic.
    if best_score < 0.20 and previous_topic == "support_hours":
        if any(word in message.lower() for word in ("weekend", "saturday", "sunday")):
            return (
                "The listed support hours are Monday to Friday, 9 AM to 6 PM. "
                "Weekend support is not specified, so please email support@example.com to confirm.",
                "support_hours",
            )

    if best_item and best_score >= 0.20:
        topic = "support_hours" if "hours" in best_item["question"].lower() else best_item["question"]
        return best_item["answer"], topic

    return (
        "I’m not sure about that yet. Try asking about passwords, support hours, refunds, or creating an account.",
        previous_topic,
    )
