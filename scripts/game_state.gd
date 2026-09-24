extends Node
## Global state that outlives a level, plus fading scene changes.

const FADE_TIME: float = 0.35

## Health carried into the next level, or -1 to start it with full health.
var carried_health: float = -1.0

var _fade_rect: ColorRect
var _changing: bool = false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var layer := CanvasLayer.new()
	layer.layer = 100
	add_child(layer)
	_fade_rect = ColorRect.new()
	_fade_rect.color = Color(0.0, 0.0, 0.0, 0.0)
	_fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	layer.add_child(_fade_rect)


## True while a fade/scene-swap is in progress. Callers that might otherwise interrupt or
## overlap that transition (like the pause menu) should check this first.
func is_changing_level() -> bool:
	return _changing


## Fade out, load the scene at `path`, fade back in.
func change_level(path: String) -> void:
	if _changing:
		return
	_changing = true
	await _fade_to(1.0)
	get_tree().change_scene_to_file(path)
	# Give the new scene a couple of frames to build before revealing it.
	await get_tree().process_frame
	await get_tree().process_frame
	await _fade_to(0.0)
	_changing = false


## Move on to another level, keeping the player's current health.
func advance_to(path: String) -> void:
	var player := get_tree().get_first_node_in_group("player")
	carried_health = player.health if player != null else -1.0
	await change_level(path)


## Restart the current level from scratch (full health).
func restart_level() -> void:
	var scene := get_tree().current_scene
	if scene == null or scene.scene_file_path.is_empty():
		return
	carried_health = -1.0
	await change_level(scene.scene_file_path)


func _fade_to(alpha: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade_rect, "color:a", alpha, FADE_TIME)
	await tween.finished
