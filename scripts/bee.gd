extends CharacterBody2D
## A flying enemy. It hovers above its platform until the player comes near, then
## spirals out into a circle and orbits the platform area, hurting anything it touches.
## The node's starting position is both the hover spot and the centre of the circle.

@export var orbit_radius: float = 150.0
## Angular speed in radians per second.
@export var orbit_speed: float = 2.0
## The bee attacks when the player is closer than this to the centre of its circle.
@export var alert_radius: float = 340.0
@export var clockwise: bool = true
## Seconds to spiral out to (or back in from) the full circle.
@export var spiral_time: float = 0.8
## Seconds the player must stay out of range before the bee calms down.
@export var calm_delay: float = 1.0

var _center: Vector2
var _angle: float = -PI / 2.0
var _radius: float = 0.0
var _spin: float = 0.0
var _hover_time: float = 0.0
var _calm_timer: float = 0.0
var _alert: bool = false
var _dead: bool = false

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var _hitbox: Area2D = $Hitbox
@onready var _body_shape: CollisionShape2D = $CollisionShape2D


func _ready() -> void:
	_center = global_position
	_hover_time = randf() * TAU
	add_to_group("enemies")
	_sprite.play("fly")


func _physics_process(delta: float) -> void:
	if _dead:
		return

	_update_alert(delta)

	# Spiral out to the full circle while alert, and back in to the hover spot when calm.
	var target_radius := orbit_radius if _alert else 0.0
	_radius = move_toward(_radius, target_radius, orbit_radius / spiral_time * delta)
	var target_spin := 0.0
	if _alert:
		target_spin = orbit_speed if clockwise else -orbit_speed
	_spin = move_toward(_spin, target_spin, orbit_speed * 2.0 * delta)
	_angle += _spin * delta

	# A gentle bob that fades out as the bee starts to orbit.
	_hover_time += delta
	var calm := 1.0 - _radius / orbit_radius
	var bob := Vector2(sin(_hover_time * 1.7) * 8.0, sin(_hover_time * 2.3) * 6.0) * calm

	var new_position := _center + Vector2.from_angle(_angle) * _radius + bob
	var dx := new_position.x - global_position.x
	global_position = new_position
	if absf(dx) > 0.2:
		_sprite.flip_h = dx < 0.0  # the art faces right
	_sprite.speed_scale = 1.0 + 0.8 * (1.0 - calm)

	# Sting anything hurtable that we overlap (the player ignores hits while invulnerable).
	for body in _hitbox.get_overlapping_bodies():
		if body.has_method("take_damage"):
			body.take_damage(global_position)


func _update_alert(delta: float) -> void:
	var player := get_tree().get_first_node_in_group("player")
	var near: bool = player != null and player.global_position.distance_to(_center) <= alert_radius
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
	_body_shape.set_deferred("disabled", true)
	var tween := create_tween().set_parallel()
	tween.tween_property(self, "position:y", position.y + 220.0, 0.6).set_ease(Tween.EASE_IN)
	tween.tween_property(_sprite, "modulate:a", 0.0, 0.6)
	tween.chain().tween_callback(queue_free)
