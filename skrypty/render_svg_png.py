#!/usr/bin/env python3
"""Make a compact true PNG preview from the SAME authored SVG, keeping the SVG.

Usage: python skrypty/render_svg_png.py wyniki/figure.svg wyniki/figure.png
Dependencies: pip install cairosvg pillow. This is not vector/CAD conversion.
"""
from pathlib import Path
import argparse
import io

def render(svg_path: Path, png_path: Path, width: int = 1000, colors: int = 64):
    import cairosvg
    from PIL import Image
    if not svg_path.is_file() or svg_path.suffix.lower() != ".svg":
        raise ValueError("source must be existing .svg")
    if png_path.suffix.lower() != ".png":
        raise ValueError("output must end with .png")
    data = cairosvg.svg2png(url=str(svg_path), output_width=width)
    im = Image.open(io.BytesIO(data)).convert("RGB")
    png_path.parent.mkdir(parents=True, exist_ok=True)
    im.quantize(colors=colors, method=Image.Quantize.FASTOCTREE).save(
        png_path, format="PNG", optimize=True
    )
    check=Image.open(png_path)
    assert check.format=="PNG" and check.width==width
    print(f"SVG: {svg_path.name}, PNG: {png_path.name}, {check.width}x{check.height}, {png_path.stat().st_size} bytes")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument("png", type=Path)
    parser.add_argument("--width",type=int,default=1000)
    parser.add_argument("--colors",type=int,default=64)
    args=parser.parse_args()
    render(args.svg,args.png,args.width,args.colors)
if __name__=="__main__":main()
