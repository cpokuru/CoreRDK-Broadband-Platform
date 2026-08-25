"""One-time generator for four of the not-yet-populated sidebar pages:

    architecture-standards.html
    technical-governance.html
    south-bound-apis.html
    hardware-compatibility.html

These are static pages — run this once now, commit the output, and don't
rerun it as part of build_site.py. Each page ships with a generic loader
that tries <slug>.json then <slug>.xml (same folder) at runtime and renders
whatever it finds; until one of those data files exists, the page shows a
clean "no data yet" empty state instead of breaking.

The JSON/XML shape is intentionally unconstrained — the loader renders:
  - an array of flat objects (same keys) as a table
  - an array of primitives as a list
  - anything else (nested objects) as a formatted read-only tree

That means whoever eventually owns north-bound-apis.json (etc.) doesn't
need to touch this HTML at all — just drop a JSON or XML file with real
data next to the page and refresh.

Usage:
    python3 gen_stub_pages.py --out-dir .
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from layout import render_hero, render_page

PAGES = [
    {
        "active_id": "architecture-standards",
        "slug": "architecture-standards",
        "eyebrow": "Architecture Standards",
        "title": "Architecture Standards",
        "lede": "Industry standards RDK-B conforms to where its functionality overlaps "
                "an established global standard.",
        "tables": [
            {"slug": "architecture-standards"},
            {
                "slug": "architecture-standards-industry",
                "heading": "Industry Standards Conformance",
                "blurb": "Where RDK-B functionality overlaps an established external "
                         "standards body, tracked by category (§7.1.3).",
            },
        ],
    },
    {
        "active_id": "technical-governance",
        "slug": "technical-governance",
        "eyebrow": "Development Standards",
        "title": "Development Standards",
        "lede": "Process, implementation, and coding standards every new or refactored "
                "component is held to.",
    },
    {
        "active_id": "sbi",
        "slug": "south-bound-apis",
        "eyebrow": "South Bound APIs",
        "title": "South Bound APIs",
        "lede": "The HAL and vendor-facing interfaces RDK-B exposes downward — the "
                "rdkb-halif-* contracts between middleware and SoC/BSP.",
    },
    {
        "active_id": "hwcompat",
        "slug": "hardware-compatibility",
        "eyebrow": "Hardware Compatibility",
        "title": "Hardware Compatibility Spec",
        "lede": "Certified SoC platforms, chipset families, and the HAL interface "
                "versions each one supports.",
    },
]

LOADER_SCRIPT_TEMPLATE = """
<script>
const TABLES = {tables_json};

function esc(s) {{
  const d = document.createElement('div');
  d.textContent = s ?? '';
  return d.innerHTML;
}}

// Very small generic XML -> plain-object walker. Repeated sibling tags
// become an array; text-only leaves become strings. Good enough for a
// simple "list of records" style XML file; deeply irregular XML falls
// back to the raw-tree renderer further down.
function xmlToObj(node) {{
  const children = Array.from(node.children);
  if (children.length === 0) {{
    return (node.textContent || '').trim();
  }}
  const out = {{}};
  for (const child of children) {{
    const val = xmlToObj(child);
    if (out[child.tagName] === undefined) {{
      out[child.tagName] = val;
    }} else if (Array.isArray(out[child.tagName])) {{
      out[child.tagName].push(val);
    }} else {{
      out[child.tagName] = [out[child.tagName], val];
    }}
  }}
  return out;
}}

function findRecordArray(value) {{
  // Walk a parsed JSON/XML object looking for the first array of
  // same-shaped flat objects — that's almost certainly "the data".
  if (Array.isArray(value)) return value;
  if (value && typeof value === 'object') {{
    for (const v of Object.values(value)) {{
      const found = findRecordArray(v);
      if (found) return found;
    }}
  }}
  return null;
}}

function renderTable(rows) {{
  const isFlatObjectArray = rows.every(r => r && typeof r === 'object' && !Array.isArray(r));
  if (!isFlatObjectArray) {{
    return '<ul class="def-table" style="list-style:none;padding:0;">' +
      rows.map(r => `<li style="padding:9px 12px;border-bottom:1px solid var(--border);">${{esc(String(r))}}</li>`).join('') +
      '</ul>';
  }}
  const cols = Object.keys(rows[0]);
  return `<table class="def-table"><thead><tr>${{cols.map(c => `<th>${{esc(c)}}</th>`).join('')}}</tr></thead><tbody>` +
    rows.map(r => `<tr>${{cols.map(c => `<td>${{esc(r[c])}}</td>`).join('')}}</tr>`).join('') +
    '</tbody></table>';
}}

function renderTree(value) {{
  return `<pre style="background:#0b1220;color:#cbd5e1;padding:20px;border-radius:10px;overflow-x:auto;font-size:0.85rem;">${{esc(JSON.stringify(value, null, 2))}}</pre>`;
}}

function render(containerId, value) {{
  const content = document.getElementById(containerId);
  const records = findRecordArray(value);
  content.innerHTML = records ? renderTable(records) : renderTree(value);
}}

function showEmptyState(containerId, jsonFile, xmlFile) {{
  document.getElementById(containerId).innerHTML = `
    <div class="empty-state">
      <div class="icon">📄</div>
      <h3>No data published yet</h3>
      <p>This section renders automatically once a data file is added.<br>Drop either file next to this page:</p>
      <p><code>${{esc(jsonFile)}}</code> &nbsp;or&nbsp; <code>${{esc(xmlFile)}}</code></p>
    </div>`;
}}

function loadTable(t) {{
  const jsonFile = t.slug + '.json';
  const xmlFile = t.slug + '.xml';
  fetch(jsonFile, {{ cache: 'no-store' }})
    .then(res => {{ if (!res.ok) throw new Error('no json'); return res.json(); }})
    .then(data => render(t.containerId, data))
    .catch(() => {{
      fetch(xmlFile, {{ cache: 'no-store' }})
        .then(res => {{ if (!res.ok) throw new Error('no xml'); return res.text(); }})
        .then(text => {{
          const xml = new DOMParser().parseFromString(text, 'application/xml');
          if (xml.getElementsByTagName('parsererror').length > 0) throw new Error('bad xml');
          render(t.containerId, xmlToObj(xml.documentElement));
        }})
        .catch(() => showEmptyState(t.containerId, jsonFile, xmlFile));
    }});
}}

TABLES.forEach(loadTable);
</script>
"""


def build_stub_page(page: dict) -> str:
    tables = page.get("tables") or [{"slug": page["slug"]}]
    sections = []
    tables_js = []
    for i, t in enumerate(tables):
        container_id = "data-content" if i == 0 else f"data-content-{i + 1}"
        tables_js.append({"containerId": container_id, "slug": t["slug"]})
        heading_html = ""
        if t.get("heading"):
            blurb = f'<p>{t["blurb"]}</p>' if t.get("blurb") else ""
            heading_html = f'<div class="section-head"><h2>{t["heading"]}</h2>{blurb}</div>'
        sections.append(f'''
<section class="tight-top">
  {heading_html}
  <div id="{container_id}"><div class="empty-state"><p>Loading…</p></div></div>
</section>
''')

    body = render_hero(page["eyebrow"], page["title"], page["lede"], compact=True, visual_key=page["active_id"]) \
        + "".join(sections)
    head_extra = f"<title>{page['title']} — RDK-B Core Broadband</title>\n" + \
        LOADER_SCRIPT_TEMPLATE.format(tables_json=json.dumps(tables_js))
    return render_page(page["active_id"], head_extra, body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for page in PAGES:
        path = out_dir / f"{page['slug']}.html"
        path.write_text(build_stub_page(page), encoding="utf-8")
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
