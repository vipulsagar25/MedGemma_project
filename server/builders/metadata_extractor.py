import re
from collections import defaultdict


# ==============================
# CONFIGURABLE METADATA RULES
# ==============================

METADATA_RULES = {
    "age_group": {
    "0-2_months": [
        r"0\s*to\s*2\s*months",
        r"young\s*infant",
        r"less\s*than\s*2\s*months"
    ],
    "2m-5y": [
        r"2\s*months?\s*(to|up\s*to|-)\s*5\s*years?",
        r"child\s*(aged|age)?\s*2\s*months",
        r"children?\s*2\s*months?\s*(to|up\s*to|-)\s*5\s*years?"
    ],
    "general": []
},


    "symptom_category": {
        "cough": [
            r"cough",
            r"fast\s*breathing",
            r"chest\s*indrawing"
        ],
        "diarrhea": [
            r"diarrhea",
            r"dehydration",
            r"loose\s*stool"
        ],
        "fever": [
            r"fever",
            r"malaria",
            r"high\s*temperature"
        ],
        "ear": [
            r"ear\s*problem",
            r"ear\s*pain",
            r"ear\s*discharge"
        ],
        "nutrition": [
            r"malnutrition",
            r"weight",
            r"feeding\s*problem"
        ],
        "danger_sign": [
            r"danger\s*sign",
            r"convulsion",
            r"unconscious",
            r"lethargic",
            r"unable\s*to\s*drink"
        ],
        "general": []
    },

    "section_type": {
        "classification": [
            r"classify",
            r"classification"
        ],
        "treatment": [
            r"treat",
            r"give\s*antibiotic",
            r"oral\s*rehydration",
            r"ors"
        ],
        "referral": [
            r"refer\s*urgently",
            r"urgent\s*referral"
        ],
        "assessment": [
            r"assess",
            r"assessment"
        ]
    },

    "severity_hint": {
    "severe": [
        r"very\s*severe",
        r"severe\s*\w*",
        r"danger\s*sign",
        r"urgent",
        r"convulsion",
        r"lethargic",
        r"unconscious"
    ],
    "some": [
        r"some\s*dehydration",
        r"moderate"
    ],
    "none": [
        r"no\s*signs",
        r"no\s*dehydration"
    ],
    "unknown": []
}
# ==============================

}

# ==============================
# GENERIC MATCHING ENGINE
# ==============================

def match_category(text, category_rules):

    scores = defaultdict(int)

    for label, patterns in category_rules.items():
        for pattern in patterns:
            if re.search(pattern, text):
                scores[label] += 1

    if not scores:
        # return default if exists
        return list(category_rules.keys())[-1]

    # Return label with highest match score
    return max(scores, key=scores.get)


# ==============================
# MAIN METADATA EXTRACTOR
# ==============================

def extract_metadata(chunk):

    text = chunk.lower()

    metadata = {}

    for field, rules in METADATA_RULES.items():
        metadata[field] = match_category(text, rules)

    return metadata
