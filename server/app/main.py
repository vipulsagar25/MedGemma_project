from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .brain import TriageBrain # Importing the class we just made
import os
import json

app = FastAPI()

# Allow React to talk to this Server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store the AI
brain = None

# Input Data Structure
class PatientInput(BaseModel):
    symptoms: str

@app.on_event("startup")
async def startup():
    global brain
    # Point to the PDF in the 'data' folder
    # Go up one level (..) then into 'data'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(current_dir, "..", "data", "guidelines.pdf")
    
    try:
        brain = TriageBrain(pdf_path)
        print("✅ SERVER ONLINE: AI is ready.")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("💡 TIP: Did you put a PDF in server/data/guidelines.pdf?")

@app.post("/analyze")
async def analyze_patient(data: PatientInput):
    if not brain:
        return {"error": "Brain not loaded"}
    
    # Get raw string from AI
    raw_response = brain.analyze(data.symptoms)
    
    # Parse it into real JSON
    try:
        return json.loads(raw_response)
    except:
        return {"error": "Failed to parse JSON", "raw": raw_response}