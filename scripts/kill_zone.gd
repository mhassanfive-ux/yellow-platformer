extends Area2D

## Path to the marker where the player is put back after falling into this zone.
@export var spawn_point_path: NodePath = ^"../PlayerSpawn"


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node2D) -> void:
	if body.has_method("fall_respawn"):
		var level := get_parent()
		if level != null and "respawn_position" in level and level.respawn_position != Vector2.ZERO:
			# The start, or the last checkpoint the player touched.
			body.fall_respawn(level.respawn_position)
			return
		var spawn := get_node_or_null(spawn_point_path) as Node2D
		if spawn == null:
			push_error("KillZone: no spawn point found at %s" % spawn_point_path)
			return
		body.fall_respawn(spawn.global_position)
	elif body.is_in_group("enemies"):
		body.queue_free()
