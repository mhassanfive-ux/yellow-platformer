extends RefCounted
## Navigation graph for the rival AI, built from a TileMapLayer and the level's ladders.
##
## Every tile with nothing above it is a "spot" where a character can stand. Spots are
## linked by the moves a character can make between them: walking, jumping across gaps
## or up one tile, dropping off ledges, and climbing ladders.

enum Kind { WALK, JUMP, DROP, CLIMB_UP, CLIMB_DOWN, SPRING }

const TILE: float = 64.0
## Jumps are only planned to cover this fraction of the true reach, as a safety margin.
const REACH_MARGIN: float = 0.8
const MAX_JUMP_TILES: int = 4
const MAX_DROP_ROWS: int = 14

var astar: AStar2D = AStar2D.new()
var spots: Dictionary = {}     # id -> standing position (character centre)
var cell_ids: Dictionary = {}  # Vector2i tile cell -> id
var spot_cells: Dictionary = {}  # id -> Vector2i tile cell
var edges: Dictionary = {}     # edge_key(a, b) -> { "kind": Kind, "ladder": Node, "takeoff": float }

var _layer: TileMapLayer


static func edge_key(a: int, b: int) -> int:
	return a * 100000 + b


func build(layer: TileMapLayer, ladders: Array, speed: float, jump_velocity: float, gravity: float, springs: Array = []) -> void:
	_layer = layer
	for cell in layer.get_used_cells():
		if layer.get_cell_source_id(cell + Vector2i.UP) == -1:
			var id := astar.get_available_point_id()
			var pos := layer.to_global(layer.map_to_local(cell)) + Vector2(0.0, -TILE)
			astar.add_point(id, pos)
			spots[id] = pos
			cell_ids[cell] = id
			spot_cells[id] = cell

	for cell in cell_ids:
		_add_walk_edges(cell)
		_add_jump_edges(cell, speed, jump_velocity, gravity)
		_add_drop_edges(cell)
	for ladder in ladders:
		_add_ladder_edges(ladder)
	for spring in springs:
		_add_spring_edges(spring, speed, gravity)


func nearest_spot(pos: Vector2, max_distance: float = 60.0) -> int:
	var best := -1
	var best_d := max_distance
	for id in spots:
		var d: float = (spots[id] as Vector2).distance_to(pos)
		if d < best_d:
			best_d = d
			best = id
	return best


## Spots from which a star at `star_pos` can be reached by standing or a single jump.
func spots_for_star(star_pos: Vector2) -> Array[int]:
	var result: Array[int] = []
	for id in spots:
		var s: Vector2 = spots[id]
		var above := s.y - star_pos.y  # positive when the star is higher than the spot
		if absf(s.x - star_pos.x) <= 96.0 and above >= -30.0 and above <= 100.0:
			result.append(id)
	return result


func _connect(a: int, b: int, kind: Kind, ladder: Node = null, takeoff: float = 0.0) -> void:
	astar.connect_points(a, b, false)
	edges[edge_key(a, b)] = {"kind": kind, "ladder": ladder, "takeoff": takeoff}


func _add_walk_edges(cell: Vector2i) -> void:
	for dir in [-1, 1]:
		var neighbour: Vector2i = cell + Vector2i(dir, 0)
		if cell_ids.has(neighbour):
			_connect(cell_ids[cell], cell_ids[neighbour], Kind.WALK)


func _add_jump_edges(cell: Vector2i, speed: float, jump_velocity: float, gravity: float) -> void:
	var apex := jump_velocity * jump_velocity / (2.0 * gravity)
	for dxc in range(-MAX_JUMP_TILES, MAX_JUMP_TILES + 1):
		if dxc == 0:
			continue
		for dyc in range(-1, 3):  # -1 = one tile higher
			var target: Vector2i = cell + Vector2i(dxc, dyc)
			if not cell_ids.has(target):
				continue
			if dyc == 0 and absi(dxc) == 1:
				continue  # plain walking
			if dyc > 0 and absi(dxc) < 3:
				continue  # short drops are done by walking off
			var rise := -dyc * TILE
			if rise > apex - 20.0:
				continue
			var disc := jump_velocity * jump_velocity - 2.0 * gravity * rise
			if disc < 0.0:
				continue
			var air_time := (-jump_velocity + sqrt(disc)) / gravity
			var gap := (absi(dxc) - 1) * TILE
			if gap > speed * air_time * REACH_MARGIN:
				continue
			# The columns crossed must have clear air above the take-off surface.
			var dir := signi(dxc)
			var clear := true
			for k in range(1, absi(dxc)):
				var col := cell.x + dir * k
				if _layer.get_cell_source_id(Vector2i(col, cell.y - 1)) != -1 \
						or _layer.get_cell_source_id(Vector2i(col, cell.y - 2)) != -1:
					clear = false
					break
			if not clear:
				continue
			# Wide jumps take off from near the edge; step-ups from the middle.
			var takeoff := 24.0 if absi(dxc) >= 2 else 0.0
			_connect(cell_ids[cell], cell_ids[target], Kind.JUMP, null, takeoff)


func _add_drop_edges(cell: Vector2i) -> void:
	for dir in [-1, 1]:
		# Only from a ledge: nothing at all beside this tile at the same height.
		if _layer.get_cell_source_id(cell + Vector2i(dir, 0)) != -1:
			continue
		for dxt in [1, 2]:
			var col: int = cell.x + dir * dxt
			if _layer.get_cell_source_id(Vector2i(col, cell.y)) != -1:
				break
			for row in range(cell.y + 1, cell.y + MAX_DROP_ROWS):
				var land := Vector2i(col, row)
				if _layer.get_cell_source_id(land) != -1:
					if cell_ids.has(land):
						_connect(cell_ids[cell], cell_ids[land], Kind.DROP)
					break


func _add_ladder_edges(ladder: Node) -> void:
	var x: float = ladder.global_position.x
	var top_y: float = ladder.global_position.y
	var bottom_y: float = top_y + ladder.height_tiles * TILE
	var foot := -1
	var tops: Array[int] = []
	for id in spots:
		var s: Vector2 = spots[id]
		if absf(s.x - x) < 10.0 and absf(s.y - (bottom_y - 32.0)) < 10.0:
			foot = id
		elif absf(s.y - (top_y - 32.0)) < 10.0 and absf(absf(s.x - x) - TILE) < 10.0:
			tops.append(id)
	if foot == -1:
		return
	for top in tops:
		_connect(foot, top, Kind.CLIMB_UP, ladder)
		_connect(top, foot, Kind.CLIMB_DOWN, ladder)


## A spring launches a character straight up; they steer in mid-air onto a higher surface.
func _add_spring_edges(spring: Node, speed: float, gravity: float) -> void:
	var launch: float = absf(spring.bounce_velocity)
	var apex := launch * launch / (2.0 * gravity)
	var from_id := -1
	for id in spots:
		var s: Vector2 = spots[id]
		if absf(s.x - spring.global_position.x) < 10.0 and absf(s.y - (spring.global_position.y - 32.0)) < 10.0:
			from_id = id
			break
	if from_id == -1:
		return
	var origin: Vector2 = spots[from_id]
	var origin_cell: Vector2i = spot_cells[from_id]
	for id in spots:
		var target: Vector2 = spots[id]
		var rise := origin.y - target.y
		# Only worth a spring for a real climb, not a one-tile hop.
		if rise < TILE * 2.0 or rise > apex - 20.0:
			continue
		var disc := launch * launch - 2.0 * gravity * rise
		var air_time := (launch + sqrt(disc)) / gravity
		var horizontal := absf(target.x - origin.x)
		if horizontal - TILE / 2.0 > speed * air_time * REACH_MARGIN:
			continue
		# The column above the spring must be open all the way up.
		var open := true
		for k in range(1, int(ceil(rise / TILE)) + 1):
			if _layer.get_cell_source_id(Vector2i(origin_cell.x, origin_cell.y - k)) != -1:
				open = false
				break
		if open:
			_connect(from_id, id, Kind.SPRING, null, 0.0)
			edges[edge_key(from_id, id)]["spring"] = spring

