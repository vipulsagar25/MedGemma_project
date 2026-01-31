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
        prompt = f"""
        You are a Clinical AI Assistant.
        
        TASK: Analyze these symptoms based ONLY on the provided GUIDELINES.
        
        GUIDELINES (Truth):
        {evidence}
        
        PATIENT SYMPTOMS:
        {symptoms}
        
        OUTPUT JSON ONLY:
        {{
            "risk_level": "High | Medium | Low",
            "suspected_condition": "Condition Name",
            "reasoning": "Why you think this (cite the guidelines)",
            "follow_up_questions": ["Question 1", "Question 2", "Question 3"]
        }}
        """
        
        print("🤔 AI is thinking...")
        return self.llm.invoke(prompt)