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

def app(code_commune, nom_commune, code_epci, nom_epci, code_departement, nom_departement, code_region, nom_region):
  # Appeler la fonction et récupérer les informations

  #############################################################################
  st.title('ALLOCATAIRES CAF')
  last_year = "2020"
  df = pd.read_csv("./caf/iris/data_CAF_" + last_year + "_IRIS.csv", dtype={"CODGEO": str, "DEPCOM": str,"EPCI": str, "REG": str}, sep=";")
  df = df.loc[df['CODGEO'].str.startswith(code_commune)]
  df = df[['CODGEO', 'AI', 'AM', 'ACSSENF', 'ACAVENF']]
  df = df.rename(columns={'CODGEO': "Code de l'iris",'AI': "Allocataires isolés sans enfant", 'AM':"Allocataires mono-parent" ,'ACSSENF':"Allocataires couples sans enfant",'ACAVENF':"Allocataires couples avec enfant(s)" })
  st.write(df)
