extends Area2D
## A one-time switch. Touching it (only the player triggers it, like the key) permanently
## reveals a hidden platform elsewhere in the level.

const UNPRESSED: Texture2D = preload("res://assets/Sprites/Tiles/Default/switch_green.png")
const PRESSED: Texture2D = preload("res://assets/Sprites/Tiles/Default/switch_green_pressed.png")

## The HiddenPlatform, ChainBox, or anything else with an activate() method that this
## switch unlocks.
@export var target_path: NodePath

var _used: bool = false

@onready var _sprite: Sprite2D = $Sprite2D


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node2D) -> void:
	if _used or not body.is_in_group("player"):
		return
	_used = true
	_sprite.texture = PRESSED
	SFX.play_at(SFX.MAGIC, global_position)
	var target := get_node_or_null(target_path)
	if target and target.has_method("activate"):
		target.activate()
