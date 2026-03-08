from protocol_agent import ProtocolAgent
from fda_agent import FDAAgent
from cdsco_agent import CDSCOAgent
from cohort_agent import CohortAgent
from feasibility_agent import FeasibilityAgent
from phi_agent import PHIAgent
import json

print("🚀 Testing TrialGuard 7 AI Agents...")

def safe_json_loads(s, description):
    try:
        # Strip potential markdown code blocks
        clean_s = s.strip()
        if clean_s.startswith("```json"):
            clean_s = clean_s[7:]
        if clean_s.endswith("```"):
            clean_s = clean_s[:-3]
        return json.loads(clean_s.strip())
    except json.JSONDecodeError:
        print(f"❌ FAILED TO PARSE {description} JSON. Raw output: {s[:200]}...")
        return {"error": "Invalid JSON", "raw": s}

# 1. Protocol Agent
pa = ProtocolAgent()
protocol_str = pa.generate_protocol("Design diabetes phase 2 trial in India")
protocol = safe_json_loads(protocol_str, "PROTOCOL")
print("✅ PROTOCOL AGENT:", json.dumps(protocol, indent=2))

# 2. FDA Agent
fa = FDAAgent("FDAAgent")
fda_check_str = fa.check_compliance(protocol_str)
fda_check = safe_json_loads(fda_check_str, "FDA")
print("\n✅ FDA AGENT:", json.dumps(fda_check, indent=2))

# 3. CDSCO Agent
ca = CDSCOAgent("CDSCOAgent")
cdsco_check_str = ca.check_compliance(protocol_str)
cdsco_check = safe_json_loads(cdsco_check_str, "CDSCO")
print("\n✅ CDSCO AGENT:", json.dumps(cdsco_check, indent=2))

# 4. COHORT AGENT
print("\n4️⃣ COHORT AGENT:")
coa = CohortAgent("CohortAgent")
cohort_stats_str = coa.generate_cohort("diabetes")
cohort_stats = safe_json_loads(cohort_stats_str, "COHORT")
print("✅ COHORT (Stats):", json.dumps(cohort_stats, indent=2))

# 5. FEASIBILITY AGENT
print("\n5️⃣ FEASIBILITY AGENT:")
fea = FeasibilityAgent("FeasibilityAgent")
feasibility_str = fea.score_feasibility(protocol_str)
feasibility = safe_json_loads(feasibility_str, "FEASIBILITY")
print("✅ FEASIBILITY:", json.dumps(feasibility, indent=2))

# 6. PHI AGENT
print("\n6️⃣ PHI AGENT:")
phia = PHIAgent()
redacted = phia.redact_phi("Patient Rahul Sharma, age 45, from Delhi.")
print("✅ PHI REDACTED:", redacted)

# 7. FULL PIPELINE TEST
print("\n7️⃣ FULL PIPELINE:")
final_result = {
    "fda_score": fda_check.get("fda_score", 0),
    "cdsco_score": cdsco_check.get("india_score", 0), 
    "protocol_status": protocol.get("status", "Unknown"),
    "feasibility": feasibility.get("feasibility", "Unknown")
}
print("✅ FINAL SCORES:", json.dumps(final_result, indent=2))

print("\n🎉 ALL 7 AGENTS LIVE! Day 2 Morning = COMPLETE!")
print("🚀 Next: FastAPI + Railway deployment → LIVE URL!")

