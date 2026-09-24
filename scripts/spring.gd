extends Area2D
## A bounce pad. Anything standing on it (player or rival) is launched upward.
## The node's origin is the bottom-centre of the pad.

const COMPRESSED: Texture2D = preload("res://assets/Sprites/Tiles/Default/spring.png")
const EXTENDED: Texture2D = preload("res://assets/Sprites/Tiles/Default/spring_out.png")

## Upward launch speed. About 800 lifts a character roughly 320px.
@export var bounce_velocity: float = -800.0

var _cooldown: float = 0.0

@onready var _sprite: Sprite2D = $Sprite2D


func _ready() -> void:
	add_to_group("springs")


func _physics_process(delta: float) -> void:
	_cooldown = maxf(_cooldown - delta, 0.0)
	if _cooldown > 0.0:
		return
	# Checked every frame rather than on entry, so a character that lands on the pad
	# while not yet willing to bounce (the rival) still gets launched once it is.
	for body in get_overlapping_bodies():
		if not body.has_method("bounce"):
			continue
		if body.has_method("accepts_bounce") and not body.accepts_bounce():
			continue
		if body.velocity.y < -200.0:
			continue  # already on the way up
		_cooldown = 0.3
		SFX.play_at(SFX.JUMP_HIGH, global_position)
		body.bounce(bounce_velocity)
		_sprite.texture = EXTENDED
		get_tree().create_timer(0.3).timeout.connect(func() -> void: _sprite.texture = COMPRESSED)
		break
