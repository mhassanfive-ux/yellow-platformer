extends Node
## Dev-only convenience: F1-F5 jump straight to Level01-05 from anywhere (the start
## screen, mid-level, whatever). Only active in debug builds (OS.is_debug_build()), so
## it's never present in an exported release build.

const LEVELS: Array[String] = [
	"res://scenes/Level01.tscn",
	"res://scenes/Level02.tscn",
	"res://scenes/Level03.tscn",
	"res://scenes/Level04.tscn",
	"res://scenes/Level05.tscn",
]


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_process_unhandled_key_input(OS.is_debug_build())


func _unhandled_key_input(event: InputEvent) -> void:
	if not (event is InputEventKey) or not event.pressed or event.echo:
		return
	if GameState.is_changing_level():
		return

	var keycode: Key = (event as InputEventKey).keycode
	if keycode < KEY_F1 or keycode > KEY_F5:
		return
	var index: int = keycode - KEY_F1
	if index >= LEVELS.size():
		return

	print("[DebugTools] Jumping to ", LEVELS[index])
	get_viewport().set_input_as_handled()
	GameState.change_level(LEVELS[index])
