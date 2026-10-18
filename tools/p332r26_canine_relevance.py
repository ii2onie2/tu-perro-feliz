#!/usr/bin/env python3
"""Conservative canine-topic gate for UNAPPROVED editorial candidates.

A passed topic is *not* fact-checked, medically reviewed, or publishable.
"""
import re
import unicodedata


def _fold(value):
    raw = unicodedata.normalize("NFKD", value.casefold())
    return "".join(ch for ch in raw if not unicodedata.combining(ch))


_CANINE = re.compile(r"\b(?:perros?|perrit[oa]s?|cachorros?|canin[oa]s?|galgos?|labradores?|pastores? alemanes?)\b")
_HIGH_RISK = re.compile(
    r"\b(?:acupuntura|acupuncture|quimioterapia|tratamientos?|terapias?|"
    r"diagnostic[oa]|medicamentos?|dosis|curas?|medicina alternativa|"
    r"enfermedades?|cancer|infecciones?|cirugias?|operaciones?)\b"
)


def rejection_reason(topic):
    """Return a rejection code or None. Never return editorial approval."""
    if not isinstance(topic, str) or not (3 <= len(topic.strip()) <= 240):
        return "DOG_EMPTY_OR_INVALID_TOPIC"
    folded = _fold(topic.strip())
    if not _CANINE.search(folded):
        return "DOG_CANINE_RELEVANCE_NOT_ESTABLISHED"
    if _HIGH_RISK.search(folded):
        return "DOG_MEDICAL_CLAIM_REQUIRES_SPECIALIST_REVIEW"
    return None
