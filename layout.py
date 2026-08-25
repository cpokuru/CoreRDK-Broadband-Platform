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
    ("about", "About Core RDK Broadband", "index.html", False),
    ("architecture-standards", "Architecture Standards", "architecture-standards.html", False),
    ("technical-governance", "Development Standards", "technical-governance.html", False),
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

  /* ---- top nav (mega-nav style) ---- */
  .topnav {
    position: fixed; top: 5px; left: 0; right: 0; z-index: 50;
    background: rgba(8,13,24,0.92); backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 28px; gap: 20px;
  }
  .topnav .brand { display: flex; align-items: center; gap: 10px; flex: 0 0 auto; }
  .topnav .brand img { height: 26px; width: auto; display: block; }
  .topnav .brand-text { font-family: "Space Grotesk", sans-serif; font-weight: 600; font-size: 0.86rem; color: #fff; white-space: nowrap; }
  .topnav nav { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; overflow-x: auto; }
  .topnav nav a {
    color: #aab8d4; text-decoration: none; font-size: 0.82rem; font-weight: 500;
    padding: 8px 12px; border-radius: 6px; white-space: nowrap;
    border-bottom: 2px solid transparent; transition: color 0.12s;
  }
  .topnav nav a:hover { color: #fff; }
  .topnav nav a.active { color: var(--rdk-blue); border-bottom-color: var(--rdk-blue); font-weight: 600; }
  .topnav nav a .ext-arrow { font-size: 0.78em; color: #6fa8e8; }
  .topnav .cta {
    flex: 0 0 auto; background: linear-gradient(90deg, var(--rdk-blue), #7c3aed); color: #fff;
    font-size: 0.76rem; font-weight: 600; padding: 7px 14px; border-radius: 999px;
    text-decoration: none; white-space: nowrap;
  }

  /* ---- main content area ---- */
  .page-main { min-height: 100vh; margin-top: 61px; }

  @media (max-width: 900px) {
    .topnav { flex-wrap: wrap; padding: 10px 16px; }
    .topnav nav { order: 3; width: 100%; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.08); margin-top: 8px; }
    .page-main { margin-top: 108px; }
  }

  /* ---- hero ---- */
  .hero {
    background:
      radial-gradient(ellipse 480px 320px at 12% 10%, rgba(41,182,232,0.35), transparent 60%),
      radial-gradient(ellipse 420px 320px at 92% 85%, rgba(122,201,67,0.18), transparent 60%),
      linear-gradient(120deg, #0a1a3d 0%, #17246a 40%, #2b1a5e 75%, #3a1a4c 100%);
    color: #fff; padding: 68px 44px 52px; position: relative; overflow: hidden;
  }
  .hero-flex { display: flex; align-items: center; gap: 44px; max-width: 1520px; }
  .hero-inner { max-width: 640px; flex: 1 1 auto; min-width: 0; }
  .hero-visual { flex: 0 0 320px; display: flex; justify-content: center; }
  .hero-visual img { max-width: 100%; max-height: 320px; width: auto; height: auto; border-radius: 14px; object-fit: contain; }
  @media (max-width: 1000px) { .hero-visual { display: none; } }

  .eyebrow { display: inline-block; font-family: "JetBrains Mono", monospace; font-size: 0.72rem; letter-spacing: 0.09em; text-transform: uppercase; color: #7ec4f2; border: 1px solid rgba(126,196,242,0.35); background: rgba(126,196,242,0.06); border-radius: 999px; padding: 5px 13px; margin-bottom: 20px; }
  .hero h1 { font-size: 2.5rem; line-height: 1.12; color: #fff; max-width: 760px; }
  .hero .lede { color: #a9b8d6; font-size: 1.08rem; max-width: 640px; margin-top: 16px; }
  .badge-row { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 28px; }
  .badge { display: inline-block; margin: 0 10px 10px 0; font-size: 0.8rem; font-weight: 600; padding: 7px 14px; border-radius: 999px; background: rgba(255,255,255,0.07); color: #dbe4f3; border: 1px solid rgba(255,255,255,0.12); }
  .stats { max-width: 1520px; margin: -32px 44px 0; padding: 0; display: flex; gap: 1px; background: var(--border); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; position: relative; z-index: 2; box-shadow: var(--shadow-md); }
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
  section { max-width: 1520px; margin: 0; padding: 60px 44px; }
  section.tight-top { padding-top: 52px; }
  @media (max-width: 760px) { section { padding: 40px 20px; } }
  .section-head { margin-bottom: 34px; }
  .section-head .eyebrow-lt { font-family: "JetBrains Mono", monospace; font-size: 0.74rem; letter-spacing: 0.09em; text-transform: uppercase; color: var(--middleware); font-weight: 600; margin-bottom: 9px; display: block; }
  .section-head h2 { font-size: 1.85rem; }
  .section-head p { margin-top: 11px; font-size: 1.02rem; max-width: 680px; }
  .callout { max-width: 820px; background: linear-gradient(135deg, #eef2ff 0%, #f3f0ff 100%); border: 1px solid #d3dbfb; border-left: 4px solid var(--middleware); border-radius: 10px; padding: 22px 26px; margin: 18px 0; }
  .callout strong { color: var(--ink); display: block; margin-bottom: 5px; font-size: 0.95rem; font-family: "Space Grotesk", sans-serif; }
  .callout p { margin: 0; font-size: 0.95rem; }
  .two-col { display: flex; gap: 28px; }
  .two-col > * { flex: 1; min-width: 0; }
  @media (max-width: 760px) { .two-col { flex-direction: column; } }
  .card { max-width: 820px; background: var(--card-bg); border: 1px solid var(--border); border-left: 3px solid var(--middleware); border-radius: 12px; padding: 22px 24px; box-shadow: var(--shadow-sm); transition: box-shadow 0.15s, transform 0.15s; }

  /* ---- quick-link card row (colorful teaser cards, e.g. "Why RDKB Core") ---- */
  .quicklink-row { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 4px; margin: 4px 0 8px; }
  .quicklink-card {
    flex: 1 1 168px; min-width: 168px; background: var(--card-bg); border: 1px solid var(--border);
    border-top: 3px solid var(--ql-color, var(--middleware)); border-radius: 12px;
    padding: 14px 16px; text-decoration: none; box-shadow: var(--shadow-sm);
    transition: box-shadow 0.15s, transform 0.15s;
  }
  .quicklink-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
  .quicklink-card .ql-icon { color: var(--ql-color, var(--middleware)); margin-bottom: 8px; display: block; }
  .quicklink-card .ql-title { font-size: 0.86rem; font-weight: 600; color: var(--ink); }
  .quicklink-card .ql-cta { font-size: 0.78rem; font-weight: 600; color: var(--ql-color, var(--middleware)); margin-top: 8px; }

  /* ---- color-tinted section panels (e.g. Why RDKB Core, RDK Ready, Benefits) ---- */
  .section-tint { border-radius: 16px; padding: 28px 30px; margin: 28px 0; }
  .section-tint.tint-blue { background: #e6f1fb; }
  .section-tint.tint-blue .subhead { color: #0c447c; }
  .section-tint.tint-green { background: #eaf3de; }
  .section-tint.tint-green .subhead { color: #27500a; }
  .section-tint.tint-amber { background: #faeeda; }
  .section-tint.tint-amber .subhead { color: #854f0b; }
  .section-tint .card { background: rgba(255,255,255,0.7); }
  .card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
  .card h3 { font-size: 1.02rem; margin-bottom: 9px; }
  .card p { font-size: 0.92rem; margin: 0; }
  table.def-table {
    width: 100%; border-collapse: separate; border-spacing: 0; margin: 14px 0 28px;
    font-size: 0.92rem; border: 1px solid var(--border); border-radius: 12px;
    overflow: hidden; box-shadow: var(--shadow-sm);
  }
  table.def-table th, table.def-table td { text-align: left; padding: 14px 18px; vertical-align: top; }
  table.def-table th {
    font-family: "Space Grotesk", sans-serif; font-size: 0.78rem; text-transform: uppercase;
    letter-spacing: 0.06em; font-weight: 700; color: #fff;
    background: linear-gradient(90deg, var(--hal), var(--middleware));
    border-bottom: none;
  }
  table.def-table th:first-child { border-top-left-radius: 12px; }
  table.def-table th:last-child { border-top-right-radius: 12px; }
  table.def-table tbody tr { border-bottom: 1px solid var(--border); }
  table.def-table tbody tr:last-child { border-bottom: none; }
  table.def-table tbody tr:nth-child(odd) { background: #fbfcff; }
  table.def-table tbody tr:nth-child(even) { background: #fff; }
  table.def-table tbody tr:hover { background: var(--cloud-bg); }
  table.def-table td { color: var(--muted); line-height: 1.65; border-right: 1px solid var(--border); }
  table.def-table td:last-child { border-right: none; }
  table.def-table td:first-child {
    color: var(--ink); font-weight: 700; font-family: "Space Grotesk", sans-serif;
    font-size: 0.94rem; border-left: 3px solid var(--rdk-blue); background: rgba(41,182,232,0.04);
    width: 26%; min-width: 200px;
  }
  table.def-table td.mono { color: var(--ink); font-weight: 600; }

  /* ---- governance process sections (§7.2 / §7.3 narrative content) ---- */
  .gov-section.level-2 { padding-top: 22px; margin-top: 22px; border-top: 1px solid var(--border); }
  .gov-section.level-2:first-child { border-top: none; padding-top: 0; margin-top: 0; }
  .gov-section h3, .gov-section h4, .gov-section h5 {
    display: flex; align-items: baseline; gap: 10px; font-family: "Space Grotesk", sans-serif;
  }
  .gov-section h3 { font-size: 1.12rem; }
  .gov-section h4 { font-size: 1.0rem; margin-top: 14px; }
  .gov-section h5 { font-size: 0.92rem; color: var(--muted); margin-top: 10px; }
  .gov-num {
    font-family: "JetBrains Mono", monospace; font-size: 0.72rem; font-weight: 700;
    color: #fff; background: var(--middleware); padding: 2px 8px; border-radius: 5px;
    flex-shrink: 0; white-space: nowrap;
  }
  .gov-section p { margin: 6px 0 10px; font-size: 0.92rem; }
  .gov-section ul { margin: 6px 0 16px; padding-left: 20px; color: var(--muted); }
  .gov-section ul li { margin-bottom: 5px; line-height: 1.6; font-size: 0.92rem; }
  .gov-section table.def-table { margin: 10px 0 18px; font-size: 0.86rem; }
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

  /* ---- floating search chatbox (site-wide, every page) ---- */
  .chatbox-toggle {
    position: fixed; bottom: 22px; right: 22px; z-index: 90;
    width: 52px; height: 52px; border-radius: 50%; border: none; cursor: pointer;
    background: linear-gradient(135deg, var(--rdk-blue), #7c3aed); color: #fff;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 6px 20px rgba(26,86,219,0.4);
  }
  .chatbox-toggle svg { width: 24px; height: 24px; }
  .chatbox-panel {
    position: fixed; bottom: 84px; right: 22px; z-index: 90;
    width: 360px; max-width: calc(100vw - 44px); height: 480px; max-height: calc(100vh - 130px);
    background: #fff; border-radius: 16px; box-shadow: var(--shadow-md), 0 12px 40px rgba(0,0,0,0.18);
    display: none; flex-direction: column; overflow: hidden; border: 1px solid var(--border);
  }
  .chatbox-panel.open { display: flex; }
  .chatbox-header {
    background: var(--bedrock); color: #fff; padding: 14px 16px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .chatbox-header .title { font-family: "Space Grotesk", sans-serif; font-weight: 600; font-size: 0.9rem; }
  .chatbox-header .subtitle { font-size: 0.72rem; color: #9fb2cf; margin-top: 2px; }
  .chatbox-close { background: none; border: none; color: #9fb2cf; cursor: pointer; font-size: 1.1rem; line-height: 1; padding: 4px; }
  .chatbox-body { flex: 1; overflow-y: auto; padding: 14px 16px; background: #f8fafc; }
  .chatbox-welcome { font-size: 0.8rem; color: var(--muted); line-height: 1.5; }
  .chatbox-answer { background: #fff; border: 1px solid var(--border); border-left: 3px solid var(--middleware); border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; }
  .chatbox-answer .cb-cat { font-family: "JetBrains Mono", monospace; font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--middleware); font-weight: 600; }
  .chatbox-answer .cb-title { font-weight: 600; font-size: 0.86rem; margin: 3px 0 5px; }
  .chatbox-answer .cb-text { font-size: 0.8rem; color: var(--muted); line-height: 1.5; }
  .chatbox-related { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin: 12px 0 6px; }
  .chatbox-result { display: block; background: #fff; border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px; margin-bottom: 6px; text-decoration: none; }
  .chatbox-result .cb-r-title { font-size: 0.8rem; font-weight: 600; color: var(--ink); }
  .chatbox-result .cb-r-cat { font-size: 0.7rem; color: var(--muted); }
  .chatbox-form { display: flex; gap: 8px; padding: 12px; border-top: 1px solid var(--border); background: #fff; }
  .chatbox-input { flex: 1; border: 1px solid var(--border); border-radius: 8px; padding: 9px 12px; font-size: 0.82rem; font-family: inherit; }
  .chatbox-submit { background: var(--middleware); color: #fff; border: none; border-radius: 8px; padding: 0 14px; font-size: 0.82rem; font-weight: 600; cursor: pointer; }

  /* ---- floating contact widget (site-wide, mirrors the search chatbox) ---- */
  .contact-toggle {
    position: fixed; bottom: 22px; left: 22px; z-index: 90;
    width: 52px; height: 52px; border-radius: 50%; border: none; cursor: pointer;
    background: linear-gradient(135deg, var(--mgmt), var(--rdk-blue)); color: #fff;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 6px 20px rgba(14,159,110,0.4);
  }
  .contact-toggle svg { width: 22px; height: 22px; }
  .contact-panel {
    position: fixed; bottom: 84px; left: 22px; z-index: 90;
    width: 340px; max-width: calc(100vw - 44px);
    background: #fff; border-radius: 16px; box-shadow: var(--shadow-md), 0 12px 40px rgba(0,0,0,0.18);
    display: none; flex-direction: column; overflow: hidden; border: 1px solid var(--border);
  }
  .contact-panel.open { display: flex; }
  .contact-header { background: var(--bedrock); color: #fff; padding: 14px 16px; display: flex; align-items: center; justify-content: space-between; }
  .contact-header .title { font-family: "Space Grotesk", sans-serif; font-weight: 600; font-size: 0.9rem; }
  .contact-header .subtitle { font-size: 0.72rem; color: #9fb2cf; margin-top: 2px; }
  .contact-close { background: none; border: none; color: #9fb2cf; cursor: pointer; font-size: 1.1rem; line-height: 1; padding: 4px; }
  .contact-body { padding: 16px; }
  .contact-field { margin-bottom: 12px; }
  .contact-field label { display: block; font-size: 0.76rem; font-weight: 600; color: var(--ink); margin-bottom: 4px; }
  .contact-field input, .contact-field textarea {
    width: 100%; border: 1px solid var(--border); border-radius: 8px; padding: 9px 11px;
    font-size: 0.84rem; font-family: inherit; resize: vertical;
  }
  .contact-submit {
    width: 100%; background: var(--mgmt); color: #fff; border: none; border-radius: 8px;
    padding: 10px; font-size: 0.86rem; font-weight: 600; cursor: pointer; margin-top: 4px;
  }
  .contact-submit:disabled { opacity: 0.6; cursor: default; }
  .contact-status { font-size: 0.78rem; margin-top: 10px; text-align: center; }
  .contact-status.ok { color: #0aa66e; }
  .contact-status.err { color: #b91c1c; }
  .contact-mailto { display: block; text-align: center; font-size: 0.76rem; color: var(--muted); margin-top: 10px; }
"""


# Small inline-SVG line icons for the quick-link card row. Hand-drawn rather
# than a webfont — the Visualizer sandbox's Tabler Icons aren't available in
# the actual deployed static site, and this avoids adding an external CDN
# dependency just for a handful of glyphs.
ICONS = {
    "recycle": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 19H4.815a1.83 1.83 0 0 1-1.57-.881 1.785 1.785 0 0 1-.004-1.784L7.196 9.5"/><path d="M11 19h8.203a1.83 1.83 0 0 0 1.556-.89 1.784 1.784 0 0 0 0-1.775l-1.226-2.12"/><path d="M14.5 4.5 12 9l-2.5-4.5"/><path d="M16.5 14.5 19 19l-2.5 4.5" opacity="0"/></svg>',
    "shield-check": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v6c0 4.5-3 8-7 9-4-1-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/></svg>',
    "cloud-up": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 18a4 4 0 0 1-.6-7.95A5 5 0 0 1 16.2 8.9 4.5 4.5 0 0 1 16 18H7z"/><path d="M12 17v-6"/><path d="M9.5 13.5 12 11l2.5 2.5"/></svg>',
    "cpu": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="6" width="12" height="12" rx="1.5"/><path d="M9 3v3M15 3v3M9 18v3M15 18v3M3 9h3M3 15h3M18 9h3M18 15h3"/></svg>',
    "layers": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 3 8l9 5 9-5-9-5z"/><path d="M3 13l9 5 9-5"/></svg>',
    "check-list": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 6h14M5 12h14M5 18h9"/><path d="M3 6l.01 0M3 12l.01 0M3 18l.01 0"/></svg>',
}


def esc(s) -> str:
    return html.escape("" if s is None else str(s))


# ---- Hero images ----
# No illustrations or photography are shipped by default (removed for legal
# safety). To add a real, approved image to a page's hero later: drop the
# image file in the repo (e.g. images/about-hero.png) and add one line to
# HERO_IMAGES below mapping that page's id to the file's path. Nothing else
# needs to change — render_hero() picks it up automatically, and pages
# without an entry simply render without a hero image, exactly as now.
HERO_IMAGES: dict[str, str] = {
    # "about": "images/about-hero.png",
    # "architecture-standards": "images/architecture-standards-hero.png",
    # "technical-governance": "images/technical-governance-hero.png",
    # "nbi": "images/nbi-hero.png",
    # "sbi": "images/sbi-hero.png",
    # "hwcompat": "images/hwcompat-hero.png",
}


def render_hero(eyebrow: str, title: str, lede: str, badges_html: str = "", compact: bool = False, visual_key: str = "about") -> str:
    """Shared hero markup: eyebrow, heading, lede paragraph, optional badge
    row, and — only if one is registered in HERO_IMAGES for this page — an
    image on wide screens. Used by every page so any future hero image
    change applies everywhere consistently.
    title/lede are escaped here — pass plain text, not pre-escaped HTML."""
    pad = "48px 40px 40px" if compact else "64px 40px 48px"
    title_style = ' style="font-size:2rem;"' if compact else ""
    badges = f'<div class="badge-row">{badges_html}</div>' if badges_html else ""
    image_path = HERO_IMAGES.get(visual_key)
    visual = f'<div class="hero-visual"><img src="{esc(image_path)}" alt=""></div>' if image_path else ""
    return f'''
<div class="hero" style="padding:{pad};">
  <div class="hero-flex">
    <div class="hero-inner">
      <span class="eyebrow">{esc(eyebrow)}</span>
      <h1{title_style}>{esc(title)}</h1>
      <p class="lede">{esc(lede)}</p>
      {badges}
    </div>
    {visual}
  </div>
</div>
'''


def render_quicklinks(items: list[dict]) -> str:
    """A horizontal row of colorful teaser cards — icon, short title, an
    "Explore" link. Each item: {icon, title, href, color}. `href` can be a
    same-page anchor (e.g. "#goal-reuse") to jump further down the page
    rather than navigating away."""
    cards = []
    for it in items:
        icon_svg = ICONS.get(it["icon"], "")
        cards.append(f'''
    <a class="quicklink-card" href="{esc(it["href"])}" style="--ql-color:{esc(it["color"])};">
      <span class="ql-icon">{icon_svg}</span>
      <div class="ql-title">{esc(it["title"])}</div>
      <div class="ql-cta">Explore &rarr;</div>
    </a>''')
    return f'<div class="quicklink-row">{"".join(cards)}</div>'


def render_topnav(active_id: str) -> str:
    links_html = []
    for id_, label, href, external in NAV_LINKS:
        if id_ == "components":
            continue  # rendered separately as the CTA button, not a plain nav link
        cls = "active" if id_ == active_id else ""
        links_html.append(f'<a class="{cls}" href="{esc(href)}">{esc(label)}</a>')
    return f'''<div class="topnav">
  <div class="brand">
    <img src="RDK-logo.png" alt="RDK-B Core Broadband logo" onerror="this.style.display='none'">
  </div>
  <nav>
    {"".join(links_html)}
  </nav>
  <a class="cta" href="{esc(COMPONENTS_URL)}">Core RDK Components ↗</a>
</div>'''


CHATBOX_HTML = """
<button class="chatbox-toggle" id="chatbox-toggle" aria-label="Search the site">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.5 8.5 0 0 1-11.9 7.8L3 21l1.7-6.1A8.5 8.5 0 1 1 21 11.5z"/></svg>
</button>
<div class="chatbox-panel" id="chatbox-panel">
  <div class="chatbox-header">
    <div>
      <div class="title">Search RDK-B Core Broadband</div>
      <div class="subtitle">Keyword search across this site — not an AI, just a fast index</div>
    </div>
    <button class="chatbox-close" id="chatbox-close" aria-label="Close">&times;</button>
  </div>
  <div class="chatbox-body" id="chatbox-body">
    <div class="chatbox-welcome">Try: "WAN Manager", "RBUS", "TR-181", "boot chain", "modularity"...</div>
  </div>
  <form class="chatbox-form" id="chatbox-form">
    <input class="chatbox-input" id="chatbox-input" type="text" placeholder="Ask a question…" autocomplete="off">
    <button class="chatbox-submit" type="submit">Search</button>
  </form>
</div>
"""

CHATBOX_SCRIPT = """
<script>
(function() {
  let searchDocs = null;

  function esc(s) {
    const d = document.createElement('div');
    d.textContent = s ?? '';
    return d.innerHTML;
  }

  function score(doc, terms) {
    const title = doc.title.toLowerCase();
    const text = doc.text.toLowerCase();
    let s = 0;
    for (const t of terms) {
      if (title.includes(t)) s += 10;
      if (text.includes(t)) s += 2;
    }
    return s;
  }

  function runSearch(query) {
    const body = document.getElementById('chatbox-body');
    const terms = query.toLowerCase().split(/\\s+/).filter(Boolean);
    if (!terms.length) return;

    if (!searchDocs) {
      body.innerHTML = '<div class="chatbox-welcome">Loading search index…</div>';
      fetch('search-index.json', { cache: 'no-store' })
        .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
        .then(data => { searchDocs = data.docs; renderResults(query, terms); })
        .catch(err => { body.innerHTML = '<div class="chatbox-welcome">Could not load the search index (' + esc(err.message) + ').</div>'; });
      return;
    }
    renderResults(query, terms);
  }

  function renderResults(query, terms) {
    const body = document.getElementById('chatbox-body');
    const scored = searchDocs
      .map(doc => ({ doc, s: score(doc, terms) }))
      .filter(x => x.s > 0)
      .sort((a, b) => b.s - a.s);

    if (!scored.length) {
      body.innerHTML = '<div class="chatbox-welcome">No matches for "' + esc(query) + '". Try a different term — component names, standard names, or words like "modularity" or "RBUS" work well.</div>';
      return;
    }

    const best = scored[0].doc;
    const rest = scored.slice(1, 6);

    let html = '<div class="chatbox-answer">' +
      '<div class="cb-cat">' + esc(best.category) + '</div>' +
      '<div class="cb-title">' + esc(best.title) + '</div>' +
      '<div class="cb-text">' + esc(best.text) + '</div>' +
      '</div>';

    if (rest.length) {
      html += '<div class="chatbox-related">Related</div>';
      html += rest.map(x => {
        const href = x.doc.url.endsWith('#') ? x.doc.url.slice(0, -1) || '#' : x.doc.url;
        return '<a class="chatbox-result" href="' + esc(href) + '">' +
          '<div class="cb-r-title">' + esc(x.doc.title) + '</div>' +
          '<div class="cb-r-cat">' + esc(x.doc.category) + '</div>' +
          '</a>';
      }).join('');
    }
    body.innerHTML = html;
  }

  const toggle = document.getElementById('chatbox-toggle');
  const panel = document.getElementById('chatbox-panel');
  const closeBtn = document.getElementById('chatbox-close');
  const form = document.getElementById('chatbox-form');
  const input = document.getElementById('chatbox-input');

  toggle.addEventListener('click', () => { panel.classList.toggle('open'); if (panel.classList.contains('open')) input.focus(); });
  closeBtn.addEventListener('click', () => panel.classList.remove('open'));
  form.addEventListener('submit', (e) => { e.preventDefault(); if (input.value.trim()) runSearch(input.value.trim()); });
})();
</script>
"""

# support@rdkcentral.com receives every submission. FormSubmit.co needs no
# signup/API key — the first real submission triggers a one-time
# confirmation email asking you to click "Activate Form"; every submission
# after that lands straight in the inbox. Sent via their /ajax/ endpoint so
# the page never redirects away — the result renders in this same panel.
CONTACT_EMAIL = "chandrakanth_pokuru2@comcast.com"

CONTACT_HTML = f"""
<button class="contact-toggle" id="contact-toggle" aria-label="Contact us">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16v16H4z" opacity="0"/><path d="M3 6l9 6 9-6"/><rect x="3" y="5" width="18" height="14" rx="2"/></svg>
</button>
<div class="contact-panel" id="contact-panel">
  <div class="contact-header">
    <div>
      <div class="title">Contact us</div>
      <div class="subtitle">Send a message — we'll get it by email</div>
    </div>
    <button class="contact-close" id="contact-close" aria-label="Close">&times;</button>
  </div>
  <div class="contact-body">
    <form id="contact-form">
      <div class="contact-field">
        <label for="contact-name">Name</label>
        <input id="contact-name" name="name" type="text" required>
      </div>
      <div class="contact-field">
        <label for="contact-email">Your email</label>
        <input id="contact-email" name="email" type="email" required>
      </div>
      <div class="contact-field">
        <label for="contact-message">Message</label>
        <textarea id="contact-message" name="message" rows="4" required></textarea>
      </div>
      <button class="contact-submit" id="contact-submit" type="submit">Send</button>
      <div class="contact-status" id="contact-status"></div>
    </form>
    <a class="contact-mailto" href="mailto:{CONTACT_EMAIL}">Or email {CONTACT_EMAIL} directly</a>
  </div>
</div>
"""

CONTACT_SCRIPT = f"""
<script>
(function() {{
  const toggle = document.getElementById('contact-toggle');
  const panel = document.getElementById('contact-panel');
  const closeBtn = document.getElementById('contact-close');
  const form = document.getElementById('contact-form');
  const submitBtn = document.getElementById('contact-submit');
  const status = document.getElementById('contact-status');

  toggle.addEventListener('click', () => {{
    panel.classList.toggle('open');
    if (panel.classList.contains('open')) document.getElementById('contact-name').focus();
  }});
  closeBtn.addEventListener('click', () => panel.classList.remove('open'));

  form.addEventListener('submit', function(e) {{
    e.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = 'Sending…';
    status.textContent = '';
    status.className = 'contact-status';

    const payload = {{
      name: document.getElementById('contact-name').value,
      email: document.getElementById('contact-email').value,
      message: document.getElementById('contact-message').value,
      _subject: 'New message from RDK-B Core Broadband site',
    }};

    fetch('https://formsubmit.co/ajax/{CONTACT_EMAIL}', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'Accept': 'application/json' }},
      body: JSON.stringify(payload),
    }})
      .then(res => {{ if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); }})
      .then(() => {{
        status.textContent = 'Sent — thanks! We\\'ll get back to you.';
        status.className = 'contact-status ok';
        form.reset();
      }})
      .catch(err => {{
        status.textContent = 'Could not send (' + err.message + '). Try the email link below instead.';
        status.className = 'contact-status err';
      }})
      .finally(() => {{
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send';
      }});
  }});
}})();
</script>
"""


def render_page(active_id: str, head_extra: str, body_html: str, script: str = "") -> str:
    """Wrap body_html (hero + sections + footer, everything but <head>/sidebar)
    in the shared shell. body_html should NOT include <html>/<head>/<body> tags.
    Pass any <script> block via `script`, not inside head_extra — head_extra
    renders inside <head>, before the body (and the elements a script needs
    to attach to) exists yet. `script` renders at the very end of <body>,
    after body_html, so document.getElementById(...) etc. always find real
    elements instead of null."""
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
{render_topnav(active_id)}
<div class="page-main">
{body_html}
</div>
{CHATBOX_HTML}
{CONTACT_HTML}
{script}
{CHATBOX_SCRIPT}
{CONTACT_SCRIPT}
</body>
</html>
'''
