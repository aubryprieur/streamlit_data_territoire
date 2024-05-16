import streamlit as st
from pages.utils import afficher_infos_commune
import pandas as pd
import numpy as np
import altair as alt
import geopandas as gpd
import requests
import json # library to handle JSON files
# from streamlit_folium import folium_static
from streamlit_folium import folium_static
import folium # map rendering library
import streamlit.components.v1 as components
import fiona
import matplotlib.pyplot as plt

def app(code_commune, nom_commune, code_epci, nom_epci, code_departement, nom_departement, code_region, nom_region):
  #afficher_infos_commune()

  #############################################################################
  st.title("🌎 Analyse de mon territoire")
  st.write("De l'iris en passant par la commune, l'epci, le département, la région et la France. COPAS vous propose de visualiser et comparer les principaux indicateurs pour analyser rapidement et facilement votre territoire.")
  st.write("Grace à notre outil, fini le temps fastidieux de récolte des données, de création des indicateurs, de la conception des graphiques et de la réalisation de cartes statistiques. Vous vous concentrez totalement sur l'analyse de votre territoire.")
  st.write("COPAS vous aide également dans l'analyse en vous fournissant les définitions des indicateurs sélectionnés, l'utilité des indicateurs et leur interprétation.")
  st.write("A ce jour, l'app compte plus de 60 indicateurs.")
  st.write("Comment procéder ?")
  st.write("1. Sélectionnez votre commune")
  st.write("2. Sélectionnez votre année de référence")
  st.write("3. Naviguez parmi les nombreuses thématiques disponibles")

  #############################################################################

