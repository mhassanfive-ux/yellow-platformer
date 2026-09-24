extends StaticBody2D
## A platform that starts invisible and solid-less until a Switch elsewhere calls
## reveal() on it, at which point it pops into existence.

@onready var _shape: CollisionShape2D = $CollisionShape2D


func _ready() -> void:
	visible = false
	_shape.disabled = true


## Idempotent: safe to call more than once (e.g. if a level is ever restarted mid-reveal).
func activate() -> void:
	if visible:
		return
	visible = true
	scale = Vector2(0.3, 0.3)
	modulate.a = 0.0
	var tween := create_tween().set_parallel()
	tween.tween_property(self, "scale", Vector2.ONE, 0.3).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tween.tween_property(self, "modulate:a", 1.0, 0.25)
	# The collision shape stays off for the whole pop-in, so nothing can stand on the
	# platform mid-animation before it looks solid.
	tween.chain().tween_callback(func() -> void: _shape.disabled = false)
