"""Render the three spec-content.json-driven pages for
CoreRDK-Broadband-Specification:

    index.html                    About & Architecture
    architecture-standards.html   Industry standards conformance
    technical-governance.html     Internal process/coding/IPC standards

All three share the left-sidebar layout in layout.py. Three other sidebar
links (North Bound APIs, South Bound APIs, Hardware Compatibility) point to
static stub pages that aren't touched by this script — see
gen_stub_pages.py.

Usage:
    python3 gen_base_page.py spec-content.json --out-dir .
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from layout import esc, render_page

COMPONENTS_URL = "components/"
COMPONENTS_FULL_URL = "components/full-list.html"
SPEC_WIKI_URL = "https://wiki.rdkcentral.com/spaces/RDK/pages/498925914/RDK9+Core+RDK+Broadband+Specification+Approved+by+TAB"

FOOTER = """
<footer>
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
</footer>
""".format(components_url=COMPONENTS_URL, components_full_url=COMPONENTS_FULL_URL,
           spec_wiki_url=SPEC_WIKI_URL, source_pdf="{source_pdf}")


# ---------- shared renderers ----------

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


# ---------- page 1: About & Architecture ----------

def build_about_page(data: dict) -> str:
    ov = data["overview"]
    body = f'''
<div class="hero">
  <div class="hero-inner">
    <span class="eyebrow">RDK-B_CoreRDK_Spec_MVP · v1.0</span>
    <h1>RDK-B Core Broadband Platform</h1>
    <p class="lede">{esc(ov["intro"])}</p>
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

<section class="tight-top">
  <div class="section-head">
    <span class="eyebrow-lt">About</span>
    <h2>What is RDK-B?</h2>
  </div>

  <div class="callout">
    <strong>Platform definition</strong>
    <p>{esc(ov["definition"])}</p>
  </div>

  <div class="subhead" style="margin-top:0;">Platform origins</div>
  <div class="timeline">
    {render_timeline(ov["origins_timeline"])}
  </div>

  <div class="subhead">Licensing</div>
  <div class="pill-row">
    {render_licensing(ov["licensing"])}
  </div>
</section>

<section style="background:#fff; border-top:1px solid var(--border); border-bottom:1px solid var(--border);">
  <div class="section-head">
    <span class="eyebrow-lt">Architecture</span>
    <h2>The five-tier model</h2>
    <p>RDK-B's architecture reads like a cross-section: cloud-facing management at the
      top, silicon at the base, with the RDK-B middleware — the platform's largest tier —
      doing the work in between.</p>
  </div>

  <div class="tier-diagram">
    {render_five_tier(data["five_tier"])}
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
      {render_test_suites(data["test_suites"])}
    </tbody>
  </table>
</section>

{FOOTER.format(source_pdf=esc(data["sourcePdf"]))}
'''
    return render_page("about", "<title>About &amp; Architecture — RDK-B Core Broadband</title>", body)


# ---------- page 2: Architecture Standards ----------

def build_architecture_standards_page(data: dict) -> str:
    body = f'''
<div class="hero" style="padding:48px 40px 40px;">
  <div class="hero-inner">
    <span class="eyebrow">Architecture Standards</span>
    <h1 style="font-size:2rem;">Industry standards conformance</h1>
    <p class="lede">Where RDK-B functionality overlaps an established global standard, the
      implementation conforms to that standard's normative requirements rather than
      introducing a proprietary deviation.</p>
  </div>
</div>

<section class="tight-top">
  {render_industry(data["industry_standards"])}
</section>

{FOOTER.format(source_pdf=esc(data["sourcePdf"]))}
'''
    return render_page("architecture-standards", "<title>Architecture Standards — RDK-B Core Broadband</title>", body)


# ---------- page 3: Technical Governance ----------

def build_technical_governance_page(data: dict) -> str:
    body = f'''
<div class="hero" style="padding:48px 40px 40px;">
  <div class="hero-inner">
    <span class="eyebrow">Technical Governance</span>
    <h1 style="font-size:2rem;">Process, implementation &amp; coding standards</h1>
    <p class="lede">Every new or refactored component is held to the same rules for modularity,
      IPC, testing, and data modeling — so the platform stays consistent as more vendors
      and operators contribute to it.</p>
  </div>
</div>

<section class="tight-top">
  <table class="def-table">
    <thead><tr><th>Standard</th><th>Requirement</th></tr></thead>
    <tbody>
      {render_governance(data["governance_standards"])}
    </tbody>
  </table>
</section>

{FOOTER.format(source_pdf=esc(data["sourcePdf"]))}
'''
    return render_page("technical-governance", "<title>Technical Governance — RDK-B Core Broadband</title>", body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("json_in")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()

    data = json.loads(Path(args.json_in).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "index.html").write_text(build_about_page(data), encoding="utf-8")
    (out_dir / "architecture-standards.html").write_text(build_architecture_standards_page(data), encoding="utf-8")
    (out_dir / "technical-governance.html").write_text(build_technical_governance_page(data), encoding="utf-8")

    print(f"Wrote {out_dir / 'index.html'}")
    print(f"Wrote {out_dir / 'architecture-standards.html'}")
    print(f"Wrote {out_dir / 'technical-governance.html'}")


if __name__ == "__main__":
    main()
