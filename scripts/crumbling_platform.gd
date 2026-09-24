extends StaticBody2D
## A platform that stays solid for a moment after you land on it, then fades out and lets
## you fall through -- and resets itself after a further delay, so a death-and-retry
## within the same level instance never permanently loses the crossing.
## The node's origin is the centre of the first tile; `tiles` sets the width.

const TEXTURE: Texture2D = preload("res://assets/Sprites/Tiles/Default/block_empty_warning.png")
const TILE_SIZE: float = 64.0

@export var tiles: int = 1
## Seconds standing on the platform before it crumbles away.
@export var crumble_delay: float = 0.5
## Seconds after crumbling before it solidifies again.
@export var respawn_delay: float = 2.5

var _triggered: bool = false
var _shape: CollisionShape2D


func _ready() -> void:
	for i in tiles:
		var sprite := Sprite2D.new()
		sprite.texture = TEXTURE
		sprite.position = Vector2(i * TILE_SIZE, 0.0)
		add_child(sprite)

	var rect := RectangleShape2D.new()
	rect.size = Vector2(tiles * TILE_SIZE, TILE_SIZE)

	_shape = CollisionShape2D.new()
	_shape.shape = rect
	_shape.position = Vector2((tiles - 1) * TILE_SIZE / 2.0, 0.0)
	add_child(_shape)

	# A separate detection area, rather than reacting to the StaticBody2D's own contacts,
	# since a StaticBody2D has no entered/exited signals of its own.
	var area := Area2D.new()
	area.collision_layer = 0
	area.collision_mask = 2  # player only -- this level has no rival to crumble under
	var area_shape := CollisionShape2D.new()
	area_shape.shape = rect
	area_shape.position = _shape.position
	area.add_child(area_shape)
	add_child(area)
	area.body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node2D) -> void:
	if _triggered or not body.is_in_group("player"):
		return
	_triggered = true
	await get_tree().create_timer(crumble_delay).timeout
	var tween := create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 0.15)
	await tween.finished
	_shape.disabled = true

	await get_tree().create_timer(respawn_delay).timeout
	modulate.a = 1.0
	_shape.disabled = false
	_triggered = false
