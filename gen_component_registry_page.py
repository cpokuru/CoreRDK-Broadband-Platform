"""One-purpose generator for component-registry.html.

Renders the shared page shell + a client-side loader (render_stub_page in
layout.py) that tries component-registry.json then component-registry.xml
(same folder) at runtime and renders whatever it finds -- a table if it's
a flat array of same-shaped records, a formatted tree otherwise. Until
either file exists, the page shows a clean "no data published yet" empty
state instead of breaking.

Mandatory registry fields and lifecycle states are already defined and
TAB-approved -- see docs/RDK-B_CoreRDK_Spec_MVP(InternalReference)_v1.1.pdf
section 7.3.2 (Component Registry) and 7.3.3 (Component Lifecycle States).
This script doesn't encode those fields -- it just renders whatever
component-registry.json contains, so the field list lives in one place
(the data file / whatever produces it), not here.

Usage:
    python3 gen_component_registry_page.py --out-dir .
"""
from __future__ import annotations

import argparse
from pathlib import Path

from layout import render_stub_page

PAGE = {
    "active_id": "component-registry",
    "slug": "component-registry",
    "eyebrow": "Component Registry",
    "title": "Component Registry",
    "lede": "The authoritative record of every RDK-B component — owner, lifecycle state, "
            "HAL contract, TR-181 model, and dependencies, per §7.3.2 of the Core RDK "
            "Broadband Specification.",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / f"{PAGE['slug']}.html"
    path.write_text(render_stub_page(PAGE), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
