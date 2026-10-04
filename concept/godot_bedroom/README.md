# Farmhouse bedroom: Godot demo

A Godot 4.5 project that loads the Blender-built bedroom and lets the boy walk around it.

1. In the Godot Project Manager choose **Import** and pick this folder's `project.godot`.
2. Press **F5**. The arrow keys walk.

It renders at the DS's 256×192 and scales up 4× to a 1024×768 window. Furniture blocking
is a list of rectangles in `player.gd`, not physics.

- The room is `assets/bedroom.glb`, copied from `../farmhouse_bedroom/out/`.
- The player strip is `assets/player_overworld_32x32.png`, copied from `../player_boy/out/`.

If you rebuild either of those, copy them over the ones in `assets/`. The platformer
project doesn't see any of this because `concept/.gdignore` hides the whole folder.
