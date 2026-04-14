extends Node2D

const ASTEROID_SCENE := preload("res://scenes/gameplay/asteroid.tscn")

@onready var asteroids_root: Node2D = $Asteroids
@onready var cannon: Node2D = $Cannon
@onready var spawn_timer: Timer = $SpawnTimer
@onready var score_label: Label = $HUD/ScoreLabel
@onready var combo_label: Label = $HUD/ComboLabel
@onready var lives_label: Label = $HUD/LivesLabel
@onready var bpm_label: Label = $HUD/BpmLabel
@onready var message_label: Label = $HUD/MessageLabel

var score: int = 0
var combo: int = 0
var lives: int = 5
var bpm: float = 92.0
var elapsed: float = 0.0
var game_over: bool = false

var active_asteroids: Array[Node2D] = []
var letter_pool: String = "ETAOINSHRDLUCMFWYPVBGKQJXZ"


func _ready() -> void:
	randomize()
	_reset_run()


func _process(delta: float) -> void:
	if game_over:
		return

	elapsed += delta
	if int(elapsed) % 15 == 0 and elapsed > 1.0:
		# Slowly raise BPM to increase spawn pressure.
		bpm = min(160.0, bpm + delta * 2.0)
		spawn_timer.wait_time = 60.0 / bpm

	if message_label.modulate.a > 0.0:
		message_label.modulate.a = max(0.0, message_label.modulate.a - delta * 2.0)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if game_over and event.keycode == KEY_R:
			_reset_run()
			return

		var typed: String = _event_to_letter(event)
		if typed != "":
			_handle_letter(typed)


func _event_to_letter(event: InputEventKey) -> String:
	if event.unicode == 0:
		return ""

	var text := char(event.unicode).to_upper()
	if text.length() == 1 and text >= "A" and text <= "Z":
		return text
	return ""


func _handle_letter(letter: String) -> void:
	if game_over:
		return

	var target: Node2D = _find_target(letter)
	if target == null:
		combo = 0
		score = max(score - 8, 0)
		_show_message("MISS")
		_sync_state()
		_update_hud()
		return

	cannon.call("shoot_at", target.global_position)
	target.call("hit")

	combo += 1
	var bonus := min(combo * 2, 60)
	score += 100 + bonus
	_show_message("HIT +%d" % (100 + bonus))
	_sync_state()
	_update_hud()


func _find_target(letter: String) -> Node2D:
	var match: Node2D = null
	for asteroid in active_asteroids:
		if not is_instance_valid(asteroid):
			continue
		if asteroid.letter != letter:
			continue
		if match == null or asteroid.position.y > match.position.y:
			match = asteroid
	return match


func _on_spawn_timer_timeout() -> void:
	if game_over:
		return

	var asteroid: Node2D = ASTEROID_SCENE.instantiate()
	var width := get_viewport_rect().size.x
	var margin := 42.0
	asteroid.position = Vector2(randf_range(margin, width - margin), -30.0)
	asteroid.speed = 95.0 + elapsed * 1.6 + randf_range(0.0, 40.0)
	asteroid.set_letter(_pick_letter())
	asteroid.reached_bottom.connect(_on_asteroid_reached_bottom)
	asteroid.destroyed.connect(_on_asteroid_destroyed)
	active_asteroids.append(asteroid)
	asteroids_root.add_child(asteroid)


func _pick_letter() -> String:
	var index := randi() % letter_pool.length()
	return letter_pool.substr(index, 1)


func _on_asteroid_destroyed(asteroid: Node2D) -> void:
	active_asteroids.erase(asteroid)


func _on_asteroid_reached_bottom(asteroid: Node2D) -> void:
	active_asteroids.erase(asteroid)
	lives -= 1
	combo = 0
	_show_message("TOO LATE")
	_sync_state()
	_update_hud()

	if lives <= 0:
		_set_game_over()


func _set_game_over() -> void:
	game_over = true
	spawn_timer.stop()
	for asteroid in active_asteroids:
		if is_instance_valid(asteroid):
			asteroid.queue_free()
	active_asteroids.clear()
	message_label.text = "GAME OVER - Press R to restart"
	message_label.modulate.a = 1.0


func _reset_run() -> void:
	for asteroid in active_asteroids:
		if is_instance_valid(asteroid):
			asteroid.queue_free()
	active_asteroids.clear()

	score = 0
	combo = 0
	lives = 5
	elapsed = 0.0
	bpm = 92.0
	game_over = false
	spawn_timer.wait_time = 60.0 / bpm
	spawn_timer.start()
	message_label.text = "Type letters to shoot"
	message_label.modulate.a = 1.0
	_sync_state()
	_update_hud()


func _show_message(value: String) -> void:
	message_label.text = value
	message_label.modulate.a = 1.0


func _update_hud() -> void:
	score_label.text = "Score: %d" % score
	combo_label.text = "Combo: %d" % combo
	lives_label.text = "Lives: %d" % lives
	bpm_label.text = "BPM: %d" % int(round(bpm))


func _sync_state() -> void:
	if not has_node("/root/GameState"):
		return
	var state := get_node("/root/GameState")
	state.score = score
	state.combo = combo
	state.lives = lives
