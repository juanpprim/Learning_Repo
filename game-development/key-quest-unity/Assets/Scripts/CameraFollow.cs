using UnityEngine;

// Smoothly follows the kid, clamped to the level bounds (same 2x-zoom view
// as the Godot edition: 576x324 px at PPU 32 -> half-extents 9 x 5.0625).
public class CameraFollow : MonoBehaviour
{
    const float SmoothSpeed = 6f;

    Transform target;
    float minX;
    float maxX;
    float minY;
    float maxY;

    public void Init(Transform followTarget, int levelWidth, int levelHeight)
    {
        target = followTarget;
        Camera cam = GetComponent<Camera>();
        float halfHeight = cam.orthographicSize;
        float halfWidth = halfHeight * cam.aspect;
        // Clamp inside the level; if the level is smaller than the view on
        // an axis, pin the camera so the level sits at the bottom-left.
        minX = Mathf.Min(halfWidth, levelWidth / 2f);
        maxX = Mathf.Max(levelWidth - halfWidth, minX);
        minY = Mathf.Min(halfHeight, levelHeight / 2f);
        maxY = Mathf.Max(levelHeight - halfHeight, minY);
        if (target != null)
        {
            transform.position = ClampedTarget();
        }
    }

    void LateUpdate()
    {
        if (target == null)
        {
            return;
        }
        transform.position = Vector3.Lerp(
            transform.position, ClampedTarget(), SmoothSpeed * Time.deltaTime);
    }

    Vector3 ClampedTarget()
    {
        return new Vector3(
            Mathf.Clamp(target.position.x, minX, maxX),
            Mathf.Clamp(target.position.y, minY, maxY),
            -10f);
    }
}
