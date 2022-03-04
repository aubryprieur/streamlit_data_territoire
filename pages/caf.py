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
       options=['2016', '2017', '2018','2019', '2020'],
       value=('2020'))
  st.sidebar.write('Mon année :', select_annee)

  #############################################################################
  st.title('ALLOCATAIRES CAF')

  df = pd.read_csv("./caf/iris/data_CAF_" + select_annee + "_IRIS.csv", dtype={"CODGEO": str, "DEPCOM": str,"EPCI": str, "REG": str}, sep=";")
  df = df.loc[df['CODGEO'].str.startswith(code_commune)]
  df = df[['CODGEO', 'AI', 'AM', 'ACSSENF', 'ACAVENF']]
  df = df.rename(columns={'CODGEO': "Code de l'iris",'AI': "Allocataires isolés sans enfant", 'AM':"Allocataires mono-parent" ,'ACSSENF':"Allocataires couples sans enfant",'ACAVENF':"Allocataires couples avec enfant(s)" })

  st.write(df)




  #   df_indice = df_indice[['COM','IRIS', 'P' + year + '_NSCOL15P_DIPLMIN', 'P' + year + '_NSCOL15P']]
  #   df_indice = df_indice.replace(',','.', regex=True)
  #   df_indice['P'+ year + '_NSCOL15P_DIPLMIN'] = df_indice['P'+ year + '_NSCOL15P_DIPLMIN'].astype(float).to_numpy()
  #   df_indice['P' + year +'_NSCOL15P'] = df_indice['P' + year +'_NSCOL15P'].astype(float).to_numpy()
  #   df_indice['indice'] = np.where(df_indice['P' + year +'_NSCOL15P'] < 1,df_indice['P' + year +'_NSCOL15P'], (df_indice['P'+ year + '_NSCOL15P_DIPLMIN']/ df_indice['P' + year +'_NSCOL15P']*100))
  #   df_indice['indice'] = df_indice['indice'].astype(float).to_numpy()
  #   communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
  #   df_indice_com = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_indice[['IRIS','P' + year +'_NSCOL15P', 'P' + year + '_NSCOL15P_DIPLMIN','indice']], left_on='CODE_IRIS', right_on="IRIS")
  #   df_indice_com = df_indice_com[['CODE_IRIS','LIB_IRIS','P' + year +'_NSCOL15P', 'P' + year + '_NSCOL15P_DIPLMIN','indice']]
  #   df_indice_com['P' + year +'_NSCOL15P'] = df_indice_com['P' + year +'_NSCOL15P'].apply(np.int64)
  #   df_indice_com['P' + year +'_NSCOL15P_DIPLMIN'] = df_indice_com['P' + year +'_NSCOL15P_DIPLMIN'].apply(np.int64)
  #   df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_NSCOL15P':"Personnes non scolarisées de 15 ans ou plus (" + select_annee + ")", 'P' + year +'_NSCOL15P_DIPLMIN':"Personnes non scolarisées de 15 ans ou plus titulaires d'aucun diplôme ou au plus un CEP (" + select_annee + ")" ,'indice':"Part des personnes non scolarisées sans diplôme (" + select_annee + ") en %" })
  #   return df_indice_com
  # indice_part_sans_diplome_iris =part_sans_diplome_iris("./caf/iris/data_CAF_" + select_annee + "_IRIS.csv",str(code_commune), select_annee)
  # with st.expander("Visualiser le tableau des iris"):
  #   st.dataframe(indice_part_sans_diplome_iris)
