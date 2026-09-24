extends Node2D
## Purely decorative: wanders back and forth within a range of its spawn point. No
## collision, no damage — ambience for the underwater level.

@export var range_x: float = 160.0
@export var speed: float = 40.0
@export var bob_height: float = 10.0
@export var bob_speed: float = 1.6

var _origin: Vector2
var _direction: int = 1
var _time: float = 0.0

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
	_origin = position
	_time = randf() * TAU
	_sprite.flip_h = _direction < 0
	_sprite.play("swim")


func _process(delta: float) -> void:
	_time += delta
	position.x += _direction * speed * delta
	if absf(position.x - _origin.x) > range_x:
		_direction *= -1
		_sprite.flip_h = _direction < 0
	position.y = _origin.y + sin(_time * bob_speed) * bob_height
