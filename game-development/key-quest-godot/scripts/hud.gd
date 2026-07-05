# Icon-only HUD: one big key icon per key in the level, grey until collected.
# No text anywhere -- a 4-year-old reads it by color alone.
extends CanvasLayer

const ICON_TEXTURE := preload("res://assets/sprites/hud_key.png")
const GREY := Color(0.45, 0.5, 0.6, 0.9)

var icons: Array[TextureRect] = []

@onready var row: HBoxContainer = $Row


func _ready() -> void:
	GameState.key_collected.connect(_on_key_collected)
	# Deferred so the LevelBuilder has registered the key count first.
	_build_icons.call_deferred()


func _build_icons() -> void:
	for i in GameState.keys_total:
		var icon := TextureRect.new()
		icon.texture = ICON_TEXTURE
		icon.modulate = GREY
		icon.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
		icon.pivot_offset = Vector2(24, 24)
		row.add_child(icon)
		icons.append(icon)


func _on_key_collected(collected: int, _total: int) -> void:
	if collected - 1 >= icons.size():
		return
	var icon := icons[collected - 1]
	icon.modulate = Color.WHITE
	var tween := create_tween()
	tween.tween_property(icon, "scale", Vector2(1.35, 1.35), 0.12)
	tween.tween_property(icon, "scale", Vector2.ONE, 0.15)
