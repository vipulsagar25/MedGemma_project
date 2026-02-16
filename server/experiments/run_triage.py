import json
import os
from brain import TriageBrain
from rulengine import IMCIRuleEngine

# Load IMCI rules from JSON file (robust loading to avoid NameError)
IMCI_RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "imci_rules.json")
IMCI_RULES = []
try:
    with open(IMCI_RULES_PATH, "r"
    ) as f:
        imci_data = json.load(f)
        IMCI_RULES = imci_data.get("rules", [])
except FileNotFoundError:
    print(f"Warning: IMCI rules file not found: {IMCI_RULES_PATH}")
except Exception as e:
    print(f"Warning: failed to load IMCI rules: {e}")

# Example patient input
patient_data = {
    "age_months": 18,
    "fever": True,
    "respiratory_rate": 55,
    "chest_indrawing": True,
    "convulsions": False
}

symptoms_text = "18 month child with fever and fast breathing and chest indrawing"

brain = TriageBrain(
    persist_dir="./vector_store/imci_handbook_db",
    rules=IMCI_RULES
)

result = brain.analyze(patient_data, symptoms_text)

print(result)
