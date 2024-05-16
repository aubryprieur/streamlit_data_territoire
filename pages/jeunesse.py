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
import streamlit_folium as folium_st
from shapely.geometry import Polygon, MultiPolygon
import streamlit.components.v1 as components
import fiona
import plotly.graph_objects as go
import jenkspy


def app(code_commune, nom_commune, code_epci, nom_epci, code_departement, nom_departement, code_region, nom_region):
  # Appeler la fonction et récupérer les informations

  #############################################################################
  st.title("👦👧 JEUNESSE")
  st.subheader("Scolarisation des plus de 18 ans")
  st.caption("Paru le 27/06/2023 - Millésime 2020")
  last_year = "2020"
  #Commune
  def part_scol_18P(code_commune, select_annee):
    df = pd.read_csv("./diplome/commune/base-cc-diplomes-formation-" + select_annee + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
    df_commune = df.loc[df['CODGEO'] == code_commune]
    df_commune["total_pop18P_commune"] = df_commune["P" + select_annee[-2:] + "_POP1824"] + df_commune["P" + select_annee[-2:] + "_POP2529"] + df_commune["P" + select_annee[-2:] + "_POP30P"]
    df_commune["pop_scol18P_commune"] = df_commune["P" + select_annee[-2:] + "_SCOL1824"] + df_commune["P" + select_annee[-2:] + "_SCOL2529"] + df_commune["P" + select_annee[-2:] + "_SCOL30P"]
    part_scol18P_commune = (df_commune["pop_scol18P_commune"].values[0] / df_commune["total_pop18P_commune"].values[0]) * 100
    return part_scol18P_commune
  part_pop_scol18P_commune = part_scol_18P(code_commune, last_year)
  #EPCI
  df = pd.read_csv("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  total_pop18P_epci = df_epci["P" + last_year[-2:] + "_POP1824"].sum() + df_epci["P" + last_year[-2:] + "_POP2529"].sum() + df_epci["P" + last_year[-2:] + "_POP30P"].sum()
  pop_scol18P_epci = df_epci["P" + last_year[-2:] + "_SCOL1824"].sum() + df_epci["P" + last_year[-2:] + "_SCOL2529"].sum() + df_epci["P" + last_year[-2:] + "_SCOL30P"].sum()
  part_scol18P_epci = (pop_scol18P_epci / total_pop18P_epci) * 100
  #Département
  df = pd.read_csv("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str, "DEP": str}, sep=";")
  df_dpt = df.loc[df['DEP'] == code_departement]
  pop_18P_dpt = df_dpt["P" + last_year[-2:] + "_POP1824"].sum() + df_dpt["P" + last_year[-2:] + "_POP2529"].sum() + df_dpt["P" + last_year[-2:] + "_POP30P"].sum()
  pop_scol_18P_dpt = df_dpt["P" + last_year[-2:] + "_SCOL1824"].sum() + df_dpt["P" + last_year[-2:] + "_SCOL2529"].sum() + df_dpt["P" + last_year[-2:] + "_SCOL30P"].sum()
  part_pop_scol18P_dpt = round(((pop_scol_18P_dpt / pop_18P_dpt) * 100), 2)
  #Région
  df = pd.read_csv("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str, "REG": str}, sep=";")
  df_region = df.loc[df['REG'] == str(code_region)]
  pop_18P_region = df_region["P" + last_year[-2:] + "_POP1824"].sum() + df_region["P" + last_year[-2:] + "_POP2529"].sum() + df_region["P" + last_year[-2:] + "_POP30P"].sum()
  pop_scol_18P_region = df_region["P" + last_year[-2:] + "_SCOL1824"].sum() + df_region["P" + last_year[-2:] + "_SCOL2529"].sum() + df_region["P" + last_year[-2:] + "_SCOL30P"].sum()
  part_pop_scol18P_region = round(((pop_scol_18P_region / pop_18P_region) * 100), 2)
  #France
  df = pd.read_csv("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  pop_18P_france = df["P" + last_year[-2:] + "_POP1824"].sum() + df["P" + last_year[-2:] + "_POP2529"].sum() + df["P" + last_year[-2:] + "_POP30P"].sum()
  pop_scol_18P_france = df["P" + last_year[-2:] + "_SCOL1824"].sum() + df["P" + last_year[-2:] + "_SCOL2529"].sum() + df["P" + last_year[-2:] + "_SCOL30P"].sum()
  part_pop_scol_18P_france = round(((pop_scol_18P_france / pop_18P_france) * 100), 2)
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Part de la population scolarisée des plus de 18 ans - " + last_year + " (en %)": [part_pop_scol18P_commune, part_scol18P_epci, part_pop_scol18P_dpt, part_pop_scol18P_region, part_pop_scol_18P_france]}
  df = pd.DataFrame(data=d)
  st.write(df)

  ######################################################
  # AGEQ80_17015 c'est pour les 15_19 ANS
  st.subheader("Autonomie des jeunes 15-19 ans")
  st.caption("Paru le 27/06/2023 - Millésime 2020")
  last_year = "2020"
  #Commune
  df = pd.read_csv("./jeunesse/cohabitation/TD_MEN7_" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  df_commune = df.loc[df['CODGEO'] == code_commune]
  df_com2 = df_commune.filter(regex='AGEQ80_17015')
  df_com2["Enfants d'un couple"] = df_com2["MOCO11_AGEQ80_17015_SEXE1"] + df_com2["MOCO11_AGEQ80_17015_SEXE2"]
  df_com2["Enfants d'une famille monoparentale"] = df_com2["MOCO12_AGEQ80_17015_SEXE1"] + df_com2["MOCO12_AGEQ80_17015_SEXE2"]
  df_com2["Adultes d'un couple sans enfant"] = df_com2["MOCO21_AGEQ80_17015_SEXE1"] + df_com2["MOCO21_AGEQ80_17015_SEXE2"]
  df_com2["Adultes d'un couple avec enfant(s)"] = df_com2["MOCO22_AGEQ80_17015_SEXE1"] + df_com2["MOCO22_AGEQ80_17015_SEXE2"]
  df_com2["Adultes d'une famille monoparentale"] = df_com2["MOCO23_AGEQ80_17015_SEXE1"] + df_com2["MOCO23_AGEQ80_17015_SEXE2"]
  df_com2["Hors famille dans ménage de plusieurs personnes"] = df_com2["MOCO31_AGEQ80_17015_SEXE1"] + df_com2["MOCO31_AGEQ80_17015_SEXE2"]
  df_com2["Personnes vivant seules"] = df_com2["MOCO32_AGEQ80_17015_SEXE1"] + df_com2["MOCO32_AGEQ80_17015_SEXE2"]
  df_com3 = df_com2[["Enfants d'un couple", "Enfants d'une famille monoparentale", "Adultes d'un couple sans enfant", "Adultes d'un couple avec enfant(s)", "Adultes d'une famille monoparentale", "Hors famille dans ménage de plusieurs personnes", "Personnes vivant seules"]]
  df_com3 = df_com3.T
  df_com3 = df_com3.rename(columns={df_com3.columns[0]: nom_commune})

  #EPCI
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci2 = df_epci.filter(regex='AGEQ80_17015')
  df_epci2["Enfants d'un couple"] = df_epci2["MOCO11_AGEQ80_17015_SEXE1"] + df_epci2["MOCO11_AGEQ80_17015_SEXE2"]
  df_epci2["Enfants d'une famille monoparentale"] = df_epci2["MOCO12_AGEQ80_17015_SEXE1"] + df_epci2["MOCO12_AGEQ80_17015_SEXE2"]
  df_epci2["Adultes d'un couple sans enfant"] = df_epci2["MOCO21_AGEQ80_17015_SEXE1"] + df_epci2["MOCO21_AGEQ80_17015_SEXE2"]
  df_epci2["Adultes d'un couple avec enfant(s)"] = df_epci2["MOCO22_AGEQ80_17015_SEXE1"] + df_epci2["MOCO22_AGEQ80_17015_SEXE2"]
  df_epci2["Adultes d'une famille monoparentale"] = df_epci2["MOCO23_AGEQ80_17015_SEXE1"] + df_epci2["MOCO23_AGEQ80_17015_SEXE2"]
  df_epci2["Hors famille dans ménage de plusieurs personnes"] = df_epci2["MOCO31_AGEQ80_17015_SEXE1"] + df_epci2["MOCO31_AGEQ80_17015_SEXE2"]
  df_epci2["Personnes vivant seules"] = df_epci2["MOCO32_AGEQ80_17015_SEXE1"] + df_epci2["MOCO32_AGEQ80_17015_SEXE2"]
  df_epci3 = df_epci2[["Enfants d'un couple", "Enfants d'une famille monoparentale", "Adultes d'un couple sans enfant", "Adultes d'un couple avec enfant(s)", "Adultes d'une famille monoparentale", "Hors famille dans ménage de plusieurs personnes", "Personnes vivant seules"]]
  df_epci3 = df_epci3.sum(axis=0)
  df_epci3 = df_epci3.to_frame()
  df_epci3 = df_epci3.rename(columns={df_epci3.columns[0]: nom_epci})

  #département
  df_dep= pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, sep = ',')
  df_dep_merge = pd.merge(df, df_dep[['COM','DEP']], left_on='CODGEO', right_on='COM')
  df_dep = df_dep_merge.loc[df_dep_merge["DEP"] == str(code_departement)]
  df_dep2 = df_dep.filter(regex='AGEQ80_17015')
  df_dep2["Enfants d'un couple"] = df_dep2["MOCO11_AGEQ80_17015_SEXE1"] + df_dep2["MOCO11_AGEQ80_17015_SEXE2"]
  df_dep2["Enfants d'une famille monoparentale"] = df_dep2["MOCO12_AGEQ80_17015_SEXE1"] + df_dep2["MOCO12_AGEQ80_17015_SEXE2"]
  df_dep2["Adultes d'un couple sans enfant"] = df_dep2["MOCO21_AGEQ80_17015_SEXE1"] + df_dep2["MOCO21_AGEQ80_17015_SEXE2"]
  df_dep2["Adultes d'un couple avec enfant(s)"] = df_dep2["MOCO22_AGEQ80_17015_SEXE1"] + df_dep2["MOCO22_AGEQ80_17015_SEXE2"]
  df_dep2["Adultes d'une famille monoparentale"] = df_dep2["MOCO23_AGEQ80_17015_SEXE1"] + df_dep2["MOCO23_AGEQ80_17015_SEXE2"]
  df_dep2["Hors famille dans ménage de plusieurs personnes"] = df_dep2["MOCO31_AGEQ80_17015_SEXE1"] + df_dep2["MOCO31_AGEQ80_17015_SEXE2"]
  df_dep2["Personnes vivant seules"] = df_dep2["MOCO32_AGEQ80_17015_SEXE1"] + df_dep2["MOCO32_AGEQ80_17015_SEXE2"]
  df_dep3 = df_dep2[["Enfants d'un couple", "Enfants d'une famille monoparentale", "Adultes d'un couple sans enfant", "Adultes d'un couple avec enfant(s)", "Adultes d'une famille monoparentale", "Hors famille dans ménage de plusieurs personnes", "Personnes vivant seules"]]
  df_dep3 = df_dep3.sum(axis=0)
  df_dep3 = df_dep3.to_frame()
  df_dep3 = df_dep3.rename(columns={df_dep3.columns[0]: nom_departement})

  #Région
  df_reg= pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
  df_reg_merge = pd.merge(df, df_reg[['COM','REG']], left_on='CODGEO', right_on='COM')
  df_reg = df_reg_merge.loc[df_reg_merge["REG"] == str(code_region)]
  df_reg2 = df_reg.filter(regex='AGEQ80_17015')
  df_reg2["Enfants d'un couple"] = df_reg2["MOCO11_AGEQ80_17015_SEXE1"] + df_reg2["MOCO11_AGEQ80_17015_SEXE2"]
  df_reg2["Enfants d'une famille monoparentale"] = df_reg2["MOCO12_AGEQ80_17015_SEXE1"] + df_reg2["MOCO12_AGEQ80_17015_SEXE2"]
  df_reg2["Adultes d'un couple sans enfant"] = df_reg2["MOCO21_AGEQ80_17015_SEXE1"] + df_reg2["MOCO21_AGEQ80_17015_SEXE2"]
  df_reg2["Adultes d'un couple avec enfant(s)"] = df_reg2["MOCO22_AGEQ80_17015_SEXE1"] + df_reg2["MOCO22_AGEQ80_17015_SEXE2"]
  df_reg2["Adultes d'une famille monoparentale"] = df_reg2["MOCO23_AGEQ80_17015_SEXE1"] + df_reg2["MOCO23_AGEQ80_17015_SEXE2"]
  df_reg2["Hors famille dans ménage de plusieurs personnes"] = df_reg2["MOCO31_AGEQ80_17015_SEXE1"] + df_reg2["MOCO31_AGEQ80_17015_SEXE2"]
  df_reg2["Personnes vivant seules"] = df_reg2["MOCO32_AGEQ80_17015_SEXE1"] + df_reg2["MOCO32_AGEQ80_17015_SEXE2"]
  df_reg3 = df_reg2[["Enfants d'un couple", "Enfants d'une famille monoparentale", "Adultes d'un couple sans enfant", "Adultes d'un couple avec enfant(s)", "Adultes d'une famille monoparentale", "Hors famille dans ménage de plusieurs personnes", "Personnes vivant seules"]]
  df_reg3 = df_reg3.sum(axis=0)
  df_reg3 = df_reg3.to_frame()
  df_reg3 = df_reg3.rename(columns={df_reg3.columns[0]: nom_region})

  #France
  df_fr = df.filter(regex='AGEQ80_17015')
  df_fr["Enfants d'un couple"] = df_fr["MOCO11_AGEQ80_17015_SEXE1"] + df_fr["MOCO11_AGEQ80_17015_SEXE2"]
  df_fr["Enfants d'une famille monoparentale"] = df_fr["MOCO12_AGEQ80_17015_SEXE1"] + df_fr["MOCO12_AGEQ80_17015_SEXE2"]
  df_fr["Adultes d'un couple sans enfant"] = df_fr["MOCO21_AGEQ80_17015_SEXE1"] + df_fr["MOCO21_AGEQ80_17015_SEXE2"]
  df_fr["Adultes d'un couple avec enfant(s)"] = df_fr["MOCO22_AGEQ80_17015_SEXE1"] + df_fr["MOCO22_AGEQ80_17015_SEXE2"]
  df_fr["Adultes d'une famille monoparentale"] = df_fr["MOCO23_AGEQ80_17015_SEXE1"] + df_fr["MOCO23_AGEQ80_17015_SEXE2"]
  df_fr["Hors famille dans ménage de plusieurs personnes"] = df_fr["MOCO31_AGEQ80_17015_SEXE1"] + df_fr["MOCO31_AGEQ80_17015_SEXE2"]
  df_fr["Personnes vivant seules"] = df_fr["MOCO32_AGEQ80_17015_SEXE1"] + df_fr["MOCO32_AGEQ80_17015_SEXE2"]
  df_fr2 = df_fr[["Enfants d'un couple", "Enfants d'une famille monoparentale", "Adultes d'un couple sans enfant", "Adultes d'un couple avec enfant(s)", "Adultes d'une famille monoparentale", "Hors famille dans ménage de plusieurs personnes", "Personnes vivant seules"]]
  df_fr2 = df_fr2.sum(axis=0)
  df_fr2 = df_fr2.to_frame()
  df_fr2 = df_fr2.rename(columns={df_fr2.columns[0]: "France"})

  # Fusion des dataframes
  df_fusionne = pd.concat([df_com3, df_epci3, df_dep3, df_reg3, df_fr2], axis=1)
  st.write(df_fusionne)

  #Graphique
  # Transposer le DataFrame pour avoir les zones géographiques en abscisse
  df_transpose = df_fusionne.T
  # Normaliser les données pour obtenir des pourcentages
  df_normalized = df_transpose.div(df_transpose.sum(axis=1), axis=0) * 100
  # Créer le graphique à barres empilées
  fig = go.Figure()
  for col in df_normalized.columns:
      fig.add_trace(go.Bar(
          x=df_normalized.index,
          y=df_normalized[col],
          name=col
      ))
  # Mise à jour du layout pour empiler les barres
  fig.update_layout(
      barmode='stack',
      title='Répartition des types de ménages par zone géographique en pourcentage',
      xaxis_title='Zone géographique',
      yaxis_title='Pourcentage',
      legend_title='Type de ménage'
  )
  # Afficher le graphique dans Streamlit
  st.plotly_chart(fig)

  ############################################################################
  st.subheader("Autonomie des jeunes 20-24 ans")
  st.caption("Paru le 27/06/2023 - Millésime 2020")
  last_year = "2020"
  #Commune
  df = pd.read_csv("./jeunesse/cohabitation/TD_MEN7_" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  df_commune = df.loc[df['CODGEO'] == code_commune]
  df_com2 = df_commune.filter(regex='AGEQ80_17020')
  df_com2["Enfants d'un couple"] = df_com2["MOCO11_AGEQ80_17020_SEXE1"] + df_com2["MOCO11_AGEQ80_17020_SEXE2"]
  df_com2["Enfants d'une famille monoparentale"] = df_com2["MOCO12_AGEQ80_17020_SEXE1"] + df_com2["MOCO12_AGEQ80_17020_SEXE2"]
  df_com2["Adultes d'un couple sans enfant"] = df_com2["MOCO21_AGEQ80_17020_SEXE1"] + df_com2["MOCO21_AGEQ80_17020_SEXE2"]
  df_com2["Adultes d'un couple avec enfant(s)"] = df_com2["MOCO22_AGEQ80_17020_SEXE1"] + df_com2["MOCO22_AGEQ80_17020_SEXE2"]
  df_com2["Adultes d'une famille monoparentale"] = df_com2["MOCO23_AGEQ80_17020_SEXE1"] + df_com2["MOCO23_AGEQ80_17020_SEXE2"]
  df_com2["Hors famille dans ménage de plusieurs personnes"] = df_com2["MOCO31_AGEQ80_17020_SEXE1"] + df_com2["MOCO31_AGEQ80_17020_SEXE2"]
  df_com2["Personnes vivant seules"] = df_com2["MOCO32_AGEQ80_17020_SEXE1"] + df_com2["MOCO32_AGEQ80_17020_SEXE2"]
  df_com3 = df_com2[["Enfants d'un couple", "Enfants d'une famille monoparentale", "Adultes d'un couple sans enfant", "Adultes d'un couple avec enfant(s)", "Adultes d'une famille monoparentale", "Hors famille dans ménage de plusieurs personnes", "Personnes vivant seules"]]
  df_com3 = df_com3.T
  df_com3 = df_com3.rename(columns={df_com3.columns[0]: nom_commune})

  #EPCI
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci2 = df_epci.filter(regex='AGEQ80_17020')
  df_epci2["Enfants d'un couple"] = df_epci2["MOCO11_AGEQ80_17020_SEXE1"] + df_epci2["MOCO11_AGEQ80_17020_SEXE2"]
  df_epci2["Enfants d'une famille monoparentale"] = df_epci2["MOCO12_AGEQ80_17020_SEXE1"] + df_epci2["MOCO12_AGEQ80_17020_SEXE2"]
  df_epci2["Adultes d'un couple sans enfant"] = df_epci2["MOCO21_AGEQ80_17020_SEXE1"] + df_epci2["MOCO21_AGEQ80_17020_SEXE2"]
  df_epci2["Adultes d'un couple avec enfant(s)"] = df_epci2["MOCO22_AGEQ80_17020_SEXE1"] + df_epci2["MOCO22_AGEQ80_17020_SEXE2"]
  df_epci2["Adultes d'une famille monoparentale"] = df_epci2["MOCO23_AGEQ80_17020_SEXE1"] + df_epci2["MOCO23_AGEQ80_17020_SEXE2"]
  df_epci2["Hors famille dans ménage de plusieurs personnes"] = df_epci2["MOCO31_AGEQ80_17020_SEXE1"] + df_epci2["MOCO31_AGEQ80_17020_SEXE2"]
  df_epci2["Personnes vivant seules"] = df_epci2["MOCO32_AGEQ80_17020_SEXE1"] + df_epci2["MOCO32_AGEQ80_17020_SEXE2"]
  df_epci3 = df_epci2[["Enfants d'un couple", "Enfants d'une famille monoparentale", "Adultes d'un couple sans enfant", "Adultes d'un couple avec enfant(s)", "Adultes d'une famille monoparentale", "Hors famille dans ménage de plusieurs personnes", "Personnes vivant seules"]]
  df_epci3 = df_epci3.sum(axis=0)
  df_epci3 = df_epci3.to_frame()
  df_epci3 = df_epci3.rename(columns={df_epci3.columns[0]: nom_epci})

  #département
  df_dep= pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, sep = ',')
  df_dep_merge = pd.merge(df, df_dep[['COM','DEP']], left_on='CODGEO', right_on='COM')
  df_dep = df_dep_merge.loc[df_dep_merge["DEP"] == str(code_departement)]
  df_dep2 = df_dep.filter(regex='AGEQ80_17020')
  df_dep2["Enfants d'un couple"] = df_dep2["MOCO11_AGEQ80_17020_SEXE1"] + df_dep2["MOCO11_AGEQ80_17020_SEXE2"]
  df_dep2["Enfants d'une famille monoparentale"] = df_dep2["MOCO12_AGEQ80_17020_SEXE1"] + df_dep2["MOCO12_AGEQ80_17020_SEXE2"]
  df_dep2["Adultes d'un couple sans enfant"] = df_dep2["MOCO21_AGEQ80_17020_SEXE1"] + df_dep2["MOCO21_AGEQ80_17020_SEXE2"]
  df_dep2["Adultes d'un couple avec enfant(s)"] = df_dep2["MOCO22_AGEQ80_17020_SEXE1"] + df_dep2["MOCO22_AGEQ80_17020_SEXE2"]
  df_dep2["Adultes d'une famille monoparentale"] = df_dep2["MOCO23_AGEQ80_17020_SEXE1"] + df_dep2["MOCO23_AGEQ80_17020_SEXE2"]
  df_dep2["Hors famille dans ménage de plusieurs personnes"] = df_dep2["MOCO31_AGEQ80_17020_SEXE1"] + df_dep2["MOCO31_AGEQ80_17020_SEXE2"]
  df_dep2["Personnes vivant seules"] = df_dep2["MOCO32_AGEQ80_17020_SEXE1"] + df_dep2["MOCO32_AGEQ80_17020_SEXE2"]
  df_dep3 = df_dep2[["Enfants d'un couple", "Enfants d'une famille monoparentale", "Adultes d'un couple sans enfant", "Adultes d'un couple avec enfant(s)", "Adultes d'une famille monoparentale", "Hors famille dans ménage de plusieurs personnes", "Personnes vivant seules"]]
  df_dep3 = df_dep3.sum(axis=0)
  df_dep3 = df_dep3.to_frame()
  df_dep3 = df_dep3.rename(columns={df_dep3.columns[0]: nom_departement})

  #Région
  df_reg= pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
  df_reg_merge = pd.merge(df, df_reg[['COM','REG']], left_on='CODGEO', right_on='COM')
  df_reg = df_reg_merge.loc[df_reg_merge["REG"] == str(code_region)]
  df_reg2 = df_reg.filter(regex='AGEQ80_17020')
  df_reg2["Enfants d'un couple"] = df_reg2["MOCO11_AGEQ80_17020_SEXE1"] + df_reg2["MOCO11_AGEQ80_17020_SEXE2"]
  df_reg2["Enfants d'une famille monoparentale"] = df_reg2["MOCO12_AGEQ80_17020_SEXE1"] + df_reg2["MOCO12_AGEQ80_17020_SEXE2"]
  df_reg2["Adultes d'un couple sans enfant"] = df_reg2["MOCO21_AGEQ80_17020_SEXE1"] + df_reg2["MOCO21_AGEQ80_17020_SEXE2"]
  df_reg2["Adultes d'un couple avec enfant(s)"] = df_reg2["MOCO22_AGEQ80_17020_SEXE1"] + df_reg2["MOCO22_AGEQ80_17020_SEXE2"]
  df_reg2["Adultes d'une famille monoparentale"] = df_reg2["MOCO23_AGEQ80_17020_SEXE1"] + df_reg2["MOCO23_AGEQ80_17020_SEXE2"]
  df_reg2["Hors famille dans ménage de plusieurs personnes"] = df_reg2["MOCO31_AGEQ80_17020_SEXE1"] + df_reg2["MOCO31_AGEQ80_17020_SEXE2"]
  df_reg2["Personnes vivant seules"] = df_reg2["MOCO32_AGEQ80_17020_SEXE1"] + df_reg2["MOCO32_AGEQ80_17020_SEXE2"]
  df_reg3 = df_reg2[["Enfants d'un couple", "Enfants d'une famille monoparentale", "Adultes d'un couple sans enfant", "Adultes d'un couple avec enfant(s)", "Adultes d'une famille monoparentale", "Hors famille dans ménage de plusieurs personnes", "Personnes vivant seules"]]
  df_reg3 = df_reg3.sum(axis=0)
  df_reg3 = df_reg3.to_frame()
  df_reg3 = df_reg3.rename(columns={df_reg3.columns[0]: nom_region})

  #France
  df_fr = df.filter(regex='AGEQ80_17020')
  df_fr["Enfants d'un couple"] = df_fr["MOCO11_AGEQ80_17020_SEXE1"] + df_fr["MOCO11_AGEQ80_17020_SEXE2"]
  df_fr["Enfants d'une famille monoparentale"] = df_fr["MOCO12_AGEQ80_17020_SEXE1"] + df_fr["MOCO12_AGEQ80_17020_SEXE2"]
  df_fr["Adultes d'un couple sans enfant"] = df_fr["MOCO21_AGEQ80_17020_SEXE1"] + df_fr["MOCO21_AGEQ80_17020_SEXE2"]
  df_fr["Adultes d'un couple avec enfant(s)"] = df_fr["MOCO22_AGEQ80_17020_SEXE1"] + df_fr["MOCO22_AGEQ80_17020_SEXE2"]
  df_fr["Adultes d'une famille monoparentale"] = df_fr["MOCO23_AGEQ80_17020_SEXE1"] + df_fr["MOCO23_AGEQ80_17020_SEXE2"]
  df_fr["Hors famille dans ménage de plusieurs personnes"] = df_fr["MOCO31_AGEQ80_17020_SEXE1"] + df_fr["MOCO31_AGEQ80_17020_SEXE2"]
  df_fr["Personnes vivant seules"] = df_fr["MOCO32_AGEQ80_17020_SEXE1"] + df_fr["MOCO32_AGEQ80_17020_SEXE2"]
  df_fr2 = df_fr[["Enfants d'un couple", "Enfants d'une famille monoparentale", "Adultes d'un couple sans enfant", "Adultes d'un couple avec enfant(s)", "Adultes d'une famille monoparentale", "Hors famille dans ménage de plusieurs personnes", "Personnes vivant seules"]]
  df_fr2 = df_fr2.sum(axis=0)
  df_fr2 = df_fr2.to_frame()
  df_fr2 = df_fr2.rename(columns={df_fr2.columns[0]: "France"})

  # Fusion des dataframes
  df_fusionne = pd.concat([df_com3, df_epci3, df_dep3, df_reg3, df_fr2], axis=1)
  st.write(df_fusionne)

  #Graphique
  # Transposer le DataFrame pour avoir les zones géographiques en abscisse
  df_transpose = df_fusionne.T
  # Normaliser les données pour obtenir des pourcentages
  df_normalized = df_transpose.div(df_transpose.sum(axis=1), axis=0) * 100
  # Créer le graphique à barres empilées
  fig = go.Figure()
  for col in df_normalized.columns:
      fig.add_trace(go.Bar(
          x=df_normalized.index,
          y=df_normalized[col],
          name=col
      ))
  # Mise à jour du layout pour empiler les barres
  fig.update_layout(
      barmode='stack',
      title='Répartition des types de ménages par zone géographique en pourcentage',
      xaxis_title='Zone géographique',
      yaxis_title='Pourcentage',
      legend_title='Type de ménage'
  )
  # Afficher le graphique dans Streamlit
  st.plotly_chart(fig)

  ###########################
  st.header("Réussite au brevet")
  st.caption("Paru le 2 juin 2023 - Millésime 2006-2021")
  df_filt = pd.read_csv('./jeunesse/EN/fr-en-dnb-par-etablissement.csv', dtype={"Session": str , "Commune": str, "Code département": str, "Code académie": str, "Code région": str}, sep=";")
  df_filt = df_filt.loc[df_filt["Commune"] == code_commune ]
  feature_1_val = df_filt["Patronyme"].unique()
  new_arr = np.insert(feature_1_val, 0, "")
  feature_1ed = st.selectbox('Sélectionner un collège', new_arr)
  st.write('Votre collège:', feature_1ed)

  df = pd.read_csv('./jeunesse/EN/fr-en-dnb-par-etablissement.csv', dtype={"Session": str, "Commune": str, "Code département": str, "Code académie": str, "Code région": str}, sep=";")
  df = df.loc[df["Commune"] == code_commune ]
  df = df.replace(',','.', regex=True)
  df = df.replace('%','', regex=True)
  df['Taux de réussite'] = pd.to_numeric(df['Taux de réussite'])
  if feature_1ed != "":
    df = df.loc[df["Patronyme"] == feature_1ed ]
  df = df.reset_index(drop=True)
  df = df[["Session", "Patronyme","Secteur d'enseignement", "Libellé commune", "Taux de réussite"]]
  df = df.sort_values(by=['Patronyme','Session'], ascending=False)
  df = df.reset_index(drop=True)
  st.write(df)

  line_chart = alt.Chart(df).mark_line(interpolate='basis').encode(
      alt.X('Session', title='Année'),
      alt.Y('Taux de réussite:Q', title='Tx de réussite', scale=alt.Scale(domain=[df["Taux de réussite"].min(), df["Taux de réussite"].max()])),
      color='Patronyme:N',
      strokeDash='Patronyme'
  ).properties(
      title='Résultat au Brevet',
      width=800,
      height=300
  )
  st.altair_chart(line_chart, use_container_width=True)


  st.header("Indice de position sociale des élèves des écoles")
  st.caption("Paru le 5 novembre 2022 - Année scolaire 2022-2023")
  last_year_ips = "2023"
  df = pd.read_csv("./jeunesse/EN/fr-en-ips-ecoles_" + last_year_ips + ".csv", dtype={"Rentrée scolaire": str , "Code du département": str, "Code INSEE de la commune": str}, sep=";")
  df = df.loc[df["Code INSEE de la commune"] == code_commune ]
  df = df.reset_index(drop=True)
  df = df[["Rentrée scolaire", "Nom de la commune","Nom de l'établissment", "Secteur", "IPS"]]
  st.write(df)

  st.caption("IPS : outil de mesure quantitatif de la situation sociale des élèves face aux apprentissages dans les établissements scolaires français. Plus l'indice est élevé, plus l'élève évolue dans un contexte familial favorable aux apprentissages. Cet indice est construit à partir des professions et catégories socioprofessionnelles (PCS) des représentants légaux des élèves.")

  st.subheader("Analyse nationale pour les écoles")
  df = pd.read_csv("./jeunesse/EN/fr-en-ips-ecoles_" + last_year_ips + ".csv", dtype={"Rentrée scolaire": str , "Code du département": str, "Code INSEE de la commune": str}, sep=";")
  fig = px.box(df, x='Secteur', y='IPS')
  boxplot_chart = st.plotly_chart(fig)
  boxplot_chart

  st.header("Indice de position sociale des élèves des collèges")
  st.caption("Paru le 5 octobre 2022 - Année scolaire 2022-2023")
  df = pd.read_csv("./jeunesse/EN/fr-en-ips-colleges_" + last_year_ips + ".csv", dtype={"Rentrée scolaire": str , "Code du département": str, "Code INSEE de la commune": str}, sep=";")
  df = df.loc[df["Code INSEE de la commune"] == code_commune ]
  df = df.reset_index(drop=True)
  df = df[["Rentrée scolaire", "Nom de la commune","Nom de l'établissment", "Secteur", "IPS"]]
  st.write(df)

  st.subheader("Analyse nationale pour les collèges")
  df = pd.read_csv("./jeunesse/EN/fr-en-ips-colleges_" + last_year_ips + ".csv", dtype={"Rentrée scolaire": str , "Code du département": str, "Code INSEE de la commune": str}, sep=";")
  fig = px.box(df, x='Secteur', y='IPS')
  boxplot_chart = st.plotly_chart(fig)
  boxplot_chart

  st.header("Indice de position sociale des élèves des lycées")
  st.caption("Paru le 27 mars 2023 - Année scolaire 2022-2023")
  df = pd.read_csv("./jeunesse/EN/fr-en-ips-lycees_" + last_year_ips + ".csv", dtype={"Rentrée scolaire": str , "Code du département": str, "Code INSEE de la commune": str}, sep=";")
  df = df.loc[df["Code INSEE de la commune"] == code_commune ]
  df = df.reset_index(drop=True)
  df = df[["Rentrée scolaire", "Nom de la commune","Nom de l'établissment", "Secteur", "IPS Ensemble GT-PRO"]]
  st.write(df)

  st.subheader("Analyse nationale pour les lycées")
  df = pd.read_csv("./jeunesse/EN/fr-en-ips-lycees_" + last_year_ips + ".csv", dtype={"Rentrée scolaire": str , "Code du département": str, "Code INSEE de la commune": str}, sep=";")
  fig = px.box(df, x='Secteur', y="IPS Ensemble GT-PRO")
  boxplot_chart = st.plotly_chart(fig)
  boxplot_chart
  #############################################################################
  st.header('1.Indice de jeunesse')
  st.caption("Paru le xx/xx/xxxx - Millésime 2020")
  st.caption("L'indice de jeunesse est le rapport de la population des moins de 20 ans sur celle des 65 ans et plus. Un indice autour de 100 indique que les 65 ans et plus et les moins de 20 ans sont présents dans à peu près les mêmes proportions sur le territoire; plus l’indice est faible plus le rapport est favorable aux personnes âgées, plus il est élevé plus il est favorable à la jeunesse.")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    st.subheader("Iris")
    def indice_jeunesse_iris(fichier, code, annee) :
      df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep=";", header=0)
      df_indice = df.loc[df['COM'] == code]
      year = annee[-2:]
      df_indice = df_indice[['COM','IRIS', 'P'+ year + '_POP65P','P' + year +'_POP0019' ]]
      df_indice = df_indice.replace(',','.', regex=True)
      df_indice['P'+ year + '_POP65P'] = df_indice['P'+ year + '_POP65P'].astype(float).to_numpy()
      df_indice['P' + year +'_POP0019'] = df_indice['P' + year +'_POP0019'].astype(float).to_numpy()
      df_indice['indice'] = np.where(df_indice['P' + year +'_POP65P'] < 1,df_indice['P' + year +'_POP65P'], (df_indice['P'+ year + '_POP0019'] / df_indice['P' + year +'_POP65P']*100))
      df_indice['indice'] = df_indice['indice'].astype(float).to_numpy()
      communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
      df_indice_com = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_indice[['IRIS','P' + year +'_POP0019', 'P' + year + '_POP65P','indice']], left_on='CODE_IRIS', right_on="IRIS")
      df_indice_com = df_indice_com[['CODE_IRIS','LIB_IRIS','P' + year +'_POP0019', 'P' + year + '_POP65P','indice']]
      df_indice_com['indice'] = df_indice_com['indice'].apply(np.int64)
      df_indice_com['P' + year +'_POP0019'] = df_indice_com['P' + year +'_POP0019'].apply(np.int64)
      df_indice_com['P' + year +'_POP65P'] = df_indice_com['P' + year +'_POP65P'].apply(np.int64)
      df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_POP0019':"Moins de 20 ans (" + annee + ")" ,'P' + year + '_POP65P':"Plus de 65 ans (" + annee + ")",'indice':"Indice de jeunesse (" + annee + ")" })
      return df_indice_com
    ind_jeunesse_iris =indice_jeunesse_iris("./population/base-ic-evol-struct-pop-" + last_year + ".csv",code_commune, last_year)
    with st.expander("Visualiser le tableau des iris"):
      st.table(ind_jeunesse_iris)

  # Carte Indice jeunesse
  # URL de l'API
  url = "https://public.opendatasoft.com/api/records/1.0/search/?dataset=georef-france-iris-millesime&q=&rows=500&sort=year&facet=year&facet=reg_name&facet=dep_name&facet=arrdep_name&facet=ze2020_name&facet=bv2012_name&facet=epci_name&facet=ept_name&facet=com_name&facet=com_arm_name&facet=iris_name&facet=iris_area_code&facet=iris_type&facet=com_code&refine.year=2022&refine.com_code=" + code_commune
  # Appel à l'API
  response = requests.get(url)
  # Conversion de la réponse en JSON
  data = response.json()
  # Normalisation des données pour obtenir un DataFrame pandas
  df = pd.json_normalize(data['records'])
  # Séparation des latitudes et longitudes
  latitudes, longitudes = zip(*df['fields.geo_point_2d'])
  # Conversion du DataFrame en GeoDataFrame
  gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(longitudes, latitudes))
  # Supposons que 'gdf' est votre GeoDataFrame original
  gdf.set_crs(epsg=4326, inplace=True)  # Définir le système de coordonnées actuel si ce n'est pas déjà fait

  def to_multipolygon(coords):
      def is_nested_list(lst):
          return any(isinstance(i, list) for i in lst)

      if len(coords) == 0:
          return None

      # If the first element of coords is a list of lists, we're dealing with a MultiPolygon
      if is_nested_list(coords[0]):
          polygons = []
          for poly_coords in coords:
              # If the first element of poly_coords is a list of lists, we're dealing with a Polygon with holes
              if is_nested_list(poly_coords[0]):
                  polygons.append(Polygon(shell=poly_coords[0], holes=poly_coords[1:]))
              else:
                  polygons.append(Polygon(poly_coords))
          return MultiPolygon(polygons)
      else:
          return Polygon(coords)


  # Convertir les coordonnées des frontières en objets Polygon ou MultiPolygon
  gdf['geometry'] = gdf['fields.geo_shape.coordinates'].apply(to_multipolygon)

  # Joindre le dataframe de population avec le GeoDataFrame
  gdf = gdf.merge(ind_jeunesse_iris, left_on='fields.iris_code', right_on="Code de l'iris")

  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]

  # Nettoyage des données en supprimant les NaN et conversion en numérique
  gdf["Indice de jeunesse (" + last_year + ")"] = pd.to_numeric(gdf["Indice de jeunesse (" + last_year + ")"], errors='coerce')
  gdf = gdf.dropna(subset=["Indice de jeunesse (" + last_year + ")"])

  # Vérification du nombre de valeurs uniques
  unique_values = gdf["Indice de jeunesse (" + last_year + ")"].nunique()

  if unique_values >= 5:
      # Calcul des breaks avec la méthode de Jenks si suffisamment de valeurs uniques
      breaks = jenkspy.jenks_breaks(gdf["Indice de jeunesse (" + last_year + ")"], 5)
      m = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

      # Ajouter la carte choroplèthe
      folium.Choropleth(
          geo_data=gdf.set_index("Code de l'iris"),
          name='choropleth',
          data=gdf,
          columns=["Code de l'iris", "Indice de jeunesse (" + last_year + ")"],
          key_on='feature.id',
          fill_color='YlOrRd',
          fill_opacity=0.7,
          line_opacity=0.2,
          color='#ffffff',
          weight=3,
          opacity=1.0,
          legend_name='Indice de jeunesse',
          bins=breaks
      ).add_to(m)

      folium.LayerControl().add_to(m)

      style_function = lambda x: {'fillColor': '#ffffff', 'color':'#000000', 'fillOpacity': 0.1, 'weight': 0.1}
      highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.50, 'weight': 0.1}
      NIL = folium.features.GeoJson(
          gdf,
          style_function=style_function,
          control=False,
          highlight_function=highlight_function,
          tooltip=folium.features.GeoJsonTooltip(
              fields=["Nom de l'iris", "Indice de jeunesse (" + last_year + ")"],
              aliases=['Iris: ', "Indice de jeunesse :"],
              style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
          )
      )
      m.add_child(NIL)
      m.keep_in_front(NIL)
      st.subheader("Indice jeunesse par IRIS")
      # Afficher la carte dans Streamlit
      folium_st.folium_static(m)
  else:
      # Pas assez de valeurs uniques pour une visualisation significative
      st.warning("Pas assez de diversité dans les données pour afficher une carte choroplèthe significative.")

  #################################
  st.subheader("Zoom QPV")
  #Année
  select_annee_0024 = st.select_slider(
       "Sélection de l'année",
       options=['2017', '2018', '2019', '2020', '2021', '2022'],
       value=('2022'))
  st.write('Mon année :', select_annee_0024)

  def indice_jeunesse_qpv(fichier, nom_ville, annee) :
    fp_qpv = "./qpv.geojson"
    map_qpv_df = gpd.read_file(fp_qpv)
    year = annee[-2:]
    df = pd.read_csv(fichier, dtype={"CODGEO": str}, sep=";")
    map_qpv_df_code_insee = map_qpv_df.merge(df, left_on='code_qp', right_on='CODGEO')
    map_qpv_df_code_insee_extract = map_qpv_df_code_insee[['nom_qp', 'code_qp', 'commune_qp','code_insee', 'IND_JEUNE' ]]
    map_qpv_df_code_insee_extract
    df_qpv = map_qpv_df_code_insee_extract.loc[map_qpv_df_code_insee_extract["commune_qp"].str.contains(nom_ville + "(,|$)")]
    df_qpv = df_qpv.reset_index(drop=True)
    df_qpv = df_qpv[['code_qp', 'nom_qp','commune_qp', 'IND_JEUNE']]
    df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", 'IND_JEUNE' : "Indice de jeunesse " + select_annee_0024})
    return df_qpv

  ind_jeunesse_qpv = indice_jeunesse_qpv('./population/demographie_qpv/DEMO_' + select_annee_0024 + '.csv', nom_commune, select_annee_0024)
  st.table(ind_jeunesse_qpv)

  st.caption("Attention, calcul de l'indice jeunesse pour les QPV : population de 0 à 19 ans / population de 60 ans et plus")
  ########################
  st.subheader('a.Comparaison sur une année')
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    #comparaison des territoires
    # Commune
    def IV_commune(fichier, code_ville, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_ville = df.loc[df["COM"]==code_ville,]
        nom_ville = df_ville.loc[df["COM"]==code_ville, 'COM']
        Plus_de_65 = df_ville.loc[:, 'P'+ year + '_POP65P'].astype(float).sum(axis = 0, skipna = True)
        Moins_de_20 = df_ville.loc[:, 'P'+ year + '_POP0019'].astype(float).sum(axis = 0, skipna = True)
        IV = round((Moins_de_20 / Plus_de_65 )*100,2)
        df_iv = pd.DataFrame(data=IV, columns = ['Indice de jeunesse en ' + annee], index = [nom_commune])
        return df_iv
    valeur_comiv = IV_commune("./population/base-ic-evol-struct-pop-" + last_year + ".csv", code_commune, last_year)

    # EPCI
    def IV_epci(fichier, epci, annee):
        epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "TYP_IRIS": str, "MODIF_IRIS": str,"COM": str, "LAB_IRIS": str, "DEP": str, "UU2010": str, "GRD_QUART": str}, sep = ';')
        year = annee[-2:]
        df_epci_com = pd.merge(df[['COM', 'P' + year + '_POP0019', 'P' + year + '_POP65P']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
        df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM','P'+ year +'_POP0019' , 'P'+ year + '_POP65P']]
        Plus_de_65 = df_epci.loc[:, 'P'+ year + '_POP65P']
        Moins_de_20 = df_epci.loc[:, 'P'+ year + '_POP0019']
        df_P65 = pd.DataFrame(data=Plus_de_65)
        df_M20 = pd.DataFrame(data=Moins_de_20)
        Somme_P65 = df_P65.sum(axis = 0, skipna = True)
        Somme_M20 = df_M20.sum(axis = 0, skipna = True)
        P65= Somme_P65.values[0]
        M20=Somme_M20.values[0]
        IV = round((M20/P65)*100,2)
        df_ind_epci = pd.DataFrame(data=IV, columns = ["Indice de jeunesse en " + annee], index = [nom_epci])
        return df_ind_epci
    valeurs_ind_epci = IV_epci("./population/base-ic-evol-struct-pop-" + last_year + ".csv",code_epci,last_year)

    # Département
    def IV_departement_M2017(fichier, departement, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_departement = df.loc[df["DEP"]==departement, 'P'+ year +'_POP0019' : 'P'+ year + '_POP65P']
        Plus_de_65 = df_departement.loc[:, 'P'+ year + '_POP65P']
        Moins_de_20 = df_departement.loc[:, 'P'+ year + '_POP0019']
        df_P65 = pd.DataFrame(data=Plus_de_65)
        df_M20 = pd.DataFrame(data=Moins_de_20)
        Somme_P65 = df_P65.sum(axis = 0, skipna = True)
        Somme_M20 = df_M20.sum(axis = 0, skipna = True)
        P65= Somme_P65.values[0]
        M20=Somme_M20.values[0]
        IV = round((M20/P65)*100,2)
        df_dep = pd.DataFrame(data=IV, columns = ['Indice de jeunesse en ' + annee], index = [nom_departement])
        return df_dep

    def IV_departement_P2017(fichier, departement, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_dpt = pd.merge(df[['COM', 'P' + year +'_POP0019', 'P' + year + '_POP65P']], communes_select[['COM','DEP']],  on='COM', how='left')
        df_departement = df_dpt.loc[df_dpt["DEP"]==departement, ['DEP', 'COM','P'+ year +'_POP0019' , 'P'+ year + '_POP65P']]
        Plus_de_65 = df_departement.loc[:, 'P'+ year + '_POP65P']
        Moins_de_20 = df_departement.loc[:, 'P'+ year + '_POP0019']
        df_P65 = pd.DataFrame(data=Plus_de_65)
        df_M20 = pd.DataFrame(data=Moins_de_20)
        Somme_P65 = df_P65.sum(axis = 0, skipna = True)
        Somme_M20 = df_M20.sum(axis = 0, skipna = True)
        P65= Somme_P65.values[0]
        M20=Somme_M20.values[0]
        IV = round((M20/P65)*100,2)
        df_dep = pd.DataFrame(data=IV, columns = ['Indice de jeunesse en ' + annee], index = [nom_departement])
        return df_dep

    if int(last_year) < 2017:
        valeurs_dep_iv = IV_departement_M2017("./population/base-ic-evol-struct-pop-" + last_year + ".csv",code_departement,last_year)
    else :
        valeurs_dep_iv = IV_departement_P2017("./population/base-ic-evol-struct-pop-" + last_year + ".csv",code_departement,last_year)

    # Région
    #si année de 2014 à 2016 (inclus)
    def IV_region_M2017(fichier, region, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_regions = df.loc[df["REG"]==region, 'P'+ year +'_POP0019' : 'P'+ year + '_POP65P']
        Plus_de_65 = df_regions.loc[:, 'P'+ year + '_POP65P']
        Moins_de_20 = df_regions.loc[:, 'P'+ year + '_POP0019']
        df_P65 = pd.DataFrame(data=Plus_de_65)
        df_M20 = pd.DataFrame(data=Moins_de_20)
        Somme_P65 = df_P65.sum(axis = 0, skipna = True)
        Somme_M20 = df_M20.sum(axis = 0, skipna = True)
        P65= Somme_P65.values[0]
        M20=Somme_M20.values[0]
        IV = round((M20/P65)*100,2)
        df_reg = pd.DataFrame(data=IV, columns = ['Indice de jeunesse en ' + annee], index = [nom_region])
        return df_reg

    #si année de 2017 à ... (inclus)
    def IV_region_P2017(fichier, region, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_regions = pd.merge(df[['COM', 'P' + year +'_POP0019', 'P' + year + '_POP65P']], communes_select[['COM','REG']],  on='COM', how='left')
        df_region = df_regions.loc[df_regions["REG"]==region, ['REG', 'COM','P'+ year +'_POP0019' , 'P'+ year + '_POP65P']]
        Plus_de_65 = df_region.loc[:, 'P'+ year + '_POP65P']
        Moins_de_20 = df_region.loc[:, 'P'+ year + '_POP0019']
        df_P65 = pd.DataFrame(data=Plus_de_65)
        df_M20 = pd.DataFrame(data=Moins_de_20)
        Somme_P65 = df_P65.sum(axis = 0, skipna = True)
        Somme_M20 = df_M20.sum(axis = 0, skipna = True)
        P65= Somme_P65.values[0]
        M20=Somme_M20.values[0]
        IV = round((M20/P65)*100,2)
        df_reg = pd.DataFrame(data=IV, columns = ['Indice de jeunesse en ' + annee], index = [nom_region])
        return df_reg

    if int(last_year) < 2017:
        valeurs_reg_iv = IV_region_M2017("./population/base-ic-evol-struct-pop-" + last_year + ".csv",code_region,last_year)
    else :
        valeurs_reg_iv = IV_region_P2017("./population/base-ic-evol-struct-pop-" + last_year + ".csv",code_region,last_year)

    # France
    def IV_France(fichier, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        Plus_de_65 = df.loc[:, 'P'+ year + '_POP65P']
        Moins_de_20 = df.loc[:, 'P'+ year + '_POP0019']
        df_P65 = pd.DataFrame(data=Plus_de_65)
        df_M20 = pd.DataFrame(data=Moins_de_20)
        Somme_P65 = df_P65.sum(axis = 0, skipna = True)
        Somme_M20 = df_M20.sum(axis = 0, skipna = True)
        P65= Somme_P65.values[0]
        M20=Somme_M20.values[0]
        IV = round((M20/P65)*100, 2)
        df_fr = pd.DataFrame(data=IV, columns = ['Indice de jeunesse en ' + annee], index = ["France"])
        return df_fr

    valeur_iv_fr = IV_France("./population/base-ic-evol-struct-pop-" + last_year + ".csv",last_year)

    # Comparaison
    def IV_global(annee):
        df = pd.concat([valeur_comiv,valeurs_ind_epci, valeurs_dep_iv, valeurs_reg_iv, valeur_iv_fr])
        year = annee
        return df

    pop_global = IV_global(last_year)
    st.table(pop_global)


  #################################
  st.header("Taux de 00-24 ans")
  st.subheader("Zoom QPV")

  #Année
  select_annee_0024 = st.select_slider(
       "Sélection de l'année",
       options=['2017', '2018', '2019', '2020', '2021', '2022'],
       value=('2022'),
       key="tx_0024_qpv")
  st.write('Mon année :', select_annee_0024)

  def tx_0024_qpv(fichier, nom_ville, annee) :
    fp_qpv = "./qpv.geojson"
    map_qpv_df = gpd.read_file(fp_qpv)
    year = annee[-2:]
    df = pd.read_csv(fichier, dtype={"CODGEO": str}, sep=";")
    map_qpv_df_code_insee = map_qpv_df.merge(df, left_on='code_qp', right_on='CODGEO')
    map_qpv_df_code_insee_extract = map_qpv_df_code_insee[['nom_qp', 'code_qp', 'commune_qp','code_insee', 'TX_TOT_0A24' ]]
    map_qpv_df_code_insee_extract
    df_qpv = map_qpv_df_code_insee_extract.loc[map_qpv_df_code_insee_extract["commune_qp"].str.contains(nom_ville + "(,|$)")]
    df_qpv = df_qpv.reset_index(drop=True)
    df_qpv = df_qpv[['code_qp', 'nom_qp','commune_qp', 'TX_TOT_0A24']]
    df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", 'TX_TOT_0A24' : "Taux des 00/24 ans " + select_annee_0024})
    return df_qpv

  tx_0024_qpv = tx_0024_qpv('./population/demographie_qpv/DEMO_' + select_annee_0024 + '.csv', nom_commune, select_annee_0024)
  st.table(tx_0024_qpv)

  ##################################
  st.subheader('2. Les NEET')
  st.caption("Paru le XX/XX/XXXX - Millésimes 2008-2009-2013-2014-2018-2020")
  st.caption("Un NEET (neither in employment nor in education or training) est une personne entre 16 et 25 ans qui n’est ni en emploi, ni en études, ni en formation (formelle ou non formelle).")
  #Année
  select_annee_neet = "2020"
  st.write('Mon année :', select_annee_neet)
  #Commune
  def neet_commune(fichier, nom_ville, annee) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_ville = df.loc[df["libgeo"] == nom_ville]
    df_ville = df_ville.loc[df_ville["an"] == annee]
    return df_ville
  neet_ville = neet_commune("./jeunesse/neet/commune/neet_commune_" + select_annee_neet + ".csv",nom_commune, select_annee_neet)
  #EPCI
  def neet_epci(fichier, epci, annee) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_epci = df.loc[df["codgeo"] == epci]
    df_epci = df_epci.loc[df_epci["an"] == annee]
    return df_epci
  neet_epci = neet_epci("./jeunesse/neet/epci/neet_epci_" + select_annee_neet + ".csv",code_epci, select_annee_neet)
  #Département
  def neet_departement(fichier, departement, annee) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_departement = df.loc[df["codgeo"] == departement]
    df_departement = df_departement.loc[df_departement["an"] == annee]
    return df_departement
  neet_dpt = neet_departement("./jeunesse/neet/departement/neet_dpt_" + select_annee_neet + ".csv",code_departement, select_annee_neet)
  #Région
  def neet_region(fichier, region, annee) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_region = df.loc[df["codgeo"] == region]
    df_region = df_region.loc[df_region["an"] == annee]
    return df_region
  neet_reg = neet_region("./jeunesse/neet/region/neet_region_" + select_annee_neet + ".csv",code_region, select_annee_neet)
  #France
  data = {'codgeo':['1'],
          'libgeo':['France'],
          'an':[select_annee_neet],
          'part_non_inseres':['15,7']
          }
  neet_france = pd.DataFrame(data)

  #Global
  result = pd.concat([neet_ville,neet_epci, neet_dpt, neet_reg, neet_france])
  result = result.reset_index(drop=True)
  st.write(result)

  ###########
  st.header('2.Part des licenciés sportifs 0/14 ans')
  select_annee_sport_0014 = "2019"
  #Commune
  def tx_licence_sport_0_14_commune(fichier, nom_ville) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_ville = df.loc[df["libgeo"] == nom_ville]
    return df_ville
  tx_lic_sport_0_14_ville = tx_licence_sport_0_14_commune("./sante/sport/sport_0014/commune/licsport_0014_commune_" + select_annee_sport_0014 +".csv",nom_commune)

  #EPCI
  def tx_licence_sport_0_14_epci(fichier, epci) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_epci = df.loc[df["codgeo"] == epci]
    return df_epci
  tx_lic_sport_0_14_epci = tx_licence_sport_0_14_epci("./sante/sport/sport_0014/epci/licsport_0014_epci_" + select_annee_sport_0014 +".csv",code_epci)

  #Département
  def tx_licence_sport_0_14_departement(fichier, departement, annee) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_departement = df.loc[df["codgeo"] == departement]
    df_departement = df_departement.loc[df_departement["an"] == annee]
    return df_departement
  tx_lic_sport_0_14_dpt = tx_licence_sport_0_14_departement("./sante/sport/sport_0014/departement/licsport_0014_departement_" + select_annee_sport_0014 +".csv",code_departement, select_annee_sport_0014)

  #Région
  def tx_licence_sport_0_14_region(fichier, region, annee) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_region = df.loc[df["codgeo"] == region]
    df_region = df_region.loc[df_region["an"] == annee]
    return df_region
  tx_lic_sport_0_14_reg = tx_licence_sport_0_14_region("./sante/sport/sport_0014/region/licsport_0014_region_" + select_annee_sport_0014 +".csv",code_region, select_annee_sport_0014)

  #France
  data = {'codgeo':['1'],
          'libgeo':['France'],
          'an':[select_annee_sport_0014],
          'p_licsport014':['47,9']
          }
  tx_lic_sport_0_14_france = pd.DataFrame(data)

  #Global
  result = pd.concat([tx_lic_sport_0_14_ville,tx_lic_sport_0_14_epci, tx_lic_sport_0_14_dpt, tx_lic_sport_0_14_reg, tx_lic_sport_0_14_france])
  result = result.reset_index(drop=True)
  st.write(result)


  ###############################
  st.header('3.Part des filles parmi les licenciés sportifs de 0-14 ans')

  #Commune
  def tx_licence_sport_0_14_filles_commune(fichier, nom_ville) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_ville = df.loc[df["libgeo"] == nom_ville]
    return df_ville
  tx_lic_sport_0_14_filles_ville = tx_licence_sport_0_14_filles_commune("./sante/sport/sport_0014_filles/commune/licsport_0014_filles_commune_" + select_annee_sport_0014 + ".csv",nom_commune)

  #EPCI
  def tx_licence_sport_0_14_filles_epci(fichier, epci) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_epci = df.loc[df["codgeo"] == epci]
    return df_epci
  tx_lic_sport_0_14_filles_epci = tx_licence_sport_0_14_filles_epci("./sante/sport/sport_0014_filles/epci/licsport_0014_filles_epci_" + select_annee_sport_0014 + ".csv",code_epci)

  #Département
  def tx_licence_sport_0_14_filles_departement(fichier, departement,annee) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_departement = df.loc[df["codgeo"] == departement]
    df_departement = df_departement.loc[df_departement["an"] == annee]
    return df_departement
  tx_lic_sport_0_14_filles_dpt = tx_licence_sport_0_14_filles_departement("./sante/sport/sport_0014_filles/departement/licsport_0014_filles_departement_" + select_annee_sport_0014 + ".csv",code_departement, select_annee_sport_0014)

  #Région
  def tx_licence_sport_0_14_filles_region(fichier, region,annee) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_region = df.loc[df["codgeo"] == region]
    df_region = df_region.loc[df_region["an"] == annee]
    return df_region
  tx_lic_sport_0_14_filles_reg = tx_licence_sport_0_14_filles_region("./sante/sport/sport_0014_filles/region/licsport_0014_filles_region_" + select_annee_sport_0014 + ".csv",code_region, select_annee_sport_0014)

  #France
  data = {'codgeo':['1'],
          'libgeo':['France'],
          'an':[select_annee_sport_0014],
          'p_licsport014_f':['40,2']
          }
  tx_lic_sport_0_14_filles_france = pd.DataFrame(data)

  #Global
  result = pd.concat([tx_lic_sport_0_14_filles_ville,tx_lic_sport_0_14_filles_epci, tx_lic_sport_0_14_filles_dpt, tx_lic_sport_0_14_filles_reg, tx_lic_sport_0_14_filles_france])
  result = result.reset_index(drop=True)
  st.write(result)


