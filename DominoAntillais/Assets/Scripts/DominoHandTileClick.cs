using UnityEngine;
using UnityEngine.InputSystem;

// Petit script place sur chaque domino de la main du Joueur 1.
// Il transmet le clic au GameManager avec l'index du domino dans la main.
public class DominoHandTileClick : MonoBehaviour
{
    // GameManager qui gere la logique de jeu.
    private GameManager gameManager;

    // Position du domino dans la main du Joueur 1.
    private int handIndex;

    // Si false, le domino ignore les clics.
    private bool isClickable;

    // Initialise le script apres creation du domino visuel.
    public void Initialize(GameManager manager, int index, bool clickable)
    {
        gameManager = manager;
        handIndex = index;
        isClickable = clickable;
    }

    // Unity appelle cette methode quand on clique sur le collider du domino.
    private void OnMouseDown()
    {
        if (!isClickable || gameManager == null)
            return;

        // On selectionne le domino. Ensuite le joueur choisit gauche/droite.
        gameManager.OnPlayerHandTilePressed(handIndex);
    }

    // Si le joueur a clique puis glisse vers une zone gauche/droite,
    // le relachement de la souris essaie de poser le domino dans cette zone.
    private void OnMouseUp()
    {
        if (!isClickable || gameManager == null)
            return;

        gameManager.OnPlayerHandTileReleased(handIndex);
    }

    // Pendant le drag, on envoie la position monde de la souris au GameManager.
    private void OnMouseDrag()
    {
        if (!isClickable || gameManager == null)
            return;

        Camera camera = Camera.main;

        if (camera == null || Mouse.current == null)
            return;

        Vector2 mousePosition = Mouse.current.position.ReadValue();
        Vector3 screenPosition = new Vector3(
            mousePosition.x,
            mousePosition.y,
            Mathf.Abs(camera.transform.position.z));
        Vector3 worldPosition = camera.ScreenToWorldPoint(screenPosition);

        gameManager.OnPlayerHandTileDragged(handIndex, worldPosition);
    }
}
