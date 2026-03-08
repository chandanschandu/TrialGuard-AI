"""
TrialGuard AI — Production Frontend
India-First Clinical Trial Protocol Generator
All 3 endpoints: /design-trial · /autopilot · /patient-summary
Run: streamlit run app.py
"""
import streamlit as st
import requests
import json
import time

BASE_URL = "https://t5whevmrmk.execute-api.us-east-1.amazonaws.com"

st.set_page_config(
    page_title="TrialGuard AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Outfit:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

:root {
  --void:#05070f; --deep:#080c18; --surface:#0e1425; --card:#111827; --card2:#141d2e;
  --rim:rgba(255,255,255,0.06); --rim2:rgba(255,255,255,0.11);
  --saffron:#FF9933; --saffron2:#e07a1a; --ashoka:#0057A8;
  --chakra:#38bdf8; --jade:#00c896; --jade2:#00a578;
  --crimson:#e63946; --gold:#f7c948;
  --white:#f0f4ff; --muted:#4e6080; --dim:#263348;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,.stApp{background:var(--void)!important;font-family:'Outfit',sans-serif!important;color:var(--white)!important;}
.stApp::before{content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background:radial-gradient(ellipse 70% 50% at -5% 0%,rgba(255,153,51,.07) 0%,transparent 55%),
    radial-gradient(ellipse 60% 40% at 105% 100%,rgba(0,200,150,.06) 0%,transparent 55%),
    radial-gradient(ellipse 40% 60% at 50% 40%,rgba(0,87,168,.04) 0%,transparent 60%);}
.stApp::after{content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:repeating-linear-gradient(-55deg,transparent 0px,transparent 40px,rgba(255,255,255,.012) 40px,rgba(255,255,255,.012) 41px);}
.main .block-container{padding:0 2.8rem 5rem!important;max-width:1380px!important;position:relative;z-index:1;}

/* MASTHEAD */
.masthead{padding:3rem 0 2.5rem;display:grid;grid-template-columns:1fr auto;align-items:end;gap:2rem;border-bottom:1px solid var(--rim);margin-bottom:2.5rem;}
.brand-kicker{font-family:'IBM Plex Mono',monospace;font-size:.62rem;letter-spacing:.25em;text-transform:uppercase;color:var(--saffron);margin-bottom:.8rem;display:flex;align-items:center;gap:.6rem;}
.brand-kicker::before{content:'';display:block;width:24px;height:1px;background:var(--saffron);}
.brand-wordmark{font-family:'Playfair Display',serif;font-size:clamp(3rem,5.5vw,4.8rem);font-weight:900;line-height:.92;letter-spacing:-.03em;color:var(--white);}
.brand-wordmark .accent{font-style:italic;color:var(--saffron);}
.brand-tagline{font-size:.88rem;color:var(--muted);margin-top:1rem;font-weight:300;line-height:1.7;max-width:50ch;letter-spacing:.01em;}
.masthead-right{text-align:right;display:flex;flex-direction:column;gap:.5rem;align-items:flex-end;}
.aws-badge{display:inline-flex;align-items:center;gap:.45rem;background:rgba(255,153,51,.08);border:1px solid rgba(255,153,51,.22);border-radius:100px;padding:.35rem 1rem;font-family:'IBM Plex Mono',monospace;font-size:.6rem;letter-spacing:.1em;color:var(--saffron);}
.live-dot{width:5px;height:5px;border-radius:50%;background:var(--saffron);box-shadow:0 0 6px var(--saffron);animation:pulse 1.8s ease-in-out infinite;}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 4px var(--saffron);}50%{opacity:.5;box-shadow:0 0 12px var(--saffron);}}
.agent-row{font-family:'IBM Plex Mono',monospace;font-size:.58rem;color:var(--dim);letter-spacing:.1em;}

/* STAT STRIP */
.stat-strip{display:grid;grid-template-columns:repeat(5,1fr);background:var(--rim);gap:1px;border-radius:14px;overflow:hidden;margin-bottom:2.8rem;}
.stat-cell{background:var(--card);padding:1.4rem 1.6rem;transition:background .2s;}
.stat-cell:hover{background:var(--card2);}
.stat-v{font-family:'Playfair Display',serif;font-size:2rem;font-weight:700;line-height:1;letter-spacing:-.04em;color:var(--c,var(--jade));}
.stat-v small{font-size:1rem;font-weight:400;opacity:.5;}
.stat-l{font-family:'IBM Plex Mono',monospace;font-size:.57rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-top:.3rem;}

/* TABS */
.stTabs [data-baseweb="tab-list"]{gap:0!important;background:transparent!important;border-bottom:1px solid var(--rim)!important;margin-bottom:2.2rem!important;}
.stTabs [data-baseweb="tab"]{font-family:'IBM Plex Mono',monospace!important;font-size:.68rem!important;letter-spacing:.14em!important;text-transform:uppercase!important;color:var(--muted)!important;background:transparent!important;border:none!important;border-bottom:2px solid transparent!important;padding:.8rem 1.5rem!important;margin-bottom:-1px!important;transition:color .2s!important;}
.stTabs [data-baseweb="tab"]:hover{color:var(--white)!important;}
.stTabs [aria-selected="true"]{color:var(--saffron)!important;border-bottom-color:var(--saffron)!important;}
.stTabs [data-baseweb="tab-panel"]{padding:0!important;}
.stTabs [data-baseweb="tab-highlight"]{display:none!important;}

/* FORMS */
.stSelectbox label,.stTextArea label,.stSlider label{font-family:'IBM Plex Mono',monospace!important;font-size:.6rem!important;letter-spacing:.16em!important;text-transform:uppercase!important;color:var(--muted)!important;}
.stTextArea textarea{background:var(--card)!important;border:1px solid var(--rim)!important;border-radius:12px!important;color:var(--white)!important;font-family:'Outfit',sans-serif!important;font-size:.93rem!important;line-height:1.65!important;transition:border-color .2s,box-shadow .2s!important;}
.stTextArea textarea:focus{border-color:rgba(255,153,51,.35)!important;box-shadow:0 0 0 3px rgba(255,153,51,.07)!important;}
.stSelectbox>div>div{background:var(--card)!important;border:1px solid var(--rim)!important;border-radius:10px!important;color:var(--white)!important;}

/* BUTTONS */
.stButton>button{width:100%!important;height:52px!important;background:linear-gradient(135deg,var(--saffron) 0%,var(--saffron2) 100%)!important;border:none!important;border-radius:12px!important;color:#fff!important;font-family:'Outfit',sans-serif!important;font-weight:700!important;font-size:.85rem!important;letter-spacing:.12em!important;text-transform:uppercase!important;box-shadow:0 4px 22px rgba(255,153,51,.28)!important;transition:all .2s!important;}
.stButton>button:hover{background:linear-gradient(135deg,#ffaa44 0%,var(--saffron) 100%)!important;box-shadow:0 6px 32px rgba(255,153,51,.44)!important;transform:translateY(-1px)!important;}
.stButton>button:active{transform:translateY(0)!important;}

/* PROGRESS */
.stProgress>div>div>div{background:linear-gradient(90deg,var(--saffron),var(--jade))!important;box-shadow:0 0 10px rgba(255,153,51,.45)!important;}
.stProgress>div>div{background:var(--surface)!important;}

/* RESULT HEADER */
.result-header{display:flex;align-items:center;gap:1rem;padding:1.3rem 1.8rem;background:linear-gradient(135deg,rgba(255,153,51,.06),rgba(0,200,150,.04));border:1px solid rgba(255,153,51,.2);border-radius:14px;margin-bottom:2rem;}
.result-icon{width:42px;height:42px;border-radius:11px;flex-shrink:0;background:rgba(255,153,51,.1);border:1px solid rgba(255,153,51,.25);display:flex;align-items:center;justify-content:center;font-size:1.2rem;}
.result-title{font-weight:700;font-size:.98rem;color:var(--white);}
.result-meta{font-family:'IBM Plex Mono',monospace;font-size:.6rem;color:var(--muted);letter-spacing:.1em;margin-top:.2rem;}

/* SCORE CARDS */
.score-row{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:2rem;}
.score-card{background:var(--card);border:1px solid var(--rim);border-radius:16px;padding:1.6rem 1.4rem;position:relative;overflow:hidden;}
.score-card::after{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--ac);box-shadow:0 0 14px var(--ac);}
.score-badge{font-family:'IBM Plex Mono',monospace;font-size:.57rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ac);background:color-mix(in srgb,var(--ac) 11%,transparent);border:1px solid color-mix(in srgb,var(--ac) 24%,transparent);border-radius:4px;padding:.18rem .5rem;display:inline-block;margin-bottom:.8rem;}
.score-num{font-family:'Playfair Display',serif;font-size:3rem;font-weight:900;line-height:1;letter-spacing:-.05em;color:var(--ac);}
.score-num small{font-size:1.3rem;font-weight:700;opacity:.35;}
.score-lbl{font-size:.75rem;color:var(--muted);margin-top:.4rem;font-weight:500;}
.score-sub{font-family:'IBM Plex Mono',monospace;font-size:.6rem;color:var(--dim);margin-top:.2rem;letter-spacing:.05em;}

/* AUTOPILOT */
.ap-wrap{background:var(--card);border:1px solid var(--rim);border-radius:16px;padding:1.8rem;margin-bottom:2rem;}
.ap-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.4rem;}
.ap-title{font-weight:700;font-size:.82rem;letter-spacing:.07em;text-transform:uppercase;color:var(--white);display:flex;align-items:center;gap:.6rem;}
.ap-chip{background:rgba(0,200,150,.1);border:1px solid rgba(0,200,150,.25);color:var(--jade);border-radius:5px;font-family:'IBM Plex Mono',monospace;font-size:.58rem;letter-spacing:.1em;padding:.18rem .55rem;}
.delta-row{display:flex;gap:.4rem;}
.delta{padding:.15rem .5rem;border-radius:4px;font-family:'IBM Plex Mono',monospace;font-size:.58rem;font-weight:600;}
.delta-up{background:rgba(0,200,150,.1);color:var(--jade);}
.delta-flat{background:rgba(78,96,128,.15);color:var(--muted);}
.round-row{display:grid;grid-template-columns:96px 1fr 1fr 72px;gap:.8rem;align-items:center;background:var(--surface);border:1px solid var(--rim);border-radius:10px;padding:.85rem 1rem;margin-bottom:.4rem;transition:border-color .2s;}
.round-row:hover{border-color:var(--rim2);}
.round-lbl{font-family:'IBM Plex Mono',monospace;font-size:.6rem;color:var(--muted);letter-spacing:.07em;}
.bar-track{height:5px;background:var(--deep);border-radius:3px;overflow:hidden;}
.bar-fill{height:100%;border-radius:3px;background:var(--bc);box-shadow:0 0 8px var(--bc);}
.bar-label{font-family:'IBM Plex Mono',monospace;font-size:.55rem;color:var(--muted);letter-spacing:.06em;margin-bottom:.22rem;}
.round-scores{font-family:'IBM Plex Mono',monospace;font-size:.7rem;font-weight:600;color:var(--white);text-align:right;}

/* SECTION HEADERS */
.sec-hdr{font-family:'IBM Plex Mono',monospace;font-size:.58rem;letter-spacing:.2em;text-transform:uppercase;color:var(--dim);border-bottom:1px solid var(--rim);padding-bottom:.4rem;margin:1.8rem 0 1.2rem;display:flex;align-items:center;gap:.7rem;}
.sec-hdr .n{color:var(--saffron);background:rgba(255,153,51,.09);border:1px solid rgba(255,153,51,.2);border-radius:3px;padding:.1rem .4rem;font-size:.52rem;}

/* CHIPS */
.chip-list{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:.8rem;}
.chip{display:flex;align-items:flex-start;gap:.45rem;background:var(--card2);border:1px solid var(--rim);border-radius:8px;padding:.55rem .85rem;font-size:.77rem;color:var(--muted);line-height:1.4;max-width:360px;transition:border-color .2s,color .2s;}
.chip:hover{border-color:var(--rim2);color:var(--white);}
.chip-dot{width:5px;height:5px;border-radius:50%;margin-top:5px;flex-shrink:0;}

/* DOWNLOADS */
.dl-pair{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1.4rem 0;}
.dl-card{display:flex;align-items:center;gap:.9rem;padding:1.2rem 1.4rem;background:var(--card);border:1px solid var(--rim);border-radius:13px;text-decoration:none!important;transition:all .2s;cursor:pointer;}
.dl-card:hover{border-color:rgba(255,153,51,.3);background:rgba(255,153,51,.03);transform:translateY(-1px);}
.dl-ico{width:38px;height:38px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0;}
.dl-name{font-weight:700;font-size:.84rem;color:var(--white);}
.dl-meta{font-family:'IBM Plex Mono',monospace;font-size:.56rem;color:var(--muted);letter-spacing:.08em;margin-top:.18rem;text-transform:uppercase;}

/* PATIENT */
.sum-block{background:var(--card);border:1px solid var(--rim);border-radius:12px;padding:1.5rem;margin-bottom:.8rem;font-size:.9rem;line-height:1.8;color:var(--muted);}
.sum-block strong{color:var(--white);}
.right-item{display:flex;align-items:flex-start;gap:.65rem;padding:.65rem .9rem;background:var(--card);border-radius:8px;border-left:3px solid var(--jade);font-size:.82rem;color:var(--muted);margin-bottom:.4rem;}
.right-item span{color:var(--jade);flex-shrink:0;}
.faq-item{border-bottom:1px solid var(--rim);padding:.9rem 0;}
.faq-q{font-weight:700;font-size:.86rem;color:var(--white);margin-bottom:.4rem;}
.faq-a{font-size:.81rem;color:var(--muted);line-height:1.65;}
.lang-tag{display:inline-flex;align-items:center;gap:.3rem;background:rgba(0,87,168,.1);border:1px solid rgba(0,87,168,.25);border-radius:5px;padding:.22rem .65rem;font-family:'IBM Plex Mono',monospace;font-size:.62rem;color:var(--chakra);letter-spacing:.06em;margin:.2rem;}

/* COHORT/DATA */
.info-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;margin-bottom:1.4rem;}
.info-tile{background:var(--card);border:1px solid var(--rim);border-radius:12px;padding:1.2rem;}
.info-tv{font-family:'Playfair Display',serif;font-size:1.55rem;font-weight:700;letter-spacing:-.03em;color:var(--saffron);}
.info-tl{font-family:'IBM Plex Mono',monospace;font-size:.57rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-top:.3rem;}
.site-tag{display:inline-flex;align-items:center;gap:.3rem;background:rgba(56,189,248,.08);border:1px solid rgba(56,189,248,.2);color:var(--chakra);border-radius:5px;padding:.25rem .65rem;font-family:'IBM Plex Mono',monospace;font-size:.6rem;letter-spacing:.06em;margin:.22rem;}
.go-badge{display:inline-flex;align-items:center;gap:.4rem;padding:.45rem 1.1rem;border-radius:7px;font-weight:700;font-size:.78rem;letter-spacing:.07em;}
.go-green{background:rgba(0,200,150,.1);border:1px solid rgba(0,200,150,.3);color:var(--jade);}
.go-amber{background:rgba(255,153,51,.1);border:1px solid rgba(255,153,51,.3);color:var(--saffron);}
.go-red{background:rgba(230,57,70,.1);border:1px solid rgba(230,57,70,.3);color:var(--crimson);}

/* SIDEBAR */
.sb-card{background:var(--card);border:1px solid var(--rim);border-radius:16px;padding:1.7rem;margin-bottom:1.1rem;}
.sb-title{font-family:'IBM Plex Mono',monospace;font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;color:var(--saffron);margin-bottom:1.1rem;display:flex;align-items:center;gap:.5rem;}
.sb-title::before{content:'';width:12px;height:1px;background:var(--saffron);}
.feat-row{display:flex;align-items:flex-start;gap:.65rem;padding:.5rem 0;border-bottom:1px solid rgba(255,255,255,.03);font-size:.78rem;}
.feat-row:last-child{border:none;}
.feat-ico{width:20px;height:20px;border-radius:5px;background:rgba(255,153,51,.07);border:1px solid rgba(255,153,51,.15);display:flex;align-items:center;justify-content:center;font-size:.68rem;flex-shrink:0;margin-top:1px;}
.feat-name{color:#94a3b8;font-weight:500;}
.feat-note{font-family:'IBM Plex Mono',monospace;font-size:.57rem;color:var(--dim);letter-spacing:.06em;margin-top:1px;}
.competitor-row{display:grid;grid-template-columns:1fr auto auto auto;gap:.5rem;align-items:center;padding:.5rem 0;border-bottom:1px solid rgba(255,255,255,.03);font-size:.74rem;}
.competitor-row:last-child{border:none;}
.comp-name{color:var(--muted);}
.check-yes{color:var(--jade);font-size:.8rem;}
.check-no{color:var(--dim);font-size:.8rem;}

/* FOOTER */
.footer{margin-top:3.5rem;padding:1.7rem 2rem;background:var(--card);border:1px solid var(--rim);border-radius:14px;display:flex;justify-content:space-between;align-items:center;gap:1.5rem;flex-wrap:wrap;}
.footer-text{font-size:.74rem;color:var(--dim);line-height:1.7;max-width:54ch;}
.footer-text strong{color:var(--muted);}
.hackathon-seal{background:linear-gradient(135deg,rgba(255,153,51,.1),rgba(0,200,150,.05));border:1px solid rgba(255,153,51,.22);border-radius:10px;padding:.7rem 1.4rem;text-align:center;flex-shrink:0;}
.seal-top{font-family:'Playfair Display',serif;font-style:italic;font-size:.88rem;font-weight:700;color:var(--saffron);}
.seal-bot{font-family:'IBM Plex Mono',monospace;font-size:.54rem;color:var(--dim);letter-spacing:.1em;margin-top:.2rem;}

/* MISC */
.stSpinner>div{border-top-color:var(--saffron)!important;}
div[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--rim)!important;border-radius:12px!important;}
div[data-testid="stExpander"] summary{font-family:'Outfit',sans-serif!important;font-weight:700!important;color:var(--white)!important;font-size:.85rem!important;}
.stAlert{background:rgba(230,57,70,.06)!important;border:1px solid rgba(230,57,70,.2)!important;border-radius:9px!important;color:#fca5a5!important;}
#MainMenu,footer,header{visibility:hidden!important;}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
for k, v in [("result", None), ("patient_data", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
# MASTHEAD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="masthead">
  <div>
    <div class="brand-kicker">India-First Clinical Intelligence · AWS Bedrock</div>
    <div class="brand-wordmark">Trial<span class="accent">Guard</span> AI</div>
    <div class="brand-tagline">
      CDSCO Schedule Y &amp; FDA 21 CFR dual-compliance engine.<br>
      8 autonomous agents · Protocol Autopilot · Hindi patient education · Built for Bharat.
    </div>
  </div>
  <div class="masthead-right">
    <div class="aws-badge"><span class="live-dot"></span>AWS LAMBDA LIVE</div>
    <div class="agent-row">BEDROCK · POLLY · COMPREHEND · S3</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STAT STRIP
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="stat-strip">
  <div class="stat-cell"><div class="stat-v" style="--c:var(--saffron)">8</div><div class="stat-l">AI Agents</div></div>
  <div class="stat-cell"><div class="stat-v" style="--c:var(--chakra)">12<small>+</small></div><div class="stat-l">Compliance Clauses</div></div>
  <div class="stat-cell"><div class="stat-v" style="--c:var(--jade)">10K</div><div class="stat-l">Synthetic Patients</div></div>
  <div class="stat-cell"><div class="stat-v" style="--c:var(--gold)">9</div><div class="stat-l">ICF Languages</div></div>
  <div class="stat-cell"><div class="stat-v" style="--c:var(--crimson)">3</div><div class="stat-l">Autopilot Rounds</div></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
col_main, col_side = st.columns([3.2, 1], gap="large")

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with col_side:
    st.markdown('<div class="sb-card"><div class="sb-title">Platform Features</div>', unsafe_allow_html=True)
    for ico, name, note in [
        ("🇮🇳","CDSCO Schedule Y","12-clause compliance"),
        ("🇺🇸","FDA 21 CFR 312","13-clause IND checklist"),
        ("🔄","Protocol Autopilot","3-round autonomous fix"),
        ("🏥","Patient Mode","English + Hindi education"),
        ("🗣️","Polly Aditi TTS","Hindi voice narration"),
        ("🏨","India Site DB","AIIMS·CMC·KEM·JIPMER+"),
        ("🧬","SDV Cohort","10K Indian demographics"),
        ("🛡️","Zero PHI","No real patient data"),
    ]:
        st.markdown(f'<div class="feat-row"><div class="feat-ico">{ico}</div><div><div class="feat-name">{name}</div><div class="feat-note">{note}</div></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-card"><div class="sb-title">Competitor Gap</div>', unsafe_allow_html=True)
    st.markdown('<div style="display:grid;grid-template-columns:1fr auto auto auto;gap:.3rem;font-family:\'IBM Plex Mono\',monospace;font-size:.54rem;letter-spacing:.08em;color:var(--dim);margin-bottom:.6rem;"><span></span><span>CDSCO</span><span>Hindi</span><span>Auto</span></div>', unsafe_allow_html=True)
    for name, c, h, a in [("TrialGuard",True,True,True),("Medidata",False,False,False),("Veeva",False,False,False),("Oracle HC",False,False,False)]:
        y = '<span class="check-yes">✓</span>'; n = '<span class="check-no">—</span>'
        b = 'style="color:var(--saffron);font-weight:700;"' if name=="TrialGuard" else ""
        st.markdown(f'<div class="competitor-row"><span class="comp-name" {b}>{name}</span>{y if c else n}{y if h else n}{y if a else n}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─── MAIN CONTENT ──────────────────────────────────────────────────────────────
with col_main:
    tab1, tab2, tab3 = st.tabs(["🧬  Protocol Design", "🏥  Patient Education", "📊  Cohort & Sites"])

    # ══ TAB 1 — PROTOCOL DESIGN ═══════════════════════════════════════════════
    with tab1:
        r1, r2 = st.columns(2)
        with r1:
            language = st.selectbox("Output Language", ["English (EN)", "हिंदी (HI)"])
            lang_code = "hi" if "HI" in language else "en"
        with r2:
            mode_sel = st.selectbox("Generation Mode", ["⚡ Standard — Fast (~20s)", "🔄 Autopilot — 3-Round Self-Improvement (~90s)"])
            autopilot = "Autopilot" in mode_sel

        trial_text = st.text_area(
            "Trial Description",
            placeholder="Disease · Phase · Patient population · India site preferences...",
            value="Design a Phase 2 RCT for a novel oral anti-diabetic agent in elderly Indian patients (age 60-80) with HbA1c > 8.0, focusing on CDSCO Schedule Y compliance and enrollment from AIIMS New Delhi, CMC Vellore, and JIPMER Puducherry.",
            height=118
        )

        if autopilot:
            rounds = st.slider("Improvement Rounds (API Gateway: use 1, local: up to 3)", 1, 3, 2)
        else:
            rounds = 1

        run_btn = st.button("🔄  Run Protocol Autopilot" if autopilot else "🧬  Generate Protocol")

        if run_btn:
            pb = st.progress(0)
            st_lbl = st.empty()
            seq = ([
                (0,14,"Spawning 8-agent compliance swarm"),
                (14,32,"FDA 21 CFR 312 — 13 clauses"),
                (32,50,"CDSCO Schedule Y — 12 clauses"),
                (50,65,"Autopilot Round 1 — patching gaps"),
                (65,80,"Autopilot Round 2 — rescoring"),
                (80,96,"Generating PDF report + TTS audio"),
            ] if autopilot else [
                (0,18,"Spawning 8-agent compliance swarm"),
                (18,42,"Running FDA 21 CFR + CDSCO Schedule Y"),
                (42,65,"Synthesising 10K Indian patient cohort"),
                (65,87,"Scoring feasibility across India sites"),
                (87,98,"Generating PDF report + TTS audio"),
            ])
            for s, e, lbl in seq:
                for v in range(s, e):
                    time.sleep(0.02)
                    pb.progress(v)
                st_lbl.markdown(f'<p style="font-family:\'IBM Plex Mono\',monospace;font-size:.68rem;color:var(--saffron);letter-spacing:.1em;margin:.3rem 0 0;">◈  {lbl.upper()}</p>', unsafe_allow_html=True)

            try:
                if autopilot:
                    resp = requests.post(f"{BASE_URL}/autopilot",
                        json={"text": trial_text, "language": lang_code, "max_rounds": rounds}, timeout=200)
                else:
                    resp = requests.post(f"{BASE_URL}/design-trial",
                        json={"text": trial_text, "language": lang_code}, timeout=40)

                pb.progress(100); pb.empty(); st_lbl.empty()

                if resp.status_code == 200:
                    st.session_state.result = resp.json()
                    st.session_state.result["_mode"] = "autopilot" if autopilot else "standard"
                    st.session_state.patient_data = None
                else:
                    st.error(f"API {resp.status_code}: {resp.text[:300]}")

            except requests.exceptions.Timeout:
                pb.empty(); st_lbl.empty()
                st.error("Timed out. For Autopilot use max_rounds=1 on API Gateway (29s limit), or run locally.")
            except Exception as ex:
                pb.empty(); st_lbl.empty()
                st.error(f"Error: {ex}")

        # ── RESULTS ──────────────────────────────────────────────────────────
        if st.session_state.result:
            r = st.session_state.result
            fda   = r.get("fda_score", 0)
            cdsco = r.get("cdsco_score", 0)
            feas  = r.get("feasibility", "–")
            sid   = r.get("session_id", "–")
            mode_used = r.get("_mode", "standard")
            feas_c = "var(--jade)" if feas=="High" else ("var(--saffron)" if feas=="Medium" else "var(--crimson)")

            proto_title = r.get("protocol", {}).get("title", "Protocol Generated")
            st.markdown(f"""
            <div class="result-header">
              <div class="result-icon">✓</div>
              <div>
                <div class="result-title">{proto_title[:65]}{"..." if len(proto_title)>65 else ""}</div>
                <div class="result-meta">SESSION {sid.upper()} · {r.get("elapsed_seconds","–")}s · {"AUTOPILOT" if mode_used=="autopilot" else "STANDARD MODE"}</div>
              </div>
            </div>
            <div class="score-row">
              <div class="score-card" style="--ac:var(--chakra)">
                <div class="score-badge">FDA 21 CFR 312</div>
                <div class="score-num" style="color:var(--chakra)">{fda}<small>/100</small></div>
                <div class="score-lbl">FDA Compliance Score</div>
                <div class="score-sub">Grade {r.get("fda_grade","–")} · {r.get("fda_submission_readiness","–")}</div>
              </div>
              <div class="score-card" style="--ac:var(--saffron)">
                <div class="score-badge">CDSCO SCHEDULE Y</div>
                <div class="score-num" style="color:var(--saffron)">{cdsco}<small>/100</small></div>
                <div class="score-lbl">India Compliance Score</div>
                <div class="score-sub">Grade {r.get("cdsco_grade","–")} · {r.get("cdsco_submission_status","–")}</div>
              </div>
              <div class="score-card" style="--ac:{feas_c}">
                <div class="score-badge">INDIA FEASIBILITY</div>
                <div class="score-num" style="color:{feas_c};font-size:2.2rem;margin-top:.2rem">{feas}</div>
                <div class="score-lbl">Site Feasibility Rating</div>
                <div class="score-sub">{r.get("go_no_go","–")}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Autopilot bars
            if mode_used == "autopilot" and r.get("autopilot"):
                ap = r["autopilot"]
                df = ap.get("score_delta_fda", 0)
                dc = ap.get("score_delta_cdsco", 0)
                st.markdown(f"""
                <div class="ap-wrap">
                  <div class="ap-header">
                    <div class="ap-title">🔄 Autopilot Score Progression
                      <span class="ap-chip">{ap.get("total_rounds_run",0)} ROUNDS</span>
                    </div>
                    <div class="delta-row">
                      <span class="delta {'delta-up' if df>=0 else 'delta-flat'}">FDA {"+" if df>=0 else ""}{df}</span>
                      <span class="delta {'delta-up' if dc>=0 else 'delta-flat'}">CDSCO {"+" if dc>=0 else ""}{dc}</span>
                    </div>
                  </div>
                """, unsafe_allow_html=True)
                for rnd in ap.get("score_progression", []):
                    fs = rnd.get("fda_score", 0)
                    cs = rnd.get("cdsco_score", 0)
                    lbl = rnd.get("label", f"Round {rnd.get('round',0)}")
                    st.markdown(f"""
                    <div class="round-row">
                      <div class="round-lbl">{lbl}</div>
                      <div><div class="bar-label">FDA</div><div class="bar-track"><div class="bar-fill" style="--bc:var(--chakra);width:{fs}%"></div></div></div>
                      <div><div class="bar-label">CDSCO</div><div class="bar-track"><div class="bar-fill" style="--bc:var(--saffron);width:{cs}%"></div></div></div>
                      <div class="round-scores">{fs} / {cs}</div>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Compliance gaps
            st.markdown('<div class="sec-hdr"><span class="n">01</span>Compliance Gaps</div>', unsafe_allow_html=True)
            ca, cb = st.columns(2)
            with ca:
                st.markdown("**🇺🇸 FDA Issues**")
                fda_gaps = r.get("fda_clauses_failed", [])
                if fda_gaps:
                    st.markdown('<div class="chip-list">', unsafe_allow_html=True)
                    for g in fda_gaps[:4]:
                        ref   = (g.get("ref","") if isinstance(g,dict) else "")
                        issue = (g.get("issue","") if isinstance(g,dict) else str(g))[:85]
                        st.markdown(f'<div class="chip"><div class="chip-dot" style="background:var(--chakra)"></div><span><strong style="color:#94a3b8;font-size:.68rem">{ref} </strong>{issue}</span></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.success("No FDA gaps detected")
            with cb:
                st.markdown("**🇮🇳 India-Specific CDSCO Gaps**")
                india_gaps = r.get("unique_india_gaps", [])
                if india_gaps:
                    st.markdown('<div class="chip-list">', unsafe_allow_html=True)
                    for g in india_gaps[:4]:
                        st.markdown(f'<div class="chip"><div class="chip-dot" style="background:var(--saffron)"></div>{str(g)[:100]}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.success("No India-specific gaps")

            st.markdown('<div class="sec-hdr"><span class="n">02</span>Full Protocol</div>', unsafe_allow_html=True)
            with st.expander("View Complete Protocol JSON"):
                st.json(r.get("protocol", {}))

            st.markdown('<div class="sec-hdr"><span class="n">03</span>Downloads</div>', unsafe_allow_html=True)
            pdf_url   = r.get("pdf_url","")
            audio_url = r.get("audio_url","")
            st.markdown('<div class="dl-pair">', unsafe_allow_html=True)
            if pdf_url and pdf_url.startswith("https://"):
                st.markdown(f'<a href="{pdf_url}" target="_blank" class="dl-card"><div class="dl-ico" style="background:rgba(56,189,248,.1)">📄</div><div><div class="dl-name">Protocol PDF</div><div class="dl-meta">Full Compliance Report · S3</div></div></a>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="dl-card" style="opacity:.4"><div class="dl-ico">📄</div><div><div class="dl-name">PDF Unavailable</div><div class="dl-meta">Not generated</div></div></div>', unsafe_allow_html=True)
            if audio_url and audio_url.startswith("https://"):
                st.markdown(f'<a href="{audio_url}" target="_blank" class="dl-card"><div class="dl-ico" style="background:rgba(255,153,51,.1)">🔊</div><div><div class="dl-name">Dr. Protocol Audio</div><div class="dl-meta">{"Hindi Polly Aditi" if lang_code=="hi" else "English TTS"} · MP3</div></div></a>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ══ TAB 2 — PATIENT EDUCATION ═════════════════════════════════════════════
    with tab2:
        if not st.session_state.result:
            st.markdown('<div style="text-align:center;padding:4rem 2rem;"><div style="font-size:2.5rem;margin-bottom:1rem">🏥</div><div style="font-family:\'IBM Plex Mono\',monospace;font-size:.72rem;letter-spacing:.1em;color:var(--dim)">GENERATE A PROTOCOL FIRST IN THE PROTOCOL DESIGN TAB</div></div>', unsafe_allow_html=True)
        else:
            r = st.session_state.result

            if st.session_state.patient_data is None:
                st.markdown('<div class="sb-card"><div class="sb-title">Generate Patient Education</div><div style="font-size:.84rem;color:var(--muted);margin-bottom:1.2rem;line-height:1.7">Bilingual English + Hindi patient guide, FAQ, visit timeline, and Polly Aditi audio — CDSCO Schedule Y Appendix V compliant.</div></div>', unsafe_allow_html=True)
                if st.button("🏥  Generate Patient Education Content"):
                    with st.spinner("Generating bilingual content..."):
                        try:
                            pr = requests.post(f"{BASE_URL}/patient-summary",
                                json={"session_id": r.get("session_id","s"), "protocol": r.get("protocol",{}), "language": "en"}, timeout=45)
                            if pr.status_code == 200:
                                st.session_state.patient_data = pr.json()
                                st.rerun()
                            else:
                                st.error(f"API {pr.status_code}: {pr.text[:200]}")
                        except Exception as ex:
                            st.error(f"Error: {ex}")

            if st.session_state.patient_data:
                pd_res = st.session_state.patient_data
                ps     = pd_res.get("patient_summary", {})

                ae = pd_res.get("audio_url_english","")
                ah = pd_res.get("audio_url_hindi","")
                if ae or ah:
                    st.markdown('<div class="sec-hdr"><span class="n">01</span>Patient Audio Guides</div>', unsafe_allow_html=True)
                    ac1, ac2 = st.columns(2)
                    with ac1:
                        if ae and ae.startswith("https://"):
                            st.markdown(f'<a href="{ae}" target="_blank" class="dl-card"><div class="dl-ico" style="background:rgba(56,189,248,.1)">🔊</div><div><div class="dl-name">English Audio Guide</div><div class="dl-meta">Dr. Protocol · MP3</div></div></a>', unsafe_allow_html=True)
                    with ac2:
                        if ah and ah.startswith("https://"):
                            st.markdown(f'<a href="{ah}" target="_blank" class="dl-card"><div class="dl-ico" style="background:rgba(255,153,51,.1)">🔊</div><div><div class="dl-name">हिंदी गाइड</div><div class="dl-meta">Polly Aditi · MP3</div></div></a>', unsafe_allow_html=True)

                lang_pick = st.radio("View in", ["English", "हिंदी"], horizontal=True)
                use_hi = lang_pick == "हिंदी"

                if use_hi:
                    hi = ps.get("patient_summary_hindi", {})
                    st.markdown('<div class="sec-hdr"><span class="n">02</span>परीक्षण की जानकारी</div>', unsafe_allow_html=True)
                    for key, lbl in [("what_is_this_trial","यह परीक्षण क्या है?"),("duration_simple","अवधि"),("will_it_cost_me","क्या कोई खर्च है?"),("is_it_safe","क्या यह सुरक्षित है?")]:
                        if hi.get(key): st.markdown(f'<div class="sum-block"><strong>{lbl}: </strong>{hi[key]}</div>', unsafe_allow_html=True)
                    rights_hi = hi.get("your_rights",[])
                    if rights_hi:
                        st.markdown('<div class="sec-hdr"><span class="n">03</span>आपके अधिकार — CDSCO Schedule Y</div>', unsafe_allow_html=True)
                        for right in rights_hi:
                            st.markdown(f'<div class="right-item"><span>✓</span>{right}</div>', unsafe_allow_html=True)
                else:
                    en = ps.get("patient_summary_english", {})
                    st.markdown('<div class="sec-hdr"><span class="n">02</span>About This Trial</div>', unsafe_allow_html=True)
                    if en.get("what_is_this_trial"): st.markdown(f'<div class="sum-block">{en["what_is_this_trial"]}</div>', unsafe_allow_html=True)
                    pc1, pc2 = st.columns(2)
                    with pc1:
                        for key, lbl in [("duration_simple","Duration"),("will_it_cost_me","Cost to you")]:
                            if en.get(key): st.markdown(f'<div class="sum-block"><strong>{lbl}:</strong> {en[key]}</div>', unsafe_allow_html=True)
                    with pc2:
                        for key, lbl in [("is_it_safe","Safety"),("who_can_join","Who can join")]:
                            if en.get(key): st.markdown(f'<div class="sum-block"><strong>{lbl}:</strong> {en[key]}</div>', unsafe_allow_html=True)

                    rights = en.get("your_rights",[])
                    if rights:
                        st.markdown('<div class="sec-hdr"><span class="n">03</span>Your Rights — CDSCO Schedule Y Appendix V</div>', unsafe_allow_html=True)
                        for right in rights: st.markdown(f'<div class="right-item"><span>✓</span>{right}</div>', unsafe_allow_html=True)

                    faq = ps.get("patient_faq",[])
                    if faq:
                        st.markdown('<div class="sec-hdr"><span class="n">04</span>Patient FAQ — Bilingual</div>', unsafe_allow_html=True)
                        for item in faq[:6]:
                            if isinstance(item,dict) and item.get("question_en"):
                                hi_line = f'<div class="faq-a" style="color:var(--saffron);font-size:.78rem;margin-top:.3rem">🇮🇳 {item.get("question_hi","")}</div>' if item.get("question_hi") else ""
                                st.markdown(f'<div class="faq-item"><div class="faq-q">Q: {item["question_en"]}</div><div class="faq-a">{item.get("answer_en","")}</div>{hi_line}</div>', unsafe_allow_html=True)

                langs = pd_res.get("languages_available",[])
                if langs:
                    st.markdown('<div class="sec-hdr"><span class="n">05</span>Available ICF Languages</div>', unsafe_allow_html=True)
                    st.markdown('<div style="margin:.5rem 0">' + "".join([f'<span class="lang-tag">🌐 {l}</span>' for l in langs]) + '</div>', unsafe_allow_html=True)

                st.markdown(f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:.58rem;color:var(--dim);padding:.7rem 1rem;background:var(--card);border-radius:8px;margin-top:1.2rem;letter-spacing:.06em">{pd_res.get("regulatory_basis","")}</div>', unsafe_allow_html=True)

    # ══ TAB 3 — COHORT & SITES ════════════════════════════════════════════════
    with tab3:
        if not st.session_state.result:
            st.markdown('<div style="text-align:center;padding:4rem 2rem;"><div style="font-size:2.5rem;margin-bottom:1rem">📊</div><div style="font-family:\'IBM Plex Mono\',monospace;font-size:.72rem;letter-spacing:.1em;color:var(--dim)">GENERATE A PROTOCOL FIRST</div></div>', unsafe_allow_html=True)
        else:
            r = st.session_state.result
            cohort = r.get("cohort", {})
            sites  = r.get("recommended_sites", [])
            months = r.get("enrollment_months_estimate", 0)
            go     = r.get("go_no_go", "GO WITH CONDITIONS")

            st.markdown('<div class="sec-hdr"><span class="n">01</span>SDV Indian Patient Cohort</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="info-grid">
              <div class="info-tile"><div class="info-tv">{cohort.get("cohort_size",10000):,}</div><div class="info-tl">Synthetic Patients</div></div>
              <div class="info-tile"><div class="info-tv">{cohort.get("eligibility_rate_pct",0)}%</div><div class="info-tl">Eligibility Rate</div></div>
              <div class="info-tile"><div class="info-tv">{cohort.get("recommended_total_n",0)}</div><div class="info-tl">Adjusted N</div></div>
              <div class="info-tile"><div class="info-tv">{cohort.get("mean_dropout_pct",0)}%</div><div class="info-tl">Predicted Dropout</div></div>
              <div class="info-tile"><div class="info-tv">{cohort.get("disease","–").title()}</div><div class="info-tl">Disease Category</div></div>
              <div class="info-tile"><div class="info-tv">{len(cohort.get("languages_required",[]))}</div><div class="info-tl">ICF Languages Required</div></div>
            </div>
            """, unsafe_allow_html=True)

            langs_req = cohort.get("languages_required",[])
            if langs_req:
                st.markdown('<div style="margin-bottom:1.2rem">' + "".join([f'<span class="lang-tag">{l}</span>' for l in langs_req]) + '</div>', unsafe_allow_html=True)

            insights = cohort.get("india_specific_insights",[])
            if insights:
                st.markdown('<div class="sec-hdr"><span class="n">02</span>India-Specific Insights</div>', unsafe_allow_html=True)
                st.markdown('<div class="chip-list">' + "".join([f'<div class="chip"><div class="chip-dot" style="background:var(--gold)"></div>{i}</div>' for i in insights[:4]]) + '</div>', unsafe_allow_html=True)

            st.markdown('<div class="sec-hdr"><span class="n">03</span>Recommended India Sites</div>', unsafe_allow_html=True)
            go_cls = "go-green" if ("GO" in go and "NO" not in go and "CONDITION" not in go) else ("go-amber" if "CONDITION" in go else "go-red")
            go_lbl = "✓ GO" if go_cls=="go-green" else ("⚡ GO WITH CONDITIONS" if go_cls=="go-amber" else "✗ NO-GO")
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.2rem;">
              <span class="go-badge {go_cls}">{go_lbl}</span>
              <span style="font-family:'IBM Plex Mono',monospace;font-size:.6rem;color:var(--muted)">{months} months estimated enrollment</span>
            </div>
            <div style="margin-bottom:1rem">{"".join([f'<span class="site-tag">🏥 {s}</span>' for s in sites])}</div>
            """, unsafe_allow_html=True)

            gaps = r.get("regional_gaps",[])
            if gaps:
                st.markdown('<div class="sec-hdr"><span class="n">04</span>Regional Coverage Gaps</div>', unsafe_allow_html=True)
                st.markdown('<div class="chip-list">' + "".join([f'<div class="chip"><div class="chip-dot" style="background:var(--crimson)"></div>Coverage gap: {g}</div>' for g in gaps]) + '</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
  <div class="footer-text">
    <strong>Hackathon Notice</strong> — Synthetic data only. Not for actual clinical use.<br>
    AI guidance requires qualified regulatory review. FDA/CDSCO scores are supportive tools, not certification.
  </div>
  <div class="hackathon-seal">
    <div class="seal-top">🇮🇳 AI for Bharat 2026</div>
    <div class="seal-bot">AWS BEDROCK · LAMBDA · POLLY · S3</div>
  </div>
</div>
""", unsafe_allow_html=True)