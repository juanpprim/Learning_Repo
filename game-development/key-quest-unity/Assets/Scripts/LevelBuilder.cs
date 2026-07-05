using UnityEngine;

// Builds the whole level at runtime from its ASCII map (legend in SPECS 2.5):
// tile sprites with merged row colliders, keys, elevators, the door, the
// player, invisible edge walls, a fall-respawn zone, background props, and
// the follow camera. Scenes stay nearly empty; 1 tile = 1 unit (PPU 32).
public class LevelBuilder : MonoBehaviour
{
    public int levelIndex = 1;

    static readonly Color BgColor = new Color(14 / 255f, 23 / 255f, 38 / 255f);

    Transform playerTransform;
    int width;
    int height;

    static Sprite Load(string name)
    {
        return Resources.Load<Sprite>("Sprites/" + name);
    }

    static bool IsSolid(char c)
    {
        return c == '#' || c == '=';
    }

    float WorldX(int x)
    {
        return x + 0.5f;
    }

    float WorldY(int y)
    {
        return height - 1 - y + 0.5f;  // map rows are top-down, Unity y is up
    }

    void Awake()
    {
        string[] rows = LoadRows();
        height = rows.Length;
        width = rows[0].Length;

        int keyCount = 0;
        foreach (string row in rows)
        {
            foreach (char c in row)
            {
                if (c == 'K')
                {
                    keyCount++;
                }
            }
        }
        GameManager.Instance.RegisterKeys(keyCount, levelIndex);

        BuildBackground();
        BuildTiles(rows);
        SpawnEntities(rows);
        AddEdgeWalls();
        AddFallZone();
        SetupCamera();
        BuildHud();
    }

    string[] LoadRows()
    {
        TextAsset map = Resources.Load<TextAsset>("Levels/level" + levelIndex);
        string[] rows = map.text.Trim('\n').Split('\n');
        for (int i = 0; i < rows.Length; i++)
        {
            rows[i] = rows[i].TrimEnd('\r');
        }
        return rows;
    }

    void BuildTiles(string[] rows)
    {
        Sprite circuit = Load("tile_circuit");
        Sprite chip = Load("tile_chip");
        var tiles = new GameObject("Tiles");
        for (int y = 0; y < height; y++)
        {
            int runStart = -1;
            for (int x = 0; x <= width; x++)
            {
                bool solid = x < width && IsSolid(rows[y][x]);
                if (solid)
                {
                    var cell = new GameObject("Tile");
                    cell.transform.SetParent(tiles.transform);
                    cell.transform.position = new Vector3(WorldX(x), WorldY(y));
                    var renderer = cell.AddComponent<SpriteRenderer>();
                    renderer.sprite = rows[y][x] == '#' ? circuit : chip;
                    if (runStart < 0)
                    {
                        runStart = x;
                    }
                }
                else if (runStart >= 0)
                {
                    // One merged collider per contiguous run of solid tiles.
                    var ground = new GameObject("Ground");
                    ground.transform.SetParent(tiles.transform);
                    ground.transform.position = new Vector3((runStart + x) / 2f, WorldY(y));
                    ground.AddComponent<BoxCollider2D>().size = new Vector2(x - runStart, 1f);
                    runStart = -1;
                }
            }
        }
    }

    void SpawnEntities(string[] rows)
    {
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                var center = new Vector2(WorldX(x), WorldY(y));
                float cellBottom = height - 1 - y;
                switch (rows[y][x])
                {
                    case 'P':
                        var player = new GameObject("Player").AddComponent<PlayerController>();
                        player.Init(new Vector2(center.x, cellBottom + 0.75f));
                        GameManager.Instance.RespawnPosition = player.transform.position;
                        playerTransform = player.transform;
                        break;
                    case 'K':
                        new GameObject("Key").AddComponent<KeyPickup>().Init(center);
                        break;
                    case 'D':
                        // Door is 2 tiles tall, drawn upward from the D cell.
                        new GameObject("Door").AddComponent<LevelExit>()
                            .Init(new Vector2(center.x, cellBottom + 1f));
                        break;
                    case 'E':
                        SpawnElevator(rows, x, y);
                        break;
                }
            }
        }
    }

    void SpawnElevator(string[] rows, int x, int y)
    {
        // The cab loops between the E cell and the topmost | above it; at
        // the top, the cab surface aligns with the adjacent platform top.
        int top = y;
        for (int yy = y - 1; yy >= 0 && rows[yy][x] == '|'; yy--)
        {
            top = yy;
        }
        float cx = WorldX(x);
        new GameObject("Elevator").AddComponent<ElevatorMover>().Init(
            new Vector2(cx, WorldY(y)),
            new Vector2(cx, height - top - 0.25f));
    }

    void AddEdgeWalls()
    {
        foreach (float x in new[] { -0.5f, width + 0.5f })
        {
            var wall = new GameObject("Wall");
            wall.transform.position = new Vector3(x, height / 2f);
            wall.AddComponent<BoxCollider2D>().size = new Vector2(1f, height * 3f);
        }
    }

    void AddFallZone()
    {
        var zone = new GameObject("FallZone");
        zone.transform.position = new Vector3(width / 2f, -3f);
        var box = zone.AddComponent<BoxCollider2D>();
        box.size = new Vector2(width * 3f, 1f);
        box.isTrigger = true;
        zone.AddComponent<FallZone>();
    }

    void BuildBackground()
    {
        Sprite server = Load("bg_server");
        Sprite led = Load("bg_led");
        var background = new GameObject("Background");
        for (int x = 3; x < width - 2; x += 9)
        {
            var rack = new GameObject("Server");
            rack.transform.SetParent(background.transform);
            rack.transform.position = new Vector3(x, 1f + 1.5f);  // on the floor
            var renderer = rack.AddComponent<SpriteRenderer>();
            renderer.sprite = server;
            renderer.sortingOrder = -10;
            renderer.color = new Color(0.8f, 0.85f, 1f, 0.9f);
        }
        var rng = new System.Random(20260702);
        for (int x = 1; x < width; x += 4)
        {
            var dot = new GameObject("Led");
            dot.transform.SetParent(background.transform);
            dot.transform.position = new Vector3(
                x + (float)rng.NextDouble(),
                2f + (float)rng.NextDouble() * Mathf.Max(1f, height - 4f));
            var renderer = dot.AddComponent<SpriteRenderer>();
            renderer.sprite = led;
            renderer.sortingOrder = -9;
        }
    }

    void SetupCamera()
    {
        Camera cam = GameCamera.GetOrCreate();
        cam.orthographic = true;
        cam.orthographicSize = 5.0625f;  // 324 px tall view at PPU 32
        cam.backgroundColor = BgColor;
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.gameObject.AddComponent<CameraFollow>().Init(playerTransform, width, height);
    }

    void BuildHud()
    {
        new GameObject("HUD").AddComponent<HudController>()
            .Init(GameManager.Instance.KeysTotal);
    }
}

// Trigger strip below the level: falling is never a fail, just a respawn.
class FallZone : MonoBehaviour
{
    void OnTriggerEnter2D(Collider2D other)
    {
        var player = other.GetComponent<PlayerController>();
        if (player != null)
        {
            player.Respawn();
        }
    }
}
