# paulsergounine.art — working rules for Claude Code

Artist website of Paul Sergounine (painter, b. 1984, Tbilisi / Düsseldorf), represented by Galerie Bruno Massa.
Purpose: a credible, quiet site for curators, institutions, prize juries and collectors. Not a shop.
This repo is separate from Nimbavero. Nothing from the nimbavero org belongs here.

## How the site is built
- Plain static HTML/CSS, no framework, no JavaScript. Hosted on GitHub Pages from `main`; domain `paulsergounine.art` (file `CNAME`), `paulsergounine.com` forwards to it at GoDaddy.
- **`data/works.json` is the single source of truth for the Work page.** `index.html` is generated:
  `python3 scripts/build.py` (template: `templates/index.html`). Never edit the works section of `index.html` by hand.
- Photos: `scripts/add_image.sh <no> "<original>"` writes `images/800|1200|1600/mm-NN.jpg`. Originals stay in Paul's iCloud folder `~/Library/Mobile Documents/com~apple~CloudDocs/Art/` and are never committed.
- `about.html`, `cv.html`, `contact.html` are edited directly.
- Before every commit: `python3 scripts/build.py && python3 scripts/check.py` (use `--draft` only on preview branches).

## Content rules (from Paul, binding)
1. Public material shows **birth year only (1984), never the birthplace.**
2. **No prices, no availability.** All sales enquiries go to Galerie Bruno Massa.
3. **The catalogue "Mind Mechanics, Selected Works 2025–2026" is the authority** for title, year, technique and size of every work it contains. Copy its wording exactly.
4. Years: Nos. 1–15 and Nos. 20, 22, 23 are 2025; all others from No. 16 are 2026 (unless the catalogue says otherwise).
5. Never guess a size or technique. If unknown, set it to `null` in `works.json` and ask Paul. `check.py` blocks publishing with unconfirmed fields.
6. Works are "numbered in the order made, not titled". Sub-titles only as the catalogue writes them, e.g. "(Assemblage I)", "(Excavation III)".
7. Works that were cut up and absorbed into later paintings may still be shown; mark them in `works.json` with a note such as "Absorbed into No. 56".
8. Image editing is limited to photographic correction (glare, crop of bare canvas edges, colour of the black ground). Never alter the paint itself.
9. Selection on the site is curated by Paul. Do not add or remove works without his OK. Watch for mislabelled source files (an "MM12" file once showed MM11) — `check.py` catches identical photos.
10. Site language: English. Paul talks to you in German or English.
11. No contacts, applications or messages in Paul's name without his explicit OK. Never put credentials in files or chat.

## Design
Follows the printed catalogue: off-white paper (#F1F0ED), italic serif (Newsreader ≈ catalogue Pagella) for titles, small letter-spaced capitals for labels, thin black rules, generous white space, one work per row with the caption beside it. No bold display type, no animation, no decorative effects. The paintings are loud; the frame stays quiet.

## Workflow
- `main` is live. Work on a branch (`update-YYYY-MM-DD` or a topic name), push, show Paul a preview, merge only after Paul says it is good.
- Small, clearly named commits. Run the checks before every push.
- Done means: everything in `DEFINITION_OF_DONE.md` is met.
