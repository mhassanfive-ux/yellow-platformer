extends "res://scripts/player.gd"
## A computer-controlled character that races the player to the stars. It reuses all of
## the player's movement (walking, jumping, ladders); only the inputs come from the AI.

const Nav = preload("res://scripts/rival_nav.gd")

@export var tile_layer_path: NodePath = ^"../TileMapLayer"
## Seconds the rival waits at the start, giving the player a head start.
@export var start_delay: float = 3.0

var _nav: RefCounted = null
var _star: Node2D = null
var _path: PackedInt64Array = PackedInt64Array()
var _step: int = 0
var _phase: int = 0
var _jumped: bool = false
var _bounce_wanted: bool = false
var _edge_time: float = 0.0
var _approach_time: float = 0.0
var _spawn: Vector2
var _kill_y: float = 900.0
var _stuck_time: float = 0.0
var _stuck_ref: Vector2 = Vector2.ZERO

# Virtual controller state, read through the _in_* overrides below.
var _ai_h: float = 0.0
var _ai_up: bool = false
var _ai_down: bool = false
var _ai_jump: bool = false
var _ai_jump_prev: bool = false


func _ready() -> void:
	super._ready()
	_spawn = global_position
	_stuck_ref = global_position
	# Let the level finish loading before reading its tiles, ladders and stars.
	await get_tree().process_frame
	await get_tree().process_frame
	var layer := get_node_or_null(tile_layer_path) as TileMapLayer
	if layer == null:
		push_error("Rival: no TileMapLayer at %s" % tile_layer_path)
		return
	var level := get_parent()
	if level != null and "kill_y" in level:
		_kill_y = level.kill_y
	_nav = Nav.new()
	_nav.build(layer, get_tree().get_nodes_in_group("ladders"), speed, jump_velocity, _gravity,
			get_tree().get_nodes_in_group("springs"))


func _physics_process(delta: float) -> void:
	_think(delta)
	super._physics_process(delta)
	_ai_jump_prev = _ai_jump


## Springs only launch the rival while it is deliberately using one.
func accepts_bounce() -> bool:
	return _bounce_wanted


## Called by the player's fireballs.
func stun(duration: float = 1.5) -> void:
	_stun_timer = duration
	_climbing = false
	_reset_plan()


## The rival never ends the level by running out of health, from a hazard or a fall -- it
## just resets to its start point with full health, the same way going past the kill zone
## already worked. Without this, a long level with enough incidental hazard contact could
## let the rival's health hit zero and restart the level out from under the player, since
## take_damage()/fall_respawn() are otherwise shared verbatim with the player.
func take_damage(from_position: Vector2, amount: float = -1.0) -> void:
	if _invulnerable_timer > 0.0 or health <= 0.0:
		return
	var dealt: float = contact_damage if amount < 0.0 else amount
	if health - dealt <= 0.0:
		SFX.play_at(SFX.HURT, global_position, _sfx_db())
		_respawn()
		health = max_health
		health_changed.emit(health, max_health)
		return
	super.take_damage(from_position, amount)


func fall_respawn(spawn_position: Vector2) -> void:
	if health - fall_damage <= 0.0:
		_respawn()
		health = max_health
		health_changed.emit(health, max_health)
		return
	super.fall_respawn(spawn_position)


# --- Input overrides -----------------------------------------------------------------

func _in_axis_h() -> float:
	return _ai_h


func _in_climb_axis() -> float:
	return (1.0 if _ai_down else 0.0) - (1.0 if _ai_up else 0.0)


func _in_up() -> bool:
	return _ai_up


func _in_down() -> bool:
	return _ai_down


func _in_accept_pressed() -> bool:
	return false  # the AI never jumps off ladders


func _in_jump_pressed() -> bool:
	return _ai_jump and not _ai_jump_prev


func _in_jump_released() -> bool:
	return _ai_jump_prev and not _ai_jump


func _in_shoot() -> bool:
	return false


# --- Thinking ------------------------------------------------------------------------

func _think(delta: float) -> void:
	_ai_h = 0.0
	_ai_up = false
	_ai_down = false
	# Hold jump until the apex so the jump isn't cut short.
	if _ai_jump and velocity.y >= 0.0:
		_ai_jump = false

	if _nav == null or _stun_timer > 0.0:
		return

	if start_delay > 0.0:
		start_delay -= delta
		return

	if global_position.y > _kill_y:
		_respawn()
		return

	_watch_stuck(delta)
	if not is_instance_valid(_star):
		_without_target(delta)
		return

	_edge_time += delta
	if _step >= _path.size() - 1:
		_final_approach(delta)
	else:
		_follow_edge()


## The target star is gone (the player took it, or a plan was thrown away). The rival must
## never freeze in the middle of a move: it finishes the climb or jump it is in, then plans
## again as soon as it is standing on something.
func _without_target(delta: float) -> void:
	if _climbing or not is_on_floor():
		if _step < _path.size() - 1:
			_edge_time += delta
			_follow_edge()
		elif _climbing:
			_ai_down = true  # nothing left to finish: climb down, then plan from the bottom
		return
	_choose_target()


func _choose_target() -> void:
	var current: int = _nav.nearest_spot(global_position)
	if current == -1:
		return
	var best_cost := INF
	var best_star: Node2D = null
	var best_path := PackedInt64Array()
	for star in get_tree().get_nodes_in_group("stars"):
		for spot in _nav.spots_for_star(star.global_position):
			var path: PackedInt64Array = _nav.astar.get_id_path(current, spot)
			if path.is_empty():
				continue
			var cost: float = 0.0
			for i in range(path.size() - 1):
				cost += (_nav.spots[path[i]] as Vector2).distance_to(_nav.spots[path[i + 1]])
			cost += (_nav.spots[spot] as Vector2).distance_to(star.global_position) * 0.5
			if cost < best_cost:
				best_cost = cost
				best_star = star
				best_path = path
	if best_star != null:
		_star = best_star
		_path = best_path
		_step = 0
		_reset_edge()
		_approach_time = 0.0


func _reset_edge() -> void:
	_phase = 0
	_jumped = false
	_bounce_wanted = false
	_edge_time = 0.0


func _reset_plan() -> void:
	_star = null
	_path = PackedInt64Array()
	_step = 0
	_ai_jump = false
	_reset_edge()


func _respawn() -> void:
	global_position = _spawn
	velocity = Vector2.ZERO
	_climbing = false
	_reset_plan()


func _dir_to(x: float) -> float:
	return signf(x - global_position.x)


func _follow_edge() -> void:
	var a: int = _path[_step]
	var b: int = _path[_step + 1]
	var edge: Dictionary = _nav.edges.get(Nav.edge_key(a, b), {})
	if edge.is_empty():
		_reset_plan()
		return
	var target: Vector2 = _nav.spots[b]

	match edge["kind"]:
		Nav.Kind.WALK, Nav.Kind.DROP:
			_ai_h = _dir_to(target.x) if absf(target.x - global_position.x) > 6.0 else 0.0
			_check_arrival(target)
		Nav.Kind.JUMP:
			_do_jump_edge(a, target, edge)
		Nav.Kind.CLIMB_UP:
			_do_climb_up(edge["ladder"], target)
		Nav.Kind.CLIMB_DOWN:
			_do_climb_down(edge["ladder"], target)
		Nav.Kind.SPRING:
			_do_spring_edge(edge["spring"], target)

	# An edge that drags on means something went wrong: plan again from here.
	if _edge_time > 8.0:
		_reset_plan()


func _check_arrival(target: Vector2) -> void:
	if is_on_floor() and absf(global_position.x - target.x) < 14.0 \
			and absf(global_position.y - target.y) < 24.0:
		_step += 1
		_reset_edge()


func _do_jump_edge(from_id: int, target: Vector2, edge: Dictionary) -> void:
	var start: Vector2 = _nav.spots[from_id]
	var dir := signf(target.x - start.x)
	if not _jumped:
		if not is_on_floor():
			return
		var takeoff_x: float = start.x + dir * float(edge["takeoff"])
		if (takeoff_x - global_position.x) * dir > 6.0:
			_ai_h = dir  # keep walking towards the take-off point
		else:
			_ai_h = dir
			_ai_jump = true
			_jumped = true
			_edge_time = 0.0
		return

	_ai_h = _dir_to(target.x)
	if is_on_floor() and _edge_time > 0.25:
		if absf(global_position.x - target.x) < 40.0 and absf(global_position.y - target.y) < 24.0:
			_step += 1
			_reset_edge()
		else:
			_reset_plan()  # missed the landing: plan again from wherever we are


func _do_spring_edge(spring: Node, target: Vector2) -> void:
	if not _jumped:
		# Walk onto the spring on purpose; springs otherwise don't launch the rival.
		_bounce_wanted = true
		var spring_x: float = spring.global_position.x
		if is_on_floor():
			_ai_h = _dir_to(spring_x) if absf(spring_x - global_position.x) > 4.0 else 0.0
		if velocity.y < -300.0:
			_jumped = true
			_edge_time = 0.0
		return

	_ai_h = _dir_to(target.x)
	if is_on_floor() and _edge_time > 0.25:
		if absf(global_position.x - target.x) < 40.0 and absf(global_position.y - target.y) < 24.0:
			_step += 1
			_reset_edge()
		else:
			_reset_plan()  # missed the landing: plan again from wherever we are


func _do_climb_up(ladder: Node, target: Vector2) -> void:
	var ladder_x: float = ladder.global_position.x
	match _phase:
		0:  # walk to the foot of the ladder and grab it
			if absf(global_position.x - ladder_x) > 6.0:
				_ai_h = _dir_to(ladder_x)
			else:
				_ai_up = true
			if _climbing:
				_phase = 1
		1:  # climb to the top rung, then climb out towards the platform
			if not _climbing:
				_phase = 0
			elif global_position.y <= ladder.top_limit_y() + 3.0:
				_ai_h = _dir_to(target.x)
				_phase = 2
			else:
				_ai_up = true
		2:
			_ai_h = _dir_to(target.x) if absf(target.x - global_position.x) > 6.0 else 0.0
			_check_arrival(target)


func _do_climb_down(ladder: Node, target: Vector2) -> void:
	var ladder_x: float = ladder.global_position.x
	if _climbing:
		_ai_down = true
		if is_on_floor():
			_check_arrival(target)
		return
	# Walk off the platform edge into the ladder's column and grab it on the way down.
	if is_on_floor() and absf(global_position.x - target.x) < 14.0:
		_check_arrival(target)
		return
	_ai_h = _dir_to(ladder_x) if absf(global_position.x - ladder_x) > 6.0 else 0.0
	if not is_on_floor() and absf(global_position.x - ladder_x) < 40.0:
		_ai_down = true


func _final_approach(delta: float) -> void:
	_approach_time += delta
	var star_pos := _star.global_position
	var dx := star_pos.x - global_position.x
	_ai_h = signf(dx) if absf(dx) > 8.0 else 0.0
	# A star above us or over a gap: jump for it.
	if is_on_floor() and (global_position.y - star_pos.y) > 24.0 and absf(dx) < 140.0 \
			and not _ai_jump:
		_ai_jump = true
	if _approach_time > 5.0:
		_reset_plan()


func _watch_stuck(delta: float) -> void:
	_stuck_time += delta
	if _stuck_time < 2.0:
		return
	_stuck_time = 0.0
	if global_position.distance_to(_stuck_ref) < 12.0 and not _climbing:
		_reset_plan()
	_stuck_ref = global_position
