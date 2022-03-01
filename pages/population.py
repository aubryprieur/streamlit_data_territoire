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
import pyperclip

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
  st.title("POPULATION")
  st.header('1.Evolution de la population')

  ville = code_commune
  df_pop_hist = pd.read_csv('./population/base-cc-serie-historique-2018.CSV', dtype={"CODGEO": str},sep=";")
  df_pop_hist_ville = df_pop_hist.loc[df_pop_hist["CODGEO"]==code_commune]
  df_pop_hist_ville = df_pop_hist_ville.reset_index()
  df_pop_hist_ville = df_pop_hist_ville.loc[:, 'P18_POP' : 'D68_POP']
  df_pop_hist_ville = df_pop_hist_ville.rename(columns={'P18_POP': '2018','P13_POP': '2013','P08_POP': '2008','D99_POP': '1999','D90_POP': '1990','D82_POP': '1982','D75_POP': '1975','D68_POP': '1968' })
  dt_test = df_pop_hist_ville.T
  df_pop_hist_ville.insert(0, 'Commune', nom_commune)
  st.table(df_pop_hist_ville)
  #Télécharger les données
  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(df_pop_hist_ville)

  st.download_button(
       label="💾 Télécharger les données",
       data=csv,
       file_name='evolution_population.csv',
       mime='text/csv',
   )
  # Chart
  st.area_chart(data=dt_test, height=300, use_container_width=True)

  #Indicateurs clés
  evol_68_18 = df_pop_hist_ville.iloc[0]["2018"] - df_pop_hist_ville.iloc[0]["1968"]
  st.metric(label="Population 2018", value='{:,.0f}'.format(df_pop_hist_ville.iloc[0]["2018"]).replace(",", " "), delta=str('{:,.0f}'.format(evol_68_18.item()).replace(",", " ")) + " hab. depuis 1968")
