"""Tiny pixel-art toolkit: build sprites from shapes with selective outlines and
directional shading, or from hand-typed character grids."""
import numpy as np
from PIL import Image, ImageDraw


def rgba(hex_code, alpha=255):
    h = hex_code.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def shift(m, dx, dy):
    """out[y, x] = m[y + dy, x + dx], False where that falls off the canvas."""
    h, w = m.shape
    out = np.zeros_like(m)
    out[max(0, -dy):min(h, h - dy), max(0, -dx):min(w, w - dx)] = \
        m[max(0, dy):min(h, h + dy), max(0, dx):min(w, w + dx)]
    return out


def erode4(m):
    """Interior of a mask: pixels whose four neighbours are all inside it."""
    return m & shift(m, 1, 0) & shift(m, -1, 0) & shift(m, 0, 1) & shift(m, 0, -1)


class Sprite:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = np.zeros((h, w, 4), np.uint8)

    def mask(self, fn):
        img = Image.new('L', (self.w, self.h), 0)
        fn(ImageDraw.Draw(img))
        return np.array(img) > 0

    def poly(self, pts):
        return self.mask(lambda d: d.polygon(pts, fill=255))

    def ellipse(self, box):
        return self.mask(lambda d: d.ellipse(box, fill=255))

    def rect(self, box):
        return self.mask(lambda d: d.rectangle(box, fill=255))

    def line(self, pts, width):
        return self.mask(lambda d: d.line(pts, fill=255, width=width))

    def part(self, m, fill, outline=None, shade=None, shade_off=(2, 1),
             hi=None, hi_off=(-1, -1)):
        """Paint a shape: outline ring, fill, then a shade band on the far side
        from the light (top-left) and an optional highlight rim facing it."""
        if outline is not None:
            self.px[m] = rgba(outline)
            inner = erode4(m)
        else:
            inner = m
        self.px[inner] = rgba(fill)
        shaded = np.zeros_like(m)
        if shade is not None:
            shaded = inner & ~shift(inner, *shade_off)
            self.px[shaded] = rgba(shade)
        if hi is not None:
            lit = inner & ~shift(inner, *hi_off) & ~shaded
            self.px[lit] = rgba(hi)
        return inner

    def paint(self, m, color):
        self.px[m] = rgba(color) if isinstance(color, str) else color

    def dots(self, pts, color):
        for x, y in pts:
            self.px[y, x] = rgba(color)

    def opaque(self):
        return self.px[..., 3] > 0

    def image(self, scale=1):
        img = Image.fromarray(self.px, 'RGBA')
        if scale != 1:
            img = img.resize((self.w * scale, self.h * scale), Image.NEAREST)
        return img


def from_grid(rows, palette):
    """Build an RGBA image from strings; '.' is transparent."""
    h, w = len(rows), max(len(r) for r in rows)
    for i, r in enumerate(rows):
        assert len(r) == w, f'row {i} is {len(r)} wide, expected {w}: {r!r}'
    px = np.zeros((h, w, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != '.':
                px[y, x] = rgba(palette[ch])
    return Image.fromarray(px, 'RGBA')


def mirror_rows(left_halves):
    """Complete symmetric rows from their left halves."""
    return [h + h[::-1] for h in left_halves]
