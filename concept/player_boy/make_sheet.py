"""Builds the player concept sheet and the standalone exports next to this file.

    python3 make_sheet.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

import overworld
import portrait
import scene
from palette import SWATCHES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')

PIXEL_FONT = '/usr/share/fonts/opentype/unifont/unifont.otf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SANS_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

INK = (43, 47, 58, 255)
MUTED = (110, 116, 130, 255)
PAPER = (243, 239, 230, 255)
CARD = (255, 255, 255, 255)
CARD_EDGE = (217, 211, 196, 255)

SW, SH = 1400, 1308


def pixel_text(txt, scale, color):
    """Unifont rendered without anti-aliasing, then scaled up crisply."""
    font = ImageFont.truetype(PIXEL_FONT, 16)
    w = int(font.getlength(txt)) + 2
    img = Image.new('L', (w, 18), 0)
    d = ImageDraw.Draw(img)
    d.fontmode = '1'
    d.text((0, 0), txt, font=font, fill=255)
    img = img.crop(img.getbbox())
    img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    out = Image.new('RGBA', img.size, color)
    out.putalpha(img)
    return out


def card(sheet, box, title, caption=None):
    d = ImageDraw.Draw(sheet)
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 + 3, y0 + 5, x1 + 3, y1 + 5), 16, fill=(0, 0, 0, 28))
    d.rounded_rectangle(box, 16, fill=CARD, outline=CARD_EDGE, width=2)
    t = pixel_text(title, 2, INK)
    sheet.alpha_composite(t, (x0 + 28, y0 + 24))
    if caption:
        d.text((x0 + 28 + t.width + 16, y0 + 26), caption, font=ImageFont.truetype(SANS, 15), fill=MUTED)


def wrap(d, txt, font, width):
    words, lines, cur = txt.split(), [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if d.textlength(trial, font=font) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def marker(d, cx, cy, n):
    d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=INK)
    f = ImageFont.truetype(SANS_BOLD, 16)
    d.text((cx, cy + 1), str(n), font=f, fill=(255, 255, 255), anchor='mm')


def build():
    os.makedirs(OUT, exist_ok=True)
    sheet = Image.new('RGBA', (SW, SH), PAPER)
    d = ImageDraw.Draw(sheet)
    for y in range(140, SH, 20):
        for x in range(10, SW, 20):
            d.point((x, y), fill=(222, 216, 202))

    # Header.
    d.rectangle((0, 0, SW, 118), fill=(38, 42, 53))
    sheet.alpha_composite(pixel_text('PLAYER CONCEPT — BOY', 3, (255, 255, 255, 255)), (40, 22))
    d.text((42, 80), 'Idle city-builder with cozy farming  ·  Gen 5 (Black/White)-inspired 2.5D pixel art  ·  v0.1',
           font=ImageFont.truetype(SANS, 18), fill=(201, 209, 224))
    x = SW - 40
    for tag, col in reversed([('IDLE', (242, 201, 76)), ('CITY BUILDER', (91, 143, 219)), ('FARMING', (108, 196, 82))]):
        t = pixel_text(tag, 1, (38, 42, 53, 255))
        w = t.width + 24
        d.rounded_rectangle((x - w, 30, x, 58), 14, fill=col)
        sheet.alpha_composite(t, (x - w + 12, 44 - t.height // 2))
        x -= w + 10

    # Key art card with numbered callouts.
    card(sheet, (40, 146, 540, 1000), 'KEY ART', '64×104 sprite, shown 6×')
    px0, py0, sc = 98, 238, 6
    d.ellipse((px0 + 30, py0 + 548, px0 + 354, py0 + 640), fill=(232, 240, 226))
    d.ellipse((px0 - 10, py0 + 40, px0 + 394, py0 + 560), fill=(246, 249, 242))
    sheet.alpha_composite(portrait.build().image(sc), (px0, py0))
    callouts = [  # (feature x, y in sprite px, side, number)
        ((51, 13), 'r', 1), ((36, 49), 'r', 2), ((52, 66), 'r', 3), ((8, 64), 'l', 4), ((22, 76), 'l', 5)]
    for (fx, fy), side, n in callouts:
        x, y = px0 + fx * sc, py0 + fy * sc
        mx = px0 + 384 + 22 if side == 'r' else px0 - 26
        d.line((x, y, mx, y), fill=INK, width=2)
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 255, 255), outline=INK, width=2)
        marker(d, mx, y, n)
    legend = [('Straw hat', 'farm roots; the brim reads at 32px'),
              ('Red neckerchief', 'echoes the hat band from any side'),
              ('Blueprint roll', 'the city-planning half'),
              ('Satchel + sprout', 'foraging and idle income'),
              ('Overalls', 'work-ready "growth" green')]
    f_b, f_r = ImageFont.truetype(SANS_BOLD, 15), ImageFont.truetype(SANS, 15)
    y = 878
    for i, (head, body) in enumerate(legend, 1):
        marker(d, 80, y + 9, i)
        d.text((104, y), head, font=f_b, fill=INK)
        bx = 104 + d.textlength(head + '  ', font=f_b)
        assert bx + d.textlength(body, font=f_r) <= 516, f'legend line {i} overflows the card'
        d.text((bx, y), body, font=f_r, fill=MUTED)
        y += 23

    # Overworld turnaround.
    card(sheet, (572, 146, 1360, 420), 'OVERWORLD', '32×32 frames, shown 5×')
    frames = overworld.frames()
    order = ['down', 'left', 'up', 'right']
    x = 1360 - 28 - 4 * 34
    d.text((x - 92, 30 + 146), 'actual size', font=ImageFont.truetype(SANS, 13), fill=MUTED)
    for i, k in enumerate(order):
        sheet.alpha_composite(frames[k], (x + i * 34, 146 + 18))
    gx = 572 + (788 - (4 * 160 + 3 * 22)) // 2
    for i, k in enumerate(order):
        x0 = gx + i * 182
        d.rounded_rectangle((x0, 214, x0 + 160, 374), 10, fill=(240, 246, 236))
        d.ellipse((x0 + 44, 344, x0 + 116, 362), fill=(214, 226, 206))
        sheet.alpha_composite(frames[k].resize((160, 160), Image.NEAREST), (x0, 214))
        t = pixel_text(k.upper(), 1, MUTED)
        sheet.alpha_composite(t, (x0 + 80 - t.width // 2, 384))

    # In-world mockup.
    card(sheet, (572, 444, 1360, 1000), 'IN-WORLD MOCKUP', '240×144 scene, shown 3×')
    sx, sy = 572 + (788 - 720) // 2, 528
    d.rounded_rectangle((sx - 6, sy - 6, sx + 726, sy + 438), 8, fill=INK)
    sheet.alpha_composite(scene.build().image(3), (sx, sy))
    d.text((sx, sy + 444), 'Cottage, crop plot with idle income ticking (+5), and an empty build lot waiting for a blueprint.',
           font=ImageFont.truetype(SANS, 14), fill=MUTED)

    # Palette.
    card(sheet, (40, 1024, 860, 1276), 'PALETTE', 'highlight / base / shade / outline')
    f = ImageFont.truetype(SANS, 14)
    for i, (name, ramp) in enumerate(SWATCHES):
        col, row = i % 5, i // 5
        x0, y0 = 68 + col * 158, 1092 + row * 88
        steps = [ramp[k] for k in ('hi', 'base', 'sh', 'ol', 'paper') if k in ramp][:4]
        for j, hexc in enumerate(steps):
            d.rectangle((x0 + j * 30, y0, x0 + j * 30 + 26, y0 + 26), fill=hexc, outline=(0, 0, 0, 40))
        d.text((x0, y0 + 34), name, font=f, fill=INK)

    # Style rules.
    card(sheet, (884, 1024, 1360, 1276), 'STYLE RULES')
    rules = ['Chibi overworld (~2 heads), taller key art (~4 heads).',
             'Outlines are a dark tint of each material, never pure black.',
             'Light from top-left; 3–4 tone ramp per material.',
             'Warm accents (straw, red) carry the read against all the green.',
             '16px tiles, 32×32 characters, tilted 3/4 camera.']
    y = 1084
    for r in rules:
        for k, line in enumerate(wrap(d, r, f_r, 420)):
            if k == 0:
                d.ellipse((912, y + 7, 918, y + 13), fill=(108, 196, 82))
            d.text((928, y), line, font=f_r, fill=INK)
            y += 22
        y += 8

    sheet.convert('RGB').save(os.path.join(OUT, 'player_concept_sheet.png'), optimize=True)

    # Standalone exports.
    portrait.build().image(1).save(os.path.join(OUT, 'player_key_art_64x104.png'))
    portrait.build().image(8).save(os.path.join(OUT, 'player_key_art_8x.png'))
    strip = Image.new('RGBA', (32 * 4, 32), (0, 0, 0, 0))
    for i, k in enumerate(order):
        strip.alpha_composite(frames[k], (32 * i, 0))
    strip.save(os.path.join(OUT, 'player_overworld_32x32.png'))
    scene.build().image(4).save(os.path.join(OUT, 'mockup_scene_4x.png'))

    # Turnaround GIF: down -> left -> up -> right on a light backdrop.
    gif = []
    for k in order:
        bg = Image.new('RGBA', (192, 192), (240, 246, 236, 255))
        ImageDraw.Draw(bg).ellipse((54, 168, 138, 186), fill=(214, 226, 206))
        bg.alpha_composite(frames[k].resize((192, 192), Image.NEAREST))
        gif.append(bg.convert('P', palette=Image.ADAPTIVE))
    gif[0].save(os.path.join(OUT, 'player_turnaround.gif'), save_all=True, append_images=gif[1:],
                duration=450, loop=0)


if __name__ == '__main__':
    build()
