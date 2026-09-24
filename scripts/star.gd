extends Area2D

## Emitted with whoever picked the star up (the player or the rival).
signal collected(collector: Node)

@onready var _sprite: Sprite2D = $Sprite2D

var _taken: bool = false


func _ready() -> void:
	add_to_group("stars")
	body_entered.connect(_on_body_entered)

	# Gentle bobbing so stars read as collectibles.
	var tween := create_tween().set_loops()
	tween.tween_property(_sprite, "position:y", -5.0, 0.6).set_trans(Tween.TRANS_SINE)
	tween.tween_property(_sprite, "position:y", 5.0, 0.6).set_trans(Tween.TRANS_SINE)


func _on_body_entered(body: Node2D) -> void:
	if _taken or not (body.is_in_group("player") or body.is_in_group("rival")):
		return
	_taken = true
	# Only the player's own pickups play a sound, so the rival racing through several
	# stars in quick succession doesn't turn into a barrage of coin noises.
	if body.is_in_group("player"):
		SFX.play_at(SFX.COIN, global_position, 0.0, 1.0, 0.06)
	collected.emit(body)
	queue_free()
