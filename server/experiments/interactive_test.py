from brain import TriageBrain
from session import TriageSession
import json
import os

# Load rules
with open("../data/imci_rules.json") as f:
    IMCI_RULES = json.load(f)["rules"]

brain = TriageBrain(
    persist_dir="./vector_store/imci_handbook_db",
    rules=IMCI_RULES
)

session = TriageSession()

print("Interactive Triage Started. Type 'exit' to stop.\n")

while True:
    user_input = input("User: ")

    if user_input.lower() == "exit":
        break

    result = brain.triage_step(session, user_input)

    print("System:", result)
