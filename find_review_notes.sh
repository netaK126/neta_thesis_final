#!/bin/bash
# Find all review notes from Dana in the thesis.
# Run from the thesis root: ./find_review_notes.sh
#
# Red notes (\Dana{})   = comments on your new changes
# Orange notes (\Danawarn{}) = old TODOs still open from the previous round
# Markup: \dadd{} = new text, \dremove{} = removed text

echo "=============================================="
echo "  Dana's review notes — compile and read the"
echo "  PDF to see them in context (red / orange)."
echo "=============================================="
echo ""

echo "--- NEW COMMENTS on your changes (red, \Dana) ---"
grep -rn '\\Dana{' main/ front/ back/ --include="*.tex" \
  | grep -v '^\s*%' | grep -v 'newcommand' \
  | sed 's/.*\(main\|front\|back\)/\1/' \
  | nl -ba
echo ""

echo "--- OLD TODOs still open (orange, \Danawarn) ---"
grep -rn '\\Danawarn{' main/ front/ back/ --include="*.tex" \
  | grep -v '^\s*%' | grep -v 'newcommand' \
  | sed 's/.*\(main\|front\|back\)/\1/' \
  | nl -ba
echo ""

echo "--- MARKUP: additions (\dadd) ---"
grep -rn '\\dadd{' main/ front/ back/ graphics/ --include="*.tex" \
  | grep -v '^\s*%' | grep -v 'newcommand' \
  | wc -l | xargs printf "  %s lines with additions\n"

echo "--- MARKUP: removals (\dremove) ---"
grep -rn '\\dremove{' main/ front/ back/ graphics/ --include="*.tex" \
  | grep -v '^\s*%' | grep -v 'newcommand' \
  | wc -l | xargs printf "  %s lines with removals\n"

echo ""
echo "To compile: latexmk -xelatex thesis.tex"
echo "Red = Dana's new comments. Orange = old TODOs you haven't addressed yet."
echo ""
echo "HOW TO RESPOND:"
echo "  1. For each \\Dana{}/\\Danawarn{} note in the .tex files:"
echo "     Add \\Neta{your answer} right after it (renders in GREEN in the PDF)."
echo "     Write 'done' if you fixed it, or your answer if you disagree."
echo "  2. Also fill in review_responses.md (same answers)."
echo "  3. After fixing, unwrap \\dadd{text} -> text, delete \\dremove{text}"
echo "  4. Run ./check_style.sh to catch typos"
echo "  5. Commit and push. Every item must have a response."
echo ""
echo "--- NETA'S RESPONSES (green, \\Neta) ---"
NETA=$(grep -rn '\\Neta{' main/ front/ back/ --include="*.tex" \
  | grep -v '^\s*%' | grep -v 'newcommand' \
  | sed 's/.*\(main\|front\|back\)/\1/')
if [ -n "$NETA" ]; then
  echo "$NETA" | nl -ba
else
  echo "  None yet."
fi
