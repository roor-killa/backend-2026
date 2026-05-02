extends Node2D

# Must match circle_visual.gd RADIUS exactly.
const HIT_RADIUS      := 80.0
# Outer ring: note just entered circle — too soon.
const TOO_SOON_RADIUS := 60.0
# Inner zone: near center — perfect. Between good and too-soon is good.
const PERFECT_RADIUS  := 20.0


func _process(_delta: float) -> void:
	if not GameManager.is_playing:
		return
	# Auto-miss notes that sat at center past the allowed window.
	for node in get_tree().get_nodes_in_group("notes"):
		var note := node as Note
		if note == null or note._expired:
			continue
		if note.get_timing_offset_ms() > GameManager.BAD_WINDOW_MS:
			note._expired = true
			GameManager.register_miss()
			note.queue_free()


func _input(event: InputEvent) -> void:
	if not GameManager.is_playing:
		return
	if event.is_action_pressed("move_up"):
		_try_hit(0)
	elif event.is_action_pressed("move_down"):
		_try_hit(1)
	elif event.is_action_pressed("move_left"):
		_try_hit(2)
	elif event.is_action_pressed("move_right"):
		_try_hit(3)


func _try_hit(direction: int) -> void:
	var center := get_viewport_rect().size / 2
	var best: Note = null
	var best_dist := INF

	for node in get_tree().get_nodes_in_group("notes"):
		var note := node as Note
		if note == null or note._expired or note.direction != direction:
			continue
		var dist := note.global_position.distance_to(center)
		# Only consider notes that are inside the visible circle.
		if dist < HIT_RADIUS and dist < best_dist:
			best_dist = dist
			best = note

	if best == null:
		return  # Nothing inside the circle for this direction — no penalty.

	best._expired = true

	var timing: String
	if best_dist >= TOO_SOON_RADIUS:
		timing = "Too Soon"
	elif best_dist >= PERFECT_RADIUS:
		timing = "Good"
	else:
		timing = "Perfect"

	GameManager.register_hit(timing)
	best.queue_free()
