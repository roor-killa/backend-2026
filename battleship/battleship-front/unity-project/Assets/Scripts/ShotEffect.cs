using UnityEngine;

public class ShotEffect : MonoBehaviour
{
    [SerializeField] private ParticleSystem hitEffect;
    [SerializeField] private ParticleSystem missEffect;
    [SerializeField] private float cellSize = 1f;

    public void PlayShotResult(int row, int col, string result)
    {
        Vector3 position = new Vector3(col * cellSize, 0.05f, row * cellSize);

        if (result == "hit" || result == "sunk")
        {
            SpawnEffect(hitEffect, position);
            return;
        }

        SpawnEffect(missEffect, position);
    }

    private static void SpawnEffect(ParticleSystem effectPrefab, Vector3 position)
    {
        if (effectPrefab == null) return;

        ParticleSystem instance = Instantiate(effectPrefab, position, Quaternion.identity);
        instance.Play();
        Destroy(instance.gameObject, instance.main.duration + instance.main.startLifetime.constantMax);
    }
}
