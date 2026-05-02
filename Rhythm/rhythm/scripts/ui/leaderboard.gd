extends Control

const UIPolishScript = preload("res://scripts/ui/ui_polish.gd")

@onready var entries_container: VBoxContainer = $ScrollContainer/EntriesContainer
@onready var status_label: Label = $StatusLabel


func _ready() -> void:
	UIPolishScript.apply_screen_theme(self)
	UIPolishScript.add_soft_panel_behind($ScrollContainer)
	UIPolishScript.style_title($TitleLabel, 40)
	UIPolishScript.style_status_label(status_label)
	UIPolishScript.style_buttons([$BackButton])
	UIPolishScript.animate_scene_in(self)
	ApiClient.request_completed.connect(_on_api_response)
	ApiClient.get_leaderboard(10)
	status_label.text = "Loading..."


func _on_back_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _on_api_response(response_code: int, body: Variant) -> void:
	status_label.hide()
	if response_code != 200:
		status_label.show()
		status_label.text = "Failed to load leaderboard."
		return

	for child in entries_container.get_children():
		child.queue_free()

	if body is Array:
		for i in body.size():
			var entry = body[i]
			var row := PanelContainer.new()
			row.custom_minimum_size = Vector2(0, 44)
			var row_style := StyleBoxFlat.new()
			row_style.bg_color = Color(0.07, 0.14, 0.21, 0.82) if i % 2 == 0 else Color(0.05, 0.1, 0.17, 0.78)
			row_style.corner_radius_top_left = 10
			row_style.corner_radius_top_right = 10
			row_style.corner_radius_bottom_right = 10
			row_style.corner_radius_bottom_left = 10
			row_style.content_margin_left = 12
			row_style.content_margin_right = 12
			row_style.content_margin_top = 8
			row_style.content_margin_bottom = 8
			row.add_theme_stylebox_override("panel", row_style)

			var line := HBoxContainer.new()
			line.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			line.add_theme_constant_override("separation", 10)

			var rank := Label.new()
			rank.custom_minimum_size = Vector2(42, 0)
			rank.text = "%d" % (i + 1)
			rank.add_theme_color_override("font_color", Color(1.0, 0.86, 0.45, 1.0))

			var user := Label.new()
			user.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			user.text = entry.get("username", "?")

			var score := Label.new()
			score.text = str(entry.get("score", 0))
			score.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
			score.add_theme_color_override("font_color", Color(0.74, 1.0, 0.9, 1.0))

			line.add_child(rank)
			line.add_child(user)
			line.add_child(score)
			row.add_child(line)
			entries_container.add_child(row)
