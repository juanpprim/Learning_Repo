using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

// Icon-only HUD: one big key icon per key in the level, grey until
// collected. No text anywhere -- a 4-year-old reads it by color alone.
public class HudController : MonoBehaviour
{
    static readonly Color Grey = new Color(0.45f, 0.5f, 0.6f, 0.9f);

    readonly List<Image> icons = new List<Image>();

    public void Init(int total)
    {
        var canvas = gameObject.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        var scaler = gameObject.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1152, 648);

        Sprite iconSprite = Resources.Load<Sprite>("Sprites/hud_key");
        for (int i = 0; i < total; i++)
        {
            var slot = new GameObject("KeyIcon" + (i + 1));
            slot.transform.SetParent(transform, false);
            var image = slot.AddComponent<Image>();
            image.sprite = iconSprite;
            image.color = Grey;
            RectTransform rect = image.rectTransform;
            rect.anchorMin = new Vector2(0f, 1f);
            rect.anchorMax = new Vector2(0f, 1f);
            rect.pivot = new Vector2(0.5f, 0.5f);
            rect.sizeDelta = new Vector2(48f, 48f);
            rect.anchoredPosition = new Vector2(48f + i * 58f, -48f);
            icons.Add(image);
        }
        GameManager.Instance.KeyCollected += OnKeyCollected;
    }

    void OnKeyCollected(int collected, int total)
    {
        if (collected - 1 < icons.Count)
        {
            Image icon = icons[collected - 1];
            icon.color = Color.white;
            StartCoroutine(Pop(icon.rectTransform));
        }
    }

    IEnumerator Pop(RectTransform rect)
    {
        yield return Scale(rect, 1f, 1.35f, 0.12f);
        yield return Scale(rect, 1.35f, 1f, 0.15f);
    }

    static IEnumerator Scale(RectTransform rect, float from, float to, float duration)
    {
        for (float t = 0f; t < duration; t += Time.deltaTime)
        {
            rect.localScale = Vector3.one * Mathf.Lerp(from, to, t / duration);
            yield return null;
        }
        rect.localScale = Vector3.one * to;
    }
}
