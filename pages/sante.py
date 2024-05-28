import streamlit as st
from pages.utils import afficher_infos_commune
import pandas as pd
import matplotlib.pyplot as plt
import plotly_express as px
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

  st.title("🩺 SANTÉ")
  st.header('1.Taux de mortalité')
  st.caption("source : Insee RP. Parue le XXXX - Millésime 1968 à 2020")
  st.caption("Le taux de mortalité est ici un taux annuel moyen sur la dernière période intercensitaire. \
              C’est le rapport entre les décès de la période et la moyenne des populations entre les deux recensements. \
              Ce taux de mortalité est le taux 'brut' de mortalité. \
              Il ne doit pas être confondu avec le taux de mortalité standardisé qui permet de comparer des taux de mortalité \
              à structure d'âge équivalente ou avec le taux de mortalité prématuré qui ne s'intéresse qu'aux décès intervenus avant 65 ans.")

  #Commune
  period = "2014-2020"
  last_year_mortal = "2020"
  def tx_mortalite_commune(fichier, nom_ville, period) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_ville = df.loc[df["libgeo"] == nom_ville]
    df_ville = df_ville.loc[df_ville["an"] == period ]
    return df_ville
  tx_mortalite_ville = tx_mortalite_commune("./sante/taux_de_mortalite/insee_rp_evol_1968_communes_" + last_year_mortal + ".csv",nom_commune, period)

  #EPCI
  def tx_mortalite_epci(fichier, epci, period) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_epci = df.loc[df["codgeo"] == epci]
    df_epci = df_epci.loc[df_epci["an"] == period]
    return df_epci
  tx_mortalite_epci = tx_mortalite_epci("./sante/taux_de_mortalite/insee_rp_evol_1968_epci_" + last_year_mortal + ".csv",code_epci, period)

  #Département
  def tx_mortalite_departement(fichier, departement, period) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_departement = df.loc[df["codgeo"] == departement]
    df_departement = df_departement.loc[df_departement["an"] == period]
    return df_departement
  tx_mortalite_dpt = tx_mortalite_departement("./sante/taux_de_mortalite/insee_rp_evol_1968_departement_" + last_year_mortal + ".csv",code_departement, period)

  #Région
  def tx_mortalite_region(fichier, region, period) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_region = df.loc[df["codgeo"] == region]
    df_region = df_region.loc[df_region["an"] == period]
    return df_region
  tx_mortalite_reg = tx_mortalite_region("./sante/taux_de_mortalite/insee_rp_evol_1968_region_" + last_year_mortal + ".csv",code_region, period)

  #France
  def tx_mortalite_france(fichier, period) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_france = df.loc[df["an"] == period]
    return df_france
  tx_mortalite_france = tx_mortalite_france("./sante/taux_de_mortalite/insee_rp_evol_1968_france_" + last_year_mortal + ".csv", period)

  #Global
  result = pd.concat([tx_mortalite_ville,tx_mortalite_epci, tx_mortalite_dpt, tx_mortalite_reg, tx_mortalite_france])
  st.write(result)
  ############################################################################
  st.header("Accessibilité potentielle localisée (APL) aux médecins généralistes")
  st.caption("Source : SNDS, Système National des Données de Santé. Parue le XXXX - Millésime 2021")
  st.caption("L’Accessibilité Potentielle Localisée est un indicateur local, disponible au niveau de chaque commune, qui tient compte de l’offre et de la demande issue des communes environnantes. Calculé à l’échelle communale, l’APL met en évidence des disparités d’offre de soins. L’APL tient compte du niveau d’activité des professionnels en exercice ainsi que de la structure par âge de la population de chaque commune qui influence les besoins de soins. L’indicateur permet de quantifier la possibilité des habitants d’accéder aux soins des médecins généralistes libéraux.")

  last_year_apl = "2021"
  #Commune
  df_apl = pd.read_csv("./sante/apl/apl_medecin_generaliste_com_" + last_year_apl + ".csv", dtype={"codgeo": str, "an": str},sep=";")
  df_apl_com = df_apl.loc[df_apl["codgeo"] == code_commune]
  apl_com = df_apl_com['apl_mg_hmep'].values[0]
  #epci
  df_apl_epci = pd.read_csv("./sante/apl/apl_medecin_generaliste_epci_" + last_year_apl + ".csv", dtype={"codgeo": str, "an": str},sep=";")
  df_apl_epci = df_apl_epci.loc[df_apl_epci["codgeo"] == code_epci]
  apl_epci = df_apl_epci['apl_mg_hmep'].values[0]
  #Département
  df_apl_dpt = pd.read_csv("./sante/apl/apl_medecin_generaliste_dpt_" + last_year_apl + ".csv", dtype={"codgeo": str, "an": str},sep=";")
  df_apl_dpt = df_apl_dpt.loc[df_apl_dpt["codgeo"] == code_departement]
  apl_dpt = df_apl_dpt['apl_mg_hmep'].values[0]
  #Région
  df_apl_reg = pd.read_csv("./sante/apl/apl_medecin_generaliste_region_" + last_year_apl + ".csv", dtype={"codgeo": str, "an": str},sep=";")
  df_apl_reg = df_apl_reg.loc[df_apl_reg["codgeo"] == code_region]
  apl_reg = df_apl_reg['apl_mg_hmep'].values[0]
  #France
  df_apl_fr = pd.read_csv("./sante/apl/apl_medecin_generaliste_france_" + last_year_apl + ".csv", dtype={"codgeo": str, "an": str},sep=";")
  apl_fr = df_apl_fr['apl_mg_hmep'].values[0]
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "APL - " + last_year_apl + "": [str(apl_com), apl_epci, apl_dpt, apl_reg, apl_fr]}
  df = pd.DataFrame(data=d)
  st.write(df)



