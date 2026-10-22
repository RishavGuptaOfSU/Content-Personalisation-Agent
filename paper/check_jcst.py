#!/usr/bin/env python
"""Checks jcst_paper.tex against JCST's published Instructions for Authors.

Source of every rule below: JCST Instruction for Authors (2025),
https://media.springer.com/full/springer-instructions-for-authors-assets/pdf/
11390_Instructions%20for%20Authors_2025.pdf

Run after any edit to the manuscript:

    python3 paper/check_jcst.py
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEX = HERE / "jcst_paper.tex"
PDF = HERE / "jcst_paper.pdf"

SRC = TEX.read_text(encoding="utf-8")
# The body is what gets pasted into the official template; the emulation
# preamble is scaffolding and is not checked for content rules.
BODY = SRC.split("% ============================== BODY-BEGIN")[1].split(
    "% =============================== BODY-END")[0]

FAILURES: list[str] = []
WARNINGS: list[str] = []


def check(rule: str, ok: bool, detail: str = "", warn_only: bool = False) -> None:
    mark = "PASS" if ok else ("WARN" if warn_only else "FAIL")
    print(f"  [{mark}] {rule}" + (f" -> {detail}" if detail else ""))
    if not ok:
        (WARNINGS if warn_only else FAILURES).append(rule)


def main() -> int:
    print("1. Abstract (100-250 words; no undefined abbreviations, no")
    print("   mathematical expressions, no bibliographic references)")
    abstract = BODY.split(r"\textbf{Abstract}")[1].split(r"\textbf{Keywords}")[0]
    plain = re.sub(r"\\quad|\\par|\\vspace\{[^}]*\}|\\noindent", " ", abstract)
    plain = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{([^{}]*)\})?", r" \3 ", plain)
    plain = re.sub(r"[{}\\]", " ", plain)
    words = len(plain.split())
    check("word count within 100-250", 100 <= words <= 250, f"{words} words")
    check("no inline mathematics", "$" not in abstract)
    check("no citations", r"\cite" not in abstract)
    check("no displayed equations", r"\begin{align" not in abstract)
    # Abbreviations: any run of 2+ capitals is suspect in an abstract.
    abbrevs = sorted(set(re.findall(r"\b[A-Z]{2,}\b", plain)))
    check("no bare abbreviations", not abbrevs, ", ".join(abbrevs) or "none found")

    print("\n2. Keywords (3-5, alphabetical order, comma separated)")
    kw_block = BODY.split(r"\textbf{Keywords}")[1].split(r"\end{adjustwidth}")[0]
    kw_block = re.sub(r"\\quad|\\noindent|\\par", " ", kw_block)
    keywords = [k.strip() for k in kw_block.split(",") if k.strip()]
    check("count between 3 and 5", 3 <= len(keywords) <= 5, f"{len(keywords)}")
    check("alphabetical order", keywords == sorted(keywords),
          " | ".join(keywords))

    print("\n3. Length (Research Paper: 8-16 pages inc. text, figures,")
    print("   tables and references)")
    if PDF.is_file():
        out = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True)
        pages = int(re.search(r"Pages:\s+(\d+)", out.stdout).group(1))
        check("page count within 8-16", 8 <= pages <= 16, f"{pages} pages")
    else:
        check("compiled PDF present to count pages", False, f"{PDF} missing")

    print("\n4. Double-blind review (no identifying information)")
    lowered = BODY.lower()
    for term in ("rishav", "gupta", "sharda", "greater noida", "github.com",
                 "orcid"):
        hit = term in lowered
        check(f"no occurrence of {term!r}", not hit)
    # An e-mail address, not the "@{}" of a tabular spec or @twocolumnfalse.
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", BODY)
    check("no e-mail address", not emails, ", ".join(emails) or "none")
    # An acknowledgements *section* de-anonymizes; the word in running prose
    # (e.g. "greetings and acknowledgements") does not.
    ack = re.findall(r"\\(?:section|subsection)\*?\{[^}]*[Aa]cknowledg[^}]*\}", BODY)
    check("no acknowledgements section", not ack, ", ".join(ack) or "none")
    check("anonymity is stated on the title block",
          "double-blind" in lowered and "withheld" in lowered)
    check("no author biography in the submission",
          "IEEEbiograph" not in BODY and r"\bio" not in BODY)

    print("\n5. Figures (cited as Fig.N with no space; caption below,")
    print("   beginning 'Fig.N.')")
    check("figure captions use the Fig. label", r"name=Fig." in SRC)
    bad_cites = re.findall(r"Fig\.\s+\\ref|Figure~?\\ref", BODY)
    check("no 'Fig. N' with a space or 'Figure N'", not bad_cites,
          ", ".join(bad_cites) or "none")
    figs = re.findall(r"\\includegraphics\[[^\]]*\]\{([^}]+)\}", BODY)
    check("every figure file exists",
          all((HERE / "figures" / f).exists() for f in figs),
          f"{len(figs)} figures")
    for env in re.findall(r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}", BODY, re.S):
        label = re.search(r"\\label\{([^}]*)\}", env)
        cap_before_graphic = env.find(r"\caption") < env.find(r"\includegraphics")
        check(f"caption below the image ({label.group(1) if label else '?'})",
              not cap_before_graphic)

    print("\n6. Tables (vertical three-line only; caption above in Title")
    print("   Case; notes beneath introduced by 'Note:')")
    tables = re.findall(r"\\begin\{table\*?\}(.*?)\\end\{table\*?\}", BODY, re.S)
    check("tables found", len(tables) > 0, f"{len(tables)} tables")
    for env in tables:
        label = re.search(r"\\label\{([^}]*)\}", env)
        name = label.group(1) if label else "?"
        check(f"{name}: caption above the tabular",
              env.find(r"\caption") < env.find(r"\begin{tabular}"))
        check(f"{name}: three-line rules only",
              r"\toprule" in env and r"\bottomrule" in env
              and r"\hline" not in env)
        check(f"{name}: no vertical rules",
              not re.search(r"\\begin\{tabular\}[^\n]*\|", env))
        check(f"{name}: has a Note", r"\tabnote" in env)
        caption = re.search(r"\\caption\{(.*?)\}\s*\n", env, re.S)
        if caption:
            text = re.sub(r"\\[a-zA-Z]+|[{}]", "", caption.group(1))
            minor = {"a", "an", "the", "of", "in", "on", "for", "and", "or",
                     "to", "with", "at", "by", "against", "from"}
            words_ = [w for w in re.findall(r"[A-Za-z]+", text)]
            bad = [w for i, w in enumerate(words_)
                   if i and w.lower() not in minor and w[0].islower()]
            check(f"{name}: caption in Title Case", not bad,
                  ", ".join(bad) or "ok")

    print("\n7. Citations (numbers in square brackets, numbered in order of")
    print("   first citation)")
    order: list[str] = []
    for group in re.findall(r"\\cite\{([^}]+)\}", BODY):
        for key in group.split(","):
            key = key.strip()
            if key and key not in order:
                order.append(key)
    bib = re.findall(r"\\bibitem\{([^}]+)\}", BODY)
    check("every citation has a bibitem", set(order) <= set(bib),
          ", ".join(sorted(set(order) - set(bib))) or "all resolved")
    check("no uncited bibitems", set(bib) <= set(order),
          ", ".join(sorted(set(bib) - set(order))) or "all cited")
    check("bibliography is in first-citation order", bib == order,
          "ok" if bib == order
          else f"first divergence at [{1 + next(i for i, (a, b) in enumerate(zip(bib, order)) if a != b)}]")
    print(f"  [INFO] {len(bib)} references")

    print("\n8. Running head (shortened title within 45 characters)")
    head = re.search(r"\\fancyhead\[L\]\{\\footnotesize ([^}]*)\}", SRC)
    if head:
        check("running head <= 45 characters", len(head.group(1)) <= 45,
              f"{len(head.group(1))} chars: {head.group(1)!r}")

    print("\n9. Items the author must still supply")
    todo = re.findall(r"\\REPLACE\{([^}]*)\}", SRC)
    for item in todo:
        print(f"  [INFO] {item}")
    if not todo:
        print("  [INFO] none")

    print()
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}):")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    if WARNINGS:
        print(f"PASSED with {len(WARNINGS)} warning(s).")
    else:
        print("CONFORMS TO JCST'S PUBLISHED INSTRUCTIONS FOR AUTHORS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
