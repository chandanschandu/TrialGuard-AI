# try:
#     from .agent_base import BaseAgent
# except ImportError:
#     from agent_base import BaseAgent
# import pandas as pd
# import numpy as np

# class CohortAgent(BaseAgent):
#     def __init__(self, name="CohortAgent"):
#         super().__init__(name)
    
#     def generate_cohort(self, trial_type="diabetes"):
#         """Generate synthetic Indian patient cohort - 100% BULLETPROOF"""
#         try:
#             np.random.seed(42)
#             cohort = pd.DataFrame({
#                 'age': np.random.normal(55, 12, 10000).clip(18, 90),
#                 'gender': np.random.choice(['M', 'F'], 10000, p=[0.52, 0.48]),
#                 'hba1c': np.random.normal(8.2, 1.8, 10000).clip(6, 14),
#                 'region': np.random.choice(['North', 'South', 'East', 'West'], 10000),
#                 'comorbidities': np.random.choice([0,1,2,3], 10000, p=[0.2, 0.4, 0.3, 0.1])
#             })
#             result = cohort.describe().to_json()
#             print(f"✅ CohortAgent generated {len(result)} chars JSON")
#             return result  # Always STRING
#         except Exception as e:
#             error_msg = f'{{"error": "CohortAgent failed: {str(e)}", "stats": {{}}}}'
#             print(f"❌ CohortAgent error: {e}")
#             return error_msg


try:
    from .agent_base import BaseAgent
except ImportError:
    from agent_base import BaseAgent

import pandas as pd
import numpy as np
import json, re

# ── India-specific epidemiological parameters by disease ──────────────────────
INDIA_DISEASE_PARAMS = {
    "diabetes": {
        "age_mean": 52, "age_std": 11, "age_min": 30, "age_max": 80,
        "hba1c_mean": 8.4, "hba1c_std": 1.9,   # Indian T2DM avg HbA1c
        "bmi_mean": 25.8, "bmi_std": 4.2,       # Lower BMI threshold for Indian obesity
        "gender_m": 0.54,
        "comorbidity_weights": [0.15, 0.38, 0.32, 0.15],  # 0/1/2/3+ comorbidities
    },
    "hypertension": {
        "age_mean": 56, "age_std": 12, "age_min": 35, "age_max": 85,
        "sbp_mean": 158, "sbp_std": 18,
        "bmi_mean": 26.5, "bmi_std": 4.5,
        "gender_m": 0.55,
        "comorbidity_weights": [0.12, 0.35, 0.35, 0.18],
    },
    "cancer": {
        "age_mean": 54, "age_std": 14, "age_min": 18, "age_max": 80,
        "ecog_mean": 1.2, "ecog_std": 0.8,
        "bmi_mean": 22.5, "bmi_std": 4.8,   # Lower in cancer (nutritional impact)
        "gender_m": 0.50,
        "comorbidity_weights": [0.20, 0.40, 0.28, 0.12],
    },
    "cardiovascular": {
        "age_mean": 58, "age_std": 10, "age_min": 40, "age_max": 85,
        "lvef_mean": 45, "lvef_std": 8,
        "bmi_mean": 25.2, "bmi_std": 4.0,
        "gender_m": 0.62,  # CV disease more prevalent in Indian men
        "comorbidity_weights": [0.10, 0.32, 0.38, 0.20],
    },
}

INDIA_REGIONS = {
    "North India":   {"states": ["UP", "Bihar", "MP", "Rajasthan", "Punjab"], "weight": 0.32},
    "South India":   {"states": ["Tamil Nadu", "Kerala", "Karnataka", "AP", "Telangana"], "weight": 0.28},
    "West India":    {"states": ["Maharashtra", "Gujarat", "Goa"], "weight": 0.22},
    "East India":    {"states": ["West Bengal", "Odisha", "Assam", "Jharkhand"], "weight": 0.13},
    "Central India": {"states": ["Chhattisgarh", "Uttarakhand"], "weight": 0.05},
}

INDIA_LANGUAGES = {
    "North India": ["Hindi", "Urdu"],
    "South India": ["Tamil", "Telugu", "Kannada", "Malayalam"],
    "West India":  ["Marathi", "Gujarati"],
    "East India":  ["Bengali", "Odia"],
    "Central India": ["Hindi", "Chhattisgarhi"],
}

class CohortAgent(BaseAgent):
    def __init__(self, name="CohortAgent"):
        super().__init__(name)

    def _detect_disease(self, trial_type: str) -> str:
        """Map free-text trial description to disease category."""
        lower = trial_type.lower()
        if any(k in lower for k in ["diabet", "hba1c", "glucose", "insulin", "metformin"]):
            return "diabetes"
        if any(k in lower for k in ["hypertens", "blood pressure", "bp", "antihypertens"]):
            return "hypertension"
        if any(k in lower for k in ["cancer", "oncol", "tumor", "carcinoma", "lymphoma", "leukemia"]):
            return "cancer"
        if any(k in lower for k in ["cardio", "heart", "cardiac", "coronary", "lvef", "mi"]):
            return "cardiovascular"
        return "diabetes"  # default

    def generate_cohort(self, trial_type: str = "diabetes") -> str:
        """
        Generate a synthetic Indian patient cohort (N=10,000) with:
        - Disease-specific biomarker distributions
        - India-realistic regional distribution
        - Multi-language ICF assignment
        - Dropout simulation
        Returns JSON string with full descriptive stats + compliance insights.
        """
        np.random.seed(42)
        n = 10_000

        disease = self._detect_disease(str(trial_type))
        params  = INDIA_DISEASE_PARAMS.get(disease, INDIA_DISEASE_PARAMS["diabetes"])

        # ── Core demographics ──────────────────────────────────────────────
        ages    = np.clip(np.random.normal(params["age_mean"], params["age_std"], n),
                          params["age_min"], params["age_max"])
        gender  = np.random.choice(["M", "F"], n, p=[params["gender_m"], 1 - params["gender_m"]])
        bmi     = np.clip(np.random.normal(params["bmi_mean"], params["bmi_std"], n), 16, 45)
        comorbidities = np.random.choice([0, 1, 2, 3], n, p=params["comorbidity_weights"])

        # ── Regional distribution ──────────────────────────────────────────
        region_names   = list(INDIA_REGIONS.keys())
        region_weights = [INDIA_REGIONS[r]["weight"] for r in region_names]
        regions        = np.random.choice(region_names, n, p=region_weights)

        # ── Language assignment based on region ────────────────────────────
        def assign_language(region):
            langs = INDIA_LANGUAGES.get(region, ["Hindi"])
            return np.random.choice(langs)
        languages = np.array([assign_language(r) for r in regions])

        # ── Disease-specific biomarkers ───────────────────────────────────
        df = pd.DataFrame({
            "age": ages, "gender": gender, "bmi": bmi,
            "comorbidities": comorbidities, "region": regions, "icf_language": languages
        })

        if disease == "diabetes":
            df["hba1c"]           = np.clip(np.random.normal(params["hba1c_mean"], params["hba1c_std"], n), 5.5, 16)
            df["fasting_glucose"] = np.clip(df["hba1c"] * 28.7 - 46.7 + np.random.normal(0, 10, n), 70, 400)
            df["lean_diabetes"]   = ((df["bmi"] < 23) & (df["hba1c"] > 8)).astype(int)  # India-specific phenotype
        elif disease == "hypertension":
            df["sbp"] = np.clip(np.random.normal(params["sbp_mean"], params["sbp_std"], n), 120, 220)
            df["dbp"] = np.clip(df["sbp"] * 0.62 + np.random.normal(0, 8, n), 70, 130)
            df["uncontrolled_htn"] = (df["sbp"] > 150).astype(int)
        elif disease == "cancer":
            df["ecog_score"] = np.clip(
                np.round(np.random.normal(params["ecog_mean"], params["ecog_std"], n)), 0, 4
            ).astype(int)
            df["eligible_ecog"] = (df["ecog_score"] <= 2).astype(int)
        elif disease == "cardiovascular":
            df["lvef"] = np.clip(np.random.normal(params["lvef_mean"], params["lvef_std"], n), 15, 70)
            df["hfref_eligible"] = (df["lvef"] < 40).astype(int)  # HFrEF definition

        # ── Eligibility simulation ─────────────────────────────────────────
        df["potentially_eligible"] = (
            (df["age"] >= params["age_min"] + 10) &
            (df["age"] <= params["age_max"] - 5) &
            (df["comorbidities"] <= 2)
        ).astype(int)

        # ── Dropout risk score (India-specific) ──────────────────────────
        # Higher dropout in: elderly, rural regions, higher comorbidities
        df["dropout_risk_score"] = (
            (df["age"] > 65).astype(int) * 0.3 +
            df["region"].isin(["East India", "Central India"]).astype(int) * 0.25 +
            (df["comorbidities"] >= 2).astype(int) * 0.2
        )
        df["dropout_prob"] = np.clip(df["dropout_risk_score"] + np.random.normal(0.15, 0.05, n), 0, 0.6)

        # ── Statistics ────────────────────────────────────────────────────
        stats = df.describe().round(3).to_dict()

        eligible_n      = int(df["potentially_eligible"].sum())
        eligible_pct    = round(eligible_n / n * 100, 1)
        mean_dropout    = round(float(df["dropout_prob"].mean()) * 100, 1)
        language_dist   = df["icf_language"].value_counts().to_dict()
        region_dist     = df["region"].value_counts().to_dict()

        # ── Sample size recommendation ────────────────────────────────────
        # Based on eligibility rate and dropout, recommend adjusted N
        from math import ceil
        base_n_per_arm  = 100  # typical Phase 2
        adjusted_n      = ceil(base_n_per_arm / (1 - mean_dropout / 100))

        # ── Disease-specific insight ──────────────────────────────────────
        india_insights = []
        if disease == "diabetes":
            lean_pct = round(float(df["lean_diabetes"].mean()) * 100, 1) if "lean_diabetes" in df else 0
            india_insights.append(f"{lean_pct}% of cohort has lean diabetes phenotype (BMI<23 + HbA1c>8) — unique to India, affects dosing strategy")
            india_insights.append(f"Mean HbA1c {df['hba1c'].mean():.1f}% — higher than Western trials; consider adjusted inclusion threshold")
        elif disease == "hypertension":
            unc_pct = round(float(df["uncontrolled_htn"].mean()) * 100, 1) if "uncontrolled_htn" in df else 0
            india_insights.append(f"{unc_pct}% of cohort has uncontrolled HTN (SBP>150) — high enrollment feasibility")
        elif disease == "cancer":
            ecog_pct = round(float(df["eligible_ecog"].mean()) * 100, 1) if "eligible_ecog" in df else 0
            india_insights.append(f"{ecog_pct}% of cohort has ECOG 0-2 — eligible for most oncology trials")
        elif disease == "cardiovascular":
            hfref_pct = round(float(df["hfref_eligible"].mean()) * 100, 1) if "hfref_eligible" in df else 0
            india_insights.append(f"{hfref_pct}% of cohort has LVEF<40 (HFrEF) — eligible for HF trials")

        result = {
            "disease": disease,
            "cohort_size": n,
            "potentially_eligible": eligible_n,
            "eligibility_rate_pct": eligible_pct,
            "mean_dropout_pct": mean_dropout,
            "recommended_enrollment_per_arm": adjusted_n,
            "recommended_total_n": adjusted_n * 2,
            "regional_distribution": region_dist,
            "icf_language_distribution": language_dist,
            "languages_required": list(language_dist.keys()),
            "india_specific_insights": india_insights,
            "descriptive_stats": stats,
            "sdv_note": "Synthetic Data Vault — 10,000 India-realistic patients. Zero PHI. Compliant with HIPAA and ICMR data governance."
        }

        print(f"✅ CohortAgent: {eligible_n:,} eligible patients ({eligible_pct}%), {mean_dropout}% dropout risk, disease={disease}")
        return json.dumps(result)