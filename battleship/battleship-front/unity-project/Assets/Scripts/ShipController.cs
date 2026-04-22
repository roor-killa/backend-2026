using UnityEngine;

public class ShipController : MonoBehaviour
{
    [SerializeField] private Animator shipAnimator;

    public void PlaceShip(Transform ship, int row, int col, float cellSize)
    {
        if (ship == null) return;

        ship.position = new Vector3(col * cellSize, 0.1f, row * cellSize);
    }

    public void OnShipSunk(int row, int col)
    {
        Debug.Log($"Bateau coule autour de la case ({row}, {col}).");

        if (shipAnimator != null)
        {
            shipAnimator.SetTrigger("Sunk");
        }
    }
}
