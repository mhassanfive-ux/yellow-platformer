extends CanvasLayer
## A pause overlay available in every level. Press Escape (the built-in "ui_cancel" action)
## during play to bring it up; it stops the game clock while staying interactive itself.
## Not offered on the start screen (there is nothing to pause there).

const StrokeFont = preload("res://scripts/stroke_font.gd")
const START_SCREEN: String = "res://scenes/StartScreen.tscn"
const SCREEN: Vector2 = Vector2(1152.0, 648.0)

var _open: bool = false
var _buttons: Array[Button] = []
var _tooltip_theme: Theme


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	layer = 90  # below GameState's fade layer (100), above everything in the level
	visible = false
	_build_ui()


func _unhandled_input(event: InputEvent) -> void:
	if not event.is_action_pressed("ui_cancel"):
		return
	if _open:
		_resume()
		get_viewport().set_input_as_handled()
	elif _can_pause():
		_pause()
		get_viewport().set_input_as_handled()


## Only inside an actual level (something with complete_level(), i.e. level.gd), and not
## while a fade/scene-swap is already under way.
func _can_pause() -> bool:
	var scene := get_tree().current_scene
	return scene != null and scene.has_method("complete_level") and not GameState.is_changing_level()


func _pause() -> void:
	_open = true
	visible = true
	get_tree().paused = true
	SFX.play(SFX.SELECT)
	_buttons[0].grab_focus()


func _resume() -> void:
	_open = false
	visible = false
	get_tree().paused = false


func _on_resume_pressed() -> void:
	SFX.play(SFX.SELECT)
	_resume()


func _on_restart_pressed() -> void:
	SFX.play(SFX.SELECT)
	_resume()
	GameState.restart_level()


func _on_start_screen_pressed() -> void:
	SFX.play(SFX.SELECT)
	_resume()
	GameState.change_level(START_SCREEN)


# --- Building the UI -------------------------------------------------------------------

func _build_ui() -> void:
	var dim := ColorRect.new()
	dim.color = Color(0.0, 0.0, 0.0, 0.55)
	dim.size = SCREEN
	dim.mouse_filter = Control.MOUSE_FILTER_STOP  # blocks clicks from reaching the level
	add_child(dim)

	var panel_size := Vector2(360.0, 400.0)
	var panel_pos := (SCREEN - panel_size) / 2.0
	var panel := Panel.new()
	panel.position = panel_pos
	panel.size = panel_size
	var style := StyleBoxFlat.new()
	style.bg_color = Color("2b3542")
	style.border_color = Color("3d4552")
	style.set_border_width_all(6)
	style.set_corner_radius_all(28)
	style.shadow_color = Color(0.0, 0.0, 0.0, 0.35)
	style.shadow_size = 10
	panel.add_theme_stylebox_override("panel", style)
	add_child(panel)

	_build_pause_icon(panel_pos + Vector2(panel_size.x / 2.0, 76.0))

	var labels := ["RESUME", "RESTART", "START"]
	var callbacks := [_on_resume_pressed, _on_restart_pressed, _on_start_screen_pressed]
	var tooltips := [
		"Continue playing right where you left off",
		"Start this level over from the beginning",
		"Leave this level and return to the title screen",
	]
	for i in labels.size():
		var button := _make_button(labels[i], callbacks[i], tooltips[i])
		button.position = panel_pos + Vector2((panel_size.x - button.size.x) / 2.0, 152.0 + i * 82.0)
		add_child(button)
		_buttons.append(button)


## Two rounded bars, drawn in the same white-core/slate-outline style as the lettering.
func _build_pause_icon(centre: Vector2) -> void:
	var layers := [[26.0, StrokeFont.OUTLINE_COLOR], [14.0, StrokeFont.CORE_COLOR]]
	for layer_info in layers:
		for x_offset in [-22.0, 22.0]:
			var bar := Line2D.new()
			bar.points = PackedVector2Array([centre + Vector2(x_offset, -34.0), centre + Vector2(x_offset, 34.0)])
			bar.width = layer_info[0]
			bar.default_color = layer_info[1]
			bar.begin_cap_mode = Line2D.LINE_CAP_ROUND
			bar.end_cap_mode = Line2D.LINE_CAP_ROUND
			bar.antialiased = true
			add_child(bar)


func _make_button(text: String, callback: Callable, tooltip: String) -> Button:
	var button := Button.new()
	button.size = Vector2(300.0, 64.0)
	button.add_theme_stylebox_override("normal", _plate(Color("fcbf1f")))
	button.add_theme_stylebox_override("hover", _plate(Color("ffd04d")))
	button.add_theme_stylebox_override("pressed", _plate(Color("e3a800")))
	button.add_theme_stylebox_override("focus", _plate(Color("fcbf1f")))
	button.pressed.connect(callback)
	button.tooltip_text = tooltip
	button.theme = _get_tooltip_theme()

	var label := StrokeFont.make_word(text, 30.0, 10.0)
	label.position = button.size / 2.0
	button.add_child(label)
	return button


## Restyles the built-in hover tooltip to match the game's dark-panel look instead of the
## default grey OS-style box. Built once and shared by every button.
func _get_tooltip_theme() -> Theme:
	if _tooltip_theme:
		return _tooltip_theme
	_tooltip_theme = Theme.new()
	var box := StyleBoxFlat.new()
	box.bg_color = Color("2b3542")
	box.border_color = Color("fcbf1f")
	box.set_border_width_all(3)
	box.set_corner_radius_all(10)
	box.content_margin_left = 12.0
	box.content_margin_right = 12.0
	box.content_margin_top = 7.0
	box.content_margin_bottom = 7.0
	_tooltip_theme.set_stylebox("panel", "TooltipPanel", box)
	_tooltip_theme.set_color("font_color", "TooltipLabel", Color.WHITE)
	return _tooltip_theme


func _plate(fill: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = fill
	style.border_color = Color("3d4552")
	style.set_border_width_all(4)
	style.set_corner_radius_all(20)
	return style
