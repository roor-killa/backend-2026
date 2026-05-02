# Rhythm Game — Asset List

Game resolution: **1280 × 720 px**

---

## Visual Assets

### Gameplay

---

**Note — Up** `note_up.png` | 30 × 30 px | PNG (RGBA) | Needed

A small red square sprite that spawns at the top edge of the screen and travels downward toward the center circle. Replaces the current red `ColorRect` placeholder used in `note.gd`. The player must press Up or W when this note reaches the red quadrant of the circle.

---

**Note — Down** `note_down.png` | 30 × 30 px | PNG (RGBA) | Needed

A small blue square sprite that spawns at the bottom screen edge and travels upward. Replaces the blue `ColorRect` placeholder. The player must press Down or S when it reaches the blue quadrant.

---

**Note — Left** `note_left.png` | 30 × 30 px | PNG (RGBA) | Needed

A small green square sprite that spawns at the left screen edge and travels rightward. Replaces the green `ColorRect` placeholder. The player must press Left or A when it reaches the green quadrant.

---

**Note — Right** `note_right.png` | 30 × 30 px | PNG (RGBA) | Needed

A small yellow square sprite that spawns at the right screen edge and travels leftward. Replaces the yellow `ColorRect` placeholder. The player must press Right or D when it reaches the yellow quadrant.

---

**Center Circle** `center_circle.png` | 200 × 200 px | PNG (RGBA) | Needed

The main gameplay target rendered at the exact center of the 1280×720 viewport. Divided into four colored quadrants (red = up, blue = down, green = left, yellow = right) with white divider lines and a white border ring. Currently drawn procedurally in `circle_visual.gd` using `draw_colored_polygon`; this sprite would replace or supplement that drawing. The active hit radius is 80 px, so the image includes a small transparent padding border.

---

**Circle Hit Flash — Up** `hit_flash_up.png` | 200 × 200 px | PNG (RGBA) | Needed

A bright, oversaturated red quadrant overlay that flashes over the center circle when the player hits an Up note. Provides instant visual feedback indicating which sector was activated. Displayed briefly (around 100–150 ms) then fades out.

---

**Circle Hit Flash — Down** `hit_flash_down.png` | 200 × 200 px | PNG (RGBA) | Needed

Same as the Up flash but in bright blue. Shown when a Down note is successfully hit.

---

**Circle Hit Flash — Left** `hit_flash_left.png` | 200 × 200 px | PNG (RGBA) | Needed

Same structure as the other hit flashes but in bright green. Shown when a Left note is successfully hit.

---

**Circle Hit Flash — Right** `hit_flash_right.png` | 200 × 200 px | PNG (RGBA) | Needed

Same structure as the other hit flashes but in bright yellow. Shown when a Right note is successfully hit.

---

**Hit Particle Effect** `hit_particles.png` | 64 × 64 px | PNG (RGBA) | Needed

A single small glowing dot or spark used as the particle texture in a `GPUParticles2D` node. Multiple copies are emitted in a burst when a Perfect or Good hit is registered, exploding outward from the circle center in the hit direction's color. Keeping it a simple circle or star shape lets the particle system handle the variety.

---

**Miss Effect** `miss_particles.png` | 64 × 64 px | PNG (RGBA) | Needed

A darker, muted grey or desaturated particle sprite used when a note is missed. Emitted as a small downward scatter from the center circle to signal failure without being too visually loud, since the player needs to keep focus on the next incoming note.

---

**Game Background** `game_background.png` | 1280 × 720 px | PNG (RGB) | Needed

A full-screen static background for the gameplay scene. Should be dark (close to the current `#0D0D1A` navy used by the placeholder `ColorRect`) so that the colored notes and center circle stand out clearly. Subtle geometric shapes, grid lines, or soft glow effects add visual interest without competing with gameplay elements. No alpha channel needed as it covers the full viewport.

---

### HUD (In-Game Overlay)

---

**Shield Icon** `shield_icon.png` | 32 × 32 px | PNG (RGBA) | Existing (`heart.png`)

A small icon displayed next to the shield count label in the top-left HUD. The existing `heart.png` is a stand-in; ideally replaced with an actual shield shape to match the game mechanic (shields absorb missed notes, not lives). Shown inline with the "Shields: N" label at 18 px font size.

---

**HUD Panel Background** `hud_panel.png` | 220 × 90 px | PNG (RGBA) | Needed

A semi-transparent dark panel that sits behind the three top-left HUD labels (Score, Funds, Shields) in `game.tscn`. Improves readability of white text against the potentially busy game background. Should have slightly rounded corners and around 60–70% opacity.

---

**Timing Label — Perfect** *(text only, no sprite)* | Font colour `#FFD700` | 36 px | —

The word "Perfect" displayed in the center of the screen via `TimingLabel` in the HUD. Gold/yellow color to signal the highest hit quality. Appears for roughly 500 ms after a hit within the ±50 ms window and then fades.

---

**Timing Label — Good** *(text only, no sprite)* | Font colour `#00CFFF` | 36 px | —

The word "Good" displayed in the same center label position. Cyan/light-blue color for a hit within the ±100 ms window. Slightly less prominent than Perfect to reflect the lower reward (50 points vs 100).

---

**Timing Label — Bad** *(text only, no sprite)* | Font colour `#FF8C00` | 36 px | —

The word "Bad" displayed center-screen. Orange color for a hit within the ±150 ms window. Earns minimal points (10) and resets the combo, so the orange signals a warning without being as alarming as a miss.

---

**Timing Label — Miss** *(text only, no sprite)* | Font colour `#FF3333` | 36 px | —

The word "Miss" displayed center-screen in red. Appears when no input is registered before the note passes the circle entirely, or when input is outside the ±150 ms window. If the player has shields, one is consumed; otherwise the game ends.

---

### Menus

---

**Menu Background** `menu_background.png` | 1280 × 720 px | PNG (RGB) | Existing (`background.png`)

The full-screen background used across all menu scenes (Main Menu, Leaderboard, Shop, Pause). The existing `background.png` fills this role. Verify it is sized at or above 1280×720 so it covers the viewport without stretching artifacts. Used as a `TextureRect` in stretch mode.

---

**Game Logo / Title** `game_title.png` | 512 × 128 px | PNG (RGBA) | Existing (`game titre.png`)

The "RHYTHM" game title graphic shown at the top of the Main Menu. The existing `game titre.png` is the placeholder. Confirm legibility when rendered at the display size defined by the `TitleLabel` node (48 px font, centered). If the image is bitmap text it should be crisp at that size; otherwise the label font below handles the text rendering and this asset may not be needed.

---

**Button — Normal** `button_normal.png` | 320 × 52 px | PNG (RGBA) | Needed

The default (unpressed, unhovered) state of all menu buttons across Main Menu, Pause Menu, Leaderboard, and Shop scenes. Flat design with rounded corners and a dark navy base matching the overall color palette. This image is assigned to the `StyleBoxTexture` normal state in a shared Godot Theme resource so all buttons stay visually consistent.

---

**Button — Hover** `button_hover.png` | 320 × 52 px | PNG (RGBA) | Needed

The button state when the mouse cursor is over it. Should be a slightly lighter or softly glowing version of the normal state to give clear visual feedback that the button is interactive. Assigned to the `StyleBoxTexture` hover state in the shared Theme.

---

**Button — Pressed** `button_pressed.png` | 320 × 52 px | PNG (RGBA) | Needed

The button state when it is being clicked. Slightly darker or inset compared to the normal state to simulate a physical press. Displayed for the brief moment between mouse-down and mouse-up. Assigned to the `StyleBoxTexture` pressed state in the shared Theme.

---

**Start Button** `start.png` | — | PNG (RGBA) | Existing

An existing decorative or icon-style start asset. May be used as an icon alongside the "Start Game" button text, or as a standalone clickable graphic. Review whether it should replace the text button or sit beside it in the `VBox` layout of `main_menu.tscn`.

---

**Quit Button** `quit.png` | — | PNG (RGBA) | Existing

An existing decorative or icon-style quit asset. Same consideration as `start.png` — decide whether it replaces the text "Quit" button or augments it. Currently the Quit button in `main_menu.tscn` and `quit_dialog.tscn` is a plain text `Button` node.

---

**Options / Settings Icon** `options.png` | — | PNG (RGBA) | Existing

An existing settings or gear icon. Not currently wired to any scene — reserved for a future Settings or Options menu. When implemented, it would appear as a small icon button on the Main Menu.

---

**Score Display Graphic** `scrore.png` | — | PNG (RGBA) | Existing

An existing score-related graphic. Note the filename has a typo (`scrore` instead of `score`) — rename to `score_display.png` before integrating into the HUD or end-game summary screen. Intended to frame or accompany the final score shown after gameplay ends.

---

**Left Hit Indicator** `left hit.png` | — | PNG (RGBA) | Existing

An existing graphic indicating the left direction. Could be used as a lane marker near the left screen edge where Left notes spawn, or as a visual arrow on the center circle's left quadrant to help new players learn the controls.

---

**Right Hit Indicator** `right hit.png` | — | PNG (RGBA) | Existing

Same purpose as `left hit.png` but for the right direction. Should be mirrored horizontally from the left indicator for visual consistency.

---

**Pause Menu Overlay** `pause_overlay.png` | 1280 × 720 px | PNG (RGBA) | Needed

A full-screen semi-transparent dark layer (approximately 60% opacity black) that dims the gameplay scene when the Pause Menu is open. It signals to the player that the game is paused while still allowing the game state to be visible in the background. Assigned to a `ColorRect` or `TextureRect` behind the pause menu buttons in `pause_menu.tscn`.

---

**Leaderboard Row Background** `leaderboard_row.png` | 600 × 48 px | PNG (RGBA) | Needed

A subtle background strip used for each row in the leaderboard table displayed in `leaderboard.tscn`. Alternating slightly different opacities (e.g. 20% white vs 10% white) between odd and even rows make the list easier to scan. Displays rank, username, and score side by side.

---

**Shop Item Card** `shop_card.png` | 300 × 120 px | PNG (RGBA) | Needed

A card-style panel background used to frame the shield item listing in `shop.tscn`. Contains the item icon, name, description ("Protects against one missed note"), and price (100 funds). A visible card helps the shop feel like a proper store rather than a plain label list.

---

**Shield Item Icon (Shop)** `shield_item.png` | 64 × 64 px | PNG (RGBA) | Needed

A larger, more detailed version of the HUD shield icon used inside the shop item card. Since it appears at 64 px instead of 32 px, it can show more detail — for example a glowing shield outline or a subtle highlight. Clearly communicates what the player is purchasing.

---

**Quit Confirmation Dialog Panel** `dialog_panel.png` | 480 × 200 px | PNG (RGBA) | Needed

The background panel for the quit confirmation dialog in `quit_dialog.tscn`. Contains the question "Are you sure you want to quit?" and two buttons (Yes / No). A dedicated panel graphic grounds it visually as a modal dialog, separate from the rest of the UI layer behind it.

---

### Fonts

---

**Primary UI Font** `font_main.ttf` | TTF / OTF | Needed

Used for all `Label` and `Button` text throughout the game. A clean, geometric sans-serif works well for a rhythm game — suggestions: Orbitron, Rajdhani, or Exo 2 (all free under OFL/Apache licences, available on Google Fonts). The same font file serves every scene at the sizes already defined in the `.tscn` files: 18 px (funds/shields), 22 px (score label, quit dialog), 32 px (leaderboard and pause titles), 36 px (shop title, timing feedback), 48 px (main menu title).

---

**Score / Number Font** `font_numbers.ttf` | TTF / OTF | Needed

Used specifically for the score counter and any numeric readouts. A monospaced or digital-display-style typeface (e.g. Share Tech Mono, DS-Digital, or Press Start 2P) ensures the score digits don't shift layout as numbers change width. Displayed at 36 px in the `TimingLabel` and potentially on the end-game summary.

---

## Audio Assets

All music files should have a clean loop point set. Godot natively imports `.ogg`, `.wav`, and `.mp3`; `.ogg` is preferred for music (good compression, seamless looping) and `.wav` for short SFX (minimal decode latency ensures tight hit feedback).

---

### Music

---

**Main Menu Theme** `music_menu.ogg` | OGG Vorbis | 2–3 min loop | Needed

Background music that plays on the Main Menu, Leaderboard, and Shop screens. Should feel energetic but relaxed enough to sit in the background during navigation — an upbeat electronic or synthwave track around 120–140 BPM works well. Loop point should be set so it restarts imperceptibly when the player stays on the menu for a long time.

---

**Gameplay Track** `music_gameplay.ogg` | OGG Vorbis | 2–4 min loop | Needed

The main in-game background track that plays during a round. Should be a driving rhythm or EDM style that complements the note-hitting action without distracting from the timing sounds. Ideally the BPM aligns with the note spawn interval so the notes feel musically timed. Has a seamless loop point so longer play sessions don't cut to silence.

---

**Game Over Sting** `music_game_over.ogg` | OGG Vorbis | 3–5 sec one-shot | Needed

A short descending musical phrase or tone that plays the moment the game ends (i.e. the player runs out of shields and a note is missed). Plays over or immediately after the gameplay track cuts out. Should clearly signal failure — a descending tone, a sad chord, or a deflating sound effect.

---

**Victory / High Score Jingle** `music_highscore.ogg` | OGG Vorbis | 3–5 sec one-shot | Needed

A short triumphant musical phrase that plays when the player achieves a new personal best score. Optional for MVP but adds satisfying polish. Plays on the score submission screen or leaderboard if the submitted score ranks in the top entries.

---

### Sound Effects

---

**Hit — Perfect** `sfx_hit_perfect.wav` | WAV 44100 Hz 16-bit | < 200 ms | Needed

A crisp, satisfying click or high-pitched chime that fires when a note is hit within the ±50 ms window. This is the most rewarding sound in the game and should feel noticeably better than Good or Bad. Played every time `register_hit()` in `game_manager.gd` returns "Perfect".

---

**Hit — Good** `sfx_hit_good.wav` | WAV 44100 Hz 16-bit | < 200 ms | Needed

A softer, slightly muted version of the Perfect hit sound. Still positive but clearly distinguishable from Perfect so the player can hear the quality difference without looking at the timing label. Fires for hits within the ±100 ms window.

---

**Hit — Bad** `sfx_hit_bad.wav` | WAV 44100 Hz 16-bit | < 300 ms | Needed

A dull thud or flat tone signaling a late or early hit within the ±150 ms window. Earns only 10 points and resets the combo, so the sound should feel noticeably worse than Good — something like a hollow knock or a flat beep.

---

**Miss / Note Lost** `sfx_miss.wav` | WAV 44100 Hz 16-bit | < 400 ms | Needed

A low buzz, error tone, or discordant sound that plays when a note fully exits the hit window without a matching input. If the player has shields remaining, one is consumed and the game continues. If not, the game ends. This sound is distinct from the game over sting — it signals a single failure event, not the end of the run.

---

**Shield Break** `sfx_shield_break.wav` | WAV 44100 Hz 16-bit | < 500 ms | Needed

A shattering, cracking, or crackling sound that plays specifically when a shield absorbs a missed note. Differentiates a shielded miss from a regular miss so the player understands their protection was consumed. Important feedback because the shield count in the HUD updates simultaneously and the player needs to register the loss.

---

**Shield Purchased** `sfx_shield_buy.wav` | WAV 44100 Hz 16-bit | < 400 ms | Needed

A coin drop, cash register, or positive chime that plays in `shop.tscn` after a successful shield purchase. Confirms the transaction went through and funds were deducted. The HUD balance and shield count update at the same moment.

---

**Button Click** `sfx_button_click.wav` | WAV 44100 Hz 16-bit | < 150 ms | Needed

A subtle, clean UI click sound that plays on every button press across all menu scenes (Main Menu, Pause, Leaderboard, Shop, Quit Dialog). Should be short and unobtrusive — this sound plays frequently and mustn't draw attention away from the music. A short tick, tap, or soft pop works well.

---

**Button Hover** `sfx_button_hover.wav` | WAV 44100 Hz 16-bit | < 100 ms | Needed

A very quiet, brief tick that fires when the mouse cursor enters a button's area. Gives the UI a tactile feel without becoming annoying. Should be noticeably quieter than the click sound. Can be omitted for keyboard/controller navigation if needed.

---

**Note Spawn** `sfx_note_spawn.wav` | WAV 44100 Hz 16-bit | < 150 ms | Needed

An optional very soft whoosh or tick that plays each time a new note enters the screen. Helps the player hear the rhythm of incoming notes alongside seeing them. If playtesting finds it distracting or clashes with the gameplay music, this can be disabled or removed without affecting core feedback.

---

**Game Over SFX** `sfx_game_over.wav` | WAV 44100 Hz 16-bit | < 1 sec | Needed

A short, punchy sound effect that plays the instant the game ends — the moment `_end_game()` fires in `game_manager.gd`. Distinct from the longer Game Over Sting music; this is the immediate impact sound (a buzzer, a loud thud, a power-down) while the sting fades in underneath it.

---

## Existing Assets Summary

| File | Location | Current Role |
|------|----------|--------------|
| `background.png` | `assets/` | Menu background — covers all menu scenes |
| `game titre.png` | `assets/` | Game title / logo on Main Menu |
| `heart.png` | `assets/` | Shield counter icon stand-in (replace with shield shape) |
| `left hit.png` | `assets/` | Left direction indicator — role TBD |
| `right hit.png` | `assets/` | Right direction indicator — role TBD |
| `options.png` | `assets/` | Reserved for future Settings menu |
| `quit.png` | `assets/` | Quit button graphic |
| `start.png` | `assets/` | Start button graphic |
| `scrore.png` | `assets/` | Score display graphic — rename to `score_display.png` |

---

## AI Generation Prompts

Use these prompts with an image-generation tool for the assets still needed:

**Notes (4 directions)**
> "Simple geometric square game sprite, flat design, glowing edges, [red/blue/green/yellow] color, dark background, 30×30 pixel art style, transparent background"

**Center Circle**
> "Circular HUD target divided into 4 equal quadrants, minimalist rhythm game UI, flat design, red/blue/green/yellow quadrant colors at 50% opacity, white divider lines and border ring, dark background, transparent background, top-down view"

**Game Background**
> "Abstract geometric background pattern, dark navy theme, subtle grid lines and hexagons, music rhythm game aesthetic, 1280×720, no text"

**Button Set**
> "Modern video game UI button, flat design, rounded corners, dark navy base, subtle glow outline, suitable for rhythm game, three states: normal/hover/pressed"

**Shield Icon**
> "Simple shield icon, flat design, white outline on transparent background, game UI style, 32×32"

**Particle Effect**
> "Small glowing spark or dot, white to yellow gradient, transparent background, 64×64, for use as a game particle texture"

**Shop Item Card**
> "Game UI item card panel, dark background, subtle border glow, flat design, 300×120, no text, for rhythm game shop"
