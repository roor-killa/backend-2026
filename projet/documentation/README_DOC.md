# Documentation du projet — Guide complet

## 📋 Contenu du dossier `documentation/`

Ce dossier contient toute la documentation académique du projet TP Scraping Kiprix.com.

---

## 📄 Fichiers présents

### 1. **rapport.md**

Rapport académique complet en Markdown contenant :

- **Page de garde** : titre, institution, membres, date
- **Table des matières** : navigation structured
- **8 sections numérotées** :
  1. Introduction et objectifs
  2. Architecture générale et principes SOLID
  3. Description détaillée des 5 classes principales
  4. Diagramme UML (référence)
  5. Tests et couverture (39 tests, 72% couverture)
  6. Docker et déploiement
  7. Répartition des rôles entre membres
  8. Difficultés rencontrées et solutions
  9. Conclusion et améliorations futures

**Usage** :
```bash
# Voir en Markdown (VS Code, GitHub, etc.)
cat rapport.md

# Convertir en PDF dengan Pandoc
pandoc rapport.md -o rapport.pdf --from markdown --to pdf \
  --variable "geometry:margin=1in" \
  --variable "fontsize=11pt"

# Ou avec Markdown PDF (VS Code extension)
# Extension: markdown-pdf
```

---

### 2. **style.css**

Feuille de style CSS professionnelle pour mise en page académique.

**Caractéristiques** :
- Palette couleur : bleu foncé universitaire (#001a4d)
- Police Times New Roman (académique)
- Texte justifié
- Titres avec bordures et couleurs distinctes
- Tableaux stylisés avec alternance de couleurs
- Code highlighting avec fond gris clair
- Responsive design (mobile-friendly)
- Print styles optimisés pour PDF

**Usage** :
```bash
# Convertir markdown + CSS en HTML puis PDF
pandoc rapport.md -o rapport.html --css=style.css
# Puis ouvrir rapport.html dans un navigateur et imprimer en PDF
```

---

### 3. **uml.puml**

Diagramme UML complet en syntaxe PlantUML.

**Contenu** :
- Classe abstraite `BaseScraper`
- Classe concrète `KiprixScraper` (hérite de BaseScraper)
- Factory `ScraperManager`
- Composant `CacheManager`
- Analyseur `DataAnalyzer`
- Relations d'héritage et dépendances

**Usage** :
```bash
# Approche 1 : Extension VS Code PlantUML
# - Installer l'extension "PlantUML" (jebbs.plantuml)
# - Ouvrir uml.puml
# - Utiliser le raccourci Alt+D pour voir l'aperçu

# Approche 2 : En ligne
# Copier le contenu de uml.puml
# Aller sur https://www.plantuml.com/plantuml/uml/
# Coller et cliquer "Submit"

# Approche 3 : CLI PlantUML (si installé)
java -jar plantuml.jar uml.puml -o . -tpng
# Génère uml.png dans le même dossier
```

---

### 4. **README_DOC.md** (ce fichier)

Guide d'utilisation de la documentation.

---

## 🎓 Comment utiliser cette documentation

### Pour présentation universitaire

1. **Lire le rapport** :
   ```bash
   cat rapport.md  # ou ouvrir dans VS Code
   ```

2. **Visualiser le diagramme UML** :
   - Utiliser l'extension PlantUML de VS Code, ou
   - Générer une image PNG/SVG

3. **Générer un PDF** (recommandé pour rendu) :
   ```bash
   # Option 1 : avec Pandoc (meilleur rendu)
   pandoc rapport.md -o rapport.pdf \
     --variable "geometry:margin=1in" \
     --variable "fontsize=12pt" \
     --highlight-style=tango
   
   # Option 2 : avec Markdown PDF (VS Code)
   # Clic droit sur rapport.md → "Markdown PDF: Export"
   ```

4. **Intégrer le diagramme UML** :
   - Générer l'image UML (PNG ou SVG)
   - Insérer dans le rapport PDF (optionnel)

---

## 📊 Structure du rapport

```
rapport.md
├── Introduction
│   ├── Contexte
│   ├── Objectifs
│   └── Membres
├── Architecture Générale
│   ├── Vision d'ensemble
│   ├── Structure des dossiers
│   └── Principes de conception
├── Classes Principales
│   ├── BaseScraper
│   ├── KiprixScraper
│   ├── ScraperManager
│   ├── CacheManager
│   └── DataAnalyzer
├── Diagramme UML
├── Tests et Couverture
│   ├── Résultats actuels (39 tests, 72%)
│   ├── Suites de tests
│   └── Techniques employées
├── Docker et Déploiement
├── Répartition des Rôles
│   ├── MEMBRE 1 (architecture)
│   ├── MEMBRE 2 (analyse)
│   └── MEMBRE 3 (qualité/DevOps)
├── Difficultés Rencontrées
├── Conclusion
└── Références
```

---

## ✨ Caractéristiques du rapport

### Avant du rapport

- ✅ Page de garde professionnelle
- ✅ Table des matières automatique (clickable en PDF)
- ✅ Numérotation des sections (1., 2., etc.)
- ✅ Couleurs institutionnelles (bleu foncé universitaire)
- ✅ Typographie académique (Times New Roman)
- ✅ Texte justifié

### Contenu

- ✅ Description complète de l'architecture POO
- ✅ Explication détaillée de chaque classe
- ✅ Diagramme UML (référence + visualisation)
- ✅ Résultats de tests et coverage
- ✅ Instructions Docker
- ✅ Répartition claire des rôles
- ✅ Difficultés et solutions

### Tonalité

- ✅ Langage académique professionnel
- ✅ Références aux concepts POO (abstraction, héritage, polymorphisme)
- ✅ Vocabulaire technique approprié
- ✅ Structures logiques claires

---

## 🛠 Outils recommandés

### Pour lire/éditer

- **VS Code** avec extensions :
  - PlantUML
  - Markdown Preview Enhanced
  - Markdown PDF

- **Navigateur** :
  - https://www.plantuml.com/plantuml/uml/ (visualiser UML)
  - Markdown viewers (pages GitHub, etc.)

### Pour convertir en PDF

- **Pandoc** (meilleur qualité) :
  ```bash
  sudo apt install pandoc  # Linux
  brew install pandoc      # macOS
  # Windows : télécharger depuis pandoc.org
  ```

- **VS Code** (plus simple) :
  - Extension "Markdown PDF" par yzane
  - Clic droit sur fichier → "Markdown PDF: Export"

---

## 📋 Checklist avant rendu

- [ ] Rapport lu et vérifié pour fautes
- [ ] Diagramme UML généré et visible
- [ ] PDF généré avec mise en page correcte
- [ ] Table des matières fonctionnelle
- [ ] Tous les noms des membres présents
- [ ] Date de rendu correcte (28 février 2026)
- [ ] Logos/images (si applicable) intégrés
- [ ] Hyperliens valides

---

## 📞 Questions fréquentes

**Q1 : Comment voir le diagramme UML sans extension ?**  
→ Utiliser https://www.plantuml.com/plantuml/uml/ ou générer une image PNG/SVG.

**Q2 : Le PDF n'a pas la bonne mise en page.**  
→ Utiliser `pandoc` au lieu de "Markdown PDF" extension pour meilleur résultat.

**Q3 : Comment inclure le diagramme UML dans le PDF final ?**  
→ Générer d'abord l'image PNG depuis PlantUML, puis ajouter dans le rapport :  
```markdown
![Diagramme UML](./uml.png)
```

**Q4 : Puis-je modifier le rapport ?**  
→ Oui ! Le fichier `rapport.md` est éditable. Juste respecter la structure académique.

**Q5 : Comment imprimer le rapport en couleur ?**  
→ Exporter en PDF depuis un navigateur moderne (Chrome, Firefox) avec "Imprimer en tant que PDF".

---

## 📅 Dates clés

- **Rendu final** : 28 février 2026
- **Format** : PDF + sources Markdown
- **Destinataire** : Enseignant POO — L2 Informatique, Université des Antilles

---

**Documentation générée** : Février 2026  
**Auteurs** : SADI, GUINDO, AKONOU  
**Module** : Programmation Orientée Objet

