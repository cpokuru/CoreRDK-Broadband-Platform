"""Extract structured content from the RDK-B Core Broadband spec PDF for the
CoreRDK-Broadband-Docs-Base site.

What gets pulled automatically from the PDF (page numbers are located by
searching for each section's heading text, not hardcoded, so a reflowed
future version still resolves correctly as long as headings are unchanged):

  - platform definition + intro paragraph      (Section 2)
  - platform origins timeline                  (Section 2.2, bullet list)
  - licensing bullets                          (Section 2.4)
  - test suite ownership table                 (Section 2.5, clean PDF table)
  - governance standards table                 (Section 7.1.1 + 7.1.2, clean PDF table)
  - industry standards conformance tables       (Section 7.1.3.x, clean PDF tables)

What is NOT auto-extracted:
  - The Five-Tier Model table (Section 2.3). Its source table has no cell
    borders and heavy multi-line wrapping, so both pdftotext -layout and
    pdfplumber's table/word-clustering reflow it out of row/column order.
    Its five rows change only on major architecture revisions, so it is kept
    as a small curated constant (FIVE_TIER) below instead of a fragile
    parser. If a future spec version restructures this table with real
    borders, this can be automated the same way as the others.

Usage:
    python3 extract_spec_content.py RDK-B_CoreRDK_Spec_MVP_v1_0.pdf --out spec-content.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

import pdfplumber

SCHEMA_VERSION = "1.0"

# Curated — see module docstring for why this one table isn't auto-parsed.
FIVE_TIER = [
    {"tier": 5, "layer": "Cloud / ACS", "note": "Top",
     "description": "Operator cloud: ACS, USP Controller, xConf, WebConfig, Telemetry backends, Crash collection, Log aggregation."},
    {"tier": 4, "layer": "Management Protocols", "note": "",
     "description": "parodus/WebPA, usp-pa-vendor-rdk, tr069-protocol-agent, xconf-client, WebconfigFramework, T2 telemetry."},
    {"tier": 3, "layer": "RDK-B Middleware", "note": "",
     "description": "RDK-B components: OneWiFi, wan-manager, dhcp-manager, DSM, Dobby, BartonCore, all feature components. All communicate via RBUS."},
    {"tier": 2, "layer": "HAL / BSP", "note": "",
     "description": "rdkb-halif-* interface libraries and vendor BSP. Boundary between RDK-B middleware and SoC firmware."},
    {"tier": 1, "layer": "Hardware / SoC", "note": "Base",
     "description": "Physical silicon: SoC CPU, Wi-Fi radio, modem chipset, Ethernet switch, Flash/RAM."},
]


def pdftotext(path: Path, first: int, last: int) -> str:
    out = subprocess.run(
        ["pdftotext", "-layout", "-f", str(first), "-l", str(last), str(path), "-"],
        capture_output=True, text=True, check=True,
    )
    return out.stdout


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def find_page_with(pdf: "pdfplumber.PDF", needle: str, start: int = 10) -> int:
    """Return 0-indexed page number of the first page containing `needle`,
    skipping the front matter (TOC / conventions pages) where section titles
    are often echoed in cross-reference tables and would false-positive."""
    for i, page in enumerate(pdf.pages):
        if i < start:
            continue
        text = page.extract_text() or ""
        if needle in text:
            return i
    raise SystemExit(f"Could not locate a page containing: {needle!r}")


def extract_overview(pdf, path: Path) -> dict:
    p_what = find_page_with(pdf, "Platform Definition")
    text = pdftotext(path, p_what + 1, p_what + 1)

    definition = norm(text.split("Platform Definition", 1)[1].split("RDK-B sits between", 1)[0])
    intro = "RDK-B sits between " + norm(text.split("RDK-B sits between", 1)[1].split("2.1 What are RDK-B", 1)[0])

    p_origins = find_page_with(pdf, "2.2 Platform Origins")
    origin_text = pdftotext(path, p_origins + 1, p_origins + 1)
    origin_block = origin_text.split("2.2 Platform Origins", 1)[1].split("2.3 Platform Architecture", 1)[0]
    timeline = []
    for m in re.finditer(r"•\s*([\d–]{4,9})\s*—\s*(.+)", origin_block):
        year, desc = m.group(1).strip(), norm(m.group(2))
        timeline.append({"year": year, "text": desc.rstrip(";").strip()})

    p_lic = find_page_with(pdf, "2.4 Licensing")
    lic_text = pdftotext(path, p_lic + 1, p_lic + 1)
    lic_block = lic_text.split("2.4 Licensing", 1)[1]
    lic_block = lic_block.split("2.5 RDK-B High level", 1)[0] if "2.5 RDK-B High level" in lic_block else lic_block
    licensing = [norm(m) for m in re.findall(r"•\s*(.+)", lic_block) if norm(m)]

    return {
        "definition": definition,
        "intro": intro,
        "origins_timeline": timeline,
        "licensing": licensing,
    }


def extract_test_suites(pdf) -> list[dict]:
    p = find_page_with(pdf, "Test Suite") if False else None
    # Search near the layering section specifically (the phrase "Test Suite" alone
    # is too generic to trust find_page_with on its own).
    for i, page in enumerate(pdf.pages):
        if i < 10:
            continue
        text = page.extract_text() or ""
        if "RDK Platform Test Suite" in text and "HAL Spec Owner" in text:
            p = i
            break
    if p is None:
        raise SystemExit("Could not locate the test suite ownership table.")
    for t in pdf.pages[p].find_tables():
        rows = t.extract()
        if rows and rows[0][:3] == ["Test Suite", "Definition", "Owner"]:
            out = []
            for row in rows[1:]:
                out.append({"name": norm(row[0] or ""), "definition": norm(row[1] or ""), "owner": norm(row[2] or "")})
            return out
    raise SystemExit("Found the test suite page but not the table on it.")


def extract_governance_standards(pdf) -> list[dict]:
    """Section 7.1.1 + 7.1.2 — 'Standard / Requirements' two-column tables, spread
    across a few consecutive pages. Each row is tagged with which of the two
    sub-sections it belongs to (detected from the PDF's own "7.1.2" heading,
    not a hardcoded row count) so callers can split architecture standards
    (7.1.1) from technical/process standards (7.1.2) without re-parsing."""
    start = find_page_with(pdf, "7.1.1 Process")
    out = []
    p = start
    consecutive_misses = 0
    section = "7.1.1"
    while consecutive_misses < 2 and p < len(pdf.pages):
        page = pdf.pages[p]
        text = page.extract_text() or ""
        if "7.1.3 Industry Standards" in text:
            break
        if re.search(r"\b7\.1\.2\b", text):
            section = "7.1.2"
        found_table = False
        for t in page.find_tables():
            rows = t.extract()
            if rows and rows[0][:2] == ["Standard", "Requirements"]:
                found_table = True
                for row in rows[1:]:
                    name, req = norm(row[0] or ""), norm(row[1] or "")
                    if name and req:
                        out.append({"name": name, "requirement": req, "section": section})
        consecutive_misses = 0 if found_table else consecutive_misses + 1
        p += 1
    return out


def _is_header_cell(c: str) -> bool:
    key = re.sub(r"\s*/\s*$", "", c.lower().strip())
    key = re.sub(r"\s+", " ", key)
    return key in {"standard", "standard / body", "body", "applies to", "note"}


def _parse_standards_table(rows: list[list]) -> list[dict]:
    """Given a raw pdfplumber-extracted table, locate the 'Standard / Body |
    Applies To | Note' header — which may be split across several ragged
    leading rows and/or include a stray empty column, as happens for the
    7.1.3.1 table — then extract the data rows that follow. Returns [] if
    this doesn't look like a standards table at all."""
    if not rows:
        return []
    ncols = max(len(r) for r in rows)
    norm_rows = [list(r) + [None] * (ncols - len(r)) for r in rows]

    col = {}  # "standard" | "applies_to" | "note" -> column index
    data_start = None
    for ri, row in enumerate(norm_rows):
        cells = [norm(c or "") for c in row]
        if not any(cells):
            continue  # blank row inside a ragged header block; keep scanning
        is_header_row = any(_is_header_cell(c) for c in cells if c)
        if is_header_row:
            for ci, c in enumerate(cells):
                key = c.lower().replace(" ", "")
                if not key:
                    continue
                if "standard" in key or key == "body":
                    col.setdefault("standard", ci)
                elif "appliesto" in key:
                    col.setdefault("applies_to", ci)
                elif "note" in key:
                    col.setdefault("note", ci)
            continue
        data_start = ri
        break

    if data_start is None or "standard" not in col:
        return []

    out = []
    for row in norm_rows[data_start:]:
        cells = [norm(c or "") for c in row]
        std = cells[col["standard"]] if col["standard"] < len(cells) else ""
        if not std:
            continue
        applies = cells[col["applies_to"]] if "applies_to" in col and col["applies_to"] < len(cells) else ""
        note = cells[col["note"]] if "note" in col and col["note"] < len(cells) else ""
        out.append({"standard": std, "applies_to": applies, "note": note})
    return out


def extract_industry_standards(pdf) -> list[dict]:
    """Section 7.1.3.x — multiple clean 'Standard / Body | Applies To | Note'
    tables, one per sub-domain (remote management, wireless, IoT, etc.).
    Category is assigned by vertical position on the page (nearest heading
    above each table), not just "last heading seen on this page", since
    several sub-tables can share a page. Category carries over across a page
    break if a table starts before any heading appears on its own page."""
    start = find_page_with(pdf, "7.1.3 Industry Standards Conformance")
    out = []
    p = start
    last_category = None
    while p < len(pdf.pages):
        page = pdf.pages[p]
        text = page.extract_text() or ""
        if p > start and re.search(r"^\s*7\.2 ", text, re.M):
            break

        words = page.extract_words()
        headings = []  # (top, category_text)
        full_text = " ".join(w["text"] for w in sorted(words, key=lambda w: (w["top"], w["x0"])))
        for m in re.finditer(r"7\.1\.3\.(\d+)\.", full_text):
            tag = f"7.1.3.{m.group(1)}."
            for w in words:
                if w["text"] == tag or w["text"].startswith(f"7.1.3.{m.group(1)}"):
                    # heading may wrap onto a second line; grab this line plus
                    # the next one, then keep only the clause before any
                    # parenthetical aside so long asides don't bloat the label.
                    band = [x for x in words if w["top"] - 2 <= x["top"] <= w["top"] + 16]
                    band.sort(key=lambda x: (x["top"], x["x0"]))
                    heading_text = " ".join(x["text"] for x in band)
                    heading_text = re.sub(r"^7\.1\.3\.\d+\.\s*", "", heading_text).strip()
                    heading_text = heading_text.split(" (")[0].strip()
                    headings.append((w["top"], heading_text))
                    break

        for t in page.find_tables():
            rows = t.extract()
            records = _parse_standards_table(rows)
            if not records:
                continue
            table_top = t.bbox[1]
            category = last_category
            for h_top, h_text in headings:
                if h_top <= table_top + 5:
                    category = h_text
            for rec in records:
                out.append({
                    "category": category,
                    "standard": rec["standard"],
                    "applies_to": rec["applies_to"],
                    "note": rec["note"],
                })
        if headings:
            last_category = headings[-1][1]
        p += 1
        if p - start > 8:  # safety bound
            break
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--out", default="spec-content.json")
    args = ap.parse_args()

    path = Path(args.pdf)
    with pdfplumber.open(path) as pdf:
        overview = extract_overview(pdf, path)
        test_suites = extract_test_suites(pdf)
        governance = extract_governance_standards(pdf)
        industry = extract_industry_standards(pdf)

    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "sourcePdf": path.name,
        "overview": overview,
        "five_tier": FIVE_TIER,
        "test_suites": test_suites,
        "governance_standards": governance,
        "industry_standards": industry,
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {args.out}")
    print(f"  origins_timeline: {len(overview['origins_timeline'])} entries")
    print(f"  licensing: {len(overview['licensing'])} entries")
    print(f"  test_suites: {len(test_suites)} entries")
    print(f"  governance_standards: {len(governance)} entries")
    print(f"  industry_standards: {len(industry)} entries")


if __name__ == "__main__":
    main()
