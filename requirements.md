# TrialGuard Voice - Requirements Document
*Built for Healthcare AI Hackathon 2026*

## 🎯 Functional Requirements

### Core Features (MVP)
- **VOICE INPUT**: "Design diabetes trial for elderly Indian patients"
- **SYNTHETIC PATIENT COHORT**: Generate 10K compliant patients
- **COMPLIANCE VALIDATION**: FDA 21 CFR 312.23 + ICH-GCP checks
- **VOICE OUTPUT**: "Trial ready. Compliance score: 98%"
- **PDF EXPORT**: Auto-generate compliant protocol

### Voice-Specific Requirements
- ✅ Multi-accent Indian English (custom TTS)
- ✅ "Dr. Protocol" medical persona voice
- ✅ Interactive clarification questions
- ✅ Compliance narration (PHI redacted alerts)
- ✅ Hands-free lab operation

## 🛠 Technical Requirements

### Backend Stack
- Lyzr Agent Framework (trial generation)
- LangChain (voice routing + RAG)
- Whisper (speech-to-text)
- ElevenLabs (custom TTS - free tier)
- PubMed API (protocol research)
- MongoDB (synthetic patient store)

### Frontend Stack
- Streamlit (voice UI)
- HTML5 Web Speech API (fallback)
- PDFKit (protocol export)

### Compliance Requirements
- ✅ Synthetic data only (no real PHI)
- ✅ FDA 21 CFR Part 11 audit trail
- ✅ ICH-GCP protocol validation
- ✅ Privacy validation scoring
- ✅ Informational only (not legal advice)

## 📊 Performance Requirements
- **Response Time**: <5s for trial generation
- **Voice Latency**: <1s round-trip
- **Compliance Score**: >95% pass rate
- **Patient Cohort**: 10K synthetic patients
- **Supported Trials**: Oncology, Diabetes, Cardiology

## 🔒 Security & Compliance
- All data synthetic/public domain
- No patient health information stored
- Compliance explanations informational
- Clear limitation disclaimers
