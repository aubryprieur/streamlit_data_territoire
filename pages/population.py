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

  ##########################################################################
  st.header('2.Personnes immigrées')
  st.caption("Selon la définition adoptée par le Haut Conseil à l’Intégration, un immigré est une personne née étrangère à l’étranger et résidant en France. Les personnes nées françaises à l’étranger et vivant en France ne sont donc pas comptabilisées. À l’inverse, certains immigrés ont pu devenir français, les autres restant étrangers. Les populations étrangère et immigrée ne se confondent pas totalement : un immigré n’est pas nécessairement étranger et réciproquement, certains étrangers sont nés en France (essentiellement des mineurs). La qualité d’immigré est permanente : un individu continue à appartenir à la population immigrée même s’il devient français par acquisition. C’est le pays de naissance, et non la nationalité à la naissance, qui définit l'origine géographique d’un immigré.")
  @st.cache()
  def part_pers_imm_iris(fichier, ville, annee) :
      df = pd.read_csv(fichier, dtype={"IRIS": str , "COM": str},sep=";")
      year = annee[-2:]
      df_ville = df.loc[df["COM"]== ville]
      df_ville = df_ville.replace(',','.', regex=True)
      df_ville = df_ville[['IRIS','P'+ year + '_POP','P'+ year + '_POP_IMM' ]]
      df_ville['indice'] = np.where(df_ville['P' + year +'_POP'] < 1,df_ville['P' + year +'_POP'], (df_ville['P'+ year + '_POP_IMM'] / df_ville['P' + year +'_POP']*100))
      communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
      df_imm = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_ville[['IRIS','P' + year +'_POP', 'P' + year + '_POP_IMM','indice']], left_on='CODE_IRIS', right_on="IRIS")
      df_imm = df_imm[['IRIS','LIB_IRIS','P' + year +'_POP', 'P' + year + '_POP_IMM','indice']]
      df_imm = df_imm.rename(columns={'LIB_IRIS': "Nom de l'iris",'IRIS': "Code de l'iris", 'P' + year + '_POP' : 'Population', 'P' + year + '_POP_IMM' : "Personnes immigrées", 'indice' : "Part des personnes immigrées" })
      df_imm = df_imm.reset_index(drop=True)
      return df_imm
  indice_imm_iris = part_pers_imm_iris("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_commune, select_annee)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(indice_imm_iris)

  ##########################################################################
  st.header('2.Personnes étrangères')
  st.caption("Un étranger est une personne qui réside en France et ne possède pas la nationalité française, soit qu'elle possède une autre nationalité (à titre exclusif), soit qu'elle n'en ait aucune (c'est le cas des personnes apatrides). Les personnes de nationalité française possédant une autre nationalité (ou plusieurs) sont considérées en France comme françaises. Un étranger n'est pas forcément immigré, il peut être né en France (les mineurs notamment).")
  @st.cache()
  def part_pers_etr_iris(fichier, ville, annee) :
      df = pd.read_csv(fichier, dtype={"IRIS": str , "COM": str},sep=";")
      year = annee[-2:]
      df_ville = df.loc[df["COM"]== ville]
      df_ville = df_ville.replace(',','.', regex=True)
      df_ville = df_ville[['IRIS','P'+ year + '_POP','P'+ year + '_POP_ETR' ]]
      df_ville['indice'] = np.where(df_ville['P' + year +'_POP'] < 1,df_ville['P' + year +'_POP'], (df_ville['P'+ year + '_POP_ETR'] / df_ville['P' + year +'_POP']*100))
      communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
      df_etr = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_ville[['IRIS','P' + year +'_POP', 'P' + year + '_POP_ETR','indice']], left_on='CODE_IRIS', right_on="IRIS")
      df_etr = df_etr[['IRIS','LIB_IRIS','P' + year +'_POP', 'P' + year + '_POP_ETR','indice']]
      df_etr = df_etr.rename(columns={'LIB_IRIS': "Nom de l'iris",'IRIS': "Code de l'iris", 'P' + year + '_POP' : 'Population', 'P' + year + '_POP_ETR' : "Personnes étrangères", 'indice' : "Part des personnes étrangères" })
      df_etr = df_etr.reset_index(drop=True)
      return df_etr
  indice_etr_iris = part_pers_etr_iris("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_commune, select_annee)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(indice_etr_iris)



