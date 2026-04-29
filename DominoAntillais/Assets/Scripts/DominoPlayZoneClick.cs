using UnityEngine;

// Script pose sur les zones "GAUCHE" et "DROITE" du plateau.
// Il permet de jouer le domino selectionne du cote choisi.
public class DominoPlayZoneClick : MonoBehaviour
{
    // GameManager qui gere la logique de jeu.
    private GameManager gameManager;

    // true = zone droite, false = zone gauche.
    private bool playRight;

    // Configure la zone apres sa creation.
    public void Initialize(GameManager manager, bool rightSide)
    {
        gameManager = manager;
        playRight = rightSide;
    }

    // Clic direct sur la zone apres avoir selectionne un domino.
    private void OnMouseDown()
    {
        if (gameManager == null)
            return;

        gameManager.OnPlayZoneClicked(playRight);
    }

    // Quand la souris passe sur la zone, le GameManager le retient.
    // Cela sert au clic-glisser.
    private void OnMouseEnter()
    {
        if (gameManager == null)
            return;

        gameManager.OnPlayZoneHoverChanged(playRight, true);
    }

    // Quand la souris sort de la zone, on retire le survol.
    private void OnMouseExit()
    {
        if (gameManager == null)
            return;

        gameManager.OnPlayZoneHoverChanged(playRight, false);
    }
}
