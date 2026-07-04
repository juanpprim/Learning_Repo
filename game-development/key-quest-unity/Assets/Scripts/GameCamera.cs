using UnityEngine;

// Small helper: return the tagged Main Camera, creating one if the scene
// somehow has none (e.g. a scene that failed to author its camera). Keeps
// the game from crashing on a null Camera.main.
public static class GameCamera
{
    public static Camera GetOrCreate()
    {
        Camera cam = Camera.main;
        if (cam == null)
        {
            var go = new GameObject("Main Camera") { tag = "MainCamera" };
            cam = go.AddComponent<Camera>();
            go.AddComponent<AudioListener>();
        }
        return cam;
    }
}
