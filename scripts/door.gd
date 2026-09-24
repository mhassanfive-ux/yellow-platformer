extends Area2D
## A two-tile-tall door. The node's origin is the bottom-centre of the door.
## Touching it with the key opens it and finishes the level; without the key it
## just shakes and shows a padlock.

const OPEN_BOTTOM: Texture2D = preload("res://assets/Sprites/Tiles/Default/door_open.png")
const OPEN_TOP: Texture2D = preload("res://assets/Sprites/Tiles/Default/door_open_top.png")

## The level to load next. Leave empty for a plain "Level Complete!" and restart.
@export_file("*.tscn") var next_level: String = ""

var _used: bool = false

@onready var _bottom: Sprite2D = $Bottom
@onready var _top: Sprite2D = $Top
@onready var _lock_icon: Sprite2D = $LockIcon


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	_lock_icon.visible = false


func _on_body_entered(body: Node2D) -> void:
	if _used or not body.is_in_group("player"):
		return
	# The level is the scene that owns this door.
	var level := owner
	if level != null and level.get("has_key"):
		_open(level)
	else:
		_show_locked(level)


func _open(level: Node) -> void:
	_used = true
	SFX.play_at(SFX.MAGIC, global_position)
	_bottom.texture = OPEN_BOTTOM
	_top.texture = OPEN_TOP
	await get_tree().create_timer(0.35).timeout
	level.complete_level(next_level)


func _show_locked(level: Node) -> void:
	SFX.play_at(SFX.BUMP, global_position)
	if level != null and level.has_signal("key_required"):
		level.key_required.emit()

	# A short shake and a padlock that floats up and fades.
	var shake := create_tween()
	for offset in [4.0, -4.0, 3.0, -3.0, 0.0]:
		shake.tween_property(self, "position:x", position.x + offset, 0.04)
	_lock_icon.visible = true
	_lock_icon.position = Vector2(0.0, -150.0)
	_lock_icon.modulate.a = 1.0
	var pop := create_tween().set_parallel()
	pop.tween_property(_lock_icon, "position:y", -178.0, 0.6)
	pop.tween_property(_lock_icon, "modulate:a", 0.0, 0.6)
	pop.chain().tween_callback(func() -> void: _lock_icon.visible = false)
