"""Render index.html (About & Architecture) for CoreRDK-Broadband-Specification.

Two source files, two different sections of the same page:

  - docs/about-content.json  -> the About section (definition, goals/challenges,
    RDK Ready program, benefits). Hand-curated from the Core RDK Broadband
    deck (a slide layout, not a structured doc, so — like FIVE_TIER below —
    it isn't a good fit for automatic extraction). Update this file by hand
    when the deck changes.

  - docs/spec-content.json   -> the Architecture section (five-tier model,
    production/vendor-test layering, test suite ownership). Unchanged from
    before — still produced by extract_spec_content.py from the spec PDF.

architecture-standards.html and technical-governance.html are separate,
empty static stub pages (see gen_stub_pages.py) — not touched by this script.

Usage:
    python3 gen_base_page.py docs/spec-content.json docs/about-content.json --out-dir .
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from layout import esc, render_hero, render_page

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


# ---------- About section renderers (from about-content.json) ----------

def render_goals(goals: list[dict]) -> str:
    out = []
    for g in goals:
        out.append(f'''
    <div class="card" style="margin-bottom:16px;">
      <h3>{esc(g["title"])}</h3>
      <p><strong style="color:var(--ink);">Goal —</strong> {esc(g["goal"])}</p>
      <p style="margin-bottom:0;"><strong style="color:var(--amber-fg);">Challenge —</strong> {esc(g["challenge"])}</p>
    </div>''')
    return "\n".join(out)


def render_rdk_ready(items: list[dict]) -> str:
    out = []
    for it in items:
        out.append(f'''
    <div class="card">
      <h3>{esc(it["title"])}</h3>
      <p style="margin-bottom:0;">{esc(it["body"])}</p>
    </div>''')
    return f'<div class="two-col">{"".join(out)}</div>'


def render_benefits(groups: list[dict]) -> str:
    cols = []
    for g in groups:
        items_html = "".join(f'<li>{esc(i)}</li>' for i in g["items"])
        cols.append(f'''
    <div class="card">
      <h3>{esc(g["category"])}</h3>
      <ul style="margin:0; padding-left:18px; font-size:0.92rem; color:var(--muted);">{items_html}</ul>
    </div>''')
    return f'<div style="display:flex; gap:20px; flex-wrap:wrap;">' + \
        "".join(f'<div style="flex:1; min-width:220px;">{c}</div>' for c in cols) + '</div>'


# ---------- Architecture section renderers (from spec-content.json, unchanged) ----------

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


# ---------- page: About & Architecture ----------

def build_about_page(spec: dict, about: dict) -> str:
    hero_badges = (
        '<span class="badge">26 features</span>'
        '<span class="badge">7 device profiles</span>'
        '<span class="badge">Five-tier architecture</span>'
        '<span class="badge">Apache-2.0 / LGPL-2.1</span>'
    )
    body = f'''
{render_hero("Core RDK Broadband", "RDK-B Core Broadband Platform", about["definition"], hero_badges, visual_key="about")}

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
    <h2>What is RDKB Core?</h2>
  </div>

  <div class="callout">
    <strong>Platform definition</strong>
    <p>{esc(about["definition"])}</p>
  </div>

  <div class="subhead" style="margin-top:0;">Why RDKB Core</div>
  {render_goals(about["goals"])}

  <div class="subhead">RDK Ready — a test and certification program for vendors</div>
  {render_rdk_ready(about["rdk_ready"])}

  <div class="subhead">Benefits &amp; uses</div>
  {render_benefits(about["benefits"])}

  <div class="callout" style="margin-top:24px;">
    <strong>Value proposition</strong>
    <p>{esc(about["value_proposition"])}</p>
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
    {render_five_tier(spec["five_tier"])}
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
      {render_test_suites(spec["test_suites"])}
    </tbody>
  </table>
</section>

{FOOTER.format(source_pdf=esc(spec["sourcePdf"]))}
'''
    return render_page("about", "<title>About &amp; Architecture — RDK-B Core Broadband</title>", body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec_json", help="spec-content.json (drives the Architecture section)")
    ap.add_argument("about_json", help="about-content.json (drives the About section)")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()

    spec = json.loads(Path(args.spec_json).read_text(encoding="utf-8"))
    about = json.loads(Path(args.about_json).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "index.html").write_text(build_about_page(spec, about), encoding="utf-8")
    print(f"Wrote {out_dir / 'index.html'}")


if __name__ == "__main__":
    main()
