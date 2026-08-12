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
  .hero-visual img { max-width: 100%; max-height: 320px; width: auto; height: auto; border-radius: 14px; object-fit: contain; }
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
