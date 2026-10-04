#!/usr/bin/env python3
"""Pre-publish checks for paulsergounine.art. Exit code 1 if anything fails.

Usage:  python3 scripts/check.py            (strict: missing work details fail)
        python3 scripts/check.py --draft    (missing work details only warn)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFT = "--draft" in sys.argv
errors, warnings = [], []

data = json.loads((ROOT / "data/works.json").read_text(encoding="utf-8"))
works = data["works"]
nos = [w["no"] for w in works]

# 1. Data integrity
if len(nos) != len(set(nos)):
    errors.append(f"duplicate work numbers: {sorted(n for n in nos if nos.count(n) > 1)}")
if max(nos) > data["series"]["made"]:
    errors.append("a shown work number is higher than series.made")
for w in works:
    name = f"mm-{w['no']:02d}.jpg"
    for px in (800, 1200, 1600):
        f = ROOT / "images" / str(px) / name
        if not f.exists():
            errors.append(f"missing image {f.relative_to(ROOT)}")
        elif px == 1600 and f.stat().st_size > 900_000:
            warnings.append(f"{f.relative_to(ROOT)} is {f.stat().st_size // 1000} KB (budget 900 KB)")
    for field in ("year", "technique", "size"):
        if not w.get(field):
            (warnings if DRAFT else errors).append(f"No. {w['no']}: {field} not confirmed")

# 2. Identical photos under different numbers (the No. 11 / No. 12 mix-up)
seen = {}
for w in works:
    f = ROOT / "images/800" / f"mm-{w['no']:02d}.jpg"
    if f.exists():
        key = f.read_bytes()[-4096:]
        if key in seen:
            errors.append(f"No. {w['no']} and No. {seen[key]} use the same photo")
        seen[key] = w["no"]

# 3. Page content rules
html_files = sorted(ROOT.glob("*.html"))
for f in html_files:
    text = f.read_text(encoding="utf-8")
    if re.search(r"moscow|moskau|москв", text, re.I):
        errors.append(f"{f.name}: birthplace mentioned (public material shows birth year only)")
    if re.search(r"[€$£]\s?\d|\d\s?(€|EUR|USD)", text):
        errors.append(f"{f.name}: looks like a price (all sales go through the gallery)")
    for tag in re.findall(r"<script\b[^>]*>", text):
        if 'src="viewer.js"' not in tag:
            errors.append(f"{f.name}: script other than viewer.js: {tag}")
    for src in re.findall(r'(?:src|href)="([^"#:]+)"', text):
        if not (ROOT / src.split("?")[0]).exists():
            errors.append(f"{f.name}: broken link {src}")

index = (ROOT / "index.html").read_text(encoding="utf-8")
if "{{" in index:
    errors.append("index.html still contains template placeholders, run scripts/build.py")
if index.count('class="work__open"') != len(works):
    errors.append("a work is missing its full-screen viewer link, run scripts/build.py")
if index.count('class="work"') != len(works):
    errors.append("index.html is out of date with data/works.json, run scripts/build.py")

for m in warnings:
    print("WARN ", m)
for m in errors:
    print("FAIL ", m)
print(f"{len(errors)} failed, {len(warnings)} warnings, {len(works)} works")
sys.exit(1 if errors else 0)
