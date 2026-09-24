extends StaticBody2D
## A green box hung by a chain, blocking the passage below/beside it until a Switch
## elsewhere calls activate() on it -- the mirror image of HiddenPlatform: this one starts
## solid and visible, and activate() removes it instead of revealing it.
## The node's origin is the top-centre of the top chain link; the chain (chain_tiles
## links) stacks downward, with the box as the final tile.

const CHAIN_TEX: Texture2D = preload("res://assets/Sprites/Tiles/Default/chain.png")
const BOX_TEX: Texture2D = preload("res://assets/Sprites/Tiles/Default/block_green.png")
const TILE_SIZE: float = 64.0

@export var chain_tiles: int = 3

var _shape: CollisionShape2D
var _activated: bool = false


func _ready() -> void:
	for i in chain_tiles:
		var link := Sprite2D.new()
		link.texture = CHAIN_TEX
		link.position = Vector2(0.0, i * TILE_SIZE + TILE_SIZE / 2.0)
		add_child(link)

	var box := Sprite2D.new()
	box.texture = BOX_TEX
	box.position = Vector2(0.0, chain_tiles * TILE_SIZE + TILE_SIZE / 2.0)
	add_child(box)

	var total_height: float = (chain_tiles + 1) * TILE_SIZE
	var rect := RectangleShape2D.new()
	rect.size = Vector2(TILE_SIZE, total_height)
	_shape = CollisionShape2D.new()
	_shape.shape = rect
	_shape.position = Vector2(0.0, total_height / 2.0)
	add_child(_shape)


## Idempotent: safe to call more than once. Retracts the whole assembly straight up and
## out of the passage (like the chain reeling in), fading it out along the way, and drops
## its collision immediately so the passage is clear as soon as the switch is pressed
## rather than only once the animation finishes.
func activate() -> void:
	if _activated:
		return
	_activated = true
	SFX.play_at(SFX.DISAPPEAR, global_position)
	# activate() runs from inside the switch's body_entered, which fires during physics
	# query flushing -- toggling collision synchronously there is refused by the physics
	# server, hence the deferred call rather than a direct assignment.
	_shape.set_deferred("disabled", true)
	var retract_distance: float = (chain_tiles + 1) * TILE_SIZE + 64.0
	var tween := create_tween().set_parallel()
	tween.tween_property(self, "position:y", position.y - retract_distance, 0.5) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	tween.tween_property(self, "modulate:a", 0.0, 0.5)
