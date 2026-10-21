# Neta's M.Sc. Thesis

LaTeX source of the thesis, based on the BLEND paper (`../neta-s-paper`),
written on the official Technion class, `misc/iitthesis.cls`
([technion-iit-thesis](https://github.com/eyalroz/technion-iit-thesis)).

## Build

```
python3 compile_thesis.py
```

The script wraps `latexmk -xelatex thesis`, which runs `xelatex`, `biber`
and `makeglossaries` as many times as needed, and leaves the result in
`aux/thesis.pdf`.

The class needs: `xelatex`, `biber`, `latexmk`, `makeglossaries`, the
`bidi` and `biblatex` packages, and a Hebrew font (David CLM, from the
`culmus` package). On Debian or Ubuntu:

```
apt install texlive-xetex texlive-latex-extra texlive-bibtex-extra \
            texlive-lang-arabic biber latexmk culmus
```

## Layout

```
thesis.tex              the master file: class options and the chapters
misc/iitthesis.cls      the Technion class, unmodified
misc/iitthesis-extra.sty  the class's optional extras, NOT loaded (see thesis.tex)
misc/thesis-fields.tex  author, title, supervision, dates, statements
misc/my-thesis-specific.tex  our packages, macros and conventions
front/abstract.tex      the abstract, English and Hebrew
front/abbrevs.tex       the notation and the abbreviations
front/personal-acks.tex the personal acknowledgements
front/pubinfo.bib       the publications the thesis is based on
main/*.tex              the chapters
back/general.bib        the bibliography
graphics/               the figures
```

The class generates everything around the chapters: the cover and title
pages in both languages, the statements, the table of contents, the page
numbering (nothing before the abstract, which is page 1), the notation
list, the bibliography, and the Hebrew section at the end in reverse
page order, ready for binding.

## Chapters

| # | File | Content |
|---|------|---------|
| 1 | `main/intro.tex` | introduction |
| 2 | `main/prelims.tex` | networks, global robustness, exact verification, abstractions |
| 3 | `main/related-work.tex` | related work |
| 4 | `main/key-ideas.tex` | the ideas, with worked examples |
| 5 | `main/blend.tex` | BLEND in full, with Algorithm 1 and the soundness lemmas |
| 6 | `main/evaluation.tex` | evaluation; `evaluation-results.tex` and `evaluation-ablation.tex` hold the copied result floats |
| 7 | `main/conclusion.tex` | conclusions and future work |

## Before submitting

- Fill the `TODO`s in `misc/thesis-fields.tex` (title, degree, dates).
- Write the Hebrew abstract in `front/abstract.tex` (500 to 2000 words).
- Fill the red `X` placeholders in the abstract and the introduction with
  the final numbers.
- For the version submitted to the libraries after the examination:
  drop `beforeDefense` from the class options in `thesis.tex`, write
  `front/personal-acks.tex`, and add the publications to
  `front/pubinfo.bib` with the blocks in `misc/thesis-fields.tex`.
