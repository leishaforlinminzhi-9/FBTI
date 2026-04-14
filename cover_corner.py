from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def cover_bottom_right(
    in_path: str | Path,
    out_path: str | Path,
    *,
    cover_w: int = 260,
    cover_h: int = 110,
    margin: int = 18,
    color: tuple[int, int, int, int] = (248, 250, 252, 255),  # Disc White-ish
) -> None:
    img = Image.open(in_path).convert("RGBA")
    w, h = img.size

    x2 = w - margin
    y2 = h - margin
    x1 = max(0, x2 - cover_w)
    y1 = max(0, y2 - cover_h)

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([x1, y1, x2, y2], fill=color)

    out = Image.alpha_composite(img, overlay).convert("RGB")
    out.save(out_path, quality=95)


def main() -> None:
    p = argparse.ArgumentParser(description="Cover bottom-right corner with a solid color block.")
    p.add_argument(
        "input",
        nargs="?",
        default="",
        help="Input image path. If omitted, process all PNGs under ./image/",
    )
    p.add_argument("-o", "--output", default="", help="Output image path (only when processing a single input)")
    p.add_argument(
        "--outdir",
        default="/data/minzhi/agent/fbti/image/new",
        help="Output directory. Save results with the same filename (e.g. out/HSVW.png). Default: ./image_out/",
    )
    p.add_argument("--w", type=int, default=260, help="Cover width in pixels")
    p.add_argument("--h", type=int, default=110, help="Cover height in pixels")
    p.add_argument("--margin", type=int, default=18, help="Margin from bottom-right corner")
    p.add_argument("--color", default="248,250,252,255", help="RGBA color, e.g. 248,250,252,255")
    args = p.parse_args()

    color = tuple(int(x.strip()) for x in args.color.split(","))  # type: ignore[assignment]
    if len(color) != 4:
        raise SystemExit("--color must be 4 numbers: R,G,B,A")

    outdir = Path(args.outdir) if args.outdir else (Path(__file__).resolve().parent / "image_out")
    outdir.mkdir(parents=True, exist_ok=True)

    if args.input:
        in_path = Path(args.input)
        out_path = Path(args.output) if args.output else (outdir / in_path.name)
        cover_bottom_right(in_path, out_path, cover_w=args.w, cover_h=args.h, margin=args.margin, color=color)  # type: ignore[arg-type]
        print(f"Saved: {out_path}")
        return

    # default: process all PNGs in ./image
    image_dir = Path(__file__).resolve().parent / "image"
    if not image_dir.exists():
        raise SystemExit(f"Default image directory not found: {image_dir}")

    inputs = sorted(image_dir.glob("*.png"))
    if not inputs:
        raise SystemExit(f"No PNG files found in: {image_dir}")

    for fp in inputs:
        out_path = outdir / fp.name
        cover_bottom_right(fp, out_path, cover_w=args.w, cover_h=args.h, margin=args.margin, color=color)
        print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()

