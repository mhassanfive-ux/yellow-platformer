extends Node
## Fire-and-forget sound effects. Each call spawns a short-lived AudioStreamPlayer(2D)
## that frees itself when done, so overlapping sounds never cut each other off and no
## caller has to manage player nodes.

const JUMP: AudioStream = preload("res://assets/Sounds/sfx_jump.ogg")
const JUMP_HIGH: AudioStream = preload("res://assets/Sounds/sfx_jump-high.ogg")
const THROW: AudioStream = preload("res://assets/Sounds/sfx_throw.ogg")
const COIN: AudioStream = preload("res://assets/Sounds/sfx_coin.ogg")
const GEM: AudioStream = preload("res://assets/Sounds/sfx_gem.ogg")
const HURT: AudioStream = preload("res://assets/Sounds/sfx_hurt.ogg")
const BUMP: AudioStream = preload("res://assets/Sounds/sfx_bump.ogg")
const DISAPPEAR: AudioStream = preload("res://assets/Sounds/sfx_disappear.ogg")
const MAGIC: AudioStream = preload("res://assets/Sounds/sfx_magic.ogg")
const SELECT: AudioStream = preload("res://assets/Sounds/sfx_select.ogg")


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


## Plays without a world position — UI sounds, or anything where panning doesn't matter.
func play(stream: AudioStream, volume_db: float = 0.0, pitch_scale: float = 1.0, pitch_variance: float = 0.0) -> void:
	var player := AudioStreamPlayer.new()
	player.stream = stream
	player.volume_db = volume_db
	player.pitch_scale = pitch_scale + randf_range(-pitch_variance, pitch_variance)
	add_child(player)
	player.finished.connect(player.queue_free)
	# Deferred so a call made before the node's own first frame (e.g. from another node's
	# _ready()) can't race the audio server's tree-entry bookkeeping.
	player.call_deferred("play")


## Plays panned/attenuated at a world position. Not parented to the emitting node, so the
## sound survives even if that node dies or frees itself immediately after calling this.
func play_at(stream: AudioStream, world_position: Vector2, volume_db: float = 0.0, pitch_scale: float = 1.0, pitch_variance: float = 0.0) -> void:
	var player := AudioStreamPlayer2D.new()
	player.stream = stream
	player.volume_db = volume_db
	player.pitch_scale = pitch_scale + randf_range(-pitch_variance, pitch_variance)
	player.global_position = world_position
	add_child(player)
	player.finished.connect(player.queue_free)
	player.call_deferred("play")
