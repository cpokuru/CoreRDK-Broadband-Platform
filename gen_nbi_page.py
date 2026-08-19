"""One-time generator for north-bound-apis.html.

Unlike the other stub pages (gen_stub_pages.py), this one isn't a generic
"fetch one JSON/XML file" template — it's a two-level page:

  1. A table of every component, built from components/ethwan-router-components.json
     (the same data the Components profile page already uses).
  2. Clicking a component with a known DML source fetches
     https://raw.githubusercontent.com/cpokuru/<repo>/main/<file> and renders
     it. Which components have a DML source, which repo, and which filename
     is controlled entirely by dml-repos.json — a component's data file
     doesn't have to be literally named dml.json (e.g. wanmanager_interface_v3.json
     works fine), no HTML/script changes needed either way.
  3. Renders whatever shape the file turns out to be: a real TR-181-style
     export ({componentInterfaceDefinition, elements: {"Device.X...": {...}}}),
     a simpler {objects, parameters} export, a flat array, or anything else
     (falls back to a readable JSON tree).

This is still a static, one-time-generated page — rerun this only if the
page's design changes, not for new data (new components come from
re-running build_site.py's xlsx step; new DML repos come from editing
dml-repos.json).

Usage:
    python3 gen_nbi_page.py --out-dir .
"""
from __future__ import annotations

import argparse
from pathlib import Path

from layout import render_hero, render_page

SCRIPT = r"""
<script>
const COMPONENTS_JSON = 'components/ethwan-router-components.json';
const REPO_MAP_JSON = 'dml-repos.json';
const RAW_BASE = 'https://raw.githubusercontent.com/cpokuru/';

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s ?? '';
  return d.innerHTML;
}

// dml-repos.json entries can be either:
//   "Component Name": "RepoSlug"                                  (file defaults to dml.json)
//   "Component Name": { "repo": "RepoSlug", "file": "custom.json" } (explicit filename)
// so each component's data file doesn't have to be literally named dml.json.
function resolveRepoEntry(mapValue) {
  if (typeof mapValue === 'string') return { repo: mapValue, file: 'dml.json' };
  return { repo: mapValue.repo, file: mapValue.file || 'dml.json' };
}

// ---- generic renderer for whatever shape dml.json turns out to be ----
function findRecordArray(value) {
  if (Array.isArray(value)) return value;
  if (value && typeof value === 'object') {
    for (const v of Object.values(value)) {
      const found = findRecordArray(v);
      if (found) return found;
    }
  }
  return null;
}

function renderRecordTable(rows) {
  const isFlatObjectArray = rows.every(r => r && typeof r === 'object' && !Array.isArray(r));
  if (!isFlatObjectArray) {
    return '<ul style="list-style:none;padding:0;">' +
      rows.map(r => `<li style="padding:9px 12px;border-bottom:1px solid var(--border);font-family:'JetBrains Mono',monospace;font-size:0.85rem;">${esc(String(r))}</li>`).join('') +
      '</ul>';
  }
  const cols = Object.keys(rows[0]);
  return `<table class="def-table"><thead><tr>${cols.map(c => `<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>` +
    rows.map(r => `<tr>${cols.map(c => `<td class="mono">${esc(typeof r[c] === 'object' ? JSON.stringify(r[c]) : r[c])}</td>`).join('')}</tr>`).join('') +
    '</tbody></table>';
}

function renderTree(value) {
  return `<pre style="background:#0b1220;color:#cbd5e1;padding:20px;border-radius:10px;overflow-x:auto;font-size:0.82rem;max-height:600px;">${esc(JSON.stringify(value, null, 2))}</pre>`;
}

function renderDmlPayload(data) {
  // Shape A: { componentInterfaceDefinition: {...}, elements: { "Device.X...": {...}, ... } }
  // A real TR-181-style export, keyed by full parameter path rather than an
  // array. Show the component metadata as a header, then flatten `elements`
  // into a Path / Kind / Type / Access / Description table, splitting TR-181
  // "object" container rows (table nodes ending in a trailing dot) from
  // "parameter" leaf rows for a clearer picture of the interface surface.
  if (data && typeof data === 'object' && data.elements && typeof data.elements === 'object' && !Array.isArray(data.elements)) {
    const def = data.componentInterfaceDefinition || {};
    let out = '';
    if (def.name || def.description) {
      out += `<div class="card" style="margin-bottom:16px;">
        <h3>${esc(def.name || 'Interface')}${def.version ? ' <span class="mono" style="font-weight:400;font-size:0.8rem;color:var(--muted);">v' + esc(def.version) + '</span>' : ''}</h3>
        <p style="margin-bottom:6px;">${esc(def.description || '')}</p>
        <p class="mono" style="font-size:0.78rem; margin-bottom:0;">${esc(def.moduleName || '')}${def.generated ? ' · generated ' + esc(def.generated) : ''}</p>
      </div>`;
    }

    const rows = Object.entries(data.elements).map(([path, el]) => {
      const isObject = path.trim().endsWith('.') || 'maxInstance' in el || 'numberOfEntriesElement' in el;
      return {
        Path: path,
        Kind: isObject ? 'object' : 'parameter',
        Type: el.type || (isObject ? 'table' : ''),
        Access: Array.isArray(el.access) ? el.access.join(', ') : (el.access || ''),
        Description: el.description || '',
      };
    });
    const objectRows = rows.filter(r => r.Kind === 'object');
    const paramRows = rows.filter(r => r.Kind === 'parameter');

    if (objectRows.length) {
      out += `<div class="subhead" style="margin-top:0;">Objects (${objectRows.length})</div>` + renderRecordTable(objectRows);
    }
    if (paramRows.length) {
      out += `<div class="subhead">Parameters (${paramRows.length})</div>` + renderRecordTable(paramRows);
    }
    return out;
  }

  // Shape B: a DML export that already separates "objects" from "parameters"
  // as flat arrays -- render each as its own table when present, otherwise
  // fall back to the generic array/tree detection.
  if (data && typeof data === 'object' && !Array.isArray(data) && (data.objects || data.parameters)) {
    let out = '';
    if (data.objects) {
      out += `<div class="subhead" style="margin-top:0;">Objects (${data.objects.length})</div>` + renderRecordTable(data.objects);
    }
    if (data.parameters) {
      out += `<div class="subhead">Parameters (${data.parameters.length})</div>` + renderRecordTable(data.parameters);
    }
    return out;
  }
  const records = findRecordArray(data);
  return records ? renderRecordTable(records) : renderTree(data);
}

// ---- page state ----
let allComponents = [];
let repoMap = {};

function componentRowHtml(c) {
  const repoEntry = repoMap[c.name];
  const action = repoEntry
    ? `<button class="dml-btn" data-name="${esc(c.name)}">View DML</button>`
    : `<span class="muted" style="font-size:0.85rem;">Not available yet</span>`;
  return `<tr>
    <td>${esc(c.name)}</td>
    <td><span class="pill" style="background:#f1f5f9;">${esc(c.category || 'Uncategorized')}</span></td>
    <td>${action}</td>
  </tr>`;
}

function renderComponentTable(filterText) {
  const q = (filterText || '').trim().toLowerCase();
  const rows = allComponents.filter(c => !q || c.name.toLowerCase().includes(q) || (c.category || '').toLowerCase().includes(q));
  document.getElementById('component-table-body').innerHTML = rows.map(componentRowHtml).join('');
  document.getElementById('component-count').textContent = `${rows.length} of ${allComponents.length} components`;
  document.querySelectorAll('.dml-btn').forEach(btn => {
    btn.addEventListener('click', () => loadDml(btn.dataset.name));
  });
}

function loadDml(name) {
  const { repo, file } = resolveRepoEntry(repoMap[name]);
  const panel = document.getElementById('dml-panel');
  const url = RAW_BASE + repo + '/main/' + file;
  panel.innerHTML = `
    <div class="subhead" style="margin-top:0;">${esc(name)} <span class="mono" style="font-weight:400;font-size:0.8rem;color:var(--muted);">// ${esc(repo)}</span></div>
    <p>Loading <code>${esc(url)}</code>…</p>`;
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });

  fetch(url, { cache: 'no-store' })
    .then(res => { if (!res.ok) throw new Error('HTTP ' + res.status); return res.json(); })
    .then(data => {
      panel.innerHTML = `
        <div class="subhead" style="margin-top:0;">${esc(name)} <span class="mono" style="font-weight:400;font-size:0.8rem;color:var(--muted);">// ${esc(repo)}</span></div>
        <p><a href="${esc(url)}" target="_blank" rel="noopener">${esc(url)}</a></p>
        ${renderDmlPayload(data)}`;
    })
    .catch(err => {
      panel.innerHTML = `
        <div class="empty-state">
          <div class="icon">⚠️</div>
          <h3>Could not load DML for ${esc(name)}</h3>
          <p>Tried: <code>${esc(url)}</code></p>
          <p style="margin-top:8px;">${esc(err.message)}</p>
        </div>`;
    });
}

Promise.all([
  fetch(COMPONENTS_JSON, { cache: 'no-store' }).then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }),
  fetch(REPO_MAP_JSON, { cache: 'no-store' }).then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }),
]).then(([componentsData, repoMapData]) => {
  allComponents = componentsData.components;
  repoMap = repoMapData;
  delete repoMap._comment;
  renderComponentTable('');
  document.getElementById('component-search').addEventListener('input', e => renderComponentTable(e.target.value));
}).catch(err => {
  document.getElementById('component-table-wrap').innerHTML = `
    <div class="empty-state">
      <div class="icon">📄</div>
      <h3>Could not load component list</h3>
      <p>${esc(err.message)}</p>
    </div>`;
});
</script>
"""

EXTRA_CSS = """
<style>
  .search-row { margin-bottom: 16px; display: flex; align-items: center; gap: 12px; }
  .search-row input {
    flex: 1; max-width: 320px; padding: 9px 14px; border: 1px solid var(--border); border-radius: 8px;
    font-family: inherit; font-size: 0.9rem;
  }
  .search-row #component-count { font-size: 0.85rem; color: var(--muted); }
  .dml-btn {
    background: var(--middleware); color: #fff; border: none; border-radius: 6px;
    padding: 6px 14px; font-size: 0.82rem; font-weight: 600; cursor: pointer;
  }
  .dml-btn:hover { background: #1442ad; }
  #dml-panel { margin-top: 20px; }
</style>
"""


def build_page() -> str:
    body = f'''
{render_hero("North Bound APIs", "North Bound APIs",
    "The operator- and cloud-facing data model each component exposes upward. Click a component below to load its DML definition.",
    compact=True, visual_key="nbi")}

<section class="tight-top">
  <div id="component-table-wrap">
    <div class="search-row">
      <input id="component-search" type="text" placeholder="Filter components…">
      <span id="component-count" class="mono"></span>
    </div>
    <table class="def-table">
      <thead><tr><th>Component</th><th>Category</th><th>DML</th></tr></thead>
      <tbody id="component-table-body">
        <tr><td colspan="3">Loading components…</td></tr>
      </tbody>
    </table>
  </div>

  <div id="dml-panel"></div>
</section>
'''
    head_extra = "<title>North Bound APIs — RDK-B Core Broadband</title>\n" + EXTRA_CSS + SCRIPT
    return render_page("nbi", head_extra, body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "north-bound-apis.html"
    path.write_text(build_page(), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
