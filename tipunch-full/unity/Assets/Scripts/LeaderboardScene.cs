// =============================================
//   Ti Punch Master — LeaderboardScene.cs
//   Contrôleur de la scène Leaderboard
//   Version 2.0 · Martinique 2026
// =============================================

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using TMPro;

public class LeaderboardScene : MonoBehaviour
{
    [Header("UI")]
    public TextMeshProUGUI finalScoreText;
    public TextMeshProUGUI finalScoreLabelText;
    public Transform       leaderboardParent;
    public GameObject      leaderboardRowPrefab;
    public Button          replayButton;
    public Button          menuButton;
    public GameObject      loadingSpinner;

    private ScoringAPI scoringAPI;

    void Start()
    {
        // Récupère le ScoringAPI (peut être sur le GameManager persistant)
        scoringAPI = FindObjectOfType<ScoringAPI>();

        // Affiche le score final
        int total = GameManager.Instance?.GetTotalScore() ?? 0;
        if (finalScoreText != null)
            finalScoreText.text = $"{total} pts";

        // Charge et affiche le classement
        StartCoroutine(LoadLeaderboard());

        // Boutons
        replayButton?.onClick.AddListener(() => SceneManager.LoadScene("GameScene"));
        menuButton?.onClick.AddListener(()  => SceneManager.LoadScene("MainMenu"));
    }

    private IEnumerator LoadLeaderboard()
    {
        loadingSpinner?.SetActive(true);

        yield return StartCoroutine(scoringAPI.GetLeaderboard(
            onSuccess: (entries) =>
            {
                loadingSpinner?.SetActive(false);
                BuildLeaderboard(entries);
            },
            onError: (error) =>
            {
                loadingSpinner?.SetActive(false);
                Debug.LogWarning($"[LeaderboardScene] Erreur classement API : {error}");
                BuildLeaderboard(new List<LeaderboardEntryData>());
            }
        ));
    }

    private void BuildLeaderboard(List<LeaderboardEntryData> entries)
    {
        if (leaderboardParent == null || leaderboardRowPrefab == null) return;

        foreach (Transform t in leaderboardParent) Destroy(t.gameObject);

        string[] medals = { "🥇", "🥈", "🥉", "4.", "5." };

        if (entries.Count == 0)
        {
            var emptyGo  = Instantiate(leaderboardRowPrefab, leaderboardParent);
            var emptyTxt = emptyGo.GetComponentInChildren<TextMeshProUGUI>();
            if (emptyTxt != null) emptyTxt.text = "Aucun score. Joue ta première partie !";
            return;
        }

        for (int i = 0; i < Mathf.Min(entries.Count, 5); i++)
        {
            var entry = entries[i];
            var row   = Instantiate(leaderboardRowPrefab, leaderboardParent);

            var rankText   = row.transform.Find("Rank")?.GetComponent<TextMeshProUGUI>();
            var nameText   = row.transform.Find("Name")?.GetComponent<TextMeshProUGUI>();
            var scoreText  = row.transform.Find("Score")?.GetComponent<TextMeshProUGUI>();
            var dateText   = row.transform.Find("Date")?.GetComponent<TextMeshProUGUI>();

            if (rankText  != null) rankText.text  = i < medals.Length ? medals[i] : $"{i + 1}.";
            if (nameText  != null) nameText.text  = entry.player_name ?? "Barman";
            if (scoreText != null) scoreText.text = $"{entry.score} pts";
            if (dateText  != null) dateText.text  = entry.date ?? "";
        }
    }
}
