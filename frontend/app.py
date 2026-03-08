"""
TrialGuard AI — Hackathon Edition
India-First Clinical Trial Protocol Generator
Run: streamlit run app.py
"""
import streamlit as st
import requests
import time

BASE_URL = "https://t5whevmrmk.execute-api.us-east-1.amazonaws.com"

st.set_page_config(
    page_title="TrialGuard AI · India-First Clinical Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# FULL CSS DESIGN SYSTEM — Cormorant × Space Grotesk × JetBrains Mono
# Luxury Biotech Editorial · Deep Navy + Flame Orange
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,600;0,700;1,300;1,600&family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
  --void:#020408; --abyss:#05080f; --deep:#080d19; --surface:#0c1220;
  --panel:#101828; --raised:#141f30; --highlight:#1a2840;
  --wire:rgba(255,255,255,.05); --wire2:rgba(255,255,255,.09); --wire3:rgba(255,255,255,.14);
  --flame:#FF6B00; --flame2:#FF9040; --flame3:#cc5500;
  --jade:#00C896; --aqua:#00D4FF; --crimson:#FF3355;
  --amber:#FFB800; --indigo:#6366F1;
  --ink:#E8F0FF; --ink2:#8899BB; --ink3:#3A4D6B; --ink4:#1E2D44;
  --serif:'Cormorant Garamond',Georgia,serif;
  --sans:'Space Grotesk',system-ui,sans-serif;
  --mono:'JetBrains Mono','Courier New',monospace;
}

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,.stApp{
  background:var(--void)!important;
  font-family:var(--sans)!important;
  color:var(--ink)!important;
  -webkit-font-smoothing:antialiased;
}

/* Ambient mesh */
.stApp::before{
  content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(ellipse 90% 60% at -15% -10%, rgba(255,107,0,.11) 0%, transparent 55%),
    radial-gradient(ellipse 70% 50% at 115%  10%, rgba(0,200,150,.08) 0%, transparent 50%),
    radial-gradient(ellipse 55% 80% at  55% 110%, rgba(0,212,255,.06) 0%, transparent 60%),
    radial-gradient(ellipse 40% 40% at  85%  55%, rgba(99,102,241,.05) 0%, transparent 50%);
}
/* Grid lines */
.stApp::after{
  content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:
    linear-gradient(rgba(255,255,255,.018) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.018) 1px,transparent 1px);
  background-size:72px 72px;
  mask-image:radial-gradient(ellipse 80% 80% at 50% 50%,black 30%,transparent 100%);
}
.main .block-container{
  padding:0 3rem 6rem!important;max-width:1440px!important;
  position:relative;z-index:1;
}

/* ── NAV ── */
.tg-nav{
  display:flex;align-items:center;justify-content:space-between;
  padding:1.5rem 0;border-bottom:1px solid var(--wire);margin-bottom:0;
}
.tg-brand{display:flex;align-items:center;gap:.8rem;}
.tg-hex{
  width:32px;height:32px;
  background:linear-gradient(135deg,var(--flame),var(--flame3));
  clip-path:polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%);
  display:flex;align-items:center;justify-content:center;
  font-size:.6rem;color:#fff;font-weight:700;font-family:var(--mono);
  animation:hex-pulse 3s ease-in-out infinite;
}
@keyframes hex-pulse{0%,100%{filter:drop-shadow(0 0 6px rgba(255,107,0,.5));}50%{filter:drop-shadow(0 0 16px rgba(255,107,0,.9));}}
.tg-name{font-family:var(--serif);font-size:1.4rem;font-weight:600;letter-spacing:-.02em;}
.tg-name em{font-style:italic;color:var(--flame);}
.tg-right{display:flex;align-items:center;gap:.8rem;flex-wrap:wrap;}
.tg-live{
  display:flex;align-items:center;gap:.45rem;padding:.3rem .9rem;
  border:1px solid rgba(0,200,150,.25);border-radius:100px;
  font-family:var(--mono);font-size:.58rem;letter-spacing:.15em;color:var(--jade);
  background:rgba(0,200,150,.06);
}
.tg-dot{
  width:5px;height:5px;border-radius:50%;background:var(--jade);
  box-shadow:0 0 6px var(--jade);animation:blink-dot 1.8s ease-in-out infinite;
}
@keyframes blink-dot{0%,100%{opacity:1;box-shadow:0 0 4px var(--jade);}50%{opacity:.4;box-shadow:0 0 14px var(--jade),0 0 28px rgba(0,200,150,.3);}}
.tg-tag{
  font-family:var(--mono);font-size:.52rem;letter-spacing:.1em;color:var(--ink3);
  background:var(--wire);border:1px solid var(--wire);border-radius:4px;padding:.2rem .55rem;
}

/* ── STATS RIBBON ── */
.ribbon{
  display:grid;grid-template-columns:repeat(5,1fr);
  gap:1px;background:var(--wire);border-radius:0 0 18px 18px;
  overflow:hidden;margin-bottom:3rem;border:1px solid var(--wire);border-top:none;
}
.rib-cell{
  background:var(--deep);padding:1.7rem 1.5rem;position:relative;overflow:hidden;
  cursor:default;transition:background .3s;
}
.rib-cell:hover{background:var(--surface);}
.rib-cell::after{
  content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
  background:var(--rc);box-shadow:0 0 15px var(--rc);opacity:0;transition:opacity .3s;
}
.rib-cell:hover::after{opacity:1;}
.rib-val{
  font-family:var(--serif);font-size:2.5rem;font-weight:600;
  line-height:1;letter-spacing:-.05em;color:var(--rc,var(--jade));
}
.rib-val sub{font-size:1rem;opacity:.45;font-weight:300;}
.rib-lbl{font-family:var(--mono);font-size:.53rem;letter-spacing:.2em;text-transform:uppercase;color:var(--ink3);margin-top:.4rem;}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{gap:0!important;background:transparent!important;border-bottom:1px solid var(--wire)!important;margin-bottom:2.5rem!important;}
.stTabs [data-baseweb="tab"]{font-family:var(--mono)!important;font-size:.62rem!important;letter-spacing:.2em!important;text-transform:uppercase!important;color:var(--ink3)!important;background:transparent!important;border:none!important;border-bottom:1.5px solid transparent!important;padding:.9rem 1.8rem!important;margin-bottom:-1px!important;transition:all .2s!important;}
.stTabs [data-baseweb="tab"]:hover{color:rgba(232,240,255,.6)!important;}
.stTabs [aria-selected="true"]{color:var(--flame)!important;border-bottom-color:var(--flame)!important;}
.stTabs [data-baseweb="tab-panel"]{padding:0!important;}
.stTabs [data-baseweb="tab-highlight"]{display:none!important;}

/* ── FORM CONTROLS ── */
.stSelectbox label,.stTextArea label,.stSlider label,.stRadio label{font-family:var(--mono)!important;font-size:.56rem!important;letter-spacing:.22em!important;text-transform:uppercase!important;color:var(--ink3)!important;}
.stTextArea textarea{background:var(--surface)!important;border:1px solid var(--wire2)!important;border-radius:14px!important;color:var(--ink)!important;font-family:var(--sans)!important;font-size:.9rem!important;line-height:1.7!important;transition:border-color .25s,box-shadow .25s!important;padding:1rem 1.2rem!important;}
.stTextArea textarea:focus{border-color:rgba(255,107,0,.4)!important;box-shadow:0 0 0 3px rgba(255,107,0,.07)!important;}
.stSelectbox>div>div{background:var(--surface)!important;border:1px solid var(--wire2)!important;border-radius:12px!important;color:var(--ink)!important;}

/* ── CTA BUTTON ── */
.stButton>button{
  width:100%!important;height:56px!important;
  background:linear-gradient(135deg,var(--flame),var(--flame3))!important;
  border:none!important;border-radius:14px!important;
  color:#fff!important;font-family:var(--sans)!important;
  font-weight:700!important;font-size:.82rem!important;
  letter-spacing:.16em!important;text-transform:uppercase!important;
  box-shadow:0 8px 32px rgba(255,107,0,.35),0 1px 0 rgba(255,255,255,.12) inset!important;
  transition:all .25s cubic-bezier(.34,1.5,.64,1)!important;
}
.stButton>button:hover{transform:translateY(-2px) scale(1.008)!important;box-shadow:0 16px 48px rgba(255,107,0,.55)!important;}
.stButton>button:active{transform:translateY(0)!important;}

/* ── PROGRESS ── */
.stProgress>div>div>div{background:linear-gradient(90deg,var(--flame),var(--jade))!important;box-shadow:0 0 14px rgba(255,107,0,.6)!important;}
.stProgress>div>div{background:var(--ink4)!important;border-radius:99px!important;}

/* ── SECTION HEADER ── */
.sh{display:flex;align-items:center;gap:.9rem;margin:2.5rem 0 1.5rem;}
.sh-n{font-family:var(--mono);font-size:.52rem;letter-spacing:.12em;color:var(--flame);background:rgba(255,107,0,.08);border:1px solid rgba(255,107,0,.18);border-radius:4px;padding:.15rem .5rem;flex-shrink:0;}
.sh-t{font-family:var(--mono);font-size:.56rem;letter-spacing:.25em;text-transform:uppercase;color:var(--ink4);}
.sh::after{content:'';flex:1;height:1px;background:var(--wire);}

/* ── RESULT BANNER ── */
.rbanner{display:flex;align-items:center;gap:1.2rem;padding:1.4rem 2rem;background:linear-gradient(135deg,rgba(255,107,0,.05),rgba(0,200,150,.03));border:1px solid rgba(255,107,0,.18);border-radius:18px;margin-bottom:2rem;position:relative;overflow:hidden;}
.rbanner::before{content:'';position:absolute;top:0;left:0;right:0;height:1.5px;background:linear-gradient(90deg,var(--flame),var(--jade),var(--aqua));}
.rb-ico{width:44px;height:44px;border-radius:12px;flex-shrink:0;background:rgba(0,200,150,.1);border:1px solid rgba(0,200,150,.25);display:grid;place-items:center;font-size:1.1rem;}
.rb-title{font-family:var(--serif);font-size:1.05rem;font-weight:600;letter-spacing:-.01em;}
.rb-meta{font-family:var(--mono);font-size:.57rem;color:var(--ink3);letter-spacing:.1em;margin-top:.25rem;}

/* ── SCORE TRIO ── */
.strio{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:2rem;}
.scard{background:var(--panel);border:1px solid var(--wire2);border-radius:20px;padding:1.8rem 1.6rem;position:relative;overflow:hidden;transition:transform .25s,box-shadow .25s;}
.scard:hover{transform:translateY(-2px);box-shadow:0 20px 50px rgba(0,0,0,.4);}
.scard::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--ac);box-shadow:0 0 24px var(--ac),0 0 48px color-mix(in srgb,var(--ac) 40%,transparent);}
.scard::after{content:'';position:absolute;bottom:-25px;right:-25px;width:110px;height:110px;border-radius:50%;background:color-mix(in srgb,var(--ac) 5%,transparent);border:1px solid color-mix(in srgb,var(--ac) 12%,transparent);}
.sc-tag{font-family:var(--mono);font-size:.52rem;letter-spacing:.18em;text-transform:uppercase;color:var(--ac);background:color-mix(in srgb,var(--ac) 9%,transparent);border:1px solid color-mix(in srgb,var(--ac) 22%,transparent);border-radius:4px;padding:.18rem .55rem;display:inline-block;margin-bottom:.9rem;}
.sc-num{font-family:var(--serif);font-size:3.6rem;font-weight:600;line-height:.9;letter-spacing:-.06em;color:var(--ac);}
.sc-den{font-size:1.5rem;opacity:.28;font-weight:300;}
.sc-lbl{font-size:.76rem;color:var(--ink2);margin-top:.55rem;font-weight:500;}
.sc-sub{font-family:var(--mono);font-size:.57rem;color:var(--ink3);margin-top:.22rem;letter-spacing:.05em;}

/* ── AUTOPILOT ── */
.apbox{background:var(--panel);border:1px solid var(--wire2);border-radius:20px;padding:2rem 2.2rem;margin-bottom:2rem;position:relative;overflow:hidden;}
.apbox::before{content:'';position:absolute;top:0;left:0;right:0;height:1.5px;background:linear-gradient(90deg,transparent,var(--jade),transparent);}
.aphead{display:flex;align-items:center;justify-content:space-between;margin-bottom:1.8rem;}
.aptitle{font-family:var(--serif);font-size:1.25rem;font-weight:600;letter-spacing:-.02em;display:flex;align-items:center;gap:.8rem;}
.apbadge{font-family:var(--mono);font-size:.55rem;letter-spacing:.12em;background:rgba(0,200,150,.08);border:1px solid rgba(0,200,150,.2);color:var(--jade);border-radius:5px;padding:.2rem .6rem;}
.dpair{display:flex;gap:.5rem;}
.dt{font-family:var(--mono);font-size:.6rem;padding:.25rem .7rem;border-radius:5px;letter-spacing:.05em;}
.dup{background:rgba(0,200,150,.1);color:var(--jade);border:1px solid rgba(0,200,150,.2);}
.dfl{background:rgba(58,77,107,.2);color:var(--ink3);border:1px solid var(--wire);}
.rrow{display:grid;grid-template-columns:100px 1fr 1fr 78px;gap:.9rem;align-items:center;padding:.9rem 1.1rem;background:var(--surface);border:1px solid var(--wire);border-radius:12px;margin-bottom:.45rem;transition:all .2s;}
.rrow:hover{border-color:var(--wire2);background:var(--raised);}
.rlbl{font-family:var(--mono);font-size:.57rem;color:var(--ink3);letter-spacing:.07em;}
.btrack{height:4px;background:var(--ink4);border-radius:3px;overflow:hidden;margin-top:.25rem;}
.bfill{height:100%;border-radius:3px;background:var(--bc);box-shadow:0 0 10px var(--bc);}
.blbl{font-family:var(--mono);font-size:.5rem;color:var(--ink3);margin-bottom:.22rem;letter-spacing:.07em;}
.rscore{font-family:var(--mono);font-size:.68rem;font-weight:500;color:var(--ink);text-align:right;}

/* ── CHIPS ── */
.chips{display:flex;flex-wrap:wrap;gap:.5rem;margin:.5rem 0 1.2rem;}
.chip{display:flex;align-items:flex-start;gap:.5rem;padding:.6rem .95rem;background:var(--raised);border:1px solid var(--wire);border-radius:9px;font-size:.77rem;color:var(--ink2);line-height:1.45;max-width:350px;transition:all .2s;}
.chip:hover{border-color:var(--wire2);color:var(--ink);}
.cdot{width:5px;height:5px;border-radius:50%;flex-shrink:0;margin-top:5px;}

/* ── DOWNLOAD CARDS ── */
.dlgrid{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1.5rem 0 2rem;}
.dlc{position:relative;display:block;border-radius:20px;overflow:hidden;background:var(--panel);border:1px solid var(--wire2);text-decoration:none!important;cursor:pointer;transition:transform .3s cubic-bezier(.34,1.4,.64,1),border-color .3s,box-shadow .3s;}
.dlc:hover{transform:translateY(-5px) scale(1.015);border-color:rgba(255,255,255,.14);box-shadow:0 24px 64px rgba(0,0,0,.5),0 0 0 1px rgba(255,255,255,.06);}
.dlc::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;z-index:3;background:linear-gradient(90deg,var(--da),var(--db));box-shadow:0 0 24px var(--da),0 0 48px color-mix(in srgb,var(--da) 30%,transparent);}
.dlc::after{content:'';position:absolute;inset:0;z-index:1;pointer-events:none;background:linear-gradient(110deg,transparent 30%,rgba(255,255,255,.03) 50%,transparent 70%);transform:translateX(-100%);transition:transform .7s ease;}
.dlc:hover::after{transform:translateX(100%);}
.dlc-orb{position:absolute;bottom:-30px;right:-30px;z-index:0;width:140px;height:140px;border-radius:50%;background:radial-gradient(circle,var(--dorb) 0%,transparent 70%);opacity:.35;transition:transform .4s,opacity .4s;}
.dlc:hover .dlc-orb{transform:scale(1.5);opacity:.55;}
.dlc-top{position:relative;z-index:2;padding:1.8rem 1.8rem 0;display:flex;align-items:flex-start;gap:1.2rem;flex:1;}
.dlc-ico{width:52px;height:52px;flex-shrink:0;border-radius:15px;background:var(--dib);border:1px solid var(--dbd);display:flex;align-items:center;justify-content:center;transition:transform .3s cubic-bezier(.34,1.5,.64,1);}
.dlc:hover .dlc-ico{transform:scale(1.1) rotate(-5deg);}
@keyframes icoglow{0%,100%{box-shadow:0 0 0 0 var(--dbd);}60%{box-shadow:0 0 0 5px transparent;}}
.dlc:not(.dlcoff) .dlc-ico{animation:icoglow 3s ease-in-out infinite;}
.dlc:hover .dlc-ico{animation:none;}
.dlc-name{font-family:var(--sans);font-weight:700;font-size:.98rem;color:var(--ink);letter-spacing:-.01em;}
.dlc-meta{font-family:var(--mono);font-size:.55rem;color:var(--ink3);letter-spacing:.1em;text-transform:uppercase;margin-top:.28rem;}
.dlc-badge{display:inline-block;margin-top:.6rem;font-family:var(--mono);font-size:.55rem;color:var(--da);background:color-mix(in srgb,var(--da) 8%,transparent);border:1px solid color-mix(in srgb,var(--da) 20%,transparent);border-radius:5px;padding:.18rem .6rem;letter-spacing:.06em;}
.dlc-foot{position:relative;z-index:2;display:flex;align-items:center;justify-content:space-between;padding:.9rem 1.8rem;margin-top:1.4rem;background:rgba(255,255,255,.022);border-top:1px solid var(--wire);transition:background .25s,border-color .25s;}
.dlc:hover .dlc-foot{background:color-mix(in srgb,var(--da) 7%,transparent);border-top-color:color-mix(in srgb,var(--da) 20%,transparent);}
.dlc-cta{font-family:var(--mono);font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;font-weight:600;color:var(--da);}
.dlc-arr{width:30px;height:30px;border-radius:9px;background:color-mix(in srgb,var(--da) 12%,transparent);border:1px solid color-mix(in srgb,var(--da) 28%,transparent);display:flex;align-items:center;justify-content:center;color:var(--da);font-size:.85rem;transition:transform .2s,background .2s;}
.dlc:hover .dlc-arr{transform:translateX(3px);background:color-mix(in srgb,var(--da) 22%,transparent);}
.dlcoff{opacity:.32;pointer-events:none;cursor:not-allowed;}
.dlcoff::before{background:var(--ink3)!important;box-shadow:none!important;}

/* ── SIDEBAR ── */
.sb{background:var(--panel);border:1px solid var(--wire2);border-radius:20px;padding:1.8rem;margin-bottom:1.2rem;}
.sbh{font-family:var(--mono);font-size:.55rem;letter-spacing:.24em;text-transform:uppercase;color:var(--flame);margin-bottom:1.4rem;display:flex;align-items:center;gap:.6rem;}
.sbh::before{content:'◆';font-size:.42rem;}
.fi{display:flex;align-items:flex-start;gap:.75rem;padding:.58rem 0;border-bottom:1px solid rgba(255,255,255,.028);}
.fi:last-child{border:none;}
.fico{width:24px;height:24px;flex-shrink:0;border-radius:7px;background:rgba(255,107,0,.07);border:1px solid rgba(255,107,0,.14);display:flex;align-items:center;justify-content:center;font-size:.72rem;margin-top:1px;}
.fn{color:rgba(232,240,255,.8);font-weight:600;font-size:.8rem;line-height:1.3;}
.fh{font-family:var(--mono);font-size:.54rem;color:var(--ink3);letter-spacing:.05em;margin-top:1px;}
.crow{display:grid;grid-template-columns:1fr auto auto auto;gap:.4rem;align-items:center;padding:.5rem 0;border-bottom:1px solid rgba(255,255,255,.025);font-size:.73rem;}
.crow:last-child{border:none;}
.cn{color:var(--ink2);} .cy{color:var(--jade);font-size:.76rem;} .cno{color:var(--ink4);font-size:.76rem;}

/* ── PATIENT ── */
.sblk{background:var(--panel);border:1px solid var(--wire);border-radius:14px;padding:1.4rem 1.6rem;margin-bottom:.8rem;font-size:.88rem;line-height:1.8;color:var(--ink2);}
.sblk strong{color:var(--ink);}
.rrow2{display:flex;align-items:flex-start;gap:.7rem;padding:.7rem 1rem;background:var(--panel);border-radius:9px;border-left:2px solid var(--jade);font-size:.8rem;color:var(--ink2);margin-bottom:.4rem;}
.rrow2 span{color:var(--jade);flex-shrink:0;}
.faq{border-bottom:1px solid var(--wire);padding:1rem 0;}
.faqq{font-weight:700;font-size:.84rem;color:var(--ink);margin-bottom:.4rem;}
.faqa{font-size:.79rem;color:var(--ink2);line-height:1.65;}
.ltag{display:inline-flex;align-items:center;gap:.3rem;font-family:var(--mono);font-size:.57rem;color:var(--aqua);background:rgba(0,212,255,.06);border:1px solid rgba(0,212,255,.18);border-radius:5px;padding:.22rem .65rem;margin:.2rem;letter-spacing:.06em;}

/* ── COHORT ── */
.igrid{display:grid;grid-template-columns:repeat(3,1fr);gap:.9rem;margin-bottom:1.4rem;}
.itile{background:var(--panel);border:1px solid var(--wire);border-radius:14px;padding:1.3rem;transition:transform .2s,border-color .2s;}
.itile:hover{transform:translateY(-2px);border-color:var(--wire2);}
.itv{font-family:var(--serif);font-size:1.65rem;font-weight:600;letter-spacing:-.04em;color:var(--flame);}
.itl{font-family:var(--mono);font-size:.52rem;letter-spacing:.16em;text-transform:uppercase;color:var(--ink3);margin-top:.35rem;}
.stag2{display:inline-flex;align-items:center;gap:.3rem;font-family:var(--mono);font-size:.57rem;letter-spacing:.06em;color:var(--aqua);background:rgba(0,212,255,.07);border:1px solid rgba(0,212,255,.18);border-radius:5px;padding:.25rem .65rem;margin:.22rem;}
.gop{display:inline-flex;align-items:center;gap:.5rem;padding:.5rem 1.2rem;border-radius:8px;font-weight:700;font-size:.76rem;letter-spacing:.08em;}
.gog{background:rgba(0,200,150,.09);border:1px solid rgba(0,200,150,.28);color:var(--jade);}
.goa{background:rgba(255,107,0,.09);border:1px solid rgba(255,107,0,.28);color:var(--flame);}
.gor{background:rgba(255,51,85,.09);border:1px solid rgba(255,51,85,.28);color:var(--crimson);}

/* ── FOOTER ── */
.footer{margin-top:4rem;padding:2rem 2.5rem;background:var(--panel);border:1px solid var(--wire);border-radius:20px;display:flex;align-items:center;justify-content:space-between;gap:2rem;flex-wrap:wrap;}
.ftxt{font-size:.71rem;color:var(--ink3);line-height:1.8;max-width:55ch;}
.ftxt strong{color:var(--ink2);}
.fseal{text-align:center;flex-shrink:0;background:linear-gradient(135deg,rgba(255,107,0,.08),rgba(0,200,150,.04));border:1px solid rgba(255,107,0,.18);border-radius:14px;padding:1rem 2rem;}
.fsh{font-family:var(--serif);font-style:italic;font-size:1rem;font-weight:600;color:var(--flame);}
.fss{font-family:var(--mono);font-size:.52rem;color:var(--ink3);letter-spacing:.14em;margin-top:.25rem;}

/* ── MISC ── */
.stSpinner>div{border-top-color:var(--flame)!important;}
div[data-testid="stExpander"]{background:var(--panel)!important;border:1px solid var(--wire2)!important;border-radius:14px!important;}
div[data-testid="stExpander"] summary{font-family:var(--sans)!important;font-weight:700!important;color:var(--ink)!important;font-size:.84rem!important;}
.stAlert{background:rgba(255,51,85,.06)!important;border:1px solid rgba(255,51,85,.2)!important;border-radius:10px!important;color:#fca5a5!important;}
#MainMenu,footer,header{visibility:hidden!important;}
.loader-ln{font-family:var(--mono);font-size:.65rem;color:var(--flame);letter-spacing:.14em;margin:.5rem 0 0;display:flex;align-items:center;gap:.6rem;}
.loader-ln::before{content:'▸';animation:b .7s step-end infinite;}
@keyframes b{0%,100%{opacity:1;}50%{opacity:0;}}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──
for k, v in [("result", None), ("patient_data", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── NAV ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="tg-nav">
  <div class="tg-brand">
    <div class="tg-hex">TG</div>
    <span class="tg-name">Trial<em>Guard</em> AI</span>
  </div>
  <div class="tg-right">
    <span class="tg-live"><span class="tg-dot"></span>AWS Lambda Live</span>
    <span class="tg-tag">BEDROCK</span>
    <span class="tg-tag">POLLY ADITI</span>
    <span class="tg-tag">COMPREHEND</span>
    <span class="tg-tag">S3</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── STATS RIBBON ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="ribbon">
  <div class="rib-cell" style="--rc:var(--flame)">
    <div class="rib-val" style="color:var(--flame)">8</div>
    <div class="rib-lbl">AI Agents</div>
  </div>
  <div class="rib-cell" style="--rc:var(--aqua)">
    <div class="rib-val" style="color:var(--aqua)">25<sub>+</sub></div>
    <div class="rib-lbl">Compliance Clauses</div>
  </div>
  <div class="rib-cell" style="--rc:var(--jade)">
    <div class="rib-val" style="color:var(--jade)">10K</div>
    <div class="rib-lbl">Synthetic Patients</div>
  </div>
  <div class="rib-cell" style="--rc:var(--amber)">
    <div class="rib-val" style="color:var(--amber)">9</div>
    <div class="rib-lbl">ICF Languages</div>
  </div>
  <div class="rib-cell" style="--rc:var(--indigo)">
    <div class="rib-val" style="color:var(--indigo)">3</div>
    <div class="rib-lbl">Autopilot Rounds</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── LAYOUT ───────────────────────────────────────────────────────────────────
col_main, col_side = st.columns([3.3, 1], gap="large")

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with col_side:
    st.markdown('<div class="sb"><div class="sbh">Platform Features</div>', unsafe_allow_html=True)
    for ico, name, hint in [
        ("🇮🇳","CDSCO Schedule Y","12-clause compliance"),
        ("🇺🇸","FDA 21 CFR 312","13-clause IND checklist"),
        ("🔄","Protocol Autopilot","3-round autonomous fix"),
        ("🏥","Patient Mode","English + Hindi education"),
        ("🗣","Polly Aditi TTS","Hindi voice narration"),
        ("🏨","India Site DB","AIIMS · CMC · KEM · JIPMER"),
        ("🧬","SDV Cohort","10K Indian demographics"),
        ("🛡","Zero PHI","No real patient data"),
    ]:
        st.markdown(f'<div class="fi"><div class="fico">{ico}</div><div><div class="fn">{name}</div><div class="fh">{hint}</div></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb"><div class="sbh">Competitor Gap</div>', unsafe_allow_html=True)
    st.markdown("""<div style="display:grid;grid-template-columns:1fr auto auto auto;gap:.3rem;
      font-family:var(--mono);font-size:.52rem;letter-spacing:.1em;color:var(--ink3);margin-bottom:.7rem;">
      <span></span><span>CDSCO</span><span>Hindi</span><span>Auto</span></div>""", unsafe_allow_html=True)
    for nm, c, h, a in [("TrialGuard",True,True,True),("Medidata",False,False,False),("Veeva",False,False,False),("Oracle HC",False,False,False)]:
        y='<span class="cy">✓</span>'; n='<span class="cno">—</span>'
        hl='style="color:var(--flame);font-weight:700;"' if nm=="TrialGuard" else ""
        st.markdown(f'<div class="crow"><span class="cn" {hl}>{nm}</span>{y if c else n}{y if h else n}{y if a else n}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── MAIN ─────────────────────────────────────────────────────────────────────
with col_main:
    tab1, tab2, tab3 = st.tabs(["⬡  Protocol Engine", "◈  Patient Education", "◉  Cohort & Sites"])

    # ══ TAB 1 ════════════════════════════════════════════════════════════════
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            language  = st.selectbox("Output Language", ["English (EN)", "हिंदी (HI)"])
            lang_code = "hi" if "HI" in language else "en"
        with c2:
            mode_sel  = st.selectbox("Generation Mode", ["⚡  Standard — Fast (~20 s)", "🔄  Autopilot — 3-Round Self-Improvement (~90 s)"])
            autopilot = "Autopilot" in mode_sel

        trial_text = st.text_area("Trial Description",
            placeholder="Disease · Phase · Patient population · India site preferences...",
            value="Design a Phase 2 RCT for a novel oral anti-diabetic agent in elderly Indian patients (age 60-80) with HbA1c > 8.0, focusing on CDSCO Schedule Y compliance and enrollment from AIIMS New Delhi, CMC Vellore, and JIPMER Puducherry.",
            height=120)

        rounds = st.slider("Improvement Rounds", 1, 3, 2) if autopilot else 1
        run_btn = st.button("🔄  Run Protocol Autopilot" if autopilot else "⬡  Generate Protocol")

        if run_btn:
            pb  = st.progress(0); lbl = st.empty()
            seq = ([
                (0,12,"Spawning 8-agent compliance swarm"),
                (12,28,"FDA 21 CFR 312 · 13 clauses"),
                (28,46,"CDSCO Schedule Y · 12 clauses"),
                (46,62,"Autopilot Round 1 · patching gaps"),
                (62,78,"Autopilot Round 2 · rescoring"),
                (78,97,"Generating PDF report + TTS audio"),
            ] if autopilot else [
                (0,18,"Spawning 8-agent compliance swarm"),
                (18,42,"FDA 21 CFR + CDSCO Schedule Y"),
                (42,65,"Synthesising 10K Indian patient cohort"),
                (65,88,"Scoring feasibility across India sites"),
                (88,98,"Generating PDF + Hindi TTS audio"),
            ])
            for s, e, txt in seq:
                for v in range(s, e): time.sleep(0.02); pb.progress(v)
                lbl.markdown(f'<div class="loader-ln">{txt.upper()}</div>', unsafe_allow_html=True)
            try:
                payload = {"text": trial_text, "language": lang_code}
                if autopilot: payload["max_rounds"] = rounds
                endpoint = "/autopilot" if autopilot else "/design-trial"
                resp = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=200 if autopilot else 45)
                pb.progress(100); pb.empty(); lbl.empty()
                if resp.status_code == 200:
                    st.session_state.result = resp.json()
                    st.session_state.result["_mode"] = "autopilot" if autopilot else "standard"
                    st.session_state.patient_data = None
                else:
                    st.error(f"API {resp.status_code}: {resp.text[:300]}")
            except requests.exceptions.Timeout:
                pb.empty(); lbl.empty()
                st.error("Timed out. Use max_rounds=1 or run locally.")
            except Exception as ex:
                pb.empty(); lbl.empty(); st.error(f"Error: {ex}")

        if st.session_state.result:
            r         = st.session_state.result
            fda       = r.get("fda_score", 0)
            cdsco     = r.get("cdsco_score", 0)
            feas      = r.get("feasibility", "–")
            sid       = r.get("session_id", "–")
            mode_used = r.get("_mode", "standard")
            feas_css  = "var(--jade)" if feas=="High" else "var(--flame)" if feas=="Medium" else "var(--crimson)"
            ptitle    = r.get("protocol", {}).get("title", "Protocol Generated")

            st.markdown(f"""
            <div class="rbanner">
              <div class="rb-ico">✓</div>
              <div>
                <div class="rb-title">{ptitle[:70]}{"…" if len(ptitle)>70 else ""}</div>
                <div class="rb-meta">SESSION {sid.upper()} &nbsp;·&nbsp; {r.get("elapsed_seconds","–")} s &nbsp;·&nbsp; {"AUTOPILOT MODE" if mode_used=="autopilot" else "STANDARD MODE"}</div>
              </div>
            </div>
            <div class="strio">
              <div class="scard" style="--ac:var(--aqua)">
                <div class="sc-tag">FDA 21 CFR 312</div>
                <div class="sc-num">{fda}<span class="sc-den">/100</span></div>
                <div class="sc-lbl">FDA Compliance Score</div>
                <div class="sc-sub">Grade {r.get("fda_grade","–")} &nbsp;·&nbsp; {r.get("fda_submission_readiness","–")}</div>
              </div>
              <div class="scard" style="--ac:var(--flame)">
                <div class="sc-tag">CDSCO SCHEDULE Y</div>
                <div class="sc-num">{cdsco}<span class="sc-den">/100</span></div>
                <div class="sc-lbl">India Compliance Score</div>
                <div class="sc-sub">Grade {r.get("cdsco_grade","–")} &nbsp;·&nbsp; {r.get("cdsco_submission_status","–")}</div>
              </div>
              <div class="scard" style="--ac:{feas_css}">
                <div class="sc-tag">INDIA FEASIBILITY</div>
                <div class="sc-num" style="font-size:2.6rem;margin-top:.2rem">{feas}</div>
                <div class="sc-lbl">Site Feasibility Rating</div>
                <div class="sc-sub">{r.get("go_no_go","–")}</div>
              </div>
            </div>""", unsafe_allow_html=True)

            if mode_used == "autopilot" and r.get("autopilot"):
                ap   = r["autopilot"]; df = ap.get("score_delta_fda",0); dc = ap.get("score_delta_cdsco",0)
                sign = lambda x: ("+" if x>=0 else "") + str(x)
                st.markdown(f"""<div class="apbox">
                  <div class="aphead">
                    <div class="aptitle">🔄 Autopilot Progression <span class="apbadge">{ap.get("total_rounds_run",0)} ROUNDS</span></div>
                    <div class="dpair">
                      <span class="dt {'dup' if df>=0 else 'dfl'}">FDA {sign(df)}</span>
                      <span class="dt {'dup' if dc>=0 else 'dfl'}">CDSCO {sign(dc)}</span>
                    </div>
                  </div>""", unsafe_allow_html=True)
                for rnd in ap.get("score_progression",[]):
                    fs=rnd.get("fda_score",0); cs=rnd.get("cdsco_score",0); lb2=rnd.get("label","")
                    st.markdown(f"""<div class="rrow"><div class="rlbl">{lb2}</div>
                      <div><div class="blbl">FDA</div><div class="btrack"><div class="bfill" style="--bc:var(--aqua);width:{fs}%"></div></div></div>
                      <div><div class="blbl">CDSCO</div><div class="btrack"><div class="bfill" style="--bc:var(--flame);width:{cs}%"></div></div></div>
                      <div class="rscore">{fs}/{cs}</div></div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Gaps
            st.markdown('<div class="sh"><span class="sh-n">01</span><span class="sh-t">Compliance Gaps</span></div>', unsafe_allow_html=True)
            ga, gb = st.columns(2)
            with ga:
                st.markdown("**🇺🇸 FDA Issues**")
                for g in r.get("fda_clauses_failed",[])[:4]:
                    ref=(g.get("ref","") if isinstance(g,dict) else ""); issue=(g.get("issue","") if isinstance(g,dict) else str(g))[:85]
                    st.markdown(f'<div class="chips"><div class="chip"><div class="cdot" style="background:var(--aqua)"></div><span><strong style="color:rgba(232,240,255,.45);font-size:.66rem">{ref} </strong>{issue}</span></div></div>', unsafe_allow_html=True)
                if not r.get("fda_clauses_failed"): st.success("No FDA gaps")
            with gb:
                st.markdown("**🇮🇳 CDSCO Gaps**")
                for g in r.get("unique_india_gaps",[])[:4]:
                    st.markdown(f'<div class="chips"><div class="chip"><div class="cdot" style="background:var(--flame)"></div>{str(g)[:100]}</div></div>', unsafe_allow_html=True)
                if not r.get("unique_india_gaps"): st.success("No India gaps")

            st.markdown('<div class="sh"><span class="sh-n">02</span><span class="sh-t">Full Protocol JSON</span></div>', unsafe_allow_html=True)
            with st.expander("View Complete Protocol"): st.json(r.get("protocol",{}))

            # ── DOWNLOADS ──
            st.markdown('<div class="sh"><span class="sh-n">03</span><span class="sh-t">Downloads</span></div>', unsafe_allow_html=True)
            pdf_url  = r.get("pdf_url",""); audio_url = r.get("audio_url","")
            pdf_ok   = bool(pdf_url   and pdf_url.startswith("https://"))
            audio_ok = bool(audio_url and audio_url.startswith("https://"))
            albl     = "Hindi · Polly Aditi" if lang_code=="hi" else "English · Dr. Protocol"

            PDF_SVG = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00D4FF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>'
            AUD_SVG = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF6B00" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>'

            st.markdown(f"""<div class="dlgrid">
              <a class="dlc{'  ' if pdf_ok else ' dlcoff'}"
                 {'href="'+pdf_url+'" target="_blank"' if pdf_ok else ''}
                 style="--da:#00D4FF;--db:#6366F1;--dorb:rgba(0,212,255,.18);--dib:rgba(0,212,255,.09);--dbd:rgba(0,212,255,.22);">
                <div class="dlc-orb"></div>
                <div class="dlc-top">
                  <div class="dlc-ico">{PDF_SVG}</div>
                  <div>
                    <div class="dlc-name">Protocol PDF</div>
                    <div class="dlc-meta">Full Compliance Report · S3 · Audit-Ready</div>
                    <span class="dlc-badge">{'PDF · Ready' if pdf_ok else 'Awaiting Generation'}</span>
                  </div>
                </div>
                <div class="dlc-foot">
                  <span class="dlc-cta">{'Open Report' if pdf_ok else 'Awaiting'}</span>
                  <div class="dlc-arr">→</div>
                </div>
              </a>
              <a class="dlc{'  ' if audio_ok else ' dlcoff'}"
                 {'href="'+audio_url+'" target="_blank"' if audio_ok else ''}
                 style="--da:#FF6B00;--db:#FF3355;--dorb:rgba(255,107,0,.18);--dib:rgba(255,107,0,.09);--dbd:rgba(255,107,0,.22);">
                <div class="dlc-orb"></div>
                <div class="dlc-top">
                  <div class="dlc-ico">{AUD_SVG}</div>
                  <div>
                    <div class="dlc-name">Dr. Protocol Audio</div>
                    <div class="dlc-meta">{albl} · MP3 · Voice Narration</div>
                    <span class="dlc-badge" style="--da:#FF6B00;">{'MP3 · Ready' if audio_ok else 'Awaiting Generation'}</span>
                  </div>
                </div>
                <div class="dlc-foot">
                  <span class="dlc-cta" style="--da:#FF6B00;">{'Play Audio' if audio_ok else 'Awaiting'}</span>
                  <div class="dlc-arr" style="--da:#FF6B00;">→</div>
                </div>
              </a>
            </div>""", unsafe_allow_html=True)

    # ══ TAB 2 ════════════════════════════════════════════════════════════════
    with tab2:
        if not st.session_state.result:
            st.markdown('<div style="text-align:center;padding:5rem 2rem;"><div style="font-family:var(--serif);font-size:3rem;font-style:italic;opacity:.15;margin-bottom:1rem">◈</div><div style="font-family:var(--mono);font-size:.65rem;letter-spacing:.22em;color:var(--ink3)">GENERATE A PROTOCOL FIRST</div></div>', unsafe_allow_html=True)
        else:
            r = st.session_state.result
            if st.session_state.patient_data is None:
                st.markdown('<div class="sb" style="margin-bottom:1.5rem"><div class="sbh">Generate Patient Education</div><div style="font-size:.84rem;color:var(--ink2);line-height:1.8">Bilingual English + Hindi patient guide, 8-question FAQ, visit timeline, Polly Aditi audio — CDSCO Schedule Y Appendix V compliant.</div></div>', unsafe_allow_html=True)
                if st.button("◈  Generate Patient Education Content"):
                    with st.spinner("Generating bilingual content…"):
                        try:
                            pr = requests.post(f"{BASE_URL}/patient-summary", json={"session_id":r.get("session_id","s"),"protocol":r.get("protocol",{}),"language":"en"}, timeout=45)
                            if pr.status_code == 200: st.session_state.patient_data = pr.json(); st.rerun()
                            else: st.error(f"API {pr.status_code}")
                        except Exception as ex: st.error(f"Error: {ex}")

            if st.session_state.patient_data:
                pd_res = st.session_state.patient_data; ps = pd_res.get("patient_summary",{})
                ae = pd_res.get("audio_url_english",""); ah = pd_res.get("audio_url_hindi","")

                if ae or ah:
                    st.markdown('<div class="sh"><span class="sh-n">01</span><span class="sh-t">Patient Audio Guides</span></div>', unsafe_allow_html=True)
                    ae_ok=bool(ae and ae.startswith("https://")); ah_ok=bool(ah and ah.startswith("https://"))
                    AUD2='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>'
                    st.markdown(f"""<div class="dlgrid">
                      <a class="dlc{'  ' if ae_ok else ' dlcoff'}" {'href="'+ae+'" target="_blank"' if ae_ok else ''} style="--da:#00D4FF;--db:#6366F1;--dorb:rgba(0,212,255,.18);--dib:rgba(0,212,255,.09);--dbd:rgba(0,212,255,.22);">
                        <div class="dlc-orb"></div><div class="dlc-top"><div class="dlc-ico" style="stroke:#00D4FF">{AUD2.replace('currentColor','#00D4FF')}</div><div><div class="dlc-name">English Audio</div><div class="dlc-meta">Dr. Protocol · MP3</div></div></div>
                        <div class="dlc-foot"><span class="dlc-cta">{'Play' if ae_ok else 'Awaiting'}</span><div class="dlc-arr">→</div></div></a>
                      <a class="dlc{'  ' if ah_ok else ' dlcoff'}" {'href="'+ah+'" target="_blank"' if ah_ok else ''} style="--da:#FF6B00;--db:#FF3355;--dorb:rgba(255,107,0,.18);--dib:rgba(255,107,0,.09);--dbd:rgba(255,107,0,.22);">
                        <div class="dlc-orb"></div><div class="dlc-top"><div class="dlc-ico">{AUD2.replace('currentColor','#FF6B00')}</div><div><div class="dlc-name">हिंदी गाइड</div><div class="dlc-meta">Polly Aditi · MP3</div></div></div>
                        <div class="dlc-foot"><span class="dlc-cta" style="--da:#FF6B00;">{'Play' if ah_ok else 'Awaiting'}</span><div class="dlc-arr" style="--da:#FF6B00;">→</div></div></a>
                    </div>""", unsafe_allow_html=True)

                lang_pick = st.radio("View in", ["English", "हिंदी"], horizontal=True)
                use_hi = lang_pick == "हिंदी"
                if use_hi:
                    hi = ps.get("patient_summary_hindi",{})
                    st.markdown('<div class="sh"><span class="sh-n">02</span><span class="sh-t">परीक्षण की जानकारी</span></div>', unsafe_allow_html=True)
                    for k,l in [("what_is_this_trial","यह परीक्षण क्या है?"),("duration_simple","अवधि"),("will_it_cost_me","खर्च"),("is_it_safe","सुरक्षा")]:
                        if hi.get(k): st.markdown(f'<div class="sblk"><strong>{l}:</strong> {hi[k]}</div>', unsafe_allow_html=True)
                    if hi.get("your_rights"):
                        st.markdown('<div class="sh"><span class="sh-n">03</span><span class="sh-t">आपके अधिकार</span></div>', unsafe_allow_html=True)
                        for right in hi["your_rights"]: st.markdown(f'<div class="rrow2"><span>✓</span>{right}</div>', unsafe_allow_html=True)
                else:
                    en = ps.get("patient_summary_english",{})
                    st.markdown('<div class="sh"><span class="sh-n">02</span><span class="sh-t">About This Trial</span></div>', unsafe_allow_html=True)
                    if en.get("what_is_this_trial"): st.markdown(f'<div class="sblk">{en["what_is_this_trial"]}</div>', unsafe_allow_html=True)
                    p1,p2 = st.columns(2)
                    with p1:
                        for k,l in [("duration_simple","Duration"),("will_it_cost_me","Cost")]:
                            if en.get(k): st.markdown(f'<div class="sblk"><strong>{l}:</strong> {en[k]}</div>', unsafe_allow_html=True)
                    with p2:
                        for k,l in [("is_it_safe","Safety"),("who_can_join","Who can join")]:
                            if en.get(k): st.markdown(f'<div class="sblk"><strong>{l}:</strong> {en[k]}</div>', unsafe_allow_html=True)
                    if en.get("your_rights"):
                        st.markdown('<div class="sh"><span class="sh-n">03</span><span class="sh-t">Your Rights — CDSCO Schedule Y Appendix V</span></div>', unsafe_allow_html=True)
                        for right in en["your_rights"]: st.markdown(f'<div class="rrow2"><span>✓</span>{right}</div>', unsafe_allow_html=True)
                    faq = ps.get("patient_faq",[])
                    if faq:
                        st.markdown('<div class="sh"><span class="sh-n">04</span><span class="sh-t">Patient FAQ — Bilingual</span></div>', unsafe_allow_html=True)
                        for item in faq[:6]:
                            if isinstance(item,dict) and item.get("question_en"):
                                hi_q = f'<div class="faqa" style="color:var(--flame);margin-top:.35rem">🇮🇳 {item.get("question_hi","")}</div>' if item.get("question_hi") else ""
                                st.markdown(f'<div class="faq"><div class="faqq">Q: {item["question_en"]}</div><div class="faqa">{item.get("answer_en","")}</div>{hi_q}</div>', unsafe_allow_html=True)
                if pd_res.get("languages_available"):
                    st.markdown('<div class="sh"><span class="sh-n">05</span><span class="sh-t">ICF Languages</span></div>', unsafe_allow_html=True)
                    st.markdown('<div>'+"".join([f'<span class="ltag">🌐 {l}</span>' for l in pd_res["languages_available"]])+'</div>', unsafe_allow_html=True)

    # ══ TAB 3 ════════════════════════════════════════════════════════════════
    with tab3:
        if not st.session_state.result:
            st.markdown('<div style="text-align:center;padding:5rem 2rem;"><div style="font-family:var(--serif);font-size:3rem;font-style:italic;opacity:.15;margin-bottom:1rem">◉</div><div style="font-family:var(--mono);font-size:.65rem;letter-spacing:.22em;color:var(--ink3)">GENERATE A PROTOCOL FIRST</div></div>', unsafe_allow_html=True)
        else:
            r=st.session_state.result; cohort=r.get("cohort",{}); sites=r.get("recommended_sites",[]); months=r.get("enrollment_months_estimate",0); go=r.get("go_no_go","GO WITH CONDITIONS")
            st.markdown('<div class="sh"><span class="sh-n">01</span><span class="sh-t">SDV Indian Patient Cohort</span></div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="igrid">
              <div class="itile"><div class="itv">{cohort.get("cohort_size",10000):,}</div><div class="itl">Synthetic Patients</div></div>
              <div class="itile"><div class="itv">{cohort.get("eligibility_rate_pct",0)}%</div><div class="itl">Eligibility Rate</div></div>
              <div class="itile"><div class="itv">{cohort.get("recommended_total_n",0)}</div><div class="itl">Adjusted N</div></div>
              <div class="itile"><div class="itv">{cohort.get("mean_dropout_pct",0)}%</div><div class="itl">Predicted Dropout</div></div>
              <div class="itile"><div class="itv">{cohort.get("disease","–").title()}</div><div class="itl">Disease Category</div></div>
              <div class="itile"><div class="itv">{len(cohort.get("languages_required",[]))}</div><div class="itl">ICF Languages</div></div>
            </div>""", unsafe_allow_html=True)
            if cohort.get("languages_required"):
                st.markdown('<div style="margin-bottom:1.2rem">'+"".join([f'<span class="ltag">{l}</span>' for l in cohort["languages_required"]])+'</div>', unsafe_allow_html=True)
            if cohort.get("india_specific_insights"):
                st.markdown('<div class="sh"><span class="sh-n">02</span><span class="sh-t">India-Specific Insights</span></div>', unsafe_allow_html=True)
                st.markdown('<div class="chips">'+"".join([f'<div class="chip"><div class="cdot" style="background:var(--amber)"></div>{i}</div>' for i in cohort["india_specific_insights"][:4]])+'</div>', unsafe_allow_html=True)
            st.markdown('<div class="sh"><span class="sh-n">03</span><span class="sh-t">Recommended India Sites</span></div>', unsafe_allow_html=True)
            gc = "gog" if ("GO" in go and "NO" not in go and "CONDITION" not in go) else ("goa" if "CONDITION" in go else "gor")
            gl = "✓ GO" if gc=="gog" else ("⚡ GO WITH CONDITIONS" if gc=="goa" else "✗ NO-GO")
            st.markdown(f"""<div style="display:flex;align-items:center;gap:1.2rem;margin-bottom:1.2rem;">
              <span class="gop {gc}">{gl}</span>
              <span style="font-family:var(--mono);font-size:.57rem;color:var(--ink3)">{months} months estimated</span>
            </div><div style="margin-bottom:1rem">{"".join([f'<span class="stag2">🏥 {s}</span>' for s in sites])}</div>""", unsafe_allow_html=True)
            if r.get("regional_gaps"):
                st.markdown('<div class="sh"><span class="sh-n">04</span><span class="sh-t">Regional Coverage Gaps</span></div>', unsafe_allow_html=True)
                st.markdown('<div class="chips">'+"".join([f'<div class="chip"><div class="cdot" style="background:var(--crimson)"></div>Gap: {g}</div>' for g in r["regional_gaps"]])+'</div>', unsafe_allow_html=True)

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  <div class="ftxt">
    <strong>Hackathon Notice</strong> — Synthetic data only. Not for actual clinical use.<br>
    AI guidance requires qualified regulatory review. FDA/CDSCO scores are decision-support tools, not certification.
  </div>
  <div class="fseal">
    <div class="fsh">🇮🇳 AI for Bharat 2026</div>
    <div class="fss">AWS BEDROCK · LAMBDA · POLLY · S3</div>
  </div>
</div>
""", unsafe_allow_html=True)
