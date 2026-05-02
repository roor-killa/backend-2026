extends Area2D
class_name Note

enum Direction { UP, DOWN, LEFT, RIGHT }

var direction: Direction = Direction.UP
var speed: float = 300.0
var _expected_arrival_ms: int = 0
var _expired: bool = false

@onready var sprite: ColorRect = $ColorRect


func _ready() -> void:
	add_to_group("notes")
	var center := get_viewport_rect().size / 2
	var dist := global_position.distance_to(center)
	_expected_arrival_ms = Time.get_ticks_msec() + int((dist / speed) * 1000.0)
	_set_color()


func _process(delta: float) -> void:
	var center := get_viewport_rect().size / 2
	var to_center := center - global_position
	var dist := to_center.length()
	if dist > speed * delta:
		global_position += to_center.normalized() * speed * delta
	else:
		global_position = center


func _set_color() -> void:
	if not sprite:
		return
	match direction:
		Direction.UP:    sprite.color = Color.RED
		Direction.DOWN:  sprite.color = Color.BLUE
		Direction.LEFT:  sprite.color = Color.GREEN
		Direction.RIGHT: sprite.color = Color.YELLOW


# Negative = player is early, positive = player is late, 0 = perfect.
func get_timing_offset_ms() -> int:
	return Time.get_ticks_msec() - _expected_arrival_ms
