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
from urllib.parse import quote

from layout import esc, render_hero, render_page

PAGES = [
    {
        "active_id": "architecture-standards",
        "slug": "architecture-standards",
        "eyebrow": "Architecture Standards",
        "title": "Architecture Standards",
        "lede": "Architectural rules every new or refactored component follows — "
                "modularity, IPC, dependency management, and data model documentation (§7.1.1).",
    },
    {
        "active_id": "industry-standards",
        "slug": "industry-standards",
        "eyebrow": "Industry Conformance Standards",
        "title": "Industry Conformance Standards",
        "lede": "Where RDK-B functionality overlaps an established external standards "
                "body, tracked by category (§7.1.3).",
        "tables": [
            {"slug": "architecture-standards-industry"},
        ],
    },
    {
        "active_id": "technical-governance",
        "slug": "technical-governance",
        "eyebrow": "Development Standards",
        "title": "Development Standards",
        "lede": "Process, implementation, and coding standards every new or refactored "
                "component is held to.",
        "tables": [
            {"slug": "technical-governance"},
            {
                "slug": "technical-governance-process",
                "kind": "sections",
                "heading": "Technical Governance Process",
                "blurb": "How a change moves from proposal to merge — classification, entry "
                         "criteria, architecture review, testing, and release governance (§7.2).",
            },
            {
                "slug": "component-governance",
                "kind": "sections",
                "heading": "Component Governance Process",
                "blurb": "How components are registered, owned, health-reviewed, deprecated, "
                         "and how interface stability is tagged over their lifecycle (§7.3).",
            },
        ],
    },
    {
        "active_id": "nbi-spec",
        "slug": "north-bound-specification",
        "eyebrow": "North Bound APIs",
        "title": "North Bound Specification",
        "lede": "The RDK-B High Level API Specification — the northbound protocol and "
                "data-model contract (TR-069, TR-369/USP, WebPA, TR-181).",
        "tables": [
            {"slug": "north-bound-specification", "kind": "sections"},
        ],
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

function renderSections(sections) {{
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
      }} else if (b.type === 'pre') {{
        if (listOpen) {{ html += '</ul>'; listOpen = false; }}
        html += `<pre class="code-block">${{esc(b.text)}}</pre>`;
      }} else if (b.type === 'h') {{
        if (listOpen) {{ html += '</ul>'; listOpen = false; }}
        html += `<h5 class="gov-subhead">${{esc(b.text)}}</h5>`;
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

function render(containerId, value, kind) {{
  const content = document.getElementById(containerId);
  if (kind === 'sections') {{
    const sections = Array.isArray(value) ? value : (Array.isArray(value && value.docs) ? value.docs : findRecordArray(value));
    content.innerHTML = sections ? renderSections(sections) : renderTree(value);
    return;
  }}
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
    .then(data => render(t.containerId, data, t.kind))
    .catch(() => {{
      fetch(xmlFile, {{ cache: 'no-store' }})
        .then(res => {{ if (!res.ok) throw new Error('no xml'); return res.text(); }})
        .then(text => {{
          const xml = new DOMParser().parseFromString(text, 'application/xml');
          if (xml.getElementsByTagName('parsererror').length > 0) throw new Error('bad xml');
          render(t.containerId, xmlToObj(xml.documentElement), t.kind);
        }})
        .catch(() => showEmptyState(t.containerId, jsonFile, xmlFile));
    }});
}}

TABLES.forEach(loadTable);
</script>
"""


def build_pdf_page(page: dict) -> str:
    """A PDF-embed page (e.g. North Bound Specification): no JSON loader,
    just an <iframe> pointing at the PDF already checked into the repo, plus
    a plain-link fallback for browsers/mobile viewers that force a download
    instead of rendering the iframe inline."""
    pdf_src = quote(page["pdf"], safe="/")
    body = render_hero(page["eyebrow"], page["title"], page["lede"], compact=True, visual_key=page["active_id"]) + f'''
<section class="tight-top">
  <div class="pdf-embed-wrap">
    <iframe src="{esc(pdf_src)}" title="{esc(page["title"])}" loading="lazy"></iframe>
  </div>
  <p style="margin-top:14px; font-size:0.86rem;">
    Viewer not loading? <a href="{esc(pdf_src)}" target="_blank" rel="noopener">Open the PDF directly ↗</a>
  </p>
</section>
'''
    head_extra = f"<title>{page['title']} — RDK-B Core Broadband</title>\n" + \
        '<style>.pdf-embed-wrap{border:1px solid var(--border);border-radius:12px;overflow:hidden;' \
        'box-shadow:var(--shadow-sm);height:82vh;min-height:520px;}' \
        '.pdf-embed-wrap iframe{width:100%;height:100%;border:none;display:block;}</style>'
    return render_page(page["active_id"], head_extra, body)


def build_stub_page(page: dict) -> str:
    tables = page.get("tables") or [{"slug": page["slug"]}]
    sections = []
    tables_js = []
    for i, t in enumerate(tables):
        container_id = "data-content" if i == 0 else f"data-content-{i + 1}"
        tables_js.append({"containerId": container_id, "slug": t["slug"], "kind": t.get("kind", "table")})
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
        html = build_pdf_page(page) if "pdf" in page else build_stub_page(page)
        path.write_text(html, encoding="utf-8")
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
