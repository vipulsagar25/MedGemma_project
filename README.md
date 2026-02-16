
# 🧠 MedGemma – IMCI Clinical Decision Support (Work in Progress)

## 🚀 Overview

MedGemma is a pediatric clinical decision-support assistant built around the IMCI (Integrated Management of Childhood Illness) framework.

The goal is to design a clinical co-pilot that supports healthcare workers during child assessment by:
- Guiding structured triage
- Highlighting danger signs
- Retrieving relevant IMCI guideline sections
- Providing explainable decision support

This project explores hybrid AI architecture combining:
- Deterministic rule systems
- Retrieval-Augmented Generation (RAG)
- Local LLM inference

> ⚠️ **Important:**
> This is an experimental research project and is **NOT** intended for real clinical deployment.

---

## 🏗 Architecture

The system was designed as a multi-layer clinical AI assistant:

### 1️⃣ Retrieval Layer (RAG)
- IMCI handbook embedded using FastEmbed
- Hybrid chunking strategy (recursive + overlap)
- Chroma vector database
- Top-k similarity retrieval

### 2️⃣ Rule Engine (Experimental)
- Deterministic rule evaluator
- JSON-based rule definitions
- Age-based thresholds
- Priority-based aggregation
> This layer is currently under research and not clinically validated.

### 3️⃣ LLM Layer
- Local inference via Gemma (2B)
- Structured JSON output enforcement
- Explanation generation based on retrieved context
- Strict prompt constraints to reduce hallucination

---

## 📂 Project Structure

```
server/
├── app/
│   ├── brain.py
│   ├── rule_engine.py
│   ├── session.py
├── builders/
│   ├── build_vector_db.py
├── data/
│   ├── imci_handbook.pdf
│   ├── imci_rules.json
├── storage/
│   └── vector_store/
└── api/
    └── main.py
```

---

## 🧪 Current Status

- ✔ IMCI handbook processed into vector database
- ✔ Hybrid chunking implemented
- ✔ Structured extraction experiments
- ✔ Deterministic rule engine prototype
- ✔ FastAPI integration
- ✔ Local LLM inference

---

## 🚧 Pending

- Clinical validation of rules
- Complete flowchart-to-rule conversion
- Formal evaluation framework
- False positive / false negative analysis
- Edge case testing suite

---

## 🎯 Research Focus

The core research question explored in this project:

> Can a hybrid deterministic + RAG-based architecture provide reliable IMCI decision support without fully autonomous diagnosis?

Key challenges identified:
- Rule completeness validation
- Hallucination mitigation
- Emergency case prioritization
- True negative vs false positive balance
- Threshold fidelity from guideline extraction

---

## ⚠️ Disclaimer

This system:
- Does **NOT** replace a clinician
- Is **NOT** validated for medical use
- Is a research prototype for exploring clinical AI architectures
- Use strictly for educational or experimental purposes.

---

## 🛣 Roadmap

Future directions:
- Formal rule graph extraction from IMCI flowcharts
- Structured decision tree modeling
- Emergency override safety layer
- Model benchmarking (Gemma vs Groq vs larger models)
- Clinical expert review for rule accuracy
- Evaluation metrics for diagnostic reliability

---

## 🧠 Why This Project Matters

Healthcare AI systems are difficult because:
- Minor rule errors can lead to unsafe outputs
- LLM hallucinations are unacceptable in medical settings
- Deterministic logic must align exactly with clinical guidelines

This project documents an attempt to design a safer hybrid architecture rather than relying solely on generative AI.

---

## 🧑‍💻 Author Note

This is an evolving system.
The deterministic rule engine is incomplete and requires clinical validation before further development.

The long-term goal is to create a structured IMCI flowchart engine combined with explainable retrieval support.