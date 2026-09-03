"""One-purpose generator for component-registry.html.

Two parts, in order:

1. The registry rules themselves -- section 7.3.2 (Component Registry),
   7.3.2.1 (Mandatory Registry Fields), 7.3.2.2 (Registry Maintenance
   Rules), 7.3.3 (Component Lifecycle States), and 7.3.3.1 (State
   Transition Rules) of the Core RDK Broadband Specification. This content
   already exists in component-governance.json (it also backs the
   "Component Governance Process" block on technical-governance.html) --
   this page fetches that same file client-side and renders only the
   7.3.2/7.3.3 subsection numbers, using the same .gov-section/.def-table
   CSS classes technical-governance.html uses, so the two pages read as
   one consistent design language.

2. The catalog itself -- every component across every device profile, one
   row each, from components/all-components.json. This is intentionally
   a narrower field set than the full 7.3.2.1 mandatory field list (only
   name/category/tier/repo, from the existing extraction pipeline) --
   owner, lifecycle state, HAL contract, TR-181 model, and dependencies
   still need their own data source before they can render here.

Usage:
    python3 gen_component_registry_page.py --data components/all-components.json \\
        --governance component-governance.json --out-dir .
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
    "lede": "The authoritative record of every RDK-B component -- registration, lifecycle "
            "state, and ownership, per §7.3.2 of the Core RDK Broadband Specification.",
}

GOV_SECTION_NUMBERS = ["7.3.2", "7.3.2.1", "7.3.2.2", "7.3.3", "7.3.3.1"]

SCRIPT_TEMPLATE = """
<script>
const DATA_URL = {data_url_json};
const GOV_URL = {gov_url_json};
const GOV_NUMBERS = {gov_numbers_json};

function esc(s) {{
  const d = document.createElement('div');
  d.textContent = s ?? '';
  return d.innerHTML;
}}

// ---- governance rules (section 7.3.2 / 7.3.3), same renderer shape as
// technical-governance.html so both pages look like one document ----
function renderGovSections(sections) {{
  let html = '';
  for (const s of sections) {{
    const level = s.level || 2;
    const tag = level <= 2 ? 'h3' : (level === 3 ? 'h4' : 'h5');
    html += `<div class="gov-section level-${{level}}">`;
    html += `<${{tag}}><span class="gov-num">${{esc(s.number)}}</span><span>${{esc(s.title)}}</span></${{tag}}>`;
    let listOpen = false;
    for (const b of (s.blocks || [])) {{
      if (b.type === 'table') {{
        if (listOpen) {{ html += '</ul>'; listOpen = false; }}
        html += '<table class="def-table"><thead><tr>' + b.headers.map(h => `<th>${{esc(h)}}</th>`).join('') + '</tr></thead><tbody>' +
          b.rows.map(r => `<tr>${{r.map(c => `<td>${{esc(c)}}</td>`).join('')}}</tr>`).join('') + '</tbody></table>';
      }} else if (b.type === 'li') {{
        if (!listOpen) {{ html += '<ul>'; listOpen = true; }}
        html += `<li>${{esc(b.text)}}</li>`;
      }} else {{
        if (listOpen) {{ html += '</ul>'; listOpen = false; }}
        html += `<p>${{esc(b.text)}}</p>`;
      }}
    }}
    if (listOpen) html += '</ul>';
    html += '</div>';
  }}
  return html;
}}

fetch(GOV_URL, {{ cache: 'no-store' }})
  .then(res => {{ if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); }})
  .then(data => {{
    const sections = (data.docs || []).filter(s => GOV_NUMBERS.includes(s.number));
    document.getElementById('cr-gov').innerHTML = renderGovSections(sections);
  }})
  .catch(() => {{
    document.getElementById('cr-gov').innerHTML =
      '<p style="color:var(--muted);">Registry policy text (§7.3.2–§7.3.3) could not be loaded from ' + esc(GOV_URL) + '.</p>';
  }});

// ---- catalog table (components/all-components.json) ----
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
    rows.length === ALL.length ? `${{ALL.length}} registered components` : `${{rows.length}} of ${{ALL.length}} registered components`;

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
  .cr-catalog-note { font-size: 0.86rem; color: var(--muted); margin: -6px 0 20px; max-width: 720px; }
</style>
"""


def build_page(data_rel_url: str, gov_rel_url: str) -> str:
    hero_badges = '<span class="badge">§7.3.2 Component Registry</span><span class="badge">§7.3.3 Lifecycle States</span>'
    body = render_hero(PAGE["eyebrow"], PAGE["title"], PAGE["lede"], hero_badges,
                        compact=True, visual_key=PAGE["active_id"]) + f'''
<section class="tight-top">
  <div id="cr-gov"><div class="empty-state"><p>Loading registry policy…</p></div></div>
</section>

<section class="tight-top">
  <div class="section-head">
    <span class="eyebrow-lt">Registry data</span>
    <h2>Registered Components</h2>
  </div>
  <p class="cr-catalog-note">
    Currently populated fields: component name, category, source repository, and per-profile
    classification tier. Owner, lifecycle state, HAL contract reference, TR-181 model, and
    dependency fields from §7.3.2.1 are not yet tracked in the pipeline that feeds this table.
  </p>
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
        SCRIPT_TEMPLATE.format(
            data_url_json=json.dumps(data_rel_url),
            gov_url_json=json.dumps(gov_rel_url),
            gov_numbers_json=json.dumps(GOV_SECTION_NUMBERS),
        )
    return render_page(PAGE["active_id"], head_extra, body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="components/all-components.json",
                     help="Path (relative to the built site root) to the component catalog JSON.")
    ap.add_argument("--governance", default="component-governance.json",
                     help="Path (relative to the built site root) to the governance sections JSON.")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / "component-registry.html"
    path.write_text(build_page(args.data, args.governance), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
