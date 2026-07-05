# Golden key pickup: spins in place; on touch it sparkles, sounds, and counts.
extends Area2D

@onready var sprite: AnimatedSprite2D = $Sprite
@onready var collision: CollisionShape2D = $Collision
@onready var pickup_sound: AudioStreamPlayer = $PickupSound
@onready var sparkles: CPUParticles2D = $Sparkles


func _on_body_entered(body: Node2D) -> void:
	if not body.is_in_group("player"):
		return
	collision.set_deferred("disabled", true)
	sprite.visible = false
	sparkles.emitting = true
	pickup_sound.play()
	GameState.collect_key()
	await pickup_sound.finished
	queue_free()
