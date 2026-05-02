extends Node

const BASE_URL_DEV  = "http://127.0.0.1:8000"
const BASE_URL_PROD = "http://YOUR_VPS_IP:8000"   # replace before VPS test
var BASE_URL: String

signal request_completed(response_code: int, body: Dictionary)
signal request_completed_with_context(endpoint: String, response_code: int, body: Dictionary)


func _ready() -> void:
	BASE_URL = BASE_URL_DEV if OS.is_debug_build() else BASE_URL_PROD


func _make_request(method: int, endpoint: String, body: Dictionary = {}) -> void:
	var http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(_on_request_done.bind(http, endpoint))

	var headers = ["Content-Type: application/json"]
	var url = BASE_URL + endpoint
	var body_str = JSON.stringify(body) if method != HTTPClient.METHOD_GET else ""

	http.request(url, headers, method, body_str)


func _on_request_done(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray, http: HTTPRequest, endpoint: String) -> void:
	http.queue_free()
	var parsed = {}
	if body.size() > 0:
		var json = JSON.new()
		if json.parse(body.get_string_from_utf8()) == OK:
			parsed = json.get_data()
	emit_signal("request_completed", response_code, parsed)
	emit_signal("request_completed_with_context", endpoint, response_code, parsed)


func register(username: String, password: String) -> void:
	_make_request(HTTPClient.METHOD_POST, "/users/register", {"username": username, "password": password})


func login(username: String, password: String) -> void:
	_make_request(HTTPClient.METHOD_POST, "/users/login", {"username": username, "password": password})


func submit_score(user_id: String, score: int, funds_earned: float) -> void:
	_make_request(HTTPClient.METHOD_POST, "/scores", {"user_id": user_id, "score": score, "funds_earned": funds_earned})


func get_leaderboard(limit: int = 10) -> void:
	_make_request(HTTPClient.METHOD_GET, "/leaderboard?limit=" + str(limit))


func get_shop_items() -> void:
	_make_request(HTTPClient.METHOD_GET, "/shop/items")


func purchase_shields(user_id: String, quantity: int) -> void:
	_make_request(HTTPClient.METHOD_POST, "/shop/purchase", {"user_id": user_id, "item_type": "shield", "quantity": quantity})


func consume_shield(user_id: String) -> void:
	_make_request(HTTPClient.METHOD_POST, "/users/%s/shields/consume" % user_id)


func get_user(user_id: String) -> void:
	_make_request(HTTPClient.METHOD_GET, "/users/" + user_id)
