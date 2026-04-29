using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

// Petit conteneur des reglages choisis avant le lancement d'une partie.
// Le but est de pouvoir transmettre plusieurs options au GameManager
// sans multiplier les parametres de methode.
public enum PrototypeLanguage
{
    French,
    FrenchCreole,
    English
}

// Petit conteneur des reglages choisis avant le lancement d'une partie.
// Le but est de pouvoir transmettre plusieurs options au GameManager
// sans multiplier les parametres de methode.
public struct MatchSetupSelection
{
    public int ScoreToWin;
    public bool PlayBlockedRoundsAtPoints;
    public float HumanTurnTimeLimit;
    public float AutomaticTurnDelay;
    public PrototypeLanguage Language;
}

// Cree un menu de lancement simple avant de commencer la partie.
// Tout est genere en code pour eviter une configuration manuelle dans la scene.
public class MatchSetupMenuRenderer : MonoBehaviour
{
    [Header("Couleurs")]
    // Fond sombre derriere le panneau.
    public Color backdropColor = new Color(0f, 0f, 0f, 0.58f);

    // Couleur du panneau principal.
    public Color panelColor = new Color(0.15f, 0.08f, 0.06f, 0.94f);

    // Couleur des boutons non selectionnes.
    public Color idleButtonColor = new Color(0.30f, 0.16f, 0.12f, 1f);

    // Couleur des boutons selectionnes.
    public Color selectedButtonColor = new Color(0.93f, 0.73f, 0.27f, 1f);

    // Couleur du bouton principal.
    public Color primaryButtonColor = new Color(0.86f, 0.47f, 0.18f, 1f);

    // Couleur generale des textes.
    public Color textColor = Color.white;

    [Header("Dimensions")]
    // Taille du panneau central.
    public Vector2 panelSize = new Vector2(860f, 720f);

    // Largeur d'un bouton de choix.
    public Vector2 optionButtonSize = new Vector2(170f, 54f);

    // Taille du bouton principal.
    public Vector2 startButtonSize = new Vector2(260f, 64f);

    // Canvas cree automatiquement pour porter le menu.
    private Canvas setupCanvas;

    // Racine du menu.
    private GameObject menuRoot;

    // Selection actuellement affichee.
    private MatchSetupSelection currentSelection;

    // GameManager qui recevra les regles quand le joueur clique sur "Lancer".
    private GameManager boundGameManager;

    // Images des boutons d'options pour recolorer la selection.
    private readonly List<Image> scoreButtonImages = new List<Image>();
    private readonly List<Image> blockedButtonImages = new List<Image>();
    private readonly List<Image> timerButtonImages = new List<Image>();
    private readonly List<Image> speedButtonImages = new List<Image>();
    private readonly List<Image> languageButtonImages = new List<Image>();

    // Bouton principal "Lancer la partie".
    private Image startButtonImage;

    // Affiche le menu avec les reglages courants.
    public void Show(GameManager gameManager, MatchSetupSelection initialSelection)
    {
        boundGameManager = gameManager;
        currentSelection = initialSelection;

        EnsureCanvas();
        EnsureEventSystem();
        EnsureMenu();

        menuRoot.SetActive(true);
        RefreshSelectionVisuals();
    }

    // Cree un canvas dedie au menu si besoin.
    private void EnsureCanvas()
    {
        if (setupCanvas != null)
            return;

        GameObject canvasObject = new GameObject("Match Setup Canvas");
        canvasObject.transform.SetParent(transform, false);

        setupCanvas = canvasObject.AddComponent<Canvas>();
        setupCanvas.renderMode = RenderMode.ScreenSpaceOverlay;
        setupCanvas.sortingOrder = 300;

        CanvasScaler scaler = canvasObject.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1600f, 900f);
        scaler.matchWidthOrHeight = 0.5f;

        canvasObject.AddComponent<GraphicRaycaster>();
    }

    // S'assure qu'un EventSystem existe pour les boutons UI.
    private void EnsureEventSystem()
    {
        if (FindFirstObjectByType<EventSystem>() != null)
            return;

        GameObject eventSystemObject = new GameObject("EventSystem");
        eventSystemObject.AddComponent<EventSystem>();
        eventSystemObject.AddComponent<StandaloneInputModule>();
    }

    // Construit le menu une seule fois.
    private void EnsureMenu()
    {
        if (menuRoot != null)
            return;

        menuRoot = CreateUiObject("Match Setup Root", setupCanvas.transform);
        RectTransform rootRect = menuRoot.GetComponent<RectTransform>();
        rootRect.anchorMin = Vector2.zero;
        rootRect.anchorMax = Vector2.one;
        rootRect.offsetMin = Vector2.zero;
        rootRect.offsetMax = Vector2.zero;

        Image backdrop = menuRoot.AddComponent<Image>();
        backdrop.color = backdropColor;

        GameObject panelObject = CreateUiObject("Setup Panel", menuRoot.transform);
        RectTransform panelRect = panelObject.GetComponent<RectTransform>();
        panelRect.anchorMin = new Vector2(0.5f, 0.5f);
        panelRect.anchorMax = new Vector2(0.5f, 0.5f);
        panelRect.pivot = new Vector2(0.5f, 0.5f);
        panelRect.sizeDelta = panelSize;
        // On remonte legerement le panneau pour que le bouton principal
        // reste bien dans la zone cliquable, meme sur des fenetres Unity plus basses.
        panelRect.anchoredPosition = new Vector2(0f, 72f);

        Image panelImage = panelObject.AddComponent<Image>();
        panelImage.color = panelColor;

        VerticalLayoutGroup panelLayout = panelObject.AddComponent<VerticalLayoutGroup>();
        panelLayout.padding = new RectOffset(34, 34, 30, 38);
        panelLayout.spacing = 15;
        panelLayout.childAlignment = TextAnchor.UpperLeft;
        panelLayout.childControlHeight = false;
        panelLayout.childControlWidth = true;
        panelLayout.childForceExpandHeight = false;
        panelLayout.childForceExpandWidth = true;

        CreateLabel(panelObject.transform, "Projet Domino", 36f, FontStyles.Bold);
        CreateDescription(panelObject.transform, "Choisis les regles principales du prototype avant de lancer la partie.");

        BuildScoreRow(panelObject.transform);
        BuildBlockedRow(panelObject.transform);
        BuildTimerRow(panelObject.transform);
        BuildSpeedRow(panelObject.transform);
        BuildLanguageRow(panelObject.transform);
        BuildStartButton(panelObject.transform);
    }

    // Ligne "score pour gagner".
    private void BuildScoreRow(Transform parent)
    {
        Transform row = CreateOptionRow(parent, "Score pour gagner");
        scoreButtonImages.Add(CreateOptionButton(row, "3 points", () =>
        {
            currentSelection.ScoreToWin = 3;
            RefreshSelectionVisuals();
        }));
        scoreButtonImages.Add(CreateOptionButton(row, "5 points", () =>
        {
            currentSelection.ScoreToWin = 5;
            RefreshSelectionVisuals();
        }));
    }

    // Ligne pour choisir ce qui se passe quand tout le monde toque.
    private void BuildBlockedRow(Transform parent)
    {
        Transform row = CreateOptionRow(parent, "Manche bloquee");
        blockedButtonImages.Add(CreateOptionButton(row, "Aux points", () =>
        {
            currentSelection.PlayBlockedRoundsAtPoints = true;
            RefreshSelectionVisuals();
        }));
        blockedButtonImages.Add(CreateOptionButton(row, "Redistribuer", () =>
        {
            currentSelection.PlayBlockedRoundsAtPoints = false;
            RefreshSelectionVisuals();
        }));
    }

    // Ligne du timer du joueur humain.
    private void BuildTimerRow(Transform parent)
    {
        Transform row = CreateOptionRow(parent, "Timer Joueur 1");
        timerButtonImages.Add(CreateOptionButton(row, "10 sec", () =>
        {
            currentSelection.HumanTurnTimeLimit = 10f;
            RefreshSelectionVisuals();
        }));
        timerButtonImages.Add(CreateOptionButton(row, "15 sec", () =>
        {
            currentSelection.HumanTurnTimeLimit = 15f;
            RefreshSelectionVisuals();
        }));
        timerButtonImages.Add(CreateOptionButton(row, "20 sec", () =>
        {
            currentSelection.HumanTurnTimeLimit = 20f;
            RefreshSelectionVisuals();
        }));
    }

    // Ligne de vitesse des IA.
    private void BuildSpeedRow(Transform parent)
    {
        Transform row = CreateOptionRow(parent, "Vitesse IA");
        speedButtonImages.Add(CreateOptionButton(row, "Lente", () =>
        {
            currentSelection.AutomaticTurnDelay = 2.6f;
            RefreshSelectionVisuals();
        }));
        speedButtonImages.Add(CreateOptionButton(row, "Normale", () =>
        {
            currentSelection.AutomaticTurnDelay = 2f;
            RefreshSelectionVisuals();
        }));
        speedButtonImages.Add(CreateOptionButton(row, "Rapide", () =>
        {
            currentSelection.AutomaticTurnDelay = 1.4f;
            RefreshSelectionVisuals();
        }));
    }

    // Ligne du choix de langue.
    // Pour le moment, elle sert de base de config propre pour la suite.
    private void BuildLanguageRow(Transform parent)
    {
        Transform row = CreateOptionRow(parent, "Langue");
        languageButtonImages.Add(CreateOptionButton(row, "FR", () =>
        {
            currentSelection.Language = PrototypeLanguage.French;
            RefreshSelectionVisuals();
        }));
        languageButtonImages.Add(CreateOptionButton(row, "FR-KREYOL", () =>
        {
            currentSelection.Language = PrototypeLanguage.FrenchCreole;
            RefreshSelectionVisuals();
        }));
        languageButtonImages.Add(CreateOptionButton(row, "EN", () =>
        {
            currentSelection.Language = PrototypeLanguage.English;
            RefreshSelectionVisuals();
        }));
    }

    // Cree le bouton principal qui demarre la partie.
    private void BuildStartButton(Transform parent)
    {
        GameObject footerObject = CreateUiObject("Start Footer", parent);
        HorizontalLayoutGroup footerLayout = footerObject.AddComponent<HorizontalLayoutGroup>();
        footerLayout.childAlignment = TextAnchor.MiddleCenter;
        footerLayout.childControlHeight = false;
        footerLayout.childControlWidth = false;
        footerLayout.childForceExpandHeight = false;
        footerLayout.childForceExpandWidth = false;

        LayoutElement footerLayoutElement = footerObject.AddComponent<LayoutElement>();
        footerLayoutElement.preferredHeight = startButtonSize.y + 18f;

        GameObject buttonObject = CreateUiObject("Start Button", footerObject.transform);
        RectTransform buttonRect = buttonObject.GetComponent<RectTransform>();
        buttonRect.sizeDelta = startButtonSize;

        LayoutElement layout = buttonObject.AddComponent<LayoutElement>();
        layout.preferredWidth = startButtonSize.x;
        layout.preferredHeight = startButtonSize.y;
        layout.minHeight = startButtonSize.y;

        startButtonImage = buttonObject.AddComponent<Image>();
        startButtonImage.color = primaryButtonColor;

        Button button = buttonObject.AddComponent<Button>();
        button.onClick.AddListener(HandleStartClicked);

        CreateButtonText(buttonObject.transform, "Lancer la partie", 28f);
    }

    // Rafraichit la couleur des boutons en fonction du choix actuel.
    private void RefreshSelectionVisuals()
    {
        ApplySelection(scoreButtonImages, currentSelection.ScoreToWin == 3 ? 0 : 1);
        ApplySelection(blockedButtonImages, currentSelection.PlayBlockedRoundsAtPoints ? 0 : 1);

        int timerIndex = Mathf.Approximately(currentSelection.HumanTurnTimeLimit, 10f) ? 0
            : Mathf.Approximately(currentSelection.HumanTurnTimeLimit, 20f) ? 2
            : 1;
        ApplySelection(timerButtonImages, timerIndex);

        int speedIndex = Mathf.Approximately(currentSelection.AutomaticTurnDelay, 2.6f) ? 0
            : Mathf.Approximately(currentSelection.AutomaticTurnDelay, 1.4f) ? 2
            : 1;
        ApplySelection(speedButtonImages, speedIndex);

        int languageIndex = currentSelection.Language == PrototypeLanguage.French ? 0
            : currentSelection.Language == PrototypeLanguage.FrenchCreole ? 1
            : 2;
        ApplySelection(languageButtonImages, languageIndex);

        if (startButtonImage != null)
            startButtonImage.color = primaryButtonColor;
    }

    // Colorie le bouton selectionne et remet les autres dans leur etat normal.
    private void ApplySelection(List<Image> images, int selectedIndex)
    {
        for (int i = 0; i < images.Count; i++)
        {
            if (images[i] == null)
                continue;

            images[i].color = i == selectedIndex ? selectedButtonColor : idleButtonColor;
        }
    }

    // Clique sur le bouton principal.
    private void HandleStartClicked()
    {
        if (boundGameManager == null)
            return;

        menuRoot.SetActive(false);
        boundGameManager.ApplySetupAndStartMatch(currentSelection);
    }

    // Cree une ligne complete : label a gauche, boutons a droite.
    private Transform CreateOptionRow(Transform parent, string label)
    {
        GameObject rowObject = CreateUiObject(label + " Row", parent);
        HorizontalLayoutGroup rowLayout = rowObject.AddComponent<HorizontalLayoutGroup>();
        rowLayout.spacing = 18;
        rowLayout.childAlignment = TextAnchor.MiddleLeft;
        rowLayout.childControlHeight = false;
        rowLayout.childControlWidth = false;
        rowLayout.childForceExpandHeight = false;
        rowLayout.childForceExpandWidth = false;

        LayoutElement rowLayoutElement = rowObject.AddComponent<LayoutElement>();
        rowLayoutElement.preferredHeight = 60f;

        GameObject labelObject = CreateUiObject(label + " Label", rowObject.transform);
        LayoutElement labelLayout = labelObject.AddComponent<LayoutElement>();
        labelLayout.preferredWidth = 220f;
        labelLayout.preferredHeight = 54f;

        CreateText(labelObject.transform, label, 24f, FontStyles.Bold, TextAlignmentOptions.Left);

        GameObject buttonsObject = CreateUiObject(label + " Buttons", rowObject.transform);
        HorizontalLayoutGroup buttonsLayout = buttonsObject.AddComponent<HorizontalLayoutGroup>();
        buttonsLayout.spacing = 12;
        buttonsLayout.childAlignment = TextAnchor.MiddleLeft;
        buttonsLayout.childControlHeight = false;
        buttonsLayout.childControlWidth = false;
        buttonsLayout.childForceExpandHeight = false;
        buttonsLayout.childForceExpandWidth = false;

        return buttonsObject.transform;
    }

    // Cree un bouton d'option.
    private Image CreateOptionButton(Transform parent, string label, UnityEngine.Events.UnityAction onClick)
    {
        GameObject buttonObject = CreateUiObject(label + " Button", parent);
        RectTransform buttonRect = buttonObject.GetComponent<RectTransform>();
        buttonRect.sizeDelta = optionButtonSize;

        LayoutElement layout = buttonObject.AddComponent<LayoutElement>();
        layout.preferredWidth = optionButtonSize.x;
        layout.preferredHeight = optionButtonSize.y;
        layout.minWidth = optionButtonSize.x;
        layout.minHeight = optionButtonSize.y;

        Image image = buttonObject.AddComponent<Image>();
        image.color = idleButtonColor;

        Button button = buttonObject.AddComponent<Button>();
        button.onClick.AddListener(onClick);

        CreateButtonText(buttonObject.transform, label, 23f);
        return image;
    }

    // Texte principal d'un bouton.
    private void CreateButtonText(Transform parent, string textValue, float fontSize)
    {
        GameObject textObject = CreateUiObject("Label", parent);
        RectTransform textRect = textObject.GetComponent<RectTransform>();
        textRect.anchorMin = Vector2.zero;
        textRect.anchorMax = Vector2.one;
        textRect.offsetMin = Vector2.zero;
        textRect.offsetMax = Vector2.zero;

        TextMeshProUGUI text = textObject.AddComponent<TextMeshProUGUI>();
        text.text = textValue;
        text.fontSize = fontSize;
        text.color = textColor;
        text.alignment = TextAlignmentOptions.Center;

        if (TMP_Settings.defaultFontAsset != null)
            text.font = TMP_Settings.defaultFontAsset;
    }

    // Cree un titre ou un texte libre dans le panneau.
    private TextMeshProUGUI CreateText(
        Transform parent,
        string textValue,
        float fontSize,
        FontStyles style,
        TextAlignmentOptions alignment)
    {
        GameObject textObject = CreateUiObject(textValue + " Text", parent);
        TextMeshProUGUI text = textObject.AddComponent<TextMeshProUGUI>();
        text.text = textValue;
        text.fontSize = fontSize;
        text.fontStyle = style;
        text.color = textColor;
        text.alignment = alignment;

        if (TMP_Settings.defaultFontAsset != null)
            text.font = TMP_Settings.defaultFontAsset;

        LayoutElement layout = textObject.AddComponent<LayoutElement>();
        layout.preferredHeight = fontSize + 18f;
        return text;
    }

    // Cree le titre du panneau.
    private void CreateLabel(Transform parent, string label, float fontSize, FontStyles style)
    {
        CreateText(parent, label, fontSize, style, TextAlignmentOptions.Left);
    }

    // Cree la petite phrase d'explication sous le titre.
    private void CreateDescription(Transform parent, string description)
    {
        TextMeshProUGUI text = CreateText(parent, description, 22f, FontStyles.Normal, TextAlignmentOptions.Left);
        text.enableWordWrapping = true;
    }

    // Cree un GameObject UI simple.
    private GameObject CreateUiObject(string objectName, Transform parent)
    {
        GameObject go = new GameObject(objectName, typeof(RectTransform));
        go.transform.SetParent(parent, false);
        return go;
    }
}
