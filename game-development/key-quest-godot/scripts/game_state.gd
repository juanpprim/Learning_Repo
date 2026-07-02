# Autoload singleton: key progress, respawn point, and level flow.
extends Node

signal key_collected(collected: int, total: int)
signal all_keys_collected

const LEVEL_SCENE := "res://scenes/Level.tscn"
const CELEBRATION_SCENE := "res://scenes/Celebration.tscn"

var level_index := 0
var keys_total := 0
var keys_collected := 0
var respawn_position := Vector2.ZERO


func register_keys(total: int) -> void:
	keys_total = total
	keys_collected = 0


func collect_key() -> void:
	keys_collected += 1
	key_collected.emit(keys_collected, keys_total)
	if keys_collected >= keys_total:
		all_keys_collected.emit()


func set_respawn(pos: Vector2) -> void:
	respawn_position = pos


func next_level() -> void:
	level_index += 1
	if level_index >= Levels.MAPS.size():
		get_tree().change_scene_to_file(CELEBRATION_SCENE)
	else:
		get_tree().change_scene_to_file(LEVEL_SCENE)


func restart() -> void:
	level_index = 0
	get_tree().change_scene_to_file(LEVEL_SCENE)
