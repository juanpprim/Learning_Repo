using UnityEngine;

// "You did it!" screen: confetti, a big happy kid, fanfare. Any key or
// click replays from Level 1; a pulsing green arrow invites it (icon-only).
public class Celebration : MonoBehaviour
{
    static readonly Color BgColor = new Color(14 / 255f, 23 / 255f, 38 / 255f);
    static readonly Color Green = new Color(0.239f, 1f, 0.545f);

    Transform arrow;

    void Start()
    {
        Camera cam = Camera.main;
        cam.orthographic = true;
        cam.orthographicSize = 5.0625f;
        cam.backgroundColor = BgColor;
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.transform.position = new Vector3(0f, 0f, -10f);

        BuildSprite("ServerLeft", "bg_server", new Vector2(-6.5f, -1.5f), 2f, -10);
        BuildSprite("ServerRight", "bg_server", new Vector2(6.5f, -1.5f), 2f, -10);
        BuildSprite("Kid", "kid_jump", new Vector2(0f, -0.5f), 5f, 10);
        arrow = BuildArrow();
        BuildConfetti();

        var audio = gameObject.AddComponent<AudioSource>();
        audio.PlayOneShot(Resources.Load<AudioClip>("Audio/win"));
    }

    void Update()
    {
        if (Input.anyKeyDown)  // covers keyboard and mouse buttons
        {
            GameManager.Instance.Restart();
        }
        if (arrow != null)
        {
            float pulse = 1f + 0.25f * Mathf.Sin(Time.time * 4f);
            arrow.localScale = new Vector3(pulse, pulse, 1f);
        }
    }

    static Transform BuildSprite(string name, string sprite, Vector2 pos, float scale, int order)
    {
        var holder = new GameObject(name);
        holder.transform.position = pos;
        holder.transform.localScale = Vector3.one * scale;
        var renderer = holder.AddComponent<SpriteRenderer>();
        renderer.sprite = Resources.Load<Sprite>("Sprites/" + sprite);
        renderer.sortingOrder = order;
        if (order < 0)
        {
            renderer.color = new Color(0.8f, 0.85f, 1f, 0.9f);
        }
        return holder.transform;
    }

    static Transform BuildArrow()
    {
        // Replay arrow: a right-pointing green triangle sprite built in code.
        var texture = new Texture2D(32, 32, TextureFormat.RGBA32, false);
        texture.filterMode = FilterMode.Point;
        for (int y = 0; y < 32; y++)
        {
            for (int x = 0; x < 32; x++)
            {
                bool inside = x >= 6 && x <= 26
                    && Mathf.Abs(y - 16) <= (26 - x) * 16f / 20f;
                texture.SetPixel(x, y, inside ? Green : Color.clear);
            }
        }
        texture.Apply();
        Sprite sprite = Sprite.Create(
            texture, new Rect(0, 0, 32, 32), new Vector2(0.5f, 0.5f), 32f);
        var holder = new GameObject("ReplayArrow");
        holder.transform.position = new Vector2(0f, -3.8f);
        var renderer = holder.AddComponent<SpriteRenderer>();
        renderer.sprite = sprite;
        renderer.sortingOrder = 20;
        return holder.transform;
    }

    static void BuildConfetti()
    {
        var holder = new GameObject("Confetti");
        holder.transform.position = new Vector3(0f, 6.5f);
        var particles = holder.AddComponent<ParticleSystem>();
        ParticleSystem.MainModule main = particles.main;
        main.startLifetime = 4f;
        main.startSpeed = 1.5f;
        main.startSize = 0.15f;
        main.gravityModifier = 0.3f;
        main.maxParticles = 300;
        main.startColor = new ParticleSystem.MinMaxGradient(
            new Color(1f, 0.83f, 0.28f), new Color(0.29f, 0.42f, 1f));
        ParticleSystem.EmissionModule emission = particles.emission;
        emission.rateOverTime = 40f;
        ParticleSystem.ShapeModule shape = particles.shape;
        shape.shapeType = ParticleSystemShapeType.Box;
        shape.scale = new Vector3(18f, 0.5f, 1f);
        holder.GetComponent<ParticleSystemRenderer>().material =
            new Material(Shader.Find("Sprites/Default"));
        particles.Play();
    }
}
