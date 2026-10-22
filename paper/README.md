# Paper: IEEE Access submission

One paper, one target venue. This replaces the four near-duplicate drafts in the
repository root (`research_paper_IJEC/IJRTMR/JCST/JSR.*`), which described the
same findings and would have constituted redundant submission if sent out
concurrently.

## Target: IEEE Access

Chosen because its review criteria are technical soundness and usefulness to the
community rather than beating a state-of-the-art benchmark, which is the right
fit for a systems-plus-measurement paper. It is indexed in Scopus and Web of
Science, so it satisfies an indexing requirement. It charges an article
processing charge — **confirm the current figure before committing**.

Acceptance is never guaranteed. What this draft does is remove the reasons a
paper gets desk-rejected before review: it is long enough, it has figures, every
number traces to a stored artefact, the statistics are real, and the limitations
are stated plainly.

## Files

| file | role |
|---|---|
| `ieee_access_paper.tex` | the submission source (IEEEtran; 5,200 words of body text, 26 references) |
| `figures/*.pdf` | vector figures for LaTeX |
| `figures/*.png` | raster copies for Word and previews |
| `make_figures.py` | regenerates every figure from the eval reports |
| `check_claims.py` | verifies all 76 quantitative claims against the stored reports |
| `make_reading_copy.py` | renders `reading_copy.docx` for review and sharing |
| `reading_copy.docx` / `.pdf` | readable version; **not** the submission artefact |

## Compiling

There is no LaTeX installed on this machine. The simplest route:

1. Open [Overleaf](https://www.overleaf.com), create a project from the
   **IEEE Access** template.
2. Upload `ieee_access_paper.tex` and the `figures/` directory.
3. Change the first line to `\documentclass{ieeeaccess}` and move the
   `\title` / `\author` content into that class's form. Everything from
   `\section{Introduction}` onward needs no change.

It also compiles unmodified with any TeX distribution, because `IEEEtran` ships
with all of them:

```bash
pdflatex ieee_access_paper && pdflatex ieee_access_paper
```

References are inline in a `thebibliography` block, so no BibTeX pass is needed.

## Before submitting

Two items are deliberately marked in red in the compiled PDF so they cannot be
missed. `check_claims.py` lists them:

```
institutional e-mail address
public repository URL
```

The repository URL matters more than it looks. The paper claims every number is
reproducible from stored artefacts, and IEEE Access reviewers do check
reproducibility statements. Push the code and the `reports/` directory first,
then paste the URL.

## Regenerating everything

```bash
# figures, straight from the measured reports
phase-2/backend/.venv/bin/python paper/make_figures.py

# verify every number in the .tex still matches those reports
phase-2/backend/.venv/bin/python paper/check_claims.py

# readable copy
python3 paper/make_reading_copy.py
soffice --headless --convert-to pdf --outdir paper paper/reading_copy.docx
```

`check_claims.py` is the important one. It recomputes each figure from the JSON
and asserts the LaTeX contains the matching string, so if a report is re-run and
a number moves, the check fails instead of the paper quietly going stale.

## What changed from the four earlier drafts

- **Framing.** The earlier drafts narrated the project ("Phase 1 delivers
  breadth, Phase 2 delivers depth") and reported test-suite counts as headline
  results. This one states four research questions and leads with the
  measurement findings, which are the transferable part.
- **Length.** 2,300–2,800 words → 5,200 words of body text.
- **Statistics.** None → a paired Wilcoxon signed-rank test with exact *p*,
  effect size, and a measured noise floor that the conclusions are bounded by.
- **Figures.** None → four, generated from the data rather than drawn by hand.
- **Related work.** Three paragraphs → four subsections positioned against the
  guardrail and LLM-judge literature, which is where a reviewer will push.
- **Negative results kept.** The per-agent model hypothesis failed; the paper
  reports it as a failure with the statistics, rather than dropping it.
- **Threats to validity.** Added, including the one that matters most: no human
  validation of the judge.
- **Placeholders.** `rishav.gupta@example.com` and `Volume XX / ISSN XXXX-XXXX`
  are gone; the two genuine unknowns are flagged loudly instead.
