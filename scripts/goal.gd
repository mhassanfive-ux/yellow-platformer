extends Area2D
## The flag at the end of a level. Touching it finishes the level.
## The node's origin is the bottom-centre of the flag.

## The level to load next. Leave empty for a plain "Level Complete!" and restart.
@export_file("*.tscn") var next_level: String = ""

var _used: bool = false

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	_sprite.play("wave")


func _on_body_entered(body: Node2D) -> void:
	if _used or not body.is_in_group("player"):
		return
	_used = true
	SFX.play_at(SFX.MAGIC, global_position)
	var pop := create_tween()
	pop.tween_property(_sprite, "scale", Vector2(1.3, 1.3), 0.12)
	pop.tween_property(_sprite, "scale", Vector2.ONE, 0.18)
	var level := owner
	if level != null and level.has_method("complete_level"):
		level.complete_level(next_level)
