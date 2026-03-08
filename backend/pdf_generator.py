# import os
# import boto3
# import json
# import re
# import ast
# import urllib.request
# from xml.sax.saxutils import escape

# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# from dotenv import load_dotenv

# load_dotenv()

# s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))

# # ─── FONT SETUP ────────────────────────────────────────────────────────────────
# # NotoSans supports Hindi (Devanagari) + Latin. We bundle it from Google Fonts.
# # On Lambda, /tmp is the only writable directory.
# FONT_URL  = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
# FONT_BOLD_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"
# FONT_TMP  = "/tmp/NotoSans-Regular.ttf"
# FONT_BOLD_TMP = "/tmp/NotoSans-Bold.ttf"

# def _ensure_fonts():
#     """Download NotoSans to /tmp if not already there. Works on Lambda cold starts."""
#     for path, url in [(FONT_TMP, FONT_URL), (FONT_BOLD_TMP, FONT_BOLD_URL)]:
#         if not os.path.exists(path):
#             try:
#                 urllib.request.urlretrieve(url, path)
#             except Exception as e:
#                 print(f"[WARN] Could not download font {url}: {e}")

#     registered = []
#     for name, path in [("NotoSans", FONT_TMP), ("NotoSans-Bold", FONT_BOLD_TMP)]:
#         if os.path.exists(path):
#             try:
#                 pdfmetrics.registerFont(TTFont(name, path))
#                 registered.append(name)
#             except Exception as e:
#                 print(f"[WARN] Font registration failed for {name}: {e}")

#     return "NotoSans" if "NotoSans" in registered else None

# # ─── TEXT HELPERS ──────────────────────────────────────────────────────────────

# def _to_safe_text(value):
#     if value is None:
#         return ""
#     if isinstance(value, (dict, list)):
#         value = json.dumps(value, indent=2, ensure_ascii=False)
#     if not isinstance(value, str):
#         value = str(value)

#     value = value.replace("\r\n", "\n").replace("\r", "\n")
#     # Strip control chars (keep newlines \n = 0x0a, tabs \t = 0x09)
#     value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", value)
#     # Remove block/box characters that render as squares in most fonts
#     value = re.sub(
#         r"[\u25A0-\u25FF\u2580-\u259F\u2600-\u26FF\u2700-\u27BF]", "", value
#     )
#     value = escape(value)
#     value = value.replace("\n", "<br/>")
#     return value


# def _format_patient_criteria(value):
#     if isinstance(value, str):
#         stripped = value.strip()
#         for fence in ("```json", "```"):
#             if stripped.startswith(fence):
#                 stripped = stripped[len(fence):]
#         if stripped.endswith("```"):
#             stripped = stripped[:-3]
#         stripped = stripped.strip()
#         if stripped.startswith("{") and stripped.endswith("}"):
#             for parser in (json.loads, ast.literal_eval):
#                 try:
#                     value = parser(stripped)
#                     break
#                 except Exception:
#                     pass

#     if isinstance(value, dict):
#         inclusion = value.get("inclusion")
#         exclusion = value.get("exclusion")

#         def _fmt_list(items):
#             if items is None:
#                 return ""
#             if isinstance(items, str):
#                 items = [items]
#             if not isinstance(items, list):
#                 items = [str(items)]
#             return "<br/>".join(f"{i}. {_to_safe_text(item)}" for i, item in enumerate(items, 1))

#         parts = []
#         if inclusion is not None:
#             parts += ["<b>Inclusion</b><br/>", _fmt_list(inclusion)]
#         if exclusion is not None:
#             if parts:
#                 parts.append("<br/><br/>")
#             parts += ["<b>Exclusion</b><br/>", _fmt_list(exclusion)]

#         combined = "".join(parts).strip()
#         if combined:
#             return combined

#     return _to_safe_text(value)

# # ─── MAIN FUNCTION ─────────────────────────────────────────────────────────────

# def generate_pdf(protocol_json, fda_result, cdsco_result, session_id):
#     # 1. Font setup
#     font_name = _ensure_fonts()
#     bold_name = "NotoSans-Bold" if font_name else "Helvetica-Bold"
#     if not font_name:
#         font_name = "Helvetica"

#     # 2. Build styles
#     styles = getSampleStyleSheet()

#     base   = ParagraphStyle("base",   fontName=font_name,  fontSize=10, leading=15, spaceAfter=4)
#     h2     = ParagraphStyle("h2",     fontName=bold_name,   fontSize=13, leading=18, spaceAfter=6, textColor="#1e3a8a")
#     h3     = ParagraphStyle("h3",     fontName=bold_name,   fontSize=11, leading=14, spaceAfter=4, textColor="#1d4ed8")
#     title  = ParagraphStyle("title",  fontName=bold_name,   fontSize=18, leading=22, alignment=1, spaceAfter=12, textColor="#0f172a")

#     # 3. Build PDF story
#     filename = f"protocol_{session_id}.pdf"
#     filepath = f"/tmp/{filename}"

#     doc = SimpleDocTemplate(filepath, pagesize=letter,
#                             leftMargin=50, rightMargin=50,
#                             topMargin=60, bottomMargin=60)
#     story = []

#     story.append(Paragraph("TrialGuard Clinical Trial Protocol", title))
#     story.append(Spacer(1, 8))

#     fda_score   = fda_result.get('fda_score',    fda_result.get('score',   'N/A'))
#     cdsco_score = cdsco_result.get('india_score', cdsco_result.get('score', 'N/A'))

#     story.append(Paragraph(f"FDA Compliance Score: {fda_score}/100", h2))
#     story.append(Paragraph(f"CDSCO Compliance Score: {cdsco_score}/100", h2))
#     story.append(Spacer(1, 14))

#     sections = [
#         ("Trial Objective",    _to_safe_text(protocol_json.get('objective', 'N/A'))),
#         ("Patient Criteria",   _format_patient_criteria(protocol_json.get('patient_criteria', 'N/A'))),
#         ("Trial Design",       _to_safe_text(protocol_json.get('trial_design', 'N/A'))),
#         ("Endpoints",          _to_safe_text(protocol_json.get('endpoints', 'N/A'))),
#         ("Statistical Plan",   _to_safe_text(protocol_json.get('statistical_plan', 'N/A'))),
#         ("FDA Summary",        _to_safe_text(fda_result.get('verbal_summary', 'N/A'))),
#         ("CDSCO Summary",      _to_safe_text(cdsco_result.get('verbal_summary', 'N/A'))),
#     ]

#     for heading, content in sections:
#         if content and content != "N/A":
#             story.append(Paragraph(f"{heading}:", h3))
#             story.append(Paragraph(content, base))
#             story.append(Spacer(1, 12))

#     doc.build(story)

#     # ─── 4. S3 UPLOAD — clean public URL, NO signed credentials ───────────────
#     bucket  = os.getenv('S3_BUCKET')
#     s3_key  = f"pdfs/protocol_{session_id}.pdf"

#     s3.upload_file(
#         filepath,
#         bucket,
#         s3_key,
#         ExtraArgs={
#             'ACL': 'public-read',           # bucket must allow public ACLs
#             'ContentType': 'application/pdf',
#             'ContentDisposition': 'inline', # opens in browser, not download
#         }
#     )

#     os.remove(filepath)

#     # ✅ Return clean HTTPS URL — no signing, no credentials in URL
#     region = os.getenv('AWS_REGION', 'us-east-1')
#     # Use path-style URL that works in all regions
#     public_url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
#     return public_url

# import os, json, re, ast, urllib.request, tempfile
# import boto3
# from xml.sax.saxutils import escape
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.lib import colors
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# from dotenv import load_dotenv

# load_dotenv()
# s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))

# # ── Cross-platform temp directory (works on Windows, Linux, Lambda) ───────────
# TMP_DIR = tempfile.gettempdir()   # C:\Users\...\AppData\Local\Temp on Windows, /tmp on Linux/Lambda

# # ── Font setup ────────────────────────────────────────────────────────────────
# FONT_URL      = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
# FONT_BOLD_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"

# def _ensure_fonts():
#     pairs = [
#         (os.path.join(TMP_DIR, "NotoSans-Regular.ttf"), FONT_URL,      "NotoSans"),
#         (os.path.join(TMP_DIR, "NotoSans-Bold.ttf"),    FONT_BOLD_URL, "NotoSans-Bold"),
#     ]
#     registered = []
#     for path, url, name in pairs:
#         if not os.path.exists(path):
#             try:
#                 print(f"[INFO] Downloading font {name} → {path}")
#                 urllib.request.urlretrieve(url, path)
#             except Exception as e:
#                 print(f"[WARN] Font download failed for {name}: {e}")
#         if os.path.exists(path):
#             try:
#                 pdfmetrics.registerFont(TTFont(name, path))
#                 registered.append(name)
#                 print(f"[INFO] Font registered: {name}")
#             except Exception as e:
#                 print(f"[WARN] Font registration failed for {name}: {e}")
#         else:
#             print(f"[WARN] Font file not found after download attempt: {path}")
#     return (
#         "NotoSans"      if "NotoSans"      in registered else None,
#         "NotoSans-Bold" if "NotoSans-Bold" in registered else None,
#     )


# # ── Text helpers ───────────────────────────────────────────────────────────────
# def _safe(value, indent=False):
#     if value is None: return ""
#     if isinstance(value, (dict, list)):
#         value = json.dumps(value, indent=2, ensure_ascii=False)
#     value = str(value)
#     value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", value)
#     value = re.sub(r"[\u25A0-\u27BF]", "", value)
#     value = escape(value)
#     value = value.replace("\n", "<br/>")
#     return value


# def _list_to_html(items):
#     if not items: return ""
#     if isinstance(items, str):
#         try: items = json.loads(items)
#         except Exception: return _safe(items)
#     if isinstance(items, list):
#         return "<br/>".join(f"• {_safe(item)}" for item in items)
#     return _safe(items)


# def _format_criteria(value):
#     if isinstance(value, str):
#         stripped = value.strip().strip("```json").strip("```").strip()
#         for parser in (json.loads, ast.literal_eval):
#             try: value = parser(stripped); break
#             except Exception: pass
#     if isinstance(value, dict):
#         parts = []
#         if value.get("inclusion"):
#             parts.append("<b>Inclusion Criteria:</b><br/>")
#             items = value["inclusion"] if isinstance(value["inclusion"], list) else [value["inclusion"]]
#             parts.append("<br/>".join(f"{i}. {_safe(item)}" for i, item in enumerate(items, 1)))
#         if value.get("exclusion"):
#             if parts: parts.append("<br/><br/>")
#             parts.append("<b>Exclusion Criteria:</b><br/>")
#             items = value["exclusion"] if isinstance(value["exclusion"], list) else [value["exclusion"]]
#             parts.append("<br/>".join(f"{i}. {_safe(item)}" for i, item in enumerate(items, 1)))
#         if value.get("sample_size") and isinstance(value["sample_size"], dict):
#             ss = value["sample_size"]
#             parts.append(f"<br/><br/><b>Sample Size:</b> N={ss.get('n','?')} "
#                          f"(Power: {ss.get('power','?')}, α={ss.get('alpha','?')})<br/>"
#                          f"{_safe(ss.get('justification',''))}")
#         combined = "".join(parts).strip()
#         if combined: return combined
#     return _safe(value)


# # ── Main PDF function ──────────────────────────────────────────────────────────
# def generate_pdf(protocol_json, fda_result, cdsco_result, session_id,
#                  cohort_json=None, feasibility_json=None):

#     font_name, bold_name = _ensure_fonts()
#     if not font_name: font_name, bold_name = "Helvetica", "Helvetica-Bold"

#     # ── Styles ────────────────────────────────────────────────────────────
#     base   = ParagraphStyle("base",   fontName=font_name, fontSize=9.5, leading=14, spaceAfter=4)
#     h1     = ParagraphStyle("h1",     fontName=bold_name, fontSize=18, leading=22, alignment=1, spaceAfter=10, textColor=colors.HexColor("#0f172a"))
#     h2     = ParagraphStyle("h2",     fontName=bold_name, fontSize=13, leading=17, spaceAfter=6, spaceBefore=10, textColor=colors.HexColor("#1e3a8a"))
#     h3     = ParagraphStyle("h3",     fontName=bold_name, fontSize=10.5, leading=14, spaceAfter=4, textColor=colors.HexColor("#1d4ed8"))
#     small  = ParagraphStyle("small",  fontName=font_name, fontSize=8, leading=12, textColor=colors.HexColor("#64748b"))
#     badge  = ParagraphStyle("badge",  fontName=bold_name, fontSize=11, leading=15, textColor=colors.HexColor("#166534"))

#     filepath = os.path.join(TMP_DIR, f"protocol_{session_id}.pdf")
#     print(f"[INFO] PDF target path: {filepath}")
#     doc = SimpleDocTemplate(filepath, pagesize=letter,
#                             leftMargin=52, rightMargin=52, topMargin=60, bottomMargin=55)
#     story = []

#     # ══ HEADER ════════════════════════════════════════════════════════════
#     story.append(Paragraph("TrialGuard AI", h1))
#     story.append(Paragraph("India-First Clinical Trial Protocol", ParagraphStyle("sub", fontName=font_name, fontSize=12, alignment=1, textColor=colors.HexColor("#334155"))))
#     story.append(Spacer(1, 4))
#     story.append(Paragraph(f"Session: {session_id}  |  CDSCO Schedule Y + FDA 21 CFR Compliant", small))
#     story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1e3a8a")))
#     story.append(Spacer(1, 8))

#     # ══ COMPLIANCE SCORE CARDS ════════════════════════════════════════════
#     fda_score   = fda_result.get("fda_score", "N/A")
#     cdsco_score = cdsco_result.get("india_score", "N/A")
#     fda_grade   = fda_result.get("grade", "")
#     cdsco_grade = cdsco_result.get("cdsco_grade", "")
#     fda_ready   = fda_result.get("submission_readiness", "")
#     cdsco_ready = cdsco_result.get("cdsco_submission_status", "")

#     score_table = Table([
#         [Paragraph(f"<b>FDA 21 CFR Score</b><br/>{fda_score}/100", ParagraphStyle("sc", fontName=bold_name, fontSize=14, alignment=1, textColor=colors.white)),
#          Paragraph(f"<b>CDSCO Schedule Y Score</b><br/>{cdsco_score}/100", ParagraphStyle("sc2", fontName=bold_name, fontSize=14, alignment=1, textColor=colors.white))],
#         [Paragraph(fda_grade, ParagraphStyle("sg", fontName=font_name, fontSize=9, alignment=1, textColor=colors.white)),
#          Paragraph(cdsco_grade, ParagraphStyle("sg2", fontName=font_name, fontSize=9, alignment=1, textColor=colors.white))],
#     ], colWidths=[3.5*inch, 3.5*inch])
#     score_table.setStyle(TableStyle([
#         ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#1e3a8a")),
#         ('BACKGROUND', (1,0), (1,-1), colors.HexColor("#065f46")),
#         ('ALIGN',    (0,0), (-1,-1), 'CENTER'),
#         ('VALIGN',   (0,0), (-1,-1), 'MIDDLE'),
#         ('ROWHEIGHT', (0,0), (-1,0), 36),
#         ('ROWHEIGHT', (0,1), (-1,1), 18),
#         ('TOPPADDING',    (0,0), (-1,-1), 6),
#         ('BOTTOMPADDING', (0,0), (-1,-1), 6),
#         ('ROUNDEDCORNERS', [4]),
#     ]))
#     story.append(score_table)
#     story.append(Spacer(1, 8))

#     # Submission readiness badges
#     story.append(Paragraph(f"FDA: {fda_ready}  |  CDSCO: {cdsco_ready}", badge))
#     story.append(Spacer(1, 12))

#     # ══ PROTOCOL SECTIONS ════════════════════════════════════════════════
#     story.append(Paragraph("Protocol Details", h2))

#     title = protocol_json.get("title", "N/A")
#     proto_id = protocol_json.get("protocol_id", "N/A")
#     story.append(Paragraph(f"<b>Title:</b> {_safe(title)}", base))
#     story.append(Paragraph(f"<b>Protocol ID:</b> {_safe(proto_id)}", base))
#     story.append(Spacer(1, 8))

#     # Objective
#     obj = protocol_json.get("objective", {})
#     story.append(Paragraph("Objectives", h3))
#     if isinstance(obj, dict):
#         story.append(Paragraph(f"<b>Primary:</b> {_safe(obj.get('primary',''))}", base))
#         sec = obj.get("secondary", [])
#         if sec:
#             story.append(Paragraph(f"<b>Secondary:</b>", base))
#             story.append(Paragraph(_list_to_html(sec), base))
#         india = obj.get("india_context", "")
#         if india:
#             story.append(Paragraph(f"<b>India Context:</b> {_safe(india)}", base))
#     else:
#         story.append(Paragraph(_safe(obj), base))
#     story.append(Spacer(1, 8))

#     # Patient Criteria
#     story.append(Paragraph("Patient Criteria", h3))
#     story.append(Paragraph(_format_criteria(protocol_json.get("patient_criteria", "N/A")), base))
#     story.append(Spacer(1, 8))

#     # Trial Design
#     design = protocol_json.get("trial_design", {})
#     story.append(Paragraph("Trial Design", h3))
#     if isinstance(design, dict):
#         story.append(Paragraph(f"<b>Type:</b> {_safe(design.get('type',''))}", base))
#         story.append(Paragraph(f"<b>Duration:</b> {design.get('duration_weeks','?')} weeks", base))
#         story.append(Paragraph(f"<b>Randomization:</b> {_safe(design.get('randomization',''))}", base))
#         # Arms table
#         arms = design.get("arms", [])
#         if arms and isinstance(arms, list):
#             arm_data = [["Arm", "N", "Dose", "Frequency", "Route"]]
#             for arm in arms:
#                 if isinstance(arm, dict):
#                     arm_data.append([arm.get("arm",""), str(arm.get("n","")),
#                                      arm.get("dose",""), arm.get("frequency",""), arm.get("route","")])
#             if len(arm_data) > 1:
#                 arm_table = Table(arm_data, colWidths=[1.4*inch, 0.5*inch, 1.8*inch, 1.0*inch, 0.8*inch])
#                 arm_table.setStyle(TableStyle([
#                     ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e0e7ff")),
#                     ('FONTNAME',   (0,0), (-1,0), bold_name),
#                     ('FONTSIZE',   (0,0), (-1,-1), 8.5),
#                     ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
#                     ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
#                 ]))
#                 story.append(arm_table)
#         # Sites
#         sites = design.get("sites", {})
#         if isinstance(sites, dict):
#             story.append(Paragraph(f"<b>Sites:</b> {sites.get('count','?')} sites in India", base))
#             india_sites = sites.get("india_regions", [])
#             if india_sites:
#                 story.append(Paragraph("<b>Recommended Sites:</b><br/>" + _list_to_html(india_sites), base))
#     else:
#         story.append(Paragraph(_safe(design), base))
#     story.append(Spacer(1, 8))

#     # Endpoints
#     ep = protocol_json.get("endpoints", {})
#     story.append(Paragraph("Endpoints", h3))
#     if isinstance(ep, dict):
#         story.append(Paragraph(f"<b>Primary:</b> {_safe(ep.get('primary',''))}", base))
#         sec = ep.get("secondary", [])
#         if sec:
#             story.append(Paragraph(f"<b>Secondary:</b>", base))
#             story.append(Paragraph(_list_to_html(sec), base))
#         india_ep = ep.get("india_specific", "")
#         if india_ep:
#             story.append(Paragraph(f"<b>India-Specific:</b> {_safe(india_ep)}", base))
#     else:
#         story.append(Paragraph(_safe(ep), base))
#     story.append(Spacer(1, 8))

#     # Statistical Plan
#     stat = protocol_json.get("statistical_plan", {})
#     story.append(Paragraph("Statistical Plan", h3))
#     if isinstance(stat, dict):
#         for key, label in [("primary_analysis","Primary Analysis"), ("itt_population","ITT Population"),
#                            ("interim_analysis","Interim Analysis"), ("multiplicity","Multiplicity")]:
#             if stat.get(key):
#                 story.append(Paragraph(f"<b>{label}:</b> {_safe(stat[key])}", base))
#     else:
#         story.append(Paragraph(_safe(stat), base))
#     story.append(Spacer(1, 8))

#     # Regulatory Map
#     reg = protocol_json.get("regulatory_map", {})
#     story.append(Paragraph("Regulatory Compliance Map", h3))
#     if isinstance(reg, dict):
#         fda_secs = reg.get("fda_sections", [])
#         if fda_secs:
#             story.append(Paragraph(f"<b>FDA 21 CFR:</b><br/>{_list_to_html(fda_secs)}", base))
#         cdsco_cls = reg.get("cdsco_clauses", [])
#         if cdsco_cls:
#             story.append(Paragraph(f"<b>CDSCO Schedule Y:</b><br/>{_list_to_html(cdsco_cls)}", base))
#         ethics = reg.get("ethics", "")
#         if ethics:
#             story.append(Paragraph(f"<b>Ethics:</b> {_safe(ethics)}", base))
#     story.append(Spacer(1, 8))

#     # ══ COMPLIANCE DETAILS ════════════════════════════════════════════════
#     story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
#     story.append(Paragraph("FDA Compliance Analysis", h2))
#     story.append(Paragraph(_safe(fda_result.get("verbal_summary", "")), base))

#     failed = fda_result.get("clauses_failed", [])
#     if failed:
#         story.append(Paragraph("<b>Issues to Fix:</b>", base))
#         for item in failed[:5]:
#             if isinstance(item, dict):
#                 story.append(Paragraph(
#                     f"• [{item.get('ref','')}] {_safe(item.get('issue',''))} → <b>Fix:</b> {_safe(item.get('fix','')[:150])}",
#                     ParagraphStyle("fix", fontName=font_name, fontSize=8.5, leading=12, spaceAfter=3,
#                                    leftIndent=10, textColor=colors.HexColor("#b91c1c"))
#                 ))
#     critical = fda_result.get("critical_gaps", [])
#     if critical:
#         story.append(Paragraph(f"<b>⚠ Critical Gaps:</b> {_list_to_html(critical)}", base))
#     story.append(Spacer(1, 8))

#     story.append(Paragraph("CDSCO India Compliance Analysis", h2))
#     story.append(Paragraph(_safe(cdsco_result.get("verbal_summary", "")), base))

#     india_viol = cdsco_result.get("india_violations", [])
#     if india_viol:
#         story.append(Paragraph("<b>India-Specific Issues:</b>", base))
#         for item in india_viol[:5]:
#             if isinstance(item, dict):
#                 sev = item.get("severity", "")
#                 story.append(Paragraph(
#                     f"• [{item.get('clause','')}] {_safe(item.get('issue','')[:120])} → {_safe(item.get('fix','')[:150])}",
#                     ParagraphStyle("ifix", fontName=font_name, fontSize=8.5, leading=12, spaceAfter=3,
#                                    leftIndent=10, textColor=colors.HexColor("#7c2d12"))
#                 ))
#     unique_gaps = cdsco_result.get("unique_india_gaps", [])
#     if unique_gaps:
#         story.append(Paragraph(f"<b>India-Only Gaps:</b><br/>{_list_to_html(unique_gaps)}", base))
#     story.append(Spacer(1, 8))

#     # ══ COHORT SECTION ════════════════════════════════════════════════════
#     if cohort_json and isinstance(cohort_json, dict) and not cohort_json.get("error"):
#         story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
#         story.append(Paragraph("Synthetic Indian Patient Cohort (SDV — Zero PHI)", h2))
#         story.append(Paragraph(
#             f"<b>Cohort Size:</b> {cohort_json.get('cohort_size',10000):,} synthetic patients  |  "
#             f"<b>Disease:</b> {cohort_json.get('disease','').title()}  |  "
#             f"<b>Eligibility Rate:</b> {cohort_json.get('eligibility_rate_pct','?')}%  |  "
#             f"<b>Mean Dropout Risk:</b> {cohort_json.get('mean_dropout_pct','?')}%",
#             base
#         ))
#         story.append(Paragraph(
#             f"<b>Recommended Sample Size (dropout-adjusted):</b> N = {cohort_json.get('recommended_total_n','?')} total",
#             base
#         ))
#         langs = cohort_json.get("languages_required", [])
#         if langs:
#             story.append(Paragraph(f"<b>ICF Languages Required:</b> {', '.join(langs)}", base))
#         insights = cohort_json.get("india_specific_insights", [])
#         if insights:
#             story.append(Paragraph("<b>India-Specific Insights:</b>", base))
#             story.append(Paragraph(_list_to_html(insights), base))
#         story.append(Paragraph(cohort_json.get("sdv_note", ""), small))
#         story.append(Spacer(1, 8))

#     # ══ FEASIBILITY SECTION ═══════════════════════════════════════════════
#     if feasibility_json and isinstance(feasibility_json, dict) and not feasibility_json.get("error"):
#         story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
#         story.append(Paragraph("India Site Feasibility Analysis", h2))
#         feas = feasibility_json.get("feasibility", "Unknown")
#         feas_score = feasibility_json.get("feasibility_score", 0)
#         feas_color = {"High": "#166534", "Medium": "#92400e", "Low": "#991b1b"}.get(feas, "#1e3a8a")
#         story.append(Paragraph(
#             f"Feasibility: <b>{feas}</b> ({feas_score}/100)  |  "
#             f"Est. Enrollment: {feasibility_json.get('enrollment_months_estimate','?')} months  |  "
#             f"Recommendation: <b>{feasibility_json.get('go_no_go_recommendation','N/A')}</b>",
#             ParagraphStyle("feas", fontName=bold_name, fontSize=10.5, leading=15,
#                            textColor=colors.HexColor(feas_color))
#         ))
#         story.append(Paragraph(_safe(feasibility_json.get("verbal_summary", "")), base))

#         rec_sites = feasibility_json.get("recommended_sites", [])
#         if rec_sites:
#             story.append(Paragraph(f"<b>Recommended Sites:</b><br/>{_list_to_html(rec_sites)}", base))

#         gaps = feasibility_json.get("regional_gaps", [])
#         if gaps:
#             story.append(Paragraph(f"<b>Regional Gaps:</b> {', '.join(gaps)}", base))

#         risks = feasibility_json.get("key_risks", [])
#         if risks:
#             story.append(Paragraph(f"<b>Key Risks:</b><br/>{_list_to_html(risks)}", base))
#         story.append(Spacer(1, 8))

#     # ══ FOOTER ════════════════════════════════════════════════════════════
#     story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
#     story.append(Paragraph(
#         "⚠ LIMITATIONS: Synthetic data only — not for actual clinical trials. "
#         "FDA/CDSCO analysis is AI-generated guidance, not legal advice. "
#         "Verify all regulatory requirements with qualified regulatory affairs professionals.",
#         small
#     ))
#     story.append(Paragraph("Generated by TrialGuard AI | AWS Bedrock | CDSCO Schedule Y + FDA 21 CFR | SDV Synthetic Cohort | Zero PHI", small))

#     # ── Build PDF ─────────────────────────────────────────────────────────
#     try:
#         doc.build(story)
#     except Exception as build_err:
#         raise RuntimeError(f"ReportLab doc.build() failed: {build_err}") from build_err

#     # ── Verify file was actually written ──────────────────────────────────
#     if not os.path.exists(filepath):
#         raise FileNotFoundError(
#             f"PDF build completed without error but file not found at: {filepath}\n"
#             f"TMP_DIR={TMP_DIR} | Check write permissions."
#         )

#     file_size = os.path.getsize(filepath)
#     print(f"[INFO] PDF built successfully: {filepath} ({file_size:,} bytes)")

#     # ── S3 Upload ─────────────────────────────────────────────────────────
#     bucket  = os.getenv('S3_BUCKET')
#     s3_key  = f"pdfs/protocol_{session_id}.pdf"
#     region  = os.getenv('AWS_REGION', 'us-east-1')

#     if not bucket:
#         raise ValueError("S3_BUCKET environment variable is not set")

#     try:
#         s3.upload_file(
#             filepath, bucket, s3_key,
#             ExtraArgs={
#                 'ACL': 'public-read',
#                 'ContentType': 'application/pdf',
#                 'ContentDisposition': 'inline',
#             }
#         )
#         print(f"[INFO] Uploaded to S3: s3://{bucket}/{s3_key}")
#     except Exception as s3_err:
#         raise RuntimeError(f"S3 upload failed: {s3_err}") from s3_err
#     finally:
#         # Always clean up local temp file
#         try:
#             os.remove(filepath)
#         except Exception:
#             pass

#     return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"



import os, json, re, ast, urllib.request, tempfile
import boto3
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from dotenv import load_dotenv

load_dotenv()
s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))

# ── Cross-platform temp directory (works on Windows, Linux, Lambda) ───────────
TMP_DIR = tempfile.gettempdir()   # C:\Users\...\AppData\Local\Temp on Windows, /tmp on Linux/Lambda

# ── Font setup ────────────────────────────────────────────────────────────────
FONT_URL      = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
FONT_BOLD_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"

def _ensure_fonts():
    pairs = [
        (os.path.join(TMP_DIR, "NotoSans-Regular.ttf"), FONT_URL,      "NotoSans"),
        (os.path.join(TMP_DIR, "NotoSans-Bold.ttf"),    FONT_BOLD_URL, "NotoSans-Bold"),
    ]
    registered = []
    for path, url, name in pairs:
        if not os.path.exists(path):
            try:
                print(f"[INFO] Downloading font {name} → {path}")
                urllib.request.urlretrieve(url, path)
            except Exception as e:
                print(f"[WARN] Font download failed for {name}: {e}")
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                registered.append(name)
                print(f"[INFO] Font registered: {name}")
            except Exception as e:
                print(f"[WARN] Font registration failed for {name}: {e}")
        else:
            print(f"[WARN] Font file not found after download attempt: {path}")
    return (
        "NotoSans"      if "NotoSans"      in registered else None,
        "NotoSans-Bold" if "NotoSans-Bold" in registered else None,
    )


# ── Text helpers ───────────────────────────────────────────────────────────────
def _safe(value, indent=False):
    if value is None: return ""
    if isinstance(value, (dict, list)):
        value = json.dumps(value, indent=2, ensure_ascii=False)
    value = str(value)
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", value)
    value = re.sub(r"[\u25A0-\u27BF]", "", value)
    value = escape(value)
    value = value.replace("\n", "<br/>")
    return value


def _list_to_html(items):
    if not items: return ""
    if isinstance(items, str):
        try: items = json.loads(items)
        except Exception: return _safe(items)
    if isinstance(items, list):
        parts = []
        for item in items:
            if isinstance(item, dict):
                if "risk" in item and "mitigation" in item:
                    parts.append(f"• <b>{_safe(item['risk'])}</b> — {_safe(item['mitigation'])}")
                elif "issue" in item and "fix" in item:
                    parts.append(f"• {_safe(item['issue'])} — <b>Fix:</b> {_safe(item['fix'])}")
                else:
                    text = "; ".join(f"{k}: {v}" for k, v in item.items() if v)
                    parts.append(f"• {_safe(text)}")
            else:
                parts.append(f"• {_safe(item)}")
        return "<br/>".join(parts)
    return _safe(items)


def _format_criteria(value):
    if isinstance(value, str):
        stripped = value.strip().strip("```json").strip("```").strip()
        for parser in (json.loads, ast.literal_eval):
            try: value = parser(stripped); break
            except Exception: pass
    if isinstance(value, dict):
        parts = []
        if value.get("inclusion"):
            parts.append("<b>Inclusion Criteria:</b><br/>")
            items = value["inclusion"] if isinstance(value["inclusion"], list) else [value["inclusion"]]
            parts.append("<br/>".join(f"{i}. {_safe(item)}" for i, item in enumerate(items, 1)))
        if value.get("exclusion"):
            if parts: parts.append("<br/><br/>")
            parts.append("<b>Exclusion Criteria:</b><br/>")
            items = value["exclusion"] if isinstance(value["exclusion"], list) else [value["exclusion"]]
            parts.append("<br/>".join(f"{i}. {_safe(item)}" for i, item in enumerate(items, 1)))
        if value.get("sample_size") and isinstance(value["sample_size"], dict):
            ss = value["sample_size"]
            parts.append(f"<br/><br/><b>Sample Size:</b> N={ss.get('n','?')} "
                         f"(Power: {ss.get('power','?')}, α={ss.get('alpha','?')})<br/>"
                         f"{_safe(ss.get('justification',''))}")
        combined = "".join(parts).strip()
        if combined: return combined
    return _safe(value)


# ── Main PDF function ──────────────────────────────────────────────────────────
def generate_pdf(protocol_json, fda_result, cdsco_result, session_id,
                 cohort_json=None, feasibility_json=None):

    font_name, bold_name = _ensure_fonts()
    if not font_name: font_name, bold_name = "Helvetica", "Helvetica-Bold"

    # ── Styles ────────────────────────────────────────────────────────────
    base   = ParagraphStyle("base",   fontName=font_name, fontSize=9.5, leading=14, spaceAfter=4)
    h1     = ParagraphStyle("h1",     fontName=bold_name, fontSize=18, leading=22, alignment=1, spaceAfter=10, textColor=colors.HexColor("#0f172a"))
    h2     = ParagraphStyle("h2",     fontName=bold_name, fontSize=13, leading=17, spaceAfter=6, spaceBefore=10, textColor=colors.HexColor("#1e3a8a"))
    h3     = ParagraphStyle("h3",     fontName=bold_name, fontSize=10.5, leading=14, spaceAfter=4, textColor=colors.HexColor("#1d4ed8"))
    small  = ParagraphStyle("small",  fontName=font_name, fontSize=8, leading=12, textColor=colors.HexColor("#64748b"))
    badge  = ParagraphStyle("badge",  fontName=bold_name, fontSize=11, leading=15, textColor=colors.HexColor("#166534"))

    filepath = os.path.join(TMP_DIR, f"protocol_{session_id}.pdf")
    print(f"[INFO] PDF target path: {filepath}")
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            leftMargin=52, rightMargin=52, topMargin=60, bottomMargin=55)
    story = []

    # ══ HEADER ════════════════════════════════════════════════════════════
    story.append(Paragraph("TrialGuard AI", h1))
    story.append(Paragraph("India-First Clinical Trial Protocol", ParagraphStyle("sub", fontName=font_name, fontSize=12, alignment=1, textColor=colors.HexColor("#334155"))))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Session: {session_id}  |  CDSCO Schedule Y + FDA 21 CFR Compliant", small))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1e3a8a")))
    story.append(Spacer(1, 8))

    # ══ COMPLIANCE SCORE CARDS ════════════════════════════════════════════
    fda_score   = fda_result.get("fda_score", "N/A")
    cdsco_score = cdsco_result.get("india_score", "N/A")
    fda_grade   = fda_result.get("grade", "")
    cdsco_grade = cdsco_result.get("cdsco_grade", "")
    fda_ready   = fda_result.get("submission_readiness", "")
    cdsco_ready = cdsco_result.get("cdsco_submission_status", "")

    score_table = Table([
        [Paragraph(f"<b>FDA 21 CFR Score</b><br/>{fda_score}/100", ParagraphStyle("sc", fontName=bold_name, fontSize=14, alignment=1, textColor=colors.white)),
         Paragraph(f"<b>CDSCO Schedule Y Score</b><br/>{cdsco_score}/100", ParagraphStyle("sc2", fontName=bold_name, fontSize=14, alignment=1, textColor=colors.white))],
        [Paragraph(fda_grade, ParagraphStyle("sg", fontName=font_name, fontSize=9, alignment=1, textColor=colors.white)),
         Paragraph(cdsco_grade, ParagraphStyle("sg2", fontName=font_name, fontSize=9, alignment=1, textColor=colors.white))],
    ], colWidths=[3.5*inch, 3.5*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#1e3a8a")),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor("#065f46")),
        ('ALIGN',    (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',   (0,0), (-1,-1), 'MIDDLE'),
        ('ROWHEIGHT', (0,0), (-1,0), 36),
        ('ROWHEIGHT', (0,1), (-1,1), 18),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ROUNDEDCORNERS', [4]),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 8))

    # Submission readiness badges
    story.append(Paragraph(f"FDA: {fda_ready}  |  CDSCO: {cdsco_ready}", badge))
    story.append(Spacer(1, 12))

    # ══ PROTOCOL SECTIONS ════════════════════════════════════════════════
    story.append(Paragraph("Protocol Details", h2))

    title = protocol_json.get("title", "N/A")
    proto_id = protocol_json.get("protocol_id", "N/A")
    story.append(Paragraph(f"<b>Title:</b> {_safe(title)}", base))
    story.append(Paragraph(f"<b>Protocol ID:</b> {_safe(proto_id)}", base))
    story.append(Spacer(1, 8))

    # Objective
    obj = protocol_json.get("objective", {})
    story.append(Paragraph("Objectives", h3))
    if isinstance(obj, dict):
        story.append(Paragraph(f"<b>Primary:</b> {_safe(obj.get('primary',''))}", base))
        sec = obj.get("secondary", [])
        if sec:
            story.append(Paragraph(f"<b>Secondary:</b>", base))
            story.append(Paragraph(_list_to_html(sec), base))
        india = obj.get("india_context", "")
        if india:
            story.append(Paragraph(f"<b>India Context:</b> {_safe(india)}", base))
    else:
        story.append(Paragraph(_safe(obj), base))
    story.append(Spacer(1, 8))

    # Patient Criteria
    story.append(Paragraph("Patient Criteria", h3))
    story.append(Paragraph(_format_criteria(protocol_json.get("patient_criteria", "N/A")), base))
    story.append(Spacer(1, 8))

    # Trial Design
    design = protocol_json.get("trial_design", {})
    story.append(Paragraph("Trial Design", h3))
    if isinstance(design, dict):
        story.append(Paragraph(f"<b>Type:</b> {_safe(design.get('type',''))}", base))
        story.append(Paragraph(f"<b>Duration:</b> {design.get('duration_weeks','?')} weeks", base))
        story.append(Paragraph(f"<b>Randomization:</b> {_safe(design.get('randomization',''))}", base))
        # Arms table
        arms = design.get("arms", [])
        if arms and isinstance(arms, list):
            arm_data = [["Arm", "N", "Dose", "Frequency", "Route"]]
            for arm in arms:
                if isinstance(arm, dict):
                    arm_data.append([arm.get("arm",""), str(arm.get("n","")),
                                     arm.get("dose",""), arm.get("frequency",""), arm.get("route","")])
            if len(arm_data) > 1:
                arm_table = Table(arm_data, colWidths=[1.4*inch, 0.5*inch, 1.8*inch, 1.0*inch, 0.8*inch])
                arm_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e0e7ff")),
                    ('FONTNAME',   (0,0), (-1,0), bold_name),
                    ('FONTSIZE',   (0,0), (-1,-1), 8.5),
                    ('GRID',       (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
                ]))
                story.append(arm_table)
        # Sites
        sites = design.get("sites", {})
        if isinstance(sites, dict):
            story.append(Paragraph(f"<b>Sites:</b> {sites.get('count','?')} sites in India", base))
            india_sites = sites.get("india_regions", [])
            if india_sites:
                story.append(Paragraph("<b>Recommended Sites:</b><br/>" + _list_to_html(india_sites), base))
    else:
        story.append(Paragraph(_safe(design), base))
    story.append(Spacer(1, 8))

    # Endpoints
    ep = protocol_json.get("endpoints", {})
    story.append(Paragraph("Endpoints", h3))
    if isinstance(ep, dict):
        story.append(Paragraph(f"<b>Primary:</b> {_safe(ep.get('primary',''))}", base))
        sec = ep.get("secondary", [])
        if sec:
            story.append(Paragraph(f"<b>Secondary:</b>", base))
            story.append(Paragraph(_list_to_html(sec), base))
        india_ep = ep.get("india_specific", "")
        if india_ep:
            story.append(Paragraph(f"<b>India-Specific:</b> {_safe(india_ep)}", base))
    else:
        story.append(Paragraph(_safe(ep), base))
    story.append(Spacer(1, 8))

    # Statistical Plan
    stat = protocol_json.get("statistical_plan", {})
    story.append(Paragraph("Statistical Plan", h3))
    if isinstance(stat, dict):
        for key, label in [("primary_analysis","Primary Analysis"), ("itt_population","ITT Population"),
                           ("interim_analysis","Interim Analysis"), ("multiplicity","Multiplicity")]:
            if stat.get(key):
                story.append(Paragraph(f"<b>{label}:</b> {_safe(stat[key])}", base))
    else:
        story.append(Paragraph(_safe(stat), base))
    story.append(Spacer(1, 8))

    # Regulatory Map
    reg = protocol_json.get("regulatory_map", {})
    story.append(Paragraph("Regulatory Compliance Map", h3))
    if isinstance(reg, dict):
        fda_secs = reg.get("fda_sections", [])
        if fda_secs:
            story.append(Paragraph(f"<b>FDA 21 CFR:</b><br/>{_list_to_html(fda_secs)}", base))
        cdsco_cls = reg.get("cdsco_clauses", [])
        if cdsco_cls:
            story.append(Paragraph(f"<b>CDSCO Schedule Y:</b><br/>{_list_to_html(cdsco_cls)}", base))
        ethics = reg.get("ethics", "")
        if ethics:
            story.append(Paragraph(f"<b>Ethics:</b> {_safe(ethics)}", base))
    story.append(Spacer(1, 8))

    # ══ COMPLIANCE DETAILS ════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
    story.append(Paragraph("FDA Compliance Analysis", h2))
    story.append(Paragraph(_safe(fda_result.get("verbal_summary", "")), base))

    failed = fda_result.get("clauses_failed", [])
    if failed:
        story.append(Paragraph("<b>Issues to Fix:</b>", base))
        for item in failed[:5]:
            if isinstance(item, dict):
                story.append(Paragraph(
                    f"• [{item.get('ref','')}] {_safe(item.get('issue',''))} → <b>Fix:</b> {_safe(item.get('fix','')[:150])}",
                    ParagraphStyle("fix", fontName=font_name, fontSize=8.5, leading=12, spaceAfter=3,
                                   leftIndent=10, textColor=colors.HexColor("#b91c1c"))
                ))
    critical = fda_result.get("critical_gaps", [])
    if critical:
        story.append(Paragraph(f"<b>⚠ Critical Gaps:</b> {_list_to_html(critical)}", base))
    story.append(Spacer(1, 8))

    story.append(Paragraph("CDSCO India Compliance Analysis", h2))
    story.append(Paragraph(_safe(cdsco_result.get("verbal_summary", "")), base))

    india_viol = cdsco_result.get("india_violations", [])
    if india_viol:
        story.append(Paragraph("<b>India-Specific Issues:</b>", base))
        for item in india_viol[:5]:
            if isinstance(item, dict):
                sev = item.get("severity", "")
                story.append(Paragraph(
                    f"• [{item.get('clause','')}] {_safe(item.get('issue','')[:120])} → {_safe(item.get('fix','')[:150])}",
                    ParagraphStyle("ifix", fontName=font_name, fontSize=8.5, leading=12, spaceAfter=3,
                                   leftIndent=10, textColor=colors.HexColor("#7c2d12"))
                ))
    unique_gaps = cdsco_result.get("unique_india_gaps", [])
    if unique_gaps:
        story.append(Paragraph(f"<b>India-Only Gaps:</b><br/>{_list_to_html(unique_gaps)}", base))
    story.append(Spacer(1, 8))

    # ══ COHORT SECTION ════════════════════════════════════════════════════
    if cohort_json and isinstance(cohort_json, dict) and not cohort_json.get("error"):
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
        story.append(Paragraph("Synthetic Indian Patient Cohort (SDV — Zero PHI)", h2))
        story.append(Paragraph(
            f"<b>Cohort Size:</b> {cohort_json.get('cohort_size',10000):,} synthetic patients  |  "
            f"<b>Disease:</b> {cohort_json.get('disease','').title()}  |  "
            f"<b>Eligibility Rate:</b> {cohort_json.get('eligibility_rate_pct','?')}%  |  "
            f"<b>Mean Dropout Risk:</b> {cohort_json.get('mean_dropout_pct','?')}%",
            base
        ))
        story.append(Paragraph(
            f"<b>Recommended Sample Size (dropout-adjusted):</b> N = {cohort_json.get('recommended_total_n','?')} total",
            base
        ))
        langs = cohort_json.get("languages_required", [])
        if langs:
            story.append(Paragraph(f"<b>ICF Languages Required:</b> {', '.join(langs)}", base))
        insights = cohort_json.get("india_specific_insights", [])
        if insights:
            story.append(Paragraph("<b>India-Specific Insights:</b>", base))
            story.append(Paragraph(_list_to_html(insights), base))
        story.append(Paragraph(cohort_json.get("sdv_note", ""), small))
        story.append(Spacer(1, 8))

    # ══ FEASIBILITY SECTION ═══════════════════════════════════════════════
    if feasibility_json and isinstance(feasibility_json, dict) and not feasibility_json.get("error"):
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
        story.append(Paragraph("India Site Feasibility Analysis", h2))
        feas = feasibility_json.get("feasibility", "Unknown")
        feas_score = feasibility_json.get("feasibility_score", 0)
        feas_color = {"High": "#166534", "Medium": "#92400e", "Low": "#991b1b"}.get(feas, "#1e3a8a")
        story.append(Paragraph(
            f"Feasibility: <b>{feas}</b> ({feas_score}/100)  |  "
            f"Est. Enrollment: {feasibility_json.get('enrollment_months_estimate','?')} months  |  "
            f"Recommendation: <b>{feasibility_json.get('go_no_go_recommendation','N/A')}</b>",
            ParagraphStyle("feas", fontName=bold_name, fontSize=10.5, leading=15,
                           textColor=colors.HexColor(feas_color))
        ))
        story.append(Paragraph(_safe(feasibility_json.get("verbal_summary", "")), base))

        rec_sites = feasibility_json.get("recommended_sites", [])
        if rec_sites:
            story.append(Paragraph(f"<b>Recommended Sites:</b><br/>{_list_to_html(rec_sites)}", base))

        gaps = feasibility_json.get("regional_gaps", [])
        if gaps:
            story.append(Paragraph(f"<b>Regional Gaps:</b> {', '.join(gaps)}", base))

        risks = feasibility_json.get("key_risks", [])
        if risks:
            story.append(Paragraph(f"<b>Key Risks:</b><br/>{_list_to_html(risks)}", base))
        story.append(Spacer(1, 8))

    # ══ FOOTER ════════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
    story.append(Paragraph(
        "⚠ LIMITATIONS: Synthetic data only — not for actual clinical trials. "
        "FDA/CDSCO analysis is AI-generated guidance, not legal advice. "
        "Verify all regulatory requirements with qualified regulatory affairs professionals.",
        small
    ))
    story.append(Paragraph("Generated by TrialGuard AI | AWS Bedrock | CDSCO Schedule Y + FDA 21 CFR | SDV Synthetic Cohort | Zero PHI", small))

    # ── Build PDF ─────────────────────────────────────────────────────────
    try:
        doc.build(story)
    except Exception as build_err:
        raise RuntimeError(f"ReportLab doc.build() failed: {build_err}") from build_err

    # ── Verify file was actually written ──────────────────────────────────
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"PDF build completed without error but file not found at: {filepath}\n"
            f"TMP_DIR={TMP_DIR} | Check write permissions."
        )

    file_size = os.path.getsize(filepath)
    print(f"[INFO] PDF built successfully: {filepath} ({file_size:,} bytes)")

    # ── S3 Upload ─────────────────────────────────────────────────────────
    bucket  = os.getenv('S3_BUCKET')
    s3_key  = f"pdfs/protocol_{session_id}.pdf"
    region  = os.getenv('AWS_REGION', 'us-east-1')

    if not bucket:
        raise ValueError("S3_BUCKET environment variable is not set")

    try:
        s3.upload_file(
            filepath, bucket, s3_key,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': 'application/pdf',
                'ContentDisposition': 'inline',
            }
        )
        print(f"[INFO] Uploaded to S3: s3://{bucket}/{s3_key}")
    except Exception as s3_err:
        raise RuntimeError(f"S3 upload failed: {s3_err}") from s3_err
    finally:
        # Always clean up local temp file
        try:
            os.remove(filepath)
        except Exception:
            pass

    return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"