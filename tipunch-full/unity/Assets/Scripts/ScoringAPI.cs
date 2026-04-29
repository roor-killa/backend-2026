// =============================================
//   Ti Punch Master — ScoringAPI.cs
//   Communication HTTP avec le backend FastAPI
//   Version 2.0 · Martinique 2026
// =============================================

using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

public class ScoringAPI : MonoBehaviour
{
    // ─── Configuration ────────────────────────────────────────────────────────
    [Header("Configuration API")]
    public string baseUrl     = "http://localhost:8000";
    public float  timeoutSecs = 5f;

    [Header("Joueur")]
    public string playerName = "Barman";

    // ─── GET /clients ─────────────────────────────────────────────────────────
    public IEnumerator GetClients(
        Action<List<ClientData>> onSuccess,
        Action<string>           onError)
    {
        string url = $"{baseUrl}/clients";
        using var req = UnityWebRequest.Get(url);
        req.timeout = (int)timeoutSecs;

        yield return req.SendWebRequest();

        if (req.result == UnityWebRequest.Result.Success)
        {
            try
            {
                var wrapper = JsonUtility.FromJson<ClientListResponse>(req.downloadHandler.text);
                onSuccess?.Invoke(wrapper.clients);
            }
            catch (Exception e)
            {
                onError?.Invoke($"Erreur parsing JSON : {e.Message}");
            }
        }
        else
        {
            onError?.Invoke(req.error ?? "Erreur réseau inconnue");
        }
    }

    // ─── POST /score ──────────────────────────────────────────────────────────
    public IEnumerator PostScore(
        ScoreRequestData         request,
        Action<ScoreResponseData> onSuccess,
        Action<string>            onError)
    {
        string url     = $"{baseUrl}/score";
        string payload = JsonUtility.ToJson(request);

        using var req = new UnityWebRequest(url, "POST");
        req.uploadHandler   = new UploadHandlerRaw(Encoding.UTF8.GetBytes(payload));
        req.downloadHandler = new DownloadHandlerBuffer();
        req.SetRequestHeader("Content-Type", "application/json");
        req.timeout = (int)timeoutSecs;

        yield return req.SendWebRequest();

        if (req.result == UnityWebRequest.Result.Success)
        {
            try
            {
                var response = JsonUtility.FromJson<ScoreResponseData>(req.downloadHandler.text);
                onSuccess?.Invoke(response);
            }
            catch (Exception e)
            {
                onError?.Invoke($"Erreur parsing réponse score : {e.Message}");
            }
        }
        else
        {
            onError?.Invoke(req.error ?? "Erreur réseau");
        }
    }

    // ─── GET /leaderboard ─────────────────────────────────────────────────────
    public IEnumerator GetLeaderboard(
        Action<List<LeaderboardEntryData>> onSuccess,
        Action<string>                     onError)
    {
        string url = $"{baseUrl}/leaderboard";
        using var req = UnityWebRequest.Get(url);
        req.timeout = (int)timeoutSecs;

        yield return req.SendWebRequest();

        if (req.result == UnityWebRequest.Result.Success)
        {
            try
            {
                var wrapper = JsonUtility.FromJson<LeaderboardResponse>(req.downloadHandler.text);
                onSuccess?.Invoke(wrapper.leaderboard);
            }
            catch (Exception e)
            {
                onError?.Invoke($"Erreur parsing classement : {e.Message}");
            }
        }
        else
        {
            onError?.Invoke(req.error ?? "Erreur réseau");
        }
    }

    // ─── POST /leaderboard ────────────────────────────────────────────────────
    public IEnumerator PostLeaderboard(
        int            score,
        Action<int>    onSuccess,
        Action<string> onError)
    {
        string url = $"{baseUrl}/leaderboard";
        var body = new LeaderboardPostData { player_name = playerName, score = score };
        string payload = JsonUtility.ToJson(body);

        using var req = new UnityWebRequest(url, "POST");
        req.uploadHandler   = new UploadHandlerRaw(Encoding.UTF8.GetBytes(payload));
        req.downloadHandler = new DownloadHandlerBuffer();
        req.SetRequestHeader("Content-Type", "application/json");
        req.timeout = (int)timeoutSecs;

        yield return req.SendWebRequest();

        if (req.result == UnityWebRequest.Result.Success)
        {
            try
            {
                var res = JsonUtility.FromJson<LeaderboardPostResponse>(req.downloadHandler.text);
                onSuccess?.Invoke(res.rank);
            }
            catch (Exception e)
            {
                onError?.Invoke(e.Message);
            }
        }
        else
        {
            onError?.Invoke(req.error ?? "Erreur réseau");
        }
    }

    // ─── Mode offline : calcul local du score ─────────────────────────────────
    public ScoreResponseData CalculateScoreLocally(ScoreRequestData request)
    {
        // Recettes embarquées pour le mode offline
        var recipes = OfflineRecipes.Get();
        if (!recipes.TryGetValue(request.cocktail, out var recipe))
        {
            return new ScoreResponseData { score = 5, feedback = "Recette inconnue en mode offline." };
        }

        float totalDiff  = 0f;
        float tolerance  = recipe.tolerance;

        foreach (var kv in recipe.target)
        {
            float actual = 0f;
            // Parcours manuel du dictionnaire sérialisable
            for (int i = 0; i < request.dosages.keys.Count; i++)
                if (request.dosages.keys[i] == kv.Key) { actual = request.dosages.values[i]; break; }

            totalDiff += Mathf.Abs(actual - kv.Value);
        }

        int score;
        if      (totalDiff == 0)                 score = 100;
        else if (totalDiff <= tolerance)          score = 85;
        else if (totalDiff <= tolerance * 2)      score = 65;
        else if (totalDiff <= tolerance * 3 + 1)  score = 40;
        else if (totalDiff <= tolerance * 4 + 2)  score = 20;
        else                                      score = 5;

        string feedback = score switch
        {
            100 => "Parfait ! (mode offline)",
            85  => "Très bon ! (mode offline)",
            65  => "Pas mal. (mode offline)",
            40  => "Approximatif. (mode offline)",
            20  => "Raté. (mode offline)",
            _   => "Non, non, non... (mode offline)"
        };

        return new ScoreResponseData
        {
            score    = score,
            feedback = feedback,
            target   = new SerializableDictionary<string, float>(recipe.target),
        };
    }

    // ─── Clients offline embarqués ────────────────────────────────────────────
    public List<ClientData> GetOfflineClients()
    {
        return OfflineClients.Get();
    }
}

// ─── Data structures ─────────────────────────────────────────────────────────

[Serializable]
public class ClientData
{
    public string id;
    public string name;
    public string avatar;
    public string difficulty;
    public string dialogue;
    public string cocktail;
}

[Serializable]
public class ClientListResponse
{
    public List<ClientData> clients;
    public int count;
}

[Serializable]
public class ScoreRequestData
{
    public string client_id;
    public string cocktail;
    public SerializableDictionary<string, float> dosages;
}

[Serializable]
public class ScoreResponseData
{
    public int    score;
    public string feedback;
    public SerializableDictionary<string, float> target;
    public SerializableDictionary<string, float> diffs;
    public float  total_diff;
}

[Serializable]
public class LeaderboardEntryData
{
    public string player_name;
    public int    score;
    public string date;
}

[Serializable]
public class LeaderboardResponse
{
    public List<LeaderboardEntryData> leaderboard;
    public int count;
}

[Serializable]
public class LeaderboardPostData
{
    public string player_name;
    public int    score;
}

[Serializable]
public class LeaderboardPostResponse
{
    public string message;
    public int    rank;
}

/// <summary>
/// Dictionnaire sérialisable par JsonUtility (qui ne supporte pas Dictionary<>).
/// </summary>
[Serializable]
public class SerializableDictionary<TKey, TValue>
{
    public List<TKey>   keys   = new();
    public List<TValue> values = new();

    public SerializableDictionary() {}

    public SerializableDictionary(Dictionary<TKey, TValue> dict)
    {
        foreach (var kv in dict) { keys.Add(kv.Key); values.Add(kv.Value); }
    }

    public Dictionary<TKey, TValue> ToDictionary()
    {
        var d = new Dictionary<TKey, TValue>();
        for (int i = 0; i < keys.Count; i++) d[keys[i]] = values[i];
        return d;
    }

    public bool TryGet(TKey key, out TValue value)
    {
        int idx = keys.IndexOf(key);
        if (idx >= 0) { value = values[idx]; return true; }
        value = default; return false;
    }
}
