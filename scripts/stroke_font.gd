extends RefCounted
## Draws text as two-tone rounded strokes (white core, slate outline), the same look as the
## HUD digits. Only the letters listed in _glyph() exist; add more there as they are needed.

const OUTLINE_COLOR: Color = Color("92a1ad")
const CORE_COLOR: Color = Color.WHITE
## Stroke widths as fractions of the letter height.
const CORE_WIDTH: float = 0.19
const OUTLINE_EXTRA: float = 0.15


## True if every character of `text` can be drawn (spaces are allowed).
static func can_draw(text: String) -> bool:
	for ch in text:
		if ch != " " and _glyph(ch).is_empty():
			return false
	return true


static func word_width(text: String, height: float, gap: float) -> float:
	var total := 0.0
	for ch in text:
		total += _advance(ch, height) + gap
	return maxf(total - gap, 0.0)


## Builds `text` as a Node2D centred on its own origin, so it can be positioned, scaled or
## animated as one piece. All outlines are drawn first and all cores second, so strokes
## that touch merge cleanly instead of showing seams.
static func make_word(text: String, height: float, gap: float) -> Node2D:
	var word := Node2D.new()
	var core_width := height * CORE_WIDTH
	var layers := [[core_width + height * OUTLINE_EXTRA, OUTLINE_COLOR], [core_width, CORE_COLOR]]
	var start_x := -word_width(text, height, gap) / 2.0
	for layer in layers:
		var cursor := start_x
		for ch in text:
			var glyph := _glyph(ch)
			for stroke in glyph.get("strokes", []):
				var line := Line2D.new()
				var points := PackedVector2Array()
				for p in stroke:
					points.append(Vector2(cursor + p.x * height, (p.y - 0.5) * height))
				line.points = points
				line.width = layer[0]
				line.default_color = layer[1]
				line.begin_cap_mode = Line2D.LINE_CAP_ROUND
				line.end_cap_mode = Line2D.LINE_CAP_ROUND
				line.joint_mode = Line2D.LINE_JOINT_ROUND
				line.closed = glyph.get("closed", false)
				line.antialiased = true
				word.add_child(line)
			cursor += _advance(ch, height) + gap
	return word


static func _advance(ch: String, height: float) -> float:
	if ch == " ":
		return height * 0.45
	return float(_glyph(ch).get("width", 0.5)) * height


static func _arc(cx: float, cy: float, rx: float, ry: float, from_deg: float, to_deg: float, steps: int = 12) -> Array:
	var points := []
	for i in steps + 1:
		var a := deg_to_rad(lerpf(from_deg, to_deg, float(i) / steps))
		points.append(Vector2(cx + cos(a) * rx, cy + sin(a) * ry))
	return points


## Letter skeletons in a box `width` wide and 1.0 tall (y down). Each stroke is a polyline.
static func _glyph(ch: String) -> Dictionary:
	match ch:
		"Y":
			return {"width": 0.7, "strokes": [[Vector2(0, 0), Vector2(0.35, 0.5)], [Vector2(0.7, 0), Vector2(0.35, 0.5)], [Vector2(0.35, 0.5), Vector2(0.35, 1)]]}
		"E":
			return {"width": 0.6, "strokes": [[Vector2(0.6, 0), Vector2(0, 0), Vector2(0, 1), Vector2(0.6, 1)], [Vector2(0, 0.5), Vector2(0.45, 0.5)]]}
		"L":
			return {"width": 0.6, "strokes": [[Vector2(0, 0), Vector2(0, 1), Vector2(0.6, 1)]]}
		"O":
			return {"width": 0.7, "strokes": [_arc(0.35, 0.5, 0.35, 0.5, 0, 360, 28)], "closed": true}
		"W":
			return {"width": 1.0, "strokes": [[Vector2(0, 0), Vector2(0.2, 1), Vector2(0.5, 0.35), Vector2(0.8, 1), Vector2(1.0, 0)]]}
		"P":
			return {"width": 0.65, "strokes": [[Vector2(0, 1), Vector2(0, 0), Vector2(0.38, 0)] + _arc(0.38, 0.28, 0.27, 0.28, -90, 90) + [Vector2(0, 0.56)]]}
		"A":
			return {"width": 0.75, "strokes": [[Vector2(0, 1), Vector2(0.375, 0), Vector2(0.75, 1)], [Vector2(0.14, 0.68), Vector2(0.61, 0.68)]]}
		"T":
			return {"width": 0.7, "strokes": [[Vector2(0, 0), Vector2(0.7, 0)], [Vector2(0.35, 0), Vector2(0.35, 1)]]}
		"F":
			return {"width": 0.6, "strokes": [[Vector2(0, 1), Vector2(0, 0), Vector2(0.6, 0)], [Vector2(0, 0.5), Vector2(0.45, 0.5)]]}
		"R":
			return {"width": 0.68, "strokes": [[Vector2(0, 1), Vector2(0, 0), Vector2(0.38, 0)] + _arc(0.38, 0.28, 0.27, 0.28, -90, 90) + [Vector2(0, 0.56)], [Vector2(0.28, 0.56), Vector2(0.68, 1)]]}
		"M":
			return {"width": 0.85, "strokes": [[Vector2(0, 1), Vector2(0, 0), Vector2(0.425, 0.6), Vector2(0.85, 0), Vector2(0.85, 1)]]}
		"U":
			# Screen space is y-down, so the arc must sweep 180 -> 0 (through 90, i.e. +y)
			# to bulge downward; 180 -> 360 would bulge it up and out through the letter top.
			return {"width": 0.7, "strokes": [[Vector2(0, 0), Vector2(0, 0.55)] + _arc(0.35, 0.55, 0.35, 0.45, 180, 0, 16) + [Vector2(0.7, 0)]]}
		"S":
			return {"width": 0.65, "strokes": [[Vector2(0.62, 0.12), Vector2(0.48, 0.0), Vector2(0.2, 0.0), Vector2(0.04, 0.14), Vector2(0.04, 0.32), Vector2(0.2, 0.46), Vector2(0.48, 0.54), Vector2(0.64, 0.68), Vector2(0.64, 0.86), Vector2(0.48, 1.0), Vector2(0.18, 1.0), Vector2(0.02, 0.88)]]}
	return {}
