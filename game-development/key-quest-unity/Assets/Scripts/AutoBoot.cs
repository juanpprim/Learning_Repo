using UnityEngine;
using UnityEngine.SceneManagement;

// Safety net: build the game from code even if a scene's Bootstrap object is
// missing or its script reference broke on import. Runs automatically after
// every scene loads and, keyed off the scene name, ensures the right builder
// exists. If the scene already wired up its own builder, this does nothing --
// so it never double-builds a correctly-authored scene.
public static class AutoBoot
{
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void Boot()
    {
        string scene = SceneManager.GetActiveScene().name;

        if (scene == "Celebration")
        {
            if (Object.FindFirstObjectByType<Celebration>() == null)
            {
                new GameObject("Celebration").AddComponent<Celebration>();
            }
            return;
        }

        if (scene.StartsWith("Level")
            && Object.FindFirstObjectByType<LevelBuilder>() == null)
        {
            int index;
            if (!int.TryParse(scene.Substring("Level".Length), out index) || index < 1)
            {
                index = 1;
            }
            // Create the object inactive so levelIndex is set before Awake runs.
            var go = new GameObject("Bootstrap");
            go.SetActive(false);
            LevelBuilder builder = go.AddComponent<LevelBuilder>();
            builder.levelIndex = index;
            go.SetActive(true);
        }
    }
}
