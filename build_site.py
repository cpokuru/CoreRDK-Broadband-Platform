"""Single entry point for the whole CoreRDK-Broadband-Specification site.

Regenerates every generated HTML/JSON file in the repo from its source file
(the spec PDF and the component xlsx). Nothing generated is hand-edited —
if a source file changes, rerun this script and commit the diff.

Order of operations (each step's output feeds the next):

  1. docs/*.pdf   --(extract_spec_content.py)-->  docs/spec-content.json
  2. docs/spec-content.json  --(gen_base_page.py)-->  index.html   (site landing page)
  3. docs/*.xlsx  --(gen_html.py)-->  components/full-list.html
                                      components/RDK-B_Component_List_2026.xlsx  (copy, so the
                                      browser's client-side fetch() finds it next to the page)
  4. docs/*.xlsx  --(build_simple_page.py)-->  components/index.html
                                                components/ethwan-router-components.json

Both source files (the spec PDF and the component xlsx) live together in
docs/. components/ holds only the generator scripts, the generated output,
and a synced copy of the xlsx (full-list.html loads it client-side via
SheetJS, so it must be co-located with the page it's served alongside — see
gen_html.py's sync_workbook()). Nothing in components/ is hand-maintained.

Usage:
    python3 build_site.py
    python3 build_site.py --profile "GW"          # build a different profile page
    python3 build_site.py --skip-pdf               # reuse existing docs/spec-content.json
    python3 build_site.py --skip-xlsx               # reuse existing components json/html
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
    run(["python3", "gen_base_page.py", "docs/spec-content.json", "--out", "index.html"], cwd=ROOT)


def step_xlsx_to_full_workbook() -> None:
    print("\n[3/4] Component xlsx -> components/full-list.html (+ synced xlsx copy)")
    run(["python3", "gen_html.py"], cwd=COMPONENTS)


def step_xlsx_to_profile_page(profile: str) -> None:
    print(f"\n[4/4] Component xlsx -> components/index.html (profile: {profile!r})")
    xlsx = find_one(DOCS, "*.xlsx")
    xlsx_rel_from_components = Path("..") / xlsx.relative_to(ROOT)
    run([
        "python3", "build_simple_page.py", "profile", profile,
        "--xlsx", str(xlsx_rel_from_components),
        "--json-out", "ethwan-router-components.json",
        "--html-out", "index.html",
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
        step_xlsx_to_full_workbook()
        step_xlsx_to_profile_page(args.profile)
    else:
        print("\n[3/4] and [4/4] Skipped (--skip-xlsx)")

    print("\nDone. Generated:")
    print("  index.html")
    print("  docs/spec-content.json")
    if not args.skip_xlsx:
        print("  components/full-list.html")
        print("  components/RDK-B_Component_List_2026.xlsx  (synced copy)")
        print("  components/index.html")
        print("  components/ethwan-router-components.json")


if __name__ == "__main__":
    main()
