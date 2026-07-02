using System.Collections;
using UnityEngine;

// Exit door: grey and inert until every key is collected, then it glows
// green, chimes, sparkles, and walking in loads the next level.
public class LevelExit : MonoBehaviour
{
    static readonly Color DoorGreen = new Color(0.239f, 1f, 0.545f);

    SpriteRenderer spriteRenderer;
    BoxCollider2D trigger;
    AudioSource audioSource;
    ParticleSystem sparkles;
    bool open;
    bool used;

    public void Init(Vector2 position)
    {
        transform.position = position;

        spriteRenderer = gameObject.AddComponent<SpriteRenderer>();
        spriteRenderer.sprite = Resources.Load<Sprite>("Sprites/door_closed");
        spriteRenderer.sortingOrder = 1;

        trigger = gameObject.AddComponent<BoxCollider2D>();
        trigger.isTrigger = true;
        trigger.size = new Vector2(0.9f, 1.9f);
        trigger.enabled = false;

        audioSource = gameObject.AddComponent<AudioSource>();
        sparkles = BuildSparkles();
        GameManager.Instance.AllKeysCollected += OnAllKeysCollected;
    }

    void OnAllKeysCollected()
    {
        open = true;
        spriteRenderer.sprite = Resources.Load<Sprite>("Sprites/door_open");
        audioSource.PlayOneShot(Resources.Load<AudioClip>("Audio/door"));
        sparkles.Play();
        trigger.enabled = true;
    }

    void OnTriggerEnter2D(Collider2D other)
    {
        if (!open || used)
        {
            return;
        }
        var player = other.GetComponent<PlayerController>();
        if (player == null)
        {
            return;
        }
        used = true;
        StartCoroutine(EnterRoutine(player));
    }

    IEnumerator EnterRoutine(PlayerController player)
    {
        player.SetControl(false);
        audioSource.PlayOneShot(Resources.Load<AudioClip>("Audio/win"));
        yield return new WaitForSeconds(1.2f);
        GameManager.Instance.NextLevel();
    }

    ParticleSystem BuildSparkles()
    {
        var holder = new GameObject("DoorSparkles");
        holder.transform.SetParent(transform);
        holder.transform.localPosition = Vector3.zero;
        var particles = holder.AddComponent<ParticleSystem>();
        ParticleSystem.MainModule main = particles.main;
        main.startLifetime = 0.8f;
        main.startSpeed = 0.8f;
        main.startSize = 0.1f;
        main.startColor = DoorGreen;
        main.gravityModifier = -0.05f;  // sparkles drift gently upward
        ParticleSystem.EmissionModule emission = particles.emission;
        emission.rateOverTime = 12f;
        ParticleSystem.ShapeModule shape = particles.shape;
        shape.shapeType = ParticleSystemShapeType.Box;
        shape.scale = new Vector3(0.8f, 1.8f, 1f);
        holder.GetComponent<ParticleSystemRenderer>().material =
            new Material(Shader.Find("Sprites/Default"));
        particles.Stop();
        return particles;
    }
}
