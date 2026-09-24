extends CharacterBody2D

@export var speed: float = 60.0
@export var start_direction: int = -1

var _direction: int
var _dead: bool = false
var _gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var _shape: CollisionShape2D = $CollisionShape2D
@onready var _hitbox: Area2D = $Hitbox
@onready var _ledge_check: RayCast2D = $LedgeCheck


func _ready() -> void:
	_direction = start_direction
	add_to_group("enemies")
	_sprite.play("walk")


func _physics_process(delta: float) -> void:
	if _dead:
		return

	if not is_on_floor():
		velocity.y += _gravity * delta
	else:
		# Turn around at ledges instead of walking into a gap.
		_ledge_check.position.x = absf(_ledge_check.position.x) * _direction
		_ledge_check.force_raycast_update()
		if not _ledge_check.is_colliding():
			_direction *= -1
	velocity.x = _direction * speed
	move_and_slide()

	# Turn around when blocked by a wall or tile.
	if is_on_wall():
		_direction *= -1
	_sprite.flip_h = _direction > 0

	# Hurt any player touching us (the player ignores hits while invulnerable).
	for body in _hitbox.get_overlapping_bodies():
		if body.has_method("take_damage"):
			body.take_damage(global_position)


func die() -> void:
	if _dead:
		return
	_dead = true
	SFX.play_at(SFX.DISAPPEAR, global_position)
	velocity = Vector2.ZERO
	_shape.set_deferred("disabled", true)
	_sprite.play("flat")
	get_tree().create_timer(0.4).timeout.connect(queue_free)
