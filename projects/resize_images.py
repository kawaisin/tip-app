#!/usr/bin/env python3
"""Resize every image in a folder to a specific size.

Usage:
    python3 projects/resize_images.py INPUT_DIR WIDTH HEIGHT [options]

Examples:
    python3 projects/resize_images.py ./photos 1080 1080
    python3 projects/resize_images.py ./photos 1920 1080 --mode fill -o ./out
    python3 projects/resize_images.py ./photos 512 512 --mode pad --background white --format png

Modes:
    fit      Shrink/grow to fit inside WIDTHxHEIGHT, keeping aspect ratio (default).
             The output may be smaller than the target on one side.
    fill     Scale and center-crop so the output is exactly WIDTHxHEIGHT.
    pad      Fit inside WIDTHxHEIGHT, then pad with a background color to exactly that size.
    stretch  Resize to exactly WIDTHxHEIGHT, ignoring aspect ratio.

Requires Pillow:  pip install Pillow
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required: pip install Pillow")

EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp"}
FORMATS = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP",
           "bmp": "BMP", "gif": "GIF", "tiff": "TIFF"}


def resize(img, size, mode, background):
    if mode == "fit":
        return ImageOps.contain(img, size, Image.LANCZOS)
    if mode == "fill":
        return ImageOps.fit(img, size, Image.LANCZOS)
    if mode == "pad":
        return ImageOps.pad(img, size, Image.LANCZOS, color=background)
    return img.resize(size, Image.LANCZOS)


def main():
    parser = argparse.ArgumentParser(description="Resize all images in a folder to a specific size.")
    parser.add_argument("input_dir", type=Path, help="folder containing images")
    parser.add_argument("width", type=int, help="target width in pixels")
    parser.add_argument("height", type=int, help="target height in pixels")
    parser.add_argument("-o", "--output", type=Path,
                        help="output folder (default: INPUT_DIR/resized)")
    parser.add_argument("-m", "--mode", choices=["fit", "fill", "pad", "stretch"], default="fit",
                        help="how to handle aspect ratio (default: fit)")
    parser.add_argument("-f", "--format", choices=sorted(FORMATS),
                        help="convert all images to this format (default: keep original)")
    parser.add_argument("-q", "--quality", type=int, default=90,
                        help="JPEG/WebP quality 1-100 (default: 90)")
    parser.add_argument("-b", "--background", default="black",
                        help="pad color, e.g. white or '#ff0000' (default: black)")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="include images in subfolders")
    args = parser.parse_args()

    if not args.input_dir.is_dir():
        sys.exit(f"Not a folder: {args.input_dir}")
    if args.width <= 0 or args.height <= 0:
        sys.exit("Width and height must be positive.")

    out_dir = args.output or args.input_dir / "resized"
    size = (args.width, args.height)
    pattern = "**/*" if args.recursive else "*"
    files = sorted(p for p in args.input_dir.glob(pattern)
                   if p.is_file() and p.suffix.lower() in EXTENSIONS
                   and out_dir.resolve() not in p.resolve().parents)

    if not files:
        sys.exit(f"No images found in {args.input_dir}")

    done = failed = 0
    for src in files:
        rel = src.relative_to(args.input_dir)
        if args.format:
            rel = rel.with_suffix("." + args.format)
            fmt = FORMATS[args.format]
        else:
            fmt = None  # let Pillow infer from the extension
        dest = out_dir / rel
        try:
            with Image.open(src) as img:
                img = ImageOps.exif_transpose(img)  # respect camera rotation
                out = resize(img, size, args.mode, args.background)
                target_fmt = fmt or Image.registered_extensions().get(dest.suffix.lower())
                if target_fmt == "JPEG" and out.mode not in ("RGB", "L"):
                    out = out.convert("RGB")  # JPEG has no alpha channel
                dest.parent.mkdir(parents=True, exist_ok=True)
                out.save(dest, fmt, quality=args.quality)
            print(f"✓ {rel}  {out.width}x{out.height}")
            done += 1
        except Exception as e:
            print(f"✗ {src.name}: {e}", file=sys.stderr)
            failed += 1

    print(f"\nResized {done} image(s) to {out_dir}" + (f", {failed} failed" if failed else ""))


if __name__ == "__main__":
    main()
