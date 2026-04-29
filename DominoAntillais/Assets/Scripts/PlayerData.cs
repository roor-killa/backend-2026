using System.Collections.Generic;

// Donnees d'un joueur pendant une manche.
// Pour l'instant il contient seulement un nom et une main de dominos.
public class PlayerData
{
    // Nom affiche dans les logs et dans l'UI.
    public string Name;

    // Liste des dominos que le joueur possede encore.
    public List<DominoTile> Hand = new List<DominoTile>();

    public PlayerData(string name)
    {
        Name = name;
    }

    // Ajoute un domino a la main du joueur.
    public void AddTile(DominoTile tile)
    {
        if (tile != null)
            Hand.Add(tile);
    }

    // Retire un domino de la main du joueur.
    public void RemoveTile(DominoTile tile)
    {
        Hand.Remove(tile);
    }

    // Verifie si le joueur peut jouer sur une des deux extremites du plateau.
    // leftEnd et rightEnd sont les valeurs ouvertes a gauche et a droite.
    public bool HasPlayableTile(int leftEnd, int rightEnd)
    {
        if (Hand.Count == 0)
            return false;

        // Si la table est vide, n'importe quel domino pourrait etre joue.
        if (leftEnd == -1 && rightEnd == -1)
            return true;

        foreach (DominoTile tile in Hand)
        {
            if (tile.Matches(leftEnd) || tile.Matches(rightEnd))
                return true;
        }

        return false;
    }

    // Cherche le plus gros double dans la main du joueur.
    // Exemple : si le joueur a [3|3] et [6|6], on retourne [6|6].
    public DominoTile FindHighestDouble()
    {
        DominoTile best = null;

        foreach (DominoTile tile in Hand)
        {
            if (!tile.IsDouble())
                continue;

            if (best == null || tile.Left > best.Left)
                best = tile;
        }

        return best;
    }
}
