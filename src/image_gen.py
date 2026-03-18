"""
image_gen.py — Generate BookTok/Instagram-style book slide images using Pillow.

Output: 1080x1350px JPEG (portrait, works on Instagram feed + TikTok photo posts)
"""
import os
import textwrap
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont


# Genre color palettes (bg, accent, text)
PALETTES = {
    "mystery":  {"bg": "#1a1a2e", "accent": "#e94560", "text": "#eaeaea"},
    "thriller": {"bg": "#0f0e17", "accent": "#ff8906", "text": "#fffffe"},
    "sci-fi":   {"bg": "#0d1b2a", "accent": "#00b4d8", "text": "#e0e0e0"},
    "horror":   {"bg": "#1a0000", "accent": "#cc2200", "text": "#f0e6e6"},
    "literary": {"bg": "#2d2d2d", "accent": "#f5c842", "text": "#f0f0f0"},
    "romance":  {"bg": "#2d1b2e", "accent": "#e040fb", "text": "#f8e8f8"},
    "default":  {"bg": "#1e293b", "accent": "#6366f1", "text": "#f8fafc"},
}


def _hex(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _dim(rgb: tuple, factor: float = 0.7) -> tuple:
    return tuple(int(c * factor) for c in rgb)


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Try local fonts dir, then common system paths, then fall back to default."""
    names = [
        f"fonts/{'Inter-Bold' if bold else 'Inter-Regular'}.ttf",
        f"fonts/{'RobotoSlab-Bold' if bold else 'RobotoSlab-Regular'}.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans{}.ttf".format("-Bold" if bold else ""),
        "/usr/share/fonts/truetype/liberation/LiberationSans{}-Regular.ttf".format("-Bold" if bold else ""),
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in names:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    # Pillow default — small but always available
    return ImageFont.load_default()


def _fetch_cover(book: dict) -> Image.Image | None:
    """Fetch cover art from cover_url or Open Library fallback."""
    urls = []
    if book.get("cover_url", "").strip():
        urls.append(book["cover_url"].strip())
    isbn = book.get("isbn", "").strip()
    if isbn:
        urls.append(f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg")

    for url in urls:
        try:
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200 and len(resp.content) > 2000:
                return Image.open(BytesIO(resp.content)).convert("RGB")
        except Exception:
            continue
    return None


def create_slide(book: dict, output_dir: str = "output") -> str:
    """
    Create a BookTok-style image for the given book dict.
    Returns the file path of the saved image.
    """
    os.makedirs(output_dir, exist_ok=True)

    genre = book.get("genre", "default").lower().strip()
    palette = PALETTES.get(genre, PALETTES["default"])
    bg = _hex(palette["bg"])
    accent = _hex(palette["accent"])
    text_col = _hex(palette["text"])

    W, H = 1080, 1350
    PAD = 64

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    y = PAD

    # ── Cover image ────────────────────────────────────────────────────
    cover = _fetch_cover(book)
    cover_area_h = int(H * 0.42)

    if cover:
        # Scale to fit width while preserving aspect ratio, center
        ratio = cover_area_h / cover.height
        new_w = int(cover.width * ratio)
        new_w = min(new_w, W - PAD * 2)
        cover_resized = cover.resize((new_w, cover_area_h), Image.LANCZOS)
        x_offset = (W - new_w) // 2
        img.paste(cover_resized, (x_offset, y))
    else:
        # Placeholder
        ph_w = int(W * 0.48)
        ph_x = (W - ph_w) // 2
        draw.rectangle([ph_x, y, ph_x + ph_w, y + cover_area_h],
                       fill=_dim(bg, 0.6), outline=accent, width=3)
        ph_font = _load_font(72)
        draw.text((W // 2, y + cover_area_h // 2), "📚",
                  anchor="mm", font=ph_font, fill=text_col)

    y += cover_area_h + 36

    # ── Accent rule ────────────────────────────────────────────────────
    draw.rectangle([PAD, y, W - PAD, y + 4], fill=accent)
    y += 24

    # ── Genre tag ──────────────────────────────────────────────────────
    tag_font = _load_font(30)
    tag = f"#{genre}" if genre not in ("default", "") else "#bookrec"
    draw.text((PAD, y), tag.upper(), font=tag_font, fill=accent)
    y += 48

    # ── Title ──────────────────────────────────────────────────────────
    title_font = _load_font(68, bold=True)
    title = book.get("title", "Unknown Title")
    wrapped = textwrap.fill(title, width=18)
    draw.multiline_text((PAD, y), wrapped, font=title_font,
                        fill=text_col, spacing=10)
    line_count = wrapped.count("\n") + 1
    y += line_count * 80 + 8

    # ── Author ─────────────────────────────────────────────────────────
    author_font = _load_font(36)
    draw.text((PAD, y), f"by {book.get('author', '')}",
              font=author_font, fill=_dim(text_col, 0.72))
    y += 58

    # ── Blurb ──────────────────────────────────────────────────────────
    blurb = book.get("blurb", "").strip()
    if blurb:
        if len(blurb) > 130:
            blurb = blurb[:127] + "…"
        blurb_font = _load_font(30)
        wrapped_blurb = textwrap.fill(blurb, width=40)
        draw.multiline_text((PAD, y), wrapped_blurb, font=blurb_font,
                            fill=_dim(text_col, 0.80), spacing=7)

    # ── Bottom CTA ─────────────────────────────────────────────────────
    cta_font = _load_font(32, bold=True)
    draw.text((W // 2, H - 72), "🔗  Shop link in bio",
              anchor="mm", font=cta_font, fill=accent)

    # ── Save ───────────────────────────────────────────────────────────
    safe_isbn = (book.get("isbn") or "book").replace(" ", "_")
    out_path = os.path.join(output_dir, f"{safe_isbn}.jpg")
    img.save(out_path, "JPEG", quality=95)
    return out_path
