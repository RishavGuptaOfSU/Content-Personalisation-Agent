# Paper

**Target: Journal of Computer Science and Technology (JCST).** One venue, one
manuscript.

This replaces the four near-duplicate drafts in the repository root
(`research_paper_IJEC/IJRTMR/JCST/JSR.*`), which described the same findings and
would have constituted redundant submission if sent out concurrently.

## Why JCST

| | |
|---|---|
| publisher | Springer, for the Institute of Computing Technology (CAS) and the China Computer Federation |
| indexing | Scopus and SCI |
| cost | **none** — subscription journal; the article processing charge applies only if you elect open access |
| scope | "all aspects of computer science and technology", which this paper sits inside |
| review | double-blind |

It was your own first choice. An earlier draft of this work was aimed at IEEE
Access, which charges **$2,160 regardless of outcome**; JCST is indexed at least
as well and costs nothing, so there was no reason to pay.

Dropped from the original four:

- **IJEC** (Int. J. of Electronic Commerce, Taylor & Francis) — a good journal,
  but it publishes electronic-commerce and information-systems research. This
  is systems engineering and evaluation methodology. Desk-rejected on scope.
- **IJRTMR** (FDRP) — not in Scopus or SCImago.
- **JSR** (Journal of Student Research) — viable fallback, not Scopus-indexed.

## Files

| file | role |
|---|---|
| `jcst_paper.tex` | **the submission source** |
| `jcst_paper.pdf` | **compiled and inspected**: 8 pages, two-column, Times, authors named |
| `figures/*.pdf` | vector figures for LaTeX |
| `figures/*.png` | raster copies for Word and previews |
| `check_jcst.py` | 55 checks against JCST's Instructions for Authors |
| `check_claims.py` | 76 checks: every number against the stored eval reports |
| `make_figures.py` | regenerates every figure from those reports |
| `ieee_access_paper.tex` / `.pdf` | the IEEE Access variant, kept in case you ever want that venue |
| `make_reading_copy.py`, `reading_copy.*` | single-column reading copy; **not** for submission |

## The one thing this repository cannot contain

JCST mandates its own LaTeX class, distributed only from the journal's own
download page and not redistributable:

> <https://jcst.ict.ac.cn/> → **Download Templates** → *JCST Submit Template
> (LaTeX)*. The package also contains `JCST.bst`.

So `jcst_paper.tex` carries an **emulation preamble** that reproduces JCST's
page layout closely enough to proof-read and verify, and the manuscript proper
sits between two markers:

```
% ============================== BODY-BEGIN
...
% =============================== BODY-END
```

**To produce the real submission:** download the official template, open its
main `.tex`, and paste everything between those markers into it. Nothing in the
body depends on the emulation preamble except three one-line macros
(`\figref`, `\tabref`, `\tabnote`) which can be inlined if the template
objects. Then confirm the page count still lands in 8–16.

## Verified against JCST's published rules

`check_jcst.py` — all 55 pass:

| JCST rule | status |
|---|---|
| Abstract 100–250 words | **243** |
| Abstract: no undefined abbreviations, no mathematics, no citations | pass |
| Keywords: 3–5, alphabetical, comma separated | **5**, alphabetical |
| Research Paper length 8–16 pages inc. figures, tables, references | **8** |
| Double-blind: no name, affiliation, e-mail, repository URL, acknowledgements | pass |
| Tables: vertical three-line only, no vertical rules | 5 tables |
| Table captions above, Title Case; notes beneath as "Note:" | pass |
| Figures cited `Fig.N` (no space); captions below as "Fig.N." | 4 figures |
| Citations: square brackets, numbered in first-citation order | 26 refs |
| Author biography and photo supplied only on acceptance | omitted |
| Running head ≤ 45 characters | **43** |

Compile status, checked page by page: 8 pages, US Letter, two-column, Times
(TeXGyreTermes) embedded, one 0.9 pt vertical overflow, no undefined references.

## Before submitting

1. **Move the body into the official JCST template** (above). This is required,
   not optional — JCST desk-rejects on template.
2. **Anonymity is already handled**, but re-read once after moving: the title
   block says author details are withheld, there is no e-mail, no affiliation,
   no acknowledgements section, and the reproducibility paragraph promises the
   artefact release *on acceptance* rather than linking it.
3. **Biography and a 600 dpi photo** are needed only if accepted. One
   `\REPLACE` marker in the file reminds you.
4. Write the cover letter. JCST asks that any prior version be referenced in
   the third person and the new contribution explained; there is no prior
   version here, so state that the work is original and not under review
   elsewhere.

## Regenerating and re-verifying

```bash
# figures, straight from the measured reports
phase-2/backend/.venv/bin/python paper/make_figures.py

# every number in the manuscript still matches those reports
phase-2/backend/.venv/bin/python paper/check_claims.py jcst_paper.tex

# still conforms to JCST's instructions
python3 paper/check_jcst.py
```

`check_claims.py` recomputes each figure from the report JSON and asserts the
manuscript states it, so if an eval is re-run and a number moves, the check
fails instead of the paper quietly going stale. It accepts either manuscript as
an argument and normalises wording differences, so the same 76 claims are
verified for both the JCST and IEEE versions.

## What changed from the four earlier drafts

- **Framing.** They narrated the project ("Phase 1 delivers breadth, Phase 2
  delivers depth") and reported test-suite counts as headline results. This
  states four research questions and leads with the measurement findings.
- **Length.** 2,300–2,800 words → 5,200 words of body text.
- **Statistics.** None → a paired Wilcoxon signed-rank test with exact *p*,
  effect size, and a measured noise floor that bounds every conclusion.
- **Figures.** None → four, generated from the data rather than drawn by hand.
- **Related work.** Three paragraphs → four subsections positioned against the
  guardrail and automatic-judge literature, which is where a reviewer pushes.
- **Negative result kept.** The per-agent model hypothesis failed; it is
  reported as a failure with its statistics rather than dropped.
- **Threats to validity.** Added, including the one that matters most: the
  judge was never validated against human raters.
- **Placeholders.** `rishav.gupta@example.com` and `Volume XX / ISSN XXXX-XXXX`
  are gone.
