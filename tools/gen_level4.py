import os
import struct

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TILE = 64.0
W = 70                      # tiles wide -> 4480px, the longest level yet
GROUND_ROW = 9               # snow-cap row
DIRT_ROW = 10                # dirt-fill row

# Snow atlas coords (col, row) in the shared spritesheet.
TOP, TL, TR = (5, 14), (6, 14), (7, 14)
CEN, LEFT, RIGHT = (2, 14), (3, 14), (4, 14)
HL, HM, HR = (13, 14), (14, 14), (17, 14)

# All jumpable, ordinary gaps -- nothing in the level's main path depends on the switch.
gaps = [(11, 12), (44, 45), (58, 59)]


def is_gap(x):
    return any(a <= x <= b for a, b in gaps)


def stand_y(row):
    """World y for a character standing on top of a tile/platform at this row."""
    return row * TILE - 32.0


def tile_xy(col, row):
    """World position for a tile's own centre, for placing tile sprites."""
    return (col * TILE + TILE / 2.0, row * TILE + TILE / 2.0)


cells = []
for x in range(W):
    if is_gap(x):
        continue
    le = x > 0 and is_gap(x - 1)
    re_ = x < W - 1 and is_gap(x + 1)
    top = TL if le else TR if re_ else TOP
    dirt = LEFT if le else RIGHT if re_ else CEN
    cells += [(x, GROUND_ROW, *top), (x, DIRT_ROW, *dirt)]


def plat(x0, row, n):
    out = [(x0, row, *HL)]
    for i in range(1, n - 1):
        out.append((x0 + i, row, *HM))
    out.append((x0 + n - 1, row, *HR))
    return out


# No extra stepping stone at gap1 either, in the end: an elevated launch pad lets you hop
# DOWN off it across the gap easily, but jumping back UP onto it from the far side needs
# meaningfully more horizontal reach than the same-height downhill jump does (falling adds
# airtime; rising against gravity costs it) -- a real headless rival trace confirmed the
# reverse crossing was simply impossible with this project's jump parameters, a one-way
# gate, not a nav bug. All three gaps are now plain, symmetric, ground-level gaps.

# Bonus puzzle (x 14-21): a short ladder (proven-safe 3-tile clearance from the ground,
# same height as the tower) leads to a landing platform; past it is a 3-tile horizontal
# gap, too wide for a direct jump (a flat jump only clears ~2 tiles here), bridged by the
# switch's hidden platform. Two earlier versions of this puzzle put a platform only 1 tile
# above the ground the player already walks on -- its solid underside sat at exactly the
# player's own standing height, physically blocking them before they ever got a chance to
# jump. Every platform with open ground directly beneath it needs real clearance (~3
# tiles, matching the tower) or a genuine gap, not a 1-tile step; an honest ground-up walk
# test, not teleporting onto the platform to test the rest of the puzzle in isolation, is
# what caught both versions.
cells += plat(15, 6, 3)    # landing platform, x15-17, y=384 surface (3 tiles above ground)

# Tower (x 35-44): always accessible, no switch involved. Each ladder sits BESIDE the
# platform it climbs to (not under any of its tiles) -- climbing straight up must never
# pass through the destination platform's own solid tile, or the climber just bonks its
# head on its underside forever. The first version got this wrong for all three ladders;
# a headless trace of the rival stuck mid-climb is what caught it. Reaching the platform
# is then a short sideways step off the top of the ladder, same as every other ladder.
# Named so the ice patch below can reuse these exact bounds instead of a hand-copied
# guess that can silently drift out of sync whenever a platform moves (as happened here:
# an earlier edit relocated the goal-rise platform and left its ice patch floating at the
# old height, and the tower's ice patch was a column off from where the tower actually is).
T1 = (36, 6, 4)    # x36-39, y=384 surface -- ladder1 climbs beside it at x35
T2 = (39, 3, 4)    # x39-42, y=192 surface -- ladder2 climbs beside it at x37 (on T1, left of T2)
T3 = (42, 0, 3)    # x42-44, y=0 surface   -- ladder3 climbs beside it at x40 (on T2, left of T3)
cells += plat(*T1)
cells += plat(*T2)
cells += plat(*T3)

# A short, ordinary 1-tile step up to the goal (matching the gap1 stepping stone's
# height) -- the earlier row6 version was 3 tiles above ground with no ladder, an
# unreachable jump, which is exactly what the reachability test caught.
GOAL_RISE = (64, 8, 4)
cells += plat(*GOAL_RISE)

# Ice tiles: real TileSet tiles (source 1, the single-tile ice_block.png atlas) dropped
# straight into the ground/platform layout in place of the normal snow tile, not a
# separate overlay area -- slipperiness is a property the tile itself carries (its
# TileData "ice" custom data, read by player.gd), so there's nothing else to keep in sync.
# Each zone reuses a platform's own placement tuple directly (see T1/GOAL_RISE above), so
# it always exactly covers that platform and nothing else.
ice_zones = [(2, GROUND_ROW, 5), T1, GOAL_RISE]
ice_cells = set()
for (x0, row, w) in ice_zones:
    for i in range(w):
        ice_cells.add((x0 + i, row))

data = [0, 0]
for (x, y, ax, ay) in cells:
    if (x, y) in ice_cells:
        source_id, ax, ay = 1, 0, 0
    else:
        source_id = 0
    data += list(struct.pack('<hhHHHH', x, y, source_id, ax, ay, 0))
tmd = "PackedByteArray(" + ", ".join(map(str, data)) + ")"

spawn = (2 * TILE + 32.0, stand_y(GROUND_ROW))
stars = [
    (5 * TILE + 32.0, stand_y(GROUND_ROW)),       # intro star on the ground
    (9 * TILE + 32.0, stand_y(GROUND_ROW)),        # near gap1
    (19 * TILE + 32.0, stand_y(6)),                # bonus star on the hidden platform (switch-gated)
    (25 * TILE + 32.0, stand_y(GROUND_ROW)),
    (36 * TILE + 32.0, stand_y(6)),                # T1
    (40 * TILE + 32.0, stand_y(3)),                # T2
    (43 * TILE + 32.0, stand_y(0)),                # T3
    (47 * TILE + 32.0, stand_y(GROUND_ROW)),       # after gap2
    (52 * TILE + 32.0, stand_y(GROUND_ROW)),
    (61 * TILE + 32.0, stand_y(GROUND_ROW)),       # after gap3
    (65 * TILE + 32.0, stand_y(8)),                # on the rise to the goal
]
snails = [
    (5 * TILE, stand_y(GROUND_ROW)),
    (27 * TILE, stand_y(GROUND_ROW)),
    (50 * TILE, stand_y(GROUND_ROW)),
    (62 * TILE, stand_y(GROUND_ROW)),
]
slimes = [(30 * TILE, stand_y(GROUND_ROW) + 2.0), (54 * TILE, stand_y(GROUND_ROW) + 2.0)]
bees = [(40.5 * TILE, stand_y(3) - 100.0), (66 * TILE, stand_y(8) - 260.0)]

checkpoints = [(24 * TILE + 32.0, stand_y(GROUND_ROW)), (49 * TILE + 32.0, stand_y(GROUND_ROW))]
switch_pos = (13 * TILE + 32.0, stand_y(GROUND_ROW))
hidden_platform_pos = tile_xy(19, 6)   # bridges the 3-tile gap past the landing platform
goal_pos = (66 * TILE + 32.0, stand_y(8))
rival_pos = ((W - 3) * TILE, stand_y(GROUND_ROW))

T = "res://assets/Sprites/Tiles/Default/"
out = f'''[gd_scene load_steps=22 format=3]

[ext_resource type="PackedScene" path="res://scenes/Player.tscn" id="1_player"]
[ext_resource type="TileSet" path="res://tilesets/snow_tileset.tres" id="2_tileset"]
[ext_resource type="Texture2D" path="res://assets/Sprites/Backgrounds/Default/background_solid_sky.png" id="3_sky"]
[ext_resource type="Texture2D" path="res://assets/Sprites/Backgrounds/Transparent/background_fade_trees.png" id="5_trees"]
[ext_resource type="PackedScene" path="res://scenes/Enemy.tscn" id="6_enemy"]
[ext_resource type="PackedScene" path="res://scenes/Bee.tscn" id="7_bee"]
[ext_resource type="PackedScene" path="res://scenes/Snail.tscn" id="8_snail"]
[ext_resource type="Script" path="res://scripts/kill_zone.gd" id="9_killzone"]
[ext_resource type="Script" path="res://scripts/level.gd" id="10_level"]
[ext_resource type="PackedScene" path="res://scenes/Ladder.tscn" id="11_ladder"]
[ext_resource type="PackedScene" path="res://scenes/Star.tscn" id="12_star"]
[ext_resource type="PackedScene" path="res://scenes/Rival.tscn" id="13_rival"]
[ext_resource type="PackedScene" path="res://scenes/HUD.tscn" id="14_hud"]
[ext_resource type="PackedScene" path="res://scenes/Checkpoint.tscn" id="15_checkpoint"]
[ext_resource type="PackedScene" path="res://scenes/Goal.tscn" id="16_goal"]
[ext_resource type="PackedScene" path="res://scenes/Switch.tscn" id="18_switch"]
[ext_resource type="PackedScene" path="res://scenes/HiddenPlatform.tscn" id="19_hiddenplatform"]
[ext_resource type="Texture2D" path="{T}rock.png" id="20_rock"]
[ext_resource type="Texture2D" path="{T}sign_right.png" id="21_sign_right"]
[ext_resource type="Texture2D" path="{T}sign_exit.png" id="22_sign_exit"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_wall"]
size = Vector2(32, 1600)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_killzone"]
size = Vector2({W * 64 + 640}, 200)
'''

out += f'''
[node name="Level04" type="Node2D"]
script = ExtResource("10_level")
bounds = Rect2(0, -512, {W * 64}, 1216)

[node name="SkyLayer" type="CanvasLayer" parent="."]
layer = -10

[node name="Sky" type="TextureRect" parent="SkyLayer"]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
texture = ExtResource("3_sky")
stretch_mode = 1

[node name="ParallaxBackground" type="ParallaxBackground" parent="."]

[node name="TreesLayer" type="ParallaxLayer" parent="ParallaxBackground"]
motion_scale = Vector2(0.4, 1)
motion_mirroring = Vector2(256, 0)

[node name="Trees" type="Sprite2D" parent="ParallaxBackground/TreesLayer"]
position = Vector2(0, 368)
texture = ExtResource("5_trees")
centered = false

[node name="TileMapLayer" type="TileMapLayer" parent="."]
tile_map_data = {tmd}
tile_set = ExtResource("2_tileset")

[node name="Decor" type="Node2D" parent="."]

[node name="SignStart" type="Sprite2D" parent="Decor"]
position = Vector2(300, {stand_y(GROUND_ROW) + 32.0})
texture = ExtResource("21_sign_right")

[node name="Rock1" type="Sprite2D" parent="Decor"]
position = Vector2(1900, {stand_y(GROUND_ROW) + 32.0})
texture = ExtResource("20_rock")

[node name="Rock2" type="Sprite2D" parent="Decor"]
position = Vector2(3300, {stand_y(GROUND_ROW) + 32.0})
texture = ExtResource("20_rock")

[node name="SignExit" type="Sprite2D" parent="Decor"]
position = Vector2({66 * 64 - 96}, {stand_y(8) + 32.0})
texture = ExtResource("22_sign_exit")

[node name="PlayerSpawn" type="Marker2D" parent="."]
position = Vector2({spawn[0]}, {spawn[1]})

[node name="Player" parent="." instance=ExtResource("1_player")]
position = Vector2({spawn[0]}, {spawn[1]})

[node name="Rival" parent="." instance=ExtResource("13_rival")]
position = Vector2({rival_pos[0]}, {rival_pos[1]})

[node name="LeftWall" type="StaticBody2D" parent="."]
position = Vector2(-16, 96)

[node name="CollisionShape2D" type="CollisionShape2D" parent="LeftWall"]
shape = SubResource("RectangleShape2D_wall")

[node name="RightWall" type="StaticBody2D" parent="."]
position = Vector2({W * 64 + 16}, 96)

[node name="CollisionShape2D" type="CollisionShape2D" parent="RightWall"]
shape = SubResource("RectangleShape2D_wall")

[node name="Enemies" type="Node2D" parent="."]
'''
for i, pos in enumerate(snails, 1):
    out += f'\n[node name="Snail{i}" parent="Enemies" instance=ExtResource("8_snail")]\nposition = Vector2({pos[0]}, {pos[1]})\n'
for i, pos in enumerate(slimes, 1):
    out += f'\n[node name="Slime{i}" parent="Enemies" instance=ExtResource("6_enemy")]\nposition = Vector2({pos[0]}, {pos[1]})\n'
for i, pos in enumerate(bees, 1):
    out += f'\n[node name="Bee{i}" parent="Enemies" instance=ExtResource("7_bee")]\nposition = Vector2({pos[0]}, {pos[1]})\n'

out += f'''
[node name="KillZone" type="Area2D" parent="."]
position = Vector2({W * 64 // 2}, 800)
collision_layer = 0
collision_mask = 6
script = ExtResource("9_killzone")
spawn_point_path = NodePath("../PlayerSpawn")

[node name="CollisionShape2D" type="CollisionShape2D" parent="KillZone"]
shape = SubResource("RectangleShape2D_killzone")

[node name="Ladders" type="Node2D" parent="."]

[node name="Ladder0" parent="Ladders" instance=ExtResource("11_ladder")]
position = Vector2({14 * 64 + 32}, {6 * 64})
height_tiles = 3

[node name="Ladder1" parent="Ladders" instance=ExtResource("11_ladder")]
position = Vector2({35 * 64 + 32}, {6 * 64})
height_tiles = 3

[node name="Ladder2" parent="Ladders" instance=ExtResource("11_ladder")]
position = Vector2({38 * 64 + 32}, {3 * 64})
height_tiles = 3

[node name="Ladder3" parent="Ladders" instance=ExtResource("11_ladder")]
position = Vector2({41 * 64 + 32}, {0})
height_tiles = 3

[node name="Switch" parent="." instance=ExtResource("18_switch")]
position = Vector2({switch_pos[0]}, {switch_pos[1]})
target_path = NodePath("../HiddenPlatform")

[node name="HiddenPlatform" parent="." instance=ExtResource("19_hiddenplatform")]
position = Vector2({hidden_platform_pos[0]}, {hidden_platform_pos[1]})

[node name="Stars" type="Node2D" parent="."]
'''
for i, pos in enumerate(stars, 1):
    out += f'\n[node name="Star{i}" parent="Stars" instance=ExtResource("12_star")]\nposition = Vector2({pos[0]}, {pos[1]})\n'

out += '\n[node name="Checkpoints" type="Node2D" parent="."]\n'
for i, pos in enumerate(checkpoints, 1):
    out += f'\n[node name="Checkpoint{i}" parent="Checkpoints" instance=ExtResource("15_checkpoint")]\nposition = Vector2({pos[0]}, {pos[1] + 32})\n'

out += f'''
[node name="Goal" parent="." instance=ExtResource("16_goal")]
position = Vector2({goal_pos[0]}, {goal_pos[1] + 32})
next_level = "res://scenes/Level05.tscn"

[node name="HUD" parent="." instance=ExtResource("14_hud")]
show_key_slot = false
'''

with open(os.path.join(PROJECT, "scenes", "Level04.tscn"), "w", newline="\n") as f:
    f.write(out)

print("wrote Level04.tscn:", len(cells), "tiles,", len(stars), "stars,", len(snails), "snails,",
      len(slimes), "slimes,", len(bees), "bees,", len(ice_cells), "ice tiles")
print("switch at", switch_pos, "-> hidden platform at", hidden_platform_pos)
print("tower ladder anchors: L1 x=", 35*64+32, "L2 x=", 37*64+32, "L3 x=", 38*64+32)
print("gaps:", gaps)
