using UnityEngine;

public class JSBridge : MonoBehaviour
{
    public void NotifyCellSelected(int row, int col)
    {
#if UNITY_WEBGL && !UNITY_EDITOR
#pragma warning disable 0618
        Application.ExternalCall("onCellSelected", row, col);
#pragma warning restore 0618
#else
        Debug.Log($"[JSBridge] onCellSelected({row}, {col})");
#endif
    }
}
