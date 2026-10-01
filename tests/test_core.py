import pymupdf
import pytest

from kdp_bleed import add_bleed, find_margin_issues, make_guide_copy
from kdp_bleed.cli import main


@pytest.fixture
def book(tmp_path):
    path = tmp_path / "book.pdf"
    doc = pymupdf.open()
    for i in range(4):
        page = doc.new_page(width=432, height=648)
        page.draw_rect(page.rect, color=None, fill=(0.1, 0.1, 0.3))
        page.insert_text((100, 300), "Body text", color=(1, 1, 1))
        page.insert_text((210, 640), str(i + 1), color=(1, 1, 1))
    doc.save(str(path))
    doc.close()
    return path


def test_add_bleed_sets_kdp_size(book, tmp_path):
    out = tmp_path / "out.pdf"
    assert add_bleed(book, out) == 4
    doc = pymupdf.open(str(out))
    for page in doc:
        assert page.rect.width == pytest.approx(441)
        assert page.rect.height == pytest.approx(666)


def test_add_bleed_leaves_no_white_edges(book, tmp_path):
    out = tmp_path / "out.pdf"
    add_bleed(book, out)
    pix = pymupdf.open(str(out))[0].get_pixmap(dpi=72)
    for x, y in [(0, 0), (pix.width - 1, 0), (0, pix.height - 1), (pix.width - 1, pix.height - 1)]:
        assert pix.pixel(x, y) != (255, 255, 255)


def test_guide_copy_draws_lines(book, tmp_path):
    out = tmp_path / "out.pdf"
    guides = tmp_path / "guides.pdf"
    add_bleed(book, out)
    make_guide_copy(out, guides)
    assert len(pymupdf.open(str(guides))[0].get_drawings()) > len(pymupdf.open(str(out))[0].get_drawings())


def test_margin_issues_flag_edge_text(book, tmp_path):
    out = tmp_path / "out.pdf"
    add_bleed(book, out)
    issues = find_margin_issues(out)
    assert [i.page for i in issues] == [1, 2, 3, 4]
    assert all("Body" not in i.words for i in issues)


def test_cli_writes_both_files(book, capsys):
    assert main([str(book)]) == 0
    assert (book.parent / "book_bleed.pdf").exists()
    assert (book.parent / "book_bleed_CHECK.pdf").exists()
    assert "page 1" in capsys.readouterr().out
