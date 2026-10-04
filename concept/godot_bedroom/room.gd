extends Node3D
## The imported bedroom model. Walls, floor and trim don't cast shadows, so the
## key light can come in from the top-left without the left and back walls
## darkening half the floor; the furniture still casts.

const NO_SHADOW_PREFIXES: Array[String] = ["wall_", "floor_", "rail_", "base_", "stairwell_"]


func _ready() -> void:
	for node in find_children("*", "MeshInstance3D", true, false):
		var mesh := node as MeshInstance3D
		for prefix in NO_SHADOW_PREFIXES:
			if mesh.name.begins_with(prefix):
				mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				break
