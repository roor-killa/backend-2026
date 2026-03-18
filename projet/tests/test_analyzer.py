import json
import pandas as pd
from pathlib import Path
from src.analyzer import DataAnalyzer


def test_load_from_json(tmp_path):
    data = [
        {"name": "Produit A", "price": 10},
        {"name": "Produit B", "price": 20}
    ]

    file_path = tmp_path / "data.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    analyzer = DataAnalyzer()
    analyzer.load_from_json(str(file_path))

    assert analyzer.df is not None
    assert len(analyzer.df) == 2


def test_load_from_json_file_not_found():
    analyzer = DataAnalyzer()

    try:
        analyzer.load_from_json("fichier_inexistant.json")
    except FileNotFoundError:
        assert True


def test_descriptive_stats_with_data(tmp_path):
    data = [
        {"name": "Produit A", "price": 10},
        {"name": "Produit B", "price": 20}
    ]

    file_path = tmp_path / "data.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    analyzer = DataAnalyzer()
    analyzer.load_from_json(str(file_path))

    stats = analyzer.descriptive_stats()

    assert stats["total"] == 2
    assert "name" in stats["colonnes"]


def test_descriptive_stats_empty():
    analyzer = DataAnalyzer()
    result = analyzer.descriptive_stats()

    assert "erreur" in result


def test_export_to_csv(tmp_path, monkeypatch):
    analyzer = DataAnalyzer()
    analyzer.df = pd.DataFrame([
        {"name": "Produit A", "price": 10}
    ])

    monkeypatch.setattr("src.analyzer.Path", lambda x="": tmp_path)

    analyzer.export_to_csv("test.csv")

    file_path = tmp_path / "test.csv"
    assert file_path.exists()


def test_export_to_excel(tmp_path, monkeypatch):
    analyzer = DataAnalyzer()
    analyzer.df = pd.DataFrame([
        {"name": "Produit A", "price": 10}
    ])

    monkeypatch.setattr("src.analyzer.Path", lambda x="": tmp_path)

    analyzer.export_to_excel("test.xlsx")

    file_path = tmp_path / "test.xlsx"
    assert file_path.exists()


def test_get_summary_report(tmp_path):
    data = [
        {"name": "Produit A", "price": 10},
    ]

    file_path = tmp_path / "data.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    analyzer = DataAnalyzer()
    analyzer.load_from_json(str(file_path))

    report = analyzer.get_summary_report()

    assert "RAPPORT DONNÉES KIPRIX" in report
