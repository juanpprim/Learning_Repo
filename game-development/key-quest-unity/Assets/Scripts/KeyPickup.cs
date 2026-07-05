using UnityEngine;

// Golden key: spins and bobs in place; on touch it sparkles, plays the
// rising arpeggio, counts in the GameManager, and disappears.
public class KeyPickup : MonoBehaviour
{
    static readonly Color Gold = new Color(1f, 0.831f, 0.278f);

    Sprite[] frames;
    SpriteRenderer spriteRenderer;
    float frameTimer;
    int frame;
    float bobPhase;
    Vector2 basePosition;
    bool collected;

    public void Init(Vector2 position)
    {
        basePosition = position;
        transform.position = position;
        frames = new Sprite[4];
        for (int i = 0; i < 4; i++)
        {
            frames[i] = Resources.Load<Sprite>("Sprites/key_" + (i + 1));
        }
        spriteRenderer = gameObject.AddComponent<SpriteRenderer>();
        spriteRenderer.sprite = frames[0];
        spriteRenderer.sortingOrder = 5;
        var circle = gameObject.AddComponent<CircleCollider2D>();
        circle.isTrigger = true;
        circle.radius = 0.45f;
        bobPhase = position.x;  // desync neighboring keys
    }

    void Update()
    {
        frameTimer += Time.deltaTime;
        if (frameTimer >= 1f / 8f)  // 8 fps spin, same as Godot
        {
            frameTimer = 0f;
            frame = (frame + 1) % frames.Length;
            spriteRenderer.sprite = frames[frame];
        }
        float bob = Mathf.Sin(Time.time * 2f + bobPhase) * 0.08f;
        transform.position = basePosition + Vector2.up * bob;
    }

    void OnTriggerEnter2D(Collider2D other)
    {
        if (collected || other.GetComponent<PlayerController>() == null)
        {
            return;
        }
        collected = true;
        AudioSource.PlayClipAtPoint(
            Resources.Load<AudioClip>("Audio/key"), transform.position, 0.9f);
        SpawnSparkles();
        GameManager.Instance.CollectKey();
        Destroy(gameObject);
    }

    void SpawnSparkles()
    {
        var burst = new GameObject("Sparkles");
        burst.transform.position = transform.position;
        var particles = burst.AddComponent<ParticleSystem>();
        ParticleSystem.MainModule main = particles.main;
        main.startLifetime = 0.45f;
        main.startSpeed = 3f;
        main.startSize = 0.12f;
        main.startColor = Gold;
        main.gravityModifier = 0f;
        ParticleSystem.EmissionModule emission = particles.emission;
        emission.enabled = false;
        var renderer = burst.GetComponent<ParticleSystemRenderer>();
        renderer.material = new Material(Shader.Find("Sprites/Default"));
        particles.Emit(14);
        Destroy(burst, 1f);
    }
}
