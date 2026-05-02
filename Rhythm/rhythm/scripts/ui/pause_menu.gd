extends Control

const UIPolishScript = preload("res://scripts/ui/ui_polish.gd")


func _ready() -> void:
	UIPolishScript.apply_screen_theme(self)
	UIPolishScript.add_soft_panel_behind($VBox)
	UIPolishScript.style_title($VBox/PausedLabel, 38)
	UIPolishScript.style_buttons([
		$VBox/ResumeButton,
		$VBox/RestartButton,
		$VBox/MainMenuButton,
		$VBox/QuitButton,
	])
	hide()
	process_mode = Node.PROCESS_MODE_ALWAYS


func _input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("ui_cancel"):
		hide_menu()


func show_menu() -> void:
	show()
	$VBox.modulate = Color(1.0, 1.0, 1.0, 0.0)
	var tween := create_tween()
	tween.tween_property($VBox, "modulate:a", 1.0, 0.18)
	$VBox/ResumeButton.grab_focus()
	get_tree().paused = true


func hide_menu() -> void:
	hide()
	get_tree().paused = false


func _on_resume_pressed() -> void:
	hide_menu()


func _on_restart_pressed() -> void:
	get_tree().paused = false
	get_tree().reload_current_scene()


func _on_main_menu_pressed() -> void:
	get_tree().paused = false
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _on_quit_pressed() -> void:
	get_tree().paused = false
	get_tree().change_scene_to_file("res://scenes/quit_dialog.tscn")
