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
  def niveau_vie_median_commune(fichier, nom_ville, annee) :
      df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
      year = select_annee[-2:]
      df_ville = df.loc[df["LIBGEO"]== nom_ville]
      df_ville = df_ville.replace(',','.', regex=True)
      ville = df.loc[df["LIBGEO"]== nom_ville]
      nvm = ville[[ 'LIBGEO' ,'Q2'+ year]]
      return nvm
  nvm_ville = niveau_vie_median_commune("./revenu/revenu_commune/FILO" + select_annee + "_DISP_COM.csv",nom_commune, select_annee)
  ######
  def niveau_vie_median_epci(fichier, cod_epci, annee) :
    df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
    year = select_annee[-2:]
    df_epci = df.loc[df["CODGEO"]== cod_epci]
    df_epci = df_epci.replace(',','.', regex=True)
    epci = df.loc[df["CODGEO"]== cod_epci]
    if epci.empty:
      st.write("l'agglo n'est pas répartoriée par l'insee")
    else:
      nvm = epci[[ 'LIBGEO' ,'Q2'+ year]]
      #epci = epci.iloc[0]["LIBGEO"]
      #nvm =df_epci.loc[:, 'Q2'+ year ].to_numpy()
      #df2 = pd.DataFrame(nvm,  columns = ['Niveau de vie médian en ' + select_annee], index=[epci])
      return nvm

  nvm_epci =niveau_vie_median_epci("./revenu/revenu_epci/FILO" + select_annee + "_DISP_EPCI.csv",str(code_epci), select_annee)
#####
  def niveau_vie_median_departement(fichier, nom_departement, annee) :
      df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
      year = select_annee[-2:]
      df_departement = df.loc[df["LIBGEO"]== nom_departement]
      df_departement = df_departement.replace(',','.', regex=True)
      departement = df.loc[df["LIBGEO"]== nom_departement]
      nvm = departement[[ 'LIBGEO' ,'Q2'+ year]]
      #departement = departement.iloc[0]["LIBGEO"]
      #nvm =df_departement.loc[:, 'Q2'+ year ].to_numpy()
      #df2 = pd.DataFrame(nvm,  columns = ['Niveau de vie médian en ' + select_annee], index=[departement])
      return nvm
  nvm_departement =niveau_vie_median_departement("./revenu/revenu_dpt/FILO" + select_annee + "_DISP_DEP.csv",nom_departement, select_annee)
#####
  def niveau_vie_median_region(fichier, nom_region, annee) :
      df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
      year = select_annee[-2:]
      df_region = df.loc[df["LIBGEO"]== nom_region]
      df_region = df_region.replace(',','.', regex=True)
      region = df.loc[df["LIBGEO"]== nom_region]
      #region = region.iloc[0]["LIBGEO"]
      #nvm =df_region.loc[:, 'Q2'+ year ].to_numpy()
      #df2 = pd.DataFrame(nvm,  columns = ['Niveau de vie médian en ' + select_annee], index=[region])
      nvm = region[[ 'LIBGEO' ,'Q2'+ year]]
      return nvm
  nvm_region =niveau_vie_median_region("./revenu/revenu_region/FILO" + select_annee + "_DISP_REG.csv",nom_region, select_annee)
#####

  def niveau_vie_median_france(fichier, annee) :
      df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
      df = df.replace(',','.', regex=True)
      year = select_annee[-2:]
      nvm = df[[ 'LIBGEO' ,'Q2'+ year]]
      return nvm
  nvm_france =niveau_vie_median_france("./revenu/revenu_france/FILO" + select_annee + "_DISP_METROPOLE.csv", select_annee)

  test_tab = pd.concat([nvm_ville, nvm_epci, nvm_departement, nvm_region, nvm_france])
  test_tab = test_tab.reset_index(drop=True)
  st.write(test_tab)



