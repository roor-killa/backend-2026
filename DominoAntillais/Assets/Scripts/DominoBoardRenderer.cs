using System.Collections.Generic;
using UnityEngine;

// Dessine la chaine de dominos sur la table.
// La logique reste gauche/droite, mais le rendu visuel "casse" la ligne
// quand elle arrive au bord de la table pour garder les dominos dans le cadre.
public class DominoBoardRenderer : MonoBehaviour
{
    [Header("Prefab optionnel")]
    // Si un prefab est branche dans l'Inspector, on l'utilise.
    // Sinon, DominoTileVisual fabrique un domino simple automatiquement.
    public GameObject dominoPrefab;

    [Header("Position du plateau")]
    // Parent des dominos poses. S'il est null, le script le cree au lancement.
    public Transform boardParent;

    // Position generale de la chaine sur l'ecran.
    public Vector3 boardCenter = new Vector3(0f, 0.65f, 0f);

    [Header("Fond de table prototype")]
    // Active un rectangle rouge simple pour simuler la table.
    public bool showTableSurface = true;

    // Taille du fond de table.
    public Vector2 tableSize = new Vector2(19.2f, 10.8f);

    // Couleur du fond de table.
    public Color tableColor = new Color(0.60f, 0.15f, 0.10f, 1f);

    [Header("Zone utile de la table")]
    // Limites locales dans lesquelles la chaine doit rester.
    public float minTableX = -7.1f;
    public float maxTableX = 7.1f;
    public float minTableY = -3.35f;
    public float maxTableY = 3.35f;

    [Header("Taille et espacement")]
    // Taille d'un domino horizontal.
    public float tileWidth = 1.38f;
    public float tileHeight = 0.69f;

    // Petit espace entre deux dominos.
    public float spacing = 0.015f;

    [Header("Anti-chevauchement")]
    // Marge invisible autour des dominos deja poses.
    // Elle evite que la chaine repasse trop pres d'un ancien domino.
    public float collisionMargin = 0.16f;

    // Les doubles depassent perpendiculairement de la ligne principale.
    // On leur reserve donc un peu plus d'air pour eviter qu'un futur virage
    // vienne couper dans leur zone.
    public float doubleCollisionExtraMargin = 0.26f;

    [Header("Lecture de l'espace libre")]
    // Nombre de pas regardes devant un coup possible.
    // Plus cette valeur est grande, plus la chaine anticipe les futurs virages.
    public int spaceScanSteps = 10;

    // Nombre de couloirs regardes a gauche et a droite de la direction testee.
    // 2 veut dire : deux couloirs a gauche, le couloir central, deux couloirs a droite.
    public int spaceScanSideLanes = 3;

    // Distance entre deux points de scan.
    public float spaceScanStepSize = 0.66f;

    // Petit bonus donne au fait de continuer tout droit quand l'espace est suffisant.
    public float straightDirectionBonus = 0.35f;

    [Header("Trajet style reference")]
    // true : le renderer garde une grande ligne horizontale comme sur la reference,
    // puis tourne pres des bords au lieu de serpenter trop tot.
    public bool useReferenceLanePath = true;

    // Distance minimale au bord avant d'autoriser la ligne a continuer tout droit.
    // Si on est plus proche que cette valeur, on cherche plutot un virage.
    public float edgeTurnReserve = 0.90f;

    // Nombre de dominos de marge gardes avant un virage horizontal.
    // 1 = on tourne juste avant le bord.
    // 2 = on garde un peu plus de place pour mieux exploiter la table.
    public int minTurnReserveTiles = 1;
    public int maxTurnReserveTiles = 2;

    // Nombre de futurs emplacements libres necessaires pour accepter de continuer tout droit.
    public int minimumStraightFreeSteps = 3;

    // Bonus donne au virage naturel : a droite on monte, a gauche on descend.
    // Cela donne une silhouette proche de la capture reference.
    public float preferredTurnBonus = 1.25f;

    // Nombre de dominos maximum dans un petit connecteur vertical avant
    // de revenir sur une ligne horizontale.
    public int verticalConnectorTiles = 3;

    [Header("Variation logique")]
    // Ajoute une petite variation de manche a manche.
    // Le jeu ne suit donc pas toujours exactement le meme trajet,
    // mais chaque manche garde une logique stable du debut a la fin.
    public bool randomizeLaneStyleEachRound = true;

    // Nombre minimum de dominos dans un connecteur vertical pour une manche.
    public int minRandomConnectorTiles = 2;

    // Nombre maximum de dominos dans un connecteur vertical pour une manche.
    public int maxRandomConnectorTiles = 4;

    // Variation maximale ajoutee a la reserve avant virage pres d'un bord.
    public float edgeTurnReserveJitter = 0.25f;

    [Header("Regle visuelle des doubles")]
    // Un double doit rester sur l'axe de la chaine.
    // Le double est visuellement perpendiculaire, mais la route ne tourne pas
    // juste parce qu'un double vient d'etre pose.
    public bool keepLineThroughDoubles = true;

    [Header("Zones de pose")]
    // Ecart supplementaire entre le dernier domino et la zone de pose.
    public float playZoneOffset = 0.22f;

    // Tous les dominos visuels actuellement affiches.
    private readonly List<GameObject> spawnedTiles = new List<GameObject>();

    // Rectangles invisibles reserves par les dominos deja poses.
    // Le renderer les utilise comme des hitbox simples pour eviter les croisements.
    private readonly List<Rect> occupiedHitboxes = new List<Rect>();

    // Hitbox plus proche du corps reel du domino.
    // Elle sert de dernier garde-fou quand la marge de securite devient trop stricte.
    private readonly List<Rect> occupiedBodyHitboxes = new List<Rect>();

    // Rectangle de fond de table cree automatiquement.
    private GameObject tableSurface;

    // Positions monde des deux zones ou le joueur peut poser son domino.
    private Vector3 leftPlayZoneWorldPosition;
    private Vector3 rightPlayZoneWorldPosition;

    // Petit curseur utilise pour dessiner une branche de la chaine.
    private struct LayoutCursor
    {
        public Vector2 Position;
        public Vector2 OpenPoint;
        public Vector2 Direction;
        public Vector2 LastFootprint;
        public int LastHitboxIndex;
        public bool LastTileWasDouble;
        public int TilesInCurrentDirection;
        public int TurnCount;

        public LayoutCursor(
            Vector2 position,
            Vector2 openPoint,
            Vector2 direction,
            Vector2 lastFootprint,
            int lastHitboxIndex,
            bool lastTileWasDouble,
            int tilesInCurrentDirection = 0)
        {
            Position = position;
            OpenPoint = openPoint;
            Direction = direction;
            LastFootprint = lastFootprint;
            LastHitboxIndex = lastHitboxIndex;
            LastTileWasDouble = lastTileWasDouble;
            TilesInCurrentDirection = tilesInCurrentDirection;
            TurnCount = 0;
        }
    }

    // Resultat d'un essai de placement.
    // On garde ces valeurs ensemble pour eviter de recalculer angle, taille et hitbox.
    private struct PlacementCandidate
    {
        public Vector2 Position;
        public Vector2 NextOpenPoint;
        public Vector2 Direction;
        public Vector2 Footprint;
        public float Angle;
        public Rect Hitbox;
        public Rect BodyHitbox;
        public int DisplayLeft;
        public int DisplayRight;
        public int CollisionCount;
        public int BodyCollisionCount;
        public float FreeSpaceScore;
    }

    // Copie de la chaine deja dessinee.
    // Elle permet de detecter si le prochain rendu ajoute seulement un domino
    // a gauche ou a droite, pour ne jamais redeplacer les anciens dominos.
    private readonly List<DominoTile> renderedChain = new List<DominoTile>();

    // Curseurs stables des deux extremites visuelles.
    private LayoutCursor stableLeftCursor;
    private LayoutCursor stableRightCursor;

    // true quand la table visuelle contient deja la manche actuelle.
    private bool hasStableBoardLayout;

    // Index du domino central dans la derniere chaine dessinee.
    private int renderedCenterTileIndex = -1;

    // Variante de trajectoire choisie pour la manche en cours.
    private bool hasActiveLaneVariation;
    private int leftPrimaryVerticalSign = -1;
    private int rightPrimaryVerticalSign = 1;
    private int leftConnectorTilesThisRound;
    private int rightConnectorTilesThisRound;
    private int leftTurnReserveTilesThisRound;
    private int rightTurnReserveTilesThisRound;
    private float leftEdgeTurnReserveThisRound;
    private float rightEdgeTurnReserveThisRound;
    private bool layoutTuningNormalized;

    // Met a jour la chaine visuelle.
    // Important : pendant une manche, on n'efface pas tout a chaque coup.
    // On ajoute seulement le nouveau domino, sinon les anciens dominos bougent.
    // boardChain       : liste logique des dominos poses, de gauche a droite.
    // centerTileIndex  : index du premier domino joue, celui qui doit rester au centre.
    public void RenderBoard(List<DominoTile> boardChain, int centerTileIndex)
    {
        NormalizeLayoutTuning();
        EnsureTableSurface();
        EnsureParent();

        if (boardChain == null || boardChain.Count == 0)
        {
            ClearBoard();
            ResetRoundLaneVariation();
            UpdateEmptyPlayZonePositions();
            return;
        }

        centerTileIndex = Mathf.Clamp(centerTileIndex, 0, boardChain.Count - 1);

        if (TryRenderIncremental(boardChain, centerTileIndex))
            return;

        BuildBoardFromScratch(boardChain, centerTileIndex);
    }

    // Garantit des valeurs minimales coherentes avec les dominos plus grands.
    // Unity garde parfois les anciennes valeurs publiques dans l'Inspector ;
    // cette passe evite donc que les anciens reglages recreent du chevauchement.
    private void NormalizeLayoutTuning()
    {
        if (layoutTuningNormalized)
            return;

        layoutTuningNormalized = true;

        tileWidth = Mathf.Max(tileWidth, 1.38f);
        tileHeight = Mathf.Max(tileHeight, 0.69f);
        tableSize = new Vector2(Mathf.Max(tableSize.x, 19.2f), Mathf.Max(tableSize.y, 10.8f));

        minTableX = Mathf.Min(minTableX, -7.1f);
        maxTableX = Mathf.Max(maxTableX, 7.1f);
        minTableY = Mathf.Min(minTableY, -3.35f);
        maxTableY = Mathf.Max(maxTableY, 3.35f);

        collisionMargin = Mathf.Max(collisionMargin, tileHeight * 0.23f);
        spaceScanSteps = Mathf.Max(spaceScanSteps, 10);
        spaceScanSideLanes = Mathf.Max(spaceScanSideLanes, 3);
        spaceScanStepSize = Mathf.Max(spaceScanStepSize, tileWidth * 0.48f);
        minimumStraightFreeSteps = Mathf.Max(minimumStraightFreeSteps, 3);

        edgeTurnReserve = Mathf.Clamp(edgeTurnReserve, tileWidth * 0.55f, tileWidth * 0.95f);
        minTurnReserveTiles = 1;
        maxTurnReserveTiles = Mathf.Clamp(maxTurnReserveTiles, minTurnReserveTiles, 2);
        verticalConnectorTiles = Mathf.Max(verticalConnectorTiles, 3);
        minRandomConnectorTiles = Mathf.Max(minRandomConnectorTiles, 2);
        maxRandomConnectorTiles = Mathf.Max(maxRandomConnectorTiles, minRandomConnectorTiles + 1);

        if (tableSurface != null)
            tableSurface.transform.localScale = new Vector3(tableSize.x, tableSize.y, 1f);
    }

    // Construit toute la table seulement au debut d'une manche, ou si Unity
    // a perdu la correspondance avec la chaine logique.
    private void BuildBoardFromScratch(List<DominoTile> boardChain, int centerTileIndex)
    {
        EnsureRoundLaneVariation();
        ClearBoard();

        DominoTile centerTile = boardChain[centerTileIndex];
        float centerAngle = GetCenterRotationAngle(centerTile);
        Vector2 centerFootprint = GetFootprintForAngle(centerAngle);

        int centerHitboxIndex = PlaceTile(centerTile.Left, centerTile.Right, Vector2.zero, centerAngle, 10);

        stableLeftCursor = new LayoutCursor(
            Vector2.zero,
            GetOpenPointFromCenter(Vector2.zero, Vector2.left, centerTile.IsDouble()),
            Vector2.left,
            centerFootprint,
            centerHitboxIndex,
            centerTile.IsDouble());

        for (int i = centerTileIndex - 1; i >= 0; i--)
        {
            DominoTile tile = boardChain[i];
            PlaceBranchTile(tile, ref stableLeftCursor, false);
        }

        stableRightCursor = new LayoutCursor(
            Vector2.zero,
            GetOpenPointFromCenter(Vector2.zero, Vector2.right, centerTile.IsDouble()),
            Vector2.right,
            centerFootprint,
            centerHitboxIndex,
            centerTile.IsDouble());

        for (int i = centerTileIndex + 1; i < boardChain.Count; i++)
        {
            DominoTile tile = boardChain[i];
            PlaceBranchTile(tile, ref stableRightCursor, true);
        }

        CopyRenderedChain(boardChain);
        renderedCenterTileIndex = centerTileIndex;
        hasStableBoardLayout = true;
        UpdateStablePlayZonePositions();
    }

    // Essaie d'ajouter uniquement le domino qui vient d'etre joue.
    // Retourne false si la chaine ne ressemble pas a une simple extension.
    private bool TryRenderIncremental(List<DominoTile> boardChain, int centerTileIndex)
    {
        if (!hasStableBoardLayout || renderedChain.Count == 0)
            return false;

        if (boardChain.Count == renderedChain.Count)
        {
            if (!ChainMatchesWithOffset(boardChain, 0))
                return false;

            renderedCenterTileIndex = centerTileIndex;
            UpdateStablePlayZonePositions();
            return true;
        }

        if (boardChain.Count != renderedChain.Count + 1)
            return false;

        bool addedLeft = ChainMatchesWithOffset(boardChain, 1);
        bool addedRight = ChainMatchesWithOffset(boardChain, 0);

        if (addedLeft)
        {
            PlaceBranchTile(boardChain[0], ref stableLeftCursor, false);
            renderedChain.Insert(0, boardChain[0]);
            renderedCenterTileIndex = centerTileIndex;
            UpdateStablePlayZonePositions();
            return true;
        }

        if (addedRight)
        {
            DominoTile newRightTile = boardChain[boardChain.Count - 1];
            PlaceBranchTile(newRightTile, ref stableRightCursor, true);
            renderedChain.Add(newRightTile);
            renderedCenterTileIndex = centerTileIndex;
            UpdateStablePlayZonePositions();
            return true;
        }

        return false;
    }

    // Verifie que les anciens dominos sont encore les memes objets dans la chaine.
    // offset = 0 : ajout a droite possible.
    // offset = 1 : ajout a gauche possible.
    private bool ChainMatchesWithOffset(List<DominoTile> boardChain, int offset)
    {
        if (boardChain.Count < renderedChain.Count + offset)
            return false;

        for (int i = 0; i < renderedChain.Count; i++)
        {
            if (!ReferenceEquals(renderedChain[i], boardChain[i + offset]))
                return false;
        }

        return true;
    }

    // Retient la chaine logique actuellement dessinee.
    private void CopyRenderedChain(List<DominoTile> boardChain)
    {
        renderedChain.Clear();

        for (int i = 0; i < boardChain.Count; i++)
            renderedChain.Add(boardChain[i]);
    }

    // Met a jour uniquement les zones de pose, sans toucher aux dominos deja poses.
    private void UpdateStablePlayZonePositions()
    {
        leftPlayZoneWorldPosition = boardParent.TransformPoint(GetZonePosition(stableLeftCursor));
        rightPlayZoneWorldPosition = boardParent.TransformPoint(GetZonePosition(stableRightCursor));
    }

    // Retourne la demi-longueur utile d'un domino dans l'axe de la chaine.
    // Un domino normal avance avec sa grande longueur.
    // Un double pose perpendiculairement avance avec sa petite largeur.
    private float GetConnectorHalfLength(bool isDouble)
    {
        return isDouble ? tileHeight * 0.5f : tileWidth * 0.5f;
    }

    // Point exact ou la chaine reste ouverte a une extremite.
    private Vector2 GetOpenPointFromCenter(Vector2 center, Vector2 direction, bool isDouble)
    {
        return center + direction * GetConnectorHalfLength(isDouble);
    }

    // Choisit une petite variante de route pour la manche.
    // Exemple :
    // - manche 1 : gauche descend / droite monte ;
    // - manche 2 : gauche monte / droite descend.
    // On ajoute aussi une variation legere sur la longueur des connecteurs
    // et la reserve avant virage pour casser la repetition visuelle.
    private void EnsureRoundLaneVariation()
    {
        if (hasActiveLaneVariation)
            return;

        if (randomizeLaneStyleEachRound)
        {
            // On garde les deux cotes sur des couloirs opposes de facon stable :
            // la branche de droite descend d'abord, la branche de gauche monte.
            // Cela evite que les deux cotes se retrouvent dans la meme zone
            // de table plus tard dans la manche.
            rightPrimaryVerticalSign = -1;
            leftPrimaryVerticalSign = 1;

            int minConnector = Mathf.Max(1, minRandomConnectorTiles);
            int maxConnector = Mathf.Max(minConnector, maxRandomConnectorTiles);
            int minReserveTiles = Mathf.Max(1, minTurnReserveTiles);
            int maxReserveTiles = Mathf.Max(minReserveTiles, maxTurnReserveTiles);

            leftConnectorTilesThisRound = Random.Range(minConnector, maxConnector + 1);
            rightConnectorTilesThisRound = Random.Range(minConnector, maxConnector + 1);
            leftTurnReserveTilesThisRound = Random.Range(minReserveTiles, maxReserveTiles + 1);
            rightTurnReserveTilesThisRound = Random.Range(minReserveTiles, maxReserveTiles + 1);

            float jitter = Mathf.Max(0f, edgeTurnReserveJitter);
            leftEdgeTurnReserveThisRound = Mathf.Max(
                0.35f,
                GetTurnReserveDistance(leftTurnReserveTilesThisRound) + Random.Range(-jitter, jitter));
            rightEdgeTurnReserveThisRound = Mathf.Max(
                0.35f,
                GetTurnReserveDistance(rightTurnReserveTilesThisRound) + Random.Range(-jitter, jitter));
        }
        else
        {
            leftPrimaryVerticalSign = 1;
            rightPrimaryVerticalSign = -1;
            leftConnectorTilesThisRound = verticalConnectorTiles;
            rightConnectorTilesThisRound = verticalConnectorTiles;
            leftTurnReserveTilesThisRound = Mathf.Max(1, minTurnReserveTiles);
            rightTurnReserveTilesThisRound = Mathf.Max(1, minTurnReserveTiles);
            leftEdgeTurnReserveThisRound = GetTurnReserveDistance(leftTurnReserveTilesThisRound);
            rightEdgeTurnReserveThisRound = GetTurnReserveDistance(rightTurnReserveTilesThisRound);
        }

        hasActiveLaneVariation = true;
    }

    // Remise a zero de la variation quand une nouvelle manche commence.
    private void ResetRoundLaneVariation()
    {
        hasActiveLaneVariation = false;
    }

    // Donne les positions monde des deux zones de pose.
    // GameManager les transmet ensuite a PlayZoneRenderer.
    public void GetPlayZoneWorldPositions(out Vector3 leftPosition, out Vector3 rightPosition)
    {
        EnsureParent();

        leftPosition = leftPlayZoneWorldPosition;
        rightPosition = rightPlayZoneWorldPosition;
    }

    // Supprime tous les dominos visuels de la table.
    public void ClearBoard()
    {
        for (int i = spawnedTiles.Count - 1; i >= 0; i--)
        {
            if (spawnedTiles[i] != null)
                Destroy(spawnedTiles[i]);
        }

        spawnedTiles.Clear();
        occupiedHitboxes.Clear();
        occupiedBodyHitboxes.Clear();
        renderedChain.Clear();
        hasStableBoardLayout = false;
        renderedCenterTileIndex = -1;
    }

    // Place un domino sur une branche gauche ou droite.
    private void PlaceBranchTile(DominoTile tile, ref LayoutCursor cursor, bool rightSide)
    {
        PlacementCandidate candidate = FindBestPlacement(tile, cursor, rightSide);

        if (Vector2.Distance(candidate.Position, cursor.Position) < GetMinimumEmergencyProgress(candidate.Footprint))
        {
            Vector2[] rescueDirections =
            {
                cursor.Direction,
                GetPreferredTurnDirection(cursor, rightSide),
                GetAlternativeTurnDirection(cursor, rightSide)
            };

            candidate = FindEmergencyPlacement(tile, cursor, rescueDirections, rightSide, cursor.LastTileWasDouble);
        }

        int hitboxIndex = PlaceTile(
            candidate.DisplayLeft,
            candidate.DisplayRight,
            candidate.Position,
            candidate.Angle,
            10);

        if (candidate.Direction != cursor.Direction)
        {
            cursor.TurnCount++;
            cursor.TilesInCurrentDirection = 1;
        }
        else
        {
            cursor.TilesInCurrentDirection++;
        }

        cursor.Position = candidate.Position;
        cursor.OpenPoint = candidate.NextOpenPoint;
        cursor.Direction = candidate.Direction;
        cursor.LastFootprint = candidate.Footprint;
        cursor.LastHitboxIndex = hitboxIndex;
        cursor.LastTileWasDouble = tile.IsDouble();
    }

    // Cherche la meilleure position pour le prochain domino.
    // Au lieu de prendre le premier emplacement libre, on compare l'espace disponible
    // devant chaque direction : tout droit, virage haut, virage bas.
    private PlacementCandidate FindBestPlacement(DominoTile tile, LayoutCursor cursor, bool rightSide)
    {
        Vector2[] directions =
        {
            cursor.Direction,
            GetPreferredTurnDirection(cursor, rightSide),
            GetAlternativeTurnDirection(cursor, rightSide)
        };

        if (keepLineThroughDoubles)
        {
            if (tile.IsDouble())
                return FindStraightPlacementAroundDouble(tile, cursor, directions, rightSide);

            if (cursor.LastTileWasDouble)
                return FindPlacementAfterDouble(tile, cursor, directions, rightSide);
        }

        if (useReferenceLanePath)
            return FindReferenceLanePlacement(tile, cursor, directions, rightSide);

        PlacementCandidate bestBlockedCandidate = CreatePlacementCandidate(tile, cursor, directions[0], rightSide);
        PlacementCandidate bestOpenCandidate = bestBlockedCandidate;
        int lowestBodyCollisionCount = int.MaxValue;
        int lowestCollisionCount = int.MaxValue;
        float bestOpenScore = float.MinValue;
        float bestBlockedScore = float.MinValue;
        bool foundOpenCandidate = false;
        bool foundInsideCandidate = false;

        foreach (Vector2 direction in directions)
        {
            PlacementCandidate candidate = CreatePlacementCandidate(tile, cursor, direction, rightSide);

            if (WouldLeaveTable(candidate.Position, candidate.Footprint))
                continue;

            candidate.CollisionCount = CountOverlaps(candidate.Hitbox, cursor.LastHitboxIndex);
            candidate.BodyCollisionCount = CountBodyOverlaps(candidate.BodyHitbox, cursor.LastHitboxIndex);
            candidate.FreeSpaceScore = ScoreFreeTableSpace(candidate, cursor.LastHitboxIndex);

            if (direction == cursor.Direction)
                candidate.FreeSpaceScore += straightDirectionBonus;

            if (candidate.CollisionCount == 0)
            {
                if (!foundOpenCandidate || candidate.FreeSpaceScore > bestOpenScore)
                {
                    bestOpenCandidate = candidate;
                    bestOpenScore = candidate.FreeSpaceScore;
                    foundOpenCandidate = true;
                }
            }

            if (!foundInsideCandidate ||
                candidate.BodyCollisionCount < lowestBodyCollisionCount ||
                candidate.BodyCollisionCount == lowestBodyCollisionCount && candidate.CollisionCount < lowestCollisionCount ||
                candidate.BodyCollisionCount == lowestBodyCollisionCount &&
                candidate.CollisionCount == lowestCollisionCount &&
                candidate.FreeSpaceScore > bestBlockedScore)
            {
                bestBlockedCandidate = candidate;
                lowestBodyCollisionCount = candidate.BodyCollisionCount;
                lowestCollisionCount = candidate.CollisionCount;
                bestBlockedScore = candidate.FreeSpaceScore;
                foundInsideCandidate = true;
            }
        }

        if (foundOpenCandidate)
            return bestOpenCandidate;

        if (foundInsideCandidate)
            return bestBlockedCandidate;

        // Secours : si aucune direction standard ne rentre dans la table, on
        // cherche une vraie sortie depuis le dernier domino au lieu de clamper
        // au bord. Le clamp etait la cause typique des empilements en fin de manche.
        return FindEmergencyPlacement(tile, cursor, directions, rightSide, false);
    }

    // Regle speciale autour des doubles.
    // Exemple : si la chaine avance horizontalement, le double est affiche verticalement,
    // puis le domino suivant continue horizontalement de l'autre cote du double.
    private PlacementCandidate FindStraightPlacementAroundDouble(
        DominoTile tile,
        LayoutCursor cursor,
        Vector2[] directions,
        bool rightSide)
    {
        PlacementCandidate straightCandidate = CreatePlacementCandidate(tile, cursor, directions[0], rightSide);

        if (TryEvaluateCandidate(ref straightCandidate, cursor.LastHitboxIndex) &&
            straightCandidate.CollisionCount == 0 &&
            straightCandidate.BodyCollisionCount == 0)
        {
            // Un double reste d'abord la piece perpendiculaire claire du trajet.
            // On evite de l'utiliser comme coin, sinon il devient vite illisible.
            return straightCandidate;
        }

        // Si le couloir courant est termine, on autorise le double a prendre
        // le nouveau couloir pour ne pas casser le serpentin.
        if (useReferenceLanePath)
        {
            PlacementCandidate bestTurnCandidate = straightCandidate;
            float bestTurnScore = float.MinValue;
            bool foundTurn = false;

            for (int i = 1; i < directions.Length; i++)
            {
                PlacementCandidate turnCandidate = CreatePlacementCandidate(tile, cursor, directions[i], rightSide);

                if (!TryEvaluateCandidate(ref turnCandidate, cursor.LastHitboxIndex))
                    continue;

                if (turnCandidate.CollisionCount > 0)
                    continue;

                if (i == 1)
                    turnCandidate.FreeSpaceScore += preferredTurnBonus * 0.2f;

                if (!foundTurn || turnCandidate.FreeSpaceScore > bestTurnScore)
                {
                    bestTurnCandidate = turnCandidate;
                    bestTurnScore = turnCandidate.FreeSpaceScore;
                    foundTurn = true;
                }
            }

            if (foundTurn)
                return bestTurnCandidate;
        }

        // Si le placement droit est vraiment impossible parce qu'on est au bord
        // ou qu'un ancien domino bloque la route, on garde quand meme une solution
        // la moins mauvaise possible.
        return FindLeastBadPlacement(tile, cursor, directions, rightSide);
    }

    // Regle speciale pour le domino joue juste apres un double.
    // Par defaut, on continue dans l'axe courant. Mais si cela devient trop serre
    // pres du bord ou d'une zone occupee, on autorise une sortie "comme un domino
    // normal" depuis le cote du double pour prendre un virage propre.
    private PlacementCandidate FindPlacementAfterDouble(
        DominoTile tile,
        LayoutCursor cursor,
        Vector2[] directions,
        bool rightSide)
    {
        PlacementCandidate straightCandidate = CreatePlacementCandidate(tile, cursor, directions[0], rightSide);
        bool straightInside = TryEvaluateCandidate(ref straightCandidate, cursor.LastHitboxIndex);
        bool straightOpen = straightInside && straightCandidate.CollisionCount == 0;

        if (straightOpen && (!useReferenceLanePath || ShouldKeepStraightInReferencePath(cursor, straightCandidate, rightSide)))
            return straightCandidate;

        PlacementCandidate bestTurnCandidate = straightCandidate;
        float bestTurnScore = float.MinValue;
        bool foundTurn = false;

        for (int i = 1; i < directions.Length; i++)
        {
            PlacementCandidate turnCandidate = CreatePlacementCandidateAfterDoubleTurn(tile, cursor, directions[i], rightSide);

            if (!TryEvaluateCandidate(ref turnCandidate, cursor.LastHitboxIndex))
                continue;

            if (turnCandidate.CollisionCount > 0)
                continue;

            if (i == 1)
                turnCandidate.FreeSpaceScore += preferredTurnBonus * 0.35f;

            if (!foundTurn || turnCandidate.FreeSpaceScore > bestTurnScore)
            {
                bestTurnCandidate = turnCandidate;
                bestTurnScore = turnCandidate.FreeSpaceScore;
                foundTurn = true;
            }
        }

        if (foundTurn)
            return bestTurnCandidate;

        if (straightOpen)
            return straightCandidate;

        return FindLeastBadPlacementAfterDouble(tile, cursor, directions, rightSide);
    }

    // Placement proche de la reference :
    // - on continue tout droit tant qu'il reste assez de piste ;
    // - si on approche d'un bord ou d'une zone chargee, on compare haut/bas ;
    // - on garde les hitbox comme securite pour ne pas traverser la chaine.
    private PlacementCandidate FindReferenceLanePlacement(
        DominoTile tile,
        LayoutCursor cursor,
        Vector2[] directions,
        bool rightSide)
    {
        PlacementCandidate straightCandidate = CreatePlacementCandidate(tile, cursor, directions[0], rightSide);
        bool straightInside = TryEvaluateCandidate(ref straightCandidate, cursor.LastHitboxIndex);
        bool straightOpen = straightInside && straightCandidate.CollisionCount == 0;

        if (straightOpen && ShouldKeepStraightInReferencePath(cursor, straightCandidate, rightSide))
            return straightCandidate;

        PlacementCandidate bestOpenTurn = straightCandidate;
        float bestTurnScore = float.MinValue;
        bool foundOpenTurn = false;

        for (int i = 1; i < directions.Length; i++)
        {
            PlacementCandidate turnCandidate = CreatePlacementCandidate(tile, cursor, directions[i], rightSide);

            if (!TryEvaluateCandidate(ref turnCandidate, cursor.LastHitboxIndex))
                continue;

            if (turnCandidate.CollisionCount > 0)
                continue;

            // On garde un petit bonus pour le virage naturel au tout premier coude,
            // mais ensuite on laisse surtout l'espace libre decider. Sinon la chaine
            // peut continuer vers une zone deja occupee juste "par habitude".
            if (i == 1)
            {
                float turnPreference = cursor.TurnCount == 0 ? preferredTurnBonus : preferredTurnBonus * 0.15f;
                turnCandidate.FreeSpaceScore += turnPreference;
            }

            if (!foundOpenTurn || turnCandidate.FreeSpaceScore > bestTurnScore)
            {
                bestOpenTurn = turnCandidate;
                bestTurnScore = turnCandidate.FreeSpaceScore;
                foundOpenTurn = true;
            }
        }

        if (foundOpenTurn)
            return bestOpenTurn;

        if (straightOpen)
            return straightCandidate;

        return FindLeastBadPlacement(tile, cursor, directions, rightSide);
    }

    // Decide si on doit rester sur la ligne actuelle dans le mode "reference".
    // Regle voulue :
    // - sur une ligne horizontale, on continue jusqu'a approcher du bord ;
    // - sur un petit connecteur vertical, on ne monte/descend que sur quelques dominos,
    //   puis on repart horizontalement.
    private bool ShouldKeepStraightInReferencePath(
        LayoutCursor cursor,
        PlacementCandidate straightCandidate,
        bool rightSide)
    {
        if (IsHorizontal(cursor.Direction))
        {
            float distanceToEdge = GetDistanceToTableEdge(
                straightCandidate.Position,
                straightCandidate.Direction,
                straightCandidate.Footprint);
            int freeStepsAhead = CountFreeStepsAhead(straightCandidate, cursor.LastHitboxIndex);

            return distanceToEdge > GetEdgeTurnReserveForSide(rightSide) &&
                   freeStepsAhead >= GetTurnReserveTilesForSide(rightSide);
        }

        return cursor.TilesInCurrentDirection < Mathf.Max(1, GetConnectorTilesForSide(rightSide));
    }

    // Evalue un candidat : il doit etre dans la table, puis on calcule collisions et espace libre.
    private bool TryEvaluateCandidate(ref PlacementCandidate candidate, int ignoredHitboxIndex)
    {
        if (WouldLeaveTable(candidate.Position, candidate.Footprint))
            return false;

        candidate.CollisionCount = CountOverlaps(candidate.Hitbox, ignoredHitboxIndex);
        candidate.BodyCollisionCount = CountBodyOverlaps(candidate.BodyHitbox, ignoredHitboxIndex);
        candidate.FreeSpaceScore = ScoreFreeTableSpace(candidate, ignoredHitboxIndex);
        return true;
    }

    // Secours quand tout est serre : on prend l'option qui chevauche le moins
    // et qui garde le plus d'espace autour d'elle.
    private PlacementCandidate FindLeastBadPlacement(
        DominoTile tile,
        LayoutCursor cursor,
        Vector2[] directions,
        bool rightSide)
    {
        PlacementCandidate bestCandidate = CreatePlacementCandidate(tile, cursor, directions[0], rightSide);
        int lowestBodyCollisionCount = int.MaxValue;
        int lowestCollisionCount = int.MaxValue;
        float bestScore = float.MinValue;
        bool foundInsideCandidate = false;

        foreach (Vector2 direction in directions)
        {
            PlacementCandidate candidate = CreatePlacementCandidate(tile, cursor, direction, rightSide);

            if (!TryEvaluateCandidate(ref candidate, cursor.LastHitboxIndex))
                continue;

            if (!foundInsideCandidate ||
                candidate.BodyCollisionCount < lowestBodyCollisionCount ||
                candidate.BodyCollisionCount == lowestBodyCollisionCount && candidate.CollisionCount < lowestCollisionCount ||
                candidate.BodyCollisionCount == lowestBodyCollisionCount &&
                candidate.CollisionCount == lowestCollisionCount &&
                candidate.FreeSpaceScore > bestScore)
            {
                bestCandidate = candidate;
                lowestBodyCollisionCount = candidate.BodyCollisionCount;
                lowestCollisionCount = candidate.CollisionCount;
                bestScore = candidate.FreeSpaceScore;
                foundInsideCandidate = true;
            }
        }

        if (!foundInsideCandidate)
            return FindEmergencyPlacement(tile, cursor, directions, rightSide, false);

        bestCandidate.CollisionCount = CountOverlaps(bestCandidate.Hitbox, cursor.LastHitboxIndex);
        bestCandidate.BodyCollisionCount = CountBodyOverlaps(bestCandidate.BodyHitbox, cursor.LastHitboxIndex);
        bestCandidate.FreeSpaceScore = ScoreFreeTableSpace(bestCandidate, cursor.LastHitboxIndex);
        return bestCandidate;
    }

    // Variante de secours pour le domino place juste apres un double.
    // On compare la continuation droite et la sortie en virage, puis on garde
    // le moins mauvais choix si la table devient vraiment serree.
    private PlacementCandidate FindLeastBadPlacementAfterDouble(
        DominoTile tile,
        LayoutCursor cursor,
        Vector2[] directions,
        bool rightSide)
    {
        PlacementCandidate bestCandidate = CreatePlacementCandidate(tile, cursor, directions[0], rightSide);
        int lowestBodyCollisionCount = int.MaxValue;
        int lowestCollisionCount = int.MaxValue;
        float bestScore = float.MinValue;
        bool foundInsideCandidate = false;

        for (int i = 0; i < directions.Length; i++)
        {
            PlacementCandidate candidate = i == 0
                ? CreatePlacementCandidate(tile, cursor, directions[i], rightSide)
                : CreatePlacementCandidateAfterDoubleTurn(tile, cursor, directions[i], rightSide);

            if (!TryEvaluateCandidate(ref candidate, cursor.LastHitboxIndex))
                continue;

            if (!foundInsideCandidate ||
                candidate.BodyCollisionCount < lowestBodyCollisionCount ||
                candidate.BodyCollisionCount == lowestBodyCollisionCount && candidate.CollisionCount < lowestCollisionCount ||
                candidate.BodyCollisionCount == lowestBodyCollisionCount &&
                candidate.CollisionCount == lowestCollisionCount &&
                candidate.FreeSpaceScore > bestScore)
            {
                bestCandidate = candidate;
                lowestBodyCollisionCount = candidate.BodyCollisionCount;
                lowestCollisionCount = candidate.CollisionCount;
                bestScore = candidate.FreeSpaceScore;
                foundInsideCandidate = true;
            }
        }

        if (!foundInsideCandidate)
            return FindEmergencyPlacement(tile, cursor, directions, rightSide, true);

        bestCandidate.CollisionCount = CountOverlaps(bestCandidate.Hitbox, cursor.LastHitboxIndex);
        bestCandidate.BodyCollisionCount = CountBodyOverlaps(bestCandidate.BodyHitbox, cursor.LastHitboxIndex);
        bestCandidate.FreeSpaceScore = ScoreFreeTableSpace(bestCandidate, cursor.LastHitboxIndex);
        return bestCandidate;
    }

    // Dernier secours anti-empilement.
    // Quand tous les candidats standards sortent de la table, on ne les plaque
    // plus contre le bord. On force plutot une direction qui avance vraiment
    // depuis le dernier domino, meme si le raccord est un peu moins parfait.
    private PlacementCandidate FindEmergencyPlacement(
        DominoTile tile,
        LayoutCursor cursor,
        Vector2[] preferredDirections,
        bool rightSide,
        bool allowAfterDoubleTurn)
    {
        List<Vector2> directions = new List<Vector2>();

        for (int i = 0; i < preferredDirections.Length; i++)
            AddUniqueDirection(directions, preferredDirections[i]);

        AddUniqueDirection(directions, GetDirectionTowardTableCenter(cursor.Position));
        AddUniqueDirection(directions, cursor.Position.x >= 0f ? Vector2.left : Vector2.right);
        AddUniqueDirection(directions, cursor.Position.y >= 0f ? Vector2.down : Vector2.up);
        AddUniqueDirection(directions, Vector2.right);
        AddUniqueDirection(directions, Vector2.left);
        AddUniqueDirection(directions, Vector2.up);
        AddUniqueDirection(directions, Vector2.down);

        PlacementCandidate bestCandidate = CreateLooseEmergencyCandidate(tile, cursor, directions[0], rightSide);
        int lowestBodyCollisionCount = int.MaxValue;
        int lowestCollisionCount = int.MaxValue;
        float bestProgress = float.MinValue;
        float bestScore = float.MinValue;
        bool foundCandidate = false;

        foreach (Vector2 direction in directions)
        {
            PlacementCandidate candidate = allowAfterDoubleTurn && cursor.LastTileWasDouble && direction != cursor.Direction
                ? CreatePlacementCandidateAfterDoubleTurn(tile, cursor, direction, rightSide)
                : CreatePlacementCandidate(tile, cursor, direction, rightSide);

            if (WouldLeaveTable(candidate.Position, candidate.Footprint))
                candidate = CreateLooseEmergencyCandidate(tile, cursor, direction, rightSide);

            if (!TryEvaluateCandidate(ref candidate, cursor.LastHitboxIndex))
                continue;

            float progress = Vector2.Distance(candidate.Position, cursor.Position);

            if (progress < GetMinimumEmergencyProgress(candidate.Footprint))
                continue;

            candidate.FreeSpaceScore += progress * 0.25f;

            if (!foundCandidate ||
                candidate.BodyCollisionCount < lowestBodyCollisionCount ||
                candidate.BodyCollisionCount == lowestBodyCollisionCount && candidate.CollisionCount < lowestCollisionCount ||
                candidate.BodyCollisionCount == lowestBodyCollisionCount &&
                candidate.CollisionCount == lowestCollisionCount &&
                progress > bestProgress ||
                candidate.BodyCollisionCount == lowestBodyCollisionCount &&
                candidate.CollisionCount == lowestCollisionCount &&
                Mathf.Approximately(progress, bestProgress) &&
                candidate.FreeSpaceScore > bestScore)
            {
                bestCandidate = candidate;
                lowestBodyCollisionCount = candidate.BodyCollisionCount;
                lowestCollisionCount = candidate.CollisionCount;
                bestProgress = progress;
                bestScore = candidate.FreeSpaceScore;
                foundCandidate = true;
            }
        }

        if (foundCandidate)
            return bestCandidate;

        // Ultime garde-fou : on avance vers le centre de la table. Cette option
        // est tres rare, mais elle evite de rendre deux fois la meme position.
        PlacementCandidate forcedCandidate = CreateLooseEmergencyCandidate(
            tile,
            cursor,
            GetDirectionTowardTableCenter(cursor.Position),
            rightSide);

        TryEvaluateCandidate(ref forcedCandidate, cursor.LastHitboxIndex);
        return forcedCandidate;
    }

    // Candidat de secours base sur le centre du dernier domino, pas sur OpenPoint.
    // Cela garantit une progression reelle meme si OpenPoint est deja trop proche
    // d'un bord ou d'une ancienne hitbox.
    private PlacementCandidate CreateLooseEmergencyCandidate(
        DominoTile tile,
        LayoutCursor cursor,
        Vector2 direction,
        bool rightSide)
    {
        direction = NormalizeDirection(direction);
        bool isDouble = tile.IsDouble();
        float angle = GetRotationAngleForDirection(direction, isDouble);
        Vector2 footprint = GetFootprintForAngle(angle);
        float step = GetTouchingStep(cursor.LastFootprint, footprint, direction);
        Vector2 position = cursor.Position + direction * step;

        position = ClampInsideTable(position, footprint);

        GetBranchValues(tile, rightSide, out int inwardValue, out int outwardValue);

        return new PlacementCandidate
        {
            Position = position,
            NextOpenPoint = GetNextOpenPoint(position, direction, isDouble),
            Direction = direction,
            Footprint = footprint,
            Angle = angle,
            Hitbox = CreateHitbox(position, footprint, isDouble),
            BodyHitbox = CreateBodyHitbox(position, footprint),
            DisplayLeft = inwardValue,
            DisplayRight = outwardValue,
            CollisionCount = 0,
            BodyCollisionCount = 0,
            FreeSpaceScore = 0f
        };
    }

    // Evite les doublons dans la liste de directions de secours.
    private void AddUniqueDirection(List<Vector2> directions, Vector2 direction)
    {
        direction = NormalizeDirection(direction);

        if (direction == Vector2.zero)
            return;

        for (int i = 0; i < directions.Count; i++)
        {
            if (directions[i] == direction)
                return;
        }

        directions.Add(direction);
    }

    // Convertit une direction quelconque en direction cardinale propre.
    private Vector2 NormalizeDirection(Vector2 direction)
    {
        if (direction == Vector2.zero)
            return Vector2.zero;

        if (Mathf.Abs(direction.x) > Mathf.Abs(direction.y))
            return direction.x >= 0f ? Vector2.right : Vector2.left;

        return direction.y >= 0f ? Vector2.up : Vector2.down;
    }

    // Choisit l'axe qui ramene le plus vite la branche vers l'interieur de la table.
    private Vector2 GetDirectionTowardTableCenter(Vector2 position)
    {
        float halfWidth = Mathf.Max(0.01f, Mathf.Max(Mathf.Abs(minTableX), Mathf.Abs(maxTableX)));
        float halfHeight = Mathf.Max(0.01f, Mathf.Max(Mathf.Abs(minTableY), Mathf.Abs(maxTableY)));
        float horizontalPressure = Mathf.Abs(position.x) / halfWidth;
        float verticalPressure = Mathf.Abs(position.y) / halfHeight;

        if (horizontalPressure >= verticalPressure)
            return position.x >= 0f ? Vector2.left : Vector2.right;

        return position.y >= 0f ? Vector2.down : Vector2.up;
    }

    // Distance minimale pour accepter un placement de secours.
    private float GetMinimumEmergencyProgress(Vector2 footprint)
    {
        return Mathf.Min(footprint.x, footprint.y) * 0.45f;
    }

    // Cree un candidat complet pour une direction donnee.
    private PlacementCandidate CreatePlacementCandidate(
        DominoTile tile,
        LayoutCursor cursor,
        Vector2 direction,
        bool rightSide)
    {
        bool isDouble = tile.IsDouble();
        float angle = GetRotationAngleForDirection(direction, isDouble);
        Vector2 footprint = GetFootprintForAngle(angle);
        Vector2 position = GetPlacementPosition(cursor, direction, isDouble);
        Vector2 nextOpenPoint = GetNextOpenPoint(position, direction, isDouble);
        GetBranchValues(tile, rightSide, out int inwardValue, out int outwardValue);

        return new PlacementCandidate
        {
            Position = position,
            NextOpenPoint = nextOpenPoint,
            Direction = direction,
            Footprint = footprint,
            Angle = angle,
            Hitbox = CreateHitbox(position, footprint, isDouble),
            BodyHitbox = CreateBodyHitbox(position, footprint),
            DisplayLeft = inwardValue,
            DisplayRight = outwardValue,
            CollisionCount = 0,
            BodyCollisionCount = 0,
            FreeSpaceScore = 0f
        };
    }

    // Cree un candidat en sortant lateralement d'un double deja pose.
    // On utilise cette variante seulement pour le domino qui suit immediatement
    // un double, quand la continuation standard deviendrait trop serree.
    private PlacementCandidate CreatePlacementCandidateAfterDoubleTurn(
        DominoTile tile,
        LayoutCursor cursor,
        Vector2 direction,
        bool rightSide)
    {
        bool isDouble = tile.IsDouble();
        float angle = GetRotationAngleForDirection(direction, isDouble);
        Vector2 footprint = GetFootprintForAngle(angle);
        Vector2 openPoint = GetSideExitOpenPoint(cursor, direction);
        Vector2 position = openPoint + direction * (spacing + GetConnectorHalfLength(isDouble));
        Vector2 nextOpenPoint = GetNextOpenPoint(position, direction, isDouble);
        GetBranchValues(tile, rightSide, out int inwardValue, out int outwardValue);

        return new PlacementCandidate
        {
            Position = position,
            NextOpenPoint = nextOpenPoint,
            Direction = direction,
            Footprint = footprint,
            Angle = angle,
            Hitbox = CreateHitbox(position, footprint, isDouble),
            BodyHitbox = CreateBodyHitbox(position, footprint),
            DisplayLeft = inwardValue,
            DisplayRight = outwardValue,
            CollisionCount = 0,
            BodyCollisionCount = 0,
            FreeSpaceScore = 0f
        };
    }

    // Calcule le centre du domino a partir du point logique ouvert de la chaine.
    // En ligne droite, on garde le placement simple. En virage, on attache le
    // domino sur la bonne moitie (haut/bas ou gauche/droite) pour obtenir le
    // rendu propre de la reference au lieu d'un raccord "au milieu".
    private Vector2 GetPlacementPosition(LayoutCursor cursor, Vector2 direction, bool isDouble)
    {
        float connectorHalfLength = GetConnectorHalfLength(isDouble);

        if (direction == cursor.Direction || isDouble)
            return cursor.OpenPoint + direction * (spacing + connectorHalfLength);

        Vector2 turnAnchorOffset = GetTurnIncomingAnchorOffset(cursor.Direction, direction);
        return cursor.OpenPoint - turnAnchorOffset;
    }

    // Point d'ouverture du cote libre du domino nouvellement pose.
    private Vector2 GetNextOpenPoint(Vector2 position, Vector2 direction, bool isDouble)
    {
        return position + direction * GetConnectorHalfLength(isDouble);
    }

    // Point de sortie lateral quand on veut traiter un double comme un point
    // de continuation "normal" pour le domino suivant.
    private Vector2 GetSideExitOpenPoint(LayoutCursor cursor, Vector2 direction)
    {
        float halfExtent = GetExtentAlongDirection(cursor.LastFootprint, direction) * 0.5f;
        return cursor.Position + direction * halfExtent;
    }

    // Point de contact d'un domino non-double au moment d'un virage.
    // Exemple :
    // - si on allait vers la droite puis vers le bas, le domino vertical doit
    //   toucher le precedent sur la moitie haute de son cote ;
    // - si on allait vers le bas puis vers la droite, le domino horizontal doit
    //   toucher le precedent sur la moitie gauche de son haut.
    private Vector2 GetTurnIncomingAnchorOffset(Vector2 previousDirection, Vector2 newDirection)
    {
        float halfShort = tileHeight * 0.5f;
        float quarterLong = tileWidth * 0.25f;

        if (newDirection == Vector2.up)
            return new Vector2(previousDirection == Vector2.right ? -halfShort : halfShort, -quarterLong);

        if (newDirection == Vector2.down)
            return new Vector2(previousDirection == Vector2.right ? -halfShort : halfShort, quarterLong);

        if (newDirection == Vector2.right)
            return new Vector2(-quarterLong, previousDirection == Vector2.up ? -halfShort : halfShort);

        return new Vector2(quarterLong, previousDirection == Vector2.up ? -halfShort : halfShort);
    }

    // Retourne les valeurs a afficher en gardant la logique du cote qui touche
    // la chaine et du cote qui reste ouvert.
    private void GetBranchValues(DominoTile tile, bool rightSide, out int inwardValue, out int outwardValue)
    {
        if (rightSide)
        {
            inwardValue = tile.Left;
            outwardValue = tile.Right;
            return;
        }

        inwardValue = tile.Right;
        outwardValue = tile.Left;
    }

    // Indique si, au prochain virage horizontal, la branche doit revenir vers le
    // centre ou repartir vers l'exterieur. Cela cree un serpentin propre :
    // bord -> couloir interieur -> bord -> couloir exterieur...
    private bool ShouldHeadTowardCenter(LayoutCursor cursor)
    {
        int completedVerticalConnectors = Mathf.Max(0, (cursor.TurnCount - 1) / 2);
        return completedVerticalConnectors % 2 == 0;
    }

    // Retourne la prochaine direction horizontale logique quand on sort d'un
    // connecteur vertical. On alterne entre "vers le centre" et "vers le bord"
    // pour que la branche garde son propre couloir au lieu de se replier sur elle.
    private Vector2 GetSnakeHorizontalDirection(LayoutCursor cursor, bool rightSide, bool towardCenter)
    {
        if (rightSide)
            return towardCenter ? Vector2.left : Vector2.right;

        return towardCenter ? Vector2.right : Vector2.left;
    }

    // Tourne dans le sens principal de la chaine.
    // Les segments horizontaux alternent entre la verticale principale puis
    // la verticale de retour. Les segments verticaux alternent ensuite leurs lignes
    // horizontales pour dessiner un vrai serpentin.
    private Vector2 GetPreferredTurnDirection(LayoutCursor cursor, bool rightSide)
    {
        Vector2 currentDirection = cursor.Direction;

        if (IsHorizontal(currentDirection))
            return GetPreferredVerticalDirection(cursor, rightSide);

        return GetSnakeHorizontalDirection(cursor, rightSide, ShouldHeadTowardCenter(cursor));
    }

    // Tourne de l'autre cote si le virage principal est bloque.
    private Vector2 GetAlternativeTurnDirection(LayoutCursor cursor, bool rightSide)
    {
        Vector2 currentDirection = cursor.Direction;

        if (IsHorizontal(currentDirection))
            return GetPreferredVerticalDirection(cursor, rightSide) == Vector2.up ? Vector2.down : Vector2.up;

        return GetSnakeHorizontalDirection(cursor, rightSide, !ShouldHeadTowardCenter(cursor));
    }

    // Sur les segments horizontaux, on alterne les virages verticaux :
    // premier couloir -> on s'eloigne du centre ;
    // couloir suivant -> on revient ;
    // puis on recommence si la manche continue encore.
    private Vector2 GetPreferredVerticalDirection(LayoutCursor cursor, bool rightSide)
    {
        int completedHorizontalLegs = cursor.TurnCount / 2;
        bool usePrimaryDirection = completedHorizontalLegs % 2 == 0;

        return usePrimaryDirection
            ? GetPrimaryVerticalDirection(rightSide)
            : GetSecondaryVerticalDirection(rightSide);
    }

    // Direction verticale principale de ce cote pour la manche en cours.
    private Vector2 GetPrimaryVerticalDirection(bool rightSide)
    {
        int sign = rightSide ? rightPrimaryVerticalSign : leftPrimaryVerticalSign;
        return sign >= 0 ? Vector2.up : Vector2.down;
    }

    // Direction verticale secondaire gardee comme secours si le virage principal
    // est bloque. Le serpentin normal n'alterne plus entre haut et bas, car cela
    // finissait par renvoyer la branche dans ses propres hitbox en fin de partie.
    private Vector2 GetSecondaryVerticalDirection(bool rightSide)
    {
        int sign = rightSide ? -rightPrimaryVerticalSign : -leftPrimaryVerticalSign;
        return sign >= 0 ? Vector2.up : Vector2.down;
    }

    // Longueur du petit connecteur vertical pour ce cote.
    private int GetConnectorTilesForSide(bool rightSide)
    {
        return rightSide ? rightConnectorTilesThisRound : leftConnectorTilesThisRound;
    }

    // Reserve avant de tourner pour ce cote.
    private float GetEdgeTurnReserveForSide(bool rightSide)
    {
        return rightSide ? rightEdgeTurnReserveThisRound : leftEdgeTurnReserveThisRound;
    }

    // Nombre de dominos qu'on veut encore pouvoir loger tout droit
    // avant de lancer le virage pour ce cote.
    private int GetTurnReserveTilesForSide(bool rightSide)
    {
        return rightSide ? rightTurnReserveTilesThisRound : leftTurnReserveTilesThisRound;
    }

    // Convertit une marge exprimee en "nombre de dominos restants"
    // en distance reelle jusqu'au bord de la table.
    private float GetTurnReserveDistance(int reserveTiles)
    {
        float tileStep = tileWidth + spacing;
        return Mathf.Max(edgeTurnReserve, Mathf.Max(1, reserveTiles) * tileStep * 0.72f);
    }

    // Verifie si le prochain domino sortirait de la table.
    private bool WouldLeaveTable(Vector2 position, Vector2 footprint)
    {
        float halfX = footprint.x * 0.5f;
        float halfY = footprint.y * 0.5f;

        return position.x - halfX < minTableX ||
               position.x + halfX > maxTableX ||
               position.y - halfY < minTableY ||
               position.y + halfY > maxTableY;
    }

    // Evite les depassements visuels si un virage arrive tres proche d'un bord.
    private Vector2 ClampInsideTable(Vector2 position, Vector2 footprint)
    {
        float halfX = footprint.x * 0.5f;
        float halfY = footprint.y * 0.5f;

        return new Vector2(
            Mathf.Clamp(position.x, minTableX + halfX, maxTableX - halfX),
            Mathf.Clamp(position.y, minTableY + halfY, maxTableY - halfY));
    }

    // Cree la hitbox locale du domino avec une petite marge.
    private Rect CreateHitbox(Vector2 position, Vector2 footprint, bool reserveExtraForDouble = false)
    {
        float effectiveMargin = collisionMargin;

        if (reserveExtraForDouble)
            effectiveMargin += Mathf.Max(0f, doubleCollisionExtraMargin);

        float width = footprint.x + effectiveMargin * 2f;
        float height = footprint.y + effectiveMargin * 2f;

        return new Rect(
            position.x - width * 0.5f,
            position.y - height * 0.5f,
            width,
            height);
    }

    // Hitbox du corps visible, legerement reduite pour permettre le contact normal
    // entre deux dominos voisins sans compter cela comme un vrai chevauchement.
    private Rect CreateBodyHitbox(Vector2 position, Vector2 footprint)
    {
        float shrink = Mathf.Max(0.025f, spacing + 0.02f);
        float width = Mathf.Max(0.01f, footprint.x - shrink * 2f);
        float height = Mathf.Max(0.01f, footprint.y - shrink * 2f);

        return new Rect(
            position.x - width * 0.5f,
            position.y - height * 0.5f,
            width,
            height);
    }

    // Compte les hitbox deja occupees qui croisent la nouvelle position.
    // On ignore le domino precedent, parce que le nouveau domino doit le toucher.
    private int CountOverlaps(Rect candidate, int ignoredHitboxIndex)
    {
        int count = 0;

        for (int i = 0; i < occupiedHitboxes.Count; i++)
        {
            if (i == ignoredHitboxIndex)
                continue;

            if (candidate.Overlaps(occupiedHitboxes[i], true))
                count++;
        }

        return count;
    }

    // Compte les vrais chevauchements du corps visible, plus grave qu'un simple
    // contact avec la marge de securite.
    private int CountBodyOverlaps(Rect candidate, int ignoredHitboxIndex)
    {
        int count = 0;

        for (int i = 0; i < occupiedBodyHitboxes.Count; i++)
        {
            if (i == ignoredHitboxIndex)
                continue;

            if (candidate.Overlaps(occupiedBodyHitboxes[i], true))
                count++;
        }

        return count;
    }

    // Compte combien de futurs dominos pourraient encore rentrer tout droit
    // apres ce candidat. Cette lecture donne le style de grande ligne propre :
    // on continue seulement si la piste devant nous n'est pas deja courte.
    private int CountFreeStepsAhead(PlacementCandidate candidate, int ignoredHitboxIndex)
    {
        Vector2 forward = candidate.Direction.normalized;
        Vector2 futureFootprint = GetFootprintForAngle(GetRotationAngleForDirection(candidate.Direction, false));
        float futureStep = GetTouchingStep(candidate.Footprint, futureFootprint, forward);
        int scanSteps = Mathf.Max(1, spaceScanSteps);
        int freeSteps = 0;
        Vector2 samplePosition = candidate.Position;

        for (int i = 0; i < scanSteps; i++)
        {
            samplePosition += forward * futureStep;
            Rect sampleHitbox = CreateHitbox(samplePosition, futureFootprint);

            if (WouldLeaveTable(samplePosition, futureFootprint))
                break;

            if (CountOverlaps(sampleHitbox, ignoredHitboxIndex) > 0)
                break;

            freeSteps++;
        }

        return freeSteps;
    }

    // Donne une note a une direction selon l'espace libre devant elle.
    // On scanne un petit couloir devant le domino candidat, avec plusieurs lignes
    // laterales, pour savoir si la table est plus ouverte tout droit, vers le haut
    // ou vers le bas.
    private float ScoreFreeTableSpace(PlacementCandidate candidate, int ignoredHitboxIndex)
    {
        Vector2 forward = candidate.Direction.normalized;
        Vector2 side = new Vector2(-forward.y, forward.x);
        Vector2 futureFootprint = GetFootprintForAngle(GetRotationAngleForDirection(candidate.Direction, false));

        int scanSteps = Mathf.Max(1, spaceScanSteps);
        int sideLanes = Mathf.Max(0, spaceScanSideLanes);
        float scanStep = Mathf.Max(0.15f, spaceScanStepSize);
        float laneStep = tileHeight + collisionMargin;
        float baseForwardDistance = GetExtentAlongDirection(candidate.Footprint, forward) * 0.5f;
        float score = 0f;

        for (int forwardStep = 1; forwardStep <= scanSteps; forwardStep++)
        {
            float forwardDistance = baseForwardDistance + forwardStep * scanStep;

            for (int lane = -sideLanes; lane <= sideLanes; lane++)
            {
                Vector2 samplePosition = candidate.Position +
                                         forward * forwardDistance +
                                         side * lane * laneStep;

                Rect sampleHitbox = CreateHitbox(samplePosition, futureFootprint);

                if (WouldLeaveTable(samplePosition, futureFootprint))
                    continue;

                if (CountOverlaps(sampleHitbox, ignoredHitboxIndex) > 0)
                    continue;

                // Les cases proches valent un peu plus, car elles servent aux
                // prochains coups immediats. Les cases lointaines aident quand meme.
                score += 1f / forwardStep;
            }
        }

        score += GetDistanceToTableEdge(candidate.Position, candidate.Direction, candidate.Footprint) * 0.2f;

        return score;
    }

    // Distance entre un domino candidat et le bord de table dans sa direction.
    private float GetDistanceToTableEdge(Vector2 position, Vector2 direction, Vector2 footprint)
    {
        if (direction == Vector2.right)
            return maxTableX - (position.x + footprint.x * 0.5f);

        if (direction == Vector2.left)
            return position.x - footprint.x * 0.5f - minTableX;

        if (direction == Vector2.up)
            return maxTableY - (position.y + footprint.y * 0.5f);

        return position.y - footprint.y * 0.5f - minTableY;
    }

    // Position de la zone de pose a l'extremite d'une branche.
    private Vector2 GetZonePosition(LayoutCursor cursor)
    {
        Vector2 zoneFootprint = new Vector2(tileWidth, tileHeight);
        float step = tileWidth * 0.5f + playZoneOffset;
        Vector2 zonePosition = cursor.OpenPoint + cursor.Direction * step;
        return ClampInsideTable(zonePosition, zoneFootprint);
    }

    // Calcule la distance entre deux centres pour que les dominos se touchent presque.
    private float GetTouchingStep(Vector2 previousFootprint, Vector2 currentFootprint, Vector2 direction)
    {
        return GetExtentAlongDirection(previousFootprint, direction) * 0.5f +
               GetExtentAlongDirection(currentFootprint, direction) * 0.5f +
               spacing;
    }

    // Taille prise par un domino selon son angle de rotation.
    private Vector2 GetFootprintForAngle(float angle)
    {
        bool vertical = Mathf.Approximately(Mathf.Abs(Mathf.DeltaAngle(angle, 0f)), 90f);

        return vertical
            ? new Vector2(tileHeight, tileWidth)
            : new Vector2(tileWidth, tileHeight);
    }

    // Donne la largeur utile dans l'axe ou la chaine avance.
    private float GetExtentAlongDirection(Vector2 footprint, Vector2 direction)
    {
        return IsHorizontal(direction) ? footprint.x : footprint.y;
    }

    // Angle du premier domino de la manche.
    // Un double est mis debout pour ressembler a la vraie pose de depart.
    private float GetCenterRotationAngle(DominoTile tile)
    {
        return tile.IsDouble() ? 90f : 0f;
    }

    // Rotation visuelle du domino selon le sens dans lequel la branche avance.
    private float GetRotationAngleForDirection(Vector2 direction, bool isDouble)
    {
        if (isDouble)
            return IsHorizontal(direction) ? 90f : 0f;

        if (direction == Vector2.up)
            return 90f;

        if (direction == Vector2.left)
            return 180f;

        if (direction == Vector2.down)
            return -90f;

        return 0f;
    }

    // Oriente les valeurs affichees pour que la valeur qui touche la chaine soit du bon cote.
    // Cote droit : tile.Left touche la chaine et tile.Right regarde vers l'exterieur.
    // Cote gauche : tile.Right touche la chaine et tile.Left regarde vers l'exterieur.
    private void GetDisplayValues(DominoTile tile, bool rightSide, out int displayLeft, out int displayRight)
    {
        if (rightSide)
        {
            displayLeft = tile.Left;
            displayRight = tile.Right;
            return;
        }

        displayLeft = tile.Right;
        displayRight = tile.Left;
    }

    private bool IsHorizontal(Vector2 direction)
    {
        return Mathf.Abs(direction.x) > Mathf.Abs(direction.y);
    }

    // Cree le parent des dominos si l'utilisateur ne l'a pas assigne.
    private void EnsureParent()
    {
        if (boardParent != null)
            return;

        GameObject root = new GameObject("Board Visuals");
        root.transform.SetParent(transform, false);
        root.transform.localPosition = boardCenter;
        boardParent = root.transform;

        UpdateEmptyPlayZonePositions();
    }

    // Positions utilisees quand aucun domino n'est encore pose.
    private void UpdateEmptyPlayZonePositions()
    {
        if (boardParent == null)
            return;

        leftPlayZoneWorldPosition = boardParent.TransformPoint(new Vector3(-(tileWidth + playZoneOffset), 0f, 0f));
        rightPlayZoneWorldPosition = boardParent.TransformPoint(new Vector3(tileWidth + playZoneOffset, 0f, 0f));
    }

    // Cree un fond de table simple pour le prototype.
    private void EnsureTableSurface()
    {
        if (!showTableSurface || tableSurface != null)
            return;

        tableSurface = DominoTileVisual.CreateRuntimeRectangle(
            "Prototype Table Surface",
            transform,
            new Vector3(0f, -0.05f, 0f),
            new Vector3(tableSize.x, tableSize.y, 1f),
            tableColor,
            -20);
    }

    // Cree et configure un domino visuel.
    private int PlaceTile(int displayLeft, int displayRight, Vector2 position, float angle, int sortingOrder)
    {
        GameObject go;
        DominoTileVisual visual;

        if (dominoPrefab != null)
        {
            go = Instantiate(dominoPrefab, boardParent);
            visual = go.GetComponent<DominoTileVisual>();
        }
        else
        {
            visual = DominoTileVisual.CreateRuntimeDomino(
                boardParent,
                "Board Tile [" + displayLeft + "|" + displayRight + "]",
                new Vector2(tileWidth, tileHeight),
                sortingOrder);
            go = visual.gameObject;
        }

        go.transform.localPosition = new Vector3(position.x, position.y, 0f);
        go.transform.localRotation = Quaternion.Euler(0f, 0f, angle);

        if (visual != null)
            visual.SetValues(displayLeft, displayRight);
        else
            Debug.LogWarning("Le prefab de domino n'a pas de composant DominoTileVisual.");

        spawnedTiles.Add(go);
        Vector2 footprint = GetFootprintForAngle(angle);
        occupiedHitboxes.Add(CreateHitbox(position, footprint, displayLeft == displayRight));
        occupiedBodyHitboxes.Add(CreateBodyHitbox(position, footprint));

        return occupiedHitboxes.Count - 1;
    }
}
