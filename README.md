# kdp-bleed

Resize a print-ready PDF (for example a Canva export) to Amazon KDP **bleed size** without re-printing it, so colours and image quality stay exactly as they were.

KDP rejects interiors whose backgrounds or images touch the page edge unless the file is sized for bleed: **0.125 in wider and 0.25 in taller** than the trim size. A 6 × 9 in book must be uploaded at 6.125 × 9.25 in.

`kdp-bleed` scales every page evenly until it covers the new size, so there are no white edges and nothing is stretched. It also gives you:

- a **guide copy** of the book with the cut line and safe zone drawn on every page
- a **margin report** listing pages where text is too close to an edge

## Install

Requires Python 3.9 or newer.

```bash
pip install git+https://github.com/amohsen01/kdp-bleed.git
```

Or from a local clone:

```bash
git clone https://github.com/amohsen01/kdp-bleed.git
cd kdp-bleed
pip install .
```

## Usage

```bash
kdp-bleed "My Book.pdf"
```

This creates two files next to the original:

| File | Purpose |
| --- | --- |
| `My Book_bleed.pdf` | Clean file to upload to KDP with **Bleed** selected |
| `My Book_bleed_CHECK.pdf` | Same pages with guide lines, for checking only |

In the guide copy:

- **Blue dashed line**: where KDP cuts the page (top, bottom and outside edge; the spine side is never cut)
- **Red box**: safe zone; keep text, page numbers and important artwork inside it

Then it prints a report like:

```
216 pages -> My Book_bleed.pdf
Guide copy (do not upload) -> My Book_bleed_CHECK.pdf
Text closer than 0.5 in to an edge on 2 page(s):
  page 14: 14
  page 15: 15
```

### Options

| Option | Default | Description |
| --- | --- | --- |
| `-o, --output PATH` | `<name>_bleed.pdf` | Output file |
| `--bleed INCHES` | `0.125` | Bleed added to the outside edge and to top and bottom |
| `--safe INCHES` | `0.5` | Safe distance from every page edge |
| `--no-guides` | | Skip the guide copy |
| `--no-check` | | Skip the margin report |
| `--first-page-left` | | Treat page 1 as a left-hand page |

You can also run it as a module: `python -m kdp_bleed "My Book.pdf"`.

### Python API

```python
from kdp_bleed import add_bleed, make_guide_copy, find_margin_issues

add_bleed("book.pdf", "book_bleed.pdf")
make_guide_copy("book_bleed.pdf", "book_bleed_CHECK.pdf")

for issue in find_margin_issues("book_bleed.pdf"):
    print(issue.page, issue.words)
```

## How it works

Each page's drawing instructions are wrapped in a single scale transform and the page box is enlarged. Images and fonts are not re-encoded, so the output looks identical to the input, just about 2.8 % larger.

Because the trim and bleed sizes have slightly different proportions, the page is scaled to cover the new height and centred; roughly 0.02 in on each side falls into the area KDP trims away anyway.

## Limitations

- The input must be at trim size (no bleed already added).
- Everything grows by about 2.8 %, so content moves slightly toward the edges. Check the margin report and the guide copy before uploading.
- The margin report checks text only, not images.
- The safe zone uses one distance for all edges. For books over 300 pages KDP requires a wider inside (gutter) margin, so check the spine side yourself.

## Development

```bash
pip install -e ".[dev]"
pytest
```
