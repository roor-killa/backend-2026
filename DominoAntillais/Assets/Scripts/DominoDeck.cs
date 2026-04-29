using System.Collections.Generic;
using UnityEngine;

// Represente le paquet complet de dominos.
// Pour un jeu double-six classique, il y a 28 dominos :
// [0|0], [0|1], ..., [6|6].
public class DominoDeck
{
    // Liste interne des dominos encore disponibles dans le paquet.
    private List<DominoTile> tiles = new List<DominoTile>();

    // Quand on cree un paquet, on genere directement les 28 dominos.
    public DominoDeck()
    {
        GenerateDeck();
    }

    // Genere tous les dominos possibles de 0 a 6.
    // La boucle commence right a left pour eviter les doublons :
    // on cree [2|5], mais pas [5|2], car c'est le meme domino retourne.
    private void GenerateDeck()
    {
        tiles.Clear();

        for (int left = 0; left <= 6; left++)
        {
            for (int right = left; right <= 6; right++)
            {
                tiles.Add(new DominoTile(left, right));
            }
        }
    }

    // Melange le paquet avec un algorithme simple :
    // on parcourt chaque position et on l'echange avec une position aleatoire.
    public void Shuffle()
    {
        for (int i = 0; i < tiles.Count; i++)
        {
            int randomIndex = Random.Range(i, tiles.Count);

            DominoTile temp = tiles[i];
            tiles[i] = tiles[randomIndex];
            tiles[randomIndex] = temp;
        }
    }

    // Retire et retourne le premier domino du paquet.
    // Retourne null si le paquet est vide.
    public DominoTile Draw()
    {
        if (tiles.Count == 0)
            return null;

        DominoTile tile = tiles[0];
        tiles.RemoveAt(0);
        return tile;
    }
}
