using System.Collections.Generic;
using UnityEngine;

// Data-lift elevator: kinematic cab looping between bottom and top with a
// sine ease and a 1 s pause at each end (48 px/s, same as Godot). Riders
// are carried by applying the cab's movement delta to their rigidbody --
// the 2D-physics-safe equivalent of parenting.
public class ElevatorMover : MonoBehaviour
{
    const float Speed = 1.5f;  // 48 px/s at 32 ppu
    const float Pause = 1f;

    readonly List<Rigidbody2D> riders = new List<Rigidbody2D>();

    Vector2 bottomPos;
    Vector2 topPos;
    Rigidbody2D body;
    float travelTime;
    float clock;

    public void Init(Vector2 bottom, Vector2 top)
    {
        bottomPos = bottom;
        topPos = top;
        transform.position = bottom;

        var renderer = gameObject.AddComponent<SpriteRenderer>();
        renderer.sprite = Resources.Load<Sprite>("Sprites/elevator");
        renderer.sortingOrder = 4;

        body = gameObject.AddComponent<Rigidbody2D>();
        body.bodyType = RigidbodyType2D.Kinematic;

        gameObject.AddComponent<BoxCollider2D>().size = new Vector2(3f, 0.5f);
        travelTime = Vector2.Distance(bottom, top) / Speed;
    }

    void FixedUpdate()
    {
        clock = (clock + Time.fixedDeltaTime) % (2f * (travelTime + Pause));
        Vector2 target = PositionAt(clock);
        Vector2 delta = target - body.position;
        foreach (Rigidbody2D rider in riders)
        {
            if (rider != null)
            {
                rider.position += delta;
            }
        }
        body.MovePosition(target);
    }

    Vector2 PositionAt(float t)
    {
        if (t < travelTime)
        {
            return Eased(t / travelTime, bottomPos, topPos);
        }
        t -= travelTime;
        if (t < Pause)
        {
            return topPos;
        }
        t -= Pause;
        return t < travelTime ? Eased(t / travelTime, topPos, bottomPos) : bottomPos;
    }

    static Vector2 Eased(float progress, Vector2 from, Vector2 to)
    {
        return Vector2.Lerp(from, to, 0.5f - 0.5f * Mathf.Cos(progress * Mathf.PI));
    }

    void OnCollisionEnter2D(Collision2D collision)
    {
        Rigidbody2D rb = collision.rigidbody;
        bool standingOnTop = collision.transform.position.y > transform.position.y + 0.3f;
        if (rb != null && standingOnTop && !riders.Contains(rb)
            && collision.gameObject.GetComponent<PlayerController>() != null)
        {
            riders.Add(rb);
        }
    }

    void OnCollisionExit2D(Collision2D collision)
    {
        if (collision.rigidbody != null)
        {
            riders.Remove(collision.rigidbody);
        }
    }
}
