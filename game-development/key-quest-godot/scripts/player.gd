# Kid player: run, generous jump with coyote time, gentle respawn.
extends CharacterBody2D

const COYOTE_TIME := 0.15

@export var speed := 180.0
@export var jump_velocity := -500.0

var coyote_timer := 0.0
var control_enabled := true

@onready var gravity: float = ProjectSettings.get_setting("physics/2d/default_gravity")
@onready var sprite: AnimatedSprite2D = $Sprite
@onready var jump_sound: AudioStreamPlayer = $JumpSound
@onready var boop_sound: AudioStreamPlayer = $BoopSound


func _physics_process(delta: float) -> void:
	if is_on_floor():
		coyote_timer = COYOTE_TIME
		_update_respawn_point()
	else:
		velocity.y += gravity * delta
		coyote_timer = maxf(coyote_timer - delta, 0.0)

	var direction := 0.0
	if control_enabled:
		direction = Input.get_axis("move_left", "move_right")
	velocity.x = direction * speed

	if control_enabled and Input.is_action_just_pressed("jump") and coyote_timer > 0.0:
		velocity.y = jump_velocity
		coyote_timer = 0.0
		jump_sound.play()

	move_and_slide()
	_update_animation(direction)


func respawn() -> void:
	if not control_enabled:
		return
	control_enabled = false
	velocity = Vector2.ZERO
	boop_sound.play()
	var tween := create_tween()
	tween.tween_property(sprite, "modulate:a", 0.0, 0.15)
	tween.tween_callback(_teleport_home)
	tween.tween_property(sprite, "modulate:a", 1.0, 0.2)
	tween.tween_callback(func() -> void: control_enabled = true)


func set_control(enabled: bool) -> void:
	control_enabled = enabled


func _teleport_home() -> void:
	global_position = GameState.respawn_position
	velocity = Vector2.ZERO


func _update_respawn_point() -> void:
	for i in get_slide_collision_count():
		var collider: Object = get_slide_collision(i).get_collider()
		if collider is Node and (collider as Node).is_in_group("ground"):
			GameState.set_respawn(global_position)
			return


func _update_animation(direction: float) -> void:
	if direction != 0.0:
		sprite.flip_h = direction < 0.0
	if not is_on_floor():
		sprite.play("jump")
	elif direction != 0.0:
		sprite.play("run")
	else:
		sprite.play("idle")
