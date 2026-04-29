using System.Collections.Generic;
using TMPro;
using UnityEngine;

// Gere l'apparence d'un seul domino.
// Il peut fonctionner de deux facons :
// 1. avec un prefab Unity qui contient deja les references leftText/rightText ;
// 2. en creant automatiquement un rectangle + des points noirs en code.
public class DominoTileVisual : MonoBehaviour
{
    [Header("References optionnelles du prefab")]
    // Textes utiles si on cree un prefab avec TextMeshPro.
    // Dans le rendu automatique actuel, on utilise plutot des points noirs.
    public TMP_Text leftText;
    public TMP_Text rightText;

    // Ligne au milieu du domino.
    public GameObject separator;

    [Header("Points crees automatiquement")]
    // Rectangle principal du domino.
    public SpriteRenderer bodyRenderer;

    // Parents qui contiennent les points du cote gauche et du cote droit.
    public Transform leftPipRoot;
    public Transform rightPipRoot;

    // Sprites partages par tous les dominos.
    // On les garde en static pour ne pas recreer les textures a chaque domino.
    private static Sprite whiteSprite;
    private static Sprite roundedSprite;
    private static Sprite pipSprite;

    // Zone dans laquelle les points sont dessines sur chaque moitie du domino.
    private Vector2 pipFieldSize = new Vector2(0.36f, 0.34f);

    // Taille d'un point noir.
    private float pipSize = 0.06f;

    // Ordre d'affichage des points.
    // Plus la valeur est grande, plus l'objet est dessine devant.
    private int pipSortingOrder = 2;

    // Cree un domino complet en code.
    // Cette methode evite d'avoir besoin d'un prefab pendant le prototype.
    public static DominoTileVisual CreateRuntimeDomino(
        Transform parent,
        string objectName,
        Vector2 size,
        int sortingOrder)
    {
        GameObject root = new GameObject(objectName);
        root.transform.SetParent(parent, false);

        DominoTileVisual visual = root.AddComponent<DominoTileVisual>();

        // Les dimensions des points dependent de la taille du domino.
        visual.pipFieldSize = new Vector2(size.x * 0.40f, size.y * 0.72f);
        visual.pipSize = Mathf.Min(size.x, size.y) * 0.16f;
        visual.pipSortingOrder = sortingOrder + 2;

        CreateDominoBase(root.transform, size, sortingOrder, false, out visual.bodyRenderer);

        // Corps principal du domino.
        visual.separator = CreateSquare(
            "Separator",
            root.transform,
            new Vector3(0f, 0f, -0.02f),
            new Vector3(0.025f, size.y * 0.82f, 1f),
            new Color(0.08f, 0.06f, 0.04f, 1f),
            sortingOrder + 1);

        // Deux zones de points : une pour chaque moitie du domino.
        visual.leftPipRoot = CreateRoot("Left Pips", root.transform, new Vector3(-size.x * 0.25f, 0f, -0.03f));
        visual.rightPipRoot = CreateRoot("Right Pips", root.transform, new Vector3(size.x * 0.25f, 0f, -0.03f));

        return visual;
    }

    // Cree un domino vu de dos.
    // Utilise pour les mains des joueurs adverses : on voit le nombre de dominos,
    // mais pas leurs valeurs.
    public static DominoTileVisual CreateRuntimeDominoBack(
        Transform parent,
        string objectName,
        Vector2 size,
        int sortingOrder)
    {
        GameObject root = new GameObject(objectName);
        root.transform.SetParent(parent, false);

        DominoTileVisual visual = root.AddComponent<DominoTileVisual>();
        CreateDominoBase(root.transform, size, sortingOrder, true, out visual.bodyRenderer);

        // Petite ligne centrale sur le dos pour donner un motif de carte/domino.
        CreateSquare(
            "Back Line",
            root.transform,
            new Vector3(0f, 0f, -0.04f),
            new Vector3(size.x * 0.78f, size.y * 0.055f, 1f),
            new Color(0.12f, 0.06f, 0.04f, 0.55f),
            sortingOrder + 2);

        return visual;
    }

    // Cree un rectangle simple.
    // Utilise aussi par DominoBoardRenderer pour creer le fond de table.
    public static GameObject CreateRuntimeRectangle(
        string objectName,
        Transform parent,
        Vector3 localPosition,
        Vector3 localScale,
        Color color,
        int sortingOrder)
    {
        return CreateSquare(objectName, parent, localPosition, localScale, color, sortingOrder);
    }

    // Met a jour les valeurs affichees sur le domino.
    public void SetValues(int left, int right)
    {
        // Si le prefab utilise des textes, on met a jour les textes.
        if (leftText != null)
            leftText.text = left.ToString();

        if (rightText != null)
            rightText.text = right.ToString();

        // Si le domino utilise les points generes en code, on redessine les points.
        if (leftPipRoot != null)
            DrawPips(leftPipRoot, left);

        if (rightPipRoot != null)
            DrawPips(rightPipRoot, right);
    }

    // Change la couleur du domino pour signaler une selection.
    // On s'en servira plus tard quand le joueur pourra cliquer sur sa main.
    public void SetHighlight(bool highlighted)
    {
        SpriteRenderer sr = bodyRenderer != null ? bodyRenderer : GetComponentInChildren<SpriteRenderer>();

        if (sr != null)
            sr.color = highlighted ? new Color(1f, 0.91f, 0.38f, 1f) : new Color(0.97f, 0.94f, 0.80f, 1f);
    }

    // Change la couleur selon l'etat du domino dans la main.
    // Normal   : couleur domino classique.
    // Jouable  : jaune.
    // Selectionne : orange, pour voir quel domino va etre pose.
    public void SetHandState(bool playable, bool selected)
    {
        SpriteRenderer sr = bodyRenderer != null ? bodyRenderer : GetComponentInChildren<SpriteRenderer>();

        if (sr == null)
            return;

        if (selected)
            sr.color = new Color(1f, 0.62f, 0.18f, 1f);
        else if (playable)
            sr.color = new Color(1f, 0.91f, 0.38f, 1f);
        else
            sr.color = new Color(0.97f, 0.94f, 0.80f, 1f);
    }

    // Supprime les anciens points et dessine les nouveaux.
    private void DrawPips(Transform root, int value)
    {
        ClearChildren(root);

        foreach (Vector2 position in GetPipPositions(value))
        {
            GameObject pip = new GameObject("Pip");
            pip.transform.SetParent(root, false);
            pip.transform.localPosition = new Vector3(position.x, position.y, 0f);
            pip.transform.localScale = new Vector3(pipSize, pipSize, 1f);

            SpriteRenderer sr = pip.AddComponent<SpriteRenderer>();
            sr.sprite = GetPipSprite();
            sr.color = new Color(0.05f, 0.04f, 0.03f, 1f);
            sr.sortingOrder = pipSortingOrder;
        }
    }

    // Retourne les positions des points pour une valeur de 0 a 6.
    // C'est la disposition classique d'un de ou d'un domino.
    private IEnumerable<Vector2> GetPipPositions(int value)
    {
        float x = pipFieldSize.x * 0.35f;
        float y = pipFieldSize.y * 0.36f;

        Vector2 center = Vector2.zero;
        Vector2 topLeft = new Vector2(-x, y);
        Vector2 topRight = new Vector2(x, y);
        Vector2 middleLeft = new Vector2(-x, 0f);
        Vector2 middleRight = new Vector2(x, 0f);
        Vector2 bottomLeft = new Vector2(-x, -y);
        Vector2 bottomRight = new Vector2(x, -y);

        switch (Mathf.Clamp(value, 0, 6))
        {
            case 1:
                yield return center;
                break;
            case 2:
                yield return topLeft;
                yield return bottomRight;
                break;
            case 3:
                yield return topLeft;
                yield return center;
                yield return bottomRight;
                break;
            case 4:
                yield return topLeft;
                yield return topRight;
                yield return bottomLeft;
                yield return bottomRight;
                break;
            case 5:
                yield return topLeft;
                yield return topRight;
                yield return center;
                yield return bottomLeft;
                yield return bottomRight;
                break;
            case 6:
                yield return topLeft;
                yield return topRight;
                yield return middleLeft;
                yield return middleRight;
                yield return bottomLeft;
                yield return bottomRight;
                break;
        }
    }

    // Cree un GameObject vide parent.
    private static Transform CreateRoot(string objectName, Transform parent, Vector3 localPosition)
    {
        GameObject root = new GameObject(objectName);
        root.transform.SetParent(parent, false);
        root.transform.localPosition = localPosition;
        return root.transform;
    }

    // Cree la base visuelle d'un domino :
    // ombre, bord sombre, corps clair ou dos colore, et petites marques de texture.
    private static void CreateDominoBase(
        Transform root,
        Vector2 size,
        int sortingOrder,
        bool backSide,
        out SpriteRenderer bodyRenderer)
    {
        CreateRoundedSquare(
            "Shadow",
            root,
            new Vector3(0.055f, -0.055f, 0.04f),
            new Vector3(size.x * 1.045f, size.y * 1.09f, 1f),
            new Color(0f, 0f, 0f, 0.28f),
            sortingOrder - 2);

        CreateRoundedSquare(
            "Dark Edge",
            root,
            Vector3.zero,
            new Vector3(size.x * 1.055f, size.y * 1.085f, 1f),
            new Color(0.10f, 0.065f, 0.035f, 1f),
            sortingOrder - 1);

        Color bodyColor = backSide
            ? new Color(0.42f, 0.12f, 0.075f, 1f)
            : new Color(0.98f, 0.94f, 0.78f, 1f);

        bodyRenderer = CreateRoundedSquare(
            "Body",
            root,
            Vector3.zero,
            new Vector3(size.x, size.y, 1f),
            bodyColor,
            sortingOrder).GetComponent<SpriteRenderer>();

        AddSurfaceTexture(root, size, sortingOrder + 1, backSide);
    }

    // Ajoute quelques petites marques fixes pour eviter un domino trop plat.
    private static void AddSurfaceTexture(Transform root, Vector2 size, int sortingOrder, bool backSide)
    {
        Color markColor = backSide
            ? new Color(1f, 0.78f, 0.42f, 0.18f)
            : new Color(0.42f, 0.27f, 0.12f, 0.13f);

        Vector2[] positions =
        {
            new Vector2(-0.34f, 0.24f),
            new Vector2(-0.13f, -0.18f),
            new Vector2(0.18f, 0.20f),
            new Vector2(0.36f, -0.12f),
            new Vector2(-0.42f, -0.04f),
            new Vector2(0.02f, 0.03f)
        };

        Vector2[] sizes =
        {
            new Vector2(0.035f, 0.010f),
            new Vector2(0.026f, 0.013f),
            new Vector2(0.030f, 0.010f),
            new Vector2(0.022f, 0.014f),
            new Vector2(0.020f, 0.010f),
            new Vector2(0.018f, 0.018f)
        };

        for (int i = 0; i < positions.Length; i++)
        {
            CreateRoundedSquare(
                "Surface Mark",
                root,
                new Vector3(positions[i].x * size.x, positions[i].y * size.y, -0.035f),
                new Vector3(size.x * sizes[i].x, size.y * sizes[i].y, 1f),
                markColor,
                sortingOrder);
        }
    }

    // Cree un rectangle a partir d'un sprite blanc 1x1.
    // On change ensuite son scale et sa couleur pour obtenir le rendu voulu.
    private static GameObject CreateSquare(
        string objectName,
        Transform parent,
        Vector3 localPosition,
        Vector3 localScale,
        Color color,
        int sortingOrder)
    {
        GameObject go = new GameObject(objectName);
        go.transform.SetParent(parent, false);
        go.transform.localPosition = localPosition;
        go.transform.localScale = localScale;

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = GetWhiteSprite();
        sr.color = color;
        sr.sortingOrder = sortingOrder;

        return go;
    }

    // Cree une forme arrondie pour le corps des dominos.
    // On garde CreateSquare pour la table et les petites lignes nettes.
    private static GameObject CreateRoundedSquare(
        string objectName,
        Transform parent,
        Vector3 localPosition,
        Vector3 localScale,
        Color color,
        int sortingOrder)
    {
        GameObject go = new GameObject(objectName);
        go.transform.SetParent(parent, false);
        go.transform.localPosition = localPosition;
        go.transform.localScale = localScale;

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = GetRoundedSprite();
        sr.color = color;
        sr.sortingOrder = sortingOrder;

        return go;
    }

    // Detruit tous les enfants d'un Transform.
    private static void ClearChildren(Transform root)
    {
        for (int i = root.childCount - 1; i >= 0; i--)
        {
            Destroy(root.GetChild(i).gameObject);
        }
    }

    // Cree un sprite blanc carre de 1 pixel.
    // Ce sprite sert de base pour les rectangles.
    private static Sprite GetWhiteSprite()
    {
        if (whiteSprite != null)
            return whiteSprite;

        Texture2D texture = new Texture2D(1, 1);
        texture.filterMode = FilterMode.Bilinear;
        texture.wrapMode = TextureWrapMode.Clamp;
        texture.SetPixel(0, 0, Color.white);
        texture.Apply();

        whiteSprite = Sprite.Create(texture, new Rect(0, 0, 1, 1), new Vector2(0.5f, 0.5f), 1f);
        return whiteSprite;
    }

    // Cree un sprite carre avec des coins arrondis et un bord doux.
    // Utilise pour que les dominos ressemblent moins a de simples pixels carres.
    private static Sprite GetRoundedSprite()
    {
        if (roundedSprite != null)
            return roundedSprite;

        const int size = 96;
        Texture2D texture = new Texture2D(size, size);
        texture.filterMode = FilterMode.Bilinear;
        texture.wrapMode = TextureWrapMode.Clamp;

        float radius = size * 0.17f;
        float edgeSoftness = 1.6f;
        float min = radius;
        float max = size - 1 - radius;

        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                float closestX = Mathf.Clamp(x, min, max);
                float closestY = Mathf.Clamp(y, min, max);
                float distance = Vector2.Distance(new Vector2(x, y), new Vector2(closestX, closestY));
                float alpha = 1f - Mathf.Clamp01((distance - radius + edgeSoftness) / edgeSoftness);
                texture.SetPixel(x, y, new Color(1f, 1f, 1f, alpha));
            }
        }

        texture.Apply();

        roundedSprite = Sprite.Create(texture, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), size);
        return roundedSprite;
    }

    // Cree un sprite rond blanc.
    // On le colorie en noir au moment de creer les points du domino.
    private static Sprite GetPipSprite()
    {
        if (pipSprite != null)
            return pipSprite;

        const int size = 80;
        Texture2D texture = new Texture2D(size, size);
        texture.filterMode = FilterMode.Bilinear;
        texture.wrapMode = TextureWrapMode.Clamp;

        Color clear = new Color(0f, 0f, 0f, 0f);
        Vector2 center = new Vector2((size - 1) * 0.5f, (size - 1) * 0.5f);
        float radius = size * 0.40f;
        float edgeSoftness = 2.2f;

        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                float distance = Vector2.Distance(new Vector2(x, y), center);
                float alpha = 1f - Mathf.Clamp01((distance - radius + edgeSoftness) / edgeSoftness);
                texture.SetPixel(x, y, alpha > 0f ? new Color(1f, 1f, 1f, alpha) : clear);
            }
        }

        texture.Apply();

        pipSprite = Sprite.Create(texture, new Rect(0, 0, size, size), new Vector2(0.5f, 0.5f), size);
        return pipSprite;
    }
}
