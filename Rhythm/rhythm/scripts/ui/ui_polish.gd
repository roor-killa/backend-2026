extends RefCounted
class_name UIPolish

const BG_COLOR := Color(0.03, 0.06, 0.11, 0.78)
const BORDER_COLOR := Color(0.26, 0.86, 0.92, 0.42)
const TEXT_PRIMARY := Color(0.92, 0.98, 1.0, 1.0)
const TEXT_MUTED := Color(0.72, 0.84, 0.9, 1.0)


static func apply_screen_theme(root: Control) -> void:
	var theme := Theme.new()

	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(0.06, 0.11, 0.18, 0.96)
	normal.corner_radius_top_left = 12
	normal.corner_radius_top_right = 12
	normal.corner_radius_bottom_right = 12
	normal.corner_radius_bottom_left = 12
	normal.border_width_left = 2
	normal.border_width_top = 2
	normal.border_width_right = 2
	normal.border_width_bottom = 2
	normal.border_color = Color(0.18, 0.44, 0.62, 0.8)
	normal.content_margin_left = 14
	normal.content_margin_right = 14
	normal.content_margin_top = 10
	normal.content_margin_bottom = 10

	var hover := normal.duplicate()
	hover.bg_color = Color(0.1, 0.2, 0.3, 0.98)
	hover.border_color = Color(0.38, 0.95, 1.0, 0.95)

	var pressed := normal.duplicate()
	pressed.bg_color = Color(0.04, 0.08, 0.13, 0.98)
	pressed.border_color = Color(0.2, 0.72, 0.86, 0.95)

	theme.set_stylebox("normal", "Button", normal)
	theme.set_stylebox("hover", "Button", hover)
	theme.set_stylebox("pressed", "Button", pressed)
	theme.set_stylebox("focus", "Button", hover)
	theme.set_color("font_color", "Button", TEXT_PRIMARY)
	theme.set_color("font_hover_color", "Button", TEXT_PRIMARY)
	theme.set_color("font_pressed_color", "Button", TEXT_PRIMARY)
	theme.set_color("font_focus_color", "Button", TEXT_PRIMARY)
	theme.set_constant("outline_size", "Button", 0)
	theme.set_font_size("font_size", "Button", 18)

	theme.set_color("font_color", "Label", TEXT_PRIMARY)
	theme.set_color("font_color", "LineEdit", TEXT_PRIMARY)
	theme.set_color("font_placeholder_color", "LineEdit", TEXT_MUTED)

	var line_edit := StyleBoxFlat.new()
	line_edit.bg_color = Color(0.03, 0.07, 0.11, 0.92)
	line_edit.border_width_left = 2
	line_edit.border_width_top = 2
	line_edit.border_width_right = 2
	line_edit.border_width_bottom = 2
	line_edit.border_color = Color(0.2, 0.44, 0.58, 0.9)
	line_edit.corner_radius_top_left = 10
	line_edit.corner_radius_top_right = 10
	line_edit.corner_radius_bottom_right = 10
	line_edit.corner_radius_bottom_left = 10
	line_edit.content_margin_left = 10
	line_edit.content_margin_right = 10
	line_edit.content_margin_top = 8
	line_edit.content_margin_bottom = 8
	theme.set_stylebox("normal", "LineEdit", line_edit)
	theme.set_stylebox("focus", "LineEdit", hover)

	root.theme = theme


static func add_soft_panel_behind(target: Control) -> void:
	if target == null:
		return
	if target.get_parent() == null:
		return
	var panel := Panel.new()
	panel.name = "%sCard" % target.name
	panel.layout_mode = target.layout_mode
	panel.anchor_left = target.anchor_left
	panel.anchor_top = target.anchor_top
	panel.anchor_right = target.anchor_right
	panel.anchor_bottom = target.anchor_bottom
	panel.offset_left = target.offset_left - 18.0
	panel.offset_top = target.offset_top - 18.0
	panel.offset_right = target.offset_right + 18.0
	panel.offset_bottom = target.offset_bottom + 18.0
	panel.grow_horizontal = target.grow_horizontal
	panel.grow_vertical = target.grow_vertical
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE

	var style := StyleBoxFlat.new()
	style.bg_color = BG_COLOR
	style.corner_radius_top_left = 22
	style.corner_radius_top_right = 22
	style.corner_radius_bottom_right = 22
	style.corner_radius_bottom_left = 22
	style.border_width_left = 2
	style.border_width_top = 2
	style.border_width_right = 2
	style.border_width_bottom = 2
	style.border_color = BORDER_COLOR
	panel.add_theme_stylebox_override("panel", style)

	var parent := target.get_parent()
	parent.add_child(panel)
	parent.move_child(panel, target.get_index())


static func style_title(label: Label, size: int = 48) -> void:
	if label == null:
		return
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", Color(0.9, 0.98, 1.0, 1.0))


static func style_status_label(label: Label) -> void:
	if label == null:
		return
	label.add_theme_color_override("font_color", TEXT_MUTED)


static func style_buttons(buttons: Array[Button]) -> void:
	for button in buttons:
		if button == null:
			continue
		button.custom_minimum_size = Vector2(0, maxf(46.0, button.custom_minimum_size.y))


static func animate_scene_in(root: Control) -> void:
	if root == null:
		return
	root.modulate = Color(1.0, 1.0, 1.0, 0.0)
	var tween := root.create_tween()
	tween.set_ease(Tween.EASE_OUT)
	tween.set_trans(Tween.TRANS_QUART)
	tween.tween_property(root, "modulate:a", 1.0, 0.35)