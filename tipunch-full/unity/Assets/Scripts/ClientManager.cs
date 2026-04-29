// =============================================
//   Ti Punch Master — ClientManager.cs
//   Gestion des animations et états des clients
//   Version 2.0 · Martinique 2026
// =============================================

using System.Collections;
using UnityEngine;

public class ClientManager : MonoBehaviour
{
    [Header("Animator du client affiché")]
    public Animator clientAnimator;

    [Header("Audio Réactions")]
    public AudioSource audioSource;
    public AudioClip[] happyClips;    // Sons de satisfaction (score >= 85)
    public AudioClip[] okClips;       // Sons neutres (score 40-65)
    public AudioClip[] sadClips;      // Sons de déception (score <= 20)

    // Paramètres de l'Animator (à configurer dans Unity Animator)
    private static readonly int StateParam = Animator.StringToHash("ClientState");
    // 0 = Idle/Attente, 1 = Content, 2 = Neutre, 3 = Déçu

    /// <summary>
    /// Réaction visuelle et audio du client selon le score obtenu.
    /// </summary>
    public void ReactToScore(int score)
    {
        int animState;
        AudioClip[] clips;

        if (score >= 85)
        {
            animState = 1;    // Content
            clips     = happyClips;
        }
        else if (score >= 40)
        {
            animState = 2;    // Neutre
            clips     = okClips;
        }
        else
        {
            animState = 3;    // Déçu
            clips     = sadClips;
        }

        clientAnimator?.SetInteger(StateParam, animState);

        // Joue un son aléatoire de la catégorie correspondante
        if (audioSource != null && clips is { Length: > 0 })
        {
            var clip = clips[Random.Range(0, clips.Length)];
            if (clip != null) audioSource.PlayOneShot(clip);
        }
    }

    /// <summary>
    /// Remet le client en état d'attente (idle).
    /// </summary>
    public void SetIdle()
    {
        clientAnimator?.SetInteger(StateParam, 0);
    }

    /// <summary>
    /// Coroutine : animation d'entrée du client.
    /// </summary>
    public IEnumerator PlayEnterAnimation()
    {
        clientAnimator?.SetTrigger("Enter");
        yield return new WaitForSeconds(0.5f);
    }

    /// <summary>
    /// Coroutine : animation de sortie du client.
    /// </summary>
    public IEnumerator PlayExitAnimation()
    {
        clientAnimator?.SetTrigger("Exit");
        yield return new WaitForSeconds(0.4f);
    }
}
