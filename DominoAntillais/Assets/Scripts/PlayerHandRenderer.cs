using System.Collections.Generic;
using UnityEngine;

// Dessine la main du Joueur 1 en bas de l'ecran.
// Les dominos jouables sont colores en jaune et recoivent un script de clic.
public class PlayerHandRenderer : MonoBehaviour
{
    [Header("Prefab optionnel")]
    // Si un prefab est branche, on l'utilise pour chaque domino de la main.
    // Sinon, le code cree un domino simple automatiquement.
    public GameObject dominoPrefab;

    [Header("Position de la main du joueur 1")]
    // Parent des dominos de la main. Cree automatiquement si null.
    public Transform handParent;

    // Position de la main du joueur dans la scene.
    // Le X a 0 permet de centrer la main en bas.
    public Vector3 handCenter = new Vector3(0f, -3.75f, 0f);

    [Header("Taille et espacement")]
    // Taille d'un domino dans la main.
    public float tileWidth = 1.34f;
    public float tileHeight = 0.66f;

    // Espace horizontal entre les dominos.
    public float spacing = 0.15f;

    // Liste des objets visuels actuellement affiches dans la main.
    private readonly List<GameObject> spawnedTiles = new List<GameObject>();

    // Derniere liste des dominos jouables.
    // Elle sert quand on change seulement le domino selectionne sans redessiner toute la main.
    private List<int> lastPlayableIndexes = new List<int>();

    // Index du domino actuellement selectionne.
    private int selectedHandIndex = -1;

    // Redessine toute la main du joueur.
    // gameManager permet aux dominos de signaler les clics.
    // playableIndexes contient les index des dominos que Joueur 1 peut jouer.
    public void RenderHand(
        List<DominoTile> hand,
        GameManager gameManager,
        List<int> playableIndexes,
        int selectedIndex)
    {
        EnsureParent();
        ClearHand();

        lastPlayableIndexes = playableIndexes != null
            ? new List<int>(playableIndexes)
            : new List<int>();
        selectedHandIndex = selectedIndex;

        if (hand == null || hand.Count == 0)
            return;

        // Les dominos de la main sont tournes a 90 degres.
        // Leur largeur d'occupation devient donc tileHeight.
        float step = tileHeight + spacing;

        // startX centre automatiquement la main, peu importe le nombre de dominos.
        float startX = -((hand.Count - 1) * step) * 0.5f;

        for (int i = 0; i < hand.Count; i++)
        {
            DominoTile tile = hand[i];
            bool isPlayable = lastPlayableIndexes.Contains(i);
            bool isSelected = i == selectedHandIndex;
            Vector3 position = new Vector3(startX + i * step, 0f, 0f);

            PlaceTile(tile, position, i, gameManager, isPlayable, isSelected);
        }
    }

    // Change seulement le visuel de selection sans detruire/recreer les objets.
    // C'est important pour permettre le clic-glisser.
    public void SetSelectedHandIndex(int selectedIndex)
    {
        selectedHandIndex = selectedIndex;

        for (int i = 0; i < spawnedTiles.Count; i++)
        {
            if (spawnedTiles[i] == null)
                continue;

            DominoTileVisual visual = spawnedTiles[i].GetComponent<DominoTileVisual>();

            if (visual != null)
                visual.SetHandState(lastPlayableIndexes.Contains(i), i == selectedHandIndex);
        }
    }

    // Supprime les anciens dominos visuels de la main.
    public void ClearHand()
    {
        for (int i = spawnedTiles.Count - 1; i >= 0; i--)
        {
            if (spawnedTiles[i] != null)
                Destroy(spawnedTiles[i]);
        }

        spawnedTiles.Clear();
    }

    // Cree le parent de la main si besoin.
    private void EnsureParent()
    {
        if (handParent != null)
            return;

        GameObject root = new GameObject("Player 1 Hand Visuals");
        root.transform.SetParent(transform, false);
        root.transform.localPosition = handCenter;
        handParent = root.transform;
    }

    // Cree un domino visuel pour la main.
    private void PlaceTile(
        DominoTile tile,
        Vector3 position,
        int handIndex,
        GameManager gameManager,
        bool isPlayable,
        bool isSelected)
    {
        GameObject go;
        DominoTileVisual visual;

        if (dominoPrefab != null)
        {
            go = Instantiate(dominoPrefab, handParent);
            visual = go.GetComponent<DominoTileVisual>();
        }
        else
        {
            visual = DominoTileVisual.CreateRuntimeDomino(
                handParent,
                "Player 1 Tile " + tile,
                new Vector2(tileWidth, tileHeight),
                20);
            go = visual.gameObject;
        }

        go.transform.localPosition = position;

        // Dans la main du joueur, les dominos sont debout/verticaux.
        go.transform.localRotation = Quaternion.Euler(0f, 0f, 90f);

        if (visual != null)
        {
            visual.SetValues(tile.Left, tile.Right);
            visual.SetHandState(isPlayable, isSelected);
        }
        else
        {
            Debug.LogWarning("Le prefab de domino n'a pas de composant DominoTileVisual.");
        }

        ConfigureClick(go, handIndex, gameManager, isPlayable);
        spawnedTiles.Add(go);
    }

    // Ajoute le collider et le script qui permettent de cliquer sur un domino.
    private void ConfigureClick(GameObject go, int handIndex, GameManager gameManager, bool isPlayable)
    {
        BoxCollider2D collider = go.GetComponent<BoxCollider2D>();

        if (collider == null)
            collider = go.AddComponent<BoxCollider2D>();

        // Taille locale du collider avant rotation.
        collider.size = new Vector2(tileWidth, tileHeight);
        collider.isTrigger = true;

        DominoHandTileClick click = go.GetComponent<DominoHandTileClick>();

        if (click == null)
            click = go.AddComponent<DominoHandTileClick>();

        click.Initialize(gameManager, handIndex, isPlayable);
    }
}
