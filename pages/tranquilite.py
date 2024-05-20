import streamlit as st
from pages.utils import afficher_infos_commune
from pages.utils import remove_comma, round_to_two, round_to_zero
import pandas as pd
import numpy as np
import altair as alt
from pandas.io.json import json_normalize
import geopandas as gpd
import requests
import json # library to handle JSON files
# from streamlit_folium import folium_static
from streamlit_folium import folium_static
import folium # map rendering library
import streamlit_folium as folium_st
from shapely.geometry import Polygon, MultiPolygon
import streamlit.components.v1 as components
import fiona
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import plotly.graph_objs as go
import jenkspy

def app(code_commune, nom_commune, code_epci, nom_epci, code_departement, nom_departement, code_region, nom_region):
  # Appeler la fonction et récupérer les informations

  #############################################################################

  # Titre de l'application
  st.title("🚨 Tranquilité")
  st.header('1. Principaux indicateurs des crimes et délits enregistrés par la police et la gendarmerie nationales')
  st.caption("Dernier millésime " + '2023' + " - Paru le : mars 2024")

  # Chargement du fichier Parquet
  file_path = "./tranquilite/donnee-comm-2023.parquet"
  df = pd.read_parquet(file_path)

  # Liste des catégories à visualiser
  categories = [
      "Coups et blessures volontaires",
      "Coups et blessures volontaires intrafamiliaux",
      "Autres coups et blessures volontaires",
      "Violences sexuelles",
      "Vols avec armes",
      "Vols violents sans arme",
      "Vols sans violence contre des personnes",
      "Cambriolages de logement",
      "Vols de véhicules",
      "Vols dans les véhicules",
      "Vols d'accessoires sur véhicules",
      "Destructions et dégradations volontaires",
      "Trafic de stupéfiants",
      "Usage de stupéfiants"
  ]

  # Création du graphique
  fig = go.Figure()

  # Filtrage des données pour chaque catégorie et ajout dans le graphique
  for category in categories:
      df_category = df[(df['CODGEO_2023'] == code_commune) & (df['classe'] == category)]
      if not df_category.empty:
          fig.add_trace(go.Scatter(x=df_category['annee'], y=df_category['tauxpourmille'], mode='lines+markers', name=category))

  fig.update_layout(
      title="Évolution des Incidents par Catégorie et par Année",
      xaxis_title="Année",
      yaxis_title="Taux pour mille",
      legend_title="Catégorie",
      template="plotly_white"
  )

  # Affichage du graphique dans Streamlit
  st.plotly_chart(fig)





  ############################################################################


