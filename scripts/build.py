#!/usr/bin/env python3
"""Build index.html from templates/index.html and data/works.json.

Usage:  python3 scripts/build.py
No dependencies beyond the Python 3 standard library.
"""
import json
import struct
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIDTHS = (800, 1200, 1600)
SIZES = "(max-width: 760px) 92vw, 68vw"


def jpeg_size(path):
    """Return (width, height) of a JPEG without third-party libraries."""
    with open(path, "rb") as f:
        f.read(2)
        while True:
            marker, length = struct.unpack(">2sH", f.read(4))
            if marker[1] in (0xC0, 0xC1, 0xC2):
                f.read(1)
                h, w = struct.unpack(">HH", f.read(4))
                return w, h
            f.read(length - 2)


def title(work):
    t = f"Mind Mechanics No. {work['no']}"
    return f"{t} ({work['suffix']})" if work.get("suffix") else t


def picture(name, alt, first=False):
    largest = ROOT / "images" / "1600" / name
    w, h = jpeg_size(largest)
    srcset = ", ".join(f"images/{px}/{name} {px}w" for px in WIDTHS)
    loading = 'fetchpriority="high"' if first else 'loading="lazy"'
    return (f'<img src="images/1200/{name}" srcset="{srcset}" sizes="{SIZES}" '
            f'alt="{escape(alt)}" width="{w}" height="{h}" decoding="async" {loading}>')


def figure(work, first):
    name = f"mm-{work['no']:02d}.jpg"
    t = title(work)
    plate = (f'<a class="work__open" href="images/1600/{name}" data-caption="{escape(t)}">'
             f'{picture(name, t, first)}</a>')
    meta = [f'<span class="work__num">No. {work["no"]}</span>',
            f'<span class="work__title">{escape(t)}</span>']
    meta += [f'<span class="work__dim">{escape(v)}</span>'
             for v in (work.get("year"), work.get("technique"), work.get("size")) if v]
    if work.get("note"):
        meta.append(f'<span class="work__note">{escape(work["note"])}</span>')
    if work.get("process"):
        meta.append(f'<a class="work__more" href="process.html#no-{work["no"]}">See how it was made</a>')
    meta_html = "\n          ".join(meta)
    return f'''    <figure class="work" id="no-{work['no']}">
        <div class="work__plate">
          {plate}
        </div>
        <figcaption class="work__meta">
          {meta_html}
        </figcaption>
      </figure>'''


def process_section(work):
    """One work's process sequence for process.html: steps, text, finished work."""
    t = title(work)
    name = f"mm-{work['no']:02d}.jpg"
    steps = ""
    for p in work["process"]:
        pw, ph = jpeg_size(ROOT / "images" / "800" / p["img"])
        cap = f'{t}, {p["label"]}'
        steps += (f'\n      <div class="process__step">'
                  f'\n        <a class="work__open process__open" href="images/1600/{p["img"]}" data-caption="{escape(cap)}">'
                  f'<img src="images/800/{p["img"]}" alt="{escape(t + ", " + p["alt"])}" '
                  f'width="{pw}" height="{ph}" loading="lazy" decoding="async"></a>'
                  f'\n        <span>{escape(p["label"])}</span>'
                  f'\n      </div>')
    w, h = jpeg_size(ROOT / "images" / "1600" / name)
    text = (f'\n    <p class="process__text">{escape(work["process_text"])}</p>'
            if work.get("process_text") else "")
    dims = " · ".join(v for v in (work.get("year"), work.get("size")) if v)
    return f'''  <section class="process__page" id="no-{work['no']}">
    <h1>{escape(t)}</h1>
    <div class="process n{len(work["process"])}">{steps}
    </div>{text}
    <figure class="process__final">
      <a class="work__open process__open" href="images/1600/{name}" data-caption="{escape(t)}">{picture(name, t)}</a>
      <figcaption>{escape(t)}{" · " + escape(dims) if dims else ""}</figcaption>
    </figure>
  </section>'''


def main():
    data = json.loads((ROOT / "data" / "works.json").read_text(encoding="utf-8"))
    works = sorted(data["works"], key=lambda w: -w["no"])
    html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    html = html.replace("{{WORKS}}", "\n".join(figure(w, i == 0) for i, w in enumerate(works)))
    html = html.replace("{{MADE}}", f"{data['series']['made']:03d}")
    html = html.replace("{{PLANNED}}", str(data["series"]["planned"]))
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    with_process = [w for w in works if w.get("process")]
    if with_process:
        page = (ROOT / "templates" / "process.html").read_text(encoding="utf-8")
        page = page.replace("{{PROCESS}}", "\n".join(process_section(w) for w in with_process))
        (ROOT / "process.html").write_text(page, encoding="utf-8")
    pending = [w["no"] for w in works if not (w.get("technique") and w.get("size"))]
    print(f"index.html built: {len(works)} works")
    if pending:
        print("details still missing for Nos.", ", ".join(map(str, pending)))


if __name__ == "__main__":
    main()
