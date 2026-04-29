using TMPro;
using UnityEngine;

// Cree deux zones cliquables sur la table : GAUCHE et DROITE.
// Le joueur selectionne un domino puis clique une zone, ou glisse vers une zone.
public class PlayZoneRenderer : MonoBehaviour
{
    [Header("Positions")]
    // Positions de secours si le plateau ne fournit pas encore ses extremites.
    public Vector3 leftZonePosition = new Vector3(-5.8f, 0.65f, 0f);
    public Vector3 rightZonePosition = new Vector3(5.8f, 0.65f, 0f);

    [Header("Taille")]
    public Vector2 zoneSize = new Vector2(1.45f, 0.98f);

    [Header("Couleurs")]
    public Color inactiveColor = new Color(0.16f, 0.16f, 0.16f, 0.55f);
    public Color activeColor = new Color(1f, 0.86f, 0.28f, 0.72f);

    private GameObject leftZone;
    private GameObject rightZone;
    private SpriteRenderer leftBody;
    private SpriteRenderer rightBody;
    private BoxCollider2D leftCollider;
    private BoxCollider2D rightCollider;

    // Affiche ou cache les zones.
    // hasSelectedTile indique si un domino est deja selectionne.
    public void Render(
        GameManager gameManager,
        bool show,
        bool hasSelectedTile,
        Vector3 leftWorldPosition,
        Vector3 rightWorldPosition,
        bool leftEnabled,
        bool rightEnabled)
    {
        EnsureZones(gameManager);

        leftZone.transform.position = leftWorldPosition;
        rightZone.transform.position = rightWorldPosition;

        leftZone.SetActive(show);
        rightZone.SetActive(show);

        leftBody.color = hasSelectedTile && leftEnabled ? activeColor : inactiveColor;
        rightBody.color = hasSelectedTile && rightEnabled ? activeColor : inactiveColor;

        if (leftCollider != null)
            leftCollider.enabled = show && hasSelectedTile && leftEnabled;

        if (rightCollider != null)
            rightCollider.enabled = show && hasSelectedTile && rightEnabled;
    }

    // Cree les deux zones si elles n'existent pas encore.
    private void EnsureZones(GameManager gameManager)
    {
        if (leftZone != null && rightZone != null)
            return;

        leftZone = CreateZone("Play Zone Left", "GAUCHE", leftZonePosition, false, gameManager, out leftBody, out leftCollider);
        rightZone = CreateZone("Play Zone Right", "DROITE", rightZonePosition, true, gameManager, out rightBody, out rightCollider);
    }

    // Cree une zone cliquable complete : rectangle, texte et collider.
    private GameObject CreateZone(
        string objectName,
        string label,
        Vector3 position,
        bool playRight,
        GameManager gameManager,
        out SpriteRenderer body,
        out BoxCollider2D zoneCollider)
    {
        GameObject root = new GameObject(objectName);
        root.transform.SetParent(transform, false);
        root.transform.position = position;

        GameObject rectangle = DominoTileVisual.CreateRuntimeRectangle(
            "Zone Body",
            root.transform,
            Vector3.zero,
            new Vector3(zoneSize.x, zoneSize.y, 1f),
            inactiveColor,
            30);

        body = rectangle.GetComponent<SpriteRenderer>();

        zoneCollider = root.AddComponent<BoxCollider2D>();
        zoneCollider.size = zoneSize;
        zoneCollider.isTrigger = true;

        DominoPlayZoneClick click = root.AddComponent<DominoPlayZoneClick>();
        click.Initialize(gameManager, playRight);

        GameObject textObject = new GameObject("Zone Label");
        textObject.transform.SetParent(root.transform, false);
        textObject.transform.localPosition = new Vector3(0f, 0f, -0.05f);

        TextMeshPro text = textObject.AddComponent<TextMeshPro>();
        text.text = label;
        text.fontSize = 0.32f;
        text.alignment = TextAlignmentOptions.Center;
        text.color = Color.white;
        text.rectTransform.sizeDelta = zoneSize;
        text.sortingOrder = 31;

        return root;
    }
}
