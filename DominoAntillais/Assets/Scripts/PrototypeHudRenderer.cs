using TMPro;
using UnityEngine;

// Petit HUD cree en code pour le prototype.
// Il affiche le score, le tour actuel et un message d'etat.
public class PrototypeHudRenderer : MonoBehaviour
{
    [Header("Position")]
    // Position du texte dans le monde Unity.
    public Vector3 hudPosition = new Vector3(0f, 4.55f, 0f);

    [Header("Style")]
    // Taille du texte dans la scene.
    public float fontSize = 0.32f;

    // Couleur du texte.
    public Color textColor = Color.white;

    // Largeur de la zone de texte.
    public float textWidth = 15.5f;

    // Objet TextMeshPro cree automatiquement.
    private TextMeshPro hudText;

    // Met a jour le texte affiche.
    public void Render(string scoreLine, string turnLine, string statusLine)
    {
        EnsureText();

        hudText.text = scoreLine + "\n" + turnLine + "\n" + statusLine;
    }

    // Cree le TextMeshPro si besoin.
    private void EnsureText()
    {
        if (hudText != null)
            return;

        GameObject go = new GameObject("Prototype HUD");
        go.transform.SetParent(transform, false);
        go.transform.localPosition = hudPosition;

        hudText = go.AddComponent<TextMeshPro>();
        hudText.fontSize = fontSize;
        hudText.color = textColor;
        hudText.alignment = TextAlignmentOptions.Top;
        hudText.textWrappingMode = TextWrappingModes.NoWrap;
        hudText.rectTransform.sizeDelta = new Vector2(textWidth, 1.5f);

        // Met le HUD devant la table et les dominos.
        hudText.sortingOrder = 100;
    }
}
