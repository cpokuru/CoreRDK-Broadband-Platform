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
    --bedrock: #0b1220; --hal: #1c3a5e; --middleware: #1a56db; --mgmt: #0e9f6e;
    --cloud-bg: #eef2ff; --cloud-fg: #3730a3; --ink: #0f172a; --muted: #5b6472;
    --page-bg: #f8fafc; --card-bg: #ffffff; --border: #e2e8f0;
    --amber-fg: #b45309; --amber-bg: #fef3c7;
    --sidebar-w: 264px;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body { margin: 0; font-family: "Inter", -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: var(--ink); background: var(--page-bg); line-height: 1.55; }
  code, .mono { font-family: "JetBrains Mono", ui-monospace, monospace; }
  a { color: var(--middleware); }
  h1, h2, h3 { font-weight: 800; letter-spacing: -0.01em; margin: 0; }
  p { margin: 0 0 12px; color: var(--muted); }

  /* ---- sidebar ---- */
  .sidebar {
    position: fixed; top: 0; left: 0; bottom: 0; width: var(--sidebar-w);
    background: linear-gradient(180deg, #0b1220 0%, #101c33 100%);
    color: #fff; overflow-y: auto; z-index: 50;
    padding: 22px 0 24px;
  }
  .sidebar .brand { padding: 0 22px 20px; font-weight: 700; font-size: 0.98rem; letter-spacing: -0.01em; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 12px; }
  .sidebar .brand .mono { display: block; color: #8fb3ff; font-size: 0.74rem; font-weight: 600; margin-top: 2px; }
  .sidebar nav { display: flex; flex-direction: column; padding: 4px 12px; gap: 2px; }
  .sidebar nav a {
    display: flex; align-items: center; justify-content: space-between;
    color: #cbd5e1; text-decoration: none; font-size: 0.88rem; font-weight: 500;
    padding: 9px 12px; border-radius: 8px;
  }
  .sidebar nav a:hover { color: #fff; background: rgba(255,255,255,0.06); }
  .sidebar nav a.active { color: #fff; background: rgba(26,86,219,0.35); font-weight: 600; }
  .sidebar nav a .ext-arrow { font-size: 0.78em; color: #8fb3ff; }
  .sidebar .nav-group-label {
    font-family: "JetBrains Mono", monospace; font-size: 0.66rem; letter-spacing: 0.08em;
    text-transform: uppercase; color: #5f7292; padding: 16px 22px 6px;
  }

  /* ---- main content area ---- */
  .page-main { margin-left: var(--sidebar-w); min-height: 100vh; }

  @media (max-width: 860px) {
    :root { --sidebar-w: 0px; }
    .sidebar { position: static; width: 100%; padding: 16px 0; }
    .sidebar .brand { padding: 0 18px 14px; }
    .sidebar nav { flex-direction: row; flex-wrap: wrap; padding: 0 12px; }
    .sidebar nav a { padding: 7px 11px; font-size: 0.82rem; }
    .page-main { margin-left: 0; }
  }

  /* ---- hero ---- */
  .hero { background: linear-gradient(180deg, #0b1220 0%, #101c33 100%); color: #fff; padding: 64px 40px 48px; }
  .hero-inner { max-width: 900px; }
  .eyebrow { display: inline-block; font-family: "JetBrains Mono", monospace; font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: #8fb3ff; border: 1px solid rgba(143,179,255,0.35); border-radius: 999px; padding: 4px 12px; margin-bottom: 18px; }
  .hero h1 { font-size: 2.3rem; color: #fff; max-width: 760px; }
  .hero .lede { color: #b6c2d9; font-size: 1.05rem; max-width: 640px; margin-top: 14px; }
  .badge-row { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 26px; }
  .badge { display: inline-block; margin: 0 10px 10px 0; font-size: 0.8rem; font-weight: 600; padding: 6px 12px; border-radius: 999px; background: rgba(255,255,255,0.08); color: #dbe4f3; border: 1px solid rgba(255,255,255,0.12); }
  .stats { max-width: 900px; margin: -30px 40px 0; padding: 0; display: flex; gap: 1px; background: var(--border); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; position: relative; z-index: 2; }
  .stat { flex: 1; min-width: 0; background: #fff; padding: 20px 16px; text-align: center; }
  .stat .num { font-size: 1.5rem; font-weight: 800; color: var(--middleware); }
  .stat .lbl { font-size: 0.74rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 2px; }
  @media (max-width: 760px) { .stats { flex-wrap: wrap; margin: -20px 16px 0; } .stat { flex: 1 1 40%; } .hero { padding: 48px 20px 40px; } }

  /* ---- sections ---- */
  section { max-width: 900px; margin: 0 auto; padding: 56px 40px; }
  section.tight-top { padding-top: 48px; }
  @media (max-width: 760px) { section { padding: 40px 20px; } }
  .section-head { margin-bottom: 32px; }
  .section-head .eyebrow-lt { font-family: "JetBrains Mono", monospace; font-size: 0.74rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--middleware); font-weight: 600; margin-bottom: 8px; display: block; }
  .section-head h2 { font-size: 1.8rem; }
  .section-head p { margin-top: 10px; font-size: 1.02rem; max-width: 680px; }
  .callout { background: #eef2ff; border: 1px solid #c7d5fb; border-radius: 12px; padding: 20px 24px; margin: 18px 0; }
  .callout strong { color: var(--ink); display: block; margin-bottom: 4px; font-size: 0.95rem; }
  .callout p { margin: 0; font-size: 0.95rem; }
  .two-col { display: flex; gap: 28px; }
  .two-col > * { flex: 1; min-width: 0; }
  @media (max-width: 760px) { .two-col { flex-direction: column; } }
  .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px 22px; }
  .card h3 { font-size: 1rem; margin-bottom: 8px; }
  .card p { font-size: 0.92rem; margin: 0; }
  table.def-table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 0.9rem; }
  table.def-table th, table.def-table td { text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
  table.def-table th { background: #f1f5f9; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }
  table.def-table td.mono { color: var(--ink); font-weight: 600; }
  .timeline { border-left: 2px solid var(--border); margin-left: 6px; padding-left: 24px; display: flex; flex-direction: column; gap: 18px; }
  .tl-item { position: relative; }
  .tl-item::before { content: ""; position: absolute; left: -29px; top: 4px; width: 10px; height: 10px; border-radius: 50%; background: var(--middleware); border: 2px solid #fff; box-shadow: 0 0 0 2px var(--middleware); }
  .tl-year { font-family: "JetBrains Mono", monospace; font-weight: 700; color: var(--middleware); font-size: 0.86rem; }
  .tl-item p { margin: 2px 0 0; font-size: 0.92rem; }
  .tier-diagram { border-radius: 14px; overflow: hidden; border: 1px solid var(--border); box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
  .tier { display: flex; align-items: stretch; border-bottom: 1px solid rgba(255,255,255,0.12); }
  .tier:last-child { border-bottom: none; }
  .tier .num { flex: 0 0 64px; display: flex; align-items: center; justify-content: center; font-family: "JetBrains Mono", monospace; font-weight: 700; font-size: 1.1rem; }
  .tier .body { flex: 1; padding: 18px 22px; }
  .tier .body h4 { margin: 0 0 4px; font-size: 1rem; font-weight: 700; }
  .tier .body p { margin: 0; font-size: 0.88rem; }
  .tier.t5 { background: var(--cloud-bg); color: var(--cloud-fg); }
  .tier.t5 .num { background: #d9e2ff; color: var(--cloud-fg); }
  .tier.t4 { background: #e3f7ef; color: #065f46; }
  .tier.t4 .num { background: var(--mgmt); color: #fff; }
  .tier.t3 { background: var(--middleware); color: #fff; }
  .tier.t3 .num { background: #1442ad; color: #fff; }
  .tier.t3 .body p { color: #dce6ff; }
  .tier.t2 { background: var(--hal); color: #fff; }
  .tier.t2 .num { background: #142b47; color: #fff; }
  .tier.t2 .body p { color: #c5d3e6; }
  .tier.t1 { background: var(--bedrock); color: #fff; }
  .tier.t1 .num { background: #05070d; color: #9fb2cf; }
  .tier.t1 .body p { color: #9fb2cf; }
  .tier-caption { text-align: center; font-size: 0.82rem; color: var(--muted); margin-top: 10px; }
  .layer-stack { display: flex; flex-direction: column; gap: 6px; }
  .layer-box { margin-bottom: 6px; border-radius: 8px; padding: 12px 16px; font-size: 0.86rem; font-weight: 600; text-align: center; }
  .layer-box:last-child { margin-bottom: 0; }
  .layer-box.top { background: var(--middleware); color: #fff; }
  .layer-box.mid { background: var(--hal); color: #fff; }
  .layer-box.bot { background: #e2e8f0; color: var(--ink); }
  .subhead { font-size: 1.15rem; font-weight: 700; margin: 34px 0 12px; }
  .subhead:first-of-type { margin-top: 8px; }
  footer { background: var(--bedrock); color: #9fb2cf; padding: 40px 40px 28px; }
  .footer-links { display: flex; flex-wrap: wrap; gap: 28px; margin-bottom: 22px; max-width: 900px; }
  .footer-links a { display: block; min-width: 200px; margin: 0 28px 14px 0; color: #dbe4f3; text-decoration: none; font-size: 0.9rem; font-weight: 600; }
  .footer-links a span { display: block; font-weight: 400; color: #8493ab; font-size: 0.8rem; margin-top: 2px; }
  .footer-meta { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 18px; font-size: 0.78rem; color: #7386a3; max-width: 900px; }
  .pill-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
  .pill { display: inline-block; margin: 0 8px 8px 0; font-size: 0.78rem; font-weight: 600; padding: 4px 10px; border-radius: 999px; background: #f1f5f9; color: var(--ink); border: 1px solid var(--border); }

  /* ---- empty-state (for the not-yet-populated API/HW pages) ---- */
  .empty-state { max-width: 560px; margin: 40px auto; text-align: center; padding: 48px 32px; background: #fff; border: 1px dashed var(--border); border-radius: 14px; }
  .empty-state .icon { font-size: 2rem; margin-bottom: 12px; }
  .empty-state h3 { font-size: 1.1rem; margin-bottom: 8px; }
  .empty-state p { font-size: 0.92rem; }
  .empty-state code { display: inline-block; background: #f1f5f9; padding: 2px 8px; border-radius: 5px; margin-top: 4px; }
"""


def esc(s) -> str:
    return html.escape("" if s is None else str(s))


def render_sidebar(active_id: str) -> str:
    links_html = []
    for id_, label, href, external in NAV_LINKS:
        cls = "active" if id_ == active_id else ""
        arrow = '<span class="ext-arrow">↗</span>' if external else ""
        links_html.append(f'<a class="{cls}" href="{esc(href)}">{esc(label)}{arrow}</a>')
    return f'''<div class="sidebar">
  <div class="brand">RDK-B Core Broadband<span class="mono">// specification</span></div>
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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{SHARED_CSS}</style>
{head_extra}
</head>
<body>
{render_sidebar(active_id)}
<div class="page-main">
{body_html}
</div>
</body>
</html>
'''
