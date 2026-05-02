extends Control

const BINDINGS_PATH := "user://keybindings.cfg"

const DEFAULT_KEYS := {
	"move_up":    KEY_UP,
	"move_down":  KEY_DOWN,
	"move_left":  KEY_LEFT,
	"move_right": KEY_RIGHT,
}

const DIR_LABELS := {
	"move_up":    "Up",
	"move_down":  "Down",
	"move_left":  "Left",
	"move_right": "Right",
}

var _waiting_for: String = ""
var _key_labels: Dictionary = {}
var _change_btns: Dictionary = {}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_build_ui()


func _build_ui() -> void:
	var overlay := ColorRect.new()
	overlay.color = Color(0, 0, 0, 0.88)
	overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(overlay)

	var panel := PanelContainer.new()
	panel.anchor_left   = 0.5
	panel.anchor_top    = 0.5
	panel.anchor_right  = 0.5
	panel.anchor_bottom = 0.5
	panel.offset_left   = -210.0
	panel.offset_top    = -200.0
	panel.offset_right  =  210.0
	panel.offset_bottom =  200.0
	add_child(panel)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 10)
	panel.add_child(vbox)

	var title := Label.new()
	title.text = "REBIND KEYS"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 26)
	vbox.add_child(title)

	vbox.add_child(HSeparator.new())

	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 16)
	grid.add_theme_constant_override("v_separation", 10)
	vbox.add_child(grid)

	for action in ["move_up", "move_down", "move_left", "move_right"]:
		var dir_lbl := Label.new()
		dir_lbl.text = DIR_LABELS[action]
		dir_lbl.custom_minimum_size = Vector2(55, 0)
		grid.add_child(dir_lbl)

		var key_lbl := Label.new()
		key_lbl.text = _get_key_name(action)
		key_lbl.custom_minimum_size = Vector2(120, 0)
		_key_labels[action] = key_lbl
		grid.add_child(key_lbl)

		var btn := Button.new()
		btn.text = "Change"
		btn.custom_minimum_size = Vector2(80, 32)
		btn.pressed.connect(_on_change_pressed.bind(action))
		_change_btns[action] = btn
		grid.add_child(btn)

	vbox.add_child(HSeparator.new())

	var reset_btn := Button.new()
	reset_btn.text = "Reset to Defaults"
	reset_btn.pressed.connect(_on_reset_pressed)
	vbox.add_child(reset_btn)

	var back_btn := Button.new()
	back_btn.text = "Back"
	back_btn.pressed.connect(_on_back_pressed)
	vbox.add_child(back_btn)


func _input(event: InputEvent) -> void:
	if not (event is InputEventKey) or not event.pressed or event.echo:
		return
	var key_ev := event as InputEventKey

	# ESC cancels current rebind, or closes the screen if idle.
	if key_ev.keycode == KEY_ESCAPE:
		if _waiting_for != "":
			_cancel_rebind()
		else:
			_on_back_pressed()
		get_viewport().set_input_as_handled()
		return

	if _waiting_for == "":
		return

	_apply_binding(_waiting_for, key_ev.keycode)
	_waiting_for = ""
	_update_labels()
	_set_btns_disabled(false)
	_save_bindings()
	get_viewport().set_input_as_handled()


func _on_change_pressed(action: String) -> void:
	_waiting_for = action
	_key_labels[action].text = "Press any key…"
	_set_btns_disabled(true)


func _on_reset_pressed() -> void:
	for action in DEFAULT_KEYS:
		_apply_binding(action, DEFAULT_KEYS[action])
	_update_labels()
	_save_bindings()


func _on_back_pressed() -> void:
	queue_free()


func _cancel_rebind() -> void:
	_waiting_for = ""
	_update_labels()
	_set_btns_disabled(false)


func _apply_binding(action: String, keycode: int) -> void:
	InputMap.action_erase_events(action)
	var ev := InputEventKey.new()
	ev.keycode = keycode
	InputMap.action_add_event(action, ev)


func _update_labels() -> void:
	for action in _key_labels:
		_key_labels[action].text = _get_key_name(action)


func _set_btns_disabled(disabled: bool) -> void:
	for action in _change_btns:
		_change_btns[action].disabled = disabled


func _get_key_name(action: String) -> String:
	var events := InputMap.action_get_events(action)
	if events.is_empty():
		return "None"
	var ev := events[0]
	if ev is InputEventKey:
		var key_ev := ev as InputEventKey
		if key_ev.keycode != KEY_NONE:
			return OS.get_keycode_string(key_ev.keycode)
		if key_ev.physical_keycode != KEY_NONE:
			return OS.get_keycode_string(key_ev.physical_keycode)
	return ev.as_text()


func _save_bindings() -> void:
	var config := ConfigFile.new()
	for action in DEFAULT_KEYS:
		var events := InputMap.action_get_events(action)
		if events.size() > 0 and events[0] is InputEventKey:
			config.set_value("bindings", action, (events[0] as InputEventKey).keycode)
	config.save(BINDINGS_PATH)
