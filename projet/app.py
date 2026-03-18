import streamlit as st
import pandas as pd
import json
from pathlib import Path
import os
import time

# Configuration de la page
st.set_page_config(
    page_title="Kiprix - Comparateur DOM/Métropole",
    page_icon="🛒",
    layout="wide"
)

# Importer nos propres modules
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.manager import ScraperManager
from src.analyzer import DataAnalyzer

st.title("Analyseur de Prix : Kiprix (France vs DOM)")
st.markdown("Interface graphique pour le scraper Kiprix - **Projet POO Groupe 2**")

st.sidebar.header("Navigation")
menu = st.sidebar.radio("Aller à :", ["Analyse des données existantes", "Lancer un nouveau Scraping"])

TERRITORIES = {
    'gp': 'Guadeloupe',
    'mq': 'Martinique',
    're': 'La Réunion',
    'gf': 'Guyane',
}

def load_all_data():
    """Charge toutes les données existantes depuis PostgreSQL."""
    from src.db_manager import DBManager
    import pandas as pd
    
    try:
        db = DBManager()
        with db.get_connection() as conn:
            query = "SELECT * FROM produits;"
            df = pd.read_sql_query(query, conn)
            # Remplacer les valeurs potentiellement manquantes ou de type None
            return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données depuis PostgreSQL : {e}")
        return pd.DataFrame()



if menu == "Analyse des données existantes":
    st.header("Analyse des prix scrapés")
    
    df = load_all_data()
    
    if df.empty:
        st.warning("Aucune donnée trouvée. Allez dans l'onglet Scraping pour récupérer des données.")
    else:
        # Métriques globales
        analyzer = DataAnalyzer()
        analyzer.df = df
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Produits Totaux", len(df))
        
        territoires_presents = df['territory_name'].nunique() if 'territory_name' in df.columns else 0
        col2.metric("Territoires couverts", territoires_presents)
        
        # Nettoyage rapide pour statistiques
        def clean_price(val):
            if pd.isna(val): return None
            v = str(val).replace('€', '').replace('\u00a0', '').replace(' ', '').replace(',', '.')
            try: return float(v)
            except: return None
            
        df['price_france_num'] = df['price_france'].apply(clean_price)
        df['price_dom_num'] = df['price_dom'].apply(clean_price)
        
        if not df['price_dom_num'].dropna().empty:
            prix_moyen_dom = df['price_dom_num'].mean()
            col3.metric("Prix moyen (DOM)", f"{prix_moyen_dom:.2f} €")

        st.markdown("---")
        
        # Filtres
        st.subheader("Filtres")
        territoires = ["Tous"] + list(df['territory_name'].dropna().unique())
        choix_territoire = st.selectbox("Filtrer par territoire :", territoires)
        
        df_display = df.copy()
        if choix_territoire != "Tous":
            df_display = df_display[df_display['territory_name'] == choix_territoire]
            
        # Affichage du tableau de données
        display_cols = ['name', 'territory_name', 'price_france', 'price_dom', 'difference']
        if 'category' in df_display.columns:
            display_cols.append('category')

        st.dataframe(
            df_display[display_cols],
            use_container_width=True
        )
        
        st.markdown("---")
        st.subheader("Top 5 des plus grands écarts de prix")
        
        # Calcul des tendances via l'analyzer existant (patch pour qu'il marche direct avec le DF courant)
        trends = analyzer.detect_price_trends()
        if 'erreur' not in trends:
            st.info(f"**Écart Moyen Global : {trends.get('moyenne', 'N/A')}%** (Médiane : {trends.get('mediane', 'N/A')}%)")
        
        # Bar chart
        import re
        def parse_diff(value):
            match = re.search(r'([+-]?\s*\d+[\d\s.,]*)\s*%', str(value))
            if not match: return None
            cleaned = match.group(1).replace(' ', '').replace('\u00a0', '').replace(',', '.')
            try: return float(cleaned)
            except: return None
            
        df_display['difference_numeric'] = df_display['difference'].apply(parse_diff)
        
        if not df_display.empty and 'difference_numeric' in df_display.columns:
            top_ecarts = df_display.nlargest(10, 'difference_numeric')
            st.bar_chart(data=top_ecarts, x='name', y='difference_numeric', color='#ff4b4b')


elif menu == "Lancer un nouveau Scraping":
    st.header("Lancer le Scraper Kiprix")
    
    st.info("💡 L'exécution se fera via le navigateur invisible (Selenium). Cela peut prendre quelques dizaines de secondes à cause des protections Cloudflare.")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_territory = st.selectbox("Choisir le territoire", 
                                          options=list(TERRITORIES.keys()), 
                                          format_func=lambda x: TERRITORIES[x])
    with col2:
        pages_to_scrape = st.number_input("Nombre de pages à scraper", min_value=1, max_value=20, value=1)
        
    if st.button("Démarrer le Scraping", type="primary"):
        with st.spinner(f"Scraping de {pages_to_scrape} page(s) pour la {TERRITORIES[selected_territory]}... Veuillez patienter."):
            
            manager = ScraperManager()
            try:
                scraper = manager.create_scraper('kiprix', territory=selected_territory)
                data = scraper.scrape(max_pages=pages_to_scrape)
                
                if data:
                    from src.db_manager import DBManager
                    db = DBManager()
                    db.init_db()  # S'assurer que la table existe
                    db.save_products(data)
                    st.success(f"✅ Scraping terminé avec succès ! {len(data)} produits enregistrés en base de données.")
                    st.balloons()
                else:
                    st.warning("⚠️ Cloudflare a bloqué la requête ou aucune donnée trouvée.")
                    
            except Exception as e:
                st.error(f"Une erreur s'est produite lors du scraping : {e}")
