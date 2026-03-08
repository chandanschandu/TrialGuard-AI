# try:
#     from .agent_base import BaseAgent
# except ImportError:
#     from agent_base import BaseAgent

# class FDAAgent(BaseAgent):
#     def check_compliance(self, protocol_json):
#         context = self.rag_retrieve("21 CFR 312.23")
#         prompt = f"""
#         CHECK FDA 21 CFR 312.23 COMPLIANCE on this protocol:
#         {protocol_json}
        
#         RAG context: {context}
        
#         Return ONLY a VALID JSON object with this exact structure:
#         {{
#             "fda_score": 94,
#             "passed": ["section1", "section2"],
#             "failed": [{{"section": "X", "violation": "Y", "fix": "Z"}}],
#             "verbal_summary": "2-sentence explanation"
#         }}
#         Do not include any other text or markdown formatting.
#         """
#         return self.call_bedrock(prompt).strip()


try:
    from .agent_base import BaseAgent
except ImportError:
    from agent_base import BaseAgent

import json, re

class FDAAgent(BaseAgent):
    def __init__(self, name="FDAAgent"):
        super().__init__(name)

    # 21 CFR 312.23 mandatory checklist — evaluated against every protocol
    CHECKLIST = [
        ("312.23(a)(1)", "Sponsor name and address"),
        ("312.23(a)(2)", "Date, protocol serial number, phase"),
        ("312.23(a)(3)", "Investigator qualifications and credentials"),
        ("312.23(a)(4)", "Investigational plan — objectives and design"),
        ("312.23(a)(5)", "Investigator's brochure reference"),
        ("312.23(a)(6)", "Full protocol — objectives, design, methodology, statistical considerations, organization"),
        ("312.23(a)(6)(iii)", "Informed consent procedures"),
        ("312.23(a)(6)(iv)", "Safety monitoring and adverse event reporting"),
        ("312.23(a)(7)", "Chemistry, manufacturing, and controls (CMC)"),
        ("312.23(a)(8)", "Pharmacology and toxicology data"),
        ("312.32",       "IND safety reporting — SAE within 15 calendar days"),
        ("312.62",       "Investigator recordkeeping obligations"),
        ("312.66",       "Assurance of IRB review"),
    ]

    def check_compliance(self, protocol_json: str) -> str:
        """
        ADVANCED: Check every 21 CFR 312 clause explicitly.
        Return scored JSON with clause-level pass/fail + fixes.
        """
        rag_context = self.rag_retrieve(
            "FDA 21 CFR Part 312 IND application protocol requirements adverse event reporting", top_k=4
        )

        checklist_str = "\n".join(
            f"  - [{ref}] {desc}" for ref, desc in self.CHECKLIST
        )

        prompt = f"""You are a senior FDA regulatory affairs specialist with 15 years of IND experience.
Evaluate this clinical trial protocol against every mandatory 21 CFR Part 312 clause listed below.

━━━ PROTOCOL TO EVALUATE ━━━
{protocol_json}

━━━ FDA RAG CONTEXT ━━━
{rag_context or 'Apply full 21 CFR Part 312 IND regulations'}

━━━ MANDATORY CHECKLIST (evaluate EVERY item) ━━━
{checklist_str}

━━━ SCORING RULES ━━━
- Start at 100 points
- Each MISSING mandatory element: -8 points
- Each PRESENT but INCOMPLETE element: -3 points
- Each element PRESENT and COMPLIANT: 0 deduction
- Minimum score: 0

━━━ SCORING INSTRUCTIONS ━━━
You MUST evaluate the actual protocol content above and compute the real score.
DO NOT use a placeholder or example number.
Count exactly how many checklist items are PRESENT, INCOMPLETE, or MISSING in the protocol above.
Apply deductions: -8 per missing, -3 per incomplete. fda_score = 100 - total_deductions (min 0).
The score MUST reflect the actual content — a protocol missing 3 items scores ~76, missing 1 scores ~92, missing 5 scores ~60.

━━━ REQUIRED OUTPUT ━━━
Return ONLY valid JSON (no markdown):
{{
  "fda_score": <integer 0-100 computed from YOUR evaluation above — NOT a placeholder>,
  "grade": "<A/B/C/D grade with descriptor based on score: 90+=A, 80-89=B+, 70-79=B, 60-69=C, <60=D>",
  "clauses_passed": [
    {{"ref": "<actual clause ref>", "status": "PASS", "evidence": "<what in the protocol satisfies this>"}}
  ],
  "clauses_failed": [
    {{"ref": "<actual clause ref>", "status": "FAIL", "issue": "<specific gap found in this protocol>", "fix": "<specific actionable fix>", "deduction": <-8 or -3>}}
  ],
  "critical_gaps": ["<only issues that would result in FDA Clinical Hold — empty list if none>"],
  "verbal_summary": "State the ACTUAL score (not a placeholder), the single biggest strength found in THIS protocol, and the single most important fix needed.",
  "submission_readiness": "Ready for IND / Needs Minor Revision / Needs Major Revision / Clinical Hold Risk"
}}"""

        raw = self.call_bedrock(prompt)
        try:
            parsed = json.loads(raw)
            # Compute score from actual clauses_failed deductions as a sanity check
            if not isinstance(parsed.get("fda_score"), (int, float)):
                deductions = sum(
                    abs(c.get("deduction", 8))
                    for c in parsed.get("clauses_failed", [])
                    if isinstance(c, dict)
                )
                parsed["fda_score"] = max(0, 100 - deductions)
            # Assign grade based on computed score if missing/generic
            score = parsed["fda_score"]
            if not parsed.get("grade") or parsed["grade"] == "B+ (Likely Approvable with Minor Revisions)":
                if score >= 90:   parsed["grade"] = "A (Ready for IND Submission)"
                elif score >= 80: parsed["grade"] = "B+ (Likely Approvable with Minor Revisions)"
                elif score >= 70: parsed["grade"] = "B (Approvable with Revisions)"
                elif score >= 60: parsed["grade"] = "C (Significant Revisions Required)"
                else:             parsed["grade"] = "D (Major Deficiencies — Pre-IND Meeting Recommended)"
            return json.dumps(parsed)
        except Exception:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return match.group(0)
            return json.dumps({"fda_score": 70, "grade": "Parse error", "verbal_summary": raw[:300],
                               "clauses_passed": [], "clauses_failed": [], "critical_gaps": [],
                               "submission_readiness": "Needs Review"})