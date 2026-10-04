# Definition of Done — paulsergounine.art

A change may go to `main` (live) only when all of these hold.

## Content
- [ ] `python3 scripts/check.py` passes in strict mode (no `--draft`).
- [ ] Every work shown has year, technique and size confirmed by Paul or taken verbatim from the catalogue.
- [ ] No birthplace, no prices, no availability anywhere on the site.
- [ ] Every photo shows the right painting (compared visually against the catalogue or Paul's own file).
- [ ] Biography, CV and statement say nothing Paul has not confirmed.

## Quality
- [ ] Desktop (1440 px) and phone (390 px) screenshots of every changed page reviewed — no overlaps, no horizontal scrolling, no empty image boxes.
- [ ] Every image exists in 800 / 1200 / 1600 px; a 1600 px image is at most 900 KB.
- [ ] The first work loads immediately; all others load lazily. No JavaScript, no layout shift (width/height set on every image).
- [ ] All internal links work (`check.py` verifies them).

## Process
- [ ] Built from `data/works.json` with `scripts/build.py`; the works section of `index.html` was not edited by hand.
- [ ] Paul has seen the preview and approved it.
