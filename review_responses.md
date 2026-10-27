# Dana's Review — Neta's Responses

For each item below, write your response next to **Response:**

- **If you fixed it:** write `done` here, and in the .tex file remove the `\Dana{}`/`\Danawarn{}` note, unwrap `\dadd{text}` (keep the text), and delete `\dremove{text}` (remove it entirely).
- **If you disagree or have a question:** write your answer here, and in the .tex file add `\Neta{your answer}` right after the note (it renders in **green** in the PDF).
- Do NOT leave any item blank.

When all items are answered, commit and push.

---

## New comments on your changes

### 1. prelims.tex:122 — "maximum" should be "supremum"
The text says "maximum of δ̂_{c_t}" but δ̂_{c_t} is defined as a sup. Should this be "supremum"?

**Response:**
I switched the definitions to supremum/infimum in the previous round, following your earlier comment above eq. 4.3. I have now switched them back to maximum/minimum, in eq. 4.3, in the Exact Verification formulation, and in the δ* definition, so the prose and the definitions agree. DONE

### 2. blend.tex:133 — Start new paragraph before τ=0
The τ=0/τ>0 soundness discussion comes right after the line-by-line walkthrough. It should be a separate paragraph.

**Response:**
DONE

### 3. blend.tex:191 — "for z_{m,k}" orphaned after eq 5.2
Fold "for z_{m,k}" into the sentence before the equation so it doesn't dangle alone.

**Response:**
DONE
### 4. blend.tex:235 — "decided" should be "stable"
"decided" is not defined in the thesis. Do you mean "stable" (Section 2.3)?

**Response:**
you are right. i missed some in my previous fix. DONE.
### 5. conclusion.tex:35 — Section 7.1 opening
The second sentence doesn't follow from the first. Suggested rewrite: "The first direction focuses on small perturbations, such as a brightness shift of ε=0.01. While this might seem simpler, it is not, since..."

**Response:**
DONE

### 6. conclusion.tex:53 — Section 7.2 title too long
"Verifying New Perturbations in Global Robustness Settings" doesn't fit one line. Shorten it, e.g. "Supporting New Perturbation Types."

**Response:**
DONE
### 7. evaluation.tex:95 — 15-minute filter
The sentence says easy instances are filtered, but in 30 of the 86 rows all three verifiers finish in under 15 minutes and those rows are in the averages. Apply the filter or drop the sentence.

**Response:**
We apply this filter only on the bar graphs, and I changed the text to match. DONE

---

## Old TODOs still open from the previous round

### 8. evaluation.tex:132 — VHAGaR faster cases
In the current tables, VHAGaR is faster mainly on MNIST conv1 under occlusion and translation. Update the text to match.

**Response:**
You are right. the paragraph was related to the old results before fixing some major bugs. however, i am not sure i find a trend. more like "statistic errors", because we do have instances for conv where blend win over vhagar. please go through what i wrote.

### 9. evaluation.tex:162 — τ=0.2 and τ=0.3 identical
BLEND's rows at τ=0.2 and τ=0.3 are identical. Is it because no neuron has a triangle error between 0.2 and 0.3? If so, say so.

**Response:** done — yes, for BLEND: no neuron has a normalized triangle area between 0.2 and 0.3, so both thresholds relax the same neurons. With transfer they do not, since N_pre's bounds tighten the pre-activations, which is why only the BLEND half of the rows repeats. Said both in the text.

### 10. evaluation.tex:174 — Wilcoxon n=87 vs 86
Transfer speed has n=87, but the tables have 86 rows. How is n counted? Also, independence concern with repeated rows.

**Response:** done. The test was already updated, I just forgot to push it.

### 11. evaluation.tex:211 — Verify ablation statements
Verify: (1) each experiment runs once, (2) timeout counts as 180 min. If verified, just say "done" and remove the TODO.

**Response:** done — verified both.

### 12. evaluation.tex:244 — Ablation average mismatch
The four τ=0.5 transfer cells average 87.9 min, not 81.1. Check that the ablation and the tables come from the same runs.

**Response:** done — these experiments were accidentally run twice. I kept one of the two runs, so the tables and the ablation now both read 81.1.

### 13. blend.tex:112 — ReLU rule at Line 14
I moved the ReLU rule of the difference interval from Line 8 to Line 14. Please confirm this is correct.

**Response:**
it is correct :)

### 14. blend.tex:182 — Pre-activations with hats
Should the difference zonotope be over pre-activations (ẑ, with hats) rather than post-activation z?

**Response:**
You are right. DONE

### 15. blend.tex:418 — δ_{c_t} with hat
Should this be δ̂_{c_t}, with a hat, as in the rest of the chapter?

**Response:**
you are right. DONE
### 16. abstract.tex:62 — Hebrew abstract
The Hebrew abstract is about 290 words. Extend to at least 1,000 words.

**Response:** done — now about 1,250 words, built on the introduction's skeleton and expanded from the other chapters, without citations. It also needed a one-line fix in iitthesis.cls, since a multi-page Hebrew abstract used to break the build.

---

## Style issues (from check_style.sh)

### 17. evaluation.tex:220 — "relaxation have" → "relaxation has"

**Response:**

### 18. evaluation.tex:224 — "experiemnts" → "experiments"

**Response:**

### 19. evaluation.tex:225 — "relexations" → "relaxations"

**Response:**

### 20. evaluation.tex:227 — "experiemnt" → "experiment"

**Response:**
