using System.Collections.Generic;
using UnityEngine;

// Affiche les mains cachees des Joueurs 2 et 3.
// On montre seulement le dos des dominos pour ne pas reveler leurs valeurs.
public class OpponentHandsRenderer : MonoBehaviour
{
    [Header("Positions")]
    // Main du Joueur 2 a gauche.
    public Vector3 leftHandCenter = new Vector3(-7.15f, 0.35f, 0f);

    // Main du Joueur 3 a droite.
    public Vector3 rightHandCenter = new Vector3(7.15f, 0.35f, 0f);

    [Header("Taille")]
    public float tileWidth = 1.08f;
    public float tileHeight = 0.53f;
    public float spacing = 0.12f;

    private Transform leftParent;
    private Transform rightParent;

    private readonly List<GameObject> leftTiles = new List<GameObject>();
    private readonly List<GameObject> rightTiles = new List<GameObject>();

    // Redessine les deux mains adverses.
    public void RenderHands(List<PlayerData> players)
    {
        EnsureParents();
        ClearTiles(leftTiles);
        ClearTiles(rightTiles);

        if (players == null || players.Count < 3)
            return;

        RenderOpponentHand(players[1].Hand.Count, leftParent, leftTiles, true);
        RenderOpponentHand(players[2].Hand.Count, rightParent, rightTiles, false);
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
