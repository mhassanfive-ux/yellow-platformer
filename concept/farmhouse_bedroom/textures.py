"""Small pixel-art textures for the bedroom, drawn in code. Blender samples them
with nearest-neighbour filtering, so each texel stays a crisp square that skews
with the camera's perspective, the way the DS renders its 3D rooms."""
import os
import random

from PIL import Image, ImageDraw


def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def floor_planks():
    """64x64 honey-coloured boards running left to right, staggered joints."""
    rnd = random.Random(3)
    img = Image.new('RGB', (64, 64))
    px = img.load()
    tones = ['#D9A066', '#D29A5E', '#DDA770', '#CF955A']
    for row in range(8):
        y0 = row * 8
        start = rnd.randrange(0, 64)
        covered = 0
        while covered < 64:                     # fill exactly one wrapped row
            length = min(rnd.randrange(22, 44), 64 - covered)
            tone = hexc(rnd.choice(tones))
            for dx in range(length):
                for dy in range(8):
                    c = tone
                    if dy == 7:
                        c = hexc('#8A5A34')     # seam under each board
                    elif dy == 0:
                        c = hexc('#E8B67C')     # lit top edge
                    elif dx == 0:
                        c = hexc('#9C673C')     # end joint
                    px[(start + covered + dx) % 64, y0 + dy] = c
            for _ in range(length // 12):       # grain streaks
                gy = y0 + rnd.randrange(2, 6)
                gx = start + covered + rnd.randrange(2, max(3, length - 6))
                for k in range(rnd.randrange(3, 6)):
                    px[(gx + k) % 64, gy] = hexc('#C18A52')
            covered += length
    return img


def wallpaper():
    """32x32 cream stripes with a little sprout motif."""
    img = Image.new('RGB', (32, 32), hexc('#F4EBD0'))
    d = ImageDraw.Draw(img)
    for x in (0, 16):
        d.rectangle((x, 0, x + 3, 31), fill=hexc('#EADFBF'))
    for ox, oy in ((8, 6), (24, 22)):
        d.point([(ox, oy + 3), (ox, oy + 2)], fill=hexc('#6E9E52'))
        d.point([(ox - 1, oy + 1), (ox - 2, oy), (ox + 1, oy), (ox + 2, oy - 1)], fill=hexc('#8DBF6A'))
    return img


def wainscot():
    """32x32 vertical boards for the lower wall."""
    rnd = random.Random(5)
    img = Image.new('RGB', (32, 32), hexc('#B9845A'))
    d = ImageDraw.Draw(img)
    for x in range(0, 32, 8):
        d.line((x, 0, x, 31), fill=hexc('#7A4E30'))
        d.line((x + 1, 0, x + 1, 31), fill=hexc('#CF9A6C'))
        for _ in range(2):
            gx, gy = x + rnd.randrange(3, 7), rnd.randrange(0, 26)
            d.line((gx, gy, gx, gy + rnd.randrange(3, 6)), fill=hexc('#A87550'))
    return img


def rug():
    """48x32 rag rug: concentric bands with a diamond centre."""
    bands = ['#7A2E2A', '#C8473B', '#F1DDB0', '#D99A3A', '#F1DDB0', '#5E9A57', '#F1DDB0']
    img = Image.new('RGB', (48, 32), hexc('#C8473B'))
    d = ImageDraw.Draw(img)
    for i, c in enumerate(bands):
        d.rectangle((i * 2, i * 2, 47 - i * 2, 31 - i * 2), fill=hexc(c))
    d.rectangle((14, 14, 33, 17), fill=hexc('#C8473B'))
    for cx in (18, 24, 30):
        d.polygon([(cx, 11), (cx + 3, 15), (cx, 20), (cx - 3, 15)], fill=hexc('#D99A3A'))
        d.point((cx, 15), fill=hexc('#7A2E2A'))
    for x in range(0, 48, 2):                                # woven texture on the rim
        d.point((x, 0), fill=hexc('#5A1E1A'))
        d.point((x + 1, 31), fill=hexc('#5A1E1A'))
    return img


def quilt():
    """32x32 patchwork: four 8x8 patches per row."""
    patches = {
        'gingham': lambda x, y: '#D9473B' if (x // 2 + y // 2) % 2 else '#F6D5C8',
        'cream': lambda x, y: '#7DB0E0' if (x % 4 == 1 and y % 4 == 1) else '#F4EBD0',
        'green': lambda x, y: '#5E9A57' if (x + y) % 4 else '#7DBF6A',
        'mustard': lambda x, y: '#E0B048' if y % 3 else '#C8952F',
    }
    order = [['gingham', 'cream', 'green', 'mustard'], ['green', 'mustard', 'gingham', 'cream'],
             ['cream', 'gingham', 'mustard', 'green'], ['mustard', 'green', 'cream', 'gingham']]
    img = Image.new('RGB', (32, 32))
    px = img.load()
    for py in range(4):
        for pxi in range(4):
            fn = patches[order[py][pxi]]
            for y in range(8):
                for x in range(8):
                    c = fn(x, y)
                    if x == 7 or y == 7:
                        c = '#FFF6E2'                            # stitching
                    px[pxi * 8 + x, py * 8 + y] = hexc(c)
    return img


def gingham():
    img = Image.new('RGB', (8, 8))
    px = img.load()
    for y in range(8):
        for x in range(8):
            a, b = (x // 2) % 2, (y // 2) % 2
            px[x, y] = hexc(['#FFFFFF', '#F0A8A0', '#F0A8A0', '#D9473B'][a + 2 * b])
    return img


def sky():
    """24x24 view out of the window: sky, cloud, distant fields."""
    img = Image.new('RGB', (24, 24))
    d = ImageDraw.Draw(img)
    for y in range(24):
        d.line((0, y, 23, y), fill=hexc(['#7FC4F0', '#8ECCF2', '#9ED5F5', '#B2DEF7'][min(3, y // 4)]))
    d.rectangle((4, 4, 11, 6), fill=(255, 255, 255))
    d.rectangle((6, 3, 9, 3), fill=(255, 255, 255))
    d.rectangle((15, 8, 19, 9), fill=hexc('#E8F5FD'))
    d.polygon([(0, 17), (8, 14), (16, 16), (23, 13), (23, 23), (0, 23)], fill=hexc('#7DC86C'))
    d.polygon([(0, 20), (12, 18), (23, 20), (23, 23), (0, 23)], fill=hexc('#5EA857'))
    d.line((2, 21, 21, 21), fill=hexc('#E0C060'))
    return img


def blueprint():
    """32x24 blueprint of a cottage floor plan, pinned on the wall."""
    img = Image.new('RGB', (32, 24), hexc('#3C6EC8'))
    d = ImageDraw.Draw(img)
    for x in range(0, 32, 4):
        d.line((x, 0, x, 23), fill=hexc('#4A7CD4'))
    for y in range(0, 24, 4):
        d.line((0, y, 31, y), fill=hexc('#4A7CD4'))
    w = (232, 242, 255)
    d.rectangle((5, 5, 26, 18), outline=w)
    d.line((15, 5, 15, 12), fill=w)
    d.line((5, 12, 21, 12), fill=w)
    d.line((10, 18, 13, 18), fill=hexc('#3C6EC8'))           # doorway
    d.point([(20, 8), (21, 8), (9, 15), (10, 15)], fill=w)
    d.rectangle((0, 0, 31, 23), outline=hexc('#1D2F63'))
    return img


def town_map():
    """32x24 hand-drawn map of the valley: river, roads, a few plots."""
    img = Image.new('RGB', (32, 24), hexc('#9BCF7A'))
    d = ImageDraw.Draw(img)
    d.line((0, 15, 9, 13, 18, 16, 31, 12), fill=hexc('#5FA8E0'), width=2)
    d.line((14, 0, 14, 23), fill=hexc('#E2C793'))
    d.line((0, 7, 31, 7), fill=hexc('#E2C793'))
    d.line((14, 14, 14, 17), fill=hexc('#B07C4E'))           # bridge
    for x, y, c in [(5, 3, '#D9473B'), (9, 3, '#5B8FDB'), (18, 3, '#D9473B'), (22, 9, '#F2C94C'),
                    (5, 9, '#F2C94C'), (25, 3, '#5B8FDB')]:
        d.rectangle((x, y, x + 2, y + 2), fill=hexc(c))
    d.rectangle((20, 18, 27, 21), outline=hexc('#FFFFFF'))   # the empty plot
    d.point((29, 20), fill=hexc('#D9473B'))                  # "you are here"
    d.rectangle((0, 0, 31, 23), outline=hexc('#F4EBD0'))
    return img


def calendar():
    img = Image.new('RGB', (12, 16), hexc('#FFFDF6'))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 11, 4), fill=hexc('#5E9A57'))
    for y in range(6, 15, 3):
        for x in range(1, 11, 3):
            d.point((x, y), fill=hexc('#8A8F9E'))
    d.point((7, 9), fill=hexc('#D9473B'))
    d.rectangle((0, 0, 11, 15), outline=hexc('#B9AE94'))
    return img


def crate():
    img = Image.new('RGB', (16, 16), hexc('#C79A62'))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 15, 15), outline=hexc('#7A5232'))
    d.rectangle((1, 1, 14, 14), outline=hexc('#A87C4C'))
    for y in (5, 10):
        d.line((1, y, 14, y), fill=hexc('#8E6438'))
    d.line((1, 1, 14, 14), fill=hexc('#A87C4C'))
    return img


def dark_wood():
    rnd = random.Random(9)
    img = Image.new('RGB', (16, 16), hexc('#8C5A3A'))
    d = ImageDraw.Draw(img)
    for _ in range(7):
        x, y = rnd.randrange(0, 13), rnd.randrange(0, 16)
        d.line((x, y, x + rnd.randrange(2, 5), y), fill=hexc('#7A4C30'))
    for _ in range(3):
        d.point((rnd.randrange(0, 16), rnd.randrange(0, 16)), fill=hexc('#A06C48'))
    return img


def drawers():
    """16x16 chest-of-drawers front: two drawers with brass knobs."""
    img = Image.new('RGB', (16, 16), hexc('#B07C4E'))
    d = ImageDraw.Draw(img)
    for y0 in (1, 8):
        d.rectangle((1, y0, 14, y0 + 6), outline=hexc('#6E4630'), fill=hexc('#C08A5A'))
        d.point([(5, y0 + 3), (10, y0 + 3)], fill=hexc('#F2C94C'))
    return img


def seed_bag():
    img = Image.new('RGB', (8, 8), hexc('#E2C793'))
    d = ImageDraw.Draw(img)
    d.line((0, 0, 7, 0), fill=hexc('#C6A56E'))
    d.point([(3, 4), (4, 3), (4, 4), (4, 5), (5, 3)], fill=hexc('#5E9A57'))
    return img


ALL = {
    'floor': floor_planks, 'wallpaper': wallpaper, 'wainscot': wainscot, 'rug': rug,
    'quilt': quilt, 'gingham': gingham, 'sky': sky, 'blueprint': blueprint,
    'calendar': calendar, 'crate': crate, 'dark_wood': dark_wood, 'drawers': drawers,
    'seed_bag': seed_bag, 'town_map': town_map,
}


def write_all(folder):
    os.makedirs(folder, exist_ok=True)
    paths = {}
    for name, fn in ALL.items():
        path = os.path.join(folder, name + '.png')
        fn().save(path)
        paths[name] = path
    return paths
