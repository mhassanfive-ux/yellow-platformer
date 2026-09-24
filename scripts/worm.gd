extends CharacterBody2D
## Floats harmlessly in place until the player comes near, then chases them directly
## through the open water. Hurts on contact; killed by fireballs.

@export var alert_radius: float = 220.0
## Seconds the player must stay out of range before the worm gives up and drifts home.
@export var calm_delay: float = 1.5
@export var chase_speed: float = 110.0
@export var chase_acceleration: float = 500.0
@export var return_speed: float = 60.0
@export var bob_height: float = 8.0
@export var bob_speed: float = 1.4

var _spawn: Vector2
var _alert: bool = false
var _calm_timer: float = 0.0
var _dead: bool = false
var _time: float = 0.0

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var _hitbox: Area2D = $Hitbox


func _ready() -> void:
	_spawn = global_position
	_time = randf() * TAU
	add_to_group("enemies")
	_sprite.play("idle")


func _physics_process(delta: float) -> void:
	if _dead:
		return

	_time += delta
	_update_alert(delta)

	if _alert:
		var player := get_tree().get_first_node_in_group("player")
		if player:
			var to_player: Vector2 = player.global_position - global_position
			if to_player.length() > 4.0:
				velocity = velocity.move_toward(to_player.normalized() * chase_speed, chase_acceleration * delta)
		_sprite.play("chase")
		if velocity.x != 0.0:
			_sprite.flip_h = velocity.x < 0.0
	else:
		var home: Vector2 = _spawn + Vector2(0.0, sin(_time * bob_speed) * bob_height)
		var to_home: Vector2 = home - global_position
		velocity = to_home.limit_length(return_speed)
		_sprite.play("idle")

	move_and_slide()

	# Sting anything hurtable we overlap (the player ignores hits while invulnerable).
	for body in _hitbox.get_overlapping_bodies():
		if body.has_method("take_damage"):
			body.take_damage(global_position)


func _update_alert(delta: float) -> void:
	var player := get_tree().get_first_node_in_group("player")
	var near: bool = player != null and player.global_position.distance_to(global_position) <= alert_radius
	if near:
		_alert = true
		_calm_timer = calm_delay
	elif _alert:
		_calm_timer -= delta
		if _calm_timer <= 0.0:
			_alert = false


## Called by the player's fireballs.
func die() -> void:
	if _dead:
		return
	_dead = true
	SFX.play_at(SFX.DISAPPEAR, global_position)
	_hitbox.set_deferred("monitoring", false)
	$CollisionShape2D.set_deferred("disabled", true)
	var tween := create_tween().set_parallel()
	tween.tween_property(self, "scale", Vector2.ZERO, 0.35).set_ease(Tween.EASE_IN)
	tween.tween_property(_sprite, "modulate:a", 0.0, 0.35)
	tween.chain().tween_callback(queue_free)
