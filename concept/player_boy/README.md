# Player concept: boy (v0.1)

First-pass concept for the player in an idle city-builder with cozy farming, in a
Gen 5 (Pokémon Black/White)-inspired 2.5D pixel style. Everything is drawn in code,
so tweak a shape or colour and rebuild:

```
pip install pillow numpy
python3 make_sheet.py
```

| File | What it is |
| --- | --- |
| `out/player_concept_sheet.png` | The full concept sheet |
| `out/player_key_art_64x104.png` / `_8x.png` | Full-body key-art sprite |
| `out/player_overworld_32x32.png` | Down, left, up and right overworld frames |
| `out/player_turnaround.gif` | The four facings, cycling |
| `out/mockup_scene_4x.png` | The in-world mockup on its own |

- `palette.py`: colour ramps for each material
- `portrait.py`: key-art sprite built from shapes
- `overworld.py`: hand-typed 32×32 frames
- `scene.py`: the mockup scene and its pixel font
- `pixel.py`: the small drawing toolkit they share

`concept/.gdignore` stops Godot from importing any of this into the platformer project.
