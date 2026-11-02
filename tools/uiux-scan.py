#!/usr/bin/env python3
"""Measure the UI/UX corpus: tokens, easing, durations, component classes.

The numbers in docs/UIUX-COMPONENT-ATLAS.md come from this script. Point it at a
directory of cloned sites (one folder per site) and it prints a per-site summary
plus the corpus-wide easing/duration distributions.

    python tools/uiux-scan.py --root ../Wesbite_Source
    python tools/uiux-scan.py --root ../Wesbite_Source --json out.json

Stdlib only. Bounded on purpose: HTML/CSS under --max-kb, --max-files per site,
so a 900-file component catalogue cannot stall the scan.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "vendor"}
TEXT_EXT = (".html", ".css")

HEX_RE = re.compile(r"#([0-9a-f]{6}|[0-9a-f]{3})\b", re.I)
FONT_RE = re.compile(r"font-family\s*:\s*([^;{}\n]{2,120})", re.I)
RAD_RE = re.compile(r"border-radius\s*:\s*([^;{}\n]{1,40})", re.I)
CLS_RE = re.compile(r'class="([^"]{1,300})"')
EASE_RE = re.compile(r"cubic-bezier\([^)]*\)", re.I)
DUR_RE = re.compile(r"(?:transition|animation)[^;{}]*?(\d*\.?\d+m?s)", re.I)


def scan_site(path: str, max_kb: int, max_files: int) -> dict:
    acc = {
        "font": collections.Counter(), "hex": collections.Counter(),
        "rad": collections.Counter(), "cls": collections.Counter(),
        "ease": collections.Counter(), "dur": collections.Counter(),
        "kf": 0, "files": 0, "bytes": 0,
    }
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if acc["files"] >= max_files:
                break
            if not name.lower().endswith(TEXT_EXT):
                continue
            fp = os.path.join(dirpath, name)
            try:
                if os.path.getsize(fp) > max_kb * 1024:
                    continue
                text = open(fp, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            acc["files"] += 1
            acc["bytes"] += len(text)
            for m in FONT_RE.findall(text):
                acc["font"][m.strip()[:70].lower()] += 1
            for m in HEX_RE.findall(text):
                acc["hex"]["#" + m.lower()] += 1
            for m in RAD_RE.findall(text):
                acc["rad"][m.strip()[:24]] += 1
            for m in CLS_RE.findall(text):
                for c in m.split():
                    acc["cls"][c[:50]] += 1
            for m in EASE_RE.findall(text):
                acc["ease"][re.sub(r"\s+", "", m)] += 1
            for m in DUR_RE.findall(text):
                acc["dur"][m] += 1
            acc["kf"] += text.count("@keyframes")
    return acc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=os.environ.get("UIUX_CORPUS", "../Wesbite_Source"))
    ap.add_argument("--json", help="write the full result to this path")
    ap.add_argument("--max-kb", type=int, default=400, help="skip files larger than this")
    ap.add_argument("--max-files", type=int, default=120, help="cap files per site")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"no such corpus directory: {root}", file=sys.stderr)
        return 2

    sites = {}
    ease_all = collections.Counter()
    dur_all = collections.Counter()

    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        if not os.path.isdir(path) or entry.startswith(".") or entry in SKIP_DIRS:
            continue
        if entry in {"tools", "analysis", "scripts", "docs"}:
            continue
        acc = scan_site(path, args.max_kb, args.max_files)
        if not acc["files"]:
            continue
        ease_all.update(acc["ease"])
        dur_all.update(acc["dur"])
        sites[entry] = {
            "files": acc["files"],
            "kb": round(acc["bytes"] / 1024),
            "keyframes": acc["kf"],
            "fonts": [f"{k} ({v})" for k, v in acc["font"].most_common(6)],
            "colors": [f"{k} ({v})" for k, v in acc["hex"].most_common(12)],
            "radii": [f"{k} ({v})" for k, v in acc["rad"].most_common(8)],
            "classes": [f"{k} ({v})" for k, v in acc["cls"].most_common(25)],
        }
        print(f"\n## {entry}  [{acc['files']} files, {round(acc['bytes']/1024)} KB, "
              f"{acc['kf']} keyframes]")
        print("  fonts:  " + "; ".join(sites[entry]["fonts"][:4]))
        print("  colors: " + ", ".join(sites[entry]["colors"][:8]))
        print("  radii:  " + ", ".join(sites[entry]["radii"][:6]))

    print("\n## Corpus-wide easing")
    for curve, n in ease_all.most_common(10):
        print(f"  {n:5d}  {curve}")
    print("\n## Corpus-wide durations")
    for dur, n in dur_all.most_common(12):
        print(f"  {n:5d}  {dur}")

    if args.json:
        payload = {"sites": sites,
                   "easing": ease_all.most_common(20),
                   "durations": dur_all.most_common(20)}
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=1)
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
