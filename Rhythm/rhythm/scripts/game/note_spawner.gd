extends Node2D

const NOTE_SCENE = preload("res://scenes/note.tscn")

# Speed ramps from BASE to MAX over PLATEAU_TIME seconds, then holds.
const BASE_SPEED    := 300.0
const MAX_SPEED     := 550.0
const BASE_INTERVAL := 1.5
const MIN_INTERVAL  := 0.75
const PLATEAU_TIME  := 90.0

var _timer:   float = 0.0
var _elapsed: float = 0.0
var _directions := [0, 1, 2, 3]


func _process(delta: float) -> void:
	if not GameManager.is_playing:
		return

	_elapsed += delta

	var t := minf(_elapsed / PLATEAU_TIME, 1.0)
	var current_speed    := lerpf(BASE_SPEED, MAX_SPEED, t)
	var current_interval := lerpf(BASE_INTERVAL, MIN_INTERVAL, t)

	_timer += delta
	if _timer >= current_interval:
		_timer = 0.0
		_spawn_note(current_speed)


func _spawn_note(speed: float) -> void:
	var note := NOTE_SCENE.instantiate()
	var dir: int = _directions[randi() % _directions.size()]
	note.direction = dir
	note.speed = speed
	note.global_position = _get_spawn_position(dir)
	get_tree().current_scene.add_child(note)


func _get_spawn_position(dir: int) -> Vector2:
	var vp := get_viewport_rect().size
	match dir:
		0: return Vector2(vp.x / 2, -50)
		1: return Vector2(vp.x / 2, vp.y + 50)
		2: return Vector2(-50, vp.y / 2)
		3: return Vector2(vp.x + 50, vp.y / 2)
	return Vector2.ZERO
