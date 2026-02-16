import json
from langchain_chroma import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_ollama import ChatOllama

from rulengine import IMCIRuleEngine


class TriageBrain:

    def __init__(self, persist_dir: str, rules: list):

        self.model_name = "gemma:2b"
        print(f"🧠 Initializing Brain with Model: {self.model_name}")

        # Persistent structured DB
        self.db = Chroma(
            collection_name="imci_handbook",
            persist_directory=persist_dir,
            embedding_function=FastEmbedEmbeddings()
        )

        # LLM used ONLY for:
        # - Structured extraction
        # - Explanation
        self.llm = ChatOllama(
            model=self.model_name,
            temperature=0
        )

        self.rules = rules

    # --------------------------------------------------
    # 1️⃣ STRUCTURED EXTRACTION FROM USER TEXT
    # --------------------------------------------------

    def extract_structured_data(self, text: str):
        prompt = f"""
Extract ONLY the clinical fields explicitly mentioned in the text.

Rules:
- Return ONLY fields that are directly mentioned.
- If a field is not mentioned, DO NOT include it in JSON.
- Do NOT assume values.
- Do NOT return null fields.
- Return minimal JSON.

Allowed fields:
- age_months
- cough
- fever
- respiratory_rate
- chest_indrawing
- convulsions

Text:
{text}

Return STRICT JSON with ONLY the mentioned fields and their values.
"""

        response = self.llm.invoke(prompt)

        try:
            return json.loads(response.content)
        except Exception:
            return {}

    # --------------------------------------------------
    # 2️⃣ MAIN INTERACTIVE TRIAGE STEP
    # --------------------------------------------------

    def triage_step(self, session, user_input: str):

        # Extract structured info from text
        extracted = self.extract_structured_data(user_input)

        # Update session patient data
        session.update_patient_data(extracted)

        print("🔎 Current Patient Data:", session.patient_data)

        # Run deterministic rule engine
        rule_engine = IMCIRuleEngine(self.rules, session.patient_data)
        rule_result = rule_engine.evaluate()

        print("🔎 Rule Engine Result:", rule_result)

        # If classification exists → final decision
        if rule_result["classifications"]:
            session.status = "complete"

            return self.generate_final_response(
                rule_result,
                session.patient_data,
                user_input
            )

        # If no match → ask for missing info
        missing = session.get_missing_fields()

        if missing:
            session.status = "incomplete"

            return {
                "status": "incomplete",
                "message": "More information required.",
                "questions": [
                    f"Please provide information about: {field}"
                    for field in missing
                ]
            }

        return {
            "status": "undetermined",
            "message": "Unable to classify based on available data."
        }

    # --------------------------------------------------
    # 3️⃣ FINAL RESPONSE WITH RETRIEVAL + EXPLANATION
    # --------------------------------------------------

    def generate_final_response(self, rule_result, patient_data, raw_text):

        risk_level = rule_result["overall_risk_level"]

        # Simple similarity retrieval
        docs = self.db.similarity_search(raw_text, k=5)
        evidence = "\n\n".join([doc.page_content for doc in docs])

        prompt = f"""
You are a pediatric clinical assistant.

The risk level has ALREADY been determined by a deterministic clinical rule engine.

RISK LEVEL: {risk_level}

CLASSIFICATIONS:
{rule_result["classifications"]}

PATIENT STRUCTURED DATA:
{patient_data}

IMCI GUIDELINES:
{evidence}

Explain the reasoning clearly.

Return STRICT JSON:

{{
    "risk_level": "{risk_level}",
    "explanation": "...",
    "follow_up_questions": ["...", "...", "..."]
}}
"""

        response = self.llm.invoke(prompt)

        try:
            parsed = json.loads(response.content)
        except Exception:
            parsed = {
                "risk_level": risk_level,
                "explanation": response.content.strip(),
                "follow_up_questions": []
            }

        # Safety enforcement
        parsed["risk_level"] = risk_level

        return parsed
