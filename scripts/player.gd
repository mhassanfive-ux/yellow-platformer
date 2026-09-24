extends CharacterBody2D

## Health is measured in hearts; half hearts are allowed.
signal health_changed(health: float, max_health: float)

@export var speed: float = 220.0
@export var acceleration: float = 1600.0
@export var friction: float = 1800.0
@export var jump_velocity: float = -420.0
@export var jump_cut_multiplier: float = 0.4
@export var coyote_time: float = 0.12
@export var climb_speed: float = 140.0
@export var vault_velocity: float = -320.0
@export var vault_time: float = 0.18
@export var fireball_scene: PackedScene
@export var shoot_cooldown: float = 0.35
@export var max_health: float = 3.0
@export var group_name: StringName = &"player"
@export var contact_damage: float = 0.5
@export var fall_damage: float = 1.0
@export var invulnerable_time: float = 1.0
@export var stun_time: float = 0.25
@export var knockback: Vector2 = Vector2(260.0, -260.0)

## Underwater levels set this true (as a scene override) for floaty, drag-based movement
## instead of walking/gravity/jumping. No air meter: the level is fully submerged throughout.
@export var swimming: bool = false
@export var swim_speed: float = 180.0
@export var swim_acceleration: float = 900.0
@export var swim_drag: float = 700.0
## Gentle downward drift while not actively swimming up or down.
@export var swim_sink_speed: float = 40.0
@export var swim_sink_acceleration: float = 200.0

## Acceleration/friction used on ice patches instead of the normal ground values, so the
## player speeds up and (especially) slows down much more gradually — the classic slide.
## Friction in particular needs to be low enough that letting go of the direction key is
## unmistakably different from normal ground, not just "a bit floatier".
@export var ice_acceleration: float = 320.0
@export var ice_friction: float = 90.0

var health: float
var _coyote_timer: float = 0.0
var _shoot_timer: float = 0.0
var _invulnerable_timer: float = 0.0
var _stun_timer: float = 0.0
var _ladder_cooldown: float = 0.0
var _vault_timer: float = 0.0
var _needs_repress: bool = false
var _jumping: bool = false
var _facing: int = 1
var _ladder: Area2D = null
var _climbing: bool = false
var _gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
	health = max_health
	# Arriving from another level: keep the health we left it with.
	if group_name == &"player" and GameState.carried_health > 0.0:
		health = minf(GameState.carried_health, max_health)
		GameState.carried_health = -1.0
	add_to_group(group_name)
	health_changed.emit(health, max_health)


func _physics_process(delta: float) -> void:
	_invulnerable_timer = maxf(_invulnerable_timer - delta, 0.0)
	_stun_timer = maxf(_stun_timer - delta, 0.0)
	_ladder_cooldown = maxf(_ladder_cooldown - delta, 0.0)
	_shoot_timer = maxf(_shoot_timer - delta, 0.0)

	if swimming:
		_swim_step(delta)
	else:
		if _stun_timer == 0.0 and not _climbing:
			_try_grab_ladder()

		if _climbing:
			_climb_step()
		else:
			_walk_step(delta)

	if _stun_timer == 0.0 and _in_shoot() and _shoot_timer == 0.0:
		_shoot()

	_update_animation()


func _walk_step(delta: float) -> void:
	if is_on_floor():
		_coyote_timer = coyote_time
	else:
		_coyote_timer = maxf(_coyote_timer - delta, 0.0)
		velocity.y += _gravity * delta

	if _stun_timer == 0.0:
		# Jump, allowed while grounded or within the coyote window.
		if _in_jump_pressed() and _coyote_timer > 0.0:
			velocity.y = jump_velocity
			_coyote_timer = 0.0
			_jumping = true
			SFX.play_at(SFX.JUMP, global_position, _sfx_db(), 1.0, 0.08)

		# Variable jump height: releasing early cuts the upward velocity. Only real
		# jumps are cut, not ladder vaults or knockback.
		if _in_jump_released() and _jumping and velocity.y < 0.0:
			velocity.y *= jump_cut_multiplier
			_jumping = false
		if velocity.y >= 0.0:
			_jumping = false

		var direction := _in_axis_h()
		if direction != 0.0:
			_facing = 1 if direction > 0.0 else -1

		var on_ice: bool = _standing_on_ice()
		var accel: float = ice_acceleration if on_ice else acceleration
		var decel: float = ice_friction if on_ice else friction

		if _vault_timer > 0.0:
			# Climbing out at the top of a ladder: rise straight up first so the
			# player clears the platform edge before moving sideways.
			_vault_timer = maxf(_vault_timer - delta, 0.0)
			velocity.x = 0.0
		elif direction != 0.0:
			velocity.x = move_toward(velocity.x, direction * speed, accel * delta)
		else:
			velocity.x = move_toward(velocity.x, 0.0, decel * delta)

	move_and_slide()


func _swim_step(delta: float) -> void:
	if _stun_timer == 0.0:
		var horizontal := _in_axis_h()
		# Up/down move the player directly; there is no jump arc underwater.
		var vertical := _in_climb_axis()

		if horizontal != 0.0:
			_facing = 1 if horizontal > 0.0 else -1
			velocity.x = move_toward(velocity.x, horizontal * swim_speed, swim_acceleration * delta)
		else:
			velocity.x = move_toward(velocity.x, 0.0, swim_drag * delta)

		if vertical != 0.0:
			velocity.y = move_toward(velocity.y, vertical * swim_speed, swim_acceleration * delta)
		else:
			# A gentle sink when not actively swimming, rather than a hard stop.
			velocity.y = move_toward(velocity.y, swim_sink_speed, swim_sink_acceleration * delta)

	move_and_slide()


func _try_grab_ladder() -> void:
	var wants_up := _in_up()
	var wants_down := _in_down()

	# After letting go, the climb keys must be released and pressed again, so
	# holding Up doesn't yank the player back onto the ladder mid-jump.
	if _needs_repress:
		if not wants_up and not wants_down:
			_needs_repress = false
		return

	if _ladder == null or _ladder_cooldown > 0.0:
		return
	# Up always grabs; Down only grabs when airborne (so standing at the foot of a
	# ladder doesn't flicker).
	if wants_up or (wants_down and not is_on_floor()):
		_climbing = true
		velocity = Vector2.ZERO
		_coyote_timer = 0.0
		global_position.x = _ladder.global_position.x


func _climb_step() -> void:
	if _ladder == null:
		_climbing = false
		return

	var vertical := _in_climb_axis()
	var horizontal := _in_axis_h()

	# Jump off the ladder at any time with Space/Enter (Up is reserved for climbing).
	if _in_accept_pressed():
		if horizontal != 0.0:
			_facing = 1 if horizontal > 0.0 else -1
		_release_ladder()
		velocity = Vector2(horizontal * speed, jump_velocity * 0.75)
		SFX.play_at(SFX.JUMP, global_position, _sfx_db(), 1.0, 0.08)
		return

	# Step off sideways. Near the top, climb out over the platform edge instead of
	# dropping down the side of it.
	if horizontal != 0.0:
		_facing = 1 if horizontal > 0.0 else -1
		var near_top: bool = global_position.y <= _ladder.top_limit_y() + 12.0
		_release_ladder()
		if near_top:
			velocity = Vector2(0.0, vault_velocity)
			_vault_timer = vault_time
		else:
			velocity = Vector2(horizontal * speed, 0.0)
		return

	velocity = Vector2(0.0, vertical * climb_speed)
	move_and_slide()

	# Stop at the top rung.
	var limit: float = _ladder.top_limit_y()
	if global_position.y < limit:
		global_position.y = limit
		velocity.y = 0.0
	# Reaching the ground at the bottom lets go.
	if vertical > 0.0 and is_on_floor():
		_release_ladder()


func _release_ladder() -> void:
	_climbing = false
	_needs_repress = true
	_ladder_cooldown = 0.2


## Whether the floor directly underfoot is tagged "ice" in its TileSet, checked via the
## most recent move_and_slide() collision rather than an overlap area, so the slipperiness
## is a property of the tile itself instead of a separate scene node to keep in sync with it.
func _standing_on_ice() -> bool:
	if not is_on_floor():
		return false
	for i in get_slide_collision_count():
		var collider: Object = get_slide_collision(i).get_collider()
		if collider is TileMapLayer:
			var layer: TileMapLayer = collider
			var probe: Vector2 = get_slide_collision(i).get_position() + Vector2(0.0, 2.0)
			var coords: Vector2i = layer.local_to_map(layer.to_local(probe))
			var data: TileData = layer.get_cell_tile_data(coords)
			# get_custom_data() errors on a TileSet that has no "ice" layer at all
			# (every tileset except the snow one), rather than just returning false.
			if data != null and layer.tile_set.get_custom_data_layer_by_name("ice") != -1 \
					and data.get_custom_data("ice"):
				return true
	return false


func enter_ladder(ladder: Area2D) -> void:
	_ladder = ladder


func exit_ladder(ladder: Area2D) -> void:
	if _ladder == ladder:
		_ladder = null
		_climbing = false


## `amount` defaults to the normal contact damage; hazards can pass their own.
func take_damage(from_position: Vector2, amount: float = -1.0) -> void:
	if _invulnerable_timer > 0.0 or health <= 0.0:
		return

	health = maxf(health - (contact_damage if amount < 0.0 else amount), 0.0)
	health_changed.emit(health, max_health)
	SFX.play_at(SFX.HURT, global_position, _sfx_db())
	if health <= 0.0:
		# Restart the level; the same path a fall-respawn uses.
		GameState.call_deferred("restart_level")
		return

	_climbing = false
	_invulnerable_timer = invulnerable_time
	_stun_timer = stun_time
	var away := signf(global_position.x - from_position.x)
	if away == 0.0:
		away = -float(_facing)
	velocity = Vector2(away * knockback.x, knockback.y)


func accepts_bounce() -> bool:
	return true


## Launched upward by a spring. Works for the player and the rival alike.
func bounce(launch_velocity: float) -> void:
	velocity.y = launch_velocity
	_climbing = false
	_jumping = false
	_coyote_timer = 0.0
	_ladder_cooldown = 0.2


func fall_respawn(spawn_position: Vector2) -> void:
	health = maxf(health - fall_damage, 0.0)
	health_changed.emit(health, max_health)
	SFX.play_at(SFX.HURT, global_position, _sfx_db())
	if health <= 0.0:
		GameState.call_deferred("restart_level")
		return

	_climbing = false
	global_position = spawn_position
	velocity = Vector2.ZERO
	_stun_timer = 0.0
	_invulnerable_timer = invulnerable_time
	$Camera2D.reset_smoothing()


func _shoot() -> void:
	if fireball_scene == null:
		return
	_shoot_timer = shoot_cooldown
	var fireball := fireball_scene.instantiate()
	fireball.direction = Vector2(_facing, 0)
	fireball.global_position = global_position + Vector2(_facing * 30, 4)
	get_tree().current_scene.add_child(fireball)
	SFX.play_at(SFX.THROW, global_position, _sfx_db())


## The rival's own sounds play quieter, so the player's actions stay easiest to hear.
func _sfx_db() -> float:
	return 0.0 if group_name == &"player" else -8.0


# Input sources. The rival AI overrides these to drive the same movement code.
func _in_axis_h() -> float:
	return Input.get_axis("ui_left", "ui_right")


func _in_climb_axis() -> float:
	return Input.get_axis("ui_up", "ui_down")


func _in_up() -> bool:
	return Input.is_action_pressed("ui_up")


func _in_down() -> bool:
	return Input.is_action_pressed("ui_down")


func _in_accept_pressed() -> bool:
	return Input.is_action_just_pressed("ui_accept")


func _in_jump_pressed() -> bool:
	return Input.is_action_just_pressed("ui_accept") or Input.is_action_just_pressed("ui_up")


func _in_jump_released() -> bool:
	return Input.is_action_just_released("ui_accept") or Input.is_action_just_released("ui_up")


func _in_shoot() -> bool:
	return Input.is_action_just_pressed("shoot")


func _update_animation() -> void:
	# Blink while invulnerable.
	if _invulnerable_timer > 0.0:
		_sprite.modulate.a = 0.4 if int(_invulnerable_timer * 10.0) % 2 == 0 else 1.0
	else:
		_sprite.modulate.a = 1.0

	if _climbing:
		_sprite.flip_h = false
		if absf(velocity.y) > 1.0:
			_sprite.play("climb")
		else:
			_sprite.pause()
		return

	if swimming:
		if _facing != 0:
			_sprite.flip_h = _facing < 0
		# The "jump" pose (limbs spread) doubles as a paddling/floating pose underwater.
		if _stun_timer > 0.0:
			_sprite.play("hurt")
		elif velocity.length() > 15.0:
			_sprite.play("jump")
		else:
			_sprite.play("idle")
		return

	var direction := _in_axis_h()
	if direction != 0.0 and _stun_timer == 0.0:
		_sprite.flip_h = direction < 0.0

	if _stun_timer > 0.0:
		_sprite.play("hurt")
	elif not is_on_floor():
		_sprite.play("jump")
	elif absf(velocity.x) > 10.0:
		_sprite.play("walk")
	else:
		_sprite.play("idle")
