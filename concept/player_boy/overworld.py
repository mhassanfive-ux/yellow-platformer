"""32x32 overworld sprites, hand-typed. Front and back views are symmetric, so
only their left halves are written out; the right-facing view mirrors the left."""
import numpy as np
from PIL import Image, ImageOps

from pixel import from_grid, mirror_rows, rgba
from palette import HAT, BAND, HAIR, SKIN, SHIRT, OVERALL, BAG, BOOT, BRASS, EYE, BLUSH

PAL = {
    'K': HAT['ol'], 'H': HAT['hi'], 'h': HAT['base'], 't': HAT['sh'],
    'r': BAND['base'], 'R': BAND['sh'], 'n': BAND['hi'], 'N': BAND['base'],
    'O': HAIR['ol'], 'b': HAIR['base'], 'B': HAIR['sh'], 'L': HAIR['hi'],
    's': SKIN['base'], 'S': SKIN['sh'], 'Z': SKIN['ol'], 'p': BLUSH,
    'e': EYE['dark'],
    'w': SHIRT['base'], 'W': SHIRT['sh'], 'V': SHIRT['ol'],
    'g': OVERALL['base'], 'G': OVERALL['sh'], 'f': OVERALL['hi'], 'F': OVERALL['ol'],
    'k': BAG['base'], 'j': BAG['sh'], 'J': BAG['ol'], 'y': BRASS['base'],
    'd': BOOT['base'], 'D': BOOT['ol'],
}

HAT_ROWS = [
    "................",
    "................",
    "...........KKKKK",
    ".........KKHHHhh",
    "........KHHhhhhh",
    "....KKKKKHhhhhhh",
    "...KhhhhKrrrrrrr",
    "..KHhhhhKRRRRRRR",
    "..KHhhhhhttttttt",
    "..KHhhhhhhhhhhhh",
    "...Ktthhhhhhhhhh",
    ".....KKKtttttttt",
]

FRONT_HALF = HAT_ROWS + [
    "......OOKKKKKKKK",
    "......ObbbbBbbbB",
    "......ObBSbSSbSS",
    "......ObZsssesss",
    "......OOZsssesss",
    "........Zpssssss",
    ".........ZZsssss",
    "........VVwZZZZZ",
    "......VVwwwgnnnn",
    ".....VwwwwwgNnnn",
    ".....VwwVwwgggNn",
    ".....VWWVwwgyggg",
    ".....ZssZwwggggg",
    ".....ZsSZWWggggg",
    ".....ZsSZFgggggg",
    "......ZZFggggggG",
    ".........FfffffG",
    ".........DdddddD",
    "........DdddddD.",
    "........DDDDDDD.",
]

BACK_HALF = HAT_ROWS[:8] + [
    "..KHhhhhhhhhhhhh",
    "..KHhhhhhhhhhhhh",
    "...Ktthhhhhhhhhh",
    ".....KKKtttttttt",
    "......OOKKKKKKKK",
    "......OBBBBBBBBB",
    "......Obbbbbbbbb",
    "......ObLbbbLbbb",
    "......ObbLbbbLbb",
    ".......OBbbbbbbb",
    "........OOBBOBBB",
    "........VVwOOOOO",
    "......VVwwwgwwww",
    ".....VwwwwwgwwwW",
    ".....VwwVwwgwwwW",
    ".....VWWVwwgwwww",
    ".....ZssZwwggggg",
    ".....ZsSZWWggggg",
    ".....ZsSZFgggggg",
    "......ZZFggggggG",
    ".........FfffffG",
    ".........DdddddD",
    "........DdddddD.",
    "........DDDDDDD.",
]

LEFT = [
    "................................",
    "................................",
    "...........KKKKKKK..............",
    ".........KKHHHhhhhKK............",
    "........KHHhhhhhhhhtK...........",
    ".......KHhhhhhhhhhhttK..........",
    ".......KrrrrrrrrrrrRRK..........",
    "...KKKKKRRRRRRRRRRRRRKKKKKK.....",
    "..KHhhhtttttttttttttthhhhhK.....",
    "..KHhhhhhhhhhhhhhhhhhhhhhtK.....",
    "...KKtthhhhhhhhhhhhhhhhttK......",
    ".....KKKKtttttttttttKKKK........",
    "......ObbBSSSSBbbbbbO...........",
    "......ZbSsssssOBbbbbO...........",
    "......ZssessssObbbBbO...........",
    ".....ZsssessssObbbbBO...........",
    "......ZpsssssSOBbbbBO...........",
    ".......ZZsssSSOBBBBO............",
    ".........ZZZZZOOOO..............",
    "..........VnnVwwwwV.............",
    ".........VgnVwwwwwV.............",
    ".........VggVwwwWVwV............",
    ".........VggVWWWWVwVJJ..........",
    ".........FggFZssZgGFkkJ.........",
    ".........FgggZsSZgGFjjJ.........",
    ".........FgggZssZgGFJJ..........",
    ".........FggggZZgGGF............",
    "..........FgggggggGF............",
    "..........FffffffGF.............",
    ".........DdddddddD..............",
    "........DddddddddD..............",
    "........DDDDDDDDDD..............",
]


def _front():
    img = from_grid(mirror_rows(FRONT_HALF), PAL)
    px = np.array(img)
    # The bag hangs at his right hip (viewer's left), its strap over his left shoulder.
    bag = {(3, 22): 'J', (4, 22): 'J', (2, 23): 'J', (3, 23): 'k', (4, 23): 'k',
           (2, 24): 'J', (3, 24): 'y', (4, 24): 'k', (2, 25): 'J', (3, 25): 'j', (4, 25): 'j',
           (3, 26): 'J', (4, 26): 'J'}
    strap = {(20, 20): 'J', (19, 21): 'J', (18, 22): 'J', (17, 23): 'J', (16, 23): 'J',
             (15, 24): 'J', (14, 24): 'J', (13, 25): 'J', (12, 25): 'J', (11, 26): 'J'}
    for (x, y), ch in {**bag, **strap}.items():
        px[y, x] = rgba(PAL[ch])
    return Image.fromarray(px, 'RGBA')


def _back():
    img = from_grid(mirror_rows(BACK_HALF), PAL)
    px = np.array(img)
    # From behind the bag is on the viewer's right.
    bag = {(27, 22): 'J', (28, 22): 'J', (27, 23): 'k', (28, 23): 'k', (29, 23): 'J',
           (27, 24): 'k', (28, 24): 'k', (29, 24): 'J', (27, 25): 'j', (28, 25): 'j', (29, 25): 'J',
           (27, 26): 'J', (28, 26): 'J'}
    strap = {(11, 20): 'J', (12, 21): 'J', (13, 22): 'J', (14, 22): 'J', (15, 23): 'J',
             (16, 23): 'J', (17, 24): 'J', (18, 24): 'J', (19, 25): 'J', (20, 25): 'J'}
    for (x, y), ch in {**bag, **strap}.items():
        px[y, x] = rgba(PAL[ch])
    return Image.fromarray(px, 'RGBA')


def frames():
    left = from_grid(LEFT, PAL)
    return {
        'down': _front(),
        'left': left,
        'up': _back(),
        'right': ImageOps.mirror(left),
    }
