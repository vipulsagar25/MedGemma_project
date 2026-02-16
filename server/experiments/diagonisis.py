import json
import os

from brain import TriageBrain
from rulengine import IMCIRuleEngine
from langchain_chroma import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_ollama import ChatOllama


# -------------------------------
# LOAD RULES
# -------------------------------

IMCI_RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "imci_rules.json")
IMCI_RULES = []

try:
    with open(IMCI_RULES_PATH, "r") as f:
        imci_data = json.load(f)
        IMCI_RULES = imci_data.get("rules", [])
except Exception as e:
    print("❌ Failed to load IMCI rules:", e)


# -------------------------------
# TEST PATIENT DATA
# -------------------------------

patient_data = {
    "age_months": 18,
    "cough": True,
    "fever": True,
    "respiratory_rate": 55,
    "chest_indrawing": True,
    "convulsions": False
}

symptoms_text = "18 month child with fever and fast breathing and chest indrawing"


print("\n==============================")
print("STEP 1️⃣  RULE ENGINE TEST")
print("==============================")

rule_engine = IMCIRuleEngine(IMCI_RULES, patient_data)
rule_result = rule_engine.evaluate()

print("Rule Engine Output:")
print(json.dumps(rule_result, indent=2))


print("\n==============================")
print("STEP 2️⃣  VECTOR DB RETRIEVAL TEST")
print("==============================")

db = Chroma(
    collection_name="imci_handbook",
    persist_directory="./vector_store/imci_handbook_db",
    embedding_function=FastEmbedEmbeddings()
)

docs = db.similarity_search(symptoms_text, k=3)

print(f"Retrieved {len(docs)} documents.\n")

for i, doc in enumerate(docs, 1):
    print(f"--- Document {i} ---")
    print(doc.page_content[:400])
    print("\n")


print("\n==============================")
print("STEP 3️⃣  LLM ALONE TEST")
print("==============================")

llm = ChatOllama(
    model="gemma:2b",
    temperature=0
)

llm_response = llm.invoke(
    "Explain what severe pneumonia is in pediatric IMCI guidelines."
)

print("LLM Response:")
print(llm_response.content)


print("\n==============================")
print("STEP 4️⃣  FULL BRAIN INTEGRATION TEST")
print("==============================")

brain = TriageBrain(
    persist_dir="./vector_store/imci_handbook_db",
    rules=IMCI_RULES
)

full_result = brain.analyze(patient_data, symptoms_text)

print("Full Brain Output:")
print(full_result)
