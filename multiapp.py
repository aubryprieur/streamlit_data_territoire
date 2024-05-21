# multiapp.py
import streamlit as st
from pages.utils import afficher_infos_commune  # Importation de la fonction

class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run(self):
        st.set_page_config(layout="wide")

        # Utiliser afficher_infos_commune pour centraliser la sélection de la commune
        st.sidebar.title("Sélection de la commune")
        code_commune, nom_commune, code_epci, nom_epci, code_departement, nom_departement, code_region, nom_region = afficher_infos_commune()

        # Ajouter un menu de navigation dans la sidebar
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox(
            'Sélectionnez votre thématique :',
            self.apps,
            format_func=lambda app: app['title']
        )

        # Afficher le contenu de la page sélectionnée
        page['function'](code_commune, nom_commune, code_epci, nom_epci, code_departement, nom_departement, code_region, nom_region)

