extends CanvasLayer

const HEART_FULL: Texture2D = preload("res://assets/Sprites/Tiles/Default/hud_heart.png")
const HEART_HALF: Texture2D = preload("res://assets/Sprites/Tiles/Default/hud_heart_half.png")
const HEART_EMPTY: Texture2D = preload("res://assets/Sprites/Tiles/Default/hud_heart_empty.png")
const STAR_ICON: Texture2D = preload("res://assets/Sprites/Tiles/Default/star.png")
const RIVAL_ICON: Texture2D = preload("res://assets/Sprites/Tiles/Default/hud_player_green.png")
const MULTIPLY: Texture2D = preload("res://assets/Sprites/Tiles/Default/hud_character_multiply.png")
const DIGITS: Array[Texture2D] = [
	preload("res://assets/Sprites/Tiles/Default/hud_character_0.png"),
	preload("res://assets/Sprites/Tiles/Default/hud_character_1.png"),
	preload("res://assets/Sprites/Tiles/Default/hud_character_2.png"),
	preload("res://assets/Sprites/Tiles/Default/hud_character_3.png"),
	preload("res://assets/Sprites/Tiles/Default/hud_character_4.png"),
	preload("res://assets/Sprites/Tiles/Default/hud_character_5.png"),
	preload("res://assets/Sprites/Tiles/Default/hud_character_6.png"),
	preload("res://assets/Sprites/Tiles/Default/hud_character_7.png"),
	preload("res://assets/Sprites/Tiles/Default/hud_character_8.png"),
	preload("res://assets/Sprites/Tiles/Default/hud_character_9.png"),
]

const HEART_SIZE: float = 48.0
const GLYPH_SIZE: float = 44.0

@onready var _health_bar: HBoxContainer = $HealthBar
@onready var _stars_counter: HBoxContainer = $StarsCounter
@onready var _rival_counter: HBoxContainer = $RivalCounter
@onready var _win_label: Label = $WinLabel
## Levels without a key can hide the slot.
@export var show_key_slot: bool = true
## Levels without a rival can hide its counter.
@export var show_rival_counter: bool = true

@onready var _key_slot: TextureRect = $KeySlot

var _banner_tween: Tween
var _key_tween: Tween
var _has_key: bool = false


func _ready() -> void:
	# Wait one frame so the player and level have run their own _ready().
	await get_tree().process_frame

	var player := get_tree().get_first_node_in_group("player")
	if player:
		player.health_changed.connect(_on_health_changed)
		_on_health_changed(player.health, player.max_health)

	var level := get_parent()
	if level.has_signal("stars_changed"):
		level.stars_changed.connect(_on_stars_changed)
		level.star_race_finished.connect(_on_star_race_finished)
		level.key_changed.connect(_on_key_changed)
		level.key_required.connect(_on_key_required)
		level.level_completed.connect(_on_level_completed)
		level.checkpoint_reached.connect(_on_checkpoint_reached)
		_on_stars_changed(level.player_stars, level.rival_stars, level.total_stars)
		_key_slot.pivot_offset = _key_slot.size / 2.0
	_key_slot.visible = show_key_slot
	_rival_counter.visible = show_rival_counter


func _on_health_changed(health: float, max_health: float) -> void:
	_clear(_health_bar)
	for i in ceili(max_health):
		var remaining := health - i
		var texture := HEART_EMPTY
		if remaining >= 1.0:
			texture = HEART_FULL
		elif remaining >= 0.5:
			texture = HEART_HALF
		_health_bar.add_child(_make_icon(texture, HEART_SIZE))


func _on_stars_changed(player_stars: int, rival_stars: int, _total: int) -> void:
	_fill_counter(_stars_counter, STAR_ICON, player_stars)
	_fill_counter(_rival_counter, RIVAL_ICON, rival_stars)


func _fill_counter(counter: HBoxContainer, icon: Texture2D, value: int) -> void:
	_clear(counter)
	counter.add_child(_make_icon(icon, HEART_SIZE))
	counter.add_child(_make_icon(MULTIPLY, GLYPH_SIZE))
	for digit in str(value):
		counter.add_child(_make_icon(DIGITS[int(digit)], GLYPH_SIZE))


## The star race is decided, but play continues: show the result for a few seconds.
func _on_star_race_finished(player_won: bool) -> void:
	_show_banner("You won the star race!" if player_won else "Rival won the star race!", 3.0)


func _on_checkpoint_reached() -> void:
	_show_banner("Checkpoint!", 1.2)


func _on_level_completed() -> void:
	_show_banner("Level Complete!", 0.0)


## Shows the banner; a duration of 0 leaves it up.
func _show_banner(text: String, duration: float) -> void:
	if _banner_tween:
		_banner_tween.kill()
	_win_label.text = text
	_win_label.visible = true
	if duration > 0.0:
		_banner_tween = create_tween()
		_banner_tween.tween_interval(duration)
		_banner_tween.tween_callback(func() -> void: _win_label.visible = false)


func _key_rest_color() -> Color:
	return Color(1.0, 1.0, 1.0, 1.0 if _has_key else 0.25)


func _on_key_changed(has_key: bool) -> void:
	_has_key = has_key
	if _key_tween:
		_key_tween.kill()  # drop any red flash so it can't overwrite the new state
	_key_slot.modulate = _key_rest_color()
	if has_key:
		_key_tween = create_tween()
		_key_tween.tween_property(_key_slot, "scale", Vector2(1.5, 1.5), 0.12)
		_key_tween.tween_property(_key_slot, "scale", Vector2.ONE, 0.18)


## The player touched the locked door: flash the key slot red.
func _on_key_required() -> void:
	if _key_tween:
		_key_tween.kill()
	_key_tween = create_tween()
	for i in 2:
		_key_tween.tween_property(_key_slot, "modulate", Color(1.0, 0.25, 0.25, 1.0), 0.1)
		_key_tween.tween_property(_key_slot, "modulate", _key_rest_color(), 0.15)


func _clear(container: Control) -> void:
	for child in container.get_children():
		container.remove_child(child)
		child.queue_free()


func _make_icon(texture: Texture2D, icon_size: float) -> TextureRect:
	var rect := TextureRect.new()
	rect.texture = texture
	rect.custom_minimum_size = Vector2(icon_size, icon_size)
	rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	return rect
