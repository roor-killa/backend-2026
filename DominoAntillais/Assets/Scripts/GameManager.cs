using System.Collections.Generic;
using TMPro;
using UnityEngine;

// Script principal du prototype.
// Il gere la partie : distribution, tours, clic du Joueur 1, IA simple,
// fin de manche, score, cochon et chamboule.
public class GameManager : MonoBehaviour
{
    [Header("UI texte ancienne (optionnelle)")]
    // Ces textes viennent de l'ancien prototype.
    // Ils restent utiles pour debugger, mais ils sont caches par defaut.
    public TMP_Text boardText;
    public TMP_Text playerHandText;
    public bool showDebugText = false;

    [Header("Rendu visuel")]
    // Dessine les dominos poses au centre de la table.
    public DominoBoardRenderer boardRenderer;

    // Dessine la main du Joueur 1 en bas de l'ecran.
    public PlayerHandRenderer playerHandRenderer;

    // Affiche le score et l'etat de la partie dans la scene.
    public PrototypeHudRenderer hudRenderer;

    // Affiche les zones gauche/droite pour poser le domino selectionne.
    public PlayZoneRenderer playZoneRenderer;

    // Affiche les mains cachees des Joueurs 2 et 3.
    public OpponentHandsRenderer opponentHandsRenderer;

    // Affiche un petit menu avant la partie pour choisir les regles principales.
    public MatchSetupMenuRenderer setupMenuRenderer;

    [Header("Prototype")]
    // Temps entre deux tours automatiques des IA.
    public float automaticTurnDelay = 2f;

    // Temps maximum pour jouer quand c'est le tour du Joueur 1.
    public float humanTurnTimeLimit = 15f;

    // Temps d'attente avant de relancer une manche apres une fin.
    public float roundRestartDelay = 3f;

    // true  : si tout le monde toque, le plus petit total en main gagne.
    // false : si tout le monde toque, on redistribue sans donner de point.
    public bool playBlockedRoundsAtPoints = true;

    // Langue choisie dans le menu de lancement.
    // Pour le moment, cela sert surtout de base propre pour la future localisation.
    public PrototypeLanguage prototypeLanguage = PrototypeLanguage.French;

    [Header("Drag visuel")]
    // Taille du domino fantome qui suit la souris pendant le drag.
    public Vector2 dragGhostSize = new Vector2(1.34f, 0.66f);

    [Header("Score")]
    // Nombre de manches a gagner pour terminer la partie.
    // Dans ta regle actuelle, on met cochon quand un joueur arrive a 3.
    public int scoreToWinGame = 3;

    // Joueur humain du prototype : 0 = Joueur 1.
    private const int HumanPlayerIndex = 0;

    // Paquet de dominos de la manche actuelle.
    private DominoDeck deck;

    // Etat logique de la table.
    private BoardState board;

    // Les trois joueurs du prototype.
    private List<PlayerData> players;

    // Score de chaque joueur dans la partie actuelle.
    private int[] scores;

    // Index du joueur dont c'est le tour dans la liste players.
    private int currentPlayerIndex;

    // Gagnant de la manche precedente.
    // -1 veut dire qu'on doit commencer avec la regle du plus gros double.
    private int nextRoundStartingPlayerIndex = -1;

    // true si la manche actuelle est commencee par le gagnant de la manche precedente.
    // Dans ce cas, il peut jouer le domino qu'il veut en premier.
    private bool currentRoundStartsFromPreviousWinner;

    // Index du domino central dans board.Chain.
    // Important : quand on ajoute un domino a gauche, le premier domino se decale
    // dans la liste. Cet index permet de garder le premier double fixe au centre.
    private int centerTileIndex;

    // Nombre de joueurs qui ont toque a la suite sans qu'un domino soit pose.
    // Quand cette valeur atteint players.Count, la manche est bloquee.
    private int consecutivePasses;

    // Indique si la manche est terminee.
    private bool roundEnded;

    // Indique si le premier domino de la manche a deja ete pose.
    private bool firstMovePlayed;

    // true quand le jeu attend un clic du Joueur 1.
    private bool waitingForHumanInput;

    // Index du domino selectionne dans la main du Joueur 1.
    // -1 veut dire qu'aucun domino n'est selectionne.
    private int selectedHumanHandIndex = -1;

    // Cote actuellement survole par la souris pour le clic-glisser.
    // -1 = gauche, 1 = droite, 0 = aucun.
    private int hoveredPlaySide;

    // Timer du tour humain.
    private float humanTurnTimeRemaining;
    private bool humanTimerActive;

    // Domino fantome affiche pendant le clic-glisser.
    private GameObject dragGhostObject;
    private DominoTileVisual dragGhostVisual;

    // Message court affiche dans le HUD prototype.
    private string statusMessage = "";

    // Petit conteneur pour le coup aleatoire du timer.
    private struct HumanMoveChoice
    {
        public int HandIndex;
        public bool PreferLeft;

        public HumanMoveChoice(int handIndex, bool preferLeft)
        {
            HandIndex = handIndex;
            PreferLeft = preferLeft;
        }
    }

    // Coup possible pour une IA.
    // Plus Score est petit, plus le coup est considere interessant.
    private struct AiMoveCandidate
    {
        public int HandIndex;
        public bool PreferLeft;
        public int Score;

        public AiMoveCandidate(int handIndex, bool preferLeft, int score)
        {
            HandIndex = handIndex;
            PreferLeft = preferLeft;
            Score = score;
        }
    }

    private void Start()
    {
        // On verifie que les scripts visuels existent avant de lancer la partie.
        // Au lieu de demarrer directement, on ouvre d'abord le menu de reglage.
        EnsureRenderers();
        ShowSetupMenu();
    }

    private void Update()
    {
        UpdateHumanTimer();
    }

    // Cree une nouvelle partie complete, donc remet les scores a zero.
    private void StartMatch()
    {
        players = new List<PlayerData>
        {
            new PlayerData("Joueur 1"),
            new PlayerData("Joueur 2"),
            new PlayerData("Joueur 3")
        };

        scores = new int[players.Count];
        nextRoundStartingPlayerIndex = -1;
        currentRoundStartsFromPreviousWinner = false;
        statusMessage = "Nouvelle partie";

        StartRound();
    }

    // Ouvre le menu de reglage du prototype avant de lancer la partie.
    private void ShowSetupMenu()
    {
        if (setupMenuRenderer == null)
        {
            StartMatch();
            return;
        }

        setupMenuRenderer.Show(this, GetCurrentMatchSetup());
    }

    // Retourne les regles actuellement configurees.
    // Le menu s'en sert pour afficher les bons boutons selectionnes.
    private MatchSetupSelection GetCurrentMatchSetup()
    {
        return new MatchSetupSelection
        {
            ScoreToWin = scoreToWinGame,
            PlayBlockedRoundsAtPoints = playBlockedRoundsAtPoints,
            HumanTurnTimeLimit = humanTurnTimeLimit,
            AutomaticTurnDelay = automaticTurnDelay,
            Language = prototypeLanguage
        };
    }

    // Point d'entree appele par le menu quand le joueur clique sur "Lancer".
    // Le menu choisit quelques regles de base, puis on demarre une vraie partie.
    public void ApplySetupAndStartMatch(MatchSetupSelection selection)
    {
        scoreToWinGame = selection.ScoreToWin;
        playBlockedRoundsAtPoints = selection.PlayBlockedRoundsAtPoints;
        humanTurnTimeLimit = selection.HumanTurnTimeLimit;
        automaticTurnDelay = selection.AutomaticTurnDelay;
        prototypeLanguage = selection.Language;

        StartMatch();
    }

    // Cree une nouvelle manche sans remettre les scores a zero.
    private void StartRound()
    {
        // Annule les Invoke de la manche precedente avant d'en relancer une.
        CancelInvoke();

        deck = new DominoDeck();
        board = new BoardState();

        currentPlayerIndex = 0;
        currentRoundStartsFromPreviousWinner = nextRoundStartingPlayerIndex >= 0;
        centerTileIndex = 0;
        consecutivePasses = 0;
        roundEnded = false;
        firstMovePlayed = false;
        waitingForHumanInput = false;
        selectedHumanHandIndex = -1;
        hoveredPlaySide = 0;
        humanTimerActive = false;
        humanTurnTimeRemaining = humanTurnTimeLimit;

        // On vide les mains avant de redistribuer.
        foreach (PlayerData player in players)
        {
            player.Hand.Clear();
        }

        deck.Shuffle();
        DealTiles();

        if (currentRoundStartsFromPreviousWinner)
        {
            currentPlayerIndex = nextRoundStartingPlayerIndex;
            statusMessage = players[currentPlayerIndex].Name + " commence car il a gagne la manche precedente";
            Debug.Log(statusMessage);
        }
        else
        {
            // Premiere manche : le premier joueur est celui qui a le plus gros double.
            // Si aucun double n'est trouve, on recommence la distribution.
            if (!ChooseStartingPlayer())
            {
                StartRound();
                return;
            }
        }

        PrintHands();
        UpdateUI();
        BeginTurn();
    }

    // Ajoute automatiquement les renderers s'ils ne sont pas deja presents.
    // Comme ca, le prototype fonctionne meme si rien n'est branche dans l'Inspector.
    private void EnsureRenderers()
    {
        if (boardRenderer == null)
            boardRenderer = GetComponent<DominoBoardRenderer>();

        if (boardRenderer == null)
            boardRenderer = gameObject.AddComponent<DominoBoardRenderer>();

        if (playerHandRenderer == null)
            playerHandRenderer = GetComponent<PlayerHandRenderer>();

        if (playerHandRenderer == null)
            playerHandRenderer = gameObject.AddComponent<PlayerHandRenderer>();

        if (hudRenderer == null)
            hudRenderer = GetComponent<PrototypeHudRenderer>();

        if (hudRenderer == null)
            hudRenderer = gameObject.AddComponent<PrototypeHudRenderer>();

        if (playZoneRenderer == null)
            playZoneRenderer = GetComponent<PlayZoneRenderer>();

        if (playZoneRenderer == null)
            playZoneRenderer = gameObject.AddComponent<PlayZoneRenderer>();

        if (opponentHandsRenderer == null)
            opponentHandsRenderer = GetComponent<OpponentHandsRenderer>();

        if (opponentHandsRenderer == null)
            opponentHandsRenderer = gameObject.AddComponent<OpponentHandsRenderer>();

        if (setupMenuRenderer == null)
            setupMenuRenderer = GetComponent<MatchSetupMenuRenderer>();

        if (setupMenuRenderer == null)
            setupMenuRenderer = gameObject.AddComponent<MatchSetupMenuRenderer>();
    }

    // Distribue 9 dominos a chaque joueur.
    // A 3 joueurs, cela fait 27 dominos distribues sur les 28 du paquet.
    private void DealTiles()
    {
        for (int i = 0; i < 9; i++)
        {
            foreach (PlayerData player in players)
            {
                player.AddTile(deck.Draw());
            }
        }
    }

    // Cherche le joueur qui possede le plus gros double.
    // Ordre attendu : [6|6], sinon [5|5], sinon [4|4], etc.
    private bool ChooseStartingPlayer()
    {
        int bestDoubleValue = -1;
        int startingIndex = 0;

        for (int i = 0; i < players.Count; i++)
        {
            DominoTile highestDouble = players[i].FindHighestDouble();

            if (highestDouble != null && highestDouble.Left > bestDoubleValue)
            {
                bestDoubleValue = highestDouble.Left;
                startingIndex = i;
            }
        }

        currentPlayerIndex = startingIndex;

        if (bestDoubleValue >= 0)
        {
            statusMessage = players[currentPlayerIndex].Name + " commence avec le double " +
                            bestDoubleValue + "-" + bestDoubleValue;
            Debug.Log(statusMessage);
            return true;
        }

        Debug.Log("Personne n'a de double. La manche est redistribuee.");
        return false;
    }

    // Demarre le tour du joueur actuel.
    private void BeginTurn()
    {
        if (roundEnded)
            return;

        PlayerData player = players[currentPlayerIndex];
        Debug.Log("Tour de " + player.Name);

        // Cas Joueur 1 : on attend un clic sur un domino jouable.
        if (currentPlayerIndex == HumanPlayerIndex)
        {
            waitingForHumanInput = true;
            selectedHumanHandIndex = -1;
            hoveredPlaySide = 0;
            humanTurnTimeRemaining = humanTurnTimeLimit;
            humanTimerActive = true;

            // Si Joueur 1 ne peut rien jouer, il toque automatiquement.
            if (!HasPlayableMove(player))
            {
                waitingForHumanInput = false;
                humanTimerActive = false;
                CompleteTurn(player, false);
                return;
            }

            statusMessage = "A toi : selectionne un domino jaune puis choisis gauche/droite";
            UpdateUI();
            return;
        }

        // Cas IA : on joue apres un court delai pour voir le tour passer.
        statusMessage = player.Name + " reflechit...";
        UpdateUI();
        Invoke(nameof(PlayAutomaticTurn), automaticTurnDelay);
    }

    // Joue un tour automatique pour les IA.
    // Pour l'instant l'IA joue le premier domino possible.
    private void PlayAutomaticTurn()
    {
        if (roundEnded || waitingForHumanInput)
            return;

        PlayerData player = players[currentPlayerIndex];
        bool played = TryPlayAnyTile(player);
        CompleteTurn(player, played);
    }

    // Methode appelee quand le joueur appuie sur un domino de sa main.
    // Cela selectionne le domino sans encore le jouer.
    public void OnPlayerHandTilePressed(int handIndex)
    {
        if (!waitingForHumanInput || roundEnded || currentPlayerIndex != HumanPlayerIndex)
            return;

        PlayerData player = players[HumanPlayerIndex];

        if (handIndex < 0 || handIndex >= player.Hand.Count)
            return;

        if (!GetPlayableHandIndexes(player).Contains(handIndex))
        {
            statusMessage = "Ce domino ne peut pas etre joue";
            UpdateHud();
            return;
        }

        selectedHumanHandIndex = handIndex;
        statusMessage = "Domino selectionne : choisis GAUCHE ou DROITE";
        ShowDragGhost(player.Hand[handIndex]);

        if (playerHandRenderer != null)
            playerHandRenderer.SetSelectedHandIndex(selectedHumanHandIndex);

        UpdatePlayZones();
        UpdateHud();
    }

    // Methode appelee quand le joueur relache un domino apres un clic-glisser.
    public void OnPlayerHandTileReleased(int handIndex)
    {
        if (!waitingForHumanInput || roundEnded)
            return;

        HideDragGhost();

        if (selectedHumanHandIndex != handIndex || hoveredPlaySide == 0)
            return;

        TryPlaySelectedHumanTile(hoveredPlaySide > 0);
    }

    // Methode appelee pendant le clic-glisser.
    // Le domino fantome suit la souris en coordonnees monde.
    public void OnPlayerHandTileDragged(int handIndex, Vector3 worldPosition)
    {
        if (!waitingForHumanInput || roundEnded || selectedHumanHandIndex != handIndex)
            return;

        if (dragGhostObject == null)
            return;

        worldPosition.z = -0.35f;
        dragGhostObject.transform.position = worldPosition;
    }

    // Methode appelee quand le joueur clique sur une zone GAUCHE ou DROITE.
    public void OnPlayZoneClicked(bool playRight)
    {
        if (!waitingForHumanInput || roundEnded)
            return;

        TryPlaySelectedHumanTile(playRight);
    }

    // Retient quelle zone est survolee pour le clic-glisser.
    public void OnPlayZoneHoverChanged(bool playRight, bool isHovered)
    {
        if (!isHovered)
        {
            if ((playRight && hoveredPlaySide == 1) || (!playRight && hoveredPlaySide == -1))
                hoveredPlaySide = 0;

            return;
        }

        hoveredPlaySide = playRight ? 1 : -1;
    }

    // Cree ou met a jour le domino fantome du drag.
    private void ShowDragGhost(DominoTile tile)
    {
        if (tile == null)
            return;

        if (dragGhostObject == null)
        {
            dragGhostVisual = DominoTileVisual.CreateRuntimeDomino(
                transform,
                "Dragged Domino Ghost",
                dragGhostSize,
                80);
            dragGhostObject = dragGhostVisual.gameObject;
            dragGhostObject.transform.localRotation = Quaternion.Euler(0f, 0f, 90f);
        }

        dragGhostVisual.SetValues(tile.Left, tile.Right);
        dragGhostVisual.SetHandState(false, true);
        dragGhostObject.SetActive(true);
    }

    // Cache le domino fantome quand le drag se termine.
    private void HideDragGhost()
    {
        if (dragGhostObject != null)
            dragGhostObject.SetActive(false);
    }

    // Termine un tour apres un coup ou une toque.
    private void CompleteTurn(PlayerData player, bool played)
    {
        if (currentPlayerIndex == HumanPlayerIndex)
        {
            humanTimerActive = false;
            selectedHumanHandIndex = -1;
            hoveredPlaySide = 0;
            HideDragGhost();
        }

        if (played)
        {
            // Des qu'un joueur pose un domino, la serie de toques est cassee.
            consecutivePasses = 0;
        }
        else
        {
            // Le joueur ne peut pas jouer : il toque.
            consecutivePasses++;
            statusMessage = player.Name + " toque";
            Debug.Log(player.Name + " toque. (" + consecutivePasses + "/" + players.Count + ")");

            // Si tout le monde toque a la suite, la manche est bloquee.
            if (consecutivePasses >= players.Count)
            {
                HandleBlockedGame();
                return;
            }
        }

        // Si le joueur n'a plus de dominos, il gagne la manche.
        if (player.Hand.Count == 0)
        {
            HandleRoundWinner(currentPlayerIndex, player.Name + " n'a plus de dominos");
            return;
        }

        board.PrintBoard();
        UpdateUI();
        NextPlayer();
        BeginTurn();
    }

    // Gere le cas "chire" / partie bloquee :
    // personne ne peut jouer apres un tour complet de toques.
    private void HandleBlockedGame()
    {
        roundEnded = true;
        waitingForHumanInput = false;
        humanTimerActive = false;
        selectedHumanHandIndex = -1;
        HideDragGhost();
        Debug.Log("=== PARTIE BLOQUEE : tout le monde a toque ===");

        if (playBlockedRoundsAtPoints)
        {
            int winnerIndex = FindLowestHandWinnerIndex(out int bestScore, out bool tie);

            if (tie || winnerIndex < 0)
            {
                statusMessage = "Egalite aux points : on redistribue";
                Debug.Log(statusMessage);
                UpdateUI();
                Invoke(nameof(StartRound), roundRestartDelay);
                return;
            }

            Debug.Log("*** " + players[winnerIndex].Name + " gagne la manche avec " +
                      bestScore + " points en main ! ***");
            HandleRoundWinner(winnerIndex, "Partie bloquee : plus petite main");
        }
        else
        {
            statusMessage = "Manche bloquee : on redistribue";
            Debug.Log(statusMessage);
            UpdateUI();
            Invoke(nameof(StartRound), roundRestartDelay);
        }
    }

    // Donne le point de manche au gagnant et applique cochon/chamboule si besoin.
    private void HandleRoundWinner(int winnerIndex, string reason)
    {
        roundEnded = true;
        waitingForHumanInput = false;
        humanTimerActive = false;
        selectedHumanHandIndex = -1;
        HideDragGhost();

        // Regle importante : le gagnant d'une manche commence la manche suivante.
        nextRoundStartingPlayerIndex = winnerIndex;

        scores[winnerIndex]++;

        statusMessage = players[winnerIndex].Name + " gagne la manche";
        Debug.Log("*** " + statusMessage + " : " + reason + " ***");
        Debug.Log("Score : " + GetScoreText());

        // Si un joueur atteint 3 points, on regarde qui est reste a 0 :
        // ces joueurs sont cochon.
        if (scores[winnerIndex] >= scoreToWinGame)
        {
            HandleGameWinner(winnerIndex);
            return;
        }

        // Interpretation actuelle du chamboule :
        // si les 3 joueurs ont au moins 1 point, personne ne peut etre cochon,
        // donc tout le monde repart a 0.
        if (AllPlayersHaveAtLeastOnePoint())
        {
            HandleChamboule();
            return;
        }

        UpdateUI();
        Invoke(nameof(StartRound), roundRestartDelay);
    }

    // Gere la fin de partie quand un joueur arrive a 3 points.
    private void HandleGameWinner(int winnerIndex)
    {
        List<string> cochons = new List<string>();

        for (int i = 0; i < scores.Length; i++)
        {
            if (i != winnerIndex && scores[i] == 0)
                cochons.Add(players[i].Name);
        }

        if (cochons.Count > 0)
        {
            statusMessage = players[winnerIndex].Name + " met cochon : " + string.Join(", ", cochons);
        }
        else
        {
            statusMessage = players[winnerIndex].Name + " gagne la partie";
        }

        Debug.Log("*** " + statusMessage + " ***");
        UpdateUI();

        // On relance une nouvelle partie complete apres l'affichage du resultat.
        Invoke(nameof(StartMatch), roundRestartDelay + 1f);
    }

    // Gere le chamboule : tout le monde reprend a zero, puis nouvelle manche.
    private void HandleChamboule()
    {
        for (int i = 0; i < scores.Length; i++)
            scores[i] = 0;

        statusMessage = "Chamboule : tout le monde reprend a 0";
        Debug.Log("*** " + statusMessage + " ***");
        UpdateUI();

        Invoke(nameof(StartRound), roundRestartDelay);
    }

    // Retourne true si chaque joueur a au moins 1 point.
    private bool AllPlayersHaveAtLeastOnePoint()
    {
        foreach (int score in scores)
        {
            if (score <= 0)
                return false;
        }

        return true;
    }

    // Compare les mains des joueurs et retourne celui qui a le moins de points.
    // tie vaut true si plusieurs joueurs ont le meme plus petit total.
    private int FindLowestHandWinnerIndex(out int bestScore, out bool tie)
    {
        bestScore = int.MaxValue;
        tie = false;
        int winnerIndex = -1;

        for (int i = 0; i < players.Count; i++)
        {
            int total = 0;

            foreach (DominoTile tile in players[i].Hand)
                total += tile.TotalValue();

            Debug.Log(players[i].Name + " a " + total + " points en main.");

            if (total < bestScore)
            {
                bestScore = total;
                winnerIndex = i;
                tie = false;
            }
            else if (total == bestScore)
            {
                tie = true;
            }
        }

        return winnerIndex;
    }

    // Essaie de jouer un domino de la main d'une IA.
    // Retourne true si un domino a ete pose, sinon false.
    private bool TryPlayAnyTile(PlayerData player)
    {
        // Si le gagnant de la manche precedente commence, il joue ce qu'il veut.
        if (!firstMovePlayed && board.Chain.Count == 0)
        {
            if (currentRoundStartsFromPreviousWinner)
            {
                if (!TryChooseBestAiMove(player, out AiMoveCandidate firstMove))
                    return false;

                if (PlayFirstTileFromHand(player, firstMove.HandIndex, out DominoTile freeFirstTile))
                {
                    statusMessage = player.Name + " commence avec " + freeFirstTile;
                    Debug.Log(statusMessage);
                    return true;
                }

                return false;
            }

            // Premiere manche : le joueur doit poser son plus gros double au centre.
            DominoTile highestDouble = player.FindHighestDouble();

            if (highestDouble == null)
                return false;

            int highestDoubleIndex = player.Hand.IndexOf(highestDouble);

            if (PlayFirstTileFromHand(player, highestDoubleIndex, out DominoTile playedDouble))
            {
                statusMessage = player.Name + " commence avec " + playedDouble;
                Debug.Log(statusMessage);
                return true;
            }

            return false;
        }

        if (!TryChooseBestAiMove(player, out AiMoveCandidate bestMove))
            return false;

        if (TryPlayTileAtIndex(player, bestMove.HandIndex, bestMove.PreferLeft, out DominoTile playedTile, out string side))
        {
            statusMessage = player.Name + " joue " + playedTile + " a " + side;
            Debug.Log(statusMessage);
            return true;
        }

        return false;
    }

    // Choisit le meilleur coup de l'IA parmi tous les coups legaux.
    // Strategie simple :
    // 1. jouer un gros domino pour garder moins de points en main ;
    // 2. garder des valeurs qui permettent encore de rejouer ensuite ;
    // 3. leger bonus si le coup joue un double.
    private bool TryChooseBestAiMove(PlayerData player, out AiMoveCandidate bestMove)
    {
        bestMove = new AiMoveCandidate(-1, true, int.MaxValue);
        bool foundMove = false;

        for (int i = 0; i < player.Hand.Count; i++)
        {
            DominoTile tile = player.Hand[i];

            if (board.Chain.Count == 0)
            {
                int score = EvaluateAiMove(player, i, tile, tile.Left, tile.Right);
                AiMoveCandidate candidate = new AiMoveCandidate(i, true, score);

                if (!foundMove || candidate.Score < bestMove.Score)
                {
                    bestMove = candidate;
                    foundMove = true;
                }

                continue;
            }

            if (TryPreviewPlayLeft(tile, out DominoTile leftPlayedTile, out int newLeftEnd))
            {
                int score = EvaluateAiMove(player, i, leftPlayedTile, newLeftEnd, board.RightEnd);
                AiMoveCandidate candidate = new AiMoveCandidate(i, true, score);

                if (!foundMove || candidate.Score < bestMove.Score)
                {
                    bestMove = candidate;
                    foundMove = true;
                }
            }

            if (TryPreviewPlayRight(tile, out DominoTile rightPlayedTile, out int newRightEnd))
            {
                int score = EvaluateAiMove(player, i, rightPlayedTile, board.LeftEnd, newRightEnd);
                AiMoveCandidate candidate = new AiMoveCandidate(i, false, score);

                if (!foundMove || candidate.Score < bestMove.Score)
                {
                    bestMove = candidate;
                    foundMove = true;
                }
            }
        }

        return foundMove;
    }

    // Donne une note a un coup IA.
    // Plus la note est petite, meilleur est le coup.
    private int EvaluateAiMove(
        PlayerData player,
        int handIndex,
        DominoTile playedTile,
        int nextLeftEnd,
        int nextRightEnd)
    {
        int remainingPoints = GetHandTotalExcluding(player, handIndex);
        int futurePlayableTiles = CountPlayableTilesAfterMove(player, handIndex, nextLeftEnd, nextRightEnd);
        int doubleBonus = playedTile.IsDouble() ? 3 : 0;

        // Le petit aleatoire evite que l'IA fasse toujours exactement le meme choix
        // quand deux coups ont une valeur tres proche.
        int smallRandomTieBreak = Random.Range(0, 2);

        return remainingPoints * 10 - futurePlayableTiles * 4 - doubleBonus + smallRandomTieBreak;
    }

    // Calcule les points restants dans la main si le domino a handIndex est joue.
    private int GetHandTotalExcluding(PlayerData player, int excludedHandIndex)
    {
        int total = 0;

        for (int i = 0; i < player.Hand.Count; i++)
        {
            if (i == excludedHandIndex)
                continue;

            total += player.Hand[i].TotalValue();
        }

        return total;
    }

    // Compte combien de dominos l'IA pourrait encore jouer apres ce coup.
    // Cela lui evite de jouer un coup qui la bloque elle-meme trop vite.
    private int CountPlayableTilesAfterMove(PlayerData player, int excludedHandIndex, int nextLeftEnd, int nextRightEnd)
    {
        int count = 0;

        for (int i = 0; i < player.Hand.Count; i++)
        {
            if (i == excludedHandIndex)
                continue;

            DominoTile tile = player.Hand[i];

            if (tile.Matches(nextLeftEnd) || tile.Matches(nextRightEnd))
                count++;
        }

        return count;
    }

    // Simule un coup a gauche sans modifier la main ni le plateau.
    private bool TryPreviewPlayLeft(DominoTile tile, out DominoTile playedTile, out int nextLeftEnd)
    {
        playedTile = null;
        nextLeftEnd = board.LeftEnd;

        if (board.Chain.Count == 0)
        {
            playedTile = new DominoTile(tile.Left, tile.Right);
            nextLeftEnd = playedTile.Left;
            return true;
        }

        int currentLeft = board.LeftEnd;

        if (tile.Right == currentLeft)
        {
            playedTile = new DominoTile(tile.Left, tile.Right);
            nextLeftEnd = playedTile.Left;
            return true;
        }

        if (tile.Left == currentLeft)
        {
            playedTile = new DominoTile(tile.Right, tile.Left);
            nextLeftEnd = playedTile.Left;
            return true;
        }

        return false;
    }

    // Simule un coup a droite sans modifier la main ni le plateau.
    private bool TryPreviewPlayRight(DominoTile tile, out DominoTile playedTile, out int nextRightEnd)
    {
        playedTile = null;
        nextRightEnd = board.RightEnd;

        if (board.Chain.Count == 0)
        {
            playedTile = new DominoTile(tile.Left, tile.Right);
            nextRightEnd = playedTile.Right;
            return true;
        }

        int currentRight = board.RightEnd;

        if (tile.Left == currentRight)
        {
            playedTile = new DominoTile(tile.Left, tile.Right);
            nextRightEnd = playedTile.Right;
            return true;
        }

        if (tile.Right == currentRight)
        {
            playedTile = new DominoTile(tile.Right, tile.Left);
            nextRightEnd = playedTile.Right;
            return true;
        }

        return false;
    }

    // Essaie de jouer le domino actuellement selectionne du cote choisi.
    private void TryPlaySelectedHumanTile(bool playRight)
    {
        if (selectedHumanHandIndex < 0)
        {
            statusMessage = "Selectionne d'abord un domino jaune";
            UpdateHud();
            return;
        }

        PlayerData player = players[HumanPlayerIndex];

        if (selectedHumanHandIndex >= player.Hand.Count)
        {
            selectedHumanHandIndex = -1;
            UpdateUI();
            return;
        }

        if (!CanTilePlayOnSide(player.Hand[selectedHumanHandIndex], playRight))
        {
            statusMessage = playRight
                ? "Ce domino ne matche pas l'extremite droite (" + board.RightEnd + ")"
                : "Ce domino ne matche pas l'extremite gauche (" + board.LeftEnd + ")";
            UpdateHud();
            return;
        }

        bool played = TryPlayHumanTileOnChosenSide(player, selectedHumanHandIndex, playRight);

        if (!played)
        {
            statusMessage = playRight
                ? "Ce domino ne passe pas a droite"
                : "Ce domino ne passe pas a gauche";
            UpdateHud();
            return;
        }

        waitingForHumanInput = false;
        CompleteTurn(player, true);
    }

    // Met a jour le timer de 15 secondes du Joueur 1.
    private void UpdateHumanTimer()
    {
        if (!humanTimerActive || !waitingForHumanInput || roundEnded)
            return;

        humanTurnTimeRemaining -= Time.deltaTime;

        if (humanTurnTimeRemaining <= 0f)
        {
            humanTurnTimeRemaining = 0f;
            humanTimerActive = false;
            PlayRandomHumanMoveBecauseTimerEnded();
            return;
        }

        UpdateHud();
    }

    // Si le timer arrive a zero, le jeu choisit un coup legal au hasard.
    private void PlayRandomHumanMoveBecauseTimerEnded()
    {
        if (!waitingForHumanInput || roundEnded || currentPlayerIndex != HumanPlayerIndex)
            return;

        PlayerData player = players[HumanPlayerIndex];
        List<HumanMoveChoice> choices = GetRandomHumanMoveChoices(player);

        if (choices.Count == 0)
        {
            waitingForHumanInput = false;
            CompleteTurn(player, false);
            return;
        }

        HumanMoveChoice choice = choices[Random.Range(0, choices.Count)];
        selectedHumanHandIndex = choice.HandIndex;

        bool played = TryPlayHumanTile(player, choice.HandIndex, choice.PreferLeft);

        if (!played)
        {
            waitingForHumanInput = false;
            CompleteTurn(player, false);
            return;
        }

        statusMessage = "Temps ecoule : coup aleatoire";
        waitingForHumanInput = false;
        CompleteTurn(player, true);
    }

    // Construit la liste des coups possibles pour le coup aleatoire du timer.
    private List<HumanMoveChoice> GetRandomHumanMoveChoices(PlayerData player)
    {
        List<HumanMoveChoice> choices = new List<HumanMoveChoice>();

        if (player == null)
            return choices;

        if (!firstMovePlayed && board.Chain.Count == 0)
        {
            if (currentRoundStartsFromPreviousWinner)
            {
                for (int i = 0; i < player.Hand.Count; i++)
                    choices.Add(new HumanMoveChoice(i, true));

                return choices;
            }

            DominoTile highestDouble = player.FindHighestDouble();

            for (int i = 0; i < player.Hand.Count; i++)
            {
                if (player.Hand[i] == highestDouble)
                    choices.Add(new HumanMoveChoice(i, true));
            }

            return choices;
        }

        for (int i = 0; i < player.Hand.Count; i++)
        {
            DominoTile tile = player.Hand[i];

            if (tile.Matches(board.LeftEnd))
                choices.Add(new HumanMoveChoice(i, true));

            if (tile.Matches(board.RightEnd))
                choices.Add(new HumanMoveChoice(i, false));
        }

        return choices;
    }

    // Essaie de jouer le domino clique par Joueur 1.
    private bool TryPlayHumanTile(PlayerData player, int handIndex, bool preferLeft)
    {
        // Si le gagnant de la manche precedente commence, il peut jouer ce qu'il veut.
        if (!firstMovePlayed && board.Chain.Count == 0)
        {
            DominoTile selectedTile = player.Hand[handIndex];

            if (currentRoundStartsFromPreviousWinner)
            {
                if (!PlayFirstTileFromHand(player, handIndex, out DominoTile freeFirstTile))
                    return false;

                statusMessage = player.Name + " commence avec " + freeFirstTile;
                Debug.Log(statusMessage);
                return true;
            }

            // Premiere manche : seul le plus gros double est autorise.
            DominoTile highestDouble = player.FindHighestDouble();

            if (selectedTile != highestDouble)
            {
                statusMessage = "Premier coup : il faut jouer " + highestDouble;
                return false;
            }

            if (!PlayFirstTileFromHand(player, handIndex, out DominoTile playedDouble))
                return false;

            statusMessage = player.Name + " commence avec " + playedDouble;
            Debug.Log(statusMessage);
            return true;
        }

        if (TryPlayTileAtIndex(player, handIndex, preferLeft, out DominoTile playedTile, out string side))
        {
            statusMessage = player.Name + " joue " + playedTile + " a " + side;
            Debug.Log(statusMessage);
            return true;
        }

        return false;
    }

    // Essaie de jouer le domino selectionne exactement du cote choisi.
    // Contrairement a TryPlayHumanTile, cette methode ne bascule pas automatiquement
    // sur l'autre cote si le cote demande est impossible.
    private bool TryPlayHumanTileOnChosenSide(PlayerData player, int handIndex, bool playRight)
    {
        if (!firstMovePlayed && board.Chain.Count == 0)
            return TryPlayHumanTile(player, handIndex, true);

        if (handIndex < 0 || handIndex >= player.Hand.Count)
            return false;

        if (!CanTilePlayOnSide(player.Hand[handIndex], playRight))
            return false;

        DominoTile playedTile;

        if (playRight)
        {
            if (!TryPlayTileRight(player, handIndex, out playedTile))
                return false;

            statusMessage = player.Name + " joue " + playedTile + " a droite";
            Debug.Log(statusMessage);
            return true;
        }

        if (!TryPlayTileLeft(player, handIndex, out playedTile))
            return false;

        statusMessage = player.Name + " joue " + playedTile + " a gauche";
        Debug.Log(statusMessage);
        return true;
    }

    // Pose le premier domino de la manche depuis une main.
    // Utilise pour le plus gros double en premiere manche et pour le gagnant
    // de la manche precedente quand il commence librement.
    private bool PlayFirstTileFromHand(PlayerData player, int handIndex, out DominoTile playedTile)
    {
        playedTile = null;

        if (handIndex < 0 || handIndex >= player.Hand.Count)
            return false;

        DominoTile tile = player.Hand[handIndex];
        player.RemoveTile(tile);
        board.PlayFirstTile(tile);

        centerTileIndex = 0;
        firstMovePlayed = true;
        playedTile = tile;
        return true;
    }

    // Essaie de jouer un domino precis, soit en preferant la gauche, soit la droite.
    private bool TryPlayTileAtIndex(
        PlayerData player,
        int handIndex,
        bool preferLeft,
        out DominoTile playedTile,
        out string side)
    {
        playedTile = null;
        side = "";

        if (handIndex < 0 || handIndex >= player.Hand.Count)
            return false;

        if (preferLeft)
        {
            if (TryPlayTileLeft(player, handIndex, out playedTile))
            {
                side = "gauche";
                return true;
            }

            if (TryPlayTileRight(player, handIndex, out playedTile))
            {
                side = "droite";
                return true;
            }
        }
        else
        {
            if (TryPlayTileRight(player, handIndex, out playedTile))
            {
                side = "droite";
                return true;
            }

            if (TryPlayTileLeft(player, handIndex, out playedTile))
            {
                side = "gauche";
                return true;
            }
        }

        return false;
    }

    // Essaie de jouer un domino a gauche.
    private bool TryPlayTileLeft(PlayerData player, int handIndex, out DominoTile playedTile)
    {
        playedTile = null;
        DominoTile tile = player.Hand[handIndex];
        DominoTile tileCopy = new DominoTile(tile.Left, tile.Right);

        if (!board.TryPlayLeft(tileCopy))
            return false;

        player.RemoveTile(tile);

        // Comme on ajoute au debut de la liste, le domino central est decale
        // d'une place vers la droite dans board.Chain.
        centerTileIndex++;

        playedTile = tileCopy;
        return true;
    }

    // Essaie de jouer un domino a droite.
    private bool TryPlayTileRight(PlayerData player, int handIndex, out DominoTile playedTile)
    {
        playedTile = null;
        DominoTile tile = player.Hand[handIndex];
        DominoTile tileCopy = new DominoTile(tile.Left, tile.Right);

        if (!board.TryPlayRight(tileCopy))
            return false;

        player.RemoveTile(tile);
        playedTile = tileCopy;
        return true;
    }

    // Retourne true si le joueur a au moins un coup legal.
    private bool HasPlayableMove(PlayerData player)
    {
        return GetPlayableHandIndexes(player).Count > 0;
    }

    // Retourne true si ce domino peut etre joue du cote demande selon
    // les vraies extremites logiques du BoardState.
    private bool CanTilePlayOnSide(DominoTile tile, bool playRight)
    {
        if (tile == null)
            return false;

        if (!firstMovePlayed && board.Chain.Count == 0)
            return true;

        return playRight ? tile.Matches(board.RightEnd) : tile.Matches(board.LeftEnd);
    }

    // Retourne les index des dominos jouables dans la main du joueur.
    // Le renderer utilise cette liste pour colorer les dominos cliquables en jaune.
    private List<int> GetPlayableHandIndexes(PlayerData player)
    {
        List<int> playableIndexes = new List<int>();

        if (player == null)
            return playableIndexes;

        // Premier coup : seul le plus gros double du joueur qui commence est jouable.
        if (!firstMovePlayed && board.Chain.Count == 0)
        {
            if (currentRoundStartsFromPreviousWinner)
            {
                for (int i = 0; i < player.Hand.Count; i++)
                    playableIndexes.Add(i);

                return playableIndexes;
            }

            DominoTile highestDouble = player.FindHighestDouble();

            for (int i = 0; i < player.Hand.Count; i++)
            {
                if (player.Hand[i] == highestDouble)
                    playableIndexes.Add(i);
            }

            return playableIndexes;
        }

        for (int i = 0; i < player.Hand.Count; i++)
        {
            DominoTile tile = player.Hand[i];

            if (tile.Matches(board.LeftEnd) || tile.Matches(board.RightEnd))
                playableIndexes.Add(i);
        }

        return playableIndexes;
    }

    // Passe au joueur suivant dans l'ordre de la liste.
    private void NextPlayer()
    {
        currentPlayerIndex++;

        if (currentPlayerIndex >= players.Count)
            currentPlayerIndex = 0;
    }

    // Affiche les mains initiales dans la console pour debugger.
    private void PrintHands()
    {
        foreach (PlayerData player in players)
        {
            string handText = player.Name + " : ";

            foreach (DominoTile tile in player.Hand)
                handText += tile + " ";

            Debug.Log(handText);
        }
    }

    // Met a jour le rendu visuel, le HUD et l'ancienne UI texte.
    private void UpdateUI()
    {
        UpdateVisuals();
        UpdateHud();
        UpdateDebugTextVisibility();

        if (!showDebugText)
            return;

        if (boardText != null)
            boardText.text = "Chaine : " + GetBoardText();

        if (playerHandText != null)
            playerHandText.text =
                "Tour actuel : " + GetCurrentTurnText() + "\n\n" +
                "Main Joueur 1 : " + GetHandText(players[0]);
    }

    // Cache ou affiche les anciens textes selon showDebugText.
    private void UpdateDebugTextVisibility()
    {
        if (boardText != null)
            boardText.gameObject.SetActive(showDebugText);

        if (playerHandText != null)
            playerHandText.gameObject.SetActive(showDebugText);
    }

    // Demande aux scripts visuels de redessiner le plateau et la main.
    private void UpdateVisuals()
    {
        if (boardRenderer != null)
            boardRenderer.RenderBoard(board.Chain, centerTileIndex);

        if (playerHandRenderer != null && players != null && players.Count > 0)
        {
            List<int> playableIndexes = waitingForHumanInput
                ? GetPlayableHandIndexes(players[HumanPlayerIndex])
                : new List<int>();

            playerHandRenderer.RenderHand(
                players[HumanPlayerIndex].Hand,
                this,
                playableIndexes,
                selectedHumanHandIndex);
        }

        UpdatePlayZones();

        if (opponentHandsRenderer != null)
            opponentHandsRenderer.RenderHands(players);
    }

    // Met a jour seulement les zones gauche/droite.
    // Important : on l'appelle aussi quand le joueur selectionne un domino,
    // pour activer immediatement la bonne zone sans reconstruire toute la main.
    private void UpdatePlayZones()
    {
        if (playZoneRenderer == null)
            return;

        Vector3 leftPlayZonePosition = new Vector3(-5.8f, 0.65f, 0f);
        Vector3 rightPlayZonePosition = new Vector3(5.8f, 0.65f, 0f);
        bool leftZoneEnabled = false;
        bool rightZoneEnabled = false;

        if (boardRenderer != null)
            boardRenderer.GetPlayZoneWorldPositions(out leftPlayZonePosition, out rightPlayZonePosition);

        if (waitingForHumanInput &&
            selectedHumanHandIndex >= 0 &&
            players != null &&
            players.Count > HumanPlayerIndex &&
            selectedHumanHandIndex < players[HumanPlayerIndex].Hand.Count)
        {
            DominoTile selectedTile = players[HumanPlayerIndex].Hand[selectedHumanHandIndex];
            leftZoneEnabled = CanTilePlayOnSide(selectedTile, false);
            rightZoneEnabled = CanTilePlayOnSide(selectedTile, true);
        }

        playZoneRenderer.Render(
            this,
            waitingForHumanInput,
            selectedHumanHandIndex >= 0,
            leftPlayZonePosition,
            rightPlayZonePosition,
            leftZoneEnabled,
            rightZoneEnabled);
    }

    // Met a jour le petit HUD cree en code.
    private void UpdateHud()
    {
        if (hudRenderer == null)
            return;

        hudRenderer.Render(GetScoreText(), GetCurrentTurnText(), GetStatusText());
    }

    // Transforme la chaine en texte lisible pour l'UI de debug.
    private string GetBoardText()
    {
        if (board.Chain.Count == 0)
            return "(aucun domino pose)";

        string result = "";
        foreach (DominoTile tile in board.Chain)
            result += tile + " ";

        return result;
    }

    // Transforme une main en texte lisible pour l'UI de debug.
    private string GetHandText(PlayerData player)
    {
        if (player.Hand.Count == 0)
            return "(main vide)";

        string result = "";
        foreach (DominoTile tile in player.Hand)
            result += tile + " ";

        return result;
    }

    // Cree une ligne de score lisible.
    private string GetScoreText()
    {
        if (players == null || scores == null)
            return "Score : -";

        string result = "Score : ";

        for (int i = 0; i < players.Count; i++)
        {
            result += players[i].Name + " " + scores[i];

            if (i < players.Count - 1)
                result += " | ";
        }

        return result;
    }

    // Retourne le nom du joueur actuel.
    private string GetCurrentTurnText()
    {
        if (players == null || players.Count == 0)
            return "Tour : -";

        return "Tour : " + players[currentPlayerIndex].Name;
    }

    // Ajoute le timer au message du HUD quand c'est le tour du joueur humain.
    private string GetStatusText()
    {
        if (humanTimerActive && waitingForHumanInput)
        {
            int seconds = Mathf.CeilToInt(humanTurnTimeRemaining);
            return "Temps : " + seconds + "s | " + statusMessage;
        }

        return statusMessage;
    }
}
