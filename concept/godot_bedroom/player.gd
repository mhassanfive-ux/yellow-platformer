extends Node3D
## Walks the boy around the bedroom with the arrow keys, turning his sprite to
## face the way he moves and bobbing it a pixel per step.

enum Facing { DOWN, LEFT, UP, RIGHT }  # frame order in the sprite strip

const SPEED := 2.2
const FOOT_RADIUS := 0.22
const FEET_OFFSET := 16  # sprite pixels from its centre down to his boots

## Floor he can stand on, and furniture footprints, as rectangles on the X/Z plane.
const ROOM := Rect2(-3.75, -2.45, 7.5, 5.2)
const BLOCKED: Array[Rect2] = [
	Rect2(1.76, 1.34, 1.99, 1.32),    # bed
	Rect2(3.2, 0.72, 0.55, 0.53),     # nightstand
	Rect2(2.37, -2.75, 1.38, 2.23),   # stairwell
	Rect2(-1.9, -2.75, 1.8, 0.65),    # desk
	Rect2(-1.25, -2.0, 0.5, 0.54),    # chair
	Rect2(-3.75, -2.56, 0.45, 1.56),  # bookshelf
	Rect2(-3.75, -0.2, 0.45, 1.4),    # dresser
	Rect2(-3.55, 1.95, 1.1, 0.6),     # seed crate and watering can
	Rect2(-2.95, -2.6, 0.5, 0.5),     # potted plant
]

@onready var sprite: Sprite3D = $Sprite3D

var _walk_time := 0.0


func _physics_process(delta: float) -> void:
	var input := Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	if input == Vector2.ZERO:
		_walk_time = 0.0
		sprite.offset.y = FEET_OFFSET
		return

	_face(input)
	var step := Vector3(input.x, 0.0, input.y) * SPEED * delta
	# Try each axis on its own so he slides along furniture instead of sticking.
	var p := position
	if _is_free(p + Vector3(step.x, 0.0, 0.0)):
		p.x += step.x
	if _is_free(p + Vector3(0.0, 0.0, step.z)):
		p.z += step.z
	position = p

	_walk_time += delta
	sprite.offset.y = FEET_OFFSET + (1 if fmod(_walk_time, 0.3) < 0.15 else 0)


func _face(dir: Vector2) -> void:
	if absf(dir.x) > absf(dir.y):
		sprite.frame = Facing.RIGHT if dir.x > 0.0 else Facing.LEFT
	else:
		sprite.frame = Facing.DOWN if dir.y > 0.0 else Facing.UP


func _is_free(p: Vector3) -> bool:
	var feet := Rect2(p.x - FOOT_RADIUS, p.z - FOOT_RADIUS * 0.6, FOOT_RADIUS * 2.0, FOOT_RADIUS * 1.2)
	if not ROOM.encloses(feet):
		return false
	for r in BLOCKED:
		if r.intersects(feet):
			return false
	return true
