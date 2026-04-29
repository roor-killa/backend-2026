// =============================================
//   Ti Punch Master — GlassController.cs
//   Animation du verre en temps réel
//   Version 2.0 · Martinique 2026
// =============================================

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GlassController : MonoBehaviour
{
    // ─── Références ───────────────────────────────────────────────────────────
    [Header("Renderers des couches de liquide")]
    [Tooltip("Layer 0 = fond (ingrédient 0), Layer 1, Layer 2 = haut")]
    public Renderer[] liquidLayers;          // 3 renderers, un par ingrédient

    [Header("Particle Systems")]
    public ParticleSystem bubblesPS;         // Bulles montantes
    public ParticleSystem splashPS;          // Éclaboussures au service

    [Header("Animator")]
    public Animator glassAnimator;           // Animation de versage

    // ─── Paramètres Shader ────────────────────────────────────────────────────
    // Les propriétés suivantes doivent exister dans votre ShaderGraph liquid shader
    private static readonly int PropFillLevel  = Shader.PropertyToID("_FillLevel");
    private static readonly int PropColor      = Shader.PropertyToID("_LiquidColor");
    private static readonly int PropTurbulence = Shader.PropertyToID("_Turbulence");
    private static readonly int PropWaveSpeed  = Shader.PropertyToID("_WaveSpeed");
    private static readonly int PropOpacity    = Shader.PropertyToID("_Opacity");

    // ─── Config ───────────────────────────────────────────────────────────────
    [Header("Paramètres visuels")]
    public float fillSmoothing  = 8f;     // Vitesse de lissage du remplissage
    public float turbulenceIdle = 0.05f;
    public float turbulencePour = 0.4f;

    // ─── État interne ─────────────────────────────────────────────────────────
    private float[] targetFills    = new float[3];
    private float[] currentFills   = new float[3];
    private Color[] targetColors   = new Color[3];
    private bool    isPouring      = false;

    // ─── Couleurs par défaut (remplacées par UIController) ───────────────────
    private readonly Color[] defaultColors =
    {
        new Color(0.83f, 0.63f, 0.19f),  // rhum doré
        new Color(0.53f, 0.80f, 0.13f),  // citron vert
        new Color(1.00f, 0.91f, 0.63f),  // sucre clair
    };

    // ─── Init ─────────────────────────────────────────────────────────────────
    void Awake()
    {
        for (int i = 0; i < 3; i++)
            targetColors[i] = defaultColors[i];
    }

    void Update()
    {
        float dt = Time.deltaTime;
        for (int i = 0; i < liquidLayers.Length && i < 3; i++)
        {
            currentFills[i] = Mathf.Lerp(currentFills[i], targetFills[i], dt * fillSmoothing);
            ApplyShaderParams(i);
        }
    }

    // ─── API publique ─────────────────────────────────────────────────────────

    /// <summary>
    /// Met à jour le remplissage du verre selon les dosages du joueur.
    /// Appelé par UIController à chaque changement de slider.
    /// </summary>
    /// <param name="dosages">Dictionnaire ingrédient → centilitres</param>
    /// <param name="ingredientColors">Couleurs des 3 ingrédients</param>
    /// <param name="maxTotal">Total max attendu (pour normaliser)</param>
    public void UpdateFill(Dictionary<string, float> dosages,
                           List<Color>               ingredientColors,
                           float                     maxTotal = 12f)
    {
        float total = 0f;
        var   vals  = new float[3];
        int   idx   = 0;
        foreach (var v in dosages.Values)
        {
            if (idx < 3) vals[idx++] = v;
            total += v;
        }

        float fillPct = Mathf.Clamp01(total / maxTotal);
        float safe    = total > 0f ? total : 1f;

        for (int i = 0; i < 3; i++)
        {
            targetFills[i]  = fillPct * (vals[i] / safe);
            if (i < ingredientColors.Count)
                targetColors[i] = ingredientColors[i];
        }

        // Active les bulles proportionnellement au remplissage
        if (bubblesPS != null)
        {
            var em = bubblesPS.emission;
            em.rateOverTime = fillPct * 15f;
        }
    }

    /// <summary>
    /// Déclenche l'animation de service.
    /// </summary>
    public IEnumerator PlayServeAnimation()
    {
        isPouring = true;
        glassAnimator?.SetTrigger("Serve");
        splashPS?.Play();

        // Augmente turbulence pendant le versage
        SetTurbulenceAll(turbulencePour);

        yield return new WaitForSeconds(0.8f);

        SetTurbulenceAll(turbulenceIdle);
        isPouring = false;
    }

    /// <summary>
    /// Réinitialise le verre (nouvelle manche).
    /// </summary>
    public void ResetGlass()
    {
        for (int i = 0; i < 3; i++)
        {
            targetFills[i]  = 0f;
            currentFills[i] = 0f;
        }
        bubblesPS?.Stop();
        glassAnimator?.SetTrigger("Reset");
    }

    // ─── Privé ────────────────────────────────────────────────────────────────

    private void ApplyShaderParams(int layerIndex)
    {
        if (layerIndex >= liquidLayers.Length || liquidLayers[layerIndex] == null) return;

        var mat = liquidLayers[layerIndex].material;
        mat.SetFloat(PropFillLevel,  currentFills[layerIndex]);
        mat.SetColor(PropColor,      targetColors[layerIndex]);
        mat.SetFloat(PropOpacity,    currentFills[layerIndex] > 0.01f ? 0.88f : 0f);
        mat.SetFloat(PropWaveSpeed,  isPouring ? 3f : 1f);
    }

    private void SetTurbulenceAll(float value)
    {
        foreach (var r in liquidLayers)
            if (r != null) r.material.SetFloat(PropTurbulence, value);
    }
}
