extends Node2D

var flash_timer: float = 0.0
var flash_target: Vector2 = Vector2.ZERO


func _process(delta: float) -> void:
	if flash_timer > 0.0:
		flash_timer = max(0.0, flash_timer - delta)
		queue_redraw()


func shoot_at(global_target: Vector2) -> void:
	flash_target = to_local(global_target)
	flash_timer = 0.08
	queue_redraw()


func _draw() -> void:
	# Base
	draw_circle(Vector2.ZERO, 30.0, Color(0.16, 0.19, 0.28, 1.0))
	draw_circle(Vector2.ZERO, 20.0, Color(0.27, 0.33, 0.46, 1.0))

	# Barrel
	draw_rect(Rect2(-7.0, -46.0, 14.0, 34.0), Color(0.80, 0.83, 0.92, 1.0))

	# Muzzle flash line
	if flash_timer > 0.0:
		draw_line(Vector2(0.0, -30.0), flash_target, Color(1.0, 0.82, 0.3, 0.9), 3.0)
