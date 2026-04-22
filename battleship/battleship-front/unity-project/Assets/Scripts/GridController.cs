using UnityEngine;

public class GridController : MonoBehaviour
{
    [SerializeField] private int rows = 10;
    [SerializeField] private int cols = 10;
    [SerializeField] private float cellSize = 1f;
    [SerializeField] private GameObject cellPrefab;

    private Renderer[,] cellRenderers;

    private void Start()
    {
        GenerateGrid();
    }

    private void GenerateGrid()
    {
        if (cellPrefab == null)
        {
            Debug.LogWarning("Cell prefab non assigne.");
            return;
        }

        cellRenderers = new Renderer[rows, cols];

        for (int r = 0; r < rows; r++)
        {
            for (int c = 0; c < cols; c++)
            {
                Vector3 position = new Vector3(c * cellSize, 0f, r * cellSize);
                GameObject cell = Instantiate(cellPrefab, position, Quaternion.identity, transform);
                cell.name = $"Cell_{r}_{c}";

                Renderer rendererComponent = cell.GetComponentInChildren<Renderer>();
                if (rendererComponent != null)
                {
                    cellRenderers[r, c] = rendererComponent;
                }
            }
        }
    }

    public void MarkShot(int row, int col, string result)
    {
        if (!IsInside(row, col)) return;

        Renderer targetRenderer = cellRenderers[row, col];
        if (targetRenderer == null) return;

        switch (result)
        {
            case "hit":
                targetRenderer.material.color = Color.red;
                break;
            case "sunk":
                targetRenderer.material.color = new Color(1f, 0.5f, 0f);
                break;
            default:
                targetRenderer.material.color = Color.cyan;
                break;
        }
    }

    private bool IsInside(int row, int col)
    {
        return row >= 0 && row < rows && col >= 0 && col < cols;
    }
}
