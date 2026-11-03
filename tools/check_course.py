#!/usr/bin/env python3
"""Course checker: structure, link, forbidden-term and Mermaid checks for the markdown course.

Usage: python3 tools/check_course.py [--mermaid] [--allow-planned] [--root DIR] [PATH ...]
Exit 0 when there are no errors; otherwise exit 1 with one `path:line: CODE message` line per error.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MERMAID_CLI = "@mermaid-js/mermaid-cli@11.4.0"

REQUIRED_HEADINGS = {
    "concept": ["The Problem", "In the Interview", "Common Mistakes", "Key Takeaways"],
    "tech": [
        "When to Use It (and When Not To)", "How It Works", "Key Numbers",
        "Interview Follow-ups", "Alternatives", "Key Takeaways",
    ],
    "breakdown": [
        "Understanding the Problem", "Requirements", "Sources & Volume", "High-Level Design",
        "Data Model", "Pipeline Design", "Potential Deep Dives", "Monitoring & SLAs",
        "Final Design", "What's Expected at Each Level", "Related Lessons",
    ],
    "quiz": ["Questions"],
}
LEVEL_SECTION = "What's Expected at Each Level"
LEVEL_HEADINGS = ["Mid-level", "Senior", "Staff+"]
WORD_RANGES = {"concept": (1500, 3000), "tech": (2000, 3500), "breakdown": (3500, 6000)}
FRAMEWORK_STEPS = [
    "Requirements", "Sources & volume", "High-level architecture", "Data model",
    "Pipeline design", "Deep dives", "Monitoring & SLAs",
]
PLANNED_RE = re.compile(r"^0[1-6]-[a-z-]+/\d\d-[a-z0-9-]+\.md$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})\s*([^\s`]*)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
QUIZ_Q_RE = re.compile(r"^###\s+Q\d+\.")


def lesson_type(path: Path) -> str | None:
    """Return concept | tech | breakdown | quiz, or None for README/GLOSSARY/other files."""
    path = Path(path)
    if path.name.lower() in ("readme.md", "glossary.md"):
        return None
    m = re.match(r"^0([1-6])-", path.parent.name)
    if not m:
        return None
    if re.search(r"quiz\.md$", path.name):
        return "quiz"
    n = int(m.group(1))
    return "concept" if n <= 3 else "tech" if n == 4 else "breakdown"


class Report:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.errors = 0

    def error(self, path, line, code, msg) -> None:
        self.errors += 1
        self.lines.append(f"{path}:{line}: {code} {msg}")

    def warn(self, path, line, msg) -> None:
        self.lines.append(f"{path}:{line}: WARN {msg}")


def parse_lines(text: str):
    """Yield (lineno, line, in_fence, fence_info) for each line; fence delimiter lines count as in_fence."""
    fence = None
    for i, line in enumerate(text.splitlines(), 1):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = (m.group(1)[0], len(m.group(1)))
                yield i, line, True, m.group(2)
                continue
            yield i, line, False, ""
        else:
            yield i, line, True, ""
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] and not m.group(2):
                fence = None


def load_forbidden(root: Path, report: Report):
    f = root / ".forbidden-terms"
    if not f.is_file():
        report.error(".forbidden-terms", 0, "FORBIDDEN", ".forbidden-terms missing; cannot check forbidden terms")
        return []
    pats = []
    for n, raw in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        try:
            pats.append(re.compile(s, re.IGNORECASE))
        except re.error as e:
            report.error(".forbidden-terms", n, "FORBIDDEN", f"invalid regex: {e}")
    return pats


def collect_files(paths, root: Path):
    out: list[Path] = []
    if not paths:
        for p in sorted(root.rglob("*.md")):
            rel = p.relative_to(root).parts
            if any(part.startswith(".") for part in rel[:-1]) or rel[0] in ("docs", "tools"):
                continue
            out.append(p)
        return out
    for arg in paths:
        p = Path(arg).resolve()
        if p.is_dir():
            for q in sorted(p.rglob("*.md")):
                if any(part.startswith(".") for part in q.relative_to(p).parts[:-1]):
                    continue
                out.append(q)
        elif p.is_file():
            out.append(p)
        else:
            out.append(p)  # reported as unreadable later
    return out


def display(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


def check_links(p, rel, parsed, root, allow_planned, report):
    for n, line, in_fence, _ in parsed:
        if in_fence:
            continue
        scan = re.sub(r"`[^`]*`", "", line)
        for m in LINK_RE.finditer(scan):
            target = m.group(1)
            if target.startswith("#") or target.lower().startswith("mailto:"):
                continue
            if re.match(r"^https?://", target, re.I):
                report.error(rel, n, "EXTERNAL_LINK", f"external link not allowed: {target}")
                continue
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            path_part = re.split(r"[#?]", target, maxsplit=1)[0]
            if not path_part:
                continue
            dest = (root / path_part.lstrip("/")) if path_part.startswith("/") else (p.parent / path_part)
            dest = Path(Path(dest).resolve())
            if dest.exists():
                continue
            try:
                drel = dest.relative_to(root).as_posix()
            except ValueError:
                drel = ""
            if allow_planned and PLANNED_RE.match(drel):
                report.warn(rel, n, f"link to planned lesson not yet written: {target}")
            else:
                report.error(rel, n, "BROKEN_LINK", f"link target not found: {target}")


def check_structure(p, rel, ltype, parsed, text, report):
    headings = [(n, len(m.group(1)), m.group(2)) for n, line, f, _ in parsed
                if not f and (m := HEADING_RE.match(line))]
    h1s = [h for h in headings if h[1] == 1]
    first = parsed[0][1] if parsed else ""
    if not (first.startswith("# ") and len(h1s) == 1 and h1s[0][0] == 1):
        report.error(rel, 1, "MISSING_H1", "file must start with exactly one '# ' H1 on line 1")

    h2 = [h[2] for h in headings if h[1] == 2]
    req = REQUIRED_HEADINGS[ltype]
    it = iter(h2)
    missing = [r for r in req if not any(h == r for h in it)]
    if missing:
        report.error(rel, 1, "HEADINGS",
                     f"required '##' headings missing or out of order (starting at '{missing[0]}'); expected: " + " | ".join(req))

    if ltype == "breakdown":
        idx = next((i for i, h in enumerate(headings) if h[1] == 2 and h[2] == LEVEL_SECTION), None)
        if idx is not None:
            sect = []
            for h in headings[idx + 1:]:
                if h[1] <= 2:
                    break
                if h[1] == 3:
                    sect.append(h[2])
            it = iter(sect)
            miss = [x for x in LEVEL_HEADINGS if not any(h == x for h in it)]
            if miss:
                report.error(rel, headings[idx][0], "LEVELS",
                             f"missing or out-of-order '###' heading(s) under '{LEVEL_SECTION}': " + ", ".join(miss))

    if ltype == "quiz":
        qs = [n for n, line, f, _ in parsed if not f and QUIZ_Q_RE.match(line)]
        if not 10 <= len(qs) <= 15:
            report.error(rel, 1, "QUIZ_COUNT", f"quiz must have 10-15 questions, found {len(qs)}")
        bounds = qs + [len(parsed) + 1]
        for k, q in enumerate(qs):
            body = [line for n, line, f, _ in parsed if q < n < bounds[k + 1] and not f]
            opens = sum(len(re.findall(r"<details\b", b)) for b in body)
            closes = sum(len(re.findall(r"</details>", b)) for b in body)
            if opens != 1 or closes != 1:
                report.error(rel, q, "QUIZ_DETAILS",
                             f"question needs exactly one <details> block (found {opens} opening, {closes} closing)")

    if ltype == "concept" and p.name == "02-delivery-framework.md" and p.parent.name == "01-the-framework":
        rows = []
        for n, line, f, _ in parsed:
            if not f and line.strip().startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) >= 2:
                    rows.append(cells[1].lower())
        steps = [s for s in FRAMEWORK_STEPS if any(r.startswith(s.lower()) for r in rows)]
        if steps != FRAMEWORK_STEPS:
            lost = [s for s in FRAMEWORK_STEPS if s not in steps]
            report.error(rel, 1, "HEADINGS", "delivery framework table must contain the 7 steps; missing: " + ", ".join(lost))

    if ltype in WORD_RANGES:
        words = len(re.findall(r"\S+", "\n".join(line for _, line, f, _ in parsed if not f)))
        lo, hi = WORD_RANGES[ltype]
        if not lo <= words <= hi:
            report.warn(rel, 1, f"word count {words} outside {lo}-{hi} for {ltype} lesson")


PARSE_MARKERS = ("Parse error", "Syntax error", "Lexical error", "Expecting ", "UnknownDiagramError", "No diagram type detected")


def check_mermaid(rel, parsed, report, state) -> None:
    blocks, cur = [], None
    for n, line, in_fence, info in parsed:
        if in_fence and info.lower() == "mermaid" and cur is None:
            cur = (n, [])
        elif cur is not None:
            if in_fence and FENCE_RE.match(line) and not FENCE_RE.match(line).group(2):
                blocks.append(cur)
                cur = None
            else:
                cur[1].append(line)
    for start, body in blocks:
        if state.get("unavailable"):
            return
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "d.mmd"
            src.write_text("\n".join(body) + "\n", encoding="utf-8")
            cmd = ["npx", "-y", MERMAID_CLI, "-i", str(src), "-o", str(src) + ".svg", "-q"]
            pcfg = Path(td) / "puppeteer.json"
            pcfg.write_text('{"args": ["--no-sandbox"]}', encoding="utf-8")
            cmd += ["-p", str(pcfg)]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            except FileNotFoundError:
                state["unavailable"] = True
                report.error(rel, start, "MERMAID", "mermaid-cli unavailable: npx not found")
                return
            except subprocess.TimeoutExpired:
                state["unavailable"] = True
                report.error(rel, start, "MERMAID", "mermaid-cli unavailable: timed out after 300s")
                return
            if r.returncode != 0:
                out = (r.stderr + "\n" + r.stdout).strip()
                if any(mk in out for mk in PARSE_MARKERS):
                    first = next((l for l in out.splitlines() if any(mk in l for mk in PARSE_MARKERS)), out.splitlines()[0])
                    report.error(rel, start, "MERMAID", f"invalid Mermaid diagram: {first.strip()}")
                else:
                    state["unavailable"] = True
                    reason = next((l.strip() for l in out.splitlines() if l.strip()), "unknown failure")
                    report.error(rel, start, "MERMAID", f"mermaid-cli unavailable: {reason}")
                    return


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mermaid", action="store_true", help="render each ```mermaid block with mermaid-cli")
    ap.add_argument("--allow-planned", action="store_true", help="downgrade links to unwritten curriculum lessons to WARN")
    ap.add_argument("--root", default=str(REPO_ROOT), help="repo root (default: parent of tools/)")
    ap.add_argument("paths", nargs="*", metavar="PATH")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()

    report = Report()
    pats = load_forbidden(root, report)
    state: dict = {}
    for p in collect_files(args.paths, root):
        rel = display(p, root)
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            report.error(rel, 0, "BROKEN_LINK", f"cannot read file: {e}")
            continue
        parsed = list(parse_lines(text))
        for n, line, _, _ in parsed:
            if any(pt.search(line) for pt in pats):
                report.error(rel, n, "FORBIDDEN", "line matches a forbidden term")
        check_links(p, rel, parsed, root, args.allow_planned, report)
        try:
            lt = lesson_type(p.relative_to(root))
        except ValueError:
            lt = lesson_type(p)
        if lt:
            check_structure(p, rel, lt, parsed, text, report)
        if args.mermaid:
            check_mermaid(rel, parsed, report, state)

    for line in report.lines:
        print(line)
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
