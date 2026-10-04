"""240x144 in-world mockup: the boy on a village path between his cottage, a
crop field and an empty build plot, with idle-game HUD bits."""
import random

import numpy as np

from pixel import Sprite, shift
import overworld

W, H = 240, 144

GRASS = dict(hi='#A2DE86', base='#7DC86C', sh='#5EA857', dk='#468A48')
PATH = dict(hi='#F0DCAE', base='#E2C793', sh='#C6A56E', ol='#9C7A4A')
SOIL = dict(base='#8E5D3E', sh='#71462D', wet='#5D3A26', ol='#3E2416')
WOOD = dict(hi='#D29A63', base='#B07C4E', sh='#86582F', ol='#4A2E1A')
WALL = dict(hi='#FFF7E4', base='#F3E6C8', sh='#D9C49C', ol='#7A5C3C')
ROOF = dict(hi='#EE7A5E', base='#CF5641', sh='#A63E31', ol='#5A1E1A')
BRICK = dict(base='#B5654A', sh='#8A4535', ol='#45201A')
GLASS = dict(hi='#D8F0FF', base='#8CC8EE', sh='#5A94C8', ol='#2E4C72')
LEAVES = dict(hi='#8FD46E', base='#5FB05A', sh='#3F8A48', ol='#1F4A2C')
CROP = dict(hi='#A6E57D', base='#6CC452', sh='#3F9A3F', ol='#1E4D22')
TURNIP = dict(base='#F6F0F4', sh='#D9C2D6', top='#D45A8A', ol='#6A3550')
GHOST = (90, 150, 240)
UI = dict(fill='#FBFBF7', edge='#2E3442', inner='#C9D2E2', text='#2E3442')
GOLD = dict(hi='#FFF2A8', base='#F2C94C', sh='#C7952A', ol='#6E4E12')

FONT = {
    '0': [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    '1': ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    '2': [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    '3': [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
    '4': ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    '5': ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    '9': [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    ',': ["..", "..", "..", "..", "..", ".#", "#."],
    '+': [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    '/': ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    ':': [".", "#", ".", ".", ".", "#", "."],
    ' ': ["..", "..", "..", "..", "..", "..", ".."],
    's': [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
    'S': [".###.", "#...#", "#....", ".###.", "....#", "#...#", ".###."],
    'P': ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    'R': ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    'I': ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    'N': ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    'G': [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    'A': [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'M': ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
}


def text(s, x, y, txt, color, outline=None):
    """Draw pixel-font text (outline first, glyphs on top); returns the end x."""
    pts = []
    for ch in txt:
        g = FONT[ch]
        pts += [(x + gx, y + gy) for gy, row in enumerate(g) for gx, c in enumerate(row) if c == '#']
        x += len(g[0]) + 1
    if outline:
        ring = {(px + ox, py + oy) for px, py in pts
                for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1))}
        s.dots(sorted(ring), outline)
    s.dots(pts, color)
    return x


def text_width(txt):
    return sum(len(FONT[c][0]) + 1 for c in txt) - 1


def ui_box(s, x0, y0, x1, y1):
    """Gen 5-style rounded text box: dark rim, pale inner rim, white fill."""
    box = s.rect((x0, y0, x1, y1)) & ~s.mask(lambda d: [d.point(p, 255) for p in
                                                       [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]])
    s.paint(box, UI['edge'])
    inner = s.rect((x0 + 1, y0 + 1, x1 - 1, y1 - 1))
    s.paint(inner, UI['inner'])
    s.paint(s.rect((x0 + 2, y0 + 2, x1 - 2, y1 - 2)), UI['fill'])


def coin(s, x, y):
    c = s.ellipse((x, y, x + 6, y + 6))
    s.part(c, GOLD['base'], GOLD['ol'], shade=GOLD['sh'], shade_off=(1, 1), hi=GOLD['hi'])
    s.dots([(x + 3, y + 2), (x + 3, y + 3), (x + 3, y + 4)], GOLD['sh'])


def build():
    rnd = random.Random(7)
    s = Sprite(W, H)

    # Grass with blade tufts and light specks.
    s.paint(s.rect((0, 0, W, H)), GRASS['base'])
    for _ in range(140):
        x, y = rnd.randrange(1, W - 3), rnd.randrange(2, H)
        s.dots([(x, y), (x + 1, y - 1), (x + 2, y)], GRASS['sh'])
    for _ in range(90):
        x, y = rnd.randrange(0, W - 1), rnd.randrange(0, H)
        s.dots([(x, y)], GRASS['hi'])

    s.paint(s.ellipse((14, 76, 92, 88)), GRASS['dk'])               # cottage shadow

    # Paths: an east-west lane and a spur up to the cottage door.
    lane = s.rect((0, 90, W, 107)) | s.rect((42, 80, 59, 92))
    lane = lane & ~s.mask(lambda d: [d.point(p, 255) for p in [(42, 80), (59, 80)]])
    s.paint(lane, PATH['base'])
    top = lane & ~shift(lane, 0, -1)
    s.paint(lane & ~shift(lane, 0, -2), PATH['sh'])  # lip under the grass edge
    s.paint(top, PATH['ol'])
    s.paint(lane & ~shift(lane, 0, 1), PATH['sh'])   # bottom edge
    for _ in range(45):
        x, y = rnd.randrange(0, W - 2), rnd.randrange(93, 105)
        s.dots([(x, y)], PATH['sh'])
        s.dots([(x + 1, y - 1)], PATH['hi'])

    # Cottage: front wall, then roof slope with shingle rows, then chimney.
    wall = s.rect((20, 44, 85, 81))
    s.part(wall, WALL['base'], WALL['ol'], shade=WALL['sh'], shade_off=(3, 0))
    s.paint(wall & s.rect((21, 45, 84, 50)), WALL['sh'])            # eave shadow
    for x0 in (20, 52, 82):
        s.part(s.rect((x0, 48, x0 + 3, 81)), WOOD['base'], WOOD['ol'], shade=WOOD['sh'], shade_off=(1, 0))
    s.part(s.rect((20, 50, 85, 53)), WOOD['base'], WOOD['ol'], shade=WOOD['sh'], shade_off=(0, 1))
    # Door with a brass knob.
    s.part(s.rect((42, 60, 59, 81)), WOOD['base'], WOOD['ol'], shade=WOOD['sh'], shade_off=(2, 0), hi=WOOD['hi'])
    s.paint(s.rect((50, 61, 50, 80)), WOOD['sh'])
    s.dots([(55, 71), (46, 71)], GOLD['base'])
    # Windows with flower boxes.
    for x0 in (26, 66):
        s.part(s.rect((x0, 57, x0 + 11, 67)), GLASS['base'], WOOD['ol'], shade=GLASS['sh'], shade_off=(2, 1), hi=GLASS['hi'])
        s.paint(s.rect((x0 + 5, 58, x0 + 6, 66)), WOOD['base'])
        s.paint(s.rect((x0 + 1, 62, x0 + 10, 62)), WOOD['base'])
        s.part(s.rect((x0 - 1, 67, x0 + 12, 71)), WOOD['base'], WOOD['ol'], shade=WOOD['sh'], shade_off=(0, 1))
        for i, c in enumerate(['#F07A9A', '#FFD25A', '#F07A9A', '#9AD0FF', '#FFD25A']):
            fx = x0 + 1 + i * 2 + (i // 3)
            s.dots([(fx, 66)], c)
            s.dots([(fx, 67)], CROP['sh'])
    roof = s.poly([(16, 8), (89, 8), (93, 47), (12, 47)])
    s.part(roof, ROOF['base'], ROOF['ol'], shade=ROOF['sh'], shade_off=(3, 2), hi=ROOF['hi'])
    for i, y in enumerate(range(14, 46, 5)):
        row = roof & s.rect((0, y, W, y)) & shift(roof, 0, 1) & shift(roof, 1, 0) & shift(roof, -1, 0)
        s.paint(row, ROOF['sh'])
        for x in range(18 + (i % 2) * 5, 92, 10):
            seam = roof & s.rect((x, y + 1, x, y + 4)) & shift(roof, 0, 1)
            s.paint(seam, ROOF['sh'])
    s.part(s.rect((14, 6, 91, 11)), ROOF['hi'], ROOF['ol'], shade=ROOF['base'], shade_off=(0, 1))   # ridge cap
    chimney = s.rect((66, 0, 76, 16))
    s.part(chimney, BRICK['base'], BRICK['ol'], shade=BRICK['sh'], shade_off=(2, 0))
    for y in (4, 8, 12):
        s.paint(chimney & s.rect((67, y, 75, y)), BRICK['sh'])
    s.part(s.rect((64, 0, 78, 3)), '#8C8C96', '#3A3A44')

    # Tree in the top-right corner.
    s.paint(s.ellipse((196, 52, 238, 64)), GRASS['dk'])
    s.part(s.rect((212, 40, 222, 60)), WOOD['base'], WOOD['ol'], shade=WOOD['sh'], shade_off=(2, 0))
    canopy = s.ellipse((194, -6, 236, 34)) | s.ellipse((188, 10, 226, 48)) | s.ellipse((208, 8, 246, 46))
    s.part(canopy, LEAVES['base'], LEAVES['ol'], shade=LEAVES['sh'], shade_off=(4, 4), hi=LEAVES['hi'])
    for _ in range(26):
        x, y = rnd.randrange(194, 236), rnd.randrange(2, 40)
        blob = s.ellipse((x, y, x + 4, y + 3)) & erode_safe(canopy)
        s.paint(blob & ~shift(blob, 0, 1), LEAVES['sh'])
        s.paint(blob & ~shift(blob, 0, -1) & ~shift(blob, -1, 0), LEAVES['hi'])

    # Fenced crop field: two rows of tilled tiles, some watered.
    field = s.rect((128, 46, 191, 81))
    s.part(field, SOIL['base'], SOIL['ol'])
    for ty in range(2):
        for tx in range(4):
            x0, y0 = 129 + tx * 16, 47 + ty * 17
            tile = s.rect((x0, y0, x0 + 14, y0 + 15))
            if (tx + ty) % 3 != 2:
                s.paint(tile, SOIL['wet'])
            for fy in range(y0 + 3, y0 + 15, 4):
                s.paint(tile & s.rect((x0 + 1, fy, x0 + 13, fy)), SOIL['sh'] if (tx + ty) % 3 == 2 else SOIL['ol'])
    crops = ['sprout', 'leafy', 'turnip', 'turnip', 'leafy', 'turnip', 'sprout', 'leafy']
    for i, kind in enumerate(crops):
        cx, cy = 129 + (i % 4) * 16 + 7, 47 + (i // 4) * 17 + 10
        draw_crop(s, cx, cy, kind)
    for x in range(124, 197, 12):
        s.part(s.rect((x, 32, x + 3, 47)), WOOD['base'], WOOD['ol'], shade=WOOD['sh'], shade_off=(1, 0), hi=WOOD['hi'])
    for y in (36, 41):
        s.part(s.rect((122, y, 199, y + 2)), WOOD['base'], WOOD['ol'], shade=WOOD['sh'], shade_off=(0, 1))
    for x in range(124, 197, 12):   # posts in front of the rails
        s.part(s.rect((x, 34, x + 3, 47)), WOOD['base'], WOOD['ol'], shade=WOOD['sh'], shade_off=(1, 0))
        s.dots([(x + 1, 35)], WOOD['hi'])

    # Empty build plot: a blueprint ghost of a house footprint with corner stakes.
    lot = s.rect((14, 113, 78, 139))
    ghost = s.px.astype(float)
    sel = lot
    ghost[sel, :3] = ghost[sel, :3] * 0.55 + np.array(GHOST) * 0.45
    s.px = ghost.astype(np.uint8)
    for x in range(14, 79, 8):
        s.paint(lot & s.rect((x, 113, x, 139)), (200, 225, 255, 255))
    for y in range(113, 140, 8):
        s.paint(lot & s.rect((14, y, 78, y)), (200, 225, 255, 255))
    edge = lot & ~erode_safe(lot)
    dashes = edge & s.mask(lambda d: [d.point((x, y), 255) for x in range(W) for y in range(H) if (x + y) // 3 % 2 == 0])
    s.paint(dashes, '#FFFFFF')
    s.paint(edge & ~dashes, (40, 80, 170, 255))
    for x, y in [(12, 110), (77, 110), (12, 136), (77, 136)]:
        s.part(s.rect((x, y, x + 2, y + 5)), WOOD['base'], WOOD['ol'])
    # "+" badge in the middle of the lot.
    s.part(s.ellipse((39, 119, 53, 133)), '#FFFFFF', '#2E5CB8', shade='#DCE8FF', shade_off=(1, 1))
    s.paint(s.rect((45, 122, 47, 130)) | s.rect((42, 125, 50, 127)), '#2E5CB8')

    # Signpost next to the plot.
    s.part(s.rect((88, 120, 89, 136)), WOOD['base'], WOOD['ol'])
    s.part(s.rect((82, 112, 97, 123)), WOOD['hi'], WOOD['ol'], shade=WOOD['base'], shade_off=(1, 1))
    s.paint(s.rect((86, 115, 93, 115)) | s.rect((86, 118, 91, 118)), WOOD['sh'])

    # Flowers and pebbles dotted around.
    for x, y, c in [(104, 120, '#F07A9A'), (112, 128, '#FFD25A'), (150, 118, '#FFFFFF'),
                    (172, 126, '#F07A9A'), (196, 116, '#FFD25A'), (210, 132, '#9AD0FF'),
                    (8, 70, '#FFD25A'), (6, 52, '#F07A9A'), (100, 60, '#FFFFFF'), (226, 84, '#F07A9A'),
                    (120, 136, '#9AD0FF'), (228, 120, '#FFFFFF')]:
        s.dots([(x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1)], c)
        s.dots([(x, y)], '#FFF4B0')
    for x, y in [(160, 128), (186, 136), (136, 114)]:
        s.part(s.ellipse((x, y, x + 6, y + 4)), '#C9CCD4', '#5A5E6E', shade='#9A9EAE', shade_off=(1, 1))

    # The player on the lane, facing the camera.
    s.paint(s.ellipse((101, 101, 120, 107)), (120, 96, 60, 120))
    sprite = np.array(overworld.frames()['down'])
    place(s, sprite, 95, 76)

    # Idle income popping off the ripe turnip.
    coin(s, 162, 20)
    text(s, 170, 20, '+5', GOLD['base'], outline=GOLD['ol'])
    s.dots([(167, 30), (167, 31), (166, 32), (168, 32)], GOLD['hi'])  # sparkle over the ripe one

    # HUD: purse + income rate, and the calendar.
    ui_box(s, 3, 3, 57, 27)
    coin(s, 8, 8)
    text(s, 18, 8, '1,250', UI['text'])
    text(s, 8, 18, '+12/s', '#3E8E4A')
    ui_box(s, 182, 3, 236, 17)
    text(s, 188, 7, 'SPRING 3', UI['text'])
    return s


def erode_safe(m):
    from pixel import erode4
    return erode4(m)


def place(s, sprite, x, y):
    h, w = sprite.shape[:2]
    region = s.px[y:y + h, x:x + w]
    a = sprite[..., 3:4] > 0
    s.px[y:y + h, x:x + w] = np.where(a, sprite, region)


def draw_crop(s, cx, cy, kind):
    if kind == 'sprout':
        s.dots([(cx, cy), (cx, cy - 1)], CROP['sh'])
        s.dots([(cx - 1, cy - 2), (cx - 2, cy - 2), (cx + 1, cy - 3), (cx + 2, cy - 3)], CROP['base'])
        s.dots([(cx - 1, cy - 3), (cx + 1, cy - 4)], CROP['hi'])
    elif kind == 'leafy':
        leaf = s.ellipse((cx - 4, cy - 6, cx, cy)) | s.ellipse((cx, cy - 7, cx + 4, cy - 1)) | \
            s.ellipse((cx - 2, cy - 4, cx + 2, cy + 1))
        s.part(leaf, CROP['base'], CROP['ol'], shade=CROP['sh'], shade_off=(1, 1), hi=CROP['hi'])
    else:
        bulb = s.ellipse((cx - 3, cy - 3, cx + 3, cy + 3))
        s.part(bulb, TURNIP['base'], TURNIP['ol'], shade=TURNIP['sh'], shade_off=(1, 1))
        s.paint(bulb & s.rect((cx - 3, cy - 3, cx + 3, cy - 2)) & erode_safe(bulb), TURNIP['top'])
        leaves = s.ellipse((cx - 5, cy - 10, cx - 1, cy - 3)) | s.ellipse((cx + 1, cy - 10, cx + 5, cy - 3))
        s.part(leaves & ~bulb, CROP['base'], CROP['ol'], shade=CROP['sh'], shade_off=(1, 1), hi=CROP['hi'])
