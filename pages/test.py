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
  st.title("Analyse de mon territoire")
  st.write("De l'iris en passant par la commune, l'epci, le département, la région et la France. COPAS vous propose de visualiser et comparer XXX indicateurs pour analyser rapidement et facilement votre territoire.")
  st.write("Grace à notre outil, fini le temps fastidieux de récolte des données et de la création des indicateurs, la conception des graphiques et des cartes statistiques. Vous vous concentrez totalement sur l'analyse de votre territoire.")
  st.write("COPAS vous aide également dans l'analyse en vous fournissant les définitions des indicateurs sélectionnés, l'utilité des indicateurs et leur interprétation.")
  st.write("A ce jour, l'app compte 12 indicateurs.")
  st.write("Comment procéder ?")
  st.write("1. Sélectionnez votre commune")
  st.write("2. Sélectionnez votre année de référence")
  st.write("3. Naviguez parmi les nombreuses thématiques disponibles")

  #############################################################################
############################
  st.subheader('Comparaison entre territoires sur une année')
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    #France
    def niveau_vie_median_france(fichier, annee) :
        df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
        df = df.replace(',','.', regex=True)
        year = annee[-2:]
        nvm = df[[ 'LIBGEO' ,'Q2'+ year]]
        if year == int(2014):
          nvm = nvm['2014'].astype(float)
        return nvm
    #Région
    def niveau_vie_median_region(fichier, nom_region, annee) :
        df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
        year = annee[-2:]
        df_region = df.loc[df["LIBGEO"]== nom_region]
        df_region = df_region.replace(',','.', regex=True)
        region = df.loc[df["LIBGEO"]== nom_region]
        nvm = region[[ 'LIBGEO' ,'Q2'+ year]]
        nvm = nvm.reset_index(drop=True)
        return nvm
##########################################@@@

    #France
    indice_2014 = niveau_vie_median_france("./revenu/revenu_france/FILO2014_DISP_METROPOLE.csv", "2014").loc[:,"Q214"][0]
    indice_2015 = niveau_vie_median_france("./revenu/revenu_france/FILO2015_DISP_METROPOLE.csv", "2015").loc[:,"Q215"][0]
    indice_2016 = niveau_vie_median_france("./revenu/revenu_france/FILO2016_DISP_METROPOLE.csv", "2016").loc[:,"Q216"][0]
    indice_2017 = niveau_vie_median_france("./revenu/revenu_france/FILO2017_DISP_METROPOLE.csv", "2017").loc[:,"Q217"][0]
    indice_2018 = niveau_vie_median_france("./revenu/revenu_france/FILO2018_DISP_METROPOLE.csv", "2018").loc[:,"Q218"][0]

    df_france_glob = pd.DataFrame(np.array([['France',indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['Territoire','2014', '2015', '2016', '2017', '2018'])
    st.write(df_france_glob)
    #Région
    indice_2014_rg = niveau_vie_median_region("./revenu/revenu_region/FILO2014_DISP_REG.csv",nom_region ,"2014").loc[:,"Q214"][0]
    indice_2015_rg = niveau_vie_median_region("./revenu/revenu_region/FILO2015_DISP_REG.csv",nom_region ,"2015").loc[:,"Q215"][0]
    indice_2016_rg = niveau_vie_median_region("./revenu/revenu_region/FILO2016_DISP_REG.csv",nom_region ,"2016").loc[:,"Q216"][0]
    indice_2017_rg = niveau_vie_median_region("./revenu/revenu_region/FILO2017_DISP_REG.csv",nom_region ,"2017").loc[:,"Q217"][0]
    indice_2018_rg = niveau_vie_median_region("./revenu/revenu_region/FILO2018_DISP_REG.csv",nom_region ,"2018").loc[:,"Q218"][0]

    df_region_glob = pd.DataFrame(np.array([[nom_region,indice_2014_rg, indice_2015_rg, indice_2016_rg, indice_2017_rg, indice_2018_rg]]),
                       columns=['Territoire','2014', '2015', '2016', '2017', '2018'])
    df_region_glob = df_region_glob.replace(',','.', regex=True)
    st.write(df_region_glob)

    data_df = pd.concat([df_france_glob, df_region_glob])
    data_df = data_df.reset_index(drop=True)

    st.write(data_df)

