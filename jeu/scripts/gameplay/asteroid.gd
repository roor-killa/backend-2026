extends Node2D

signal reached_bottom(asteroid: Node2D)
signal destroyed(asteroid: Node2D)

@export var letter: String = "A"
@export var speed: float = 110.0

@onready var letter_label: Label = $LetterLabel


func _ready() -> void:
	letter = letter.to_upper()
	_configure_label()


func _process(delta: float) -> void:
	position.y += speed * delta
	if position.y > get_viewport_rect().size.y + 40.0:
		reached_bottom.emit(self)
		queue_free()


func set_letter(value: String) -> void:
	letter = value.to_upper()
	if is_node_ready():
		_configure_label()


func hit() -> void:
	destroyed.emit(self)
	queue_free()


func _configure_label() -> void:
	letter_label.text = letter
	letter_label.position = Vector2(-20, -16)
	letter_label.size = Vector2(40, 32)
	letter_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	letter_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER


func _draw() -> void:
	draw_circle(Vector2.ZERO, 24.0, Color(0.55, 0.55, 0.64, 1.0))
	draw_arc(Vector2.ZERO, 24.0, -0.6, 2.5, 20, Color(0.75, 0.75, 0.82, 0.75), 2.0)
