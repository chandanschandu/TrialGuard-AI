# try:
#     from .agent_base import BaseAgent
# except ImportError:
#     from agent_base import BaseAgent
# import json

# class ProtocolAgent(BaseAgent):
#     def __init__(self):
#         super().__init__("ProtocolAgent")
    
#     def generate_protocol(self, voice_input):
#         context = self.rag_retrieve(voice_input)
#         prompt = f"""
#         GENERATE CLINICAL TRIAL PROTOCOL from: "{voice_input}"
        
#         RAG context (FDA/CDSCO): {context}
        
#         Return ONLY a VALID JSON object with this exact structure:
#         {{
#             "objective": "Primary endpoint",
#             "patient_criteria": "Inclusion/exclusion",
#             "fda_score": 94,
#             "cdsco_score": 91,
#             "status": "Protocol generated successfully"
#         }}
#         Do not include any other text or markdown formatting.
#         """
#         result = self.call_bedrock(prompt)
try:
    from .agent_base import BaseAgent
except ImportError:
    from agent_base import BaseAgent

import json, re

class ProtocolAgent(BaseAgent):
    def __init__(self, name="ProtocolAgent"):
        super().__init__(name)

    def generate_protocol(self, user_input: str) -> str:
        """
        ADVANCED: 3-step chain-of-thought protocol generation.
        Step 1: Classify request → structured metadata
        Step 2: Targeted dual RAG (FDA + CDSCO + PubMed India)
        Step 3: Generate fully-quantified, India-first protocol
        """
        # ── Step 1: Intent classification ──────────────────────────────────
        classify_prompt = f"""
Extract clinical trial metadata from this request. Return ONLY valid JSON, no markdown:
REQUEST: "{user_input}"
{{
  "disease_area": "exact disease name",
  "phase": "Phase 1/2/3/4",
  "primary_population": "specific patient description",
  "intervention_type": "drug|device|behavioral|diagnostic",
  "india_specific_concern": "key India-relevant factor"
}}"""
        try:
            meta = json.loads(self.call_bedrock(classify_prompt))
        except Exception:
            meta = {"disease_area": "unspecified", "phase": "Phase 2",
                    "primary_population": user_input[:120], "intervention_type": "drug",
                    "india_specific_concern": "general Indian population"}

        disease    = meta.get("disease_area", "unspecified")
        phase      = meta.get("phase", "Phase 2")
        population = meta.get("primary_population", "Indian adults")
        india_note = meta.get("india_specific_concern", "")
        proto_id   = f"TG-{re.sub(r'[^A-Z]','',disease.upper())[:4]}-{phase.replace(' ','')}-2024"

        # ── Step 2: Targeted RAG ────────────────────────────────────────────
        fda_ctx    = self.rag_retrieve(f"FDA 21 CFR 312 {disease} {phase} protocol requirements", top_k=3)
        cdsco_ctx  = self.rag_retrieve(f"CDSCO Schedule Y India {disease} new drugs clinical trials", top_k=3)
        pubmed_ctx = self.rag_retrieve(f"{disease} India epidemiology prevalence clinical outcomes", top_k=2)

        # ── Step 3: Full protocol generation ───────────────────────────────
        prompt = f"""You are TrialGuard AI — India's most advanced clinical trial protocol designer.
Generate a COMPLETE, PUBLICATION-QUALITY protocol compliant with BOTH FDA 21 CFR Part 312 AND CDSCO Schedule Y 2019.

REQUEST: {user_input}
DISEASE: {disease} | PHASE: {phase} | POPULATION: {population}
INDIA NOTE: {india_note}

FDA RAG CONTEXT: {fda_ctx or 'Apply standard 21 CFR 312.23 requirements'}
CDSCO RAG CONTEXT: {cdsco_ctx or 'Apply CDSCO Schedule Y 2019 standard requirements'}
INDIA EPIDEMIOLOGY: {pubmed_ctx or 'Use known India disease burden data'}

RULES:
- Every field must be SPECIFIC and QUANTIFIED (no placeholders like "as appropriate")
- Include actual clause numbers from FDA 21 CFR and CDSCO Schedule Y
- Sample sizes must include power calculation with India-specific dropout rate (~20-25%)
- Include at least 3 India-specific elements (regional sites, local comorbidities, language ICF)

Return ONLY this JSON (no markdown, no preamble):
{{
  "title": "Full formal trial title with drug class, indication, phase",
  "protocol_id": "{proto_id}",
  "objective": {{
    "primary": "Primary objective with SPECIFIC measurable endpoint and timeframe",
    "secondary": ["Secondary objective 1 with metric", "Secondary objective 2 with metric", "Exploratory objective"],
    "india_context": "Why this matters uniquely for Indian population with epidemiological data"
  }},
  "patient_criteria": {{
    "inclusion": [
      "Age XX-YY years (justified by India epidemiology for {disease})",
      "Specific biomarker threshold with India-norm reference",
      "Minimum 6-month prior standard care documented at Indian site",
      "Willing to provide written informed consent in regional language"
    ],
    "exclusion": [
      "Severe renal impairment (eGFR < 30 mL/min/1.73m²)",
      "Active TB or prior anti-TB therapy within 12 months (India-specific)",
      "Pregnancy or breastfeeding per CDSCO Schedule Y Appendix XI",
      "Prior participation in clinical trial within 30 days"
    ],
    "sample_size": {{
      "n": 200,
      "power": "90%",
      "alpha": "0.05 (two-sided)",
      "effect_size": "Specify minimum clinically important difference",
      "dropout_adjustment": "25% inflation for India site dropout rate",
      "justification": "Full statistical rationale with formula"
    }}
  }},
  "trial_design": {{
    "type": "Randomized, double-blind, placebo-controlled, parallel-group",
    "randomization": "1:1 ratio, stratified by site and disease severity, block size 4",
    "blinding": "Double-blind with matched placebo; unblinding procedure documented",
    "duration_weeks": 24,
    "arms": [
      {{"arm": "Treatment", "n": 100, "dose": "Specific dose mg/kg or fixed dose", "frequency": "BID/QD", "route": "oral/IV/SC"}},
      {{"arm": "Placebo", "n": 100, "dose": "Matched placebo", "frequency": "BID/QD", "route": "oral/IV/SC"}}
    ],
    "sites": {{
      "count": 8,
      "india_regions": [
        "North: AIIMS New Delhi (high volume diabetes/cardiology)",
        "South: CMC Vellore, JIPMER Puducherry (lean diabetes phenotype)",
        "West: KEM Mumbai, B.J. Medical Ahmedabad",
        "East: AIIMS Bhubaneswar, NRS Medical Kolkata",
        "Central: AIIMS Bhopal"
      ],
      "rationale": "Multi-regional capture of genetic, dietary, and phenotypic diversity in Indian population"
    }},
    "india_logistics": "Regional language ICF (Hindi, Tamil, Marathi, Bengali), cold chain per WHO guidelines, rural site transport allowance per ICMR"
  }},
  "endpoints": {{
    "primary": "Primary endpoint: specific measurement (e.g. change from baseline HbA1c at Week 24, MMRM analysis)",
    "secondary": [
      "Fasting plasma glucose change at Week 12 and 24",
      "Body weight change (kg) at Week 24",
      "Incidence of hypoglycemic episodes (ADA 2023 definition)",
      "Safety: Treatment-emergent adverse events (TEAE) per CTCAE v5.0"
    ],
    "india_specific": "Quality of life via Hindi-validated WHO-5 Well-Being Index at baseline and Week 24"
  }},
  "statistical_plan": {{
    "primary_analysis": "MMRM for continuous primary endpoint; ANCOVA if single timepoint",
    "populations": "ITT (all randomized), PP (per-protocol ≥80% compliance), Safety (all dosed)",
    "interim_analysis": "Planned at 50% enrollment (DSMB review) per CDSCO Rule 25 requirement",
    "missing_data": "Multiple imputation (MI) for missing primary endpoint data",
    "multiplicity": "Hochberg step-up procedure for multiple secondary endpoints"
  }},
  "regulatory_map": {{
    "fda_sections": [
      "21 CFR 312.23(a)(6) — Full protocol content requirements",
      "21 CFR 312.23(a)(8) — Pharmacology and toxicology section",
      "21 CFR 312.32 — IND safety reporting (SAE within 15 days)"
    ],
    "cdsco_clauses": [
      "Schedule Y Rule 101 — Clinical trial application",
      "Schedule Y Appendix I — Contents of protocol",
      "Schedule Y Appendix V — Informed consent process",
      "Schedule Y Appendix XI — Special populations (women of childbearing potential)",
      "NDCT Rules 2019 Rule 25 — Serious adverse event reporting (24h)"
    ],
    "ethics": "IEC approval required per ICMR National Ethical Guidelines 2017; audit trail per GCP ICH E6 R2",
    "local_pi": "Mandatory Indian Principal Investigator with CDSCO-registered site per NDCT Rule 2019"
  }},
  "safety_monitoring": {{
    "dsmb": "5-member independent DSMB: 1 biostatistician, 1 Indian endocrinologist, 1 cardiologist, 1 ethicist, 1 patient advocate",
    "stopping_rules": "Pre-specified: >2x SAE rate in treatment vs control; O'Brien-Fleming alpha spending",
    "sae_reporting": "SAE to CDSCO within 24h, to Sponsor within 24h, to IEC within 7 days per NDCT Rules 2019 Rule 25",
    "safety_endpoints": "TEAE, SAE, SUSAR, laboratory abnormalities (CTCAE v5.0 Grade ≥3)"
  }}
}}"""

        raw = self.call_bedrock(prompt)
        # Validate + return clean JSON
        try:
            return json.dumps(json.loads(raw))
        except Exception:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            return match.group(0) if match else raw