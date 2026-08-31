"""One-time generator for hardware-compatibility.html.

Unlike the other stub pages, this one reads a small set of static local
files rather than fetching anything client-side: one JSON file per RDK-B
device profile (docs/*.json, matching docs/hw-compat.schema.json), published
per Core-RDK-Broadband-Hardware-Compatibility-Spec_v3.docx section 3.2.
Everything is rendered server-side at generation time.

Two of the seven profiles (EthWAN WiFi Router, EXT EasyMesh) are actually
in scope for this spec revision and carry real CPU/RAM/flash/peripheral
data; the other five are defined in the RDK-B Component List 2026 but not
yet covered -- their JSON files are present with every field set to "n/a"
(see hw-compat.schema.json's own description) and are rendered as a
compact "not yet covered" list rather than full detail cards.

PROFILE_DEFINITIONS below is the one piece of narrative text that isn't in
the JSON schema (the spec's own one-line profile definitions, per Table 1
of the .docx) -- kept here as a small static lookup since it rarely
changes and isn't worth its own data file for seven short lines.

Usage:
    python3 gen_hwcompat_page.py --profiles-dir docs --out-dir .
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from layout import esc, render_hero, render_page

# From Table 1 of Core-RDK-Broadband-Hardware-Compatibility-Spec_v3.docx --
# the RDK-B Component List 2026's one-line definition of each of the seven
# profiles. Order here also sets display order (in-scope profiles first).
PROFILE_DEFINITIONS: dict[str, str] = {
    "ethwan-wifi-router": "IPv4/IPv6 router with Ethernet WAN and Wi-Fi AP features. EasyMesh features are optional.",
    "ext-easymesh": "Wi-Fi extender device based on EasyMesh Agent technology; supports Wi-Fi AP fronthaul and Wi-Fi/Ethernet backhaul.",
    "modem-onu": "Managed or unmanaged bridge from a WAN access technology to an Ethernet LAN port(s); may provide WAN configuration and diagnostics data. Does not include routing or Wi-Fi AP features.",
    "gw": "IPv4/IPv6 router with one or more WAN access technologies and Wi-Fi AP features.",
    "gw-opensync": "IPv4/IPv6 router with one or more WAN access technologies and OpenSync Mesh Wi-Fi features.",
    "gw-easymesh": "IPv4/IPv6 router with one or more WAN access technologies and EasyMesh Wi-Fi controller + agent features.",
    "ext-opensync": "Wi-Fi extender device based on OpenSync technology; supports Wi-Fi AP fronthaul and Wi-Fi/Ethernet backhaul.",
}

STATUS_STYLE = {
    "validated": {"bg": "#d1fae5", "fg": "#065f46", "label": "Validated"},
    "partial": {"bg": "#fef3c7", "fg": "#92400e", "label": "Partial"},
    "not-started": {"bg": "#e5e7eb", "fg": "#374151", "label": "Not started"},
}


def load_profiles(profiles_dir: Path) -> list[dict]:
    profiles = []
    for path in sorted(profiles_dir.glob("*.json")):
        if path.name == "hw-compat.schema.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if "profileId" not in data:
            continue
        profiles.append(data)
    order = {pid: i for i, pid in enumerate(PROFILE_DEFINITIONS)}
    profiles.sort(key=lambda p: order.get(p["profileId"], 999))
    return profiles


def status_pill(status: str) -> str:
    s = STATUS_STYLE.get(status, STATUS_STYLE["not-started"])
    return f'<span class="pill" style="background:{s["bg"]};color:{s["fg"]};border-radius:999px;">{esc(s["label"])}</span>'


def render_coverage_table(profiles: list[dict]) -> str:
    rows = []
    for p in profiles:
        in_scope = p["validationStatus"] != "not-started"
        coverage = "In scope (this document)" if in_scope else "Defined \u2014 not covered in this revision"
        definition = PROFILE_DEFINITIONS.get(p["profileId"], "")
        rows.append(
            "<tr><td>" + esc(p["profileName"]) + "</td><td>" + esc(coverage) + "</td><td>" + esc(definition) + "</td></tr>"
        )
    return (
        '<table class="def-table"><thead><tr><th>Device Profile</th><th>Coverage in this Spec</th>'
        "<th>Definition</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


def render_minimums_table(in_scope: list[dict]) -> str:
    rows = []
    for p in in_scope:
        cpu, mem, sto, ref = p["cpu"], p["memory"], p["storage"], p["referenceDevice"]
        cpu_txt = f'{esc(cpu["family"])}, \u2265 {esc(cpu["minClockGHz"])} GHz'
        cores_txt = str(cpu["minCores"]) + (f' ({esc(cpu["coreTopology"])})' if cpu.get("coreTopology") else "")
        ref_txt = esc(ref["name"]) + (f', {esc(ref["soc"])}' if ref.get("soc") else "")
        rows.append(
            "<tr><td>" + esc(p["profileName"]) + "</td><td class=\"mono\">" + cpu_txt + "</td><td>" + cores_txt +
            "</td><td>" + esc(mem["minRamMB"]) + " MB</td><td>" + esc(sto["minFlashMB"]) + " MB (" + esc(sto["type"]) +
            ")</td><td>" + ref_txt + "</td></tr>"
        )
    return (
        '<table class="def-table"><thead><tr><th>Profile</th><th>CPU (min.)</th><th>Cores</th>'
        "<th>RAM (min.)</th><th>Flash (min.)</th><th>Reference Device</th></tr></thead><tbody>"
        + "".join(rows) + "</tbody></table>"
    )


def render_connectivity_row(label: str, value) -> str:
    if isinstance(value, bool):
        text = "Required" if value else "Not required"
    elif isinstance(value, list):
        text = ", ".join(str(v) for v in value) if value else "\u2014"
    else:
        text = str(value) if value not in (None, "") else "\u2014"
    return f'<tr><td class="mono" style="white-space:nowrap;">{esc(label)}</td><td>{esc(text)}</td></tr>'


def render_peripheral_block(title: str, fields: dict) -> str:
    rows = "".join(render_connectivity_row(k, v) for k, v in fields.items())
    return (
        '<div style="margin-bottom:14px;"><div style="font-weight:600; font-size:0.85rem; margin-bottom:4px;">'
        + esc(title) + '</div><table class="def-table" style="font-size:0.85rem;"><tbody>' + rows + "</tbody></table></div>"
    )


def render_profile_card(p: dict) -> str:
    cpu, mem, sto, ref, per = p["cpu"], p["memory"], p["storage"], p["referenceDevice"], p["peripherals"]
    conn = per.get("connectivity", {})

    blocks = [
        render_peripheral_block("WAN", conn.get("wan", {})),
        render_peripheral_block("LAN", conn.get("lan", {})),
        render_peripheral_block("Wi-Fi", conn.get("wifi", {})),
        render_peripheral_block("EasyMesh", conn.get("easyMesh", {})),
        render_peripheral_block("Bluetooth / IoT", conn.get("bluetoothIot", {})),
        render_peripheral_block("Storage Interface", per.get("storageInterface", {})),
        render_peripheral_block("Media Tuner", per.get("mediaTuner", {})),
        render_peripheral_block("Diagnostics", per.get("diagnostics", {})),
    ]

    last_validated = ""
    if p.get("lastValidated") and p["lastValidated"] != "n/a":
        last_validated = f'last validated {esc(p["lastValidated"])}'

    ref_line = esc(ref["name"])
    if ref.get("soc"):
        ref_line += f' ({esc(ref["soc"])})'

    return (
        '<div class="card" style="max-width:none; margin-bottom:20px;">'
        '<div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:10px;">'
        f'<h3 style="margin:0;">{esc(p["profileName"])}</h3>'
        f'{status_pill(p["validationStatus"])}'
        f'<span style="font-size:0.78rem; color:var(--muted);">{last_validated}</span>'
        '</div>'
        '<div class="hwcompat-summary">'
        f'<span><strong>CPU:</strong> {esc(cpu["family"])} ({esc(cpu["architecture"])}), \u2265 {esc(cpu["minClockGHz"])} GHz, {esc(cpu["minCores"])} cores</span>'
        f'<span><strong>RAM:</strong> {esc(mem["minRamMB"])} MB</span>'
        f'<span><strong>Flash:</strong> {esc(sto["minFlashMB"])} MB ({esc(sto["type"])})</span>'
        f'<span><strong>Reference device:</strong> {ref_line}</span>'
        '</div>'
        '<div class="subhead" style="margin-top:18px;">Peripheral Requirements</div>'
        '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:14px;">'
        + "".join(blocks) +
        '</div></div>'
    )


def render_not_covered_list(profiles: list[dict]) -> str:
    rows = []
    for p in profiles:
        rows.append(
            "<tr><td>" + esc(p["profileName"]) + "</td><td>" + esc(PROFILE_DEFINITIONS.get(p["profileId"], ""))
            + "</td><td>" + esc(p.get("coverageNote", "")) + "</td></tr>"
        )
    return (
        '<table class="def-table"><thead><tr><th>Device Profile</th><th>Definition</th>'
        "<th>Status</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


EXTRA_CSS = """
<style>
  .hwcompat-summary { display: flex; flex-wrap: wrap; gap: 8px 22px; font-size: 0.85rem; color: var(--muted); }
  .hwcompat-summary strong { color: var(--ink); font-weight: 600; }
</style>
"""


def build_page(profiles_dir: Path) -> str:
    profiles = load_profiles(profiles_dir)
    in_scope = [p for p in profiles if p["validationStatus"] != "not-started"]
    not_covered = [p for p in profiles if p["validationStatus"] == "not-started"]

    body = f'''
{render_hero("Hardware Compatibility", "Hardware Compatibility Spec",
    "Minimum CPU, RAM, flash, and required peripheral hardware per RDK-B device profile, "
    "validated against a BPI-R4 (MT7988/Filogic) reference platform.",
    compact=True, visual_key="hwcompat")}

<section class="tight-top">
  <div class="section-head"><h2>Device Profile Coverage</h2>
    <p>The RDK-B Component List 2026 defines seven device profiles; this revision of the spec covers two.</p>
  </div>
  {render_coverage_table(profiles)}
</section>

<section class="tight-top">
  <div class="section-head"><h2>Minimum CPU, Memory, and Flash Storage</h2></div>
  {render_minimums_table(in_scope)}
</section>

<section class="tight-top">
  <div class="section-head"><h2>Profile Details</h2>
    <p>Full CPU/memory/flash minimums and peripheral requirements for each in-scope profile.</p>
  </div>
  {"".join(render_profile_card(p) for p in in_scope)}
</section>

<section class="tight-top">
  <div class="section-head"><h2>Not Yet Covered</h2>
    <p>Defined in the RDK-B Component List 2026 but out of scope for this revision.</p>
  </div>
  {render_not_covered_list(not_covered)}
</section>
'''
    head_extra = "<title>Hardware Compatibility Spec \u2014 RDK-B Core Broadband</title>\n" + EXTRA_CSS
    return render_page("hwcompat", head_extra, body)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles-dir", default="docs")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "hardware-compatibility.html"
    path.write_text(build_page(Path(args.profiles_dir)), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
