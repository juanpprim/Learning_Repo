# Entry point: hands off to GameState, which loads the current level.
extends Node


func _ready() -> void:
	GameState.restart.call_deferred()
