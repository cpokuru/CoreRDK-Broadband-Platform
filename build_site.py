"""Single entry point for the whole CoreRDK-Broadband-Specification site.

Regenerates the landing page and every *.json data file from source (the
spec PDF and the component xlsx). components/index.html and
components/full-list.html are static templates, committed once — they load
their data at runtime in the browser instead of having it baked in at build
time. This script never rewrites either of them.

Order of operations (each step's output feeds the next):

  1. docs/*.pdf   --(extract_spec_content.py)-->  docs/spec-content.json
  2. docs/spec-content.json  --(gen_base_page.py)-->  index.html (About Core RDK Broadband —
                                                       About comes from docs/about-content.json,
                                                       Architecture comes from spec-content.json)
  3. docs/*.xlsx  --(gen_html.py --sync-only)-->  components/RDK-B_Component_List_2026.xlsx
                                                   (a synced copy — full-list.html loads THIS xlsx
                                                    directly client-side via SheetJS, same-directory
                                                    fetch, so the file has to physically sit next to it)
  4. docs/*.xlsx  --(extract_components.py)-->  components/ethwan-router-components.json
                                                 (fetched at runtime by the static components/index.html)

Both source files (the spec PDF and the component xlsx) live together in
docs/. components/ holds the generator scripts, the two static HTML
templates, and the synced xlsx + generated JSON — no hand-maintained data.

Usage:
    python3 build_site.py
    python3 build_site.py --profile "GW"          # regenerate the JSON for a different profile
    python3 build_site.py --skip-pdf               # reuse existing docs/spec-content.json
    python3 build_site.py --skip-xlsx               # reuse existing components/* data
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
COMPONENTS = ROOT / "components"


def find_one(directory: Path, pattern: str) -> Path:
    matches = sorted(directory.glob(pattern))
    if not matches:
        raise SystemExit(f"No file matching {pattern!r} found in {directory}/")
    if len(matches) > 1:
        print(f"  note: multiple matches for {pattern!r} in {directory}/, using the newest: "
              f"{max(matches, key=lambda p: p.stat().st_mtime).name}")
        return max(matches, key=lambda p: p.stat().st_mtime)
    return matches[0]


def run(cmd: list[str], cwd: Path) -> None:
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    subprocess.run([sys.executable if cmd[0] == "python3" else cmd[0], *cmd[1:]], cwd=cwd, check=True)


def step_pdf_to_json() -> None:
    print("\n[1/4] Spec PDF -> docs/spec-content.json")
    pdf = find_one(DOCS, "*.pdf")
    run(["python3", "extract_spec_content.py", str(pdf.relative_to(ROOT)), "--out", "docs/spec-content.json"], cwd=ROOT)


def step_json_to_base_html() -> None:
    print("\n[2/4] docs/spec-content.json -> index.html")
    run(["python3", "gen_base_page.py", "docs/spec-content.json", "docs/about-content.json", "--out-dir", "."], cwd=ROOT)


def step_sync_workbook_for_full_list() -> None:
    print("\n[3/4] Component xlsx -> components/RDK-B_Component_List_2026.xlsx (synced copy for full-list.html)")
    run(["python3", "gen_html.py", "--sync-only"], cwd=COMPONENTS)


def step_xlsx_to_profile_json(profile: str) -> None:
    print(f"\n[4/4] Component xlsx -> components/ethwan-router-components.json (profile: {profile!r})")
    xlsx = find_one(DOCS, "*.xlsx")
    xlsx_rel_from_components = Path("..") / xlsx.relative_to(ROOT)
    run([
        "python3", "extract_components.py", "profile", profile,
        "--xlsx", str(xlsx_rel_from_components),
        "--out", "ethwan-router-components.json",
        "--show-core",
    ], cwd=COMPONENTS)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="EthWAN WiFi Router", help="Device profile for components/index.html")
    ap.add_argument("--skip-pdf", action="store_true", help="Reuse existing docs/spec-content.json instead of re-parsing the PDF")
    ap.add_argument("--skip-xlsx", action="store_true", help="Skip both xlsx-driven steps")
    args = ap.parse_args()

    print("Building CoreRDK-Broadband-Docs-Base")
    print("=" * 40)

    if not args.skip_pdf:
        step_pdf_to_json()
    else:
        print("\n[1/4] Skipped (--skip-pdf) — reusing docs/spec-content.json")
    step_json_to_base_html()

    if not args.skip_xlsx:
        step_sync_workbook_for_full_list()
        step_xlsx_to_profile_json(args.profile)
    else:
        print("\n[3/4] and [4/4] Skipped (--skip-xlsx)")

    print("\nDone. Generated:")
    print("  index.html")
    print("  docs/spec-content.json")
    if not args.skip_xlsx:
        print("  components/RDK-B_Component_List_2026.xlsx  (synced copy, read by full-list.html)")
        print("  components/ethwan-router-components.json  (read by components/index.html)")
    print("\ncomponents/full-list.html and components/index.html are static — not")
    print("touched by this script. Regenerate full-list.html with plain")
    print("'python3 gen_html.py' (no --sync-only) only if the page design itself")
    print("changes, not the data. components/index.html has no generator at all")
    print("by design; edit it directly if its design needs to change.")


if __name__ == "__main__":
    main()
