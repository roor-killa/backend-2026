extends Control

const UIPolishScript = preload("res://scripts/ui/ui_polish.gd")

@onready var username_input: LineEdit = $VBox/UsernameInput
@onready var password_input: LineEdit = $VBox/PasswordInput
@onready var status_label: Label = $VBox/StatusLabel
@onready var login_button: Button = $VBox/HBoxAuth/LoginButton
@onready var register_button: Button = $VBox/HBoxAuth/RegisterButton
@onready var quit_button: Button = $VBox/QuitButton

var _pending_action: String = ""


func _ready() -> void:
	UIPolishScript.apply_screen_theme(self)
	UIPolishScript.add_soft_panel_behind($VBox)
	UIPolishScript.style_title($VBox/TitleLabel, 52)
	UIPolishScript.style_status_label(status_label)
	UIPolishScript.style_buttons([login_button, register_button, quit_button])
	UIPolishScript.animate_scene_in(self)
	username_input.grab_focus()
	ApiClient.request_completed.connect(_on_api_response)


func _on_login_pressed() -> void:
	var user := username_input.text.strip_edges()
	var pass_ := password_input.text
	if user.is_empty() or pass_.is_empty():
		_set_status("Please enter a username and password.", false)
		return
	_set_status("Logging in...", true)
	_set_auth_buttons(false)
	_pending_action = "login"
	ApiClient.login(user, pass_)


func _on_register_pressed() -> void:
	var user := username_input.text.strip_edges()
	var pass_ := password_input.text
	if user.is_empty() or pass_.is_empty():
		_set_status("Please enter a username and password.", false)
		return
	_set_status("Creating account...", true)
	_set_auth_buttons(false)
	_pending_action = "register"
	ApiClient.register(user, pass_)


func _on_api_response(response_code: int, body: Dictionary) -> void:
	_set_auth_buttons(true)

	if response_code == 0:
		_set_status("Cannot reach the server. Is it running?", false)
		_pending_action = ""
		return

	match _pending_action:
		"login":
			match response_code:
				200:
					UserSession.login(body)
					get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
					password_input.text = ""
				401:
					_set_status("Incorrect username or password.", false)
				404:
					_set_status("No account found with that username.", false)
				422:
					_set_status("Please enter a valid username and password.", false)
				_:
					_set_status(body.get("detail", "Login failed (error %d)." % response_code), false)

		"register":
			match response_code:
				201:
					UserSession.login(body)
					get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
					password_input.text = ""
				409:
					_set_status("That username is already taken.", false)
				422:
					_set_status("Please enter a valid username and password.", false)
				_:
					_set_status(body.get("detail", "Registration failed (error %d)." % response_code), false)

	_pending_action = ""


func _set_status(message: String, success: bool) -> void:
	status_label.text = message
	status_label.modulate = Color(0.4, 1.0, 0.4) if success else Color(1.0, 0.4, 0.4)


func _on_quit_pressed() -> void:
	get_tree().quit()


func _set_auth_buttons(enabled: bool) -> void:
	login_button.disabled = not enabled
	register_button.disabled = not enabled