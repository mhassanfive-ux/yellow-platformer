extends Area2D
## A key the player can pick up. Only the player can take it, not the rival.

signal collected(collector: Node)

@onready var _sprite: Sprite2D = $Sprite2D

var _taken: bool = false


func _ready() -> void:
	add_to_group("keys")
	body_entered.connect(_on_body_entered)

	# Gentle bobbing so the key reads as a collectible.
	var tween := create_tween().set_loops()
	tween.tween_property(_sprite, "position:y", -6.0, 0.7).set_trans(Tween.TRANS_SINE)
	tween.tween_property(_sprite, "position:y", 6.0, 0.7).set_trans(Tween.TRANS_SINE)


func _on_body_entered(body: Node2D) -> void:
	if _taken or not body.is_in_group("player"):
		return
	_taken = true
	SFX.play_at(SFX.GEM, global_position)
	collected.emit(body)
	queue_free()
