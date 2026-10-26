#!/usr/bin/env python3
"""Redraw the solve-time charts of the paper, one axis per figure.

The charts are delivered as finished pdfs under graphics/, and the
generator of the paper splits each of them over several plots, every
plot with its own frame, its own pair of axes and its own names. The
split cannot be undone by cropping.

This script reads those pdfs, recovers the numbers behind every bar
and every tightness point, and writes one tikz picture per figure that
draws them all on one axis. The numbers are not re-measured and not
re-run: they are the coordinates of the shapes in the pdfs, turned
back into minutes and percent with the axis calibration below, so each
figure says exactly what the paper's figure says.

    python3 tools/build_time_figures.py

writes the pictures named in FIGURES, which main/evaluation-results.tex
inputs. Re-run it if the source pdfs are regenerated.
"""

import itertools
import math
import os
import re
import sys

import fitz

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPHICS = os.path.join(HERE, "graphics")

# the figures to build: output name -> the source pdfs, in order
OCC = ["n2_time_app_6.pdf", "n2_time_app_7.pdf", "n2_time_app_8.pdf"]
BD = ["n2_bounddiff_app_%d.pdf" % i for i in range(1, 10)]
# the networks of the bound-difference charts, to select them by name
HAR_CIFAR = (r"1$\times$500 HAR", r"\emph{conv4} CIFAR-10",
             r"3$\times$100 MNIST")
F3X50 = (r"3$\times$50 FMNIST",)
M3X50 = (r"3$\times$50 MNIST",)
C1F = (r"\emph{conv1} FMNIST",)
C1M = (r"\emph{conv1} MNIST",)
TRANSL = ["n2_time_app_4.pdf", "n2_time_app_5.pdf"]
# the two networks the first three occlusion figures leave out
MNIST_CONV = (r"\emph{conv1} MNIST", r"\emph{conv4} CIFAR-10")

# the figures to build: output name -> the source pdfs, and the
# perturbation to keep, when one figure of the paper carries two
FIGURES = [
    # ---- the solve-time charts ----
    ("fig_patch_merged.tex",
     ["n2_time_app.pdf", "n2_time_app_2.pdf"], [(None, None)], "time"),
    ("fig_rot_linf_merged.tex",
     ["n2_time_app_3.pdf", "n2_time_app_4.pdf"],
     [(("rotation", "ℓ∞"), None)], "time"),
    # translation runs to 23 class pairs, past one axis at full bar
    # width, so it is split on the network boundaries of the source
    ("fig_transl_a_merged.tex", TRANSL, [(("translation",), (0, 2))], "time"),
    ("fig_transl_b_merged.tex", TRANSL, [(("translation",), (2, 5))], "time"),
    # occlusion runs to 42 class pairs, far past one axis, so it is
    # split by architecture, each figure as wide as the text block
    ("fig_occ_3x50_merged.tex",  OCC, [(None, (0, 2))], "time"),
    # the last occlusion block runs to 20 class pairs, so its two
    # smallest sizes join Fashion-MNIST conv1 and the rest stand alone
    ("fig_occ_cnn1f_merged.tex", OCC,
     [(None, (2, 3)), (("occ(1,1,5)", "occ(1,1,9)"), MNIST_CONV)], "time"),
    ("fig_occ_mnist_b_merged.tex", OCC,
     [(("occ(3,3,5)", "occ(5,5,5)", "occ(14,14,9)"), MNIST_CONV)], "time"),
    # ---- the bound-difference charts ----
    # 139 class pairs over seven networks, so they are split the same
    # way: by network, and within a network by perturbation
    ("fig_bd_har_merged.tex",      BD, [(None, HAR_CIFAR)], "bd"),
    ("fig_bd_f3x50_merged.tex",    BD, [(None, F3X50)], "bd"),
    ("fig_bd_c1f_merged.tex",      BD, [(None, C1F)], "bd"),
    ("fig_bd_m_occ_a_merged.tex",  BD, [(("occ(3,3,5)",), M3X50)], "bd"),
    ("fig_bd_m_occ_b_merged.tex",  BD,
     [(("occ(5,5,5)", "occ(14,14,9)"), M3X50)], "bd"),
    ("fig_bd_m_bright_merged.tex", BD,
     [(("brightness", "patch"), M3X50)], "bd"),
    ("fig_bd_m_contr_merged.tex",  BD,
     [(("contrast", "translation"), M3X50)], "bd"),
    ("fig_bd_m_rot_merged.tex",    BD, [(("rotation", "ℓ∞"), M3X50)], "bd"),
    ("fig_bd_c1m_a_merged.tex",    BD, [(("ℓ∞", "rotation"), C1M)], "bd"),
    ("fig_bd_c1m_b_merged.tex",    BD,
     [(("brightness", "contrast", "occ", "translation"), C1M)], "bd"),
]

# The paper draws two kinds of chart. The solve-time charts carry the
# execution time as bars, with the analysis tightness over them as a
# black line on a second axis; the bound-difference charts carry the
# tightness itself as bars, on one axis. Each has its own palette, and
# its own calibration: the bars stand on "base" and a bar at the full
# scale reaches "top".
KINDS = {
    "time": {
        "series": [("transfer", (0.083, 0.301, 0.083)),
                   ("blend",    (0.652, 0.844, 0.652)),
                   ("vhagar",   (0.753, 0.314, 0.302))],
        "full": 180.0,                    # the three-hour timeout
        "ticks": (0, 100, 200), "name": "time (minutes)",
        "right": True, "line": True,
    },
    "bd": {
        "series": [("transfer", (0.067, 0.259, 0.388)),
                   ("blend",    (0.666, 0.799, 0.888)),
                   ("vhagar",   (0.878, 0.510, 0.078))],
        "full": None,                     # scaled to the data, as the
        "ticks": None,                    # source charts scale it

        "name": r"$\delta_u-\delta_l$ (\%$\delta_{\max}$)",
        "right": False, "line": False,
    },
}
PCT_FULL = 100.0

# the rows of the source pdfs, by their distance from the top
TITLE_BAND = (9.0, 12.0)        # the perturbation over each block;
                                # a tick label can sit just under it
CS_BAND = (86.0, 95.0)          # the class pair under each block
NAME_BAND = (96.0, 120.0)       # the network under each block


def calibrate(page, bars):
    """The axis of one source chart: where zero is, and how many units
    one point is worth.

    The charts do not share a scale: a solve-time chart runs to 200
    minutes, and a bound-difference chart runs to whatever its own
    numbers need, 100 or 60 or 20 percent. Both are read off the chart
    itself: the bars stand on the axis, which fixes zero, and the tick
    labels to its left fix the spacing.
    """
    base = max(b[1] for b in bars)
    left = min(b[0] for b in bars)
    ticks = sorted(((w[1] + w[3]) / 2, float(w[4]))
                   for w in page.get_text("words")
                   if w[2] < left - 1 and w[1] > 12
                   and w[4].replace(".", "", 1).isdigit())
    if len(ticks) < 2:
        raise SystemExit("a chart with no tick labels to calibrate against")
    (ya, va), (yb, vb) = ticks[0], ticks[-1]
    per_pt = (va - vb) / (yb - ya)        # units per point, downwards
    return base, per_pt


def rows(page, lo, hi):
    """The labels of one row: (centre, text), left to right.

    A long network name wraps onto a second line in the source charts,
    so the words are gathered line by line and the lines that sit over
    one another are joined back into one label.
    """
    words = [w for w in page.get_text("words") if lo <= w[1] <= hi]
    lines = {}
    for w in words:
        key = next((k for k in lines if abs(k - w[1]) < 3), w[1])
        lines.setdefault(key, []).append(w)
    blocks = []
    for key in sorted(lines):
        cur = []
        for w in sorted(lines[key], key=lambda w: w[0]):
            if cur and w[0] - cur[-1][2] > 12:
                blocks.append((key, cur))
                cur = []
            cur.append(w)
        if cur:
            blocks.append((key, cur))
    out = []
    for key, g in blocks:
        lo_x, hi_x = g[0][0], g[-1][2]
        text = " ".join(w[4] for w in g)
        prev = next((o for o in out
                     if min(hi_x, o[2]) - max(lo_x, o[1]) > -6), None)
        if prev:                      # the next line of the same label
            prev[1], prev[2] = min(lo_x, prev[1]), max(hi_x, prev[2])
            prev[3] += " " + text
        else:
            out.append([key, lo_x, hi_x, text])
    return [((o[1] + o[2]) / 2, o[3]) for o in sorted(out, key=lambda o: o[1])]


def word_row(page, lo, hi, join=False):
    """One label per word: the perturbations and the class pairs are
    each a single word, and two of them can sit 3pt apart, so they are
    kept apart by default. A perturbation is the exception: the source
    sometimes sets it as two words, such as "occ (14,14,9)", whose
    halves all but touch, and join=True puts those back together."""
    words = sorted((w[0], w[2], w[4]) for w in page.get_text("words")
                   if lo <= w[1] <= hi)
    out = []
    for x0, x1, text in words:
        if join and out and x0 - out[-1][1] < 6:
            out[-1] = (out[-1][0], x1, out[-1][2] + text)
        else:
            out.append((x0, x1, text))
    return [((a + b) / 2, t) for a, b, t in out]


def read(path, K):
    """The bars, the tightness dots and the three label rows of one pdf."""
    page = fitz.open(path)[0]
    raw, marks = [], []
    for d in page.get_drawings():
        rect = d["rect"]
        if rect.y1 < 12:            # the legend, drawn once per file
            continue
        fill = d.get("fill")
        key = tuple(round(c, 3) for c in fill) if fill else None
        name = dict((c, n) for n, c in K["series"]).get(key)
        if name:
            raw.append((rect.x0, rect.y1, rect.x1, name, rect.y0))
        elif K["line"] and fill and max(fill) < 0.2 and rect.width < 3:
            marks.append(((rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2))
    base, per_pt = calibrate(page, [(r[0], r[1]) for r in raw])
    bars = [(x0, x1, name, (base - top) * per_pt)
            for x0, _, x1, name, top in raw]
    # the tightness line of a solve-time chart shares the bars' span,
    # and runs from 0 to 100 percent where they run to the timeout
    dots = [(x, (base - y) * per_pt / K["full"] * PCT_FULL) for x, y in marks]
    # the three bars of one class pair touch; the next pair starts after
    # a gap
    cells, cur = [], []
    for bar in sorted(bars):
        if cur and bar[0] - cur[-1][1] > 1.0:
            cells.append(cur)
            cur = []
        cur.append(bar)
    if cur:
        cells.append(cur)
    pairs = []
    for cell in cells:
        if len(cell) != 3:
            raise SystemExit("%s: a class pair with %d bars"
                             % (os.path.basename(path), len(cell)))
        lo, hi = cell[0][0], cell[-1][1]
        pairs.append({"lo": lo, "hi": hi, "mid": (lo + hi) / 2,
                      "val": {n: v for _, _, n, v in cell},
                      "pct": [p for x, p in sorted(dots)
                              if lo - 1 <= x <= hi + 1]})
    return (pairs, word_row(page, *TITLE_BAND, join=True),
            word_row(page, *CS_BAND),
            rows(page, *NAME_BAND))


def tidy_name(text):
    """'conv1, Fashion' -> ('\\emph{conv1}', 'FMNIST')."""
    arch, _, data = text.partition(",")
    arch, data = arch.strip(), data.strip()
    arch = arch.replace("×", r"$\times$")
    if re.match(r"^conv\d+$", arch):
        arch = r"\emph{%s}" % arch
    if data == "Fashion":
        data = "FMNIST"
    return arch, data


# Network labels the thesis prints differently from the source charts. The
# paper's charts name HAR's network 1x500; the thesis calls it 2x500, to match
# the architecture convention the text states. That was a hand-edit to the
# generated tikz, so a regeneration used to silently revert it -- applied here
# instead, at EMIT time only, so the name the figures are SELECTED by (the
# HAR_CIFAR filter, which matches what the pdf says) keeps working.
NAME_FIXUPS = {(r"1$\times$500", "HAR"): (r"2$\times$500", "HAR")}


def tidy_pert(name):
    """The perturbation, as the thesis writes it."""
    return name.replace("\u2113\u221e", r"$\ell_\infty$").replace("occ", "occlusion")


def nearest(labels, x):
    return min(labels, key=lambda t: abs(t[0] - x))[1]


def collect(sources, keep=None, nets_range=None, K=None):
    """The figure: a list of networks, each a list of class pairs."""
    pairs, titles, cs_labels, names = [], [], [], []
    for i, fname in enumerate(sources):
        shift = 1000.0 * i          # the files sit side by side
        p, t, c, n = read(os.path.join(GRAPHICS, fname), K)
        for cell in p:
            for k in ("lo", "hi", "mid"):
                cell[k] += shift
            pairs.append(cell)
        titles += [(x + shift, s) for x, s in t]
        cs_labels += [(x + shift, s.replace("cs=", "")) for x, s in c]
        names += [(x + shift, s) for x, s in n]
    pairs.sort(key=lambda c: c["mid"])
    # a gap much wider than the usual pitch separates two networks
    pitch = min(b["mid"] - a["mid"] for a, b in zip(pairs, pairs[1:]))
    nets, cur = [], [pairs[0]]
    for prev, cell in zip(pairs, pairs[1:]):
        if cell["mid"] - prev["mid"] < pitch * 1.5:
            cur.append(cell)
        else:
            nets.append(cur)
            cur = [cell]
    nets.append(cur)
    # every class pair takes the labels of its own network's span
    for net in nets:
        lo, hi = net[0]["lo"], net[-1]["hi"]
        mine = lambda row: [t for t in row if lo - 24 <= t[0] <= hi + 24]
        here_t, here_c = mine(titles) or titles, mine(cs_labels) or cs_labels
        for cell in net:
            cell["title"] = nearest(here_t, cell["mid"])
            cell["cs"] = nearest(here_c, cell["mid"])
        net_name = nearest(mine(names) or names, (lo + hi) / 2)
        for cell in net:
            cell["net"] = net_name
    if keep:
        nets = [[c for c in net if c["title"].startswith(tuple(keep))]
                for net in nets]
        nets = [net for net in nets if net]
    # the source splits one network over several blocks when its
    # experiments use different sizes; here they are one network
    joined = []
    for net in nets:
        if joined and joined[-1][0]["net"] == net[0]["net"]:
            joined[-1] += net
        else:
            joined.append(net)
    if nets_range and isinstance(nets_range[0], str):
        joined = [n for n in joined
                  if " ".join(tidy_name(n[0]["net"])) in nets_range]
    elif nets_range:
        joined = joined[nets_range[0]:nets_range[1]]
    return joined


# ----------------------------- the figure -----------------------------
BAR = 5.5               # the bar width, a little under the 5.98 of the source
BAR_MIN = 3.0           # ... narrowed, but never past this, when a figure
                        # carries too many class pairs to fit otherwise
PAIR_GAP = 4.48         # between class pairs of one class-pair block
CS_GAP = 6.0            # between the class-pair blocks of one network,
                        # so that two $c_s$ labels never run together
NET_GAP = (8.0, 24.0)   # between networks: as wide as the budget allows
HEIGHT = 62.5           # the plot box; its full scale sits at SPAN, and
SPAN = 48.05            # the rest is headroom, as in the source charts
AXIS_L, AXIS_R = 34.0, 34.0   # the tick numbers
LABEL_OFF = 26.0        # the axis names, just clear of the numbers
BUDGET = 389.0          # the plot plus its reserves; the rotated axis names
                        # stick out past them, and the picture then measures
                        # just under the 412.6pt text block

# the caption font of the document, for the axis names and the
# perturbation over each block
CAPTION = r"\fontsize{10.95}{13}\selectfont"
# the class pairs and the network names: clearly bigger than the 6pt of
# the source charts, still under the caption
MIDSIZE = r"\fontsize{9}{10.5}\selectfont"

FILL = {"transfer": "blendtr", "blend": "blendpl", "vhagar": "vhagarcol"}

#: Clearance kept between two neighbouring size labels, in points. Generous
#: on purpose: _text_w only estimates the set width, so the slack has to
#: cover the estimate being a little low.
SIZE_PAD = 7.0


def _size_label(cell):
    _pert, _, size = cell["title"].partition("(")
    return "(" + size if size else ""


def _text_w(s):
    """Rough width of a size label set at MIDSIZE (9pt), in points.

    Digits carry the width, commas and parentheses much less. Only used to
    decide whether two labels would touch, so an estimate is enough.
    """
    return sum(2.3 if c == "," else 3.0 if c in "()" else 4.5 for c in s)


def _size_pads(nets, bar):
    """{(net index, pair index): extra gap} so two size labels never collide.

    A block one class pair wide can be far narrower than the size that names
    it -- conv4's single patch pair is ~14pt under a ~40pt '(1,14,14,3)' --
    and the gap rule only looks at c_s, so two perturbations of one network
    sit a PAIR_GAP apart and their labels run into each other. Widen just
    those boundaries, by just enough: every figure without a collision is
    laid out exactly as before.
    """
    out = {}
    for ni, net in enumerate(nets):
        runs = []
        for pi, cell in enumerate(net):
            lab = _size_label(cell)
            if runs and runs[-1][2] == lab:
                runs[-1][1] = pi
            else:
                runs.append([pi, pi, lab])
        for a, b in zip(runs, runs[1:]):
            na, nb = a[1] - a[0] + 1, b[1] - b[0] + 1
            wa = na * 3 * bar + (na - 1) * PAIR_GAP
            wb = nb * 3 * bar + (nb - 1) * PAIR_GAP
            g = (PAIR_GAP if net[a[1] + 1]["cs"] == net[a[1]]["cs"]
                 else CS_GAP)
            need = (_text_w(a[2]) + _text_w(b[2])) / 2.0 + SIZE_PAD
            natural = wa / 2.0 + g + wb / 2.0
            if need > natural:
                out[(ni, a[1])] = need - natural
    return out


def emit(nets, K):
    pairs = sum(len(n) for n in nets)
    # the gaps a figure needs: one between the class pairs of a block,
    # a wider one between blocks, a wider one still between networks
    blocks = sum(sum(1 for _ in itertools.groupby(n, key=lambda c: c["cs"]))
                 for n in nets)
    reserve = AXIS_L + (AXIS_R if K["right"] else 6.0)
    base_fixed = (pairs - blocks) * PAIR_GAP + (blocks - len(nets)) * CS_GAP \
        + NET_GAP[0] * (len(nets) - 1)
    # The label pads depend on the bar width and the bar width on the pads, so
    # settle them together; it converges at once, the pads being a few points.
    pads, fixed = {}, base_fixed
    for _ in range(3):
        bar = max(BAR_MIN,
                  min(BAR, (BUDGET - reserve - fixed) / (pairs * 3)))
        pads = _size_pads(nets, bar)
        fixed = base_fixed + sum(pads.values())
    bar = min(BAR, (BUDGET - reserve - fixed) / (pairs * 3))
    bar = max(BAR_MIN, bar)
    content = sum(len(n) * 3 * bar for n in nets) + fixed \
        - NET_GAP[0] * (len(nets) - 1)
    if len(nets) > 1:
        room = (BUDGET - reserve - content) / (len(nets) - 1)
        gap = max(NET_GAP[0], min(NET_GAP[1], room))
    else:
        gap = 0.0
    width = content + gap * (len(nets) - 1)
    # the scale of the axis: fixed for a solve-time chart, which always
    # runs to the three-hour timeout, and rounded up to the data for a
    # bound-difference chart, as the source charts do
    full = K["full"]
    if full is None:
        peak = max(v for net in nets for c in net for v in c["val"].values())
        full = min(100.0, max(20.0, math.ceil(peak / 20.0) * 20.0))
    ticks = K["ticks"] or (0, int(full / 2), int(full))
    span = SPAN                                   # the plot's own height
    y = lambda v: v / full * span                 # the chart's unit -> pt
    yp = lambda v: v / PCT_FULL * span            # percent -> pt

    L = []
    add = L.append
    add(r"% ===================================================================")
    add(r"% Written by tools/build_time_figures.py -- do not edit by hand.")
    add(r"% One axis for every experiment of this perturbation, rebuilt from")
    add(r"% the numbers of the pdfs the paper generates, in their colours.")
    add(r"% ===================================================================")
    for name, rgb in K["series"]:
        add(r"\definecolor{%s}{rgb}{%.3f,%.3f,%.3f}" % ((FILL[name],) + rgb))
    add(r"\begin{tikzpicture}[x=1pt,y=1pt,font=%s]" % MIDSIZE)
    add(r"  \fill[black!3] (0,0) rectangle (%.2f,%.2f);" % (width, HEIGHT))

    x = 0.0
    spans = []          # (kind, key, from, to) for the three label rows
    for ni, net in enumerate(nets):
        net_start = x
        for pi, cell in enumerate(net):
            start = x
            for name, _ in K["series"]:
                top = y(min(cell["val"].get(name, 0.0), full))
                add(r"  \fill[%s] (%.2f,0) rectangle (%.2f,%.2f);"
                    % (FILL[name], x, x + bar, top))
                if name == "blend":      # hatched, as in the legend
                    add(r"  \fill[pattern=north east lines,pattern color=%s] "
                        r"(%.2f,0) rectangle (%.2f,%.2f);"
                        % (FILL["transfer"], x, x + bar, top))
                add(r"  \draw[black!60,line width=0.2pt] "
                    r"(%.2f,0) rectangle (%.2f,%.2f);" % (x, x + bar, top))
                x += bar
            if K["line"] and len(cell["pct"]) == 3:
                pts = " -- ".join(
                    "(%.2f,%.2f)" % (start + (i + 0.5) * bar, yp(p))
                    for i, p in enumerate(cell["pct"]))
                add(r"  \draw[black,line width=0.3pt] %s;" % pts)
                for i, p in enumerate(cell["pct"]):
                    add(r"  \fill[black] (%.2f,%.2f) circle (0.75pt);"
                        % (start + (i + 0.5) * bar, yp(p)))
            pert, _, size = cell["title"].partition("(")
            spans.append(["title", tidy_pert(pert.strip()), start, x])
            spans.append(["size", "(" + size if size else "", start, x])
            spans.append(["cs", cell["cs"], start, x])
            if pi < len(net) - 1:
                x += PAIR_GAP if net[pi + 1]["cs"] == cell["cs"] else CS_GAP
                x += pads.get((ni, pi), 0.0)
        spans.append(["net", net[0]["net"], net_start, x])
        if ni < len(nets) - 1:
            x += gap

    # the frame, the rule at the full scale, and the axes
    add(r"  \draw[black!60,line width=0.3pt] (0,0) rectangle (%.2f,%.2f);"
        % (width, HEIGHT))
    add(r"  \draw[black,dashed,line width=0.3pt] (0,%.2f) -- (%.2f,%.2f);"
        % (y(full), width, y(full)))
    for v in ticks:
        add(r"  \draw[black!60,line width=0.3pt] (0,%.2f) -- (-2,%.2f) "
            r"node[left,inner sep=1pt,font=%s] {%d};" % (y(v), y(v), CAPTION, v))
    add(r"  \node[rotate=90,anchor=south,font=%s] at (-%.1f,%.2f) {%s};"
        % (CAPTION, LABEL_OFF, HEIGHT / 2, K["name"]))
    if K["right"]:          # the tightness, over the solve-time bars
        for v in (0, 50, 100):
            add(r"  \draw[black!60,line width=0.3pt] (%.2f,%.2f) -- (%.2f,%.2f) "
                r"node[right,inner sep=1pt,font=%s] {%d};"
                % (width, yp(v), width + 2, yp(v), CAPTION, v))
        add(r"  \node[rotate=90,anchor=north,font=%s] at (%.2f,%.2f) "
            r"{$\delta_u-\delta_l$ (\%%$\delta_{\max}$)};"
            % (CAPTION, width + LABEL_OFF, HEIGHT / 2))

    labels = merge(spans)
    # a figure that carries two perturbations brackets each of them, so
    # that it is plain which sizes belong to which
    braced = len({key for k, key, _, _ in labels if k == "title"}) > 1
    # a single size over the whole figure needs no bracket of its own
    size_braced = sum(1 for k, _, _, _ in labels if k == "size") > 1
    size_top = HEIGHT + (3.0 if size_braced else 1.5)
    name_y = -15.0
    # the three label rows, each label over or under the block it covers
    for kind, key, lo, hi in labels:
        mid = (lo + hi) / 2
        if kind == "size":
            if size_braced:   # bracketed over its own blocks
                add(r"  \draw[black,line width=0.25pt] "
                    r"(%.2f,%.2f) -- (%.2f,%.2f) -- (%.2f,%.2f) -- (%.2f,%.2f);"
                    % (lo, HEIGHT + 1.5, lo, HEIGHT + 3.0,
                       hi, HEIGHT + 3.0, hi, HEIGHT + 1.5))
            add(r"  \node[above,inner sep=1.5pt,font=%s] at (%.2f,%.2f) {%s};"
                % (MIDSIZE, mid, size_top, key))
        elif kind == "title":
            if braced:      # which blocks this perturbation covers
                add(r"  \draw[black,line width=0.25pt] "
                    r"(%.2f,%.2f) -- (%.2f,%.2f) -- (%.2f,%.2f) -- (%.2f,%.2f);"
                    % (lo, size_top + 11.5, lo, size_top + 13.0,
                       hi, size_top + 13.0, hi, size_top + 11.5))
            add(r"  \node[above,inner sep=1.5pt,font=%s] at (%.2f,%.2f) {%s};"
                % (CAPTION, mid,
                   size_top + (13.0 if braced else 11.5), key))
        elif kind == "cs":
            add(r"  \draw[black,line width=0.25pt] "
                r"(%.2f,-1.5) -- (%.2f,-3) -- (%.2f,-3) -- (%.2f,-1.5);"
                % (lo, lo, hi, hi))
            add(r"  \node[below,inner sep=1.5pt,font=%s] at (%.2f,-3) "
                r"{$c_s{=}%s$};" % (MIDSIZE, mid, key))
        else:
            arch, data = NAME_FIXUPS.get(tidy_name(key), tidy_name(key))
            add(r"  \node[below,align=center,inner sep=1pt,font=%s\bfseries] "
                r"at (%.2f,%.2f) {%s\\%s};"
                % (MIDSIZE, mid, name_y, arch, data))
    add(r"\end{tikzpicture}")
    return ("\n".join(L) + "\n",
            width + reserve)


def merge(spans):
    """Join the neighbouring blocks that carry the same label.

    The three rows interleave in the order the bars were drawn, so each
    row is merged on its own.
    """
    # a perturbation carries over the gap between two networks; a class
    # pair of the same name in the next network does not
    reach = {"title": 30.0, "size": 30.0, "cs": 6.0, "net": 6.0}
    out = []
    for kind in ("title", "size", "cs", "net"):
        run = []
        for sp in (s for s in spans if s[0] == kind):
            if run and run[-1][1] == sp[1] and sp[2] - run[-1][3] < reach[kind]:
                run[-1][3] = sp[3]
            else:
                run.append(list(sp))
        out += run
    return out


CORRECTIONS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "conv4_corrections.json")


def load_corrections(enabled=True):
    """The conv4 overrides, or {} when disabled or absent.

    The source pdfs still carry conv4's pre-fix tau=0.5 transfer runs, so the
    numbers recovered from them are corrected here before anything is drawn.
    tools/emit_conv4_corrections.py writes the file from the pinned source
    map, so these figures and the per-cell tables cannot drift apart.
    """
    if not enabled or not os.path.exists(CORRECTIONS):
        return {}
    import json
    with open(CORRECTIONS, encoding="utf-8") as fh:
        return json.load(fh)


def apply_corrections(nets, K, corr, kind):
    """Override conv4's tau=0.5 numbers and re-partition the pair that moved.

    A class pair where all three methods reach the cap is a bound-difference
    instance, not a solve-time one: the two figure families partition the
    pairs between them. Correcting the numbers can therefore move a pair, and
    conv4/patch/c_s=0/c_t=1 is exactly that case -- its transfer run went from
    168.5 min to a 180 min timeout, so it leaves the solve-time figure and
    joins the bound-difference one.

    Cells carry no c_t of their own, so a pair is addressed by its position
    left to right inside its (title, c_s) group, which IS c_t ascending.
    """
    if not corr:
        return nets, []
    fixes, moved = corr.get(kind, {}), []
    for net in nets:
        if net[0]["net"] != corr["net"]:
            continue
        seen = {}
        for cell in net:
            g = (cell["title"], str(cell["cs"]))
            idx = seen[g] = seen.get(g, -1) + 1
            fix = fixes.get(f"{g[0]}|{g[1]}|{idx}")
            if not fix:
                continue
            if kind == "time":
                cell["val"]["transfer"] = fix["transfer_min"]
                if len(cell["pct"]) == 3:
                    cell["pct"][0] = fix["transfer_pct"]
            else:
                cell["val"]["transfer"] = fix["transfer_pct"]

    if kind == "time":
        full = K["full"]
        for net in nets:
            keep = []
            for cell in net:
                if all(v >= full - 1e-6 for v in cell["val"].values()):
                    moved.append((cell["net"], cell["title"], cell["cs"]))
                    continue
                keep.append(cell)
            net[:] = keep
        return [n for n in nets if n], moved

    # bd: add the pairs that crossed over, in the canonical perturbation order
    for ins in corr.get("bd_insert", ()):
        for net in nets:
            if net[0]["net"] != corr["net"]:
                continue
            cell = {"lo": 0.0, "hi": 0.0, "mid": 0.0, "pct": [],
                    "val": dict(ins["val"]), "title": ins["title"],
                    "cs": ins["cs"], "net": corr["net"]}
            at = next((i for i, c in enumerate(net)
                       if _pert_rank(c["title"]) > _pert_rank(ins["title"])),
                      len(net))
            net.insert(at, cell)
            moved.append((corr["net"], ins["title"], ins["cs"]))
            break
    return nets, moved


#: The order the paper lists perturbations in (_AAAI_PERT_ORDER), so an
#: inserted block lands where a regenerated figure would have put it.
_PERT_ORDER = ("linf", "brightness", "contrast", "patch", "occ",
               "translation", "rotation")


def _pert_rank(title):
    name = title.split("(")[0].strip()
    name = {"occlusion": "occ"}.get(name, name)
    return _PERT_ORDER.index(name) if name in _PERT_ORDER else len(_PERT_ORDER)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="emit with corrections OFF, for diffing against the "
                         "committed figures")
    args = ap.parse_args()
    corr = load_corrections(not args.verify)
    if corr:
        print("[time-figures] corrections: %d time, %d bd, %d moved pair(s)"
              % (len(corr.get("time", {})), len(corr.get("bd", {})),
                 len(corr.get("bd_insert", ()))))
    elif not args.verify:
        print("[time-figures] no corrections file -- drawing the pdfs as-is")

    for out, sources, selections, kind in FIGURES:
        K = KINDS[kind]
        nets = [net for keep, rng in selections
                for net in collect(sources, keep, rng, K)]
        nets, moved = apply_corrections(nets, K, corr, kind)
        for m in moved:
            print("     moved: %s %s c_s=%s" % m)
        tex, total = emit(nets, K)
        with open(os.path.join(GRAPHICS, out), "w") as fh:
            fh.write(tex)
        print("[time-figures] %s: %d networks, %d class pairs, %.1fpt wide"
              % (out, len(nets), sum(len(n) for n in nets), total))
        for net in nets:
            print("     %-24s %d class pairs"
                  % (" ".join(tidy_name(net[0]["net"])), len(net)))


if __name__ == "__main__":
    sys.exit(main())
