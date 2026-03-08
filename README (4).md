# ⬡ TrialGuard AI
### India's First Autonomous Dual-Compliance Clinical Trial Engine

> *"TrialGuard is the only AI that autonomously improves its own protocol until it passes CDSCO + FDA compliance — then explains the trial to the patient in Hindi."*

![Track](https://img.shields.io/badge/Track-AI%20for%20Healthcare%20%26%20Life%20Sciences-blue)
![Hackathon](https://img.shields.io/badge/Hackathon-AI%20for%20Bharat%202026-green)
![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20Lambda%20%7C%20Polly-orange)
![Speed](https://img.shields.io/badge/Speed-1800×%20Faster-brightgreen)
![Cost](https://img.shields.io/badge/Cost-100×%20Cheaper-purple)
![PHI](https://img.shields.io/badge/PHI-Zero%20Real%20Data-red)

---

## 🇮🇳 What Is This?

TrialGuard AI takes a plain-language clinical trial description (e.g. *"Phase 2 anti-diabetic RCT in elderly Indians, AIIMS Delhi"*) and in ~60 seconds produces:

- ✅ A fully-structured **dual-compliant protocol** (FDA 21 CFR 312 + CDSCO Schedule Y simultaneously)
- ✅ **Clause-level compliance scores** with specific gap explanations and fixes
- ✅ A **3-round Autopilot** that self-patches its own protocol until both scores reach ≥92%
- ✅ A **10,000-patient synthetic Indian cohort** with India-realistic demographics and zero PHI
- ✅ **India site feasibility** across 8 real hospitals (AIIMS, CMC, KEM, JIPMER…) with GO/NO-GO
- ✅ **Bilingual patient education** — English + Hindi plain-language guide + FAQ + Polly Aditi TTS audio
- ✅ A **downloadable PDF report** uploaded directly to S3

---

## ⚡ Key Numbers

| Metric | Value | Context |
|--------|-------|---------|
| Protocol generation | ~60 seconds | vs. months with a CRO |
| Cost per protocol | ₹500–₹700 | vs. ₹50 lakh+ CRO (100× cheaper) |
| AWS cost per run | ₹40–₹70 | Bedrock + Lambda + S3 + Polly |
| AI agents | 8 autonomous | All running on AWS Bedrock |
| Compliance clauses | 25+ enforced | 13 FDA + 12 CDSCO simultaneously |
| Synthetic patients | 10,000 | Zero PHI — India demographics |
| ICF languages | 9 | Hindi, Tamil, Bengali, Telugu, Marathi +4 |
| India sites | 8 real hospitals | AIIMS, CMC, KEM, JIPMER, NRS, BJ Medical |
| Speed gain | **1800×** | Months of human work → 60 seconds |
| Market TAM | $76 Billion | SAM $1.8B India, SOM $120M academic |

---

## 🏗️ Architecture

```
User Input (text / voice)
        │
        ▼
┌──────────────────────────────────────────────────┐
│              AWS Lambda (FastAPI + Mangum)        │
│                                                  │
│  ProtocolAgent → FDAAgent ──┐                    │
│                              ├→ ImproverAgent    │
│  CDSCOAgent   → CDSCOAgent ─┘   (Autopilot)      │
│                                                  │
│  CohortAgent  → 10K synthetic Indian patients    │
│  FeasibilityAgent → India site GO/NO-GO          │
│  PatientAgent → English + Hindi + Polly TTS      │
│  PHIAgent     → PHI redaction                    │
│  PDFGenerator → ReportLab → S3 upload            │
└──────────────────────────────────────────────────┘
        │
        ▼
AWS S3 (PDF + MP3) → Public HTTPS URL
```

### AWS Services

| Service | Usage |
|---------|-------|
| **AWS Bedrock** | Claude 3 Sonnet (all 8 agents) + Titan Embeddings v2 (RAG) |
| **AWS Lambda** | Serverless compute for all 3 API endpoints |
| **AWS API Gateway** | REST API — POST /design-trial, /autopilot, /patient-summary |
| **AWS Polly (Aditi)** | Hindi neural TTS for patient audio guides |
| **AWS S3** | PDF + MP3 storage with public-read ACL |
| **AWS Comprehend** | Medical entity detection for PHI screening |
| **AWS Transcribe** | Speech-to-text for doctor voice input (roadmap) |
| **Amazon DynamoDB** | Session persistence + audit trail |
| **Pinecone** | Vector DB for FDA/CDSCO/PubMed regulatory RAG corpus |

---

## 🤖 The 8 AI Agents

| File | Agent | Responsibility |
|------|-------|----------------|
| `agent_base.py` | BaseAgent | Bedrock client, Titan Embeddings v2, Pinecone RAG, PHI-safe string handling |
| `protocol_agent.py` | ProtocolAgent | 3-step CoT: intent classification → dual RAG (FDA + CDSCO + PubMed) → full JSON protocol |
| `fda_agent.py` | FDAAgent | 21 CFR 312.23 clause-level scoring — 13 items, -8/-3 deductions, Grade A–D |
| `cdsco_agent.py` | CDSCOAgent | Schedule Y / NDCT Rules 2019 — 12 items, India-specific criteria, -7/-5/-15 deductions |
| `cohort_agent.py` | CohortAgent | 10K synthetic Indian patients, disease biomarkers, regional distribution, dropout scoring |
| `feasibility_agent.py` | FeasibilityAgent | Real India site DB — AIIMS/CMC/KEM/JIPMER, enrollment rate modeling, GO/NO-GO |
| `improver_agent.py` | ImproverAgent | 3-round autonomous loop: collect failures → patch → rescore → best-score guard |
| `patient_agent.py` | PatientAgent | English + Hindi plain-language guide + 8-question FAQ + CDSCO Rule 26 rights + Polly TTS |

---

## 🔄 Autopilot Mode — How It Works

```
Initial Protocol Generated
         │
         ▼
    Round 0: FDA 72 / CDSCO 72
         │
    ┌────┴────────────────────────────────┐
    │  ImproverAgent collects all gaps    │
    │  from both FDA + CDSCO agents       │
    │  → patches protocol JSON            │
    │  → rescores with both agents        │
    │  → best-score guard (never regress) │
    └────┬────────────────────────────────┘
         │
    Round 1: FDA 81 / CDSCO 84
         │
    Round 2: FDA 88 / CDSCO 91  ← Best saved ✅
         │
    Round 3: Stops early if both ≥ 92
```

The Autopilot **never regresses** — it keeps the best-scoring version and only accepts a new round if the combined score improves.

---

## 📁 Repository Structure

```
trialguard/
├── main.py                  # FastAPI — 3 Lambda endpoints
├── lambda_handler.py        # Mangum wrapper for AWS Lambda
├── agent_base.py            # BaseAgent + Bedrock + Pinecone RAG
├── protocol_agent.py        # Full protocol JSON generation
├── fda_agent.py             # FDA 21 CFR 312.23 compliance
├── cdsco_agent.py           # CDSCO Schedule Y compliance
├── cohort_agent.py          # 10K synthetic Indian cohort
├── feasibility_agent.py     # India site feasibility + GO/NO-GO
├── improver_agent.py        # 3-round Autopilot self-improvement
├── patient_agent.py         # Bilingual patient education + TTS
├── phi_agent.py             # PHI regex redaction
├── pdf_generator.py         # ReportLab PDF + S3 upload
├── tts_generator.py         # AWS Polly TTS — Hindi + English
├── app.py                   # Streamlit frontend UI
├── test_agents.py           # Full pipeline integration test
├── requirements.txt
└── .env.example
```

---

## 🚀 Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/trialguard-ai.git
cd trialguard-ai
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
cp .env.example .env
# Fill in:
# AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
# S3_BUCKET, PINECONE_API_KEY, PINECONE_INDEX
```

### 3. Run the Streamlit Frontend

```bash
streamlit run app.py
# Opens at http://localhost:8501
```

### 4. Run the FastAPI Backend

```bash
uvicorn main:app --reload --port 8000
```

### 5. Test the Live API

```bash
# Standard mode (~20s)
curl -X POST "https://t5whevmrmk.execute-api.us-east-1.amazonaws.com/design-trial" \
  -H "Content-Type: application/json" \
  -d '{"text": "Phase 2 anti-diabetic RCT, AIIMS Delhi", "language": "en"}'

# Autopilot mode (~90s, 3 rounds)
curl -X POST "https://t5whevmrmk.execute-api.us-east-1.amazonaws.com/autopilot" \
  -H "Content-Type: application/json" \
  -d '{"text": "Phase 2 anti-diabetic RCT, AIIMS Delhi", "language": "en", "max_rounds": 3}'

# Patient summary + Hindi TTS
curl -X POST "https://t5whevmrmk.execute-api.us-east-1.amazonaws.com/patient-summary" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123", "protocol": {}, "language": "hi"}'
```

---

## 🌐 API Endpoints

**Base URL:** `https://t5whevmrmk.execute-api.us-east-1.amazonaws.com`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/design-trial` | POST | Standard mode — full protocol in ~20 seconds |
| `/autopilot` | POST | 3-round self-improvement — targets ≥92% on both scores |
| `/patient-summary` | POST | Bilingual patient guide + FAQ + Polly Aditi audio |
| `/health` | GET | Returns status of all 8 agents |

### Example Response (Autopilot)

```json
{
  "success": true,
  "session_id": "a7f3",
  "elapsed_seconds": 58.3,
  "fda_score": 88,
  "fda_grade": "B+ (Ready with Minor Revisions)",
  "cdsco_score": 91,
  "cdsco_grade": "A (Ready for CDSCO Submission)",
  "feasibility": "High",
  "go_no_go": "GO",
  "autopilot": {
    "total_rounds_run": 2,
    "score_delta_fda": 16,
    "score_delta_cdsco": 19,
    "score_progression": [
      {"round": 0, "label": "Initial Generation", "fda_score": 72, "cdsco_score": 72},
      {"round": 1, "label": "Autopilot Round 1",  "fda_score": 81, "cdsco_score": 84},
      {"round": 2, "label": "Autopilot Round 2",  "fda_score": 88, "cdsco_score": 91}
    ]
  },
  "pdf_url": "https://your-bucket.s3.us-east-1.amazonaws.com/pdfs/protocol_a7f3.pdf",
  "audio_url": "https://your-bucket.s3.us-east-1.amazonaws.com/audio/dr_protocol_a7f3.mp3"
}
```

---

## 🏥 India Site Database

The `feasibility_agent.py` contains real enrollment data for 8 hospitals:

| Hospital | Region | Tier | GCP | Active Trials |
|----------|--------|------|-----|---------------|
| AIIMS New Delhi | North | 1 | ✓ | 95 |
| CMC Vellore | South | 1 | ✓ | 78 |
| KEM Hospital Mumbai | West | 1 | ✓ | 62 |
| JIPMER Puducherry | South | 1 | ✓ | 44 |
| AIIMS Bhopal | Central | 1 | ✓ | 28 |
| NRS Medical College Kolkata | East | 2 | — | 18 |
| BJ Medical College Ahmedabad | West | 2 | ✓ | 35 |
| AIIMS Bhubaneswar | East | 1 | ✓ | 22 |

---

## 🇮🇳 Why India Needs This

India has 8 critical gaps vs. global pharma infrastructure — TrialGuard solves all 8:

1. **No CDSCO-aware AI** — every existing tool is FDA-only
2. **Language barrier** — ICFs only in English; 80% of India doesn't read English
3. **Rural dropout** — 20–26% dropout in East/Central India sites; TrialGuard models this
4. **Lean diabetes phenotype** — Indian T2DM at BMI 23 vs. Western BMI 30; no tool adjusts for this
5. **No site matching** — sponsors manually identify Indian sites; TrialGuard automates it
6. **ICMR 2017 compliance** — tribal population consent procedures ignored by global tools
7. **CDSCO Rule 26** — mandatory injury compensation clauses missing from global templates
8. **Multi-lingual ICF** — 9 regional languages required; no tool generates these automatically

---

## 🆚 Competitive Positioning

| Platform | CDSCO | Hindi TTS | Autopilot | India Sites |
|----------|-------|-----------|-----------|-------------|
| **TrialGuard AI** | ✅ | ✅ | ✅ | ✅ |
| Medidata Rave | ❌ | ❌ | ❌ | ❌ |
| Veeva Vault | ❌ | ❌ | ❌ | ❌ |
| Oracle Clinical | ❌ | ❌ | ❌ | ❌ |

---

## 🗺️ Roadmap

### Phase 1 — Hackathon ✅ (Current)
- [x] 8-agent autonomous pipeline on AWS Lambda
- [x] CDSCO Schedule Y + FDA 21 CFR dual compliance
- [x] 3-round Autopilot self-improvement loop
- [x] Hindi patient education + Polly Aditi TTS
- [x] 10K synthetic Indian cohort (zero PHI)
- [x] Streamlit frontend + FastAPI backend

### Phase 2 — Post-Hackathon (3–6 months)
- [ ] E-CTR portal API for electronic trial registration
- [ ] AWS HealthLake integration for real EHR cohort matching
- [ ] Doctor voice input via AWS Transcribe
- [ ] 9-language ICF generation (Tamil, Bengali, Telugu...)

### Phase 3 — Scale (6–18 months)
- [ ] SaaS API for Indian pharma + CROs
- [ ] EMA (European Medicines Agency) module
- [ ] CDSCO Schedule M (GMP) integration
- [ ] Blockchain audit trail for protocol versioning

---

## 🔧 Environment Variables

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET=your-bucket-name
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=your_index_name
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

---

## ⚠️ Disclaimer

> Synthetic data only. Not for actual clinical use.
> FDA/CDSCO scores are AI-generated decision-support tools, not regulatory certification.
> Verify all requirements with qualified regulatory affairs professionals before any submission.

---

*Built for AI for Bharat 2026 · AWS Bedrock · CDSCO Schedule Y + FDA 21 CFR · Zero PHI · 🇮🇳*
