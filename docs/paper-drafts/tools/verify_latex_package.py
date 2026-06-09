#!/usr/bin/env python3
"""Static QA for the SAQT LNCS/Overleaf draft package.

The current environment does not provide pdflatex/bibtex, so this script checks
the parts that can be verified locally: citation closure, BibTeX synchronization,
graphics references, figure PDF hashes, and Overleaf zip synchronization.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PAPER_ROOT = REPO_ROOT / "docs" / "paper-drafts"
LATEX_ROOT = PAPER_ROOT / "latex"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def latex_files() -> list[Path]:
    return [LATEX_ROOT / "main.tex", *sorted((LATEX_ROOT / "sections").glob("*.tex"))]


def extract_cite_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for match in re.finditer(r"\\cite\{([^}]*)\}", text):
        for key in match.group(1).split(","):
            key = key.strip()
            if key:
                keys.add(key)
    return keys


def extract_bib_keys(text: str) -> set[str]:
    return set(re.findall(r"^@[A-Za-z]+\{([^,\s]+),", text, flags=re.MULTILINE))


def extract_graphics(text: str) -> set[str]:
    return set(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", text))


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    tex_text = "\n".join(read_text(path) for path in latex_files())
    bib_text = read_text(LATEX_ROOT / "references.bib")

    cite_keys = extract_cite_keys(tex_text)
    bib_keys = extract_bib_keys(bib_text)
    missing_cites = sorted(cite_keys - bib_keys)
    unused_bib = sorted(bib_keys - cite_keys)

    if missing_cites:
        failures.append(f"missing citation keys: {', '.join(missing_cites)}")
    if unused_bib:
        failures.append(f"unused BibTeX entries: {', '.join(unused_bib)}")

    print(f"cite_keys={len(cite_keys)}")
    print(f"bib_keys={len(bib_keys)}")
    print(f"missing_cites={len(missing_cites)}")
    print(f"unused_bib={len(unused_bib)}")

    bib_triplet = [
        PAPER_ROOT / "references_seed.bib",
        PAPER_ROOT / "references.bib",
        LATEX_ROOT / "references.bib",
    ]
    bib_hashes = {path: sha256(path) for path in bib_triplet}
    if len(set(bib_hashes.values())) != 1:
        failures.append("references_seed.bib, references.bib, and latex/references.bib differ")
    print(f"bib_files_synchronized={len(set(bib_hashes.values())) == 1}")

    graphics = sorted(extract_graphics(tex_text))
    missing_graphics = []
    for rel in graphics:
        path = LATEX_ROOT / rel
        if not path.exists():
            missing_graphics.append(rel)
    if missing_graphics:
        failures.append(f"missing graphics: {', '.join(missing_graphics)}")
    print(f"graphics_refs={len(graphics)}")
    print(f"missing_graphics={len(missing_graphics)}")

    figure_pairs = [
        (
            LATEX_ROOT / "figures" / "figure1_saqt_overview.pdf",
            PAPER_ROOT / "figures" / "figure1_saqt_overview.pdf",
        ),
        (
            LATEX_ROOT / "figures" / "figure2_main_results.pdf",
            PAPER_ROOT / "figures" / "figure2_main_results.pdf",
        ),
    ]
    for latex_pdf, source_pdf in figure_pairs:
        if not latex_pdf.exists() or not source_pdf.exists():
            failures.append(f"missing figure pair: {latex_pdf} / {source_pdf}")
            continue
        if sha256(latex_pdf) != sha256(source_pdf):
            failures.append(f"figure hash mismatch: {latex_pdf.name}")
    print(f"figure_pairs_checked={len(figure_pairs)}")

    zip_a = LATEX_ROOT / "saqt_lncs_overleaf_draft.zip"
    zip_b = PAPER_ROOT / "saqt_lncs_overleaf_draft.zip"
    if not zip_a.exists() or not zip_b.exists():
        failures.append("missing Overleaf zip file")
    elif sha256(zip_a) != sha256(zip_b):
        failures.append("latex and parent Overleaf zip hashes differ")
    else:
        print(f"zip_sha256={sha256(zip_a)}")

    placeholder_patterns = [
        "TODO",
        "REF_NEEDED",
        "RESULT_NEEDED",
        "METHOD_DETAIL_NEEDED",
    ]
    placeholders = [
        pattern for pattern in placeholder_patterns if re.search(pattern, tex_text)
    ]
    if placeholders:
        failures.append(f"unresolved placeholders: {', '.join(placeholders)}")
    print(f"unresolved_placeholders={len(placeholders)}")

    if warnings:
        print(f"warnings={len(warnings)}")
        for warning in warnings:
            print(f"WARNING {warning}")
    else:
        print("warnings=0")

    print(f"failures={len(failures)}")
    for failure in failures:
        print(f"FAIL {failure}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
