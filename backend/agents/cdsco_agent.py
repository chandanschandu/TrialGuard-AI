# try:
#     from .agent_base import BaseAgent
# except ImportError:
#     from agent_base import BaseAgent

# class CDSCOAgent(BaseAgent):
#     def check_compliance(self, protocol_json):
#         context = self.rag_retrieve("Schedule Y")
#         prompt = f"""
#         CHECK CDSCO SCHEDULE Y COMPLIANCE (INDIA ONLY):
#         {protocol_json}
        
#         RAG context: {context}
        
#         Return ONLY a VALID JSON object with this exact structure:
#         {{
#             "india_score": 91,
#             "schedule_y_passed": ["clause1.2", "clause4.3"],
#             "india_violations": [{{"clause": "II.3", "issue": "X", "fix": "Y"}}],
#             "verbal_summary": "Hindi-friendly explanation"
#         }}
#         Do not include any other text or markdown formatting.
#         """
#         return self.call_bedrock(prompt).strip()

try:
    from .agent_base import BaseAgent
except ImportError:
    from agent_base import BaseAgent

import json, re

class CDSCOAgent(BaseAgent):
    def __init__(self, name="CDSCOAgent"):
        super().__init__(name)

    # Schedule Y / NDCT Rules 2019 — key clauses
    SCHEDULE_Y_CHECKLIST = [
        ("Rule 101",         "Clinical trial application to CDSCO with Form CT-04"),
        ("Appendix I",       "Protocol content: title, objectives, design, population, procedures, statistical methods"),
        ("Appendix II",      "Investigator's Undertaking (Form CT-03) — Indian PI signature"),
        ("Appendix V",       "Informed consent form — vernacular language (Hindi + regional)"),
        ("Appendix VII",     "Investigator's Brochure content requirements"),
        ("Appendix XI",      "Special populations: women of childbearing potential, elderly, pediatrics"),
        ("Rule 25",          "SAE reporting: within 24 hours to sponsor + CDSCO; 14 days for non-fatal"),
        ("Rule 2019 Sec 3",  "Mandatory Indian Principal Investigator with registered site"),
        ("GCP-ICH E6 R2",    "Good Clinical Practice compliance — audit trail, monitoring plan"),
        ("ICMR 2017",        "National Ethical Guidelines — IEC approval, community consent for tribal populations"),
        ("Rule 26",          "Compensation to trial subjects for trial-related injury"),
        ("Rule 40",          "New Drug Application requirements if moving to Phase 3"),
    ]

    def check_compliance(self, protocol_json: str) -> str:
        """
        ADVANCED: Check every CDSCO Schedule Y / NDCT 2019 clause.
        This is the UNIQUE differentiator — no other AI tool does this.
        """
        rag_context = self.rag_retrieve(
            "CDSCO Schedule Y India clinical trial new drugs NDCT rules 2019 informed consent SAE", top_k=4
        )

        checklist_str = "\n".join(
            f"  - [{ref}] {desc}" for ref, desc in self.SCHEDULE_Y_CHECKLIST
        )

        prompt = f"""You are India's top regulatory affairs expert, specializing in CDSCO Schedule Y and the 
New Drugs and Clinical Trials Rules 2019 (NDCT Rules). You have led 50+ successful CDSCO submissions.

Evaluate this clinical trial protocol against every mandatory CDSCO requirement listed below.

━━━ PROTOCOL TO EVALUATE ━━━
{protocol_json}

━━━ CDSCO RAG CONTEXT ━━━
{rag_context or 'Apply CDSCO Schedule Y 2019 and NDCT Rules 2019 full requirements'}

━━━ CDSCO / SCHEDULE Y MANDATORY CHECKLIST ━━━
{checklist_str}

━━━ INDIA-SPECIFIC EVALUATION CRITERIA ━━━
1. Does the protocol address India-specific disease phenotypes? (e.g. lean T2DM, early-onset CVD)
2. Are multi-regional Indian sites included (North/South/East/West)?
3. Is regional language ICF specified (Hindi + at least 1 regional language)?
4. Is Indian PI co-investigator explicitly required?
5. Does SAE reporting meet 24-hour CDSCO requirement (stricter than FDA's 15 days)?
6. Is subject compensation for trial-related injury addressed (Rule 26 — mandatory in India)?
7. Are tribal/rural population consent procedures per ICMR 2017 addressed if applicable?

━━━ SCORING RULES ━━━
- Start at 100 points
- Each missing mandatory CDSCO element: -7 points
- Each missing India-specific element: -5 points  
- Critical violation (would cause CDSCO rejection): -15 points
- Elements fully compliant: 0 deduction

━━━ SCORING INSTRUCTIONS ━━━
You MUST evaluate the actual protocol content above and compute the real score.
DO NOT use a placeholder or example number.
Count exactly which CDSCO checklist items and India-specific criteria are PRESENT, INCOMPLETE, or MISSING.
Apply deductions: -7 per missing mandatory element, -5 per missing India-specific element, -15 per critical violation.
india_score = 100 - total_deductions (min 0).
The score MUST differ per protocol — a strong protocol with 1 gap scores ~85-93, one with 3 gaps scores ~71-79, one missing critical elements scores below 60.

Return ONLY valid JSON (no markdown):
{{
  "india_score": <integer 0-100 computed from YOUR evaluation — NOT a placeholder>,
  "cdsco_grade": "<A/B/C/D grade based on score: 90+=A, 80-89=B+, 70-79=B, 60-69=C, <60=D>",
  "schedule_y_passed": [
    {{"clause": "<actual clause>", "status": "PASS", "evidence": "<what in THIS protocol satisfies it>"}}
  ],
  "india_violations": [
    {{
      "clause": "<actual Schedule Y clause>",
      "issue": "<specific gap found in THIS protocol — not a generic example>",
      "fix": "<specific actionable fix for this protocol>",
      "severity": "HIGH / MEDIUM / LOW",
      "deduction": <-15, -7, or -5>
    }}
  ],
  "india_strengths": ["<specific strength found in THIS protocol>"],
  "unique_india_gaps": ["<gaps that are India-only — not caught by FDA check — specific to THIS protocol>"],
  "verbal_summary": "State the ACTUAL computed score, the single biggest India-specific strength in THIS protocol, and the single most important CDSCO fix needed.",
  "cdsco_submission_status": "Ready for Submission / Minor Revision Required / Major Revision Required / Pre-Submission Meeting Recommended"
}}"""

        raw = self.call_bedrock(prompt)
        try:
            parsed = json.loads(raw)
            # Compute score from actual deductions as sanity check
            if not isinstance(parsed.get("india_score"), (int, float)):
                deductions = sum(
                    abs(v.get("deduction", 7))
                    for v in parsed.get("india_violations", [])
                    if isinstance(v, dict)
                )
                parsed["india_score"] = max(0, 100 - deductions)
            # Assign grade based on actual score if it's the default placeholder
            score = parsed["india_score"]
            if not parsed.get("cdsco_grade") or "Submission Ready with Minor Additions" in parsed.get("cdsco_grade", ""):
                if score >= 90:   parsed["cdsco_grade"] = "A (Ready for CDSCO Submission)"
                elif score >= 80: parsed["cdsco_grade"] = "B+ (Submission Ready with Minor Additions)"
                elif score >= 70: parsed["cdsco_grade"] = "B (Minor Revisions Required)"
                elif score >= 60: parsed["cdsco_grade"] = "C (Significant Revisions Required)"
                else:             parsed["cdsco_grade"] = "D (Major Deficiencies — Pre-Submission Meeting Required)"
            return json.dumps(parsed)
        except Exception:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return match.group(0)
            return json.dumps({"india_score": 70, "cdsco_grade": "Parse error",
                               "verbal_summary": raw[:300], "schedule_y_passed": [],
                               "india_violations": [], "india_strengths": [], "unique_india_gaps": [],
                               "cdsco_submission_status": "Needs Review"})