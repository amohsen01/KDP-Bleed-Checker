import argparse
import sys
from pathlib import Path

from . import __version__
from .core import add_bleed, find_margin_issues, make_guide_copy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kdp-bleed",
        description="Resize a print-ready PDF to KDP bleed size without re-printing it.",
    )
    parser.add_argument("input", type=Path, help="PDF at trim size, e.g. 6 x 9 in")
    parser.add_argument("-o", "--output", type=Path, help="output path (default: <name>_bleed.pdf)")
    parser.add_argument("--bleed", type=float, default=0.125, help="bleed in inches (default: 0.125)")
    parser.add_argument("--safe", type=float, default=0.5, help="safe margin from every page edge in inches (default: 0.5)")
    parser.add_argument("--no-guides", action="store_true", help="skip the _CHECK copy with guide lines")
    parser.add_argument("--no-check", action="store_true", help="skip the text margin report")
    parser.add_argument("--first-page-left", action="store_true", help="treat page 1 as a left-hand page")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    src: Path = args.input

    if not src.is_file():
        print(f"File not found: {src}", file=sys.stderr)
        return 1

    out = args.output or src.with_name(f"{src.stem}_bleed.pdf")
    count = add_bleed(src, out, bleed=args.bleed)
    print(f"{count} pages -> {out}")

    if not args.no_guides:
        guides = out.with_name(f"{out.stem}_CHECK.pdf")
        make_guide_copy(
            out,
            guides,
            bleed=args.bleed,
            safe=args.safe,
            first_page_right=not args.first_page_left,
        )
        print(f"Guide copy (do not upload) -> {guides}")

    if not args.no_check:
        issues = find_margin_issues(out, safe=args.safe)
        if not issues:
            print(f"All text is at least {args.safe} in from every edge.")
        else:
            print(f"Text closer than {args.safe} in to an edge on {len(issues)} page(s):")
            for issue in issues:
                sample = " ".join(issue.words[:8])
                more = " ..." if len(issue.words) > 8 else ""
                print(f"  page {issue.page}: {sample}{more}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
