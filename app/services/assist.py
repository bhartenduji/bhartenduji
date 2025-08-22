from __future__ import annotations

import re
from typing import Dict, List


AMBIGUOUS_TERMS = [
    "etc",
    "thing",
    "always",
    "never",
    "stuff",
    "various",
    "kind of",
    "sort of",
]

BLOOM_VERB_MAP = {
    "Remember": ["define", "list", "recall", "identify", "state", "name"],
    "Understand": ["describe", "summarize", "explain", "classify", "discuss"],
    "Apply": ["apply", "use", "solve", "demonstrate", "calculate"],
    "Analyze": ["analyze", "compare", "contrast", "differentiate", "examine"],
    "Evaluate": ["evaluate", "justify", "critique", "argue", "assess"],
    "Create": ["create", "design", "formulate", "compose", "develop"],
}


def diagnose_stem(stem: str) -> Dict:
    s = stem.strip()
    issues: List[str] = []

    # ambiguous words
    lower = s.lower()
    for term in AMBIGUOUS_TERMS:
        if term in lower:
            issues.append(f"Contains ambiguous term: '{term}'")

    # overly long sentences
    if len(s) > 300:
        issues.append("Stem is very long; consider simplifying")

    # suggest bloom level based on first verb
    tokens = re.findall(r"[A-Za-z']+", lower)
    suggestion = None
    for level, verbs in BLOOM_VERB_MAP.items():
        for v in verbs:
            if tokens and tokens[0] == v:
                suggestion = level
                break
        if suggestion:
            break

    return {
        "issues": issues,
        "suggestedBloomLevel": suggestion,
    }