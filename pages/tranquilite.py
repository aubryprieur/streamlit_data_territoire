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
  st.subheader("À l'échelle d'une commune")
  st.caption("Dernier millésime " + '2023' + " - Paru le : mars 2024")

  # Chargement des données pour la commune
  file_path_commune = "./tranquilite/donnee-comm-2023.parquet"
  df_commune = pd.read_parquet(file_path_commune)
  # Chargement des données pour la région
  file_path_region = "./tranquilite/donnee-reg-2023.csv"
  df_region = pd.read_csv(file_path_region, dtype={"Code.région": str}, sep=';', decimal=',')
  # Chargement des données pour le département
  file_path_departement = "./tranquilite/donnee-dep-2023.csv"
  df_departement = pd.read_csv(file_path_departement, sep=';', decimal=',', dtype={"Code.département": str})

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

  # Création du graphique de criminalité globale
  # Filtrage et agrégation des données pour chaque niveau
  df_commune_filtered = df_commune[(df_commune['CODGEO_2023'] == code_commune) & (df_commune['classe'].isin(categories))]
  df_region_filtered = df_region[(df_region['Code.région'] == code_region) & (df_region['classe'].isin(categories))]
  df_departement_filtered = df_departement[(df_departement['Code.département'] == code_departement) & (df_departement['classe'].isin(categories))]

  # Groupement des données par année et calcul de la somme des tauxpourmille
  commune_yearly = df_commune_filtered.groupby('annee')['tauxpourmille'].sum().reset_index()
  region_yearly = df_region_filtered.groupby('annee')['tauxpourmille'].sum().reset_index()
  departement_yearly = df_departement_filtered.groupby('annee')['tauxpourmille'].sum().reset_index()

  # Création du graphique avec Plotly
  fig = go.Figure()

  # Ajout des traces pour chaque niveau
  fig.add_trace(go.Scatter(x=commune_yearly['annee'], y=commune_yearly['tauxpourmille'],
                           mode='lines+markers', name=f"{nom_commune}"))
  fig.add_trace(go.Scatter(x=region_yearly['annee'], y=region_yearly['tauxpourmille'],
                           mode='lines+markers', name=f"{nom_region}"))
  fig.add_trace(go.Scatter(x=departement_yearly['annee'], y=departement_yearly['tauxpourmille'],
                           mode='lines+markers', name=f"{nom_departement}"))

  # Configuration du layout
  fig.update_layout(
      title='Évolution Totale de la Criminalité par Année par Niveau Administratif',
      xaxis_title="Année",
      yaxis_title="Taux pour mille total",
      legend_title="Niveau Administratif",
      template="plotly_white"
  )

  # Affichage du graphique dans Streamlit
  st.plotly_chart(fig)

  #########################################################################
  # Création du graphique par catégorie
  fig = go.Figure()

  # Filtrage des données pour chaque catégorie et ajout dans le graphique
  for category in categories:
      df_category = df_commune[(df_commune['CODGEO_2023'] == code_commune) & (df_commune['classe'] == category)]
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
  st.subheader("Comparaison entre la commune, le département et la région")
  # Configuration des graphiques
  num_columns = 3
  num_rows = (len(categories) + num_columns - 1) // num_columns

  for i in range(num_rows):
      cols = st.columns(num_columns)
      for j in range(num_columns):
          index = i * num_columns + j
          if index < len(categories):
              category = categories[index]
              df_category_commune = df_commune[(df_commune['CODGEO_2023'] == code_commune) & (df_commune['classe'] == category)]
              df_category_region = df_region[(df_region["Code.région"] == code_region) & (df_region['classe'] == category)]
              df_category_departement = df_departement[(df_departement["Code.département"] == code_departement) & (df_departement['classe'] == category)]

              fig = go.Figure()

              # Ajout de la trace pour la commune
              if not df_category_commune.empty:
                  fig.add_trace(go.Scatter(
                      x=df_category_commune['annee'], y=df_category_commune['tauxpourmille'],
                      mode='lines+markers', name=f"{nom_commune}"
                  ))

              # Ajout de la trace pour la région
              if not df_category_region.empty:
                  fig.add_trace(go.Scatter(
                      x=df_category_region['annee'], y=df_category_region['tauxpourmille'],
                      mode='lines+markers', name=f"{nom_region}"
                  ))
              # Ajout de la trace pour le département
              if not df_category_departement.empty:
                  fig.add_trace(go.Scatter(
                      x=df_category_departement['annee'], y=df_category_departement['tauxpourmille'],
                      mode='lines+markers', name=f"{nom_departement}"
                  ))

              fig.update_layout(
                  title=f"{category}",
                  xaxis_title="Année",
                  yaxis_title="Taux pour mille",
                  legend_title="Catégorie",
                  template="plotly_white",
                  title_font=dict(size=12),
                  legend=dict(
                  orientation="h",
                  xanchor="center",
                  x=0.5,
                  y=-0.3
                )
              )

              with cols[j]:
                  st.plotly_chart(fig, use_container_width=True)

  # Calcul des quartiles et de la médiane
  # Filtrage des données pour "Coups et blessures volontaires"
  df_cbv_commune = df_commune[(df_commune['classe'] == "Coups et blessures volontaires") & (df_commune['annee'] == 23)]
  # Exclusion des valeurs zéro
  df_cbv_commune_non_zero = df_cbv_commune[df_cbv_commune['tauxpourmille'] != 0]
  q1 = df_cbv_commune_non_zero['tauxpourmille'].quantile(0.25)
  median = df_cbv_commune_non_zero['tauxpourmille'].median()
  q3 = df_cbv_commune_non_zero['tauxpourmille'].quantile(0.75)
  # Affichage des valeurs calculées
  st.write("### Statistiques pour 'Coups et blessures volontaires' au niveau communal")
  st.write(f"1er quartile: {q1:.2f}")
  st.write(f"Médiane: {median:.2f}")
  st.write(f"3ème quartile: {q3:.2f}")
