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
pre = data.get("pre_series", {}).get("works", [])

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

# Pre-series works: outside the numbered cycle, same rules for images and details
pre_ids = [w["id"] for w in pre]
if len(pre_ids) != len(set(pre_ids)):
    errors.append(f"duplicate pre-series ids: {pre_ids}")
for w in pre:
    for px in (800, 1200, 1600):
        f = ROOT / "images" / str(px) / w["image"]
        if not f.exists():
            errors.append(f"missing image {f.relative_to(ROOT)}")
        elif px == 1600 and f.stat().st_size > 900_000:
            warnings.append(f"{f.relative_to(ROOT)} is {f.stat().st_size // 1000} KB (budget 900 KB)")
    for field in ("year", "technique", "size"):
        if not w.get(field):
            (warnings if DRAFT else errors).append(f"{w['title']}: {field} not confirmed")

# 2. Identical photos under different numbers (the No. 11 / No. 12 mix-up)
seen = {}
for w in works:
    f = ROOT / "images/800" / f"mm-{w['no']:02d}.jpg"
    if f.exists():
        key = f.read_bytes()[-4096:]
        if key in seen:
            errors.append(f"No. {w['no']} and No. {seen[key]} use the same photo")
        seen[key] = w["no"]
for w in pre:
    f = ROOT / "images/800" / w["image"]
    if f.exists():
        key = f.read_bytes()[-4096:]
        if key in seen:
            errors.append(f"{w['title']} and No. {seen[key]} use the same photo")
        seen[key] = w["title"]

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
if index.count('class="work__open"') != len(works) + len(pre):
    errors.append("a work is missing its full-screen viewer link, run scripts/build.py")
if index.count('class="work"') != len(works) + len(pre):
    errors.append("index.html is out of date with data/works.json, run scripts/build.py")

# 4. Five scales diagram: one canvas format per rect, drawn to scale (1 unit = 1 cm),
#    all sharing the bottom-left corner, each labelled with its own size
SCALES = [(200, 240), (175, 210), (150, 180), (125, 150), (100, 120)]
svg = re.search(r'<svg class="scales__svg".*?</svg>', index, re.S)
if not svg:
    errors.append("index.html: five scales diagram missing (templates/index.html)")
else:
    rects = [tuple(int(v) for v in r) for r in re.findall(
        r'<rect x="(\d+)" y="(\d+)" width="(\d+)" height="(\d+)"', svg.group())]
    labels = re.findall(r'<text x="\d+" y="(\d+)">(\d+) × (\d+) cm</text>', svg.group())
    if [(w, h) for _, _, w, h in rects] != SCALES:
        errors.append(f"five scales: formats drawn are {rects}, expected {SCALES}")
    if any(x != 0 or y + h != 240 for x, y, _, h in rects):
        errors.append("five scales: rectangles do not share the bottom-left corner")
    if [(int(y), int(w), int(h)) for y, w, h in labels] != [(240 - h, w, h) for w, h in SCALES]:
        errors.append("five scales: labels do not match the formats or their top edges")

for m in warnings:
    print("WARN ", m)
for m in errors:
    print("FAIL ", m)
print(f"{len(errors)} failed, {len(warnings)} warnings, {len(works)} works, {len(pre)} pre-series")
sys.exit(1 if errors else 0)
