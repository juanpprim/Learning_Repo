# Exit door: grey and inert until every key is collected, then it glows
# green, sparkles, and walking in loads the next level.
extends Area2D

const OPEN_TEXTURE := preload("res://assets/sprites/door_open.png")

var is_open := false
var used := false

@onready var sprite: Sprite2D = $Sprite
@onready var open_sound: AudioStreamPlayer = $OpenSound
@onready var fanfare: AudioStreamPlayer = $Fanfare
@onready var sparkles: CPUParticles2D = $Sparkles


func _ready() -> void:
	GameState.all_keys_collected.connect(_on_all_keys_collected)


func _on_all_keys_collected() -> void:
	is_open = true
	sprite.texture = OPEN_TEXTURE
	open_sound.play()
	sparkles.emitting = true


func _on_body_entered(body: Node2D) -> void:
	if not is_open or used or not body.is_in_group("player"):
		return
	used = true
	if body.has_method("set_control"):
		body.set_control(false)
	fanfare.play()
	var tween := create_tween()
	tween.tween_property(body, "modulate:a", 0.0, 0.6)
	tween.tween_interval(0.5)
	tween.tween_callback(GameState.next_level)
