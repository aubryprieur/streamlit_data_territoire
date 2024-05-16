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
  st.title("🚨 Tranquilité")
  ############
  st.header('1.Test')
  #df_pop_iris = pd.read_csv("./tranquilite/delinquance_2024.csv", sep=";")


  ############################################################################


