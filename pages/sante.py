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

  st.title("SANTÉ")
  st.header('1.Taux de mortalité')
  st.caption("Le taux de mortalité est ici un taux annuel moyen sur la dernière période intercensitaire. \
              C’est le rapport entre les décès de la période et la moyenne des populations entre les deux recensements. \
              Ce taux de mortalité est le taux 'brut' de mortalité. \
              Il ne doit pas être confondu avec le taux de mortalité standardisé qui permet de comparer des taux de mortalité \
              à structure d'âge équivalente ou avec le taux de mortalité prématuré qui ne s'intéresse qu'aux décès intervenus avant 65 ans.")

  #Commune
  def tx_mortalite_commune(fichier, nom_ville) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_ville = df.loc[df["libgeo"] == nom_ville]
    df_ville = df_ville.loc[df_ville["an"] == "2013-2018"]
    return df_ville
  tx_mortalite_ville = tx_mortalite_commune("./sante/taux_de_mortalite/insee_rp_evol_1968_communes_2018.csv",nom_commune)

  #EPCI
  def tx_mortalite_epci(fichier, epci) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_epci = df.loc[df["codgeo"] == epci]
    df_epci = df_epci.loc[df_epci["an"] == "2013-2018"]
    return df_epci
  tx_mortalite_epci = tx_mortalite_epci("./sante/taux_de_mortalite/insee_rp_evol_1968_epci_2018.csv",code_epci)

  #Département
  def tx_mortalite_departement(fichier, departement) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_departement = df.loc[df["codgeo"] == departement]
    df_departement = df_departement.loc[df_departement["an"] == "2013-2018"]
    return df_departement
  tx_mortalite_dpt = tx_mortalite_departement("./sante/taux_de_mortalite/insee_rp_evol_1968_departement_2018.csv",code_departement)

  #Région
  def tx_mortalite_region(fichier, region) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_region = df.loc[df["codgeo"] == region]
    df_region = df_region.loc[df_region["an"] == "2013-2018"]
    return df_region
  tx_mortalite_reg = tx_mortalite_region("./sante/taux_de_mortalite/insee_rp_evol_1968_region_2018.csv",str(round(code_region)))

  #France
  data = {'codgeo':['1'],
          'libgeo':['France'],
          'an':['2013-2018'],
          'tx_morta':['8,8']
          }
  tx_mortalite_france = pd.DataFrame(data)

  #Global
  result = pd.concat([tx_mortalite_ville,tx_mortalite_epci, tx_mortalite_dpt, tx_mortalite_reg, tx_mortalite_france])
  st.write(result)

  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(result)

  st.download_button(
    label="💾 Télécharger les données",
    data=csv,
    file_name='tx_mortalite_comparaison.csv',
    mime='text/csv',
  )

  ###############################
  st.header('2.Licenciés sportifs')
