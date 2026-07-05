using System.Collections;
using UnityEngine;

// Kid player: run, generous jump with coyote time, gentle respawn.
// Same numbers as the Godot edition: 180 px/s, 3.55-tile jump, 0.15 s coyote.
public class PlayerController : MonoBehaviour
{
    const float Speed = 5.625f;         // 180 px/s at 32 ppu
    const float JumpVelocity = 15.625f; // 500 px/s
    const float Gravity = 34.375f;      // 1100 px/s^2
    const float CoyoteTime = 0.15f;

    Rigidbody2D body;
    SpriteRenderer spriteRenderer;
    AudioSource audioSource;
    AudioClip jumpClip;
    AudioClip boopClip;
    Sprite idleSprite;
    Sprite jumpSprite;
    Sprite[] runSprites;

    float moveInput;
    bool jumpRequested;
    bool grounded;
    Collider2D groundCollider;
    float coyoteTimer;
    bool controlEnabled = true;
    float runFrameTimer;
    int runFrame;

    public void Init(Vector2 position)
    {
        transform.position = position;

        idleSprite = Resources.Load<Sprite>("Sprites/kid_idle");
        jumpSprite = Resources.Load<Sprite>("Sprites/kid_jump");
        runSprites = new[]
        {
            Resources.Load<Sprite>("Sprites/kid_run_1"),
            Resources.Load<Sprite>("Sprites/kid_run_2"),
        };
        jumpClip = Resources.Load<AudioClip>("Audio/jump");
        boopClip = Resources.Load<AudioClip>("Audio/boop");

        spriteRenderer = gameObject.AddComponent<SpriteRenderer>();
        spriteRenderer.sprite = idleSprite;
        spriteRenderer.sortingOrder = 10;

        body = gameObject.AddComponent<Rigidbody2D>();
        body.freezeRotation = true;
        body.gravityScale = Gravity / Mathf.Abs(Physics2D.gravity.y);
        body.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
        body.interpolation = RigidbodyInterpolation2D.Interpolate;

        gameObject.AddComponent<BoxCollider2D>().size = new Vector2(0.7f, 1.45f);
        audioSource = gameObject.AddComponent<AudioSource>();
    }

    void Update()
    {
        moveInput = controlEnabled ? Input.GetAxisRaw("Horizontal") : 0f;
        bool jumpDown = Input.GetKeyDown(KeyCode.Space)
            || Input.GetKeyDown(KeyCode.W)
            || Input.GetKeyDown(KeyCode.UpArrow);
        if (controlEnabled && jumpDown)
        {
            jumpRequested = true;
        }
        UpdateAnimation();
    }

    void FixedUpdate()
    {
        CheckGround();
        if (grounded)
        {
            coyoteTimer = CoyoteTime;
            UpdateRespawnPoint();
        }
        else
        {
            coyoteTimer = Mathf.Max(0f, coyoteTimer - Time.fixedDeltaTime);
        }

        body.velocity = new Vector2(moveInput * Speed, body.velocity.y);

        if (jumpRequested && coyoteTimer > 0f)
        {
            body.velocity = new Vector2(body.velocity.x, JumpVelocity);
            coyoteTimer = 0f;
            audioSource.PlayOneShot(jumpClip);
        }
        jumpRequested = false;
    }

    void CheckGround()
    {
        var feet = (Vector2)transform.position + Vector2.down * 0.78f;
        groundCollider = Physics2D.OverlapBox(feet, new Vector2(0.6f, 0.1f), 0f);
        grounded = groundCollider != null;
    }

    void UpdateRespawnPoint()
    {
        // Only remember spots on real ground, not on a moving elevator.
        if (groundCollider != null && groundCollider.GetComponent<ElevatorMover>() == null)
        {
            GameManager.Instance.RespawnPosition = transform.position;
        }
    }

    public void Respawn()
    {
        if (controlEnabled)
        {
            StartCoroutine(RespawnRoutine());
        }
    }

    public void SetControl(bool enabled)
    {
        controlEnabled = enabled;
    }

    IEnumerator RespawnRoutine()
    {
        controlEnabled = false;
        body.velocity = Vector2.zero;
        audioSource.PlayOneShot(boopClip);
        yield return Fade(1f, 0f, 0.15f);
        transform.position = GameManager.Instance.RespawnPosition;
        body.velocity = Vector2.zero;
        yield return Fade(0f, 1f, 0.2f);
        controlEnabled = true;
    }

    IEnumerator Fade(float from, float to, float duration)
    {
        for (float t = 0f; t < duration; t += Time.deltaTime)
        {
            SetAlpha(Mathf.Lerp(from, to, t / duration));
            yield return null;
        }
        SetAlpha(to);
    }

    void SetAlpha(float alpha)
    {
        Color c = spriteRenderer.color;
        c.a = alpha;
        spriteRenderer.color = c;
    }

    void UpdateAnimation()
    {
        if (moveInput != 0f)
        {
            spriteRenderer.flipX = moveInput < 0f;
        }
        if (!grounded)
        {
            spriteRenderer.sprite = jumpSprite;
        }
        else if (moveInput != 0f)
        {
            runFrameTimer += Time.deltaTime;
            if (runFrameTimer >= 1f / 6f)  // 6 fps run cycle, same as Godot
            {
                runFrameTimer = 0f;
                runFrame = 1 - runFrame;
            }
            spriteRenderer.sprite = runSprites[runFrame];
        }
        else
        {
            spriteRenderer.sprite = idleSprite;
        }
    }
}
