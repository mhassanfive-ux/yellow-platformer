extends Area2D
## A row of spikes on the ground. Hurts the player on contact and knocks them back.
## The node's origin is the bottom-centre of the first tile; `tiles` sets the width.

const TEXTURE: Texture2D = preload("res://assets/Sprites/Tiles/Default/spikes.png")
const TILE_SIZE: float = 64.0

## Hearts of damage per touch.
@export var damage: float = 1.0
## Width in tiles. Keep patches at 1 tile: a full jump only clears about 150px of
## danger plus body width, so wider patches leave almost no margin for error.
@export var tiles: int = 1


func _ready() -> void:
	for i in tiles:
		var sprite := Sprite2D.new()
		sprite.texture = TEXTURE
		sprite.position = Vector2(i * TILE_SIZE, -TILE_SIZE / 2.0)
		add_child(sprite)

	# Only the pointy lower part of the tile is dangerous.
	var shape := RectangleShape2D.new()
	shape.size = Vector2(tiles * TILE_SIZE - 12.0, 26.0)
	var collision := CollisionShape2D.new()
	collision.shape = shape
	collision.position = Vector2((tiles - 1) * TILE_SIZE / 2.0, -13.0)
	add_child(collision)


func _physics_process(_delta: float) -> void:
	for body in get_overlapping_bodies():
		if body.has_method("take_damage"):
			# Knock the player up and away from the middle of the patch, so they are thrown
			# clear of it rather than back into it.
			var centre_x := global_position.x + (tiles - 1) * TILE_SIZE / 2.0
			body.take_damage(Vector2(centre_x, body.global_position.y + 40.0), damage)
