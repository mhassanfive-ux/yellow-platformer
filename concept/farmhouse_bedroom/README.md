# Farmhouse bedroom (DS-style 3D demo)

The boy's upstairs bedroom, built in Blender from a script and rendered the way the
DS draws its 3D rooms: low-poly boxes, tiny pixel textures sampled without smoothing,
a tilted perspective camera, 256×192 output, and the player composited as a 1:1 pixel
sprite.

```
pip install bpy==5.0.1 pillow numpy   # bpy 5.0 needs Python 3.11
python3 build_room.py                 # SAMPLES=24 for a quick preview
```

| File | What it is |
| --- | --- |
| `out/bedroom_4x.png` | The render, scaled 4× for viewing |
| `out/bedroom_256x192.png` | Native DS resolution |
| `out/bedroom.glb` | The room as a glTF model for Godot (nearest-filtered textures) |
| `out/bedroom.blend` | Blender scene with camera and lights, textures packed in |
| `out/textures/` | The pixel textures on their own |

- `textures.py` draws the textures.
- `build_room.py` builds the room, the furniture, the camera and the lights, then renders and exports.

The player sprite comes from `../player_boy/overworld.py`.
