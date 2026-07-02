# Data-lift elevator: loops slowly between bottom and top, carrying the kid.
extends AnimatableBody2D

const PAUSE_TIME := 1.0

@export var speed := 48.0
@export var bottom_position := Vector2.ZERO
@export var top_position := Vector2.ZERO


func _ready() -> void:
	global_position = bottom_position
	var duration := bottom_position.distance_to(top_position) / speed
	var tween := create_tween().set_loops()
	tween.set_process_mode(Tween.TWEEN_PROCESS_PHYSICS)
	tween.tween_interval(PAUSE_TIME)
	tween.tween_property(self, "global_position", top_position, duration) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	tween.tween_interval(PAUSE_TIME)
	tween.tween_property(self, "global_position", bottom_position, duration) \
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
