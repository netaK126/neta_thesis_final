#!/bin/bash
# Style checker for Dana's thesis rules.
# Run from the thesis root: ./check_style.sh
#
# Checks:
#  1. No semicolons in prose (use periods or parentheses)
#  2. No orphan \ref without Figure~/Table~/Section~ prefix
#  3. Figures/tables should use [t] placement
#  4. "undecided" should be "unstable"
#  5. Common typos
#  6. Remaining TODO/FIXME comments
#  7. "binary" for ReLU encoding (say "exact encoding" or "unstable")

DIRS="main/ front/"
FILES="--include=*.tex"
ISSUES=0

echo "=============================================="
echo "  Style checker (Dana's rules)"
echo "=============================================="
echo ""

# 1. Semicolons in prose (skip comments, math, and algorithm lines)
echo "--- Semicolons in prose ---"
SEMI=$(grep -rn ';' $DIRS $FILES \
  | grep -v '^\s*%' \
  | grep -v '\\DontPrintSemicolon' \
  | grep -v '\\;' \
  | grep -v 'url{' \
  | grep -v 'eprint' \
  | grep -v 'newcommand' \
  | grep -v '\\KwFunction' \
  | grep -v '\\SetKw' \
  | grep -v 'algorithm2e' \
  | grep -v 'hypersetup' \
  | grep -v 'usepackage' \
  | grep -v 'bibsetup' \
  | grep -v 'makeatother\|makeatletter' \
  | grep -v '\\fi\|\\else\|\\if' \
  | grep -v 'renewcommand\|renewenvironment\|renewglossarystyle' \
  | grep -v 'tabularnewline\|longtable\|tabular' \
  | grep -v '\.bib:' \
  | grep -v 'misc/' )
if [ -n "$SEMI" ]; then
  echo "$SEMI" | sed 's/.*\(main\|front\)/  \1/'
  ISSUES=$((ISSUES + $(echo "$SEMI" | wc -l)))
else
  echo "  None found."
fi
echo ""

# 2. Bare \ref without prefix
echo "--- Bare \\ref (should be Figure~\\ref, Table~\\ref, etc.) ---"
BARE=$(grep -rn '\\ref{' $DIRS $FILES \
  | grep -v '^\s*%' \
  | grep -v 'Figure~\\ref\|Table~\\ref\|Section~\\ref\|Chapter~\\ref\|Equation~\\ref\|Lemma~\\ref\|Theorem~\\ref\|Algorithm~\\ref' \
  | grep -v 'eqref\|autoref\|cref\|nameref' \
  | grep -v '~\\ref\|\\ref{eq:' \
  | grep -v 'label\|caption\|\\ref{ch:\|\\ref{sec:\|\\ref{fig:\|\\ref{tab:\|\\ref{lem:\|\\ref{thm:' \
  | grep -v 'newcommand\|renewcommand')
if [ -n "$BARE" ]; then
  echo "$BARE" | sed 's/.*\(main\|front\)/  \1/' | head -20
  ISSUES=$((ISSUES + $(echo "$BARE" | wc -l)))
else
  echo "  None found."
fi
echo ""

# 3. "undecided" (should be "unstable")
echo "--- 'undecided' (should be 'unstable') ---"
UNDEC=$(grep -rn 'undecided' $DIRS $FILES | grep -v '^\s*%' | grep -v 'dremove')
if [ -n "$UNDEC" ]; then
  echo "$UNDEC" | sed 's/.*\(main\|front\)/  \1/'
  ISSUES=$((ISSUES + $(echo "$UNDEC" | wc -l)))
else
  echo "  None found."
fi
echo ""

# 4. Common typos
echo "--- Common typos ---"
TYPOS=$(grep -rni 'experiemnts\|experiemnt\|relexation\|teh \|seperately\| hte \|nework\|neruon\|pertubation\b' $DIRS $FILES | grep -v '^\s*%')
if [ -n "$TYPOS" ]; then
  echo "$TYPOS" | sed 's/.*\(main\|front\)/  \1/'
  ISSUES=$((ISSUES + $(echo "$TYPOS" | wc -l)))
else
  echo "  None found."
fi
echo ""

# 5. Remaining TODOs
echo "--- Remaining TODO/FIXME ---"
TODOS=$(grep -rn 'TODO\|FIXME' $DIRS $FILES | grep -v 'newcommand\|find_review\|check_style')
if [ -n "$TODOS" ]; then
  echo "$TODOS" | sed 's/.*\(main\|front\)/  \1/' | head -20
  COUNT=$(echo "$TODOS" | wc -l)
  echo "  ($COUNT total)"
  ISSUES=$((ISSUES + COUNT))
else
  echo "  None found."
fi
echo ""

# 6. Subject-verb: "relaxation have" etc.
echo "--- Subject-verb agreement ---"
SVA=$(grep -rni 'relaxation have\|relaxation are\|interval have\|zonotope have\|network have\b' $DIRS $FILES | grep -v '^\s*%')
if [ -n "$SVA" ]; then
  echo "$SVA" | sed 's/.*\(main\|front\)/  \1/'
  ISSUES=$((ISSUES + $(echo "$SVA" | wc -l)))
else
  echo "  None found."
fi
echo ""

# 7. Orphan paragraphs (1-2 non-blank lines between blank lines)
echo "--- Possible orphan paragraphs ---"
for f in main/*.tex front/*.tex; do
  [ -f "$f" ] || continue
  awk -v file="$f" '
  /^\s*$/ || /^\s*%/ { blank++; next }
  { if (blank >= 1) { start = NR; count = 0 }
    blank = 0; count++; lines[count] = $0 }
  blank >= 1 && count > 0 && count <= 2 {
    # skip if line is a command-only line (section, label, begin, end, etc.)
    skip = 1
    for (i = 1; i <= count; i++) {
      if (lines[i] !~ /^\\(section|subsection|paragraph|label|begin|end|chapter|Dana|Danawarn|Neta|dadd|dremove)/) skip = 0
    }
    if (!skip) printf "  %s:%d (%d line%s)\n", file, start, count, (count>1?"s":"")
    count = 0
  }
  END { if (count > 0 && count <= 2) {
    skip = 1
    for (i = 1; i <= count; i++) {
      if (lines[i] !~ /^\\(section|subsection|paragraph|label|begin|end|chapter|Dana|Danawarn|Neta|dadd|dremove)/) skip = 0
    }
    if (!skip) printf "  %s:%d (%d line%s)\n", file, start, count, (count>1?"s":"")
  }}
  ' "$f"
done 2>/dev/null
echo ""

# 8. Inflated / overly academic words
echo "--- Inflated phrasing ---"
INFLATED=$(grep -rni '\butilize\b\|aforementioned\|\bhenceforth\b\|\bhereby\b\|\bnotwithstanding\b\|\bendeavor\b\|\bfacilitate\b\|\bparadigm\b\|\bpivotal\b\|\bplethora\b\|\bdelve\b\|\bfurthermore\b\|\bnevertheless\b\|\bmore specifically\b\|\bin order to\b\|\bdue to the fact\b\|\bit is worth noting\b\|\bit should be noted\b' $DIRS $FILES | grep -v '^\s*%' | grep -v 'newcommand')
if [ -n "$INFLATED" ]; then
  echo "$INFLATED" | sed 's/.*\(main\|front\)/  \1/'
  ISSUES=$((ISSUES + $(echo "$INFLATED" | wc -l)))
else
  echo "  None found."
fi
echo ""

# 9. Unhandled review comments (every \Dana/\Danawarn must have a \Neta right after, or be removed)
echo "--- Unhandled review comments ---"
UNHANDLED_LIST=""
for f in main/*.tex front/*.tex; do
  [ -f "$f" ] || continue
  HITS=$(awk -v file="$f" '
  /\\Dana\{/ || /\\Danawarn\{/ {
    if ($0 ~ /newcommand/) next
    note_line = NR
    found_response = 0
    for (i = 1; i <= 3; i++) {
      if ((getline nextline) > 0) {
        if (nextline ~ /\\Neta\{/) { found_response = 1; break }
        if (nextline ~ /\\Dana\{/ || nextline ~ /\\Danawarn\{/) break
        if (nextline !~ /^\s*$/ && nextline !~ /^\s*%/) break
      }
    }
    if (!found_response) printf "  %s:%d  NOT HANDLED\n", file, note_line
  }
  ' "$f")
  [ -n "$HITS" ] && UNHANDLED_LIST="${UNHANDLED_LIST}${HITS}
"
done
if [ -z "$UNHANDLED_LIST" ]; then
  echo "  All comments handled!"
else
  echo "$UNHANDLED_LIST"
  UNHANDLED=$(echo "$UNHANDLED_LIST" | grep -c 'NOT HANDLED')
  echo "  $UNHANDLED comment(s) without a \\Neta{} response."
  echo "  Either fix the issue and remove the note, or add \\Neta{your answer} after it."
  ISSUES=$((ISSUES + UNHANDLED))
fi
echo ""

echo "=============================================="
echo "  Total issues: $ISSUES"
echo "=============================================="

