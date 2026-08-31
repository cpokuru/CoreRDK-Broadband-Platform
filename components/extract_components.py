"""Extract simple, single-table component lists from RDK-B_Component_List_2026.xlsx.

Three modes:

  core         -> components tagged CORE (common to every profile) plus components
                  that are Required in every profile they apply to. Tiers:
                  'common-core' vs 'required'.

  profile      -> all components that apply (Required or Optional, i.e. not 'n/a')
                  to a single device profile column, e.g. "EthWAN WiFi Router".
                  Tiers: 'required' vs 'optional'.

  all-profiles -> runs 'profile' for every column in PROFILE_COLUMNS in one go,
                  writing one <profile>-components.json per profile into the
                  current directory (see PROFILE_FILENAMES for exact names).

Usage:
    python3 extract_components.py core \
        --xlsx RDK-B_Component_List_2026.xlsx --out core-b-components.json

    python3 extract_components.py profile "EthWAN WiFi Router" \
        --xlsx RDK-B_Component_List_2026.xlsx --out ethwan-router-components.json

    python3 extract_components.py all-profiles \
        --xlsx RDK-B_Component_List_2026.xlsx --show-core
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import openpyxl

SCHEMA_VERSION = "1.0"

PROFILE_COLUMNS = [
    "Modem\n/ONU",
    "EthWAN WiFi Router",
    "GW",
    "GW\nOpenSync",
    "GW\nEasyMesh",
    "EXT\nOpenSync",
    "EXT\nEasyMesh",
]

# Output filename per profile column, for the "all-profiles" mode.
# EthWAN WiFi Router keeps its existing name since components/index.html and
# components/gen_components_page.py already depend on it by that exact
# filename; every other profile follows <profile-id>-components.json.
PROFILE_FILENAMES = {
    "Modem\n/ONU": "modem-onu-components.json",
    "EthWAN WiFi Router": "ethwan-router-components.json",
    "GW": "gw-components.json",
    "GW\nOpenSync": "gw-opensync-components.json",
    "GW\nEasyMesh": "gw-easymesh-components.json",
    "EXT\nOpenSync": "ext-opensync-components.json",
    "EXT\nEasyMesh": "ext-easymesh-components.json",
}

TIERS = {
    "common-core": {"id": "common-core", "label": "Common Core", "color": "gold"},
    "required": {"id": "required", "label": "Required", "color": "blue"},
    "optional": {"id": "optional", "label": "Optional", "color": "gray"},
}


def _rows(ws):
    """Yield (subsystem, name, url, core_flag, profile_values) with subsystem forward-filled."""
    headers = [c.value for c in ws[1]]
    name_idx = headers.index("Component Repo")
    subsys_idx = headers.index("Subsystem")
    url_idx = headers.index("Github Link")
    core_idx = headers.index("Core Components")
    profile_idxs = [headers.index(c) for c in PROFILE_COLUMNS]

    cur_subsys = None
    for row in ws.iter_rows(min_row=3, values_only=True):
        if row[name_idx] is None and row[subsys_idx] is None:
            continue
        if row[subsys_idx]:
            cur_subsys = row[subsys_idx]
        name = row[name_idx]
        if name is None:
            continue
        if isinstance(name, str):
            name = name.strip()
        url = row[url_idx]
        if isinstance(url, str):
            # A handful of rows list multiple links newline-separated; keep the first.
            url = url.strip().splitlines()[0].strip() or None
        yield {
            "subsystem": cur_subsys,
            "name": name,
            "url": url,
            "is_core": row[core_idx] == "CORE",
            "profile_values": {PROFILE_COLUMNS[i]: row[profile_idxs[i]] for i in range(len(PROFILE_COLUMNS))},
        }


def extract_core(ws) -> list[dict]:
    out = []
    for r in _rows(ws):
        vals = [v for v in r["profile_values"].values() if v not in (None, "n/a")]
        required_everywhere = bool(vals) and all(v == "Required" for v in vals)
        if r["is_core"] or required_everywhere:
            out.append({
                "name": r["name"],
                "category": r["subsystem"],
                "tier": "common-core" if r["is_core"] else "required",
                "url": r["url"],
            })
    return out


def extract_profile(ws, profile: str, required_only: bool = False, show_core: bool = False) -> list[dict]:
    """All components that apply to a single device profile column.

    show_core=False (default): tiers are 'required' / 'optional' only, matching
        the profile column value verbatim (today's simple pages).
    show_core=True: components flagged CORE ('Core Components' == 'CORE') are
        tagged 'common-core' instead of their raw Required/Optional value, so
        the page distinguishes Common Core vs Required vs Optional. Ignored
        when required_only=True (core components are always required-everywhere
        by definition, so they'd show as Required either way).
    """
    if profile not in PROFILE_COLUMNS:
        raise SystemExit(f"Unknown profile {profile!r}. Choose from: {PROFILE_COLUMNS}")
    wanted = ("Required",) if required_only else ("Required", "Optional")
    out = []
    for r in _rows(ws):
        v = r["profile_values"][profile]
        if v not in wanted:
            continue
        tier = "common-core" if (show_core and not required_only and r["is_core"]) else v.lower()
        out.append({
            "name": r["name"],
            "category": r["subsystem"],
            "tier": tier,
            "url": r["url"],
        })
    return out


def build_payload(components: list[dict], title: str, subtitle: str, tier_ids: list[str]) -> dict:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "title": title,
        "subtitle": subtitle,
        "tiers": [TIERS[t] for t in tier_ids],
        "components": components,
    }


def build_profile_payload(ws, profile: str, required_only: bool = False, show_core: bool = False) -> tuple[list[dict], dict]:
    """Extract + build the payload for one profile column. Shared by the
    'profile' and 'all-profiles' CLI modes so their output is identical."""
    components = extract_profile(ws, profile, required_only=required_only, show_core=show_core)
    if required_only:
        tier_ids = ["required"]
    elif show_core:
        tier_ids = ["common-core", "required", "optional"]
    else:
        tier_ids = ["required", "optional"]
    # Some profile column headers in the xlsx contain an embedded newline
    # (e.g. "GW\nOpenSync", wrapped for column width) -- that's needed
    # verbatim for the exact-match lookup in extract_profile(), but reads as
    # a broken mid-sentence line break in a title/subtitle string, so
    # normalize to a single space for display purposes only.
    profile_display = " ".join(profile.split())
    subtitle = f"Components required for the {profile_display} device profile." if required_only \
        else f"Components for the {profile_display} device profile: Common Core, Required, and Optional." if show_core \
        else f"Components that apply to the {profile_display} device profile."
    payload = build_payload(
        components,
        title=f"RDK-B {profile_display} Components",
        subtitle=subtitle,
        tier_ids=tier_ids,
    )
    return components, payload


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="mode", required=True)

    core_p = sub.add_parser("core")
    core_p.add_argument("--xlsx", default="RDK-B_Component_List_2026.xlsx")
    core_p.add_argument("--out", default="core-b-components.json")

    prof_p = sub.add_parser("profile")
    prof_p.add_argument("profile", help='e.g. "EthWAN WiFi Router"')
    prof_p.add_argument("--xlsx", default="RDK-B_Component_List_2026.xlsx")
    prof_p.add_argument("--out", default="profile-components.json")
    prof_p.add_argument("--required-only", action="store_true", help="Omit Optional components; show only Required.")
    prof_p.add_argument("--show-core", action="store_true", help="Tag CORE components as 'Common Core' instead of Required/Optional.")

    all_p = sub.add_parser("all-profiles", help="Run 'profile' for every profile column, writing one file each into the current directory.")
    all_p.add_argument("--xlsx", default="RDK-B_Component_List_2026.xlsx")
    all_p.add_argument("--required-only", action="store_true", help="Omit Optional components; show only Required.")
    all_p.add_argument("--show-core", action="store_true", help="Tag CORE components as 'Common Core' instead of Required/Optional.")

    args = p.parse_args()
    wb = openpyxl.load_workbook(Path(args.xlsx), data_only=True)
    ws = wb["Components"]

    if args.mode == "core":
        components = extract_core(ws)
        payload = build_payload(
            components,
            title="Core RDK-B Components",
            subtitle="Components common to every RDK-B device profile, or required wherever they apply.",
            tier_ids=["common-core", "required"],
        )
        Path(args.out).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {args.out} ({len(components)} components)")

    elif args.mode == "profile":
        components, payload = build_profile_payload(ws, args.profile, required_only=args.required_only, show_core=args.show_core)
        Path(args.out).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {args.out} ({len(components)} components)")

    else:  # all-profiles
        for profile in PROFILE_COLUMNS:
            out_name = PROFILE_FILENAMES[profile]
            components, payload = build_profile_payload(ws, profile, required_only=args.required_only, show_core=args.show_core)
            Path(out_name).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  {out_name:35} {len(components):3} components  ({' '.join(profile.split())})")
        print(f"Wrote {len(PROFILE_COLUMNS)} profile component files.")


if __name__ == "__main__":
    main()
