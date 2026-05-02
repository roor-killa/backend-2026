extends Node

signal score_updated(new_score: int)
signal funds_updated(new_funds: float)
signal shields_updated(count: int)
signal hearts_updated(count: int)
signal shield_state_updated(state: String)
signal game_finished(won: bool, final_score: int, total_funds: float)
signal note_hit(timing: String)

# Only BAD_WINDOW_MS remains — used by hit_detector to auto-miss notes
# that sit at center without being hit.
const BAD_WINDOW_MS := 150
const MAX_HEARTS        := 3

var current_score: int       = 0
var funds_earned: float      = 0.0
var shields: int             = 0
var hearts: int              = MAX_HEARTS
var shield_active: bool      = false
var shield_broken: bool      = false
var shield_used_this_game: bool = false
var perfect_hits: int        = 0
var good_hits: int      = 0
var bad_hits: int       = 0
var misses: int         = 0
var combo: int          = 0
var is_playing: bool    = false


func start_game() -> void:
	current_score = 0
	funds_earned  = 0.0
	shields              = UserSession.shields_owned
	hearts               = MAX_HEARTS
	shield_active        = false
	shield_broken        = false
	shield_used_this_game = false
	perfect_hits         = 0
	good_hits     = 0
	bad_hits      = 0
	misses        = 0
	combo         = 0
	is_playing    = false
	emit_signal("shields_updated", shields)
	emit_signal("shield_state_updated", "empty")


func begin_play() -> void:
	is_playing = true


func activate_shield() -> bool:
	if shield_active:
		return false
	if shields <= 0:
		return false
	if shield_used_this_game:
		return false

	print("[GameManager] activate_shield() — before: shields=%d shield_active=%s shield_broken=%s" % [shields, str(shield_active), str(shield_broken)])

	shields -= 1
	UserSession.shields_owned = shields
	emit_signal("shields_updated", shields)
	shield_used_this_game = true
	shield_broken = false
	shield_active = true
	emit_signal("shield_state_updated", "filled")
	print("[GameManager] activate_shield() — after: shields=%d" % shields)
	return true


func activate_shield_from_server(new_shield_count: int) -> bool:
	if shield_active:
		return false
	if new_shield_count < 0:
		return false
	if shield_used_this_game:
		return false

	print("[GameManager] activate_shield_from_server(new_shield_count=%d)" % new_shield_count)

	shields = new_shield_count
	UserSession.shields_owned = shields
	emit_signal("shields_updated", shields)
	shield_used_this_game = true
	shield_broken = false
	shield_active = true
	emit_signal("shield_state_updated", "filled")
	print("[GameManager] activated from server, shields=%d" % shields)
	return true


func register_hit(timing: String) -> void:
	match timing:
		"Perfect":
			current_score += 100
			funds_earned  += 15.0
			combo         += 1
			perfect_hits  += 1
		"Good":
			current_score += 50
			funds_earned  += 10.0
			combo         += 1
			good_hits     += 1
		"Too Soon":
			current_score += 10
			funds_earned  += 5.0
			combo          = 0
			bad_hits      += 1

	emit_signal("score_updated", current_score)
	emit_signal("funds_updated", funds_earned)
	emit_signal("note_hit", timing)


func register_miss() -> void:
	if not is_playing:
		return
	combo = 0

	if shield_active:
		shield_active = false
		shield_broken = true
		emit_signal("shield_state_updated", "broken")
		emit_signal("note_hit", "Blocked")
		return

	misses += 1
	emit_signal("note_hit", "Miss")
	hearts -= 1
	emit_signal("hearts_updated", hearts)
	if hearts <= 0:
		finish_game(false)


func finish_game(won: bool) -> void:
	is_playing = false
	emit_signal("game_finished", won, current_score, funds_earned)
