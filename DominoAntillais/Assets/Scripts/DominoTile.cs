using System;

// Une tuile de domino simple.
// Exemple : Left = 6 et Right = 4 represente le domino [6|4].
[Serializable]
public class DominoTile
{
    // Valeur du cote gauche du domino.
    public int Left;

    // Valeur du cote droit du domino.
    public int Right;

    // Constructeur appele quand on cree un nouveau domino.
    public DominoTile(int left, int right)
    {
        Left = left;
        Right = right;
    }

    // Retourne true si les deux cotes ont la meme valeur.
    // Exemple : [6|6], [3|3], [0|0].
    public bool IsDouble()
    {
        return Left == Right;
    }

    // Additionne les deux valeurs du domino.
    // Cette methode sert pour les fins de manche aux points.
    public int TotalValue()
    {
        return Left + Right;
    }

    // Verifie si ce domino contient une valeur donnee.
    // Exemple : [2|5].Matches(5) retourne true.
    public bool Matches(int value)
    {
        return Left == value || Right == value;
    }

    // Inverse le sens du domino.
    // Exemple : [3|5] devient [5|3].
    public void Flip()
    {
        int temp = Left;
        Left = Right;
        Right = temp;
    }

    // Format utilise dans la console Unity.
    public override string ToString()
    {
        return "[" + Left + "|" + Right + "]";
    }
}
