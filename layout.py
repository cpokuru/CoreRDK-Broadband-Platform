"""Shared page shell for the CoreRDK-Broadband-Specification site: a fixed
left sidebar nav + content area, used by every page (both the ones generated
from spec-content.json and the static stub pages).

Not imported by the stub pages at runtime — this only runs at generation
time, in Python, to produce plain static HTML. Nothing here ships to the
browser as Python.
"""
from __future__ import annotations

import html

COMPONENTS_URL = "components/"

# (id, label, href, external) — external items get an "external link" arrow
# and open the components site rather than a local page in this repo.
NAV_LINKS = [
    ("about", "About & Architecture", "index.html", False),
    ("architecture-standards", "Architecture Standards", "architecture-standards.html", False),
    ("technical-governance", "Technical Governance", "technical-governance.html", False),
    ("nbi", "North Bound APIs", "north-bound-apis.html", False),
    ("sbi", "South Bound APIs", "south-bound-apis.html", False),
    ("hwcompat", "Hardware Compatibility", "hardware-compatibility.html", False),
    ("components", "Core RDK Components", COMPONENTS_URL, True),
]

SHARED_CSS = """
  :root {
    --bedrock: #080d18; --hal: #16305a; --middleware: #2a5cf0; --mgmt: #0aa66e;
    --cloud-bg: #eef1ff; --cloud-fg: #3730a3; --ink: #0b1220; --muted: #5b6472;
    --page-bg: #f6f7fb; --card-bg: #ffffff; --border: #e5e8f0;
    --amber-fg: #b45309; --amber-bg: #fef3c7;
    --sidebar-w: 268px;
    --rdk-blue: #29b6e8; --rdk-amber: #f5a623; --rdk-green: #7ac943; --rdk-orange: #f0653e;
    --shadow-sm: 0 1px 2px rgba(15,23,42,0.06), 0 1px 1px rgba(15,23,42,0.04);
    --shadow-md: 0 8px 24px rgba(15,23,42,0.08), 0 2px 6px rgba(15,23,42,0.04);
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body { margin: 0; font-family: "Inter", -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: var(--ink); background: var(--page-bg); line-height: 1.6; -webkit-font-smoothing: antialiased; }
  code, .mono { font-family: "JetBrains Mono", ui-monospace, monospace; }
  a { color: var(--middleware); }
  h1, h2, h3, h4 { font-family: "Space Grotesk", "Inter", sans-serif; font-weight: 700; letter-spacing: -0.015em; margin: 0; color: var(--ink); }
  p { margin: 0 0 12px; color: var(--muted); }

  /* ---- top accent bar, echoes the RDK mark's four bars ---- */
  .accent-bar {
    height: 5px; width: 100%;
    background: linear-gradient(90deg, var(--rdk-blue) 0%, var(--rdk-blue) 25%, var(--rdk-green) 25%, var(--rdk-green) 50%, var(--rdk-amber) 50%, var(--rdk-amber) 75%, var(--rdk-orange) 75%, var(--rdk-orange) 100%);
    position: fixed; top: 0; left: 0; z-index: 60;
  }

  /* ---- sidebar ---- */
  .sidebar {
    position: fixed; top: 5px; left: 0; bottom: 0; width: var(--sidebar-w);
    background: linear-gradient(160deg, #080d18 0%, #0e1a35 60%, #0a1530 100%);
    color: #fff; overflow-y: auto; z-index: 50;
    padding: 24px 0 24px;
    border-right: 1px solid rgba(255,255,255,0.06);
  }
  .sidebar .brand { display: flex; flex-direction: column; align-items: flex-start; gap: 12px; padding: 4px 22px 22px; letter-spacing: -0.01em; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 14px; }
  .sidebar .brand img { height: 34px; width: auto; display: block; }
  .sidebar .brand-text { font-family: "Space Grotesk", sans-serif; font-weight: 600; font-size: 0.94rem; line-height: 1.35; color: #fff; width: 100%; overflow-wrap: break-word; }
  .sidebar .brand-text .mono { display: block; color: #6fa8e8; font-size: 0.72rem; font-weight: 500; margin-top: 5px; letter-spacing: 0.02em; }
  .sidebar nav { display: flex; flex-direction: column; padding: 6px 12px; gap: 2px; }
  .sidebar nav a {
    display: flex; align-items: center; justify-content: space-between;
    color: #aab8d4; text-decoration: none; font-size: 0.88rem; font-weight: 500;
    padding: 10px 13px; border-radius: 8px; transition: background 0.12s, color 0.12s;
  }
  .sidebar nav a:hover { color: #fff; background: rgba(255,255,255,0.055); }
  .sidebar nav a.active { color: #fff; background: linear-gradient(90deg, rgba(42,92,240,0.55), rgba(42,92,240,0.22)); font-weight: 600; box-shadow: inset 2px 0 0 var(--rdk-blue); }
  .sidebar nav a .ext-arrow { font-size: 0.78em; color: #6fa8e8; }
  .sidebar .nav-group-label {
    font-family: "JetBrains Mono", monospace; font-size: 0.66rem; letter-spacing: 0.08em;
    text-transform: uppercase; color: #4f6188; padding: 16px 22px 6px;
  }

  /* ---- main content area ---- */
  .page-main { margin-left: var(--sidebar-w); min-height: 100vh; margin-top: 5px; }

  @media (max-width: 860px) {
    :root { --sidebar-w: 0px; }
    .sidebar { position: static; width: 100%; padding: 16px 0; top: 0; }
    .sidebar .brand { padding: 0 18px 14px; }
    .sidebar nav { flex-direction: row; flex-wrap: wrap; padding: 0 12px; }
    .sidebar nav a { padding: 7px 11px; font-size: 0.82rem; }
    .page-main { margin-left: 0; }
  }

  /* ---- hero ---- */
  .hero { background: radial-gradient(ellipse 900px 500px at 15% 0%, #14245a 0%, transparent 60%), linear-gradient(165deg, #080d18 0%, #0d1730 55%, #0a1226 100%); color: #fff; padding: 68px 44px 52px; position: relative; overflow: hidden; }
  .hero-flex { display: flex; align-items: center; gap: 44px; max-width: 1180px; }
  .hero-inner { max-width: 640px; flex: 1 1 auto; min-width: 0; }
  .hero-visual { flex: 0 0 320px; display: flex; justify-content: center; }
  @media (max-width: 1000px) { .hero-visual { display: none; } }

  .eyebrow { display: inline-block; font-family: "JetBrains Mono", monospace; font-size: 0.72rem; letter-spacing: 0.09em; text-transform: uppercase; color: #7ec4f2; border: 1px solid rgba(126,196,242,0.35); background: rgba(126,196,242,0.06); border-radius: 999px; padding: 5px 13px; margin-bottom: 20px; }
  .hero h1 { font-size: 2.5rem; line-height: 1.12; color: #fff; max-width: 760px; }
  .hero .lede { color: #a9b8d6; font-size: 1.08rem; max-width: 640px; margin-top: 16px; }
  .badge-row { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 28px; }
  .badge { display: inline-block; margin: 0 10px 10px 0; font-size: 0.8rem; font-weight: 600; padding: 7px 14px; border-radius: 999px; background: rgba(255,255,255,0.07); color: #dbe4f3; border: 1px solid rgba(255,255,255,0.12); }
  .stats { max-width: 900px; margin: -32px 44px 0; padding: 0; display: flex; gap: 1px; background: var(--border); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; position: relative; z-index: 2; box-shadow: var(--shadow-md); }
  .stat { flex: 1; min-width: 0; background: #fff; padding: 22px 16px; text-align: center; border-top: 3px solid transparent; }
  .stat:nth-child(1) { border-top-color: var(--rdk-blue); }
  .stat:nth-child(2) { border-top-color: var(--rdk-green); }
  .stat:nth-child(3) { border-top-color: var(--rdk-amber); }
  .stat:nth-child(4) { border-top-color: var(--rdk-orange); }
  .stat:nth-child(5) { border-top-color: var(--middleware); }
  .stat .num { font-family: "Space Grotesk", sans-serif; font-size: 1.55rem; font-weight: 700; color: var(--ink); }
  .stat .lbl { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 3px; font-weight: 500; }
  @media (max-width: 760px) { .stats { flex-wrap: wrap; margin: -20px 16px 0; } .stat { flex: 1 1 40%; } .hero { padding: 48px 20px 40px; } }

  /* ---- sections ---- */
  section { max-width: 900px; margin: 0 auto; padding: 60px 44px; }
  section.tight-top { padding-top: 52px; }
  @media (max-width: 760px) { section { padding: 40px 20px; } }
  .section-head { margin-bottom: 34px; }
  .section-head .eyebrow-lt { font-family: "JetBrains Mono", monospace; font-size: 0.74rem; letter-spacing: 0.09em; text-transform: uppercase; color: var(--middleware); font-weight: 600; margin-bottom: 9px; display: block; }
  .section-head h2 { font-size: 1.85rem; }
  .section-head p { margin-top: 11px; font-size: 1.02rem; max-width: 680px; }
  .callout { background: linear-gradient(135deg, #eef2ff 0%, #f3f0ff 100%); border: 1px solid #d3dbfb; border-left: 4px solid var(--middleware); border-radius: 10px; padding: 22px 26px; margin: 18px 0; }
  .callout strong { color: var(--ink); display: block; margin-bottom: 5px; font-size: 0.95rem; font-family: "Space Grotesk", sans-serif; }
  .callout p { margin: 0; font-size: 0.95rem; }
  .two-col { display: flex; gap: 28px; }
  .two-col > * { flex: 1; min-width: 0; }
  @media (max-width: 760px) { .two-col { flex-direction: column; } }
  .card { background: var(--card-bg); border: 1px solid var(--border); border-left: 3px solid var(--middleware); border-radius: 12px; padding: 22px 24px; box-shadow: var(--shadow-sm); transition: box-shadow 0.15s, transform 0.15s; }
  .card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
  .card h3 { font-size: 1.02rem; margin-bottom: 9px; }
  .card p { font-size: 0.92rem; margin: 0; }
  table.def-table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 0.9rem; }
  table.def-table th, table.def-table td { text-align: left; padding: 11px 14px; border-bottom: 1px solid var(--border); vertical-align: top; }
  table.def-table th { background: #f1f3f9; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); font-weight: 600; }
  table.def-table tbody tr:hover { background: #fafbff; }
  table.def-table td.mono { color: var(--ink); font-weight: 600; }
  .timeline { border-left: 2px solid var(--border); margin-left: 6px; padding-left: 24px; display: flex; flex-direction: column; gap: 18px; }
  .tl-item { position: relative; }
  .tl-item::before { content: ""; position: absolute; left: -29px; top: 4px; width: 10px; height: 10px; border-radius: 50%; background: var(--middleware); border: 2px solid #fff; box-shadow: 0 0 0 2px var(--middleware); }
  .tl-year { font-family: "JetBrains Mono", monospace; font-weight: 700; color: var(--middleware); font-size: 0.86rem; }
  .tl-item p { margin: 2px 0 0; font-size: 0.92rem; }
  .tier-diagram { border-radius: 16px; overflow: hidden; border: 1px solid var(--border); box-shadow: var(--shadow-md); }
  .tier { display: flex; align-items: stretch; border-bottom: 1px solid rgba(255,255,255,0.12); }
  .tier:last-child { border-bottom: none; }
  .tier .num { flex: 0 0 64px; display: flex; align-items: center; justify-content: center; font-family: "Space Grotesk", sans-serif; font-weight: 700; font-size: 1.15rem; }
  .tier .body { flex: 1; padding: 19px 24px; }
  .tier .body h4 { margin: 0 0 4px; font-size: 1.02rem; }
  .tier .body p { margin: 0; font-size: 0.88rem; }
  .tier.t5 { background: var(--cloud-bg); color: var(--cloud-fg); }
  .tier.t5 .num { background: #d9e2ff; color: var(--cloud-fg); }
  .tier.t4 { background: #e3f7ef; color: #065f46; }
  .tier.t4 .num { background: var(--mgmt); color: #fff; }
  .tier.t3 { background: var(--middleware); color: #fff; }
  .tier.t3 .num { background: #1a3fb5; color: #fff; }
  .tier.t3 .body p { color: #dce6ff; }
  .tier.t2 { background: var(--hal); color: #fff; }
  .tier.t2 .num { background: #0e2144; color: #fff; }
  .tier.t2 .body p { color: #c5d3e6; }
  .tier.t1 { background: var(--bedrock); color: #fff; }
  .tier.t1 .num { background: #000308; color: #9fb2cf; }
  .tier.t1 .body p { color: #9fb2cf; }
  .tier-caption { text-align: center; font-size: 0.82rem; color: var(--muted); margin-top: 12px; }
  .layer-stack { display: flex; flex-direction: column; gap: 6px; }
  .layer-box { margin-bottom: 6px; border-radius: 9px; padding: 13px 16px; font-size: 0.86rem; font-weight: 600; text-align: center; }
  .layer-box:last-child { margin-bottom: 0; }
  .layer-box.top { background: var(--middleware); color: #fff; }
  .layer-box.mid { background: var(--hal); color: #fff; }
  .layer-box.bot { background: #e2e8f0; color: var(--ink); }
  .subhead { font-family: "Space Grotesk", sans-serif; font-size: 1.2rem; font-weight: 700; margin: 36px 0 14px; }
  .subhead:first-of-type { margin-top: 8px; }
  footer { background: var(--bedrock); color: #9fb2cf; padding: 44px 44px 30px; }
  .footer-links { display: flex; flex-wrap: wrap; gap: 28px; margin-bottom: 22px; max-width: 900px; }
  .footer-links a { display: block; min-width: 200px; margin: 0 28px 14px 0; color: #dbe4f3; text-decoration: none; font-size: 0.9rem; font-weight: 600; }
  .footer-links a span { display: block; font-weight: 400; color: #8493ab; font-size: 0.8rem; margin-top: 2px; }
  .footer-meta { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 18px; font-size: 0.78rem; color: #7386a3; max-width: 900px; }
  .pill-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
  .pill { display: inline-block; margin: 0 8px 8px 0; font-size: 0.78rem; font-weight: 600; padding: 5px 12px; border-radius: 999px; background: #f1f3f9; color: var(--ink); border: 1px solid var(--border); }

  /* ---- empty-state (for the not-yet-populated API/HW pages) ---- */
  .empty-state { max-width: 560px; margin: 40px auto; text-align: center; padding: 48px 32px; background: #fff; border: 1px dashed var(--border); border-radius: 16px; }
  .empty-state .icon { font-size: 2rem; margin-bottom: 12px; }
  .empty-state h3 { font-size: 1.1rem; margin-bottom: 8px; }
  .empty-state p { font-size: 0.92rem; }
  .empty-state code { display: inline-block; background: #f1f3f9; padding: 2px 8px; border-radius: 5px; margin-top: 4px; }
"""


def esc(s) -> str:
    return html.escape("" if s is None else str(s))


# Custom isometric illustrations for each page's hero — no photography, no
# third-party assets, so there's no licensing question, and each is
# thematically literal to its page rather than one image reused everywhere.
# All six share a visual language (isometric block, dashed data-flow lines,
# colored accent markers, faint circuit-trace background) so the site still
# feels like one family, but the subject differs per topic.

_CIRCUIT_BG = """
  <g opacity="0.14" stroke="#8fb3ff" stroke-width="1" fill="none">
    <path d="M20 40 H70 V80 H110"/>
    <circle cx="70" cy="40" r="2.5" fill="#8fb3ff" stroke="none"/>
    <circle cx="70" cy="80" r="2.5" fill="#8fb3ff" stroke="none"/>
    <path d="M300 60 H250 V100 H210"/>
    <circle cx="250" cy="60" r="2.5" fill="#8fb3ff" stroke="none"/>
    <circle cx="250" cy="100" r="2.5" fill="#8fb3ff" stroke="none"/>
    <path d="M30 260 H80 V290"/>
    <circle cx="80" cy="260" r="2.5" fill="#8fb3ff" stroke="none"/>
    <path d="M290 250 H260 V300 H300"/>
    <circle cx="260" cy="250" r="2.5" fill="#8fb3ff" stroke="none"/>
    <circle cx="260" cy="300" r="2.5" fill="#8fb3ff" stroke="none"/>
  </g>
"""

HERO_VISUALS = {

    # About & Architecture — gateway/router device with antennas and WiFi.
    "about": f"""
<svg viewBox="0 0 320 320" width="320" height="320" role="img" aria-label="Illustration of a networking gateway device">
  {_CIRCUIT_BG}
  <g opacity="0.9">
    <path d="M198 96 Q225 70 252 90" fill="none" stroke="#29b6e8" stroke-width="2.5" stroke-linecap="round" opacity="0.85"/>
    <path d="M204 106 Q225 88 246 104" fill="none" stroke="#29b6e8" stroke-width="2.5" stroke-linecap="round" opacity="0.6"/>
    <path d="M210 116 Q225 105 240 115" fill="none" stroke="#29b6e8" stroke-width="2.5" stroke-linecap="round" opacity="0.4"/>
  </g>
  <g stroke="#1c3a5e" stroke-width="1.5" stroke-linecap="round">
    <line x1="185" y1="130" x2="170" y2="75"/>
    <line x1="205" y1="122" x2="218" y2="92"/>
  </g>
  <circle cx="170" cy="72" r="4" fill="#29b6e8"/>
  <circle cx="219" cy="89" r="4" fill="#29b6e8"/>
  <polygon points="160,90 230,130 160,170 90,130" fill="#3b7de8"/>
  <polygon points="90,130 160,170 160,250 90,210" fill="#1c3a5e"/>
  <polygon points="160,170 230,130 230,210 160,250" fill="#0f2744"/>
  <circle cx="185" cy="200" r="5" fill="#7ac943"/>
  <circle cx="200" cy="208" r="5" fill="#f5a623"/>
  <circle cx="215" cy="216" r="5" fill="#29b6e8"/>
  <g stroke="#f5a623" stroke-width="1.5" stroke-dasharray="3,4" opacity="0.7">
    <line x1="90" y1="150" x2="55" y2="120"/>
  </g>
  <polygon points="55,105 70,113 55,121 40,113" fill="#f5a623" opacity="0.9"/>
  <g stroke="#7ac943" stroke-width="1.5" stroke-dasharray="3,4" opacity="0.7">
    <line x1="230" y1="190" x2="268" y2="215"/>
  </g>
  <polygon points="268,200 283,208 268,216 253,208" fill="#7ac943" opacity="0.9"/>
</svg>
""",

    # Architecture Standards — isometric certification shield with a checkmark.
    "architecture-standards": f"""
<svg viewBox="0 0 320 320" width="320" height="320" role="img" aria-label="Illustration of a certification shield">
  {_CIRCUIT_BG}
  <polygon points="160,60 225,90 225,175 160,235 95,175 95,90" fill="#1c3a5e"/>
  <polygon points="160,60 225,90 160,120 95,90" fill="#3b7de8"/>
  <polygon points="95,90 160,120 160,235 95,175" fill="#16305a"/>
  <polygon points="160,120 225,90 225,175 160,235" fill="#0f2744"/>
  <path d="M128 150 L152 176 L196 122" fill="none" stroke="#7ac943" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
  <g stroke="#f5a623" stroke-width="1.5" stroke-dasharray="3,4" opacity="0.75">
    <line x1="95" y1="130" x2="55" y2="105"/>
  </g>
  <polygon points="55,90 70,98 55,106 40,98" fill="#f5a623" opacity="0.9"/>
  <g stroke="#29b6e8" stroke-width="1.5" stroke-dasharray="3,4" opacity="0.75">
    <line x1="225" y1="130" x2="265" y2="155"/>
  </g>
  <circle cx="272" cy="160" r="7" fill="#29b6e8" opacity="0.9"/>
  <g stroke="#7ac943" stroke-width="1.5" stroke-dasharray="3,4" opacity="0.65">
    <line x1="160" y1="235" x2="160" y2="275"/>
  </g>
  <polygon points="150,278 160,293 170,278" fill="#7ac943" opacity="0.9"/>
</svg>
""",

    # Technical Governance — stacked policy/process document plates.
    "technical-governance": f"""
<svg viewBox="0 0 320 320" width="320" height="320" role="img" aria-label="Illustration of stacked governance documents">
  {_CIRCUIT_BG}
  <g opacity="0.95">
    <polygon points="105,195 215,195 245,213 135,213" fill="#0f2744"/>
    <polygon points="105,195 135,213 135,225 105,207" fill="#0c2038"/>
    <polygon points="135,213 245,213 245,225 135,225" fill="#16305a"/>
  </g>
  <g opacity="0.97">
    <polygon points="100,160 210,160 240,178 130,178" fill="#16305a"/>
    <polygon points="100,160 130,178 130,190 100,172" fill="#122a4c"/>
    <polygon points="130,178 240,178 240,190 130,190" fill="#1c3a5e"/>
  </g>
  <g>
    <polygon points="95,122 205,122 235,140 125,140" fill="#3b7de8"/>
    <polygon points="95,122 125,140 125,152 95,134" fill="#2a63c9"/>
    <polygon points="125,140 235,140 235,152 125,152" fill="#1a56db"/>
    <line x1="140" y1="128" x2="185" y2="128" stroke="#dbe6ff" stroke-width="2" stroke-linecap="round" opacity="0.7"/>
    <line x1="140" y1="134" x2="170" y2="134" stroke="#dbe6ff" stroke-width="2" stroke-linecap="round" opacity="0.5"/>
  </g>
  <circle cx="235" cy="95" r="16" fill="#7ac943"/>
  <path d="M227 95 L233 101 L245 88" fill="none" stroke="#0f2744" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <g stroke="#f5a623" stroke-width="1.5" stroke-dasharray="3,4" opacity="0.7">
    <line x1="95" y1="150" x2="55" y2="170"/>
  </g>
  <polygon points="40,170 55,178 55,162" fill="#f5a623" opacity="0.9"/>
</svg>
""",

    # North Bound APIs — cloud, with data flowing UP into it from the device below.
    "nbi": f"""
<svg viewBox="0 0 320 320" width="320" height="320" role="img" aria-label="Illustration of northbound cloud APIs">
  {_CIRCUIT_BG}
  <g fill="#3b7de8">
    <circle cx="145" cy="105" r="34"/>
    <circle cx="185" cy="95" r="26"/>
    <circle cx="205" cy="115" r="30"/>
    <circle cx="160" cy="128" r="30"/>
  </g>
  <rect x="110" y="105" width="120" height="35" rx="17" fill="#3b7de8"/>
  <polygon points="140,220 190,220 190,255 140,255" fill="#1c3a5e"/>
  <polygon points="140,220 155,210 205,210 190,220" fill="#3b7de8"/>
  <polygon points="190,220 205,210 205,245 190,255" fill="#0f2744"/>
  <circle cx="150" cy="238" r="3" fill="#7ac943"/>
  <circle cx="160" cy="238" r="3" fill="#f5a623"/>
  <g stroke="#7ac943" stroke-width="2" stroke-dasharray="4,5" opacity="0.85">
    <line x1="165" y1="210" x2="165" y2="160"/>
  </g>
  <polygon points="157,163 165,148 173,163" fill="#7ac943"/>
  <g stroke="#f5a623" stroke-width="2" stroke-dasharray="4,5" opacity="0.7">
    <line x1="130" y1="205" x2="110" y2="165"/>
  </g>
  <polygon points="99,168 112,153 122,170" fill="#f5a623" opacity="0.9"/>
</svg>
""",

    # South Bound APIs — chip/silicon, with data flowing DOWN into it from above.
    "sbi": f"""
<svg viewBox="0 0 320 320" width="320" height="320" role="img" aria-label="Illustration of southbound HAL APIs into silicon">
  {_CIRCUIT_BG}
  <polygon points="160,110 225,148 160,186 95,148" fill="#3b7de8"/>
  <polygon points="95,148 160,186 160,225 95,187" fill="#1c3a5e"/>
  <polygon points="160,186 225,148 225,187 160,225" fill="#0f2744"/>
  <g stroke="#16305a" stroke-width="3" stroke-linecap="round">
    <line x1="115" y1="160" x2="95" y2="160"/>
    <line x1="115" y1="175" x2="95" y2="175"/>
    <line x1="205" y1="160" x2="225" y2="160"/>
    <line x1="205" y1="175" x2="225" y2="175"/>
  </g>
  <rect x="145" y="145" width="30" height="30" rx="3" fill="#0b1220"/>
  <circle cx="155" cy="155" r="2" fill="#29b6e8"/>
  <circle cx="165" cy="155" r="2" fill="#7ac943"/>
  <circle cx="155" cy="165" r="2" fill="#f5a623"/>
  <circle cx="165" cy="165" r="2" fill="#29b6e8"/>
  <g stroke="#29b6e8" stroke-width="2" stroke-dasharray="4,5" opacity="0.85">
    <line x1="160" y1="95" x2="160" y2="120"/>
  </g>
  <polygon points="152,110 160,125 168,110" fill="#29b6e8"/>
  <g stroke="#f5a623" stroke-width="1.5" stroke-dasharray="3,4" opacity="0.7">
    <line x1="95" y1="130" x2="60" y2="105"/>
  </g>
  <circle cx="52" cy="98" r="6" fill="#f5a623" opacity="0.9"/>
</svg>
""",

    # Hardware Compatibility — circuit board with multiple vendor SoCs, certified.
    "hwcompat": f"""
<svg viewBox="0 0 320 320" width="320" height="320" role="img" aria-label="Illustration of certified hardware compatibility">
  {_CIRCUIT_BG}
  <polygon points="160,95 235,137 160,179 85,137" fill="#16305a"/>
  <polygon points="85,137 160,179 160,235 85,193" fill="#0f2744"/>
  <polygon points="160,179 235,137 235,193 160,235" fill="#0a1930"/>
  <g stroke="#22406e" stroke-width="1" opacity="0.6">
    <line x1="105" y1="150" x2="105" y2="180"/>
    <line x1="125" y1="160" x2="125" y2="195"/>
    <line x1="195" y1="160" x2="195" y2="195"/>
    <line x1="215" y1="150" x2="215" y2="180"/>
  </g>
  <g>
    <polygon points="145,110 168,122 145,134 122,122" fill="#3b7de8"/>
    <polygon points="192,110 215,122 192,134 169,122" fill="#7ac943"/>
    <polygon points="145,140 168,152 145,164 122,152" fill="#f5a623"/>
  </g>
  <circle cx="245" cy="100" r="18" fill="#7ac943"/>
  <path d="M236 100 L243 107 L256 92" fill="none" stroke="#0f2744" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
  <g stroke="#29b6e8" stroke-width="1.5" stroke-dasharray="3,4" opacity="0.7">
    <line x1="85" y1="160" x2="50" y2="180"/>
  </g>
  <polygon points="35,180 50,188 50,172" fill="#29b6e8" opacity="0.9"/>
</svg>
""",
}


def render_hero(eyebrow: str, title: str, lede: str, badges_html: str = "", compact: bool = False, visual_key: str = "about") -> str:
    """Shared hero markup: eyebrow, heading, lede paragraph, optional badge
    row, and the network-hardware illustration on wide screens. Used by
    every page so the visual upgrade applies everywhere consistently.
    title/lede are escaped here — pass plain text, not pre-escaped HTML."""
    pad = "48px 40px 40px" if compact else "64px 40px 48px"
    title_style = ' style="font-size:2rem;"' if compact else ""
    badges = f'<div class="badge-row">{badges_html}</div>' if badges_html else ""
    return f'''
<div class="hero" style="padding:{pad};">
  <div class="hero-flex">
    <div class="hero-inner">
      <span class="eyebrow">{esc(eyebrow)}</span>
      <h1{title_style}>{esc(title)}</h1>
      <p class="lede">{esc(lede)}</p>
      {badges}
    </div>
    <div class="hero-visual">{HERO_VISUALS.get(visual_key, HERO_VISUALS["about"])}</div>
  </div>
</div>
'''


def render_sidebar(active_id: str) -> str:
    links_html = []
    for id_, label, href, external in NAV_LINKS:
        cls = "active" if id_ == active_id else ""
        arrow = '<span class="ext-arrow">↗</span>' if external else ""
        links_html.append(f'<a class="{cls}" href="{esc(href)}">{esc(label)}{arrow}</a>')
    return f'''<div class="sidebar">
  <div class="brand">
    <img src="RDK-logo.png" alt="RDK logo" onerror="this.style.display='none'">
    <div class="brand-text">RDK-B Core Broadband</div>
  </div>
  <nav>
    {"".join(links_html)}
  </nav>
</div>'''


def render_page(active_id: str, head_extra: str, body_html: str) -> str:
    """Wrap body_html (hero + sections + footer, everything but <head>/sidebar)
    in the shared shell. body_html should NOT include <html>/<head>/<body> tags."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{SHARED_CSS}</style>
{head_extra}
</head>
<body>
<div class="accent-bar"></div>
{render_sidebar(active_id)}
<div class="page-main">
{body_html}
</div>
</body>
</html>
'''
