"""Player palette. Each material has highlight / base / shade / outline steps;
outlines are a dark tint of their own material (selective outlining) rather than
pure black, which keeps the sprite soft like the Gen 5 handheld sprites."""

HAT = dict(hi='#FCE7A8', base='#EBC56E', sh='#C9973F', ol='#6A4419')
BAND = dict(hi='#F06A55', base='#D9473B', sh='#A32F2E', ol='#5A1A1E')
HAIR = dict(hi='#B9784C', base='#8C4F2D', sh='#62341D', ol='#33190E')
SKIN = dict(hi='#FFE9D2', base='#FBD1A8', sh='#E3A57E', ol='#8E5139')
SHIRT = dict(hi='#FFFFFF', base='#F4F4EC', sh='#C6CBDA', ol='#565B72')
OVERALL = dict(hi='#7CC370', base='#4E9C55', sh='#357343', ol='#1C3F27')
BAG = dict(hi='#C98A52', base='#A0643A', sh='#744425', ol='#3B2113')
BOOT = dict(hi='#8C5D40', base='#6E4630', sh='#4C2E1F', ol='#24150E')
SOLE = dict(base='#D9B98A', sh='#B08F62')
PRINT = dict(hi='#A9CCF5', base='#5B8FDB', sh='#3C66B0', ol='#1D2F63', paper='#EAF2FF')
LEAF = dict(hi='#A6E57D', base='#6CC452', sh='#3F9A3F', ol='#1E4D22')
BRASS = dict(base='#F2C94C', ol='#8A6A1E')
EYE = dict(dark='#2A2030', iris='#6B4A3A', glint='#FFFFFF')
BLUSH = '#F4A08A'

# Swatches shown on the concept sheet, in reading order.
SWATCHES = [
    ('Straw hat', HAT), ('Hat band / scarf', BAND), ('Hair', HAIR),
    ('Skin', SKIN), ('Shirt', SHIRT), ('Overalls', OVERALL),
    ('Satchel', BAG), ('Boots', BOOT), ('Blueprint', PRINT), ('Sprout', LEAF),
]
