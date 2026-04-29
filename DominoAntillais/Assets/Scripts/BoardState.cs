using System.Collections.Generic;
using UnityEngine;

// Etat logique du plateau.
// Cette classe ne dessine rien : elle garde seulement la chaine de dominos.
public class BoardState
{
    // Liste des dominos poses sur la table, de gauche a droite.
    public List<DominoTile> Chain = new List<DominoTile>();

    // Valeur ouverte a gauche de la chaine.
    // Si la chaine est vide, on retourne -1 pour dire "pas de valeur".
    public int LeftEnd
    {
        get
        {
            if (Chain.Count == 0)
                return -1;

            return Chain[0].Left;
        }
    }

    // Valeur ouverte a droite de la chaine.
    // Si la chaine est vide, on retourne -1 pour dire "pas de valeur".
    public int RightEnd
    {
        get
        {
            if (Chain.Count == 0)
                return -1;

            return Chain[Chain.Count - 1].Right;
        }
    }

    // Pose le tout premier domino de la manche.
    // On refuse si un domino est deja pose.
    public bool PlayFirstTile(DominoTile tile)
    {
        if (Chain.Count > 0)
            return false;

        Chain.Add(tile);
        return true;
    }

    // Essaie de poser un domino a gauche.
    // Si le domino est dans le mauvais sens, on le retourne avec Flip().
    public bool TryPlayLeft(DominoTile tile)
    {
        if (Chain.Count == 0)
        {
            Chain.Add(tile);
            return true;
        }

        int currentLeft = LeftEnd;

        // Exemple : chaine commence par 4, domino [2|4].
        // Le cote droit du domino touche le 4, donc il peut aller a gauche.
        if (tile.Right == currentLeft)
        {
            Chain.Insert(0, tile);
            return true;
        }

        // Exemple : chaine commence par 4, domino [4|2].
        // Il faut le retourner en [2|4] avant de l'inserer a gauche.
        if (tile.Left == currentLeft)
        {
            tile.Flip();
            Chain.Insert(0, tile);
            return true;
        }

        return false;
    }

    // Essaie de poser un domino a droite.
    // Meme principe que TryPlayLeft, mais avec l'extremite droite.
    public bool TryPlayRight(DominoTile tile)
    {
        if (Chain.Count == 0)
        {
            Chain.Add(tile);
            return true;
        }

        int currentRight = RightEnd;

        // Exemple : chaine finit par 5, domino [5|1].
        // Le cote gauche du domino touche le 5, donc il peut aller a droite.
        if (tile.Left == currentRight)
        {
            Chain.Add(tile);
            return true;
        }

        // Exemple : chaine finit par 5, domino [1|5].
        // Il faut le retourner en [5|1] avant de l'ajouter a droite.
        if (tile.Right == currentRight)
        {
            tile.Flip();
            Chain.Add(tile);
            return true;
        }

        return false;
    }

    // Affiche la chaine actuelle dans la console Unity.
    public void PrintBoard()
    {
        string result = "Chaine : ";

        foreach (DominoTile tile in Chain)
        {
            result += tile + " ";
        }

        Debug.Log(result);
    }
}
