using System;
using UnityEngine;
using UnityEngine.SceneManagement;

// Singleton game state: key progress, respawn point, and level flow.
// Created lazily by LevelBuilder so any scene can be played directly.
public class GameManager : MonoBehaviour
{
    const int LevelCount = 3;

    static GameManager instance;

    public static GameManager Instance
    {
        get
        {
            if (instance == null)
            {
                instance = new GameObject("GameManager").AddComponent<GameManager>();
            }
            return instance;
        }
    }

    public event Action<int, int> KeyCollected;
    public event Action AllKeysCollected;

    public int KeysTotal { get; private set; }
    public int KeysCollected { get; private set; }
    public Vector2 RespawnPosition { get; set; }

    int levelIndex = 1;

    void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }
        instance = this;
        DontDestroyOnLoad(gameObject);
    }

    // Called by LevelBuilder at scene start; also drops subscribers from
    // the previous scene so events never target destroyed objects.
    public void RegisterKeys(int total, int currentLevel)
    {
        KeysTotal = total;
        KeysCollected = 0;
        levelIndex = currentLevel;
        KeyCollected = null;
        AllKeysCollected = null;
    }

    public void CollectKey()
    {
        KeysCollected++;
        KeyCollected?.Invoke(KeysCollected, KeysTotal);
        if (KeysCollected >= KeysTotal)
        {
            AllKeysCollected?.Invoke();
        }
    }

    public void NextLevel()
    {
        levelIndex++;
        SceneManager.LoadScene(levelIndex <= LevelCount ? "Level" + levelIndex : "Celebration");
    }

    public void Restart()
    {
        levelIndex = 1;
        SceneManager.LoadScene("Level1");
    }
}
