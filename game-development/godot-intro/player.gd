# Reference GDScript snippet for a CharacterBody2D player node.
# Attach to a CharacterBody2D once you've created the Godot project in the editor.
extends CharacterBody2D

@export var speed: float = 300.0

func _physics_process(delta: float) -> void:
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	velocity = direction * speed
	move_and_slide()
