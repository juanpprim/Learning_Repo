# "You did it!" screen: confetti, a big happy kid, fanfare.
# Icon-only: a pulsing green arrow invites a replay; any key or click works.
extends Node2D

@onready var arrow: Polygon2D = $Arrow


func _ready() -> void:
	$Fanfare.play()
	var tween := create_tween().set_loops()
	tween.tween_property(arrow, "scale", Vector2(1.25, 1.25), 0.5) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_property(arrow, "scale", Vector2.ONE, 0.5) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


func _input(event: InputEvent) -> void:
	var pressed_key := event is InputEventKey and event.pressed
	var clicked := event is InputEventMouseButton and event.pressed
	if pressed_key or clicked:
		GameState.restart()
