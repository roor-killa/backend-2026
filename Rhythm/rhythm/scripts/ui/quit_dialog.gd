extends Control

const UIPolishScript = preload("res://scripts/ui/ui_polish.gd")


func _ready() -> void:
	UIPolishScript.apply_screen_theme(self)
	UIPolishScript.add_soft_panel_behind($VBox)
	UIPolishScript.style_title($VBox/ConfirmLabel, 28)
	UIPolishScript.style_buttons([$VBox/YesButton, $VBox/NoButton])
	UIPolishScript.animate_scene_in(self)
	$VBox/NoButton.grab_focus()


func _on_yes_pressed() -> void:
	get_tree().quit()


func _on_no_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
