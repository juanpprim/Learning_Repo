# Builds the current level entirely from its ASCII map (legend in levels.gd):
# tiles into a TileMapLayer, keys/elevators/door/player as scene instances,
# plus edge walls, a fall-respawn zone, background props, and camera limits.
extends Node2D

const TILE := 32
const VIEW_WIDTH := 576   # 1152x648 window at 2x zoom
const VIEW_HEIGHT := 324

const Levels := preload("res://scripts/levels.gd")

const PLAYER_SCENE := preload("res://scenes/Player.tscn")
const KEY_SCENE := preload("res://scenes/Key.tscn")
const DOOR_SCENE := preload("res://scenes/Door.tscn")
const ELEVATOR_SCENE := preload("res://scenes/Elevator.tscn")
const TILE_CIRCUIT := preload("res://assets/sprites/tile_circuit.png")
const TILE_CHIP := preload("res://assets/sprites/tile_chip.png")
const BG_SERVER := preload("res://assets/sprites/bg_server.png")
const BG_LED := preload("res://assets/sprites/bg_led.png")

var player: Node2D

@onready var camera: Camera2D = $Camera


func _ready() -> void:
	var rows := Levels.rows(GameState.level_index)
	var width := rows[0].length()
	var height := rows.size()
	GameState.register_keys(_count_keys(rows))
	_build_background(width, height)
	_build_tiles(rows)
	_spawn_entities(rows)
	_add_edge_walls(width, height)
	_add_fall_zone(width, height)
	_setup_camera(width, height)


func _process(_delta: float) -> void:
	if is_instance_valid(player):
		camera.global_position = player.global_position


func _count_keys(rows: PackedStringArray) -> int:
	var count := 0
	for row in rows:
		count += row.count("K")
	return count


func _build_tiles(rows: PackedStringArray) -> void:
	var tile_set := TileSet.new()
	tile_set.tile_size = Vector2i(TILE, TILE)
	tile_set.add_physics_layer()
	tile_set.add_source(_make_tile_source(TILE_CIRCUIT), 0)
	tile_set.add_source(_make_tile_source(TILE_CHIP), 1)
	var layer := TileMapLayer.new()
	layer.tile_set = tile_set
	layer.add_to_group("ground")
	add_child(layer)
	for y in rows.size():
		for x in rows[y].length():
			match rows[y][x]:
				"#":
					layer.set_cell(Vector2i(x, y), 0, Vector2i.ZERO)
				"=":
					layer.set_cell(Vector2i(x, y), 1, Vector2i.ZERO)


func _make_tile_source(texture: Texture2D) -> TileSetAtlasSource:
	var source := TileSetAtlasSource.new()
	source.texture = texture
	source.texture_region_size = Vector2i(TILE, TILE)
	source.create_tile(Vector2i.ZERO)
	var data := source.get_tile_data(Vector2i.ZERO, 0)
	data.add_collision_polygon(0)
	data.set_collision_polygon_points(0, 0, PackedVector2Array([
		Vector2(-16, -16), Vector2(16, -16), Vector2(16, 16), Vector2(-16, 16),
	]))
	return source


func _spawn_entities(rows: PackedStringArray) -> void:
	for y in rows.size():
		for x in rows[y].length():
			var center := Vector2(x * TILE + TILE / 2.0, y * TILE + TILE / 2.0)
			var cell_bottom := (y + 1) * TILE
			match rows[y][x]:
				"P":
					player = PLAYER_SCENE.instantiate()
					player.position = Vector2(center.x, cell_bottom - 24.0)
					add_child(player)
					GameState.set_respawn(player.position)
				"K":
					var key = KEY_SCENE.instantiate()
					key.position = center
					add_child(key)
				"D":
					# Door is 2 tiles tall, drawn upward from the D cell.
					var door = DOOR_SCENE.instantiate()
					door.position = Vector2(center.x, cell_bottom - 32.0)
					add_child(door)
				"E":
					add_child(_make_elevator(rows, x, y))


func _make_elevator(rows: PackedStringArray, x: int, y: int) -> Node2D:
	# The cab loops between the E cell and the topmost | above it; at the
	# top, the cab surface aligns with the adjacent platform surface.
	var top_row := y
	for row in range(y - 1, -1, -1):
		if rows[row][x] == "|":
			top_row = row
		else:
			break
	var elevator = ELEVATOR_SCENE.instantiate()
	var cab_x := x * TILE + TILE / 2.0
	elevator.set("bottom_position", Vector2(cab_x, y * TILE + TILE / 2.0))
	elevator.set("top_position", Vector2(cab_x, top_row * TILE + 8.0))
	return elevator


func _add_edge_walls(width: int, height: int) -> void:
	for x_pos: float in [-16.0, width * TILE + 16.0]:
		var wall := StaticBody2D.new()
		var shape := CollisionShape2D.new()
		var rect := RectangleShape2D.new()
		rect.size = Vector2(TILE, height * TILE * 3.0)
		shape.shape = rect
		wall.add_child(shape)
		wall.position = Vector2(x_pos, height * TILE / 2.0)
		add_child(wall)


func _add_fall_zone(width: int, height: int) -> void:
	var zone := Area2D.new()
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(width * TILE * 3.0, TILE)
	shape.shape = rect
	zone.add_child(shape)
	zone.position = Vector2(width * TILE / 2.0, height * TILE + 3.0 * TILE)
	zone.body_entered.connect(_on_fall_zone_entered)
	add_child(zone)


func _on_fall_zone_entered(body: Node2D) -> void:
	if body.has_method("respawn"):
		body.respawn()


func _build_background(width: int, height: int) -> void:
	var floor_top := (height - 1) * TILE
	for x in range(3, width - 2, 9):
		var server := Sprite2D.new()
		server.texture = BG_SERVER
		server.z_index = -10
		server.modulate = Color(0.8, 0.85, 1.0, 0.9)
		server.position = Vector2(x * TILE, floor_top - 48.0)
		add_child(server)
	var rng := RandomNumberGenerator.new()
	rng.seed = 20260702
	for x in range(1, width, 4):
		var led := Sprite2D.new()
		led.texture = BG_LED
		led.z_index = -9
		led.position = Vector2(
			x * TILE + rng.randf_range(0, TILE),
			rng.randf_range(TILE, floor_top - TILE * 2.0)
		)
		add_child(led)


func _setup_camera(width: int, height: int) -> void:
	camera.limit_left = 0
	camera.limit_right = maxi(width * TILE, VIEW_WIDTH)
	camera.limit_bottom = height * TILE
	camera.limit_top = mini(0, camera.limit_bottom - VIEW_HEIGHT)
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 6.0
