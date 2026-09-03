"""One-purpose generator for component-registry.html.

Renders a single, profile-agnostic component catalog -- every component
across every RDK-B device profile, one row each, no per-profile split.
Source of truth is components/all-components.json (already deduplicated
across profiles by extract_components.py's all-profiles/merge step); all
parsing and rendering happens client-side in the generated page, since
all-components.json's shape ({schemaVersion, tiers, components}) doesn't
fit the generic "flat array of records" loader in layout.render_stub_page
-- the tiers legend array would get picked up as "the data" instead of the
78-entry components array.

This intentionally carries a narrower field set than the full section 7.3.2
Component Registry (name/category/tier/repo only, from the existing
extraction pipeline) -- it's the profile-agnostic catalog view, not the
governance registry with owner/lifecycle/HAL contract/dependencies. Those
richer fields still need their own data source before they can render here
or anywhere else.

Usage:
    python3 gen_component_registry_page.py --data components/all-components.json --out-dir .
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from layout import esc, render_hero, render_page

PAGE = {
    "active_id": "component-registry",
    "eyebrow": "Component Registry",
    "title": "Component Registry",
    "lede": "Every RDK-B component in one place, independent of device profile -- name, "
            "category, classification tier, and source repository.",
}

SCRIPT_TEMPLATE = """
<script>
const DATA_URL = {data_url_json};

function esc(s) {{
  const d = document.createElement('div');
  d.textContent = s ?? '';
  return d.innerHTML;
}}

let ALL = [];
let TIERS = [];
let activeTier = null;

function tierMeta(id) {{
  return TIERS.find(t => t.id === id) || {{ id, label: id, color: 'gray' }};
}}

function renderLegend() {{
  const el = document.getElementById('cr-legend');
  el.innerHTML = TIERS.map(t => {{
    const count = ALL.filter(c => c.tier === t.id).length;
    const active = activeTier === t.id ? ' active' : '';
    return `<button class="cr-chip cr-chip-${{esc(t.color)}}${{active}}" data-tier="${{esc(t.id)}}">` +
      `${{esc(t.label)}} <span class="cr-chip-count">${{count}}</span></button>`;
  }}).join('') +
  `<button class="cr-chip cr-chip-all${{activeTier === null ? ' active' : ''}}" data-tier="">All <span class="cr-chip-count">${{ALL.length}}</span></button>`;
  el.querySelectorAll('.cr-chip').forEach(btn => {{
    btn.addEventListener('click', () => {{
      activeTier = btn.dataset.tier || null;
      renderLegend();
      renderTable();
    }});
  }});
}}

function renderTable() {{
  const q = document.getElementById('cr-search').value.trim().toLowerCase();
  const rows = ALL.filter(c => {{
    if (activeTier && c.tier !== activeTier) return false;
    if (!q) return true;
    return c.name.toLowerCase().includes(q) || c.category.toLowerCase().includes(q);
  }});

  document.getElementById('cr-count').textContent =
    rows.length === ALL.length ? `${{ALL.length}} components` : `${{rows.length}} of ${{ALL.length}} components`;

  const body = document.getElementById('cr-tbody');
  if (!rows.length) {{
    body.innerHTML = `<tr><td colspan="3" class="cr-empty">No components match "${{esc(q)}}".</td></tr>`;
    return;
  }}
  body.innerHTML = rows
    .sort((a, b) => a.name.localeCompare(b.name))
    .map(c => {{
      const t = tierMeta(c.tier);
      return `<tr>` +
        `<td><a href="${{esc(c.url)}}" target="_blank" rel="noopener">${{esc(c.name)}}</a></td>` +
        `<td class="cr-cat">${{esc(c.category)}}</td>` +
        `<td><span class="cr-badge cr-chip-${{esc(t.color)}}">${{esc(t.label)}}</span></td>` +
        `</tr>`;
    }}).join('');
}}

fetch(DATA_URL, {{ cache: 'no-store' }})
  .then(res => {{ if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); }})
  .then(data => {{
    ALL = data.components || [];
    TIERS = data.tiers || [];
    document.getElementById('cr-loading').style.display = 'none';
    document.getElementById('cr-content').style.display = '';
    renderLegend();
    renderTable();
    document.getElementById('cr-search').addEventListener('input', renderTable);
  }})
  .catch(err => {{
    document.getElementById('cr-loading').innerHTML =
      `<div class="empty-state"><div class="icon">📄</div><h3>Could not load the catalog</h3>` +
      `<p>${{esc(err.message)}} — expected data at <code>${{esc(DATA_URL)}}</code>.</p></div>`;
  }});
</script>
"""

STYLE = """
<style>
  .cr-toolbar { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; margin-bottom: 18px; }
  .cr-search-input { flex: 1 1 260px; max-width: 340px; padding: 10px 14px; font-size: 0.92rem;
    border: 1px solid var(--border); border-radius: 10px; background: var(--card-bg); color: var(--ink); }
  .cr-count { font-size: 0.82rem; color: var(--muted); white-space: nowrap; }
  .cr-legend { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 22px; }
  .cr-chip { border: 1px solid var(--border); background: var(--card-bg); color: var(--ink);
    border-radius: 999px; padding: 6px 14px; font-size: 0.82rem; font-weight: 600; cursor: pointer;
    display: inline-flex; align-items: center; gap: 6px; transition: border-color 0.15s, background 0.15s; }
  .cr-chip:hover { border-color: var(--middleware); }
  .cr-chip.active { background: var(--ink); color: #fff; border-color: var(--ink); }
  .cr-chip-count { font-weight: 700; opacity: 0.65; font-size: 0.78rem; }
  .cr-chip-gold::before, .cr-badge.cr-chip-gold::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: #d97706; display: inline-block; }
  .cr-chip-blue::before, .cr-badge.cr-chip-blue::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--middleware); display: inline-block; }
  .cr-chip-gray::before, .cr-badge.cr-chip-gray::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: #9ca3af; display: inline-block; }
  .cr-chip-all::before { display: none; }
  table.cr-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
  table.cr-table thead th { text-align: left; background: var(--page-bg); color: var(--muted); font-weight: 600;
    font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.04em; padding: 12px 16px; border-bottom: 1px solid var(--border); }
  table.cr-table tbody td { padding: 12px 16px; border-bottom: 1px solid var(--border); vertical-align: middle; }
  table.cr-table tbody tr:last-child td { border-bottom: none; }
  table.cr-table tbody tr:hover { background: var(--page-bg); }
  table.cr-table a { font-weight: 600; text-decoration: none; }
  table.cr-table a:hover { text-decoration: underline; }
  .cr-cat { color: var(--muted); }
  .cr-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px;
    font-size: 0.78rem; font-weight: 600; border: 1px solid var(--border); }
  .cr-empty { text-align: center; color: var(--muted); padding: 32px 16px !important; }
</style>
"""


def build_page(data_rel_url: str) -> str:
    hero_badges = '<span class="badge">Profile-independent catalog</span>'
    body = render_hero(PAGE["eyebrow"], PAGE["title"], PAGE["lede"], hero_badges,
                        compact=True, visual_key=PAGE["active_id"]) + f'''
<section class="tight-top">
  <div id="cr-loading" class="empty-state"><p>Loading component catalog…</p></div>
  <div id="cr-content" style="display:none;">
    <div class="cr-toolbar">
      <input id="cr-search" class="cr-search-input" type="text" placeholder="Search by name or category…" />
      <span id="cr-count" class="cr-count"></span>
    </div>
    <div id="cr-legend" class="cr-legend"></div>
    <table class="cr-table">
      <thead><tr><th>Component</th><th>Category</th><th>Tier</th></tr></thead>
      <tbody id="cr-tbody"></tbody>
    </table>
  </div>
</section>
'''
    head_extra = f"<title>{PAGE['title']} — RDK-B Core Broadband</title>\n" + STYLE + \
        SCRIPT_TEMPLATE.format(data_url_json=json.dumps(data_rel_url))
    return render_page(PAGE["active_id"], head_extra, body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="components/all-components.json",
                     help="Path (relative to the built site root) to the component catalog JSON.")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / "component-registry.html"
    path.write_text(build_page(args.data), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
