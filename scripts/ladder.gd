extends Area2D
## A climbable ladder. The node's origin is the top-centre of the top rung;
## tiles stack downward from there.

const TILE_SIZE: int = 64
const TEX_TOP: Texture2D = preload("res://assets/Sprites/Tiles/Default/ladder_top.png")
const TEX_MIDDLE: Texture2D = preload("res://assets/Sprites/Tiles/Default/ladder_middle.png")
const TEX_BOTTOM: Texture2D = preload("res://assets/Sprites/Tiles/Default/ladder_bottom.png")

## How far above the top rung the area extends, so the player can climb until their
## feet are level with the platform the ladder leads to.
const OVERSHOOT: float = 40.0

@export var height_tiles: int = 4


func _ready() -> void:
	add_to_group("ladders")
	for i in height_tiles:
		var sprite := Sprite2D.new()
		if i == 0:
			sprite.texture = TEX_TOP
		elif i == height_tiles - 1:
			sprite.texture = TEX_BOTTOM
		else:
			sprite.texture = TEX_MIDDLE
		sprite.position = Vector2(0, i * TILE_SIZE + TILE_SIZE / 2.0)
		add_child(sprite)

	var shape := RectangleShape2D.new()
	shape.size = Vector2(24, height_tiles * TILE_SIZE + OVERSHOOT)
	var collision := CollisionShape2D.new()
	collision.shape = shape
	collision.position = Vector2(0, (height_tiles * TILE_SIZE - OVERSHOOT) / 2.0)
	add_child(collision)

	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)


## Highest point (smallest y) the player's centre may reach while climbing: hands on
## the top rung, with most of the body still alongside the ladder.
func top_limit_y() -> float:
	return global_position.y - 8.0


func _on_body_entered(body: Node2D) -> void:
	if body.has_method("enter_ladder"):
		body.enter_ladder(self)


func _on_body_exited(body: Node2D) -> void:
	if body.has_method("exit_ladder"):
		body.exit_ladder(self)
