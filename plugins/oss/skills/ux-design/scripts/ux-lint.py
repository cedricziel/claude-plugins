#!/usr/bin/env python3
"""Deterministic UI slop linter for the ux-design skill.

Catches the failures that are greppable: shipped placeholder content,
non-semantic click targets, deleted focus rings, images without alt, hardcoded
colour next to a real token set, off-scale spacing, AI-marketing vocabulary, and
the accessibility footguns the skill's references warn about.

It does not judge taste and it does not call a model. Findings are either
`block` (unambiguous defect) or `warn` (worth a look).

Usage:
  ux-lint.py FILE...
  ux-lint.py --staged
  ux-lint.py --snippet --filename src/Hero.tsx    # lints stdin

Exit codes: 0 no blocking finding, 2 blocking finding, 1 usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

UI_SUFFIXES = {
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".astro",
}

EXEMPT_PARTS = (
    "node_modules", "/dist/", "/build/", "/.next/", "/vendor/",
    "/__tests__/", "/fixtures/", "/fixture/", "/mocks/", "/e2e/",
    "/examples/", "/example/", "/stories/", "/.storybook/",
)
EXEMPT_SUFFIXES = (".test.js", ".test.jsx", ".test.ts", ".test.tsx",
                   ".spec.js", ".spec.jsx", ".spec.ts", ".spec.tsx",
                   ".stories.js", ".stories.jsx", ".stories.ts", ".stories.tsx",
                   ".min.css", ".min.js")

PLACEHOLDERS = (
    "lorem ipsum", "john doe", "jane doe", "acme corp", "acme inc",
    "jane@example.com", "john@example.com", "your company name",
    "todo copy", "replace me",
)

SLOP_WORDS = (
    "seamless", "effortlessly", "supercharge", "unleash", "revolutionize",
    "revolutionise", "game-chang", "cutting-edge", "next-generation",
    "world-class", "state-of-the-art", "elevate your", "empower your",
    "transform your", "to the next level", "unlock the power",
)

SPACING_SCALE = {0, 1, 2, 3, 4, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 56, 64, 72, 80, 96, 128}

TOKEN_MARKERS = ("tailwind.config", "tokens.json", "design-tokens", "theme.css", "globals.css")

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]")
QUOTED_RE = re.compile(r'"[^"\n]*"|\'[^\'\n]*\'|`[^`\n]*`')
JSX_TEXT_RE = re.compile(r">([^<>]{2,})<")


@dataclass
class Finding:
    file: str
    line: int
    rule: str
    severity: str
    message: str


def is_exempt(path: Path) -> bool:
    posix = path.as_posix()
    if path.suffix not in UI_SUFFIXES:
        return True
    if posix.endswith(EXEMPT_SUFFIXES):
        return True
    return any(part in f"/{posix.lstrip('/')}" for part in EXEMPT_PARTS)


def repo_root(path: Path) -> Path:
    try:
        out = subprocess.run(
            ["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return path.parent


def has_tokens(root: Path, path: Path) -> bool:
    """True when the repo ships a real token source, so a raw hex is drift.

    Bounded on purpose: this runs on every edit, so it checks root and the
    usual style directories (plus one level of packages) and stops.
    """
    if "token" in path.name.lower() or path.name in {"theme.css", "globals.css"}:
        return False
    candidates = [root, root / "src", root / "app", root / "styles",
                  root / "src" / "styles", root / "app" / "styles"]
    for directory in candidates:
        if not directory.is_dir():
            continue
        for marker in TOKEN_MARKERS:
            try:
                if any(directory.glob(marker + "*")):
                    return True
            except OSError:
                continue
    try:
        return any((root / "packages").glob("*/tailwind.config.*"))
    except OSError:
        return False


def visible_spans(line: str) -> list[tuple[int, int]]:
    spans = [m.span() for m in QUOTED_RE.finditer(line)]
    spans += [m.span(1) for m in JSX_TEXT_RE.finditer(line)]
    return spans


def in_visible_text(line: str, start: int) -> bool:
    return any(lo <= start < hi for lo, hi in visible_spans(line))


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def line_rules(text: str, path: Path, rel: str, tokens: bool) -> list[Finding]:
    out: list[Finding] = []
    lower_lines = text.lower().splitlines()

    for number, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        for word in PLACEHOLDERS:
            start = lowered.find(word)
            if start >= 0 and in_visible_text(line, start):
                out.append(Finding(rel, number, "placeholder-copy", "block",
                                   f'"{word}" is shipped placeholder content. Use realistic content or remove the element.'))
                break
        for word in SLOP_WORDS:
            start = lowered.find(word)
            if start >= 0 and in_visible_text(line, start):
                out.append(Finding(rel, number, "slop-copy", "warn",
                                   f'"{word}" is marketing filler. Say the concrete claim instead.'))
                break
        if EMOJI_RE.search(line) and in_visible_text(line, EMOJI_RE.search(line).start()):
            out.append(Finding(rel, number, "emoji-in-copy", "warn",
                               "Emoji in interface copy reads as decoration. Remove it or make it an icon with a label."))
        caps = re.search(r"[A-Z]{2,}(?:\s+[A-Z]{2,})+", line)
        if caps and in_visible_text(line, caps.start()):
            out.append(Finding(rel, number, "all-caps", "warn",
                               "Multi-word capitals slow reading. Use sentence case."))
        if path.suffix in {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".astro"}:
            if re.search(r">[^<>]*![^<>]*<", line):
                out.append(Finding(rel, number, "exclamation", "warn",
                                   "Exclamation marks in interface copy add pressure. Delete it and let the fact carry."))
        if re.search(r"tabIndex\s*=\s*\{?\s*[\"']?[1-9]\d*", line):
            out.append(Finding(rel, number, "positive-tabindex", "warn",
                               "Positive tabindex breaks DOM tab order. Use DOM order instead."))
        if re.search(r"\bmaxLength\b|\bmaxlength\b", line):
            out.append(Finding(rel, number, "maxlength", "warn",
                               "maxlength truncates pasted input silently. Validate the value instead."))
        if re.search(r"\[-?\d+px\]", line):
            num = re.search(r"\[(-?\d+)px\]", line)
            if num and abs(int(num.group(1))) not in SPACING_SCALE:
                out.append(Finding(rel, number, "off-scale-spacing", "warn",
                                   f"Arbitrary {num.group(1)}px breaks the spacing scale. Use a token."))

    # Tag-level rules need the whole element, which may span lines.
    for match in re.finditer(r"<img\b[^>]*>", text, re.S | re.I):
        if not re.search(r"\balt\s*=", match.group(0), re.I):
            out.append(Finding(rel, line_of(text, match.start()), "img-no-alt", "block",
                               "<img> with no alt attribute: add alt, or alt=\"\" when decorative."))

    for match in re.finditer(r"<(div|span)\b([^>]*)>", text, re.S | re.I):
        attrs = match.group(2)
        if re.search(r"onClick|@click|v-on:click", attrs) and not re.search(r"\brole\s*=", attrs):
            out.append(Finding(rel, line_of(text, match.start()), "non-semantic-click", "block",
                               f"<{match.group(1)}> with a click handler and no role: use <button> or add role and keyboard handling."))

    for match in re.finditer(r"<input\b[^>]*>", text, re.S | re.I):
        if re.search(r"type\s*=\s*[\"'{]*number", match.group(0), re.I):
            out.append(Finding(rel, line_of(text, match.start()), "number-input", "warn",
                               'Avoid <input type="number">: use type="text" with inputmode="numeric".'))

    for match in re.finditer(r"<a\b[^>]*target\s*=\s*[\"']_blank[\"'][^>]*>", text, re.S | re.I):
        if not re.search(r"\brel\s*=", match.group(0), re.I):
            out.append(Finding(rel, line_of(text, match.start()), "unsafe-blank", "warn",
                               'target="_blank" needs rel="noopener noreferrer".'))

    # Whole-file rules.
    if path.suffix in {".css", ".scss", ".sass", ".less"} or "<style" in text:
        if re.search(r"outline\s*:\s*(none|0)\b", text) and not re.search(r":focus", text):
            offset = re.search(r"outline\s*:\s*(none|0)\b", text).start()
            out.append(Finding(rel, line_of(text, offset), "focus-removed", "block",
                               "outline removed with no :focus replacement: keyboard users lose their place. Add a focus-visible ring."))
        if re.search(r"(^|[^-\w])(animation|transition)\s*:", text) and "prefers-reduced-motion" not in text:
            out.append(Finding(rel, 1, "motion-no-reduced", "warn",
                               "Animation without a prefers-reduced-motion block. Add the override."))

    if tokens:
        for number, line in enumerate(text.splitlines(), start=1):
            hexes = re.findall(r"#[0-9a-fA-F]{3,8}\b", line)
            looks_like_color = re.search(r"color|background|border|fill|stroke|shadow|gradient", line, re.I)
            if hexes and looks_like_color:
                out.append(Finding(rel, number, "raw-color", "warn",
                                   f"Raw colour {hexes[0]} in a repo with design tokens. Use the semantic token."))
                break

    if re.search(r"padding|margin|gap", text):
        for number, line in enumerate(text.splitlines(), start=1):
            for value in re.findall(r"(?:padding|margin|gap)[^:;\n]*:\s*([^;{}\n]+)", line, re.I):
                px = [int(n) for n in re.findall(r"(\d+)px", value)]
                off = [n for n in px if n not in SPACING_SCALE]
                if off:
                    out.append(Finding(rel, number, "off-scale-spacing", "warn",
                                       f"{off[0]}px is not on the spacing scale. Use a token."))
                    break

    for line in lower_lines:
        if "ux-lint-disable" in line:
            return []
    return out


def apply_ignores(text: str, findings: list[Finding]) -> list[Finding]:
    lines = text.splitlines()
    kept = []
    for finding in findings:
        previous = lines[finding.line - 2].lower() if finding.line >= 2 and finding.line - 2 < len(lines) else ""
        if "ux-lint-ignore" in previous:
            continue
        kept.append(finding)
    return kept


def lint_text(text: str, path: Path) -> list[Finding]:
    if is_exempt(path):
        return []
    rel = path.as_posix()
    findings = line_rules(text, path, rel, has_tokens(repo_root(path), path))
    findings = apply_ignores(text, findings)
    findings.sort(key=lambda f: (f.severity != "block", f.line, f.rule))
    return findings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Deterministic UI slop linter")
    parser.add_argument("files", nargs="*")
    parser.add_argument("--staged", action="store_true", help="lint staged files")
    parser.add_argument("--snippet", action="store_true", help="lint stdin instead of files")
    parser.add_argument("--filename", default="snippet.tsx", help="filename for --snippet")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--max", type=int, default=20)
    args = parser.parse_args(argv)

    if args.snippet:
        targets = [(Path(args.filename), sys.stdin.read())]
    else:
        files = list(args.files)
        if args.staged:
            out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                                 capture_output=True, text=True)
            files += [f for f in out.stdout.splitlines() if f]
        if not files:
            parser.error("no files given; pass paths, --staged, or --snippet")
        targets = [(Path(f), Path(f).read_text(errors="replace")) for f in files if Path(f).is_file()]

    findings: list[Finding] = []
    for path, text in targets:
        findings.extend(lint_text(text, path))
    findings = findings[: args.max]

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        for f in findings:
            print(f"{f.file}:{f.line}: {f.severity} {f.rule}: {f.message}")

    return 2 if any(f.severity == "block" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
