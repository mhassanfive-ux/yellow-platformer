extends Node2D

signal stars_changed(player_stars: int, rival_stars: int, total: int)
## Emitted once every star has been taken. The player wins the race with more stars than
## the rival. Play continues afterwards: the level ends at the door.
signal star_race_finished(player_won: bool)
signal key_changed(has_key: bool)
## Emitted (by the door) when the player touches it without the key.
@warning_ignore("unused_signal")
signal key_required
## Emitted when the door is used and there is no next level to load.
signal level_completed
## Emitted when the player touches a checkpoint flag.
signal checkpoint_reached

## The playable area in world coordinates. It sets the camera limits, the invisible walls
## at the sides and the kill zone below the level.
@export var bounds: Rect2 = Rect2(0.0, -512.0, 2560.0, 1216.0)
## Seconds to show "Level Complete!" before restarting when there is no next level.
@export var restart_delay: float = 3.0
## Levels with no rival (nothing else collects stars) skip the "star race" banner.
@export var has_rival: bool = true

## Height below which a falling character is out of the level.
var kill_y: float = 0.0
var total_stars: int = 0
var player_stars: int = 0
var rival_stars: int = 0
var has_key: bool = false
## Where a fall respawns the player: the start, or the last checkpoint touched.
var respawn_position: Vector2 = Vector2.ZERO

var _completing: bool = false


func _ready() -> void:
	_apply_bounds()
	var spawn := get_node_or_null("PlayerSpawn") as Node2D
	if spawn:
		respawn_position = spawn.global_position
	# Stars and keys are children, so they have already run _ready() and joined their groups.
	for star in get_tree().get_nodes_in_group("stars"):
		total_stars += 1
		star.collected.connect(_on_star_collected)
	for key in get_tree().get_nodes_in_group("keys"):
		key.collected.connect(_on_key_collected)


func _apply_bounds() -> void:
	kill_y = bounds.end.y + 196.0

	var camera := get_node_or_null("Player/Camera2D") as Camera2D
	if camera:
		camera.limit_left = int(bounds.position.x)
		camera.limit_top = int(bounds.position.y)
		camera.limit_right = int(bounds.end.x)
		camera.limit_bottom = int(bounds.end.y)

	# Invisible walls just outside each side, tall enough to never be jumped over.
	var wall_height := bounds.size.y + 1000.0
	var centre_y := bounds.position.y + bounds.size.y / 2.0
	for wall_name in ["LeftWall", "RightWall"]:
		var wall := get_node_or_null(wall_name) as StaticBody2D
		if wall == null:
			continue
		var side := -1.0 if wall_name == "LeftWall" else 1.0
		var edge := bounds.position.x if side < 0.0 else bounds.end.x
		wall.position = Vector2(edge + side * 16.0, centre_y)
		var shape := (wall.get_node("CollisionShape2D") as CollisionShape2D).shape as RectangleShape2D
		shape.size = Vector2(32.0, wall_height)

	var kill_zone := get_node_or_null("KillZone") as Area2D
	if kill_zone:
		kill_zone.position = Vector2(bounds.position.x + bounds.size.x / 2.0, bounds.end.y + 96.0)
		var kill_shape := (kill_zone.get_node("CollisionShape2D") as CollisionShape2D).shape as RectangleShape2D
		kill_shape.size = Vector2(bounds.size.x + 640.0, 200.0)


func _on_star_collected(collector: Node) -> void:
	if collector.is_in_group("rival"):
		rival_stars += 1
	else:
		player_stars += 1
	stars_changed.emit(player_stars, rival_stars, total_stars)

	if has_rival and player_stars + rival_stars >= total_stars:
		star_race_finished.emit(player_stars > rival_stars)


func _on_key_collected(_collector: Node) -> void:
	has_key = true
	key_changed.emit(true)


## Called by a checkpoint flag when the player touches it.
func set_checkpoint(position_: Vector2) -> void:
	respawn_position = position_
	checkpoint_reached.emit()


## Called by the door once the player has opened it.
func complete_level(next_level: String) -> void:
	if _completing:
		return
	_completing = true
	if next_level != "" and ResourceLoader.exists(next_level):
		GameState.advance_to(next_level)
		return
	level_completed.emit()
	await get_tree().create_timer(restart_delay).timeout
	GameState.restart_level()
