extends Area2D
## A checkpoint flag. Touching it sets where the player respawns after a fall.
## The node's origin is the bottom-centre of the flag.

var _active: bool = false

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	_sprite.play("off")


func _on_body_entered(body: Node2D) -> void:
	if _active or not body.is_in_group("player"):
		return
	_active = true
	SFX.play_at(SFX.SELECT, global_position)
	_sprite.play("on")
	var pop := create_tween()
	pop.tween_property(_sprite, "scale", Vector2(1.25, 1.25), 0.1)
	pop.tween_property(_sprite, "scale", Vector2.ONE, 0.15)

	# The level is the scene that owns this flag. Respawn with the feet on the ground.
	var level := owner
	if level != null and level.has_method("set_checkpoint"):
		level.set_checkpoint(global_position + Vector2(0.0, -32.0))
