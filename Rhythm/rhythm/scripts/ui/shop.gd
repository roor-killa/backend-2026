extends Control

const UIPolishScript = preload("res://scripts/ui/ui_polish.gd")

@onready var funds_label: Label = $VBox/FundsLabel
@onready var shields_label: Label = $VBox/ShieldsLabel
@onready var quantity_input: SpinBox = $VBox/QuantityInput
@onready var status_label: Label = $VBox/StatusLabel

var _pending_action: String = ""


func _ready() -> void:
	UIPolishScript.apply_screen_theme(self)
	UIPolishScript.add_soft_panel_behind($VBox)
	UIPolishScript.style_title($VBox/TitleLabel, 42)
	UIPolishScript.style_status_label(status_label)
	UIPolishScript.style_buttons([$VBox/BuyButton, $VBox/BackButton])
	quantity_input.custom_minimum_size = Vector2(0, 44)
	UIPolishScript.animate_scene_in(self)
	ApiClient.request_completed.connect(_on_api_response)
	_refresh_display()


func _refresh_display() -> void:
	funds_label.text = "Funds: %.2f" % UserSession.account_funds
	shields_label.text = "Shields: %d" % UserSession.shields_owned


func _on_buy_pressed() -> void:
	if not UserSession.is_logged_in:
		status_label.text = "Please log in first."
		return
	var qty = int(quantity_input.value)
	if qty <= 0:
		status_label.text = "Enter a valid quantity."
		return
	_pending_action = "purchase"
	status_label.text = "Purchasing %d shield(s)..." % qty
	status_label.modulate = Color.WHITE
	ApiClient.purchase_shields(UserSession.user_id, qty)


func _on_back_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _on_api_response(response_code: int, body: Dictionary) -> void:
	if _pending_action != "purchase":
		return

	_pending_action = ""
	if response_code == 200:
		UserSession.update_from_response(body)
		_refresh_display()
		status_label.text = "Purchase successful!"
		status_label.modulate = Color(0.4, 1.0, 0.4)
	else:
		status_label.text = body.get("detail", "Purchase failed.")
		status_label.modulate = Color(1.0, 0.4, 0.4)
