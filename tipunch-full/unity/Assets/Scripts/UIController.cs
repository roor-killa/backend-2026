// =============================================
//   Ti Punch Master — UIController.cs
//   Gestion de tout l'UI Canvas
//   Version 2.0 · Martinique 2026
// =============================================

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class UIController : MonoBehaviour
{
    // ─── Références — Client Panel ────────────────────────────────────────────
    [Header("Panneau Client")]
    public Image       clientAvatarImage;
    public TextMeshProUGUI clientNameText;
    public TextMeshProUGUI clientDialogueText;
    public TextMeshProUGUI difficultyBadgeText;
    public Image           difficultyBadgeBg;

    // ─── Références — Cocktail Label ─────────────────────────────────────────
    [Header("Label Cocktail")]
    public TextMeshProUGUI cocktailLabelText;

    // ─── Références — HUD ────────────────────────────────────────────────────
    [Header("HUD")]
    public TextMeshProUGUI scoreText;
    public Transform       mancheDotsParent;
    public GameObject      mancheDotPrefab;

    // ─── Références — Sliders ────────────────────────────────────────────────
    [Header("Sliders")]
    public Transform   slidersParent;
    public GameObject  sliderGroupPrefab;    // Prefab : Label + Slider + ValueText

    // ─── Références — Bouton Servir ───────────────────────────────────────────
    [Header("Bouton Servir")]
    public Button          serveButton;
    public TextMeshProUGUI serveButtonText;

    // ─── Références — Feedback Panel ─────────────────────────────────────────
    [Header("Panneau Feedback")]
    public GameObject      feedbackPanel;
    public TextMeshProUGUI feedbackEmojiText;
    public TextMeshProUGUI feedbackScoreText;
    public TextMeshProUGUI feedbackMessageText;
    public Transform       dosageCompareParent;
    public GameObject      dosageItemPrefab;
    public Button          nextClientButton;

    // ─── Références — Divers ─────────────────────────────────────────────────
    [Header("Divers")]
    public GameObject loadingOverlay;
    public GameObject offlineBanner;

    // ─── Couleurs des badges difficulté ──────────────────────────────────────
    [Header("Couleurs badges")]
    public Color colorFacile    = new Color(0.11f, 0.48f, 0.25f);
    public Color colorMoyen     = new Color(0.60f, 0.40f, 0.00f);
    public Color colorDifficile = new Color(0.69f, 0.13f, 0.13f);

    // ─── État interne ─────────────────────────────────────────────────────────
    private CocktailData              currentCocktail;
    private Dictionary<string, float> currentDosages = new();
    private List<Slider>              activeSliders   = new();
    private List<Color>               ingredientColors = new();

    // ─── Affichage chargement ─────────────────────────────────────────────────
    public void ShowLoading(bool show) =>
        loadingOverlay?.SetActive(show);

    public void ShowOfflineBanner() =>
        offlineBanner?.SetActive(true);

    // ─── HUD ──────────────────────────────────────────────────────────────────
    public void UpdateScore(int score) =>
        scoreText?.SetText($"Score : {score}");

    public void UpdateRoundIndicator(int current, int total)
    {
        if (mancheDotsParent == null) return;

        // Nettoie les anciens points
        foreach (Transform child in mancheDotsParent)
            Destroy(child.gameObject);

        for (int i = 0; i < total; i++)
        {
            var dot = Instantiate(mancheDotPrefab, mancheDotsParent);
            var img = dot.GetComponent<Image>();
            if (img == null) continue;

            if (i < current)        img.color = new Color(1f, 0.88f, 0.20f);   // doré = fait
            else if (i == current)  img.color = Color.white;                    // blanc = actif
            else                    img.color = new Color(1f, 1f, 1f, 0.3f);   // transparent = futur
        }
    }

    // ─── Client ───────────────────────────────────────────────────────────────
    public void DisplayClient(ClientData client)
    {
        clientNameText?.SetText(client.name);
        clientDialogueText?.SetText($"\"{client.dialogue}\"");

        // Badge difficulté
        if (difficultyBadgeText != null)
        {
            difficultyBadgeText.text = client.difficulty;
            Color c = client.difficulty switch
            {
                "Difficile" => colorDifficile,
                "Moyen"     => colorMoyen,
                _           => colorFacile
            };
            difficultyBadgeText.color = c;
            if (difficultyBadgeBg != null) difficultyBadgeBg.color = new Color(c.r, c.g, c.b, 0.15f);
        }

        // Sprite avatar (si sprite avec nom matching existe dans Resources)
        if (clientAvatarImage != null)
        {
            var sprite = Resources.Load<Sprite>($"Sprites/Avatars/{client.avatar}");
            if (sprite != null) clientAvatarImage.sprite = sprite;
        }
    }

    // ─── Sliders ──────────────────────────────────────────────────────────────
    public void BuildSliders(string cocktailId)
    {
        currentCocktail = CocktailDatabase.Get(cocktailId);
        if (currentCocktail == null) { Debug.LogError($"Cocktail '{cocktailId}' introuvable !"); return; }

        // Nettoyage
        foreach (Transform t in slidersParent) Destroy(t.gameObject);
        activeSliders.Clear();
        ingredientColors.Clear();
        currentDosages.Clear();

        // Label cocktail
        cocktailLabelText?.SetText($"{currentCocktail.emoji}  {currentCocktail.name}");

        // Crée un slider par ingrédient
        foreach (var ingr in currentCocktail.ingredients)
        {
            currentDosages[ingr.key] = 0f;
            ingredientColors.Add(ingr.color);

            var go     = Instantiate(sliderGroupPrefab, slidersParent);
            var slider = go.GetComponentInChildren<Slider>();
            var label  = go.transform.Find("Label")?.GetComponent<TextMeshProUGUI>();
            var val    = go.transform.Find("Value")?.GetComponent<TextMeshProUGUI>();
            var valBg  = go.transform.Find("ValueBg")?.GetComponent<Image>();

            if (label != null) label.text = ingr.name;
            if (val   != null) val.text   = "0 cl";
            if (valBg != null) valBg.color = ingr.color;

            if (slider != null)
            {
                slider.minValue = 0f;
                slider.maxValue = 10f;
                slider.value    = 0f;
                slider.wholeNumbers = true;

                string key   = ingr.key;
                int    index = activeSliders.Count;

                slider.onValueChanged.AddListener((v) =>
                {
                    currentDosages[key] = v;
                    if (val != null) val.text = $"{(int)v} cl";
                    OnSliderChanged();
                });

                activeSliders.Add(slider);
            }
        }

        // Reset glass
        GameManager.Instance?.glassController?.ResetGlass();
    }

    private void OnSliderChanged()
    {
        GameManager.Instance?.glassController?
            .UpdateFill(currentDosages, ingredientColors,
                        currentCocktail?.GetMaxTotal() ?? 12f);
    }

    // ─── Bouton Servir ────────────────────────────────────────────────────────
    public void SetServeButtonInteractable(bool value)
    {
        if (serveButton != null) serveButton.interactable = value;
    }

    // Appelé par le bouton Servir (OnClick dans l'inspecteur)
    public void OnServeButtonClicked()
    {
        SetServeButtonInteractable(false);
        StartCoroutine(ServeSequence());
    }

    private IEnumerator ServeSequence()
    {
        // Animation versage
        if (GameManager.Instance?.glassController != null)
            yield return StartCoroutine(GameManager.Instance.glassController.PlayServeAnimation());

        GameManager.Instance?.ServecocktaiL(currentDosages);
    }

    // ─── Feedback Panel ───────────────────────────────────────────────────────
    public void ShowFeedback(ScoreResponseData response, ClientData client)
    {
        feedbackPanel?.SetActive(true);

        string emoji = response.score switch
        {
            100 => "🤩", 85 => "😄", 65 => "😊",
            40  => "😐", 20 => "😞", _  => "😤"
        };
        if (feedbackEmojiText != null) feedbackEmojiText.text = emoji;
        if (feedbackMessageText != null) feedbackMessageText.text = response.feedback;

        // Animation du compteur de score
        StartCoroutine(AnimateScore(0, response.score, 0.6f));

        // Comparaison dosages
        BuildDosageCompare(response);

        // Bouton suivant
        if (nextClientButton != null)
        {
            nextClientButton.interactable = false;
            nextClientButton.GetComponentInChildren<TextMeshProUGUI>()?.SetText(
                GameManager.Instance?.GetCurrentRound() < GameManager.Instance?.totalRounds - 1
                    ? "Client suivant →"
                    : "🏆 Voir le classement");
            StartCoroutine(EnableNextButtonDelayed(1.4f));
        }
    }

    public void HideFeedback() =>
        feedbackPanel?.SetActive(false);

    // Appelé par le bouton "Client suivant" (OnClick dans l'inspecteur)
    public void OnNextClientClicked() =>
        GameManager.Instance?.NextRound();

    private void BuildDosageCompare(ScoreResponseData response)
    {
        if (dosageCompareParent == null || dosageItemPrefab == null) return;

        foreach (Transform t in dosageCompareParent) Destroy(t.gameObject);

        if (currentCocktail == null) return;

        foreach (var ingr in currentCocktail.ingredients)
        {
            var go       = Instantiate(dosageItemPrefab, dosageCompareParent);
            var nameText = go.transform.Find("IngrName")?.GetComponent<TextMeshProUGUI>();
            var yourText = go.transform.Find("Yours")?.GetComponent<TextMeshProUGUI>();
            var tgtText  = go.transform.Find("Target")?.GetComponent<TextMeshProUGUI>();

            float yours  = currentDosages.TryGetValue(ingr.key, out var v) ? v : 0f;
            float target = 0f;
            response.target?.TryGet(ingr.key, out target);
            bool  perfect = Mathf.Approximately(yours, target);

            if (nameText != null) nameText.text = ingr.name;
            if (yourText != null) yourText.text = $"{(int)yours} cl";
            if (tgtText  != null)
            {
                tgtText.text  = perfect ? "✓ Parfait !" : $"Cible : {(int)target} cl";
                tgtText.color = perfect ? colorFacile : colorDifficile;
            }
        }
    }

    private IEnumerator AnimateScore(int from, int to, float duration)
    {
        float elapsed = 0f;
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t   = Mathf.Clamp01(elapsed / duration);
            float ease = 1f - Mathf.Pow(1f - t, 3f);
            int   val  = Mathf.RoundToInt(Mathf.Lerp(from, to, ease));
            feedbackScoreText?.SetText($"{val} pts");
            yield return null;
        }
        feedbackScoreText?.SetText($"{to} pts");
    }

    private IEnumerator EnableNextButtonDelayed(float delay)
    {
        yield return new WaitForSeconds(delay);
        if (nextClientButton != null) nextClientButton.interactable = true;
    }
}
