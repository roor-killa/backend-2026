// =============================================
//   Ti Punch Master — CocktailDatabase.cs
//   Base de données embarquée des 8 cocktails
//   Version 2.0 · Martinique 2026
// =============================================

using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class IngredientData
{
    public string key;     // clé API : "rhum", "citron", etc.
    public string name;    // nom affiché : "Rhum agricole"
    public Color  color;
    public float  defaultCl;
}

[Serializable]
public class CocktailData
{
    public string              id;
    public string              name;
    public string              emoji;
    public float               tolerance;
    public List<IngredientData> ingredients;

    public float GetMaxTotal()
    {
        float t = 0f;
        foreach (var i in ingredients) t += i.defaultCl;
        return t * 1.5f;
    }
}

public static class CocktailDatabase
{
    private static readonly Dictionary<string, CocktailData> _db = new()
    {
        ["tipunch"] = new CocktailData
        {
            id="tipunch", name="Ti Punch", emoji="🥃", tolerance=1f,
            ingredients = new()
            {
                new(){key="rhum",   name="Rhum agricole", color=new Color(0.83f,0.63f,0.19f), defaultCl=4},
                new(){key="citron", name="Citron vert",   color=new Color(0.53f,0.80f,0.13f), defaultCl=3},
                new(){key="sucre",  name="Sucre canne",   color=new Color(1.00f,0.91f,0.63f), defaultCl=3},
            }
        },
        ["tipunch_hard"] = new CocktailData
        {
            id="tipunch_hard", name="Ti Punch Fort", emoji="🥃", tolerance=0.5f,
            ingredients = new()
            {
                new(){key="rhum",   name="Rhum agricole", color=new Color(0.83f,0.63f,0.19f), defaultCl=6},
                new(){key="citron", name="Citron vert",   color=new Color(0.53f,0.80f,0.13f), defaultCl=2},
                new(){key="sucre",  name="Sucre canne",   color=new Color(1.00f,0.91f,0.63f), defaultCl=2},
            }
        },
        ["mojito"] = new CocktailData
        {
            id="mojito", name="Mojito", emoji="🍃", tolerance=1f,
            ingredients = new()
            {
                new(){key="rhum",   name="Rhum blanc",    color=new Color(0.94f,0.88f,0.63f), defaultCl=4},
                new(){key="citron", name="Citron vert",   color=new Color(0.53f,0.80f,0.13f), defaultCl=3},
                new(){key="menthe", name="Sirop menthe",  color=new Color(0.13f,0.73f,0.40f), defaultCl=2},
            }
        },
        ["mojito_hard"] = new CocktailData
        {
            id="mojito_hard", name="Mojito Précis", emoji="🍃", tolerance=0.5f,
            ingredients = new()
            {
                new(){key="rhum",   name="Rhum blanc",    color=new Color(0.94f,0.88f,0.63f), defaultCl=5},
                new(){key="citron", name="Citron vert",   color=new Color(0.53f,0.80f,0.13f), defaultCl=3},
                new(){key="menthe", name="Sirop menthe",  color=new Color(0.13f,0.73f,0.40f), defaultCl=2},
            }
        },
        ["planteur"] = new CocktailData
        {
            id="planteur", name="Planteur", emoji="🍊", tolerance=1f,
            ingredients = new()
            {
                new(){key="rhum",      name="Rhum vieux",    color=new Color(0.75f,0.44f,0.13f), defaultCl=4},
                new(){key="orange",    name="Jus orange",    color=new Color(1.00f,0.53f,0.13f), defaultCl=5},
                new(){key="grenadine", name="Grenadine",     color=new Color(0.80f,0.07f,0.27f), defaultCl=2},
            }
        },
        ["daiquiri"] = new CocktailData
        {
            id="daiquiri", name="Daïquiri Fraise", emoji="🍓", tolerance=1f,
            ingredients = new()
            {
                new(){key="rhum",   name="Rhum blanc",    color=new Color(0.94f,0.88f,0.63f), defaultCl=4},
                new(){key="citron", name="Citron vert",   color=new Color(0.53f,0.80f,0.13f), defaultCl=3},
                new(){key="fraise", name="Sirop fraise",  color=new Color(0.93f,0.20f,0.40f), defaultCl=3},
            }
        },
        ["daiquiri_hard"] = new CocktailData
        {
            id="daiquiri_hard", name="Daïquiri Parfait", emoji="🍓", tolerance=0.5f,
            ingredients = new()
            {
                new(){key="rhum",   name="Rhum blanc",    color=new Color(0.94f,0.88f,0.63f), defaultCl=5},
                new(){key="citron", name="Citron vert",   color=new Color(0.53f,0.80f,0.13f), defaultCl=3},
                new(){key="fraise", name="Sirop fraise",  color=new Color(0.93f,0.20f,0.40f), defaultCl=2},
            }
        },
        ["sangria"] = new CocktailData
        {
            id="sangria", name="Sangria", emoji="🍷", tolerance=1f,
            ingredients = new()
            {
                new(){key="vin",    name="Vin rouge",     color=new Color(0.53f,0.07f,0.20f), defaultCl=6},
                new(){key="orange", name="Jus orange",    color=new Color(1.00f,0.53f,0.13f), defaultCl=4},
                new(){key="peche",  name="Sirop pêche",   color=new Color(1.00f,0.67f,0.40f), defaultCl=2},
            }
        },
        ["punchcoco"] = new CocktailData
        {
            id="punchcoco", name="Punch Coco", emoji="🥥", tolerance=1f,
            ingredients = new()
            {
                new(){key="rhum",   name="Rhum agricole", color=new Color(0.83f,0.63f,0.19f), defaultCl=4},
                new(){key="coco",   name="Lait de coco",  color=new Color(0.94f,0.93f,0.85f), defaultCl=4},
                new(){key="ananas", name="Jus ananas",    color=new Color(1.00f,0.88f,0.25f), defaultCl=3},
            }
        },
        ["gintonic"] = new CocktailData
        {
            id="gintonic", name="Gin Tonic", emoji="🍸", tolerance=1f,
            ingredients = new()
            {
                new(){key="gin",    name="Gin",           color=new Color(0.78f,0.91f,1.00f), defaultCl=4},
                new(){key="citron", name="Citron vert",   color=new Color(0.53f,0.80f,0.13f), defaultCl=2},
                new(){key="tonic",  name="Tonic",         color=new Color(0.85f,0.95f,1.00f), defaultCl=6},
            }
        },
        ["spritz"] = new CocktailData
        {
            id="spritz", name="Spritz", emoji="🍊", tolerance=1f,
            ingredients = new()
            {
                new(){key="aperol",   name="Aperol",     color=new Color(1.00f,0.40f,0.13f), defaultCl=4},
                new(){key="prosecco", name="Prosecco",   color=new Color(0.94f,0.91f,0.63f), defaultCl=5},
                new(){key="soda",     name="Soda",       color=new Color(0.82f,0.95f,1.00f), defaultCl=2},
            }
        },
    };

    public static CocktailData Get(string id) =>
        _db.TryGetValue(id, out var c) ? c : null;

    public static IEnumerable<CocktailData> All => _db.Values;
}
