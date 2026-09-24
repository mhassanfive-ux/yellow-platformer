import os
import struct

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TILE = 64.0
COLS = 10  # x = 0..9, a narrow vertical shaft rather than a wide horizontal level

# Snow atlas coords (col, row) in the shared spritesheet -- same tileset as Level04, so
# this reads as continuing up the same mountain past its summit sign.
TOP, TL, TR = (5, 14), (6, 14), (7, 14)
CEN, LEFT, RIGHT = (2, 14), (3, 14), (4, 14)
HL, HM, HR = (13, 14), (14, 14), (17, 14)

# Room floors, top to bottom of the climb (rows increase downward in Godot).
R5_ROW = 8    # summit: crumbling platforms + goal
R4_ROW = 16   # moving platform over a gap
R3_ROW = 24   # ice ledges (== R2's top -- the two rooms share one floor row)
SPRING_LAND_ROW = 28  # mid-ledge the spring boosts you onto
R2_ROW = 32   # spring pad + base of the internal ladder
R1_ROW = 40   # base camp


def stand_y(row):
    """World y for a character standing on top of a tile/platform at this row."""
    return row * TILE - 32.0


def tile_xy(col, row):
    """World position for a tile's own centre, for placing tile sprites."""
    return (col * TILE + TILE / 2.0, row * TILE + TILE / 2.0)


def plat(x0, row, n):
    out = [(x0, row, *HL)]
    for i in range(1, n - 1):
        out.append((x0 + i, row, *HM))
    out.append((x0 + n - 1, row, *HR))
    return out


def floor_strip(col_start, col_end, row):
    """A solid ground strip from col_start to col_end (inclusive) at `row`, with a plain
    dirt-fill row beneath it. Edge caps only appear where the strip borders a real gap
    (col_start > 0 or col_end < COLS - 1), matching the look of every other level's ground.
    The top-row cell is added even where a room later marks it as ice (see ice_cells) --
    the data-packing step below overrides the atlas coords for those, same as Level04."""
    out = []
    for x in range(col_start, col_end + 1):
        if x == col_start and col_start > 0:
            t, d = TL, LEFT
        elif x == col_end and col_end < COLS - 1:
            t, d = TR, RIGHT
        else:
            t, d = TOP, CEN
        out.append((x, row, *t))
        out.append((x, row + 1, *d))
    return out


# Every inter-room ladder needs a column with NO floor tile at its destination row to
# climb through -- a ladder whose top sits under a solid tile in its own column is the
# exact "climbs into the ceiling" bug Level04's tower hit. Each room's floor below leaves
# a one-column notch exactly at the ladder that lands there; the ladder's own BASE is
# always allowed to coincide with solid ground (that's just standing on the floor).
LADDER0_COL = 9  # room1 -> room2, notch in room2's floor
LADDER1_COL = 8  # mid-ledge -> room3, notch in room3's (ice) floor
LADDER2_COL = 0  # room3 -> room4, notch in room4's floor
LADDER3_COL = 9  # room4 -> room5, notch in room5's floor

cells = []
ice_cells = set()

# Room 1 -- base camp: solid floor the full width, spikes to hop, checkpoint, ladder up.
cells += floor_strip(0, COLS - 1, R1_ROW)

# Room 2 -- spring pad floor (notch at column 9 for Ladder0) and the mid-ledge.
cells += floor_strip(0, LADDER0_COL - 1, R2_ROW)
cells += plat(6, SPRING_LAND_ROW, 3)  # mid-ledge, columns 6-8

# Room 3 -- ice ledges: the whole floor is the real ice tile (source 1), not an overlay,
# with a notch at column 8 for Ladder1.
for x in range(0, LADDER1_COL):
    ice_cells.add((x, R3_ROW))
cells += floor_strip(0, LADDER1_COL - 1, R3_ROW)

# Room 4 -- moving platform gap (columns 3-6 open); the left landing also leaves a notch
# at column 0 for Ladder2.
cells += floor_strip(LADDER2_COL + 1, 2, R4_ROW)
cells += floor_strip(7, COLS - 1, R4_ROW)

# Room 5 -- summit: solid landing on both ends (crumbling platforms bridge columns 4-7),
# with a notch at column 9 for Ladder3.
cells += floor_strip(0, 3, R5_ROW)
cells += floor_strip(8, LADDER3_COL - 1, R5_ROW)

data = [0, 0]
for (x, y, ax, ay) in cells:
    source_id = 1 if (x, y) in ice_cells else 0
    if source_id == 1:
        ax, ay = 0, 0
    data += list(struct.pack('<hhHHHH', x, y, source_id, ax, ay, 0))
tmd = "PackedByteArray(" + ", ".join(map(str, data)) + ")"

spawn = (1 * TILE + 32.0, stand_y(R1_ROW))

stars = [
    (6 * TILE + 32.0, stand_y(R1_ROW)),
    (7 * TILE + 32.0, stand_y(SPRING_LAND_ROW)),
    (2 * TILE + 32.0, stand_y(R3_ROW)),
    (4 * TILE + 32.0, stand_y(R4_ROW)),
    (6 * TILE + 32.0, stand_y(R5_ROW)),
]

checkpoints = [
    (8 * TILE + 32.0, stand_y(R1_ROW)),
    (7 * TILE + 32.0, stand_y(R3_ROW)),
    (8 * TILE + 32.0, stand_y(R4_ROW)),
]

spikes = [
    (4 * TILE + 32.0, R1_ROW * TILE),
    (4 * TILE + 32.0, R3_ROW * TILE),
]

# Column 4, NOT under the mid-ledge (columns 6-8): a spring's rise is almost straight up,
# so launching directly beneath a platform just bonks its underside instead of clearing
# it. From here the rise has clear air well past the ledge's height, and the player has
# to hold right during the arc to drift onto it -- landing on the way back down, since
# the ledge (4 tiles up) is well under the spring's full apex (~5 tiles).
SPRING_COL = 4
spring_pos = (SPRING_COL * TILE + 32.0, R2_ROW * TILE)

# (column, top_row, height_tiles)
ladders = [
    (LADDER0_COL, R2_ROW, R1_ROW - R2_ROW),                # room1 -> room2 (spring pad floor)
    (LADDER1_COL, R3_ROW, SPRING_LAND_ROW - R3_ROW),       # mid-ledge -> room3 (ice floor)
    (LADDER2_COL, R4_ROW, R3_ROW - R4_ROW),                # room3 -> room4
    (LADDER3_COL, R5_ROW, R4_ROW - R5_ROW),                # room4 -> room5
]

# The platform is 2 tiles (128px) wide and the gap it bridges is exactly 4 tiles
# (columns 3-6, 256px). A sweep that exactly touches each edge gives a single-frame
# boarding window -- reachable in principle, but rewards frame-perfect timing rather than
# the platforming skill the room is meant to test. Extending the sweep by REACH_MARGIN on
# each side has it briefly overlap the solid ground at both ends instead, so there's a
# real window to just walk on (an AnimatableBody2D overlapping static ground causes no
# collision issue -- nothing is pushed, a CharacterBody2D just sees solid floor there).
REACH_MARGIN = 20.0
moving_platform = {
    "pos": (3 * TILE + 32.0 - REACH_MARGIN, R4_ROW * TILE + 32.0),
    "travel": (2 * TILE + 2 * REACH_MARGIN, 0.0),
    "speed": 90.0,
    "tiles": 2,
}

crumbling = [
    (7 * TILE + 32.0, R5_ROW * TILE + 32.0),
    (6 * TILE + 32.0, R5_ROW * TILE + 32.0),
    (5 * TILE + 32.0, R5_ROW * TILE + 32.0),
    (4 * TILE + 32.0, R5_ROW * TILE + 32.0),
]

goal_pos = (1 * TILE + 32.0, stand_y(R5_ROW))

bounds_top = (R5_ROW - 5) * TILE
bounds_bottom = (R1_ROW + 3) * TILE

out = f'''[gd_scene load_steps=18 format=3]

[ext_resource type="PackedScene" path="res://scenes/Player.tscn" id="1_player"]
[ext_resource type="TileSet" path="res://tilesets/snow_tileset.tres" id="2_tileset"]
[ext_resource type="Texture2D" path="res://assets/Sprites/Backgrounds/Default/background_solid_sky.png" id="3_sky"]
[ext_resource type="Texture2D" path="res://assets/Sprites/Backgrounds/Default/background_clouds.png" id="4_clouds"]
[ext_resource type="Texture2D" path="res://assets/Sprites/Backgrounds/Default/background_solid_cloud.png" id="4b_cloudsolid"]
[ext_resource type="Script" path="res://scripts/kill_zone.gd" id="5_killzone"]
[ext_resource type="Script" path="res://scripts/level.gd" id="6_level"]
[ext_resource type="PackedScene" path="res://scenes/Ladder.tscn" id="7_ladder"]
[ext_resource type="PackedScene" path="res://scenes/Star.tscn" id="8_star"]
[ext_resource type="PackedScene" path="res://scenes/HUD.tscn" id="9_hud"]
[ext_resource type="PackedScene" path="res://scenes/Checkpoint.tscn" id="10_checkpoint"]
[ext_resource type="PackedScene" path="res://scenes/Goal.tscn" id="11_goal"]
[ext_resource type="PackedScene" path="res://scenes/Spikes.tscn" id="12_spikes"]
[ext_resource type="PackedScene" path="res://scenes/Spring.tscn" id="13_spring"]
[ext_resource type="PackedScene" path="res://scenes/MovingPlatform.tscn" id="14_movingplatform"]
[ext_resource type="PackedScene" path="res://scenes/CrumblingPlatform.tscn" id="15_crumbling"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_wall"]
size = Vector2(32, {bounds_bottom - bounds_top + 1000.0})

[sub_resource type="RectangleShape2D" id="RectangleShape2D_killzone"]
size = Vector2({COLS * 64 + 640}, 200)

[node name="Level05" type="Node2D"]
script = ExtResource("6_level")
bounds = Rect2(0, {bounds_top}, {COLS * 64}, {bounds_bottom - bounds_top})
has_rival = false

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

[node name="CloudsBackground" type="Sprite2D" parent="."]
position = Vector2({-64.0}, {bounds_top - 128.0})
centered = false
texture = ExtResource("4_clouds")
texture_repeat = 2
region_enabled = true
region_rect = Rect2(0, 0, {COLS * 64 + 128}, {bounds_bottom - bounds_top + 256})

[node name="CloudCeiling" type="Sprite2D" parent="."]
position = Vector2({COLS * 32}, {(bounds_top + R3_ROW * TILE) / 2.0})
centered = true
texture = ExtResource("4b_cloudsolid")
scale = Vector2({(COLS * 64 + 64) / 256.0}, {(R3_ROW * TILE - bounds_top) / 256.0})
modulate = Color(1, 1, 1, 0.6)

[node name="TileMapLayer" type="TileMapLayer" parent="."]
tile_map_data = {tmd}
tile_set = ExtResource("2_tileset")

[node name="Decor" type="Node2D" parent="."]
'''

out += f'''
[node name="PlayerSpawn" type="Marker2D" parent="."]
position = Vector2({spawn[0]}, {spawn[1]})

[node name="Player" parent="." instance=ExtResource("1_player")]
position = Vector2({spawn[0]}, {spawn[1]})

[node name="LeftWall" type="StaticBody2D" parent="."]
position = Vector2(-16, {(bounds_top + bounds_bottom) / 2.0})

[node name="CollisionShape2D" type="CollisionShape2D" parent="LeftWall"]
shape = SubResource("RectangleShape2D_wall")

[node name="RightWall" type="StaticBody2D" parent="."]
position = Vector2({COLS * 64 + 16}, {(bounds_top + bounds_bottom) / 2.0})

[node name="CollisionShape2D" type="CollisionShape2D" parent="RightWall"]
shape = SubResource("RectangleShape2D_wall")

[node name="KillZone" type="Area2D" parent="."]
position = Vector2({COLS * 64 // 2}, {bounds_bottom + 96.0})
collision_layer = 0
collision_mask = 2
script = ExtResource("5_killzone")
spawn_point_path = NodePath("../PlayerSpawn")

[node name="CollisionShape2D" type="CollisionShape2D" parent="KillZone"]
shape = SubResource("RectangleShape2D_killzone")

[node name="Ladders" type="Node2D" parent="."]
'''
for i, (col, top_row, height) in enumerate(ladders):
    out += f'\n[node name="Ladder{i}" parent="Ladders" instance=ExtResource("7_ladder")]\nposition = Vector2({col * 64 + 32}, {top_row * 64})\nheight_tiles = {height}\n'

out += f'''
[node name="Spring" parent="." instance=ExtResource("13_spring")]
position = Vector2({spring_pos[0]}, {spring_pos[1]})

[node name="Hazards" type="Node2D" parent="."]
'''
for i, pos in enumerate(spikes, 1):
    out += f'\n[node name="Spikes{i}" parent="Hazards" instance=ExtResource("12_spikes")]\nposition = Vector2({pos[0]}, {pos[1]})\n'

out += '\n[node name="MovingPlatform" parent="." instance=ExtResource("14_movingplatform")]\n'
out += f'position = Vector2({moving_platform["pos"][0]}, {moving_platform["pos"][1]})\n'
out += f'tiles = {moving_platform["tiles"]}\n'
out += f'travel_offset = Vector2({moving_platform["travel"][0]}, {moving_platform["travel"][1]})\n'
out += f'speed = {moving_platform["speed"]}\n'

out += '\n[node name="CrumblingPlatforms" type="Node2D" parent="."]\n'
for i, pos in enumerate(crumbling, 1):
    out += f'\n[node name="Crumbling{i}" parent="CrumblingPlatforms" instance=ExtResource("15_crumbling")]\nposition = Vector2({pos[0]}, {pos[1]})\n'

out += '\n[node name="Stars" type="Node2D" parent="."]\n'
for i, pos in enumerate(stars, 1):
    out += f'\n[node name="Star{i}" parent="Stars" instance=ExtResource("8_star")]\nposition = Vector2({pos[0]}, {pos[1]})\n'

out += '\n[node name="Checkpoints" type="Node2D" parent="."]\n'
for i, pos in enumerate(checkpoints, 1):
    out += f'\n[node name="Checkpoint{i}" parent="Checkpoints" instance=ExtResource("10_checkpoint")]\nposition = Vector2({pos[0]}, {pos[1] + 32})\n'

out += f'''
[node name="Goal" parent="." instance=ExtResource("11_goal")]
position = Vector2({goal_pos[0]}, {goal_pos[1] + 32})

[node name="HUD" parent="." instance=ExtResource("9_hud")]
show_key_slot = false
show_rival_counter = false
'''

with open(os.path.join(PROJECT, "scenes", "Level05.tscn"), "w", newline="\n") as f:
    f.write(out)

print("wrote Level05.tscn:", len(cells), "tiles,", len(stars), "stars,", len(checkpoints),
      "checkpoints,", len(ladders), "ladders,", len(crumbling), "crumbling platforms")
print("bounds y:", bounds_top, "to", bounds_bottom)
