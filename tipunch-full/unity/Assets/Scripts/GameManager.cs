// =============================================
//   Ti Punch Master — GameManager.cs
//   Singleton orchestrant le flux de jeu
//   Version 2.0 · Martinique 2026
// =============================================

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    // ─── Singleton ────────────────────────────────────────────────────────────
    public static GameManager Instance { get; private set; }

    // ─── Références ───────────────────────────────────────────────────────────
    [Header("Managers")]
    public UIController    uiController;
    public ClientManager   clientManager;
    public ScoringAPI      scoringAPI;
    public GlassController glassController;

    // ─── État de partie ───────────────────────────────────────────────────────
    [Header("Paramètres de partie")]
    public int totalRounds = 5;

    private int          currentRound = 0;
    private int          totalScore   = 0;
    private ClientData   currentClient;
    private List<ClientData> clientList = new List<ClientData>();

    // ─── Awake / Start ────────────────────────────────────────────────────────
    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    void Start()
    {
        StartCoroutine(LoadClientsAndBegin());
    }

    // ─── Chargement des clients depuis l'API ──────────────────────────────────
    private IEnumerator LoadClientsAndBegin()
    {
        uiController?.ShowLoading(true);

        yield return StartCoroutine(scoringAPI.GetClients(
            onSuccess: (clients) =>
            {
                clientList = clients;
                ShuffleList(clientList);
                Debug.Log($"[GameManager] {clientList.Count} clients chargés depuis l'API.");
                uiController?.ShowLoading(false);
                StartRound();
            },
            onError: (error) =>
            {
                Debug.LogWarning($"[GameManager] API indisponible ({error}). Mode offline.");
                clientList = scoringAPI.GetOfflineClients();
                ShuffleList(clientList);
                uiController?.ShowLoading(false);
                uiController?.ShowOfflineBanner();
                StartRound();
            }
        ));
    }

    // ─── Démarrer une manche ──────────────────────────────────────────────────
    public void StartRound()
    {
        if (currentRound >= totalRounds)
        {
            EndGame();
            return;
        }

        currentClient = clientList[currentRound % clientList.Count];

        Debug.Log($"[GameManager] Manche {currentRound + 1}/{totalRounds} — Client : {currentClient.name}");

        uiController?.UpdateRoundIndicator(currentRound, totalRounds);
        uiController?.UpdateScore(totalScore);
        uiController?.DisplayClient(currentClient);
        glassController?.ResetGlass();
        uiController?.BuildSliders(currentClient.cocktail);
        uiController?.SetServeButtonInteractable(true);
    }

    // ─── Servir le cocktail ───────────────────────────────────────────────────
    public void ServecocktaiL(Dictionary<string, float> dosages)
    {
        uiController?.SetServeButtonInteractable(false);

        var request = new ScoreRequestData
        {
            client_id = currentClient.id,
            cocktail  = currentClient.cocktail,
            dosages   = dosages
        };

        StartCoroutine(scoringAPI.PostScore(
            request,
            onSuccess: (response) =>
            {
                totalScore += response.score;
                Debug.Log($"[GameManager] Score manche : {response.score} | Total : {totalScore}");
                uiController?.ShowFeedback(response, currentClient);
            },
            onError: (error) =>
            {
                Debug.LogWarning($"[GameManager] Erreur scoring API : {error}. Calcul local.");
                var localResponse = scoringAPI.CalculateScoreLocally(request);
                totalScore += localResponse.score;
                uiController?.ShowFeedback(localResponse, currentClient);
            }
        ));
    }

    // ─── Manche suivante ──────────────────────────────────────────────────────
    public void NextRound()
    {
        currentRound++;
        uiController?.HideFeedback();
        StartRound();
    }

    // ─── Fin de partie ────────────────────────────────────────────────────────
    private void EndGame()
    {
        Debug.Log($"[GameManager] Partie terminée ! Score final : {totalScore}");

        StartCoroutine(scoringAPI.PostLeaderboard(
            totalScore,
            onSuccess: (rank) =>
            {
                Debug.Log($"[GameManager] Score soumis au classement. Rang : {rank}");
            },
            onError: (error) =>
            {
                Debug.LogWarning($"[GameManager] Impossible de soumettre le classement : {error}");
            }
        ));

        SceneManager.LoadScene("Leaderboard");
    }

    // ─── Accesseurs ───────────────────────────────────────────────────────────
    public int   GetTotalScore()   => totalScore;
    public int   GetCurrentRound() => currentRound;
    public ClientData GetCurrentClient() => currentClient;

    // ─── Utils ────────────────────────────────────────────────────────────────
    private void ShuffleList<T>(List<T> list)
    {
        for (int i = list.Count - 1; i > 0; i--)
        {
            int j = Random.Range(0, i + 1);
            (list[i], list[j]) = (list[j], list[i]);
        }
    }
}
