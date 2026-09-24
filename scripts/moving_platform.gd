extends AnimatableBody2D
## A platform that rides back and forth between two points, carrying anything standing on
## it. AnimatableBody2D + sync_to_physics is what lets a CharacterBody2D rider's
## move_and_slide() pick up the platform's motion each frame instead of sliding off it.
## The node's origin is the centre of the first tile; `tiles` sets the width.

const TEXTURE: Texture2D = preload("res://assets/Sprites/Tiles/Default/block_planks.png")
const TILE_SIZE: float = 64.0

@export var tiles: int = 2
## Where the platform travels to, relative to its starting (scene) position.
@export var travel_offset: Vector2 = Vector2(256.0, 0.0)
@export var speed: float = 80.0

var _start: Vector2
var _end: Vector2
var _going_forward: bool = true


func _ready() -> void:
	sync_to_physics = true
	_start = global_position
	_end = global_position + travel_offset

	for i in tiles:
		var sprite := Sprite2D.new()
		sprite.texture = TEXTURE
		sprite.position = Vector2(i * TILE_SIZE, 0.0)
		add_child(sprite)

	var shape := RectangleShape2D.new()
	shape.size = Vector2(tiles * TILE_SIZE, TILE_SIZE)
	var collision := CollisionShape2D.new()
	collision.shape = shape
	collision.position = Vector2((tiles - 1) * TILE_SIZE / 2.0, 0.0)
	add_child(collision)


func _physics_process(delta: float) -> void:
	var target: Vector2 = _end if _going_forward else _start
	var to_target: Vector2 = target - global_position
	var dist: float = to_target.length()
	var step: float = speed * delta
	if step >= dist:
		global_position = target
		_going_forward = not _going_forward
	else:
		global_position += to_target.normalized() * step
