

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json, os, uuid, time, re
from dotenv import load_dotenv

from agents.protocol_agent    import ProtocolAgent
from agents.fda_agent         import FDAAgent
from agents.cdsco_agent       import CDSCOAgent
from agents.cohort_agent      import CohortAgent
from agents.feasibility_agent import FeasibilityAgent
from agents.phi_agent         import PHIAgent
from agents.improver_agent    import ImproverAgent
from agents.patient_agent     import PatientAgent
from pdf_generator            import generate_pdf
from tts_generator            import generate_tts

load_dotenv()
app = FastAPI(title="TrialGuard AI — India-First Clinical Trial Engine")

class TrialRequest(BaseModel):
    text: str
    language: str = "en"

class AutopilotRequest(BaseModel):
    text: str
    language: str = "en"
    max_rounds: int = 3

class PatientRequest(BaseModel):
    session_id: str
    protocol: dict
    language: str = "en"

def safe_parse(s) -> dict:
    if isinstance(s, dict): return s
    if not isinstance(s, str): s = str(s)
    s = s.strip()
    for fence in ("```json", "```"):
        if s.startswith(fence): s = s[len(fence):]
    if s.endswith("```"): s = s[:-3]
    s = s.strip()
    try: return json.loads(s)
    except Exception:
        match = re.search(r'\{.*\}', s, re.DOTALL)
        if match:
            try: return json.loads(match.group(0))
            except Exception: pass
    return {"error": "Could not parse JSON", "raw": s[:500]}

def extract_disease(protocol_json: dict, original_request: str = "") -> str:
    sources = [
        str(protocol_json.get("title", "")),
        str(protocol_json.get("objective", {}).get("primary", "") if isinstance(protocol_json.get("objective"), dict) else ""),
        str(protocol_json.get("objective", {}).get("india_context", "") if isinstance(protocol_json.get("objective"), dict) else ""),
    ]
    text = (" ".join(sources) + " " + original_request).lower()
    HINDI_MAP = {
        "hypertension":   ["उच्च रक्तचाप", "रक्तचाप", "hypertens", "blood pressure", "antihypertens"],
        "diabetes":       ["मधुमेह", "diabet", "hba1c", "glucose", "insulin"],
        "cancer":         ["कैंसर", "cancer", "oncol", "tumor", "carcinoma", "lymphoma"],
        "cardiovascular": ["हृदय", "cardio", "heart", "cardiac", "coronary"],
    }
    for disease, keywords in HINDI_MAP.items():
        if any(kw in text for kw in keywords):
            return disease
    return "diabetes"

def run_core_pipeline(text: str, language: str, session_id: str) -> dict:
    errors = {}
    pa            = ProtocolAgent()
    protocol_str  = pa.generate_protocol(text)
    protocol_json = safe_parse(protocol_str)
    proto_str     = json.dumps(protocol_json, indent=2) if isinstance(protocol_json, dict) else protocol_str
    fa         = FDAAgent("FDAAgent")
    ca         = CDSCOAgent("CDSCOAgent")
    fda_json   = safe_parse(fa.check_compliance(proto_str))
    cdsco_json = safe_parse(ca.check_compliance(proto_str))
    disease_keyword  = extract_disease(protocol_json, text)
    cohort_json      = safe_parse(CohortAgent("CohortAgent").generate_cohort(f"{disease_keyword} {text[:100]}"))
    feasibility_json = safe_parse(FeasibilityAgent("FeasibilityAgent").score_feasibility(proto_str))
    redacted         = PHIAgent().redact_phi(proto_str)
    return dict(protocol_json=protocol_json, fda_json=fda_json, cdsco_json=cdsco_json,
                cohort_json=cohort_json, feasibility_json=feasibility_json,
                redacted=redacted, disease_keyword=disease_keyword,
                fa=fa, ca=ca, errors=errors)

def build_response(sid, elapsed, pipe, pdf_url, audio_url,
                   override_protocol=None, override_fda=None,
                   override_cdsco=None, extra_fields=None) -> dict:
    p  = override_protocol or pipe["protocol_json"]
    f  = override_fda      or pipe["fda_json"]
    c  = override_cdsco    or pipe["cdsco_json"]
    fe = pipe["feasibility_json"]
    co = pipe["cohort_json"]
    dk = pipe["disease_keyword"]
    r = {
        "success": True, "session_id": sid, "elapsed_seconds": elapsed, "protocol": p,
        "fda_score": f.get("fda_score", 0), "fda_grade": f.get("grade", "N/A"),
        "fda_submission_readiness": f.get("submission_readiness", "N/A"),
        "fda_critical_gaps": f.get("critical_gaps", []),
        "fda_clauses_failed": f.get("clauses_failed", []),
        "cdsco_score": c.get("india_score", 0), "cdsco_grade": c.get("cdsco_grade", "N/A"),
        "cdsco_submission_status": c.get("cdsco_submission_status", "N/A"),
        "india_violations": c.get("india_violations", []),
        "unique_india_gaps": c.get("unique_india_gaps", []),
        "cohort": {
            "disease": dk, "cohort_size": co.get("cohort_size", 10000),
            "eligibility_rate_pct": co.get("eligibility_rate_pct", 0),
            "recommended_total_n": co.get("recommended_total_n", 200),
            "mean_dropout_pct": co.get("mean_dropout_pct", 0),
            "languages_required": co.get("languages_required", []),
            "india_specific_insights": co.get("india_specific_insights", []),
        },
        "feasibility": fe.get("feasibility", "Unknown"),
        "feasibility_score": fe.get("feasibility_score", 0),
        "enrollment_months_estimate": fe.get("enrollment_months_estimate", 0),
        "recommended_sites": fe.get("recommended_sites", []),
        "regional_gaps": fe.get("regional_gaps", []),
        "go_no_go": fe.get("go_no_go_recommendation", "GO WITH CONDITIONS"),
        "pdf_url": pdf_url, "audio_url": audio_url,
        "phi_preview": pipe["redacted"][:300] + "...",
        "india_optimized": True, "errors": pipe["errors"],
    }
    if extra_fields: r.update(extra_fields)
    return r

# ── ENDPOINT 1: Standard ──────────────────────────────────────────────────────
@app.post("/design-trial")
async def design_trial(request: TrialRequest):
    t0 = time.time(); sid = str(uuid.uuid4())[:8]
    pipe = run_core_pipeline(request.text, request.language, sid)
    pdf_url = None
    try:
        pdf_url = generate_pdf(pipe["protocol_json"], pipe["fda_json"], pipe["cdsco_json"], sid,
                               cohort_json=pipe["cohort_json"], feasibility_json=pipe["feasibility_json"])
    except Exception as e: pipe["errors"]["pdf_error"] = str(e)
    audio_url = None
    try:
        f, c, fe = pipe["fda_json"], pipe["cdsco_json"], pipe["feasibility_json"]
        tts = (f"Protocol complete. FDA {f.get('fda_score',0)}/100. CDSCO {c.get('india_score',0)}/100. "
               f"Feasibility {fe.get('feasibility','')}. Sites: {', '.join(fe.get('recommended_sites',[])[:3])}.")
        if request.language == "hi":
            tts = (f"प्रोटोकॉल तैयार है। FDA स्कोर {f.get('fda_score',0)}। CDSCO {c.get('india_score',0)}।")
        audio_url = generate_tts(tts, sid, lang=request.language)
    except Exception as e: pipe["errors"]["audio_error"] = str(e)
    return build_response(sid, round(time.time()-t0, 1), pipe, pdf_url, audio_url)

# ── ENDPOINT 2: Autopilot ─────────────────────────────────────────────────────
@app.post("/autopilot")
async def autopilot(request: AutopilotRequest):
    """
    Protocol Autopilot — autonomous 3-round improvement.
    Response includes autopilot.score_progression for UI progress bar.
    """
    t0 = time.time(); sid = str(uuid.uuid4())[:8]
    pipe = run_core_pipeline(request.text, request.language, sid)
    init_fda   = pipe["fda_json"].get("fda_score", 0)
    init_cdsco = pipe["cdsco_json"].get("india_score", 0)

    result = ImproverAgent().run_autopilot(
        protocol_json=pipe["protocol_json"], fda_json=pipe["fda_json"],
        cdsco_json=pipe["cdsco_json"], fda_agent=pipe["fa"], cdsco_agent=pipe["ca"],
        max_rounds=min(max(request.max_rounds, 1), 3),
    )
    pipe["protocol_json"] = result["improved_protocol"]
    pipe["fda_json"]      = result["final_fda_json"]
    pipe["cdsco_json"]    = result["final_cdsco_json"]

    final_fda   = result["final_fda_json"].get("fda_score", 0)
    final_cdsco = result["final_cdsco_json"].get("india_score", 0)

    pdf_url = None
    try:
        pdf_url = generate_pdf(result["improved_protocol"], result["final_fda_json"],
                               result["final_cdsco_json"], sid,
                               cohort_json=pipe["cohort_json"], feasibility_json=pipe["feasibility_json"])
    except Exception as e: pipe["errors"]["pdf_error"] = str(e)

    audio_url = None
    try:
        df, dc = final_fda - init_fda, final_cdsco - init_cdsco
        if request.language == "hi":
            tts = (f"ऑटोपायलट पूर्ण। {result['total_rounds_run']} राउंड। "
                   f"FDA {init_fda} से {final_fda}। CDSCO {init_cdsco} से {final_cdsco}।")
        else:
            tts = (f"Autopilot complete in {result['total_rounds_run']} rounds. "
                   f"FDA improved {init_fda} to {final_fda} (+{df}). "
                   f"CDSCO improved {init_cdsco} to {final_cdsco} (+{dc}). "
                   f"Status: {result['final_fda_json'].get('submission_readiness','ready')}.")
        audio_url = generate_tts(tts, sid, lang=request.language)
    except Exception as e: pipe["errors"]["audio_error"] = str(e)

    extra = {"autopilot": {
        "total_rounds_run": result["total_rounds_run"],
        "initial_fda_score": init_fda, "initial_cdsco_score": init_cdsco,
        "final_fda_score": final_fda, "final_cdsco_score": final_cdsco,
        "score_delta_fda": final_fda - init_fda,
        "score_delta_cdsco": final_cdsco - init_cdsco,
        "autopilot_success": result["autopilot_success"],
        "score_progression": [
            {"round": r["round"], "label": r["label"],
             "fda_score": r["fda_score"], "cdsco_score": r["cdsco_score"],
             "fda_grade": r["fda_grade"], "cdsco_grade": r["cdsco_grade"],
             "fixes_applied": r.get("fixes_applied", [])}
            for r in result["rounds"]
        ],
    }}
    return build_response(sid, round(time.time()-t0, 1), pipe, pdf_url, audio_url,
                          override_protocol=result["improved_protocol"],
                          override_fda=result["final_fda_json"],
                          override_cdsco=result["final_cdsco_json"],
                          extra_fields=extra)

# ── ENDPOINT 3: Patient Summary ───────────────────────────────────────────────
@app.post("/patient-summary")
async def patient_summary(request: PatientRequest):
    """Patient education — English + Hindi content + dual TTS audio."""
    t0 = time.time(); errors = {}
    summary = PatientAgent().generate_patient_summary(request.protocol, request.language)
    audio_en = audio_hi = None
    try:
        en = summary.get("patient_summary_english", {})
        tts_en = (f"Hello, I am Dr. Protocol from TrialGuard. "
                  f"{en.get('what_is_this_trial','')} {en.get('duration_simple','')} "
                  f"{en.get('will_it_cost_me','')} You can stop at any time. All treatment is free.")
        audio_en = generate_tts(tts_en[:800], request.session_id + "_pen", lang="en")
    except Exception as e: errors["audio_en"] = str(e)
    try:
        hi = summary.get("patient_summary_hindi", {})
        tts_hi = (f"नमस्ते। मैं डॉ. प्रोटोकॉल हूँ। "
                  f"{hi.get('what_is_this_trial','')} {hi.get('duration_simple','')} "
                  f"{hi.get('will_it_cost_me','')} आप किसी भी समय रोक सकते हैं।")
        audio_hi = generate_tts(tts_hi[:800], request.session_id + "_phi", lang="hi")
    except Exception as e: errors["audio_hi"] = str(e)
    return {
        "success": True, "session_id": request.session_id,
        "elapsed_seconds": round(time.time()-t0, 1),
        "patient_summary": summary,
        "audio_url_english": audio_en, "audio_url_hindi": audio_hi,
        "faq_count": len(summary.get("patient_faq", [])),
        "languages_available": ["English","Hindi","Tamil","Telugu","Kannada",
                                "Malayalam","Marathi","Bengali","Gujarati"],
        "regulatory_basis": "CDSCO Schedule Y Appendix V | ICMR 2017 | ICH E6 R2",
        "errors": errors,
    }

@app.get("/")
async def root():
    return {"message": "TrialGuard AI LIVE", "agents": 8,
            "endpoints": ["POST /design-trial", "POST /autopilot", "POST /patient-summary", "GET /health"]}

@app.get("/health")
async def health():
    return {"status": "ALL 8 AGENTS LIVE", "autopilot": "ACTIVE", "patient_mode": "ACTIVE"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)