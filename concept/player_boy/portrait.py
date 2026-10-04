"""Full-body 'trainer card' sprite of the boy, 64x104, front-facing."""
from pixel import Sprite, shift
from palette import (HAT, BAND, HAIR, SKIN, SHIRT, OVERALL, BAG, BOOT, SOLE,
                     PRINT, LEAF, BRASS, EYE, BLUSH)

W, H = 64, 104


def mir(pts):
    return [(W - 1 - x, y) for x, y in pts]


def mirbox(box):
    x0, y0, x1, y1 = box
    return (W - 1 - x1, y0, W - 1 - x0, y1)


def build():
    s = Sprite(W, H)

    # Ground shadow.
    s.paint(s.ellipse((11, 92, 52, 100)), (40, 30, 40, 70))

    # Satchel hanging at his left hip (viewer's left), behind the arm.
    bag = s.poly([(5, 61), (17, 61), (18, 63), (18, 74), (16, 76), (6, 76), (4, 74), (4, 63)])
    s.part(bag, BAG['base'], BAG['ol'], shade=BAG['sh'])
    flap = s.poly([(4, 61), (18, 61), (18, 67), (11, 70), (4, 67)])
    s.part(flap, BAG['hi'], BAG['ol'], shade=BAG['base'], shade_off=(1, 1))
    s.part(s.rect((10, 66, 12, 68)), BRASS['base'], BRASS['ol'])
    # Sprout poking out of the satchel.
    s.part(s.poly([(9, 61), (5, 55), (6, 53), (11, 58), (11, 61)]),
           LEAF['base'], LEAF['ol'], shade=LEAF['sh'], shade_off=(1, 1))
    s.part(s.poly([(10, 61), (13, 53), (16, 51), (15, 56), (12, 61)]),
           LEAF['hi'], LEAF['ol'], shade=LEAF['base'], shade_off=(1, 1))

    # Legs (overall trousers), cuffs and boots.
    legs = s.poly([(18, 63), (45, 63), (46, 85), (33, 85), (32, 72), (31, 72), (30, 85), (17, 85)])
    s.part(legs, OVERALL['base'], OVERALL['ol'], shade=OVERALL['sh'], shade_off=(3, 1))
    for box in [(17, 81, 30, 86), (33, 81, 46, 86)]:
        s.part(s.rect(box), OVERALL['hi'], OVERALL['ol'], shade=OVERALL['base'], shade_off=(2, 1))
    boot_l = [(18, 86), (30, 86), (30, 95), (14, 95), (14, 92), (16, 89)]
    for pts in [boot_l, mir(boot_l)]:
        s.part(s.poly(pts), BOOT['base'], BOOT['ol'], shade=BOOT['sh'], hi=BOOT['hi'])
    for box in [(14, 94, 30, 96), mirbox((14, 94, 30, 96))]:
        s.part(s.rect(box), SOLE['base'], BOOT['ol'])

    # Torso: white tee.
    torso = [(21, 44), (42, 44), (46, 48), (45, 64), (18, 64), (17, 48)]
    s.part(s.poly(torso), SHIRT['base'], SHIRT['ol'], shade=SHIRT['sh'], shade_off=(3, 1))

    # Overall bib, straps, pocket, brass buttons.
    s.part(s.rect((24, 51, 39, 65)), OVERALL['base'], OVERALL['ol'], shade=OVERALL['sh'], shade_off=(3, 1))
    strap_l = [(23, 52), (27, 52), (24, 43), (20, 44)]
    for pts in [strap_l, mir(strap_l)]:
        s.part(s.poly(pts), OVERALL['base'], OVERALL['ol'], shade=OVERALL['sh'], shade_off=(1, 1))
    s.part(s.rect((28, 55, 35, 60)), OVERALL['base'], OVERALL['sh'])
    s.dots([(29, 57), (30, 57), (31, 57), (32, 57), (33, 57), (34, 57)], OVERALL['sh'])
    for box in [(24, 50, 26, 52), mirbox((24, 50, 26, 52))]:
        s.part(s.rect(box), BRASS['base'], BRASS['ol'])

    # Neck.
    s.part(s.rect((27, 39, 36, 46)), SKIN['sh'], SKIN['ol'])

    # Satchel strap from his right shoulder across to the bag.
    strap = s.line([(44, 44), (12, 64)], 4)
    s.part(strap, BAG['base'], BAG['ol'], shade=BAG['sh'], shade_off=(0, 1))

    # Red neckerchief.
    s.part(s.poly([(24, 44), (39, 44), (32, 53), (31, 53)]), BAND['base'], BAND['ol'],
           shade=BAND['sh'], shade_off=(2, 1))
    s.part(s.rect((28, 43, 35, 47)), BAND['hi'], BAND['ol'], shade=BAND['base'], shade_off=(1, 1))

    # Head.
    face_pts = [(19, 16), (44, 16), (44, 33), (41, 39), (37, 42), (26, 42), (22, 39), (19, 33)]
    face = s.part(s.poly(face_pts), SKIN['base'], SKIN['ol'], shade=SKIN['sh'], shade_off=(2, 1))
    brim = s.ellipse((6, 9, 57, 25))
    s.paint(face & shift(brim, 0, -3) & ~brim, SKIN['sh'])  # shadow cast by the hat brim

    # Hair: side tufts and spiky bangs.
    tuft_l = [(14, 20), (22, 20), (22, 31), (21, 35), (19, 31), (16, 34), (17, 29), (13, 28), (16, 25)]
    for pts in [tuft_l, mir(tuft_l)]:
        s.part(s.poly(pts), HAIR['base'], HAIR['ol'], shade=HAIR['sh'], hi=HAIR['hi'])
    bangs = [(19, 18), (44, 18), (44, 27), (42, 25), (40, 29), (37, 25), (34, 28), (32, 25),
             (31, 25), (29, 28), (26, 25), (23, 29), (21, 25), (19, 27)]
    s.part(s.poly(bangs), HAIR['base'], HAIR['ol'], shade=HAIR['sh'], shade_off=(1, 1), hi=HAIR['hi'])

    # Eyes: tall ovals with a glint, Gen 5 style.
    for x0 in (25, 36):
        eye = s.rect((x0, 30, x0 + 2, 34))
        s.paint(eye, EYE['dark'])
        s.dots([(x0 + 1, 33), (x0 + 1, 32)], EYE['iris'])
        s.dots([(x0, 30)], EYE['glint'])
    s.dots([(24, 29), (39, 29)], HAIR['ol'])   # lash flicks
    s.dots([(30, 38), (31, 39), (32, 39), (33, 38)], SKIN['ol'])  # smile
    s.dots([(31, 36)], SKIN['sh'])  # nose
    s.dots([(22, 36), (23, 36), (40, 36), (41, 36)], BLUSH)

    # Straw hat: brim, then crown sitting in its centre, then band.
    crown = s.ellipse((19, 0, 44, 30)) & s.rect((0, 0, W, 17))
    s.part(brim, HAT['base'], HAT['ol'], shade=HAT['sh'], shade_off=(0, 2), hi=HAT['hi'])
    s.paint(brim & shift(crown, 0, -1) & ~crown, HAT['sh'])  # crown's shadow on brim
    s.part(crown, HAT['base'], HAT['ol'], shade=HAT['sh'], shade_off=(3, 0), hi=HAT['hi'])
    band = crown & s.rect((0, 12, W, 16))
    s.part(band, BAND['base'], BAND['ol'], shade=BAND['sh'], shade_off=(3, 0))
    # Woven straw texture.
    s.dots([(23, 5), (27, 3), (32, 2), (37, 4), (25, 9), (30, 7), (35, 8), (40, 9),
            (12, 17), (18, 20), (45, 20), (51, 17), (15, 21), (48, 21)], HAT['sh'])

    # Arms: sleeves with rolled cuffs, forearms, hands. His right hand
    # (viewer's right) holds a rolled-up blueprint.
    roll = s.poly([(47, 49), (53, 50), (51, 78), (45, 77)])
    s.part(roll, PRINT['base'], PRINT['ol'], shade=PRINT['sh'], shade_off=(2, 0), hi=PRINT['hi'])
    s.part(s.ellipse((46, 46, 54, 52)), PRINT['paper'], PRINT['ol'], shade=PRINT['hi'], shade_off=(1, 1))
    s.dots([(50, 49)], PRINT['sh'])
    s.dots([(48, 57), (49, 57), (50, 57), (48, 70), (49, 70), (47, 73), (48, 73)], PRINT['hi'])

    sleeve_l = [(16, 45), (22, 45), (22, 55), (13, 55), (13, 48)]
    for pts in [sleeve_l, mir(sleeve_l)]:
        s.part(s.poly(pts), SHIRT['base'], SHIRT['ol'], shade=SHIRT['sh'], shade_off=(2, 1))
    for box in [(13, 52, 22, 56), mirbox((13, 52, 22, 56))]:
        s.part(s.rect(box), SHIRT['sh'], SHIRT['ol'])
    for box in [(14, 56, 20, 64), mirbox((14, 56, 20, 64))]:
        s.part(s.rect(box), SKIN['base'], SKIN['ol'], shade=SKIN['sh'], shade_off=(2, 0))
    s.part(s.ellipse((13, 62, 20, 69)), SKIN['base'], SKIN['ol'], shade=SKIN['sh'], shade_off=(2, 1))
    s.part(s.ellipse((43, 61, 52, 69)), SKIN['base'], SKIN['ol'], shade=SKIN['sh'], shade_off=(2, 1))
    s.dots([(47, 64), (48, 64), (47, 66), (48, 66)], SKIN['sh'])  # curled fingers

    return s
