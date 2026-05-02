extends Control

const UIPolishScript = preload("res://scripts/ui/ui_polish.gd")


func _ready() -> void:
	UIPolishScript.apply_screen_theme(self)
	UIPolishScript.add_soft_panel_behind($VBox)
	UIPolishScript.style_title($VBox/TitleLabel, 54)
	UIPolishScript.style_status_label($VBox/StatusLabel)
	UIPolishScript.style_buttons([
		$VBox/StartButton,
		$VBox/LeaderboardButton,
		$VBox/ShopButton,
		$VBox/LogoutButton,
		$VBox/QuitButton,
	])
	$VBox/StatusLabel.text = "Welcome, %s" % (UserSession.username if UserSession.is_logged_in else "Guest")
	UIPolishScript.animate_scene_in(self)

func _on_start_pressed() -> void:
	if not UserSession.is_logged_in:
		get_tree().change_scene_to_file("res://scenes/login.tscn")
		return
	get_tree().change_scene_to_file("res://scenes/music_select.tscn")


func _on_leaderboard_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/leaderboard.tscn")


func _on_shop_pressed() -> void:
	if not UserSession.is_logged_in:
		get_tree().change_scene_to_file("res://scenes/login.tscn")
		return
	get_tree().change_scene_to_file("res://scenes/shop.tscn")


func _on_logout_pressed() -> void:
	UserSession.logout()
	get_tree().change_scene_to_file("res://scenes/login.tscn")


func _on_quit_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/quit_dialog.tscn")
