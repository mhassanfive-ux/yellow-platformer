extends CharacterBody2D
## A snail that patrols like the other ground enemies. Stomped from above, it retracts into
## its shell (harmless from then on); touched from the side while shelled, it goes sliding
## and kills any other enemy it hits — a tool for the player, never a hazard to them, the
## same rule the fireball follows. Stomped again while already a shell, it's destroyed
## outright. A shell left alone long enough wakes back up into a walking snail.

enum State { WALKING, SHELL, SLIDING }

@export var speed: float = 50.0
@export var start_direction: int = -1
@export var shell_speed: float = 340.0
## Seconds a stationary shell waits before waking back up into a walking snail.
@export var shell_recovery_time: float = 6.0
## Seconds a sliding shell keeps going before settling back into a stationary shell.
@export var slide_time: float = 3.5
## The little hop the stomper gets, mirroring the bounce a spring gives.
@export var stomp_bounce: float = -280.0

var _state: State = State.WALKING
var _direction: int
var _timer: float = 0.0
## Brief grace period after entering the shell state, so the same contact that caused the
## stomp/settle can't also immediately register as a kick.
var _kick_cooldown: float = 0.0
var _dead: bool = false
var _gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var _shape: CollisionShape2D = $CollisionShape2D
@onready var _hitbox: Area2D = $Hitbox
@onready var _stomp_zone: Area2D = $StompZone
@onready var _ledge_check: RayCast2D = $LedgeCheck


func _ready() -> void:
	_direction = start_direction
	add_to_group("enemies")
	_sprite.play("walk")


func _physics_process(delta: float) -> void:
	if _dead:
		return

	_kick_cooldown = maxf(_kick_cooldown - delta, 0.0)
	if not is_on_floor():
		velocity.y += _gravity * delta

	if _state != State.WALKING:
		_timer -= delta
		if _timer <= 0.0:
			if _state == State.SHELL:
				_wake_up()
			else:
				_settle()

	match _state:
		State.WALKING:
			_process_walking()
		State.SHELL:
			_process_shell(delta)
		State.SLIDING:
			_process_sliding(delta)

	move_and_slide()
	_check_stomp()

	# _check_stomp() may just have changed our state; act on the current one, not a stale one.
	match _state:
		State.WALKING:
			_check_side_damage()
		State.SHELL:
			_check_shell_kick()
		State.SLIDING:
			_check_sliding_hits()


static func _is_actor(body: Node) -> bool:
	return body.is_in_group("player") or body.is_in_group("rival")


func _process_walking() -> void:
	if is_on_floor():
		_ledge_check.position.x = absf(_ledge_check.position.x) * _direction
		_ledge_check.force_raycast_update()
		if not _ledge_check.is_colliding():
			_direction *= -1
	if is_on_wall():
		_direction *= -1
	velocity.x = _direction * speed
	_sprite.flip_h = _direction > 0


func _process_shell(_delta: float) -> void:
	velocity.x = 0.0


func _process_sliding(_delta: float) -> void:
	if is_on_floor():
		_ledge_check.position.x = absf(_ledge_check.position.x) * _direction
		_ledge_check.force_raycast_update()
		if not _ledge_check.is_colliding():
			_direction *= -1
	if is_on_wall():
		_direction *= -1
	velocity.x = _direction * shell_speed


func _check_stomp() -> void:
	for body in _stomp_zone.get_overlapping_bodies():
		if _is_actor(body) and body.velocity.y > 0.0:
			if _state == State.WALKING:
				_retract(body)
			elif _state == State.SHELL:
				die()
			return


func _check_side_damage() -> void:
	for body in _hitbox.get_overlapping_bodies():
		if body.has_method("take_damage"):
			body.take_damage(global_position)


func _check_shell_kick() -> void:
	if _kick_cooldown > 0.0:
		return
	for body in _hitbox.get_overlapping_bodies():
		if _is_actor(body):
			_kick(body.global_position)
			return


func _check_sliding_hits() -> void:
	for body in _hitbox.get_overlapping_bodies():
		if body != self and body.has_method("die"):
			body.die()


func _retract(stomper: Node2D) -> void:
	_state = State.SHELL
	_timer = shell_recovery_time
	_kick_cooldown = 0.35
	velocity = Vector2.ZERO
	_sprite.play("shell")
	SFX.play_at(SFX.BUMP, global_position)
	if stomper.has_method("bounce"):
		stomper.bounce(stomp_bounce)


func _kick(from_position: Vector2) -> void:
	var dir := signf(global_position.x - from_position.x)
	_direction = 1 if dir >= 0.0 else -1
	_state = State.SLIDING
	_timer = slide_time
	SFX.play_at(SFX.THROW, global_position)


func _settle() -> void:
	_state = State.SHELL
	_timer = shell_recovery_time
	_kick_cooldown = 0.35
	velocity.x = 0.0
	SFX.play_at(SFX.BUMP, global_position)


func _wake_up() -> void:
	_state = State.WALKING
	_sprite.play("walk")


## Called by the player's fireballs, or by another snail's shell sliding into this one.
func die() -> void:
	if _dead:
		return
	_dead = true
	SFX.play_at(SFX.DISAPPEAR, global_position)
	velocity = Vector2.ZERO
	_shape.set_deferred("disabled", true)
	_stomp_zone.set_deferred("monitoring", false)
	_hitbox.set_deferred("monitoring", false)
	var tween := create_tween()
	tween.tween_property(_sprite, "modulate:a", 0.0, 0.3)
	tween.tween_callback(queue_free)
