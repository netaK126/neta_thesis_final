# Dana's Review — Neta's Responses

For each item, respond in **two places**:

1. **In the PDF** — add `\Neta{your answer}` right after the `\Dana{}`/`\Danawarn{}` note in the .tex file. This renders in **green** so I can see it in the PDF.
2. **In this file** — write your response next to `Response:` below.

- If you fixed it: write `done` in both places.
- If you disagree or have a question: write your answer in both places.
- Do NOT leave any item blank.

When all items are answered, commit and push.

---

## New comments on your changes

### 1. prelims.tex:122 — "maximum" should be "supremum"
The text says "maximum of δ̂_{c_t}" but δ̂_{c_t} is defined as a sup. Should this be "supremum"?

**Response:**

### 2. blend.tex:133 — Start new paragraph before τ=0
The τ=0/τ>0 soundness discussion comes right after the line-by-line walkthrough. It should be a separate paragraph.

**Response:**

### 3. blend.tex:191 — "for z_{m,k}" orphaned after eq 5.2
Fold "for z_{m,k}" into the sentence before the equation so it doesn't dangle alone.

**Response:**

### 4. blend.tex:235 — "decided" should be "stable"
"decided" is not defined in the thesis. Do you mean "stable" (Section 2.3)?

**Response:**

### 5. conclusion.tex:35 — Section 7.1 opening
The second sentence doesn't follow from the first. Suggested rewrite: "The first direction focuses on small perturbations, such as a brightness shift of ε=0.01. While this might seem simpler, it is not, since..."

**Response:**

### 6. conclusion.tex:51 — Restore one-copy equation in Section 7.1
The rewrite is shorter (good), but the formal derivation (eqs 7.1–7.3) was a concrete contribution. Keep one displayed equation showing the one-copy condition.

**Response:**

### 7. conclusion.tex:76 — Keep first-layer bounds in Section 7.2
Good rewrite, but the old version had concrete first-layer bounds (ℓ₀: top-t weights, ℓ₁: Hölder, ℓ₂: Cauchy–Schwarz). Keep one sentence per norm.

**Response:**

### 8. evaluation.tex:95 — 15-minute filter
The sentence says easy instances are filtered, but in 30 of the 86 rows all three verifiers finish in under 15 minutes and those rows are in the averages. Apply the filter or drop the sentence.

**Response:**

---

## Old TODOs still open from the previous round

### 9. evaluation.tex:132 — VHAGaR faster cases
In the current tables, VHAGaR is faster mainly on MNIST conv1 under occlusion and translation. Update the text to match.

**Response:**

### 10. evaluation.tex:162 — τ=0.2 and τ=0.3 identical
BLEND's rows at τ=0.2 and τ=0.3 are identical. Is it because no neuron has a triangle error between 0.2 and 0.3? If so, say so.

**Response:**

### 11. evaluation.tex:174 — Wilcoxon n=87 vs 86
Transfer speed has n=87, but the tables have 86 rows. How is n counted? Also, independence concern with repeated rows.

**Response:**

### 12. evaluation.tex:211 — Verify ablation statements
Verify: (1) each experiment runs once, (2) timeout counts as 180 min. If verified, just say "done" and remove the TODO.

**Response:**

### 13. evaluation.tex:244 — Ablation average mismatch
The four τ=0.5 transfer cells average 87.9 min, not 81.1. Check that the ablation and the tables come from the same runs.

**Response:**

### 14. blend.tex:112 — ReLU rule at Line 14
I moved the ReLU rule of the difference interval from Line 8 to Line 14. Please confirm this is correct.

**Response:**

### 15. blend.tex:182 — Pre-activations with hats
Should the difference zonotope be over pre-activations (ẑ, with hats) rather than post-activation z?

**Response:**

### 16. blend.tex:418 — δ_{c_t} with hat
Should this be δ̂_{c_t}, with a hat, as in the rest of the chapter?

**Response:**

### 17. abstract.tex:62 — Hebrew abstract
The Hebrew abstract is about 290 words. Extend to at least 1,000 words.

**Response:**

---

## Style issues (from check_style.sh)

### 18. evaluation.tex:220 — "relaxation have" → "relaxation has"

**Response:**

### 19. evaluation.tex:224 — "experiemnts" → "experiments"

**Response:**

### 20. evaluation.tex:225 — "relexations" → "relaxations"

**Response:**

### 21. evaluation.tex:227 — "experiemnt" → "experiment"

**Response:**
