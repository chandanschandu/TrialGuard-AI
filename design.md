# TrialGuard Voice - System Design Document

## 🏗️ High-Level Architecture

VOICE INPUT (Whisper STT)
↓
VOICE AGENT ROUTER (LangChain)
↓
┌─────────────────────────────┐
│ TRIAL GENERATION SWARM      │
│ - Cohort Generator          │
│ - Protocol Builder          │
│ - Compliance Validator      │
└─────────────────────────────┘
↓
COMPLIANCE AUDITOR (FDA/ICH-GCP)
↓
PDF PROTOCOL GENERATOR
↓
VOICE OUTPUT (ElevenLabs TTS)
↓
DOWNLOAD + VERBAL WALKTHROUGH

## 🔄 Process Flow Diagram

1. **Step 1: Voice Command**
   - "Design oncology trial for lung cancer"
2. **Step 2: STT Processing**
   - → Transcribe → Parse intent → Extract parameters
3. **Step 3: Trial Swarm Execution**
   - → Generate 10K synthetic patients
   - → Build protocol (PubMed RAG)
   - → Validate compliance (98% score)
4. **Step 4: Voice Response**
   - "Privacy validated ✓ Trial success rate: 68% ±4.2%"
5. **Step 5: PDF Export + Walkthrough**
   - "Protocol audit passed. Download or explain Section 7?"

## 🧠 Component Design

### 1. Voice Agent Router
```python
class VoiceTrialAgent:
    def route_intent(self, transcript):
        if "design trial" in transcript:
            return TrialGenerator()
        elif "explain section" in transcript:
            return ProtocolExplainer()
        elif "compliance" in transcript:
            return ComplianceAuditor()
```

### 2. Synthetic Patient Generator
- **Input**: "Elderly Indian diabetes patients"
- **Output**: 10K patients with:
  - Age: 65-85 (Indian demographics)
  - Comorbidities: Hypertension 42%, CKD 28%
  - PHI: Fully redacted/synthetic

### 3. Compliance Validator
- **Checks**:
  - FDA 21 CFR 312.23 (IND content)
  - ICH-GCP E6(R2) (protocol requirements)
  - Privacy: No PHI in outputs
  - Statistical validity: Power calculations
- **Score**: 98% (Green: Pass, Yellow: Warning, Red: Fail)

## 🎙️ Voice Design Specifications

### Custom Voice Persona: "Dr. Protocol"
- **Voice**: Deep, authoritative, medical gravitas
- **Accent**: Neutral Indian English (Delhi/Bengaluru)
- **Pace**: 140 WPM (deliberate, professional)
- **Tone**: Confident, reassuring, precise
- **Phrases**: "Compliance validated", "Protocol audit passed"

### Interactive Flow Examples
- **User**: "Design diabetes trial"
- **AI**: "Type 1 or Type 2? Any comorbidities?"
- **User**: "Type 2, elderly"
- **AI**: "Generating cohort... Privacy validated ✓"

## 📋 API Endpoints
- `POST /voice-trial`: Input: Audio file (Whisper STT) -> Output: Trial protocol JSON + PDF
- `GET /compliance-check/:section`: Returns: Verbal explanation + citations
- `POST /synthetic-patients`: Params: demographics, trial_type -> Returns: 10K patient cohort

## 🛡️ Error Handling & Fallbacks
- **Voice Recognition Fails**: Text input fallback
- **Compliance Fail**: Suggest fixes verbally
- **Network Issues**: Offline protocol cache
- **Unsupported Trial**: "Recommend consulting specialist"

## 🎯 Success Metrics
- **Demo Impact**: Judges hear live voice interaction
- **Researcher Fit**: Hands-free lab operation
- **Compliance Score**: 98%+ validation pass rate
- **Trial Speed**: 10x faster than manual design

*All data synthetic. Compliance informational only.*
