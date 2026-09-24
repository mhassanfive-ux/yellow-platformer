extends Node2D
## The title screen: a running player on a scrolling landscape, the game's name in stroke
## lettering, and a START button that fades into the first level.

const StrokeFont = preload("res://scripts/stroke_font.gd")

const FIRST_LEVEL: String = "res://scenes/Level01.tscn"
const TILES: String = "res://assets/Sprites/Tiles/Default/"
const SCREEN: Vector2 = Vector2(1152.0, 648.0)
const GROUND_Y: float = 520.0
## How fast the world scrolls past the (stationary) running player, in pixels per second.
const WORLD_SPEED: float = 130.0

var _started: bool = false
var _time: float = 0.0
var _hovered: bool = false
var _pressed: bool = false

var _hills: Sprite2D
var _ground: Node2D
var _title: Node2D
var _subtitle: Node2D
var _bee: AnimatedSprite2D
var _button: Button
## Things that drift left with the world and wrap around: [node, x] pairs.
var _drifters: Array = []


func _ready() -> void:
	_build_sky()
	_build_hills()
	_build_ground()
	_build_drifters()
	_build_player()
	_build_bee()
	_build_title()
	_build_button()


func _process(delta: float) -> void:
	_time += delta

	_hills.position.x = -40.0 - fmod(_time * WORLD_SPEED * 0.4, 256.0)
	_ground.position.x = -fmod(_time * WORLD_SPEED, 64.0)
	for entry in _drifters:
		entry[1] -= WORLD_SPEED * delta
		if entry[1] < -120.0:
			entry[1] += SCREEN.x + 300.0
		var node: Node2D = entry[0]
		node.position.x = entry[1]

	# The bee crosses the sky in the opposite direction, bobbing as it goes.
	_bee.position.x -= 90.0 * delta
	if _bee.position.x < -80.0:
		_bee.position.x = SCREEN.x + 80.0
	_bee.position.y = 150.0 + sin(_time * 2.2) * 22.0

	_title.position.y = 104.0 + sin(_time * 1.6) * 5.0
	_subtitle.position.y = 244.0 + sin(_time * 1.6 + 0.7) * 4.0

	# The button eases towards a size that depends on hover/press, with a slow idle pulse.
	var target := 1.0 + sin(_time * 3.0) * 0.02
	if _pressed:
		target = 0.94
	elif _hovered:
		target = 1.08
	_button.scale = _button.scale.lerp(Vector2(target, target), clampf(14.0 * delta, 0.0, 1.0))


func _unhandled_input(event: InputEvent) -> void:
	# Enter or Space also starts (a focused button handles it too; this covers lost focus).
	if event.is_action_pressed("ui_accept"):
		get_viewport().set_input_as_handled()
		_start()


func _start() -> void:
	if _started:
		return
	_started = true
	_button.disabled = true
	SFX.play(SFX.SELECT)
	GameState.change_level(FIRST_LEVEL)


# --- Building the scene ---------------------------------------------------------------

func _sprite(path: String, position_: Vector2, scale_: float = 1.0) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = load(path)
	sprite.position = position_
	sprite.scale = Vector2(scale_, scale_)
	return sprite


func _animated(paths: Array, fps: float, position_: Vector2) -> AnimatedSprite2D:
	var frames := SpriteFrames.new()
	frames.set_animation_speed("default", fps)
	for path in paths:
		frames.add_frame("default", load(path))
	var sprite := AnimatedSprite2D.new()
	sprite.sprite_frames = frames
	sprite.position = position_
	sprite.play("default")
	return sprite


func _build_sky() -> void:
	var sky := ColorRect.new()
	sky.color = Color(195.0 / 255.0, 227.0 / 255.0, 1.0)
	sky.size = SCREEN
	add_child(sky)


func _build_hills() -> void:
	_hills = Sprite2D.new()
	_hills.texture = load("res://assets/Sprites/Backgrounds/Transparent/background_fade_hills.png")
	_hills.centered = false
	_hills.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	_hills.region_enabled = true
	_hills.region_rect = Rect2(0.0, 0.0, SCREEN.x + 512.0, 142.0)
	_hills.position = Vector2(-40.0, GROUND_Y - 142.0)
	add_child(_hills)


func _build_ground() -> void:
	_ground = Node2D.new()
	add_child(_ground)
	for i in 20:
		_ground.add_child(_sprite(TILES + "terrain_grass_block_top.png", Vector2(i * 64.0 + 32.0, GROUND_Y + 32.0)))
		_ground.add_child(_sprite(TILES + "terrain_grass_block_center.png", Vector2(i * 64.0 + 32.0, GROUND_Y + 96.0)))


func _build_drifters() -> void:
	var stars := [Vector2(300, GROUND_Y - 60), Vector2(860, GROUND_Y - 110), Vector2(960, GROUND_Y - 60)]
	for spot in stars:
		_add_drifter(_sprite(TILES + "star.png", spot, 0.8), spot.x)
	_add_drifter(_animated(
			["res://assets/Vector/Enemies/slime_fire_walk_a.svg", "res://assets/Vector/Enemies/slime_fire_walk_b.svg"],
			4.0, Vector2(1010, GROUND_Y - 32)), 1010.0)
	_add_drifter(_animated(
			[TILES + "flag_green_a.png", TILES + "flag_green_b.png"],
			4.0, Vector2(780, GROUND_Y - 32)), 780.0)


func _add_drifter(node: Node2D, x: float) -> void:
	add_child(node)
	_drifters.append([node, x])


func _build_player() -> void:
	var paths := [
		"res://assets/Sprites/Characters/Default/character_yellow_walk_a.png",
		"res://assets/Sprites/Characters/Default/character_yellow_walk_b.png",
	]
	add_child(_animated(paths, 8.0, Vector2(170.0, GROUND_Y - 62.0)))


func _build_bee() -> void:
	_bee = _animated(["res://assets/Vector/Enemies/bee_a.svg", "res://assets/Vector/Enemies/bee_b.svg"],
			10.0, Vector2(SCREEN.x + 80.0, 150.0))
	_bee.flip_h = true  # the art faces right and the bee flies left
	add_child(_bee)


func _build_title() -> void:
	_title = StrokeFont.make_word("YELLOW", 108.0, 34.0)
	_title.position = Vector2(SCREEN.x / 2.0, 104.0)
	add_child(_title)
	_subtitle = StrokeFont.make_word("PLATFORMER", 80.0, 26.0)
	_subtitle.position = Vector2(SCREEN.x / 2.0, 244.0)
	add_child(_subtitle)


func _build_button() -> void:
	_button = Button.new()
	_button.size = Vector2(380.0, 124.0)
	_button.position = Vector2(SCREEN.x / 2.0 - 190.0, 336.0)
	_button.pivot_offset = _button.size / 2.0
	_button.add_theme_stylebox_override("normal", _plate(Color("fcbf1f")))
	_button.add_theme_stylebox_override("hover", _plate(Color("ffd04d")))
	_button.add_theme_stylebox_override("pressed", _plate(Color("e3a800")))
	_button.add_theme_stylebox_override("disabled", _plate(Color("e3a800")))
	_button.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	_button.pressed.connect(_start)
	_button.mouse_entered.connect(func() -> void: _hovered = true)
	_button.mouse_exited.connect(func() -> void: _hovered = false)
	_button.button_down.connect(func() -> void: _pressed = true)
	_button.button_up.connect(func() -> void: _pressed = false)
	add_child(_button)

	var label := StrokeFont.make_word("START", 52.0, 18.0)
	label.position = _button.size / 2.0 + Vector2(0.0, -2.0)
	_button.add_child(label)
	_button.grab_focus()


## A yellow plate with the same dark outline the tiles have.
func _plate(fill: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = fill
	style.border_color = Color("3d4552")
	style.set_border_width_all(6)
	style.set_corner_radius_all(34)
	style.shadow_color = Color(0.0, 0.0, 0.0, 0.25)
	style.shadow_size = 8
	style.shadow_offset = Vector2(0.0, 6.0)
	return style
