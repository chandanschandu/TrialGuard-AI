try:
    from .agent_base import BaseAgent
except ImportError:
    from agent_base import BaseAgent

import json, re

class ImproverAgent(BaseAgent):
    """
    Autonomous Protocol Autopilot — 3-round self-improvement loop.
    
    Round 1: Identify ALL failures from FDA + CDSCO agents
    Round 2: Patch every failing section → rescore
    Round 3: Final cleanup of any remaining gaps → final score
    
    Demo moment: Score rises from red → yellow → green autonomously.
    """

    def __init__(self, name="ImproverAgent"):
        super().__init__(name)

    def _collect_all_gaps(self, fda_json: dict, cdsco_json: dict) -> dict:
        """Collect every failure from both compliance agents into one structured list."""
        fda_failures = []
        for item in fda_json.get("clauses_failed", []):
            if isinstance(item, dict):
                fda_failures.append({
                    "source": "FDA 21 CFR",
                    "ref":   item.get("ref", ""),
                    "issue": item.get("issue", ""),
                    "fix":   item.get("fix", ""),
                    "deduction": item.get("deduction", -8),
                })
        for gap in fda_json.get("critical_gaps", []):
            fda_failures.append({
                "source": "FDA CRITICAL",
                "ref":    "Critical Hold Risk",
                "issue":  str(gap),
                "fix":    f"Resolve critical gap: {str(gap)[:200]}",
                "deduction": -15,
            })

        cdsco_failures = []
        for item in cdsco_json.get("india_violations", []):
            if isinstance(item, dict):
                cdsco_failures.append({
                    "source":   "CDSCO Schedule Y",
                    "ref":      item.get("clause", ""),
                    "issue":    item.get("issue", ""),
                    "fix":      item.get("fix", ""),
                    "severity": item.get("severity", "MEDIUM"),
                    "deduction": item.get("deduction", -7),
                })
        for gap in cdsco_json.get("unique_india_gaps", []):
            cdsco_failures.append({
                "source":   "CDSCO India-Only",
                "ref":      "India-Specific",
                "issue":    str(gap),
                "fix":      f"Address India-specific gap: {str(gap)[:200]}",
                "deduction": -5,
            })

        return {
            "fda_failures":   fda_failures,
            "cdsco_failures": cdsco_failures,
            "total_failures": len(fda_failures) + len(cdsco_failures),
            "fda_score_before":   fda_json.get("fda_score", 0),
            "cdsco_score_before": cdsco_json.get("india_score", 0),
        }

    def _patch_protocol(self, protocol_json: dict, gaps: dict, round_num: int) -> dict:
        """
        Ask the LLM to patch ONLY the failing sections.
        Returns an updated protocol_json dict.
        """
        fda_fixes   = gaps.get("fda_failures", [])
        cdsco_fixes = gaps.get("cdsco_failures", [])

        if not fda_fixes and not cdsco_fixes:
            print(f"[ImproverAgent] Round {round_num}: No gaps to fix — protocol already optimal.")
            return protocol_json

        fda_fix_str   = json.dumps(fda_fixes,   indent=2)
        cdsco_fix_str = json.dumps(cdsco_fixes, indent=2)

        prompt = f"""You are TrialGuard Protocol Autopilot — Round {round_num} of autonomous improvement.

You previously generated this clinical trial protocol:
{json.dumps(protocol_json, indent=2)[:3000]}

━━━ FDA 21 CFR FAILURES TO FIX ━━━
{fda_fix_str}

━━━ CDSCO SCHEDULE Y FAILURES TO FIX ━━━
{cdsco_fix_str}

━━━ YOUR TASK ━━━
Patch the protocol to fix EVERY failure listed above.
- For FDA failures: add the missing sections/content specified in each "fix" field
- For CDSCO failures: add India-specific content as specified in each "fix" field
- Keep ALL existing content that was already correct — only ADD or IMPROVE failing sections
- Be specific and quantified — no placeholders

Key additions typically needed:
- sponsor: Add "Sponsor: [Trial Sponsor Organization], Address: [India/Global address]"
- investigator_qualifications: Add PI credentials (MD/DM/PhD, subspecialty, years experience)
- investigator_brochure: Add IB reference version and date
- cmc_summary: Add drug formulation, manufacturing site, stability data reference
- pharmacology_summary: Add mechanism of action, preclinical data summary
- compensation_policy: Add CDSCO Rule 26 compensation — treatment costs + income loss covered
- tribal_consent: Add ICMR 2017 community consent procedure for tribal/rural sites

Return the COMPLETE updated protocol as valid JSON — same structure as input but with gaps filled.
Return ONLY valid JSON, no markdown, no explanation."""

        raw = self.call_bedrock(prompt)

        try:
            patched = json.loads(raw)
            print(f"[ImproverAgent] Round {round_num}: Protocol patched successfully")
            return patched
        except Exception:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            print(f"[ImproverAgent] Round {round_num}: Parse error — returning original")
            return protocol_json

    def run_autopilot(
        self,
        protocol_json: dict,
        fda_json: dict,
        cdsco_json: dict,
        fda_agent,
        cdsco_agent,
        max_rounds: int = 3,
    ) -> dict:
        """
        Full autonomous improvement loop.
        
        Returns dict with:
        - improved_protocol: final patched protocol
        - rounds: list of {round, fda_score, cdsco_score, fixes_applied, elapsed}
        - final_fda_json: last FDA compliance result
        - final_cdsco_json: last CDSCO compliance result
        - score_delta_fda: improvement in FDA score
        - score_delta_cdsco: improvement in CDSCO score
        """
        import time

        initial_fda_score   = fda_json.get("fda_score", 0)
        initial_cdsco_score = cdsco_json.get("india_score", 0)

        current_protocol  = dict(protocol_json)
        current_fda_json  = dict(fda_json)
        current_cdsco_json = dict(cdsco_json)

        rounds_log = [{
            "round":       0,
            "label":       "Initial Generation",
            "fda_score":   initial_fda_score,
            "cdsco_score": initial_cdsco_score,
            "fda_grade":   fda_json.get("grade", ""),
            "cdsco_grade": cdsco_json.get("cdsco_grade", ""),
            "fixes_applied": [],
            "elapsed_s":   0,
        }]

        # Track best versions — never let a bad round overwrite a good one
        best_protocol   = dict(current_protocol)
        best_fda_json   = dict(current_fda_json)
        best_cdsco_json = dict(current_cdsco_json)
        best_combined   = initial_fda_score + initial_cdsco_score

        for round_num in range(1, max_rounds + 1):
            t0 = time.time()

            # Always collect gaps from BEST version, not just last round
            gaps = self._collect_all_gaps(best_fda_json, best_cdsco_json)
            total_gaps = gaps["total_failures"]

            if total_gaps == 0:
                print(f"[ImproverAgent] Round {round_num}: All gaps resolved — stopping early ✅")
                break

            fixes_this_round = (
                [f["ref"] + ": " + f["issue"][:60] for f in gaps["fda_failures"][:3]] +
                [f["ref"] + ": " + f["issue"][:60] for f in gaps["cdsco_failures"][:3]]
            )

            print(f"[ImproverAgent] Round {round_num}: Fixing {total_gaps} gaps...")

            # Patch from BEST protocol, not potentially degraded current
            candidate_protocol = self._patch_protocol(dict(best_protocol), gaps, round_num)

            # Rescore candidate
            protocol_str       = json.dumps(candidate_protocol, indent=2)
            candidate_fda_str  = fda_agent.check_compliance(protocol_str)
            candidate_cdsco_str = cdsco_agent.check_compliance(protocol_str)

            candidate_fda_json   = _safe_parse(candidate_fda_str)
            candidate_cdsco_json = _safe_parse(candidate_cdsco_str)

            new_fda_score   = candidate_fda_json.get("fda_score", 0)
            new_cdsco_score = candidate_cdsco_json.get("india_score", 0)
            new_combined    = new_fda_score + new_cdsco_score
            elapsed         = round(time.time() - t0, 1)

            # ── BEST-SCORE GUARD: only accept if combined score improved ───
            if new_combined >= best_combined:
                best_protocol   = candidate_protocol
                best_fda_json   = candidate_fda_json
                best_cdsco_json = candidate_cdsco_json
                best_combined   = new_combined
                print(f"[ImproverAgent] Round {round_num} ACCEPTED: "
                      f"FDA {gaps['fda_score_before']} → {new_fda_score} | "
                      f"CDSCO {gaps['cdsco_score_before']} → {new_cdsco_score} ✅ ({elapsed}s)")
            else:
                print(f"[ImproverAgent] Round {round_num} REJECTED (score regressed "
                      f"FDA {new_fda_score}, CDSCO {new_cdsco_score} < best {best_combined}) "
                      f"— keeping previous best ⚠️ ({elapsed}s)")
                new_fda_score   = best_fda_json.get("fda_score", 0)
                new_cdsco_score = best_cdsco_json.get("india_score", 0)

            rounds_log.append({
                "round":         round_num,
                "label":         f"Autopilot Round {round_num}",
                "fda_score":     new_fda_score,
                "cdsco_score":   new_cdsco_score,
                "fda_grade":     best_fda_json.get("grade", ""),
                "cdsco_grade":   best_cdsco_json.get("cdsco_grade", ""),
                "fixes_applied": fixes_this_round,
                "elapsed_s":     elapsed,
            })

            # Stop early if both scores are excellent
            if new_fda_score >= 92 and new_cdsco_score >= 92:
                print(f"[ImproverAgent] Both scores ≥92 — stopping early ✅")
                break

        # Always return BEST, not last
        current_protocol   = best_protocol
        current_fda_json   = best_fda_json
        current_cdsco_json = best_cdsco_json

        final_fda_score   = best_fda_json.get("fda_score", initial_fda_score)
        final_cdsco_score = best_cdsco_json.get("india_score", initial_cdsco_score)

        return {
            "improved_protocol":    best_protocol,
            "rounds":               rounds_log,
            "final_fda_json":       best_fda_json,
            "final_cdsco_json":     best_cdsco_json,
            "initial_fda_score":    initial_fda_score,
            "initial_cdsco_score":  initial_cdsco_score,
            "final_fda_score":      final_fda_score,
            "final_cdsco_score":    final_cdsco_score,
            "score_delta_fda":      final_fda_score   - initial_fda_score,
            "score_delta_cdsco":    final_cdsco_score - initial_cdsco_score,
            "total_rounds_run":     len(rounds_log) - 1,
            "autopilot_success":    final_fda_score >= 85 and final_cdsco_score >= 85,
        }


def _safe_parse(s) -> dict:
    if isinstance(s, dict): return s
    try:
        s = s.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(s)
    except Exception:
        match = re.search(r'\{.*\}', str(s), re.DOTALL)
        if match:
            try: return json.loads(match.group(0))
            except Exception: pass
    return {}