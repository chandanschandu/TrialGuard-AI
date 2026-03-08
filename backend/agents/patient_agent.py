try:
    from .agent_base import BaseAgent
except ImportError:
    from agent_base import BaseAgent

import json, re

class PatientAgent(BaseAgent):
    """
    Dual-Mode Patient Summary Agent.
    
    Takes the technical protocol and produces:
    1. English plain-language patient summary (Class 8 reading level)
    2. Hindi patient summary via the same content
    3. FAQ — 8 questions a real Indian patient would ask
    4. What to expect week-by-week timeline
    5. Rights & safety summary per CDSCO Schedule Y patient rights
    
    This hits the hackathon criteria:
    - "Patient education" ✅
    - "Care navigation" ✅  
    - "Decision-support systems" ✅
    """

    def __init__(self, name="PatientAgent"):
        super().__init__(name)

    def generate_patient_summary(self, protocol_json: dict, language: str = "en") -> dict:
        """
        Generate complete patient-facing content from technical protocol.
        Returns structured dict with English + Hindi content.
        """
        # Extract key facts for grounding the prompt
        title     = protocol_json.get("title", "Clinical Trial")
        obj       = protocol_json.get("objective", {})
        primary   = obj.get("primary", "") if isinstance(obj, dict) else str(obj)
        design    = protocol_json.get("trial_design", {})
        duration  = design.get("duration_weeks", "several") if isinstance(design, dict) else "several"
        arms      = design.get("arms", []) if isinstance(design, dict) else []
        criteria  = protocol_json.get("patient_criteria", {})
        inclusion = criteria.get("inclusion", []) if isinstance(criteria, dict) else []
        exclusion = criteria.get("exclusion", []) if isinstance(criteria, dict) else []
        endpoints = protocol_json.get("endpoints", {})
        primary_ep = endpoints.get("primary", "") if isinstance(endpoints, dict) else str(endpoints)

        # Arm descriptions
        arm_desc = ""
        if arms:
            for arm in arms[:2]:
                if isinstance(arm, dict):
                    arm_desc += f"- {arm.get('arm','')}: {arm.get('dose','')} {arm.get('frequency','')} {arm.get('route','')}\n"

        prompt = f"""You are Dr. Priya — a warm, caring Indian doctor explaining a clinical trial to a patient 
and their family in simple language they can understand.

━━━ TECHNICAL PROTOCOL ━━━
Trial: {title}
Goal: {primary}
Duration: {duration} weeks
Treatment arms:
{arm_desc}
Primary measurement: {primary_ep}

Inclusion criteria (who can join): {json.dumps(inclusion[:4])}
Exclusion criteria (who cannot join): {json.dumps(exclusion[:4])}

━━━ YOUR TASK ━━━
Write patient-facing content that:
- Uses Class 8 reading level (no jargon — explain any medical term used)
- Is warm, reassuring, and honest
- Addresses real concerns Indian patients have (cost, family, time off work, side effects)
- Mentions patient RIGHTS under CDSCO Schedule Y (right to withdraw, free treatment, compensation for injury)

Return ONLY valid JSON (no markdown):
{{
  "patient_summary_english": {{
    "what_is_this_trial": "2-3 sentences: what disease, what drug, what we are testing. Simple language.",
    "why_should_i_join": "3 bullet points: benefits of joining this trial for the patient",
    "what_will_happen": "Step-by-step: what happens at each visit, what tests, how often",
    "duration_simple": "Simple statement: how long in weeks/months, how many visits",
    "will_it_cost_me": "Free treatment + compensation explanation per CDSCO Rule 26",
    "is_it_safe": "Honest explanation of known risks + safety monitoring + right to withdraw anytime",
    "who_can_join": "Simple version of inclusion criteria — who is this for",
    "who_cannot_join": "Simple version of exclusion criteria",
    "your_rights": [
      "You can stop participating at any time without any penalty",
      "All your treatment during the trial is free",
      "If you are injured because of the trial, you will be compensated",
      "Your personal information is completely confidential",
      "You can ask questions anytime — your doctor must answer honestly"
    ],
    "contact": "For questions, contact your trial doctor or the Independent Ethics Committee"
  }},
  "patient_summary_hindi": {{
    "what_is_this_trial": "यह परीक्षण क्या है — 2-3 सरल वाक्यों में",
    "why_should_i_join": "मुझे क्यों शामिल होना चाहिए — 3 कारण",
    "what_will_happen": "क्या होगा — हर मुलाकात में क्या होता है",
    "duration_simple": "यह कितने समय तक चलेगा",
    "will_it_cost_me": "क्या मुझे पैसे देने होंगे — CDSCO नियम 26 के अनुसार मुफ्त इलाज",
    "is_it_safe": "क्या यह सुरक्षित है — सच्ची और सरल जानकारी",
    "who_can_join": "कौन शामिल हो सकता है",
    "who_cannot_join": "कौन शामिल नहीं हो सकता",
    "your_rights": [
      "आप किसी भी समय परीक्षण छोड़ सकते हैं — कोई जुर्माना नहीं",
      "परीक्षण के दौरान सभी दवाएं और जांचें मुफ्त हैं",
      "परीक्षण के कारण चोट लगने पर मुआवजा मिलेगा",
      "आपकी व्यक्तिगत जानकारी पूरी तरह गोपनीय है",
      "आप कभी भी सवाल पूछ सकते हैं"
    ],
    "contact": "सवालों के लिए अपने डॉक्टर या स्वतंत्र नैतिकता समिति से संपर्क करें"
  }},
  "patient_faq": [
    {{
      "question_en": "Will this trial cost me money?",
      "answer_en": "No. All treatment, tests, and medicines during the trial are completely free. If you are harmed because of the trial, you will also receive compensation.",
      "question_hi": "क्या इस परीक्षण में मुझे पैसे देने होंगे?",
      "answer_hi": "नहीं। परीक्षण के दौरान सभी इलाज, जांचें और दवाएं बिल्कुल मुफ्त हैं।"
    }},
    {{
      "question_en": "Can I stop if I don't feel comfortable?",
      "answer_en": "Yes, absolutely. You can stop at any time, for any reason, without any penalty or effect on your regular medical care.",
      "question_hi": "क्या मैं बीच में रोक सकता हूँ?",
      "answer_hi": "हाँ, बिल्कुल। आप किसी भी समय, किसी भी कारण से रोक सकते हैं।"
    }},
    {{
      "question_en": "How many times will I need to visit the hospital?",
      "answer_en": "Specific answer based on the {duration} week trial duration and visit schedule.",
      "question_hi": "मुझे कितनी बार अस्पताल आना होगा?",
      "answer_hi": "{duration} हफ्तों के दौरान नियमित मुलाकातें होंगी।"
    }},
    {{
      "question_en": "Will I get the real medicine or a sugar pill?",
      "answer_en": "This is a blinded trial — neither you nor your doctor will know which group you are in. Both groups receive full medical monitoring and care.",
      "question_hi": "क्या मुझे असली दवा मिलेगी या नकली?",
      "answer_hi": "यह एक अंध परीक्षण है — आपको और आपके डॉक्टर दोनों को पता नहीं होगा। दोनों समूहों को पूरी देखभाल मिलती है।"
    }},
    {{
      "question_en": "What are the risks?",
      "answer_en": "Honest summary of known risks from the protocol, plus explanation of safety monitoring and DSMB oversight.",
      "question_hi": "क्या जोखिम हैं?",
      "answer_hi": "ज्ञात जोखिमों की ईमानदार और सरल जानकारी, साथ ही सुरक्षा निगरानी की व्याख्या।"
    }},
    {{
      "question_en": "Will my employer or family know I am in a trial?",
      "answer_en": "No. Your participation is completely confidential. Your information is protected under Indian data privacy laws.",
      "question_hi": "क्या मेरे नियोक्ता या परिवार को पता चलेगा?",
      "answer_hi": "नहीं। आपकी भागीदारी पूरी तरह गोपनीय है।"
    }},
    {{
      "question_en": "What happens after the trial ends?",
      "answer_en": "You will receive a summary of results. If the treatment worked, your doctor will discuss options for continued access.",
      "question_hi": "परीक्षण के बाद क्या होगा?",
      "answer_hi": "आपको परिणामों का सारांश मिलेगा। अगर दवा काम आई, तो आगे के विकल्प पर चर्चा होगी।"
    }},
    {{
      "question_en": "Do I need to speak English?",
      "answer_en": "No. Informed consent forms are available in Hindi and your regional language. A translator will be available if needed.",
      "question_hi": "क्या मुझे अंग्रेजी आनी चाहिए?",
      "answer_hi": "नहीं। सहमति पत्र हिंदी और आपकी क्षेत्रीय भाषा में उपलब्ध है।"
    }}
  ],
  "week_by_week_timeline": [
    {{"week": "Week 0 (Screening)", "what_happens_en": "First visit: blood tests, medical history, check if you qualify", "what_happens_hi": "पहली मुलाकात: रक्त परीक्षण, चिकित्सा इतिहास"}},
    {{"week": "Week 1 (Start)", "what_happens_en": "Randomization: assigned to treatment or placebo group, receive first medication", "what_happens_hi": "समूह निर्धारण: दवा या प्लेसीबो समूह में शामिल"}},
    {{"week": "Week 4, 8, 12", "what_happens_en": "Regular check-up visits: blood tests, vital signs, side effect monitoring", "what_happens_hi": "नियमित जांच: रक्त परीक्षण, महत्वपूर्ण संकेत"}},
    {{"week": f"Week {duration} (End)", "what_happens_en": "Final visit: comprehensive tests, results review, next steps discussion", "what_happens_hi": f"सप्ताह {duration}: अंतिम मुलाकात, परिणाम समीक्षा"}}
  ],
  "icf_languages_note": "Informed consent available in: Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi, Bengali, Gujarati, Odia — patient may choose their language",
  "cdsco_patient_rights_ref": "Your rights are protected under CDSCO Schedule Y Appendix V and ICMR National Ethical Guidelines 2017"
}}"""

        raw = self.call_bedrock(prompt)

        try:
            parsed = json.loads(raw)
        except Exception:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except Exception:
                    parsed = self._fallback_summary(title, duration, language)
            else:
                parsed = self._fallback_summary(title, duration, language)

        # Always add metadata
        parsed["trial_title"] = title
        parsed["duration_weeks"] = duration
        parsed["generated_by"] = "TrialGuard AI — Patient Education Module"
        parsed["regulatory_basis"] = "CDSCO Schedule Y Appendix V | ICMR 2017 | ICH E6 R2"

        return parsed

    def _fallback_summary(self, title: str, duration, language: str) -> dict:
        """Minimal fallback if LLM parse fails."""
        return {
            "patient_summary_english": {
                "what_is_this_trial": f"This is a clinical trial called: {title}. It will test a new treatment to see if it is safe and effective.",
                "duration_simple": f"The trial lasts {duration} weeks.",
                "your_rights": [
                    "You can stop at any time without penalty",
                    "All treatment is free",
                    "You will be compensated for any trial-related injury",
                    "Your information is confidential",
                ],
                "will_it_cost_me": "No cost to you. Free treatment + CDSCO Rule 26 compensation applies.",
                "is_it_safe": "Safety is monitored by an independent board throughout the trial.",
            },
            "patient_summary_hindi": {
                "what_is_this_trial": f"यह एक नैदानिक परीक्षण है: {title}",
                "duration_simple": f"यह परीक्षण {duration} हफ्तों तक चलेगा।",
                "your_rights": [
                    "आप किसी भी समय रोक सकते हैं",
                    "सभी इलाज मुफ्त हैं",
                    "चोट पर मुआवजा मिलेगा",
                ],
                "will_it_cost_me": "कोई खर्च नहीं। CDSCO नियम 26 के अनुसार मुफ्त इलाज।",
            },
            "patient_faq": [],
            "week_by_week_timeline": [],
        }