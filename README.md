# paulart

Source of [paulsergounine.art](https://paulsergounine.art). Rules for working on it: see `CLAUDE.md` and `DEFINITION_OF_DONE.md`.

```sh
python3 scripts/build.py          # rebuild index.html from data/works.json
python3 scripts/check.py          # pre-publish checks
scripts/add_image.sh 47 "<photo>" # add a work photo in all sizes
python3 -m http.server 8000       # local preview at http://localhost:8000
```
