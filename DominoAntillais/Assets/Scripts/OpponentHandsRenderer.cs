using System.Collections.Generic;
using UnityEngine;

// Affiche les mains cachees des adversaires.
// On montre seulement le dos des dominos pour ne pas reveler leurs valeurs.
public class OpponentHandsRenderer : MonoBehaviour
{
    [Header("Positions")]
    // Main du Joueur 2 a gauche.
    public Vector3 leftHandCenter = new Vector3(-7.15f, 0.35f, 0f);

    // Main de l'adversaire a droite.
    public Vector3 rightHandCenter = new Vector3(7.15f, 0.35f, 0f);

    // Main du Joueur 3 en haut quand on joue a 4.
    // En mode 4 joueurs : Joueur 2 a gauche, Joueur 3 en haut, Joueur 4 a droite.
    public Vector3 topHandCenter = new Vector3(0f, 4.35f, 0f);

    [Header("Taille")]
    public float tileWidth = 1.08f;
    public float tileHeight = 0.53f;
    public float spacing = 0.12f;

    private Transform leftParent;
    private Transform rightParent;
    private Transform topParent;

    private readonly List<GameObject> leftTiles = new List<GameObject>();
    private readonly List<GameObject> rightTiles = new List<GameObject>();
    private readonly List<GameObject> topTiles = new List<GameObject>();

    // Redessine les mains adverses.
    // Mode 3 joueurs : Joueur 2 a gauche, Joueur 3 a droite.
    // Mode 4 joueurs : Joueur 2 a gauche, Joueur 3 en haut, Joueur 4 a droite.
    public void RenderHands(List<PlayerData> players)
    {
        EnsureParents();
        ClearTiles(leftTiles);
        ClearTiles(rightTiles);
        ClearTiles(topTiles);

        if (players == null || players.Count < 3)
            return;

        RenderOpponentHand(players[1].Hand.Count, leftParent, leftTiles, true);

        if (players.Count >= 4)
        {
            RenderTopOpponentHand(players[2].Hand.Count);
            RenderOpponentHand(players[3].Hand.Count, rightParent, rightTiles, false);
        }
        else
        {
            RenderOpponentHand(players[2].Hand.Count, rightParent, rightTiles, false);
        }
    }

    // Cree les parents si besoin.
    private void EnsureParents()
    {
        if (leftParent == null)
        {
            GameObject leftRoot = new GameObject("Player 2 Hidden Hand");
            leftRoot.transform.SetParent(transform, false);
            leftRoot.transform.localPosition = leftHandCenter;
            leftParent = leftRoot.transform;
        }

        if (rightParent == null)
        {
            GameObject rightRoot = new GameObject("Player 3 Hidden Hand");
            rightRoot.transform.SetParent(transform, false);
            rightRoot.transform.localPosition = rightHandCenter;
            rightParent = rightRoot.transform;
        }

        if (topParent == null)
        {
            GameObject topRoot = new GameObject("Player 3 Hidden Hand Top");
            topRoot.transform.SetParent(transform, false);
            topRoot.transform.localPosition = topHandCenter;
            topParent = topRoot.transform;
        }

        // Si les valeurs sont ajustees dans l'Inspector, on les reapplique au rendu suivant.
        leftParent.localPosition = leftHandCenter;
        rightParent.localPosition = rightHandCenter;
        topParent.localPosition = topHandCenter;
    }

    // Affiche une main cachee sous forme de pile verticale legerement espacee.
    private void RenderOpponentHand(int tileCount, Transform parent, List<GameObject> spawnedTiles, bool leftSide)
    {
        float step = tileHeight + spacing;
        float startY = -((tileCount - 1) * step) * 0.5f;

        for (int i = 0; i < tileCount; i++)
        {
            DominoTileVisual visual = DominoTileVisual.CreateRuntimeDominoBack(
                parent,
                "Hidden Opponent Tile",
                new Vector2(tileWidth, tileHeight),
                18);

            GameObject go = visual.gameObject;
            go.transform.localPosition = new Vector3(0f, startY + i * step, 0f);

            // Les mains adverses sont orientees vers la table.
            go.transform.localRotation = leftSide
                ? Quaternion.Euler(0f, 0f, -8f)
                : Quaternion.Euler(0f, 0f, 8f);

            spawnedTiles.Add(go);
        }
    }

    // Affiche la main du joueur du haut en ligne horizontale.
    private void RenderTopOpponentHand(int tileCount)
    {
        float step = tileWidth + spacing;
        float startX = -((tileCount - 1) * step) * 0.5f;

        for (int i = 0; i < tileCount; i++)
        {
            DominoTileVisual visual = DominoTileVisual.CreateRuntimeDominoBack(
                topParent,
                "Hidden Top Opponent Tile",
                new Vector2(tileWidth, tileHeight),
                18);

            GameObject go = visual.gameObject;
            go.transform.localPosition = new Vector3(startX + i * step, 0f, 0f);

            // La main du haut reste horizontale pour lire clairement la place disponible.
            go.transform.localRotation = Quaternion.identity;

            topTiles.Add(go);
        }
    }

    // Detruit les anciens objets d'une main.
    private void ClearTiles(List<GameObject> spawnedTiles)
    {
        for (int i = spawnedTiles.Count - 1; i >= 0; i--)
        {
            if (spawnedTiles[i] != null)
                Destroy(spawnedTiles[i]);
        }

        spawnedTiles.Clear();
    }
}
