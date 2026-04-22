using UnityEngine;

[System.Serializable]
public class ShotResultPayload
{
    public int row;
    public int col;
    public string result = "miss";
}

public class GameManager : MonoBehaviour
{
    [SerializeField] private GridController gridController;
    [SerializeField] private ShipController shipController;
    [SerializeField] private ShotEffect shotEffect;
    [SerializeField] private JSBridge jsBridge;

    public void OnShotResult(string shotResultJson)
    {
        if (string.IsNullOrWhiteSpace(shotResultJson))
        {
            Debug.LogWarning("OnShotResult recu avec un payload vide.");
            return;
        }

        ShotResultPayload payload;

        try
        {
            payload = JsonUtility.FromJson<ShotResultPayload>(shotResultJson);
        }
        catch
        {
            Debug.LogWarning("Payload JSON invalide: " + shotResultJson);
            return;
        }

        if (payload == null)
        {
            Debug.LogWarning("Payload deserialise null.");
            return;
        }

        gridController?.MarkShot(payload.row, payload.col, payload.result);
        shotEffect?.PlayShotResult(payload.row, payload.col, payload.result);

        if (payload.result == "sunk")
        {
            shipController?.OnShipSunk(payload.row, payload.col);
        }
    }

    public void OnGridCellSelected(int row, int col)
    {
        jsBridge?.NotifyCellSelected(row, col);
    }
}
