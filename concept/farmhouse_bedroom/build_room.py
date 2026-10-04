"""Builds the farmhouse bedroom in Blender and renders it the way the DS draws
its 3D rooms: low-poly boxes, tiny nearest-neighbour textures, a tilted
perspective camera, 256x192 output, and the player as a 1:1 pixel sprite.

    pip install bpy==5.0.1 pillow numpy   # bpy needs Python 3.11
    python3 build_room.py

Writes out/bedroom_256x192.png, out/bedroom_4x.png, out/bedroom.glb (the room,
for Godot) and out/bedroom.blend (camera and lights included).
"""
import math
import os
import sys

import bpy  # must come first: it makes bmesh and bpy_extras importable
import bmesh
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'player_boy'))
import overworld  # noqa: E402
import textures  # noqa: E402

RES = (256, 192)
DENSITY = 24          # texels per metre for tiling textures
PLAYER_AT = (0.0, -0.9)

# Room interior spans X -3.75..3.75 (left to right), Y -2.75..2.75 (front to back).
X0, X1, Y0, Y1 = -3.75, 3.75, -2.75, 2.75
WALL_T, WALL_H, BASE = 0.2, 2.2, -1.6
STAIR = (2.45, X1, 0.6, Y1)   # stairwell opening: x0, x1, y0, y1

TEX = {}
MATS = {}


def lin(hex_code):
    h = hex_code.lstrip('#')
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def mix_hex(a, b, t):
    ca = [int(a.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02X}' for x, y in zip(ca, cb))


def material(name, tex=None, color=None, rough=0.92, emit=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except AttributeError:
        pass
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Specular IOR Level'].default_value = 0.08
    if tex:
        img = bpy.data.images.load(TEX[tex])
        node = nt.nodes.new('ShaderNodeTexImage')
        node.image = img
        node.interpolation = 'Closest'
        nt.links.new(node.outputs['Color'], bsdf.inputs['Base Color'])
        if emit:
            nt.links.new(node.outputs['Color'], bsdf.inputs['Emission Color'])
        m['tex_px'] = list(img.size)
    else:
        bsdf.inputs['Base Color'].default_value = lin(color)
        if emit:
            bsdf.inputs['Emission Color'].default_value = lin(color)
    if emit:
        bsdf.inputs['Emission Strength'].default_value = emit
    if alpha < 1:
        bsdf.inputs['Alpha'].default_value = alpha
    MATS[name] = m
    return m


def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


FACES = {
    '+z': lambda x0, y0, z0, x1, y1, z1: [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
    '-z': lambda x0, y0, z0, x1, y1, z1: [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)],
    '+x': lambda x0, y0, z0, x1, y1, z1: [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
    '-x': lambda x0, y0, z0, x1, y1, z1: [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
    '+y': lambda x0, y0, z0, x1, y1, z1: [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
    '-y': lambda x0, y0, z0, x1, y1, z1: [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
}


def planar_uv(face, p):
    x, y, z = p
    return {'+z': (x, y), '-z': (x, -y), '+x': (y, z), '-x': (-y, z), '+y': (-x, z), '-y': (x, z)}[face]


def box(name, lo, hi, mat, faces=None, full=()):
    """Axis-aligned box. `faces` overrides the material per side ('+z', '-y', ...);
    sides listed in `full` show their texture once, edge to edge, instead of tiling."""
    faces = faces or {}
    me = bpy.data.meshes.new(name)
    ob = link(bpy.data.objects.new(name, me))
    slots = []
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new('UVMap')
    for key, corners in FACES.items():
        m = MATS[faces.get(key, mat)]
        if m.name not in slots:
            slots.append(m.name)
            me.materials.append(m)
        verts = [bm.verts.new(c) for c in corners(*lo, *hi)]
        f = bm.faces.new(verts)
        f.material_index = slots.index(m.name)
        tw, th = m.get('tex_px', (16, 16))
        for i, loop in enumerate(f.loops):
            if key in full:
                loop[uv].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][i]
            else:
                u, v = planar_uv(key, loop.vert.co)
                loop[uv].uv = (u * DENSITY / tw, v * DENSITY / th)
    bm.to_mesh(me)
    bm.free()
    return ob


def roof(name, lo, hi, mat):
    """Gable roof prism with its ridge along X."""
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    ym = (y0 + y1) / 2
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x0, y0, z0), (x1, y0, z0), (x1, ym, z1), (x0, ym, z1), (x0, y1, z0), (x1, y1, z0)], [],
                   [(0, 1, 2, 3), (5, 4, 3, 2), (0, 3, 4), (1, 5, 2), (0, 4, 5, 1)])
    me.materials.append(MATS[mat])
    return link(bpy.data.objects.new(name, me))


def prim(kind, mat, **kw):
    getattr(bpy.ops.mesh, f'primitive_{kind}_add')(**kw)
    ob = bpy.context.object
    ob.data.materials.append(MATS[mat])
    return ob


def build_materials():
    for name in ['floor', 'wallpaper', 'wainscot', 'rug', 'quilt', 'gingham', 'blueprint',
                 'calendar', 'crate', 'dark_wood', 'drawers', 'seed_bag', 'town_map']:
        material(name, tex=name)
    material('sky', tex='sky', emit=0.6)
    for name, c in {'cap': '#5E3A24', 'trim': '#8C5A3A', 'linen': '#F4F4EC', 'pot': '#C8664A',
                    'leaf': '#5FB05A', 'leaf_dk': '#3F8A48', 'teal': '#4AA3A8', 'brass': '#E8B84A',
                    'cream': '#F3E6C8', 'roof_red': '#CF5641', 'radio': '#A63E31', 'grill': '#4A2E1A',
                    'pencil': '#F2C94C', 'stairwell': '#2E1C12'}.items():
        material(name, color=c)
    material('lampshade', color='#FFE3A0', emit=1.5)
    for c in ['#D9473B', '#5B8FDB', '#5E9A57', '#E0B048', '#8C5A9A', '#F4EBD0', '#3C6EC8', '#C8664A']:
        material('book' + c, color=c)
    material('shadow', color='#000000', alpha=0.42)


def build_room():
    # Floor around the stairwell, with a thick front edge like a cut-away dollhouse.
    sx0, sx1, sy0, sy1 = STAIR
    edge = {'-y': 'cap', '+y': 'cap', '-x': 'cap', '+x': 'cap', '-z': 'cap'}
    box('floor_front', (X0, Y0, -0.3), (X1, sy0, 0), 'floor', {**edge, '+z': 'floor'})
    box('floor_back', (X0, sy0, -0.3), (sx0, Y1, 0), 'floor', {**edge, '+z': 'floor'})

    # Walls: wainscot below the rail, wallpaper above, dark caps on the cut edges.
    cap = {'+z': 'cap', '-y': 'cap', '-z': 'cap'}
    for name, lo, hi, faces in [
            ('back', (X0 - WALL_T, Y1, -0.3), (X1 + WALL_T, Y1 + WALL_T, 0.8), {'-z': 'cap'}),
            ('left', (X0 - WALL_T, Y0 - WALL_T, -0.3), (X0, Y1, 0.8), cap),
            ('right', (X1, Y0 - WALL_T, -0.3), (X1 + WALL_T, Y1, 0.8), cap)]:
        box(f'wall_{name}_low', lo, hi, 'wainscot', faces)
        box(f'wall_{name}_high', (lo[0], lo[1], 0.8), (hi[0], hi[1], WALL_H), 'wallpaper', {**faces, '+z': 'cap'})
    box('stairwell_back', (sx0, Y1, BASE), (X1 + WALL_T, Y1 + WALL_T, -0.3), 'stairwell')
    box('stairwell_right', (X1, sy0, BASE), (X1 + WALL_T, Y1, -0.3), 'stairwell')
    box('rail_back', (X0, Y1 - 0.05, 0.78), (X1, Y1, 0.86), 'trim')
    box('rail_left', (X0, Y0 - WALL_T, 0.78), (X0 + 0.05, Y1, 0.86), 'trim')
    box('rail_right', (X1 - 0.05, Y0 - WALL_T, 0.78), (X1, Y1, 0.86), 'trim')
    box('base_back', (X0, Y1 - 0.04, 0), (sx0, Y1, 0.12), 'trim')
    box('base_left', (X0, Y0 - WALL_T, 0), (X0 + 0.04, Y1, 0.12), 'trim')
    box('base_right', (X1 - 0.04, Y0 - WALL_T, 0), (X1, sy0, 0.12), 'trim')

    # Stairs going down at the back right, each step darker as it drops into the
    # stairwell, with a banister along the open side.
    n = 7
    depth = (sy1 - sy0) / n
    for i in range(n):
        tread, riser = f'tread_{i}', f'riser_{i}'
        material(tread, color=mix_hex('#C8925A', '#3A2416', i / (n - 1)))
        material(riser, color=mix_hex('#8C5A3A', '#24150E', i / (n - 1)))
        box(f'step_{i}', (sx0, sy0 + i * depth, BASE), (sx1, sy0 + (i + 1) * depth, -(i + 1) * 0.2),
            riser, {'+z': tread})
        box(f'nosing_{i}', (sx0, sy0 + i * depth, -(i + 1) * 0.2), (sx1, sy0 + i * depth + 0.04, -(i + 1) * 0.2 + 0.02),
            tread)
    for y in np.linspace(sy0, sy1 - 0.1, 6):
        box('baluster', (sx0 - 0.04, y, 0), (sx0 + 0.04, y + 0.06, 0.7), 'trim')
    box('banister', (sx0 - 0.06, sy0 - 0.02, 0.7), (sx0 + 0.06, sy1, 0.78), 'dark_wood')
    box('newel', (sx0 - 0.08, sy0 - 0.08, 0), (sx0 + 0.08, sy0 + 0.08, 0.9), 'dark_wood')


def build_furniture():
    # Bed in the front-right corner, headboard against the right wall.
    box('bed_frame', (1.85, -2.6, 0), (3.72, -1.4, 0.3), 'dark_wood')
    box('mattress', (1.9, -2.55, 0.3), (3.62, -1.45, 0.46), 'linen')
    box('quilt', (1.86, -2.62, 0.22), (3.0, -1.38, 0.5), 'quilt', {'+z': 'quilt'})
    box('pillow', (3.12, -2.38, 0.46), (3.58, -1.62, 0.6), 'linen')
    box('headboard', (3.6, -2.66, 0), (3.75, -1.34, 1.0), 'dark_wood')
    box('footboard', (1.76, -2.66, 0), (1.86, -1.34, 0.62), 'dark_wood')
    box('nightstand', (3.2, -1.25, 0), (3.75, -0.72, 0.55), 'dark_wood', {'-x': 'drawers'}, full=('-x',))
    prim('cylinder', 'brass', vertices=8, radius=0.05, depth=0.22, location=(3.47, -0.98, 0.66))
    prim('cone', 'lampshade', vertices=8, radius1=0.18, radius2=0.1, depth=0.18, location=(3.47, -0.98, 0.84))

    # Desk under the window, with the town plans spread out on it.
    box('desk_top', (-1.9, 2.1, 0.7), (-0.1, Y1, 0.78), 'dark_wood')
    for x in (-1.86, -0.18):
        for y in (2.14, 2.66):
            box('desk_leg', (x, y, 0), (x + 0.06, y + 0.06, 0.7), 'dark_wood')
    box('desk_plans', (-1.55, 2.18, 0.78), (-0.8, 2.66, 0.79), 'blueprint', {'+z': 'blueprint'}, full=('+z',))
    box('model_house', (-0.62, 2.32, 0.78), (-0.32, 2.56, 0.95), 'cream')
    roof('model_roof', (-0.66, 2.28, 0.95), (-0.28, 2.6, 1.1), 'roof_red')
    prim('cylinder', 'teal', vertices=8, radius=0.06, depth=0.14, location=(-1.75, 2.58, 0.85))
    for dx, h in ((-0.02, 0.24), (0.02, 0.2)):
        box('pencil', (-1.75 + dx, 2.57, 0.85), (-1.73 + dx, 2.59, 0.78 + h), 'pencil')
    box('chair_seat', (-1.25, 1.5, 0.42), (-0.75, 1.98, 0.48), 'dark_wood')
    for x in (-1.24, -0.81):
        for y in (1.52, 1.91):
            box('chair_leg', (x, y, 0), (x + 0.05, y + 0.05, 0.42), 'dark_wood')
    box('chair_back', (-1.25, 1.46, 0.48), (-0.75, 1.52, 0.98), 'dark_wood')

    # Window with gingham curtains.
    box('window_frame', (-1.55, Y1 - 0.06, 1.08), (-0.45, Y1, 1.92), 'trim')
    box('window_glass', (-1.47, Y1 - 0.08, 1.16), (-0.53, Y1 - 0.06, 1.84), 'sky', {'-y': 'sky'}, full=('-y',))
    box('mullion_v', (-1.02, Y1 - 0.1, 1.16), (-0.98, Y1 - 0.08, 1.84), 'trim')
    box('mullion_h', (-1.47, Y1 - 0.1, 1.48), (-0.53, Y1 - 0.08, 1.52), 'trim')
    box('sill', (-1.62, Y1 - 0.14, 1.03), (-0.38, Y1, 1.09), 'trim')
    box('curtain_l', (-1.78, Y1 - 0.12, 1.0), (-1.48, Y1 - 0.04, 2.02), 'gingham')
    box('curtain_r', (-0.52, Y1 - 0.12, 1.0), (-0.22, Y1 - 0.04, 2.02), 'gingham')
    box('curtain_rod', (-1.9, Y1 - 0.14, 2.02), (-0.1, Y1 - 0.08, 2.06), 'dark_wood')

    # Wall decor: the valley map and a calendar.
    box('map', (0.45, Y1 - 0.02, 1.12), (1.55, Y1, 1.88), 'town_map', {'-y': 'town_map'}, full=('-y',))
    box('calendar', (1.78, Y1 - 0.02, 1.25), (2.08, Y1, 1.68), 'calendar', {'-y': 'calendar'}, full=('-y',))
    for x, z in ((0.5, 1.83), (1.5, 1.83)):
        box('pin', (x - 0.02, Y1 - 0.05, z - 0.02), (x + 0.02, Y1 - 0.02, z + 0.02), 'book#D9473B')

    # Bookshelf against the left wall.
    bx0, bx1 = X0, X0 + 0.45
    box('shelf_back', (bx0, 1.0, 0), (bx0 + 0.04, 2.56, 1.6), 'dark_wood')
    for y in (1.0, 2.5):
        box('shelf_side', (bx0, y, 0), (bx1, y + 0.06, 1.6), 'dark_wood')
    for z in (0.0, 0.52, 1.04, 1.55):
        box('shelf', (bx0, 1.06, z), (bx1, 2.5, z + 0.05), 'dark_wood')
    import random
    rnd = random.Random(11)
    colours = [k for k in MATS if k.startswith('book')]
    for z in (0.05, 0.57, 1.09):
        y = 1.1
        while y < 2.3:
            w, h = rnd.uniform(0.07, 0.13), rnd.uniform(0.3, 0.44)
            box('book', (bx0 + 0.06, y, z), (bx1 - 0.05, y + w, z + h), rnd.choice(colours))
            y += w + (0.08 if rnd.random() < 0.15 else 0.01)

    # Dresser with a radio and a little plant.
    box('dresser', (X0, -1.2, 0), (X0 + 0.45, 0.2, 0.85), 'dark_wood', {'+x': 'drawers'}, full=('+x',))
    box('radio', (X0 + 0.08, -0.85, 0.85), (X0 + 0.36, -0.35, 1.1), 'radio')
    box('radio_grill', (X0 + 0.36, -0.78, 0.9), (X0 + 0.37, -0.52, 1.05), 'grill')
    prim('cylinder', 'pot', vertices=8, radius=0.09, depth=0.14, location=(X0 + 0.22, -0.05, 0.92))
    prim('ico_sphere', 'leaf', subdivisions=1, radius=0.13, location=(X0 + 0.22, -0.05, 1.07))

    # Seed crate and watering can by the front-left corner.
    box('crate', (-3.55, -2.55, 0), (-2.95, -1.95, 0.45), 'crate', full=('+z', '-y', '+x', '-x', '+y'))
    for i, (x, y) in enumerate([(-3.45, -2.4), (-3.25, -2.35), (-3.12, -2.15)]):
        box('seed_bag', (x, y, 0.45), (x + 0.16, y + 0.1, 0.65), 'seed_bag', {'-y': 'seed_bag'}, full=('-y',))
    prim('cylinder', 'teal', vertices=10, radius=0.14, depth=0.26, location=(-2.6, -2.4, 0.13))
    spout = prim('cylinder', 'teal', vertices=6, radius=0.03, depth=0.3, location=(-2.37, -2.4, 0.24))
    spout.rotation_euler = (0, math.radians(55), 0)
    box('can_handle', (-2.72, -2.43, 0.26), (-2.52, -2.37, 0.36), 'teal')

    # Big potted plant in the back-left corner.
    prim('cylinder', 'pot', vertices=8, radius=0.22, depth=0.36, location=(-2.7, 2.35, 0.18))
    for (dx, dy, dz, r, m) in [(0, 0, 0.62, 0.3, 'leaf'), (-0.14, 0.06, 0.5, 0.22, 'leaf_dk'),
                               (0.15, -0.05, 0.52, 0.22, 'leaf_dk'), (0.02, 0.0, 0.86, 0.2, 'leaf')]:
        prim('ico_sphere', m, subdivisions=1, radius=r, location=(-2.7 + dx, 2.35 + dy, dz))

    # Braided rug in the middle of the room.
    box('rug', (-1.6, -2.0, 0), (1.3, 0.05, 0.02), 'rug', {'+z': 'rug'}, full=('+z',))


def build_camera_and_lights():
    sc = bpy.context.scene
    cam_data = bpy.data.cameras.new('cam')
    cam_data.lens = 32
    cam_data.sensor_fit = 'HORIZONTAL'
    cam = link(bpy.data.objects.new('camera', cam_data))
    cam.location = (0.0, -7.6, 8.0)
    target = Vector((0.0, 0.15, -0.2))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam

    area = bpy.data.lights.new('ceiling', 'AREA')
    area.shape = 'RECTANGLE'
    area.size, area.size_y = 6.5, 4.5
    area.energy = 380
    area.color = (1.0, 0.96, 0.88)
    link(bpy.data.objects.new('ceiling', area)).location = (0, 0, 4.4)

    sun = bpy.data.lights.new('fill', 'SUN')
    sun.energy = 0.9
    sun.angle = math.radians(20)
    fill = link(bpy.data.objects.new('fill', sun))
    fill.rotation_euler = (math.radians(42), 0, math.radians(-18))

    # Warm ambient light, but a black void behind the cut-away room like the DS.
    world = bpy.data.worlds.new('world')
    try:
        world.use_nodes = True
    except AttributeError:
        pass
    sc.world = world
    nt = world.node_tree
    bg = nt.nodes['Background']
    bg.inputs['Color'].default_value = lin('#FFF1DC')
    bg.inputs['Strength'].default_value = 0.35
    black = nt.nodes.new('ShaderNodeBackground')
    black.inputs['Color'].default_value = (0, 0, 0, 1)
    path = nt.nodes.new('ShaderNodeLightPath')
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(path.outputs['Is Camera Ray'], mix.inputs['Fac'])
    nt.links.new(bg.outputs['Background'], mix.inputs[1])
    nt.links.new(black.outputs['Background'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], nt.nodes['World Output'].inputs['Surface'])
    return cam


def render(path, samples=96):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    sc.cycles.filter_width = 0.01          # no anti-aliasing: hard DS-style edges
    sc.cycles.max_bounces = 4
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def place_player(cam, render_path):
    """Composite the overworld sprite at 1:1 pixels where his feet land."""
    sc = bpy.context.scene
    u, v, _ = world_to_camera_view(sc, cam, Vector((*PLAYER_AT, 0.0)))
    fx, fy = round(u * RES[0]), round((1 - v) * RES[1])
    frame = Image.open(render_path).convert('RGBA')
    sprite = overworld.frames()['down']
    frame.alpha_composite(sprite, (fx - 16, fy - 30))
    return frame.convert('RGB')


def main():
    os.makedirs(OUT, exist_ok=True)
    TEX.update(textures.write_all(os.path.join(OUT, 'textures')))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    build_materials()
    build_room()
    build_furniture()
    room = [o for o in bpy.context.scene.objects if o.type == 'MESH']

    shadow = prim('cylinder', 'shadow', vertices=12, radius=0.24, depth=0.01, location=(*PLAYER_AT, 0.025))
    shadow.scale = (1.0, 0.75, 1.0)
    cam = build_camera_and_lights()

    raw = os.path.join(OUT, 'bedroom_raw_256x192.png')
    render(raw, samples=int(os.environ.get('SAMPLES', 160)))
    frame = place_player(cam, raw)
    os.remove(raw)
    frame.save(os.path.join(OUT, 'bedroom_256x192.png'))
    frame.resize((RES[0] * 4, RES[1] * 4), Image.NEAREST).save(os.path.join(OUT, 'bedroom_4x.png'))

    bpy.ops.object.select_all(action='DESELECT')
    for o in room:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'bedroom.glb'), export_format='GLB', use_selection=True)
    bpy.ops.file.pack_all()
    blend = os.path.join(OUT, 'bedroom.blend')
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    if os.path.exists(blend + '1'):
        os.remove(blend + '1')    # Blender's backup of the previous save


if __name__ == '__main__':
    main()
