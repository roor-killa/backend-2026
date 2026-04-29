// =============================================
//   Ti Punch Master — OfflineData.cs
//   Données embarquées pour le mode offline
//   Version 2.0 · Martinique 2026
// =============================================

using System.Collections.Generic;

/// <summary>
/// Recette locale pour le calcul offline du score.
/// </summary>
public class LocalRecipe
{
    public Dictionary<string, float> target;
    public float tolerance;
}

/// <summary>
/// Recettes embarquées utilisées quand le serveur FastAPI est inaccessible.
/// </summary>
public static class OfflineRecipes
{
    public static Dictionary<string, LocalRecipe> Get() => new()
    {
        ["tipunch"]       = new(){ target=new(){["rhum"]=4,["citron"]=3,["sucre"]=3},       tolerance=1f   },
        ["tipunch_hard"]  = new(){ target=new(){["rhum"]=6,["citron"]=2,["sucre"]=2},       tolerance=0.5f },
        ["mojito"]        = new(){ target=new(){["rhum"]=4,["citron"]=3,["menthe"]=2},      tolerance=1f   },
        ["mojito_hard"]   = new(){ target=new(){["rhum"]=5,["citron"]=3,["menthe"]=2},      tolerance=0.5f },
        ["planteur"]      = new(){ target=new(){["rhum"]=4,["orange"]=5,["grenadine"]=2},   tolerance=1f   },
        ["daiquiri"]      = new(){ target=new(){["rhum"]=4,["citron"]=3,["fraise"]=3},      tolerance=1f   },
        ["daiquiri_hard"] = new(){ target=new(){["rhum"]=5,["citron"]=3,["fraise"]=2},      tolerance=0.5f },
        ["sangria"]       = new(){ target=new(){["vin"]=6,["orange"]=4,["peche"]=2},        tolerance=1f   },
        ["punchcoco"]     = new(){ target=new(){["rhum"]=4,["coco"]=4,["ananas"]=3},        tolerance=1f   },
        ["gintonic"]      = new(){ target=new(){["gin"]=4,["citron"]=2,["tonic"]=6},        tolerance=1f   },
        ["spritz"]        = new(){ target=new(){["aperol"]=4,["prosecco"]=5,["soda"]=2},    tolerance=1f   },
    };
}

/// <summary>
/// Liste de clients embarquée pour le mode offline.
/// </summary>
public static class OfflineClients
{
    public static System.Collections.Generic.List<ClientData> Get() => new()
    {
        new(){ id="madeleine",  name="Madeleine",    avatar="madeleine",  difficulty="Facile",    dialogue="Un bon ti punch bien dosé, siouplé !",          cocktail="tipunch"      },
        new(){ id="jean_claude",name="Jean-Claude",  avatar="jean_claude",difficulty="Facile",    dialogue="Donne-moi un mojito rafraîchissant !",           cocktail="mojito"       },
        new(){ id="marie",      name="Marie-Hélène", avatar="marie_helene",difficulty="Moyen",    dialogue="Je voudrais un planteur bien fruité.",           cocktail="planteur"     },
        new(){ id="theo",       name="Théo",         avatar="theo",       difficulty="Moyen",     dialogue="Un daïquiri fraise s'il te plaît !",             cocktail="daiquiri"     },
        new(){ id="cecile",     name="Cécile",       avatar="cecile",     difficulty="Facile",    dialogue="Une sangria légère pour moi.",                   cocktail="sangria"      },
        new(){ id="mamie_rose", name="Mamie Rose",   avatar="mamie_rose", difficulty="Facile",    dialogue="Un punch coco comme autrefois !",                cocktail="punchcoco"    },
        new(){ id="baptiste",   name="Baptiste",     avatar="baptiste",   difficulty="Moyen",     dialogue="Gin tonic bien équilibré merci.",                cocktail="gintonic"     },
        new(){ id="sylvie",     name="Sylvie",       avatar="sylvie",     difficulty="Moyen",     dialogue="Un spritz pour l'apéro !",                       cocktail="spritz"       },
        new(){ id="marco",      name="Marco",        avatar="marco",      difficulty="Difficile", dialogue="Ti punch fort, comme un vrai martiniquais !",    cocktail="tipunch_hard" },
        new(){ id="laure",      name="Laure",        avatar="laure",      difficulty="Difficile", dialogue="Mojito parfait, chaque millilitre compte !",     cocktail="mojito_hard"  },
        new(){ id="remy",       name="Rémy",         avatar="remy",       difficulty="Difficile", dialogue="Daïquiri parfait, soyez précis !",               cocktail="daiquiri_hard"},
        new(){ id="isabelle",   name="Isabelle",     avatar="isabelle",   difficulty="Facile",    dialogue="Punch coco léger s'il vous plaît.",              cocktail="punchcoco"    },
    };
}
