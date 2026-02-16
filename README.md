
# MedGemma – A Clinical Thinking Partner for Child Health

## What's This About?

MedGemma is an experimental AI assistant designed to help healthcare workers assess sick children using the IMCI (Integrated Management of Childhood Illness) framework. Think of it as a knowledgeable colleague who can help you:

- Walk through a structured assessment
- Flag potentially serious warning signs
- Look up relevant IMCI guidelines quickly
- Explain why certain things matter
## How It Works Under the Hood

Under the surface, MedGemma combines three different approaches:

1. **Smart rule-based logic** – Deterministic rules that check specific symptoms and conditions
2. **Context-aware retrieval** – Searches the IMCI handbook to find relevant guidelines (RAG approach)
3. **Local AI reasoning** – Uses a small language model (Gemma 2B) to explain findings clearly

**A heads-up:** This is research-grade software. It's not ready for real patient care yet—treat it as an experimental exploration of how AI might support clinical decision-making safely.

---

## Architecture Overview

The system is built in three layers that work together:

### Layer 1: Knowledge Retrieval
We've embedded the entire IMCI handbook using FastEmbed and stored it in a vector database (Chroma). When you ask a question, the system searches for the most relevant guideline sections. This keeps answers grounded in official IMCI guidance.

### Layer 2: Rule-Based Decision Engine
A set of deterministic rules checks symptoms, age, and vital signs to flag potential concerns. These are defined in JSON and follow specific thresholds. *Note: This is still experimental and hasn't been clinically validated.*

### Layer 3: AI Explanations
A local copy of Gemma (a small language model) runs on-device to explain what the rules found and connect it back to the guidelines. We keep it on a tight leash with strict prompts to prevent it from making things up.

---

## Project Structure

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

## What's Done

- ✔ IMCI handbook converted to embeddings and stored
- ✔ Chunking and retrieval working
- ✔ Rule engine built and tested
- ✔ API endpoints set up with FastAPI
- ✔ Local model running without external calls

---

## What's Next (In Progress)

- Validate rules with actual clinicians
- Convert IMCI flowcharts into formal rules
- Build a proper testing framework
- Test for false alarms and missed cases
- Handle weird edge cases

---

## The Big Question We're Exploring

Can we build a system that stays reliable by combining rules and AI, without letting the AI make its own decisions?

This matters because:
- **Rules alone are rigid** – They can miss nuance
- **AI alone is risky in medicine** – It can confidently say wrong things
- **Combined thoughtfully** – We might get the best of both

The hardest parts so far:
- Getting the rules complete and accurate
- Keeping the AI from confabulating
- Knowing when something is an emergency
- Balancing false alarms vs. missed cases

---

## Please Read This

Let's be clear about what this is and isn't:

- **This is NOT a doctor.** It doesn't replace your clinical judgment.
- **This is NOT approved for patient care.** It's a research prototype.
- **This is a learning experiment.** We're exploring ideas, not deploying products.
- **Use it for learning only.** Try it in educational settings or controlled research.

If you use this with real patients without proper validation, that's on you—and it could hurt people.

---

## Where We Want to Go

- Extract rules directly from IMCI flowcharts
- Model everything as a formal decision tree
- Add emergency overrides and safety checks
- Benchmark different AI models
- Get real clinicians to review the rules
- Create proper benchmarks for accuracy and safety

---

## Why This Matters

Building trustworthy AI for medicine is genuinely hard:
- One small mistake in logic can cascade into bad advice
- AI models can sound confident while being completely wrong (hallucinations)
- Every rule must match what the guidelines actually say—no improvisation

Most AI hype focuses on just throwing big language models at problems. This project explores a different path: what if we combine rules and retrieval with careful AI oversight? Maybe that's safer.

---

## A Note From the Developer

This is work in progress. The rule engine is still rough around the edges and needs clinicians to poke holes in it.

Long-term, if this goes anywhere, it should become a proper engine that reads IMCI flowcharts directly and explains its reasoning clearly. That's the dream—a tool that thinks like a clinician, not like a startup.