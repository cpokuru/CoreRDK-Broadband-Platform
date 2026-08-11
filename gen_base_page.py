"""Render CoreRDK-Broadband-Docs-Base's index.html from spec-content.json
(the output of extract_spec_content.py).

Usage:
    python3 gen_base_page.py spec-content.json --out index.html
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

COMPONENTS_URL = "components/"
COMPONENTS_FULL_URL = "components/full-list.html"
SPEC_WIKI_URL = "https://wiki.rdkcentral.com/spaces/RDK/pages/498925914/RDK9+Core+RDK+Broadband+Specification+Approved+by+TAB"


def esc(s) -> str:
    return html.escape("" if s is None else str(s))


def render_timeline(items: list[dict]) -> str:
    out = []
    for it in items:
        out.append(f'''<div class="tl-item"><span class="tl-year">{esc(it["year"])}</span><p>{esc(it["text"])}.</p></div>''')
    return "\n".join(out)


def render_licensing(items: list[str]) -> str:
    return "\n".join(f'<span class="pill">{esc(x)}</span>' for x in items)


def render_five_tier(tiers: list[dict]) -> str:
    out = []
    for t in sorted(tiers, key=lambda x: -x["tier"]):
        out.append(f'''
    <div class="tier t{t["tier"]}">
      <div class="num">{t["tier"]}</div>
      <div class="body">
        <h4>{esc(t["layer"])}</h4>
        <p>{esc(t["description"])}</p>
      </div>
    </div>''')
    return "\n".join(out)


def render_test_suites(rows: list[dict]) -> str:
    out = []
    for r in rows:
        out.append(f'<tr><td class="mono">{esc(r["name"])}</td><td>{esc(r["definition"])}</td><td>{esc(r["owner"])}</td></tr>')
    return "\n".join(out)


def render_governance(rows: list[dict]) -> str:
    out = []
    for r in rows:
        out.append(f'<tr><td class="mono">{esc(r["name"])}</td><td>{esc(r["requirement"])}</td></tr>')
    return "\n".join(out)


def render_industry(rows: list[dict]) -> str:
    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(r["category"] or "Other", []).append(r)
    out = []
    for cat, items in groups.items():
        out.append(f'<div class="subhead">{esc(cat)}</div>')
        out.append('<table class="def-table"><thead><tr><th>Standard / body</th><th>Applies to</th><th>Note</th></tr></thead><tbody>')
        for it in items:
            out.append(f'<tr><td class="mono">{esc(it["standard"])}</td><td>{esc(it["applies_to"])}</td><td>{esc(it["note"])}</td></tr>')
        out.append('</tbody></table>')
    return "\n".join(out)


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RDK-B Core Broadband Platform</title>
<meta name="description" content="RDK-B Core Broadband Platform — overview, five-tier architecture, and architecture standards.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bedrock: #0b1220; --hal: #1c3a5e; --middleware: #1a56db; --mgmt: #0e9f6e;
    --cloud-bg: #eef2ff; --cloud-fg: #3730a3; --ink: #0f172a; --muted: #5b6472;
    --page-bg: #f8fafc; --card-bg: #ffffff; --border: #e2e8f0;
    --amber-fg: #b45309; --amber-bg: #fef3c7;
  }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{ margin: 0; font-family: "Inter", -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: var(--ink); background: var(--page-bg); line-height: 1.55; }}
  code, .mono {{ font-family: "JetBrains Mono", ui-monospace, monospace; }}
  a {{ color: var(--middleware); }}
  h1, h2, h3 {{ font-weight: 800; letter-spacing: -0.01em; margin: 0; }}
  p {{ margin: 0 0 12px; color: var(--muted); }}
  nav {{ position: sticky; top: 0; z-index: 50; background: rgba(11,18,32,0.95); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: space-between; padding: 14px 32px; border-bottom: 1px solid rgba(255,255,255,0.08); }}
  .brand {{ color: #fff; font-weight: 700; font-size: 0.98rem; letter-spacing: -0.01em; display: flex; align-items: center; gap: 8px; }}
  .brand .mono {{ color: #8fb3ff; font-size: 0.78rem; font-weight: 600; }}
  .navlinks a {{ color: #cbd5e1; text-decoration: none; font-size: 0.88rem; font-weight: 500; margin-left: 26px; }}
  .navlinks a:hover {{ color: #fff; }}
  .navlinks a.ext::after {{ content: " ↗"; font-size: 0.78em; }}
  .hero {{ background: linear-gradient(180deg, #0b1220 0%, #101c33 100%); color: #fff; padding: 72px 32px 56px; }}
  .hero-inner {{ max-width: 980px; margin: 0 auto; }}
  .eyebrow {{ display: inline-block; font-family: "JetBrains Mono", monospace; font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; color: #8fb3ff; border: 1px solid rgba(143,179,255,0.35); border-radius: 999px; padding: 4px 12px; margin-bottom: 18px; }}
  .hero h1 {{ font-size: 2.6rem; color: #fff; max-width: 760px; }}
  .hero .lede {{ color: #b6c2d9; font-size: 1.1rem; max-width: 640px; margin-top: 14px; }}
  .badge-row {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 26px; }}
  .badge {{ display: inline-block; margin: 0 10px 10px 0; font-size: 0.8rem; font-weight: 600; padding: 6px 12px; border-radius: 999px; background: rgba(255,255,255,0.08); color: #dbe4f3; border: 1px solid rgba(255,255,255,0.12); }}
  .stats {{ max-width: 980px; margin: -30px auto 0; padding: 0 32px; display: flex; gap: 1px; background: var(--border); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; position: relative; z-index: 2; }}
  .stat {{ flex: 1; min-width: 0; background: #fff; padding: 20px 16px; text-align: center; }}
  .stat .num {{ font-size: 1.5rem; font-weight: 800; color: var(--middleware); }}
  .stat .lbl {{ font-size: 0.74rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 2px; }}
  @media (max-width: 760px) {{ .stats {{ flex-wrap: wrap; }} .stat {{ flex: 1 1 40%; }} }}
  section {{ max-width: 980px; margin: 0 auto; padding: 72px 32px; }}
  section.tight-top {{ padding-top: 56px; }}
  .section-head {{ margin-bottom: 32px; }}
  .section-head .eyebrow-lt {{ font-family: "JetBrains Mono", monospace; font-size: 0.74rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--middleware); font-weight: 600; margin-bottom: 8px; display: block; }}
  .section-head h2 {{ font-size: 1.9rem; }}
  .section-head p {{ margin-top: 10px; font-size: 1.02rem; max-width: 680px; }}
  .callout {{ background: #eef2ff; border: 1px solid #c7d5fb; border-radius: 12px; padding: 20px 24px; margin: 18px 0; }}
  .callout strong {{ color: var(--ink); display: block; margin-bottom: 4px; font-size: 0.95rem; }}
  .callout p {{ margin: 0; font-size: 0.95rem; }}
  .two-col {{ display: flex; gap: 28px; }}
  .two-col > * {{ flex: 1; min-width: 0; }}
  @media (max-width: 760px) {{ .two-col {{ flex-direction: column; }} }}
  .card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px 22px; }}
  .card h3 {{ font-size: 1rem; margin-bottom: 8px; }}
  .card p {{ font-size: 0.92rem; margin: 0; }}
  table.def-table {{ width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 0.9rem; }}
  table.def-table th, table.def-table td {{ text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }}
  table.def-table th {{ background: #f1f5f9; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }}
  table.def-table td.mono {{ color: var(--ink); font-weight: 600; }}
  .timeline {{ border-left: 2px solid var(--border); margin-left: 6px; padding-left: 24px; display: flex; flex-direction: column; gap: 18px; }}
  .tl-item {{ position: relative; }}
  .tl-item::before {{ content: ""; position: absolute; left: -29px; top: 4px; width: 10px; height: 10px; border-radius: 50%; background: var(--middleware); border: 2px solid #fff; box-shadow: 0 0 0 2px var(--middleware); }}
  .tl-year {{ font-family: "JetBrains Mono", monospace; font-weight: 700; color: var(--middleware); font-size: 0.86rem; }}
  .tl-item p {{ margin: 2px 0 0; font-size: 0.92rem; }}
  .tier-diagram {{ border-radius: 14px; overflow: hidden; border: 1px solid var(--border); box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
  .tier {{ display: flex; align-items: stretch; border-bottom: 1px solid rgba(255,255,255,0.12); }}
  .tier:last-child {{ border-bottom: none; }}
  .tier .num {{ flex: 0 0 64px; display: flex; align-items: center; justify-content: center; font-family: "JetBrains Mono", monospace; font-weight: 700; font-size: 1.1rem; }}
  .tier .body {{ flex: 1; padding: 18px 22px; }}
  .tier .body h4 {{ margin: 0 0 4px; font-size: 1rem; font-weight: 700; }}
  .tier .body p {{ margin: 0; font-size: 0.88rem; }}
  .tier.t5 {{ background: var(--cloud-bg); color: var(--cloud-fg); }}
  .tier.t5 .num {{ background: #d9e2ff; color: var(--cloud-fg); }}
  .tier.t4 {{ background: #e3f7ef; color: #065f46; }}
  .tier.t4 .num {{ background: var(--mgmt); color: #fff; }}
  .tier.t3 {{ background: var(--middleware); color: #fff; }}
  .tier.t3 .num {{ background: #1442ad; color: #fff; }}
  .tier.t3 .body p {{ color: #dce6ff; }}
  .tier.t2 {{ background: var(--hal); color: #fff; }}
  .tier.t2 .num {{ background: #142b47; color: #fff; }}
  .tier.t2 .body p {{ color: #c5d3e6; }}
  .tier.t1 {{ background: var(--bedrock); color: #fff; }}
  .tier.t1 .num {{ background: #05070d; color: #9fb2cf; }}
  .tier.t1 .body p {{ color: #9fb2cf; }}
  .tier-caption {{ text-align: center; font-size: 0.82rem; color: var(--muted); margin-top: 10px; }}
  .layer-stack {{ display: flex; flex-direction: column; gap: 6px; }}
  .layer-box {{ margin-bottom: 6px; border-radius: 8px; padding: 12px 16px; font-size: 0.86rem; font-weight: 600; text-align: center; }}
  .layer-box:last-child {{ margin-bottom: 0; }}
  .layer-box.top {{ background: var(--middleware); color: #fff; }}
  .layer-box.mid {{ background: var(--hal); color: #fff; }}
  .layer-box.bot {{ background: #e2e8f0; color: var(--ink); }}
  .subhead {{ font-size: 1.15rem; font-weight: 700; margin: 34px 0 12px; }}
  .subhead:first-of-type {{ margin-top: 8px; }}
  footer {{ background: var(--bedrock); color: #9fb2cf; padding: 44px 32px 30px; }}
  .footer-inner {{ max-width: 980px; margin: 0 auto; }}
  .footer-links {{ display: flex; flex-wrap: wrap; gap: 28px; margin-bottom: 22px; }}
  .footer-links a {{ display: block; min-width: 200px; margin: 0 28px 14px 0; color: #dbe4f3; text-decoration: none; font-size: 0.9rem; font-weight: 600; }}
  .footer-links a span {{ display: block; font-weight: 400; color: #8493ab; font-size: 0.8rem; margin-top: 2px; }}
  .footer-meta {{ border-top: 1px solid rgba(255,255,255,0.1); padding-top: 18px; font-size: 0.78rem; color: #7386a3; }}
  .pill-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }}
  .pill {{ display: inline-block; margin: 0 8px 8px 0; font-size: 0.78rem; font-weight: 600; padding: 4px 10px; border-radius: 999px; background: #f1f5f9; color: var(--ink); border: 1px solid var(--border); }}
</style>
</head>
<body>

<nav>
  <div class="brand">RDK-B Core Broadband <span class="mono">// base</span></div>
  <div class="navlinks">
    <a href="#overview">Overview</a>
    <a href="#architecture">Architecture</a>
    <a href="#standards">Standards</a>
    <a href="{components_url}">Components</a>
  </div>
</nav>

<div class="hero">
  <div class="hero-inner">
    <span class="eyebrow">RDK-B_CoreRDK_Spec_MVP · v1.0</span>
    <h1>RDK-B Core Broadband Platform</h1>
    <p class="lede">{intro}</p>
    <div class="badge-row">
      <span class="badge">26 features</span>
      <span class="badge">7 device profiles</span>
      <span class="badge">Five-tier architecture</span>
      <span class="badge">Apache-2.0 / LGPL-2.1</span>
    </div>
  </div>
</div>

<div class="stats">
  <div class="stat"><div class="num">2012</div><div class="lbl">Platform origin</div></div>
  <div class="stat"><div class="num">2016</div><div class="lbl">RDK Central formed</div></div>
  <div class="stat"><div class="num">100M+</div><div class="lbl">Devices deployed</div></div>
  <div class="stat"><div class="num">5</div><div class="lbl">Architecture tiers</div></div>
  <div class="stat"><div class="num">2026</div><div class="lbl">Matter / IoT added</div></div>
</div>

<section id="overview" class="tight-top">
  <div class="section-head">
    <span class="eyebrow-lt">01 — Overview</span>
    <h2>What is RDK-B?</h2>
  </div>

  <div class="callout">
    <strong>Platform definition</strong>
    <p>{definition}</p>
  </div>

  <div class="subhead" style="margin-top:0;">Platform origins</div>
  <div class="timeline">
    {timeline}
  </div>

  <div class="subhead">Licensing</div>
  <div class="pill-row">
    {licensing}
  </div>
</section>

<section id="architecture" style="background:#fff; border-top:1px solid var(--border); border-bottom:1px solid var(--border);">
  <div class="section-head">
    <span class="eyebrow-lt">02 — Architecture</span>
    <h2>The five-tier model</h2>
    <p>RDK-B's architecture reads like a cross-section: cloud-facing management at the
      top, silicon at the base, with the RDK-B middleware — the platform's largest tier —
      doing the work in between.</p>
  </div>

  <div class="tier-diagram">
    {five_tier}
  </div>
  <div class="tier-caption">Tier 3 (RDK-B Middleware) is where nearly all feature development happens; Tiers 1–2 are vendor-owned and certified via RDK Ready.</div>

  <div class="two-col" style="margin-top:44px;">
    <div>
      <div class="subhead" style="margin-top:0;">Production software builds</div>
      <div class="layer-stack">
        <div class="layer-box top">RDK-B Components</div>
        <div class="layer-box mid">Hardware Abstraction Layer</div>
        <div class="layer-box bot">Vendor Layer — hardware-dependent implementation</div>
      </div>
    </div>
    <div>
      <div class="subhead" style="margin-top:0;">Vendor test software builds</div>
      <div class="layer-stack">
        <div class="layer-box top">RDK Ready — Vendor Test Software</div>
        <div class="layer-box mid">Hardware Abstraction Layer</div>
        <div class="layer-box bot">Vendor Layer — hardware-dependent implementation</div>
      </div>
    </div>
  </div>

  <table class="def-table" style="margin-top:32px;">
    <thead><tr><th>Test suite</th><th>Definition</th><th>Owner</th></tr></thead>
    <tbody>
      {test_suites}
    </tbody>
  </table>
</section>

<section id="standards">
  <div class="section-head">
    <span class="eyebrow-lt">03 — Standards</span>
    <h2>Architecture standards and governance</h2>
    <p>Every new or refactored component is held to the same rules for modularity, IPC,
      testing, and data modeling — so the platform stays consistent as more vendors and
      operators contribute to it.</p>
  </div>

  <div class="subhead" style="margin-top:0;">Process, implementation &amp; coding standards</div>
  <table class="def-table">
    <thead><tr><th>Standard</th><th>Requirement</th></tr></thead>
    <tbody>
      {governance}
    </tbody>
  </table>

  <div class="subhead">Industry standards conformance</div>
  <p style="margin-bottom:18px;">Where RDK-B functionality overlaps an established global standard, the
    implementation conforms to that standard's normative requirements rather than
    introducing a proprietary deviation.</p>

  {industry}
</section>

<footer>
  <div class="footer-inner">
    <div class="footer-links">
      <a href="{components_url}">Components — profiles<span>Required / optional components per device profile</span></a>
      <a href="{components_full_url}">Components — full workbook<span>Interactive component list, all profiles</span></a>
      <a href="{spec_wiki_url}">RDK9 Core RDK Broadband Spec<span>TAB-approved specification (wiki)</span></a>
      <a href="https://github.com/rdkcentral">rdkcentral on GitHub<span>Component source repositories</span></a>
    </div>
    <div class="footer-meta">
      RDK-B_CoreRDK_Spec_MVP(InternalReference)_v1.0 · RDKM · © 2026 RDK Central. All rights reserved.
      Generated from {source_pdf}.
    </div>
  </div>
</footer>

</body>
</html>
"""


def build_html(data: dict) -> str:
    ov = data["overview"]
    return TEMPLATE.format(
        components_url=COMPONENTS_URL,
        components_full_url=COMPONENTS_FULL_URL,
        spec_wiki_url=SPEC_WIKI_URL,
        intro=esc(ov["intro"]),
        definition=esc(ov["definition"]),
        timeline=render_timeline(ov["origins_timeline"]),
        licensing=render_licensing(ov["licensing"]),
        five_tier=render_five_tier(data["five_tier"]),
        test_suites=render_test_suites(data["test_suites"]),
        governance=render_governance(data["governance_standards"]),
        industry=render_industry(data["industry_standards"]),
        source_pdf=esc(data["sourcePdf"]),
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("json_in")
    ap.add_argument("--out", default="index.html")
    args = ap.parse_args()

    data = json.loads(Path(args.json_in).read_text(encoding="utf-8"))
    Path(args.out).write_text(build_html(data), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
