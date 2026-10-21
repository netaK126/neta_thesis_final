#!/usr/bin/env python3
"""Compile the thesis.

Runs, in the directory of this script:

    latexmk -xelatex thesis

The Technion class needs xelatex (for the Hebrew), biber (for the
bibliography) and makeglossaries (for the notation list), each of them
the right number of times and in the right order. latexmk works that
out from .latexmkrc, which also sends the auxiliary files to build/.
(Not aux/: that name is a reserved device name on Windows, which
stops the engine from creating the directory.)

latexmk and makeglossaries are perl scripts, and MiKTeX will not run
them unless a perl interpreter is on the PATH. Windows has none of its
own, so the script looks for one and puts it on the PATH of the build
only. Nothing outside the build sees the change.

A run that fails is tried once more from clean, because a stale
auxiliary file left by an interrupted run, or by a package that is no
longer loaded, breaks every later run with an error that points
somewhere else entirely. Pass --clean to start from clean in the first
place.

The script prints one line: where the pdf is, or why the compilation
failed.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
JOB = "thesis"
BUILD_DIR = HERE / "build"
PDF = HERE / (JOB + ".pdf")

COMMAND = ["latexmk", "-xelatex", "-interaction=nonstopmode", JOB]

TIMEOUT_SECONDS = 900


def fail(reason):
    print("Failed to compile due to {}".format(reason))
    sys.exit(1)


def tex_error():
    """The first error reported in the log, with the line it occurred on."""
    try:
        lines = (BUILD_DIR / (JOB + ".log")).read_text(errors="replace").splitlines()
    except OSError:
        return None
    for i, line in enumerate(lines):
        if line.startswith("!"):
            error = line.lstrip("! ").strip()
            for following in lines[i + 1:i + 8]:
                if following.startswith("l."):
                    return "{} ({})".format(error, following.strip())
            return error
    return None


def tool_error():
    """The first complaint of biber or of makeglossaries.

    xelatex itself reports nothing when one of them fails, so without
    this a missing bibliography entry or a broken glossary would be
    reported only as an exit status.
    """
    for suffix, marker, tool in ((".blg", "ERROR", "biber"),
                                 (".glg", "Error", "makeglossaries")):
        try:
            lines = (BUILD_DIR / (JOB + suffix)).read_text(errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            if marker in line:
                return "{}: {}".format(tool, line.strip())
    return None


def unresolved():
    """What the run left unresolved, if anything.

    A citation key that is not in the bibliography does not fail the
    build: biber warns, biblatex prints the key in bold and carries on.
    The same holds for a reference to a label that does not exist.
    Both are worth saying out loud, so that an empty bibliography or a
    dangling cross-reference is never mistaken for a clean run.
    """
    notes = []

    try:
        blg = (BUILD_DIR / (JOB + ".blg")).read_text(errors="replace")
    except OSError:
        blg = ""
    missing = len(re.findall(r"I didn't find a database entry for", blg))
    if missing:
        notes.append("{} citations are not in the bibliography".format(missing))

    try:
        log = (BUILD_DIR / (JOB + ".log")).read_text(errors="replace")
    except OSError:
        log = ""
    dangling = len(re.findall(r"Reference `", log))
    if dangling:
        notes.append("{} references are undefined".format(dangling))

    return notes


# Where a perl interpreter hides on a Windows machine that has none of
# its own. Git for Windows always ships one; Strawberry Perl is the
# usual standalone. On Linux perl is on the PATH already and none of
# this applies.
PERL_DIRECTORIES = (
    r"C:\Strawberry\perl\bin",
    r"C:\Program Files\Git\usr\bin",
    r"C:\Program Files (x86)\Git\usr\bin",
)


def perl_directory():
    """A directory holding perl.exe, or None if there is none to find."""
    for candidate in PERL_DIRECTORIES:
        if (Path(candidate) / "perl.exe").exists():
            return candidate
    # git is on the PATH more often than it sits in one of the places
    # above, and it keeps perl two directories up from git.exe
    git = shutil.which("git")
    if git:
        beside = Path(git).resolve().parent.parent / "usr" / "bin"
        if (beside / "perl.exe").exists():
            return str(beside)
    return None


def environment():
    """The environment to build in, with perl on the PATH.

    Appended rather than prepended: the directory perl lives in also
    holds unix tools whose names collide with the Windows ones, and the
    Windows ones should go on winning.
    """
    env = os.environ.copy()
    if shutil.which("perl") is None:
        directory = perl_directory()
        if directory:
            env["PATH"] = env.get("PATH", "") + os.pathsep + directory
    return env


def run_latexmk():
    """One run of latexmk. Returns None if it timed out."""
    try:
        return subprocess.run(
            COMMAND,
            cwd=str(HERE),
            env=environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=TIMEOUT_SECONDS,
            # not universal_newlines, which decodes with the locale
            # encoding: on Windows that is cp1252, and the Hebrew
            # latexmk echoes back is utf-8, which it cannot decode
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        return None


def clean():
    """Remove everything the build generates."""
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)


def succeeded(run):
    return run is not None and run.returncode == 0 \
        and (BUILD_DIR / (JOB + ".pdf")).exists()


def main():
    for tool in ("latexmk", "xelatex", "biber", "makeglossaries"):
        if shutil.which(tool) is None:
            fail("{} is not installed".format(tool))

    # latexmk and makeglossaries are perl scripts, and MiKTeX reports a
    # missing perl only as an exit status, which reads as a failure of
    # the thesis rather than of the machine
    if shutil.which("perl", path=environment()["PATH"]) is None:
        fail("perl is not installed, and latexmk and makeglossaries are "
             "perl scripts. Install Strawberry Perl, or Git for Windows, "
             "which ships one")

    if "--clean" in sys.argv[1:]:
        clean()

    run = run_latexmk()
    if not succeeded(run):
        # a stale auxiliary file is the usual reason, so try once from clean
        # before believing the error
        clean()
        run = run_latexmk()

    if run is None:
        fail("latexmk did not finish within {} seconds".format(TIMEOUT_SECONDS))
    if not succeeded(run):
        fail(tex_error() or tool_error()
             or "latexmk exited with status {}".format(run.returncode))

    # latexmk keeps its output next to the auxiliary files; the pdf is
    # easier to find next to the source it was built from
    shutil.copyfile(BUILD_DIR / (JOB + ".pdf"), PDF)

    notes = unresolved()
    if notes:
        print("Compiled neta thesis into {}, but {}".format(PDF, ", and ".join(notes)))
    else:
        print("Compiled neta thesis into {}".format(PDF))


if __name__ == "__main__":
    main()
