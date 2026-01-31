import os
import json
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.llms import Ollama

class TriageBrain:
    def __init__(self, pdf_path: str):
        # 1. SETUP MODEL
        # We use 'gemma:2b' for dev. For the competition, we swap this string.
        self.model_name = "gemma:2b" 
        print(f"🧠 Initializing Brain with Model: {self.model_name}")

        # 2. LOAD PDF (The Medical Knowledge)
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"⚠️ PDF not found at {pdf_path}")
            
        print("📚 Reading Guidelines... (This happens once)")
        loader = PyPDFLoader(pdf_path)
        docs = loader.load_and_split()
        
        # 3. CREATE MEMORY (Vector DB)
        # fastembed is great because it doesn't need a heavy GPU
        self.db = Chroma.from_documents(docs, FastEmbedEmbeddings())
        
        # 4. CONNECT TO OLLAMA
        self.llm = Ollama(
            model=self.model_name, 
            temperature=0, # 0 = Strict facts only
            format="json"  # Force JSON output for the App
        )

    def analyze(self, symptoms: str):
        # A. Find relevant pages in the PDF
        results = self.db.similarity_search(symptoms, k=3)
        evidence = "\n".join([doc.page_content for doc in results])
        
        # B. The Prompt
        # B. The Enhanced Prompt (Fixes the "High | Medium | Low" bug)
        prompt = f"""
        You are a Clinical Triage AI. 
        Analyze the patient based ONLY on the provided GUIDELINES.
        
        GUIDELINES:
        {evidence}
        
        PATIENT SYMPTOMS:
        {symptoms}
        
        INSTRUCTIONS:
        1. RISK LEVEL: Choose EXACTLY ONE from: "High", "Medium", or "Low".
        2. QUESTIONS: Suggest 3 specific "Yes/No" or check-box style questions to rule out danger.
        3. FORMAT: Output pure JSON.
        
        OUTPUT JSON:
        {{
            "risk_level": "High", 
            "suspected_condition": "Pneumonia",
            "reasoning": "Patient has fever and fast breathing which indicates...",
            "follow_up_questions": [
                "Does the child have chest indrawing?",
                "Is the child unable to drink or breastfeed?",
                "Has the child had convulsions?"
            ]
        }}
        """
        
        print("🤔 AI is thinking...")
        return self.llm.invoke(prompt)