"""
TrialGuard AI — AWS Live Endpoint Test Suite v3.1
Fixed: Validator logic for Patient Summary
"""

import requests
import json
import time
import sys
import os

# ══════════════════════════════════════════════════════════════════════════════
# ⚙️  CONFIG
# ══════════════════════════════════════════════════════════════════════════════
API_ID  = "t5whevmrmk"
REGION  = "us-east-1"
AWS_BASE_URL = f"https://{API_ID}.execute-api.{REGION}.amazonaws.com"

USE_AUTOPILOT = False  
USE_PATIENT   = True

# ══════════════════════════════════════════════════════════════════════════════
GREEN="\033[92m"; RED="\033[91m"; YELLOW="\033[93m"
BLUE="\033[94m"; BOLD="\033[1m"; RESET="\033[0m"; CYAN="\033[96m"

def ok(msg):   print(f"   {GREEN}✅ {msg}{RESET}")
def fail(msg): print(f"   {RED}❌ {msg}{RESET}")
def warn(msg): print(f"   {YELLOW}⚠️  {msg}{RESET}")
def info(msg): print(f"   {BLUE}ℹ️  {msg}{RESET}")
def head(msg): print(f"\n{BOLD}{CYAN}{'─'*60}\n   {msg}\n{'─'*60}{RESET}")

# ══════════════════════════════════════════════════════════════════════════════
# LAMBDA TEST EVENTS
# ══════════════════════════════════════════════════════════════════════════════
def _make_event(method, path, body=None):
    return {
        "version": "2.0",
        "routeKey": f"{method} {path}",
        "rawPath": path,
        "headers": {"content-type": "application/json"},
        "requestContext": {
            "http": {"method": method, "path": path},
            "stage": "$default"
        },
        "body": json.dumps(body) if body else None,
        "isBase64Encoded": False
    }

LAMBDA_EVENTS = {
    "diabetes_design": _make_event("POST", "/design-trial", {
        "text": "Phase 2 diabetes trial for elderly in Bengaluru", "language": "en"
    }),
    "patient_summary_hi": _make_event("POST", "/patient-summary", {
        "session_id": "test-123", "language": "hi",
        "protocol": {"title": "Diabetes Trial", "objective": {"primary": "HbA1c reduction"}}
    })
}

def save_lambda_events():
    os.makedirs("lambda_events", exist_ok=True)
    for name, event in LAMBDA_EVENTS.items():
        with open(f"lambda_events/{name}.json", "w") as f:
            json.dump(event, f, indent=2)
    ok("Lambda events saved to /lambda_events")

# ══════════════════════════════════════════════════════════════════════════════
# VALIDATORS
# ══════════════════════════════════════════════════════════════════════════════
def validate_patient_response(result):
    # Core requirements for a PASS
    required = ["patient_summary_english", "patient_summary_hindi"]
    found_requirements = 0
    
    ps = result.get("patient_summary", {})
    
    if ps.get("patient_summary_english"): 
        ok("English Summary generated"); found_requirements += 1
    if ps.get("patient_summary_hindi"): 
        ok("Hindi Summary generated"); found_requirements += 1
    
    # Check for S3 Audio Links
    if result.get("audio_url_english"): ok("English TTS Link found")
    if result.get("audio_url_hindi"): ok("Hindi TTS (Aditi) Link found")
    
    # If we have both summaries and at least one audio link, it's a success
    return found_requirements >= 2 and (result.get("audio_url_english") or result.get("audio_url_hindi"))

# ══════════════════════════════════════════════════════════════════════════════
# MAIN TEST RUNNER
# ══════════════════════════════════════════════════════════════════════════════
def run_suite():
    head("TRIALGUARD AI — AWS DEPLOYMENT TEST")
    info(f"Endpoint: {AWS_BASE_URL}")
    results = {}

    # --- TEST 1: DESIGN TRIAL ---
    head("POST /design-trial (Diabetes)")
    try:
        payload = {"text": "Phase 2 diabetes trial, elderly patients, HbA1c > 8.0", "language": "en"}
        r = requests.post(f"{AWS_BASE_URL}/design-trial", json=payload, timeout=30)
        
        if r.status_code == 200:
            data = r.json()
            sid = data.get("session_id")
            proto = data.get("protocol")
            ok(f"Success! Session ID: {sid}")
            ok(f"FDA Score: {data.get('fda_score')} | CDSCO Score: {data.get('cdsco_score')}")
            results["Design Trial"] = True
            
            # --- TEST 2: PATIENT SUMMARY ---
            if USE_PATIENT:
                head("POST /patient-summary (Bilingual)")
                p_payload = {"session_id": sid, "protocol": proto, "language": "hi"}
                pr = requests.post(f"{AWS_BASE_URL}/patient-summary", json=p_payload, timeout=30)
                
                if pr.status_code == 200:
                    results["Patient Summary"] = validate_patient_response(pr.json())
                else:
                    fail(f"Patient Summary failed: {pr.status_code}")
                    results["Patient Summary"] = False
        else:
            fail(f"Design Trial failed: {r.status_code} - {r.text}")
            results["Design Trial"] = False

    except Exception as e:
        fail(f"Connection Error: {str(e)}")

    # --- FINAL REPORT ---
    head("FINAL AWS REPORT")
    for test, status in results.items():
        color = GREEN if status else RED
        print(f"{color}{test}: {'PASSED' if status else 'FAILED'}{RESET}")

if __name__ == "__main__":
    save_lambda_events()
    run_suite()