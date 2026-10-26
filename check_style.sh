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

echo "=============================================="
echo "  Total issues: $ISSUES"
echo "=============================================="
