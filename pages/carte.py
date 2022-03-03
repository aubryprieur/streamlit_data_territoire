import streamlit as st
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

def app():
  #Commune
  df_commune = pd.read_csv("./commune_2021.csv", sep=",")
  list_commune = df_commune.loc[:, 'LIBELLE']
  nom_commune = st.sidebar.selectbox(
       "Sélectionnez votre commune :",
       options=list_commune)
  code_commune = df_commune.loc[df_commune['LIBELLE'] == nom_commune, 'COM'].iloc[0]
  st.sidebar.write('Ma commune:', code_commune, nom_commune)

  #EPCI
  df_epci = pd.read_csv("./EPCI_2020.csv", sep=";")
  nom_epci = df_epci.loc[df_epci['CODGEO'] == code_commune, 'LIBEPCI'].iloc[0]
  code_epci = df_epci.loc[df_epci['CODGEO'] == code_commune, 'EPCI'].iloc[0]
  st.sidebar.write('Mon EPCI:', code_epci, nom_epci)


  #Département
  code_departement = df_commune.loc[df_commune['LIBELLE'] == nom_commune, 'DEP'].iloc[0]
  df_departement = pd.read_csv("./departement2021.csv", dtype={"CHEFLIEU": str}, sep=",")
  nom_departement = df_departement.loc[df_departement['DEP'] == code_departement, 'LIBELLE'].iloc[0]
  st.sidebar.write('Mon département:', code_departement, nom_departement)

  #Région
  code_region = df_commune.loc[df_commune['LIBELLE'] == nom_commune, 'REG'].iloc[0]
  df_region = pd.read_csv("./region2021.csv", dtype={"CHEFLIEU": str}, sep=",")
  nom_region = df_region.loc[df_region['REG'] == code_region, 'LIBELLE'].iloc[0]
  st.sidebar.write('Ma région:', str(round(code_region)), nom_region)

  #Année
  select_annee = st.sidebar.select_slider(
       "Sélection de l'année",
       options=['2014', '2015', '2016', '2017', '2018'],
       value=('2018'))
  st.sidebar.write('Mon année :', select_annee)

  #############################################################################

  st.title("Test carte")
  def niveau_vie_median_iris(fichier, nom_ville, annee) :
      df = pd.read_csv(fichier, dtype={"IRIS": str , "COM": str},sep=";")
      year = annee[-2:]
      df_ville = df.loc[df["LIBCOM"]==nom_ville]
      df_ville = df_ville.replace(',','.', regex=True)
      df_ville = df_ville[['IRIS','LIBIRIS','DISP_MED'+ year]]
      if year == "14":
        df_ville['DISP_MED' + year] = df_ville['DISP_MED' + year].str.replace(',','.').astype(float)
      df_ville['DISP_MED' + year] = df_ville['DISP_MED' + year].astype(int)
      df_ville.reset_index(inplace=True, drop=True)
      return df_ville
  nvm_iris = niveau_vie_median_iris("./revenu/revenu_iris/BASE_TD_FILO_DISP_IRIS_" + select_annee + ".csv","Lille", select_annee)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(nvm_iris)
  #######
  # request

  import requests
  from pandas.io.json import json_normalize
  from geopandas import GeoDataFrame
  from shapely.geometry import Polygon

  url = "https://public.opendatasoft.com/api/records/1.0/search/?dataset=georef-france-iris-millesime&q=Lille&sort=year&facet=year&facet=reg_name&facet=dep_name&facet=arrdep_name&facet=ze2020_name&facet=bv2012_name&facet=epci_name&facet=ept_name&facet=com_name&facet=com_arm_name&facet=iris_name&facet=iris_area_code&facet=iris_type&refine.year=2020&refine.com_name=Lille"
  reponse = requests.get(url)
  st.write(reponse)

  contenu = reponse.json()
  f = contenu

  df = pd.json_normalize(contenu)
  map_df = df['records'][0]
  st.write(map_df)

  select_map = pd.json_normalize(map_df)
  st.write(select_map)
  # fig, ax = plt.subplots(1, figsize=(20, 12))
  # select_map.plot()
  # st.pyplot(fig)
  #Merge with nvm_iris
  map_all = select_map.merge(nvm_iris, left_on='fields.iris_code', right_on='IRIS')
  map_all = GeoDataFrame(map_all)
  st.write(map_all)
  #map
  # variable = 'DISP_MED18'
  # fig, ax = plt.subplots(1, figsize=(20, 12))
  # map_all.plot(column=variable,linewidth=1.5, ax=ax, edgecolor='white', alpha=0.9, cmap='RdYlGn',legend=True)
  # st.pyplot(fig)

  ######################
  m = folium.Map(
      location=[-59.1759, -11.6016],
      tiles="cartodbpositron",
      zoom_start=2,
  )

  m



