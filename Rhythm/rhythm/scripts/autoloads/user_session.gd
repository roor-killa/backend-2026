extends Node

const BINDINGS_PATH := "user://keybindings.cfg"
const DEFAULT_MUSIC_TITLE := "ILYBB"
const DEFAULT_MUSIC_PATH := "res://assets/music/Ailow, Dionysus - ILYBB [NCS Release].mp3"

var user_id: String = ""
var username: String = ""
var account_funds: float = 0.0
var shields_owned: int = 0
var selected_music_title: String = DEFAULT_MUSIC_TITLE
var selected_music_path: String = DEFAULT_MUSIC_PATH
var is_logged_in: bool = false


func _ready() -> void:
	_load_key_bindings()


func _load_key_bindings() -> void:
	var config := ConfigFile.new()
	if config.load(BINDINGS_PATH) != OK:
		return
	for action in ["move_up", "move_down", "move_left", "move_right"]:
		var keycode: int = config.get_value("bindings", action, 0)
		if keycode <= 0:
			continue
		InputMap.action_erase_events(action)
		var ev := InputEventKey.new()
		ev.keycode = keycode
		InputMap.action_add_event(action, ev)


func login(data: Dictionary) -> void:
	user_id = data.get("id", "")
	username = data.get("username", "")
	account_funds = data.get("account_funds", 0.0)
	shields_owned = data.get("shields_owned", 0)
	is_logged_in = true


func logout() -> void:
	user_id = ""
	username = ""
	account_funds = 0.0
	shields_owned = 0
	is_logged_in = false


func update_from_response(data: Dictionary) -> void:
	account_funds = data.get("account_funds", account_funds)
	shields_owned = data.get("shields_owned", shields_owned)
	account_funds = data.get("new_balance", account_funds)
	shields_owned = data.get("new_shield_count", shields_owned)


func select_music(title: String, path: String) -> void:
	selected_music_title = title
	selected_music_path = path
