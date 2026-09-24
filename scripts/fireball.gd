extends Area2D

@export var speed: float = 520.0
@export var lifetime: float = 1.5
@export var spin_speed: float = 12.0

var direction: Vector2 = Vector2.RIGHT

@onready var _sprite: Sprite2D = $Sprite2D


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	get_tree().create_timer(lifetime).timeout.connect(queue_free)


func _physics_process(delta: float) -> void:
	position += direction * speed * delta
	_sprite.rotation += spin_speed * delta * signf(direction.x)


func _on_body_entered(body: Node) -> void:
	SFX.play_at(SFX.BUMP, global_position)
	if body.has_method("die"):
		body.die()
	elif body.has_method("stun"):
		body.stun()
	queue_free()
