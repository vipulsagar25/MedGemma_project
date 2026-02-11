import json
from typing import List, Optional, Literal
from pydantic import BaseModel, ValidationError, Field

# --- 1. DEFINE THE SCHEMA (The Validation Layer) ---
# This ensures the "pure JSON" is never broken or missing fields.

class RuleCondition(BaseModel):
    logic: Literal["ANY", "ALL", "MIN_COUNT", "DEFAULT"]
    symptoms: List[str]
    min_count: Optional[int] = None # Only used if logic is MIN_COUNT

class ClassificationRule(BaseModel):
    classification: str
    color: Literal["PINK", "YELLOW", "GREEN"]
    severity_rank: int = Field(..., description="1 is highest (Pink), 3 is lowest (Green)")
    condition: RuleCondition
    treatments: List[str]

class MedicalDomain(BaseModel):
    id: str
    name: str
    trigger_question: str
    rules: List[ClassificationRule]

class IMCIKnowledgeBase(BaseModel):
    version: str = "1.0"
    source: str = "WHO IMCI Chart Booklet 2014"
    domains: List[MedicalDomain]

# --- 2. THE EXTRACTOR LOGIC ---
# In a real pipeline, this function would call an LLM API (Gemini/GPT)
# to parse the raw PDF text into dictionaries.
# Here, I simulate the extraction of the "Ear Problem" section (Page 9) as a demo.

def extract_ear_problem_data():
    """
    Simulates extracting Page 9 (Ear Problem) from the raw PDF text.
    """
    return {
        "id": "ear_problem",
        "name": "Ear Problem",
        "trigger_question": "Does the child have an ear problem?",
        "rules": [
            {
                "classification": "MASTOIDITIS",
                "color": "PINK",
                "severity_rank": 1,
                "condition": {
                    "logic": "ANY",
                    "symptoms": ["tender_swelling_behind_ear"]
                },
                "treatments": [
                    "Give first dose of appropriate antibiotic",
                    "Give first dose of paracetamol for pain",
                    "Refer URGENTLY to hospital"
                ]
            },
            {
                "classification": "ACUTE EAR INFECTION",
                "color": "YELLOW",
                "severity_rank": 2,
                "condition": {
                    "logic": "ANY",
                    "symptoms": [
                        "ear_pain",
                        "pus_draining_less_than_14_days"
                    ]
                },
                "treatments": [
                    "Give antibiotic for 5 days",
                    "Give paracetamol for pain",
                    "Dry the ear by wicking",
                    "Follow-up in 5 days"
                ]
            },
            {
                "classification": "CHRONIC EAR INFECTION",
                "color": "YELLOW",
                "severity_rank": 2,
                "condition": {
                    "logic": "ANY",
                    "symptoms": [
                        "pus_draining_14_days_or_more"
                    ]
                },
                "treatments": [
                    "Dry the ear by wicking",
                    "Treat with topical quinolone eardrops for 14 days",
                    "Follow-up in 5 days"
                ]
            },
            {
                "classification": "NO EAR INFECTION",
                "color": "GREEN",
                "severity_rank": 3,
                "condition": {
                    "logic": "DEFAULT",
                    "symptoms": []
                },
                "treatments": ["No treatment"]
            }
        ]
    }

# --- 3. THE MAIN PIPELINE ---

def main():
    print("⚙️  Starting Extraction Pipeline...")
    
    # Step A: Extract Raw Data (Simulated)
    raw_domain_data = extract_ear_problem_data()
    
    try:
        # Step B: Validate Data
        # This checks types, missing fields, and enum values (Pink/Yellow/Green)
        print("🔍 Validating Schema...")
        domain_obj = MedicalDomain(**raw_domain_data)
        
        # Create the full KB object
        full_kb = IMCIKnowledgeBase(domains=[domain_obj])
        
        # Step C: Export Pure JSON
        json_output = full_kb.model_dump_json(indent=2)
        
        # Save to file
        filename = "imci_extracted_data.json"
        with open(filename, "w") as f:
            f.write(json_output)
            
        print(f"✅ Success! Data validated and saved to '{filename}'")
        print("\n--- PREVIEW OF EXTRACTED DATA ---")
        print(json_output)

    except ValidationError as e:
        print(f"❌ Validation Failed!\n{e}")

if __name__ == "__main__":
    main()