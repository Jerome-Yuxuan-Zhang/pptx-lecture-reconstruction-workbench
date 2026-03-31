from __future__ import annotations

from html import escape
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont

from app.models.ir_models import BoundingBox


def _coerce_text(text: str | None, description: str | None, shape_type: str) -> str:
    candidate = (text or "").strip()
    if candidate:
        return candidate
    candidate = (description or "").strip()
    if candidate:
        return candidate
    return f"Degraded {shape_type}"


def _wrap_lines(text: str, width: int = 24, max_lines: int = 6) -> list[str]:
    collapsed = " ".join(text.split())
    wrapped = wrap(collapsed, width=width) or [collapsed]
    lines = wrapped[:max_lines]
    if len(wrapped) > max_lines:
        lines[-1] = f"{lines[-1]}..."
    return lines


def _visual_width(bbox: BoundingBox) -> int:
    return max(320, min(960, int(max(bbox.width * 2.2, 320))))


def _visual_height(bbox: BoundingBox, line_count: int) -> int:
    content_height = 170 + max(0, line_count - 2) * 34
    return max(220, min(720, int(max(bbox.height * 2.0, content_height))))


def _load_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/NotoSerifSC-Regular.otf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/times.ttf",
        "C:/Windows/Fonts/timesbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _draw_text(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    *,
    fill: tuple[int, int, int],
    font: ImageFont.ImageFont,
) -> None:
    try:
        draw.text(position, text, fill=fill, font=font)
    except UnicodeEncodeError:
        fallback = text.encode("ascii", "ignore").decode().strip() or "[see svg asset]"
        draw.text(position, fallback, fill=fill, font=ImageFont.load_default())


def build_diagram_assets(
    *,
    shape_type: str,
    bbox: BoundingBox,
    output_stem: Path,
    text: str | None,
    description: str | None,
) -> dict[str, str]:
    output_stem.parent.mkdir(parents=True, exist_ok=True)
    display_text = _coerce_text(text, description, shape_type)
    lines = _wrap_lines(display_text)
    width = _visual_width(bbox)
    height = _visual_height(bbox, len(lines))

    svg_path = output_stem.with_suffix(".svg")
    preview_path = output_stem.with_suffix(".png")

    svg_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">'
        ),
        "  <defs>",
        '    <linearGradient id="card" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#eef5f1" />',
        '      <stop offset="100%" stop-color="#ffffff" />',
        "    </linearGradient>",
        "  </defs>",
        (
            f'  <rect x="10" y="10" width="{width - 20}" height="{height - 20}" '
            'rx="28" fill="url(#card)" stroke="#2a6b51" stroke-width="4" />'
        ),
        (
            f'  <text x="{width / 2}" y="56" text-anchor="middle" font-size="24" '
            'font-family="Times New Roman, Noto Serif SC, serif" fill="#173a2c">'
            "Diagram Fallback</text>"
        ),
        (
            f'  <text x="{width / 2}" y="92" text-anchor="middle" font-size="18" '
            'font-family="Times New Roman, Noto Serif SC, serif" fill="#4d5e56">'
            f"{escape(shape_type)}</text>"
        ),
        (
            '  <rect x="42" y="118" width="120" height="36" rx="18" '
            'fill="#dfeee6" stroke="#2a6b51" stroke-width="2" />'
        ),
        (
            '  <text x="102" y="141" text-anchor="middle" font-size="16" '
            'font-family="Times New Roman, Noto Serif SC, serif" fill="#173a2c">'
            "Recovered Text</text>"
        ),
    ]
    for index, line in enumerate(lines):
        y = 196 + index * 32
        svg_lines.append(
            f'  <text x="44" y="{y}" font-size="22" '
            'font-family="Times New Roman, Noto Serif SC, serif" fill="#19222a">'
            f"{escape(line)}</text>"
        )
    svg_lines.append(
        f'  <text x="44" y="{height - 26}" font-size="14" '
        'font-family="Times New Roman, Noto Serif SC, serif" fill="#62706a">'
        f"Original bbox: {bbox.width:.1f}pt x {bbox.height:.1f}pt</text>"
    )
    svg_lines.append("</svg>")
    svg_path.write_text("\n".join(svg_lines), encoding="utf-8")

    title_font = _load_font(28)
    subtitle_font = _load_font(18)
    body_font = _load_font(22)
    meta_font = _load_font(14)

    image = Image.new("RGB", (width, height), color=(252, 250, 244))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (10, 10, width - 10, height - 10),
        radius=28,
        outline=(42, 107, 81),
        width=4,
        fill=(245, 248, 245),
    )
    _draw_text(draw, (44, 34), "Diagram Fallback", fill=(23, 58, 44), font=title_font)
    _draw_text(draw, (44, 76), shape_type, fill=(77, 94, 86), font=subtitle_font)
    draw.rounded_rectangle(
        (42, 118, 170, 154),
        radius=18,
        outline=(42, 107, 81),
        width=2,
        fill=(223, 238, 230),
    )
    _draw_text(draw, (58, 127), "Recovered Text", fill=(23, 58, 44), font=subtitle_font)
    for index, line in enumerate(lines):
        _draw_text(
            draw,
            (44, 178 + index * 32),
            line,
            fill=(25, 34, 42),
            font=body_font,
        )
    _draw_text(
        draw,
        (44, height - 36),
        f"Original bbox: {bbox.width:.1f}pt x {bbox.height:.1f}pt",
        fill=(98, 112, 106),
        font=meta_font,
    )
    image.save(preview_path)

    return {
        "svg_path": str(svg_path),
        "preview_path": str(preview_path),
        "asset_mode": "svg+preview",
    }
