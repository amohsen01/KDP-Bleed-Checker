from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Union

import pymupdf
from pypdf import PdfWriter, Transformation
from pypdf.generic import RectangleObject

INCH = 72.0
PathLike = Union[str, Path]


@dataclass(frozen=True)
class MarginIssue:
    page: int
    words: List[str] = field(default_factory=list)


def add_bleed(src: PathLike, dst: PathLike, bleed: float = 0.125) -> int:
    b = bleed * INCH
    writer = PdfWriter(clone_from=str(src))

    for page in writer.pages:
        box = page.mediabox
        x0, y0 = float(box.left), float(box.bottom)
        w, h = float(box.width), float(box.height)
        tw, th = w + b, h + 2 * b

        s = max(tw / w, th / h)
        tx = (tw - w * s) / 2
        ty = (th - h * s) / 2

        page.add_transformation(
            Transformation().translate(-x0, -y0).scale(s, s).translate(tx, ty)
        )
        rect = RectangleObject([0, 0, tw, th])
        page.mediabox = rect
        page.cropbox = rect
        page.trimbox = rect
        page.bleedbox = rect
        page.artbox = rect

    with open(dst, "wb") as f:
        writer.write(f)
    return len(writer.pages)


def make_guide_copy(
    src: PathLike,
    dst: PathLike,
    bleed: float = 0.125,
    safe: float = 0.5,
    first_page_right: bool = True,
) -> None:
    b = bleed * INCH
    m = safe * INCH
    doc = pymupdf.open(str(src))

    for index, page in enumerate(doc):
        w, h = page.rect.width, page.rect.height
        is_right = (index % 2 == 0) == first_page_right
        if is_right:
            trim = pymupdf.Rect(0, b, w - b, h - b)
        else:
            trim = pymupdf.Rect(b, b, w, h - b)

        page.draw_rect(trim, color=(0, 0.45, 1), width=0.75, dashes="[4 3] 0", overlay=True)
        page.draw_rect(pymupdf.Rect(m, m, w - m, h - m), color=(1, 0, 0), width=1, overlay=True)

    doc.save(str(dst), garbage=1, deflate=True)
    doc.close()


def find_margin_issues(path: PathLike, safe: float = 0.5) -> List[MarginIssue]:
    m = safe * INCH
    issues = []
    doc = pymupdf.open(str(path))

    for number, page in enumerate(doc, start=1):
        w, h = page.rect.width, page.rect.height
        words = [
            word
            for x0, y0, x1, y1, word, *_ in page.get_text("words")
            if x0 < m or y0 < m or x1 > w - m or y1 > h - m
        ]
        if words:
            issues.append(MarginIssue(page=number, words=words))

    doc.close()
    return issues
