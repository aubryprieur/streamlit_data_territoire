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
  st.title("Logement")

  #variables
  #P17_RP : nombre de résidences principales
  #C17_RP_HSTU1P_SUROCC : nombre de résidences principales (hors studio de 1 personne) en suroccupation
  #P17_RP_PROP : nombre de résidences principales occupées par des propriétaires
  #P17_RP_LOC : nombre de résidences principales occupées par des locataires
  #P17_RP_LOCHLMV : nombre de résidences principales HLM loué vide
  #P17_RP_GRAT : nombre de résidences principales occupées gratuitement
  #IRIS
  #REG
  #DEP
  #COM
  #LIBIRIS


  st.header('1.Part des logements HLM')

  st.subheader("Iris")
  def part_log_hlm_iris(fichier, code, annee) :
    df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, sep=";")
    df_indice = df.loc[df['COM'] == code]
    year = annee[-2:]
    df_indice = df_indice[['COM','IRIS', 'P'+ year + '_RP','P' + year +'_RP_LOCHLMV' ]]
    df_indice['P'+ year + '_RP'] = df_indice['P'+ year + '_RP'].astype(float).to_numpy()
    df_indice['P' + year +'_RP_LOCHLMV'] = df_indice['P' + year +'_RP_LOCHLMV'].astype(float).to_numpy()
    df_indice['indice'] = np.where(df_indice['P' + year +'_RP'] < 1,df_indice['P' + year +'_RP'], (df_indice['P'+ year + '_RP_LOCHLMV'] / df_indice['P' + year +'_RP']*100))
    df_indice['indice'] = df_indice['indice'].astype(float).to_numpy()
    communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
    df_indice_com = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_indice[['IRIS','P' + year +'_RP', 'P' + year + '_RP_LOCHLMV','indice']], left_on='CODE_IRIS', right_on="IRIS")
    df_indice_com = df_indice_com[['CODE_IRIS','LIB_IRIS','P' + year +'_RP', 'P' + year + '_RP_LOCHLMV','indice']]
    df_indice_com['indice'] = df_indice_com['indice'].apply(np.int64)
    df_indice_com['P' + year +'_RP'] = df_indice_com['P' + year +'_RP'].apply(np.int64)
    df_indice_com['P' + year +'_RP_LOCHLMV'] = df_indice_com['P' + year +'_RP_LOCHLMV'].apply(np.int64)
    df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_RP':"Résidences principales (" + select_annee + ")" ,'P' + year + '_RP_LOCHLMV':"résidences principales HLM loué vide (" + select_annee + ")" ,'indice':"Part des résidences principales HLM (" + select_annee + ")" })
    return df_indice_com

  indice_part_log_hlm_iris =part_log_hlm_iris("./logement/base-ic-logement-" + select_annee + ".csv",code_commune, select_annee)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(indice_part_log_hlm_iris)

  st.subheader('Comparaison')
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    # Commune
    def part_hlm_com(fichier, code_commune, annee):
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, sep = ';')
      year = annee[-2:]
      df_ville = df.loc[df["COM"]==code_commune]
      nb_residences_princ = df_ville.loc[:, 'P'+ year + '_RP'].sum()
      nb_residences_hlm = (df_ville.loc[:, 'P'+ year + '_RP_LOCHLMV'].sum())
      part_hlm = (nb_residences_hlm / nb_residences_princ)*100
      df_part_hlm = pd.DataFrame(data=part_hlm, columns = ['Part des hlm ' + annee], index = [nom_commune])
      return df_part_hlm
    indice_part_hlm_com = part_hlm_com("./logement/base-ic-logement-" + select_annee + ".csv",code_commune, select_annee)

    # EPCI
    def part_hlm_epci(fichier, epci, annee):
      epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
      df = pd.read_csv(fichier, dtype={"IRIS": str, "TYP_IRIS": str, "MODIF_IRIS": str,"COM": str, "LAB_IRIS": str, "DEP": str, "UU2010": str, "GRD_QUART": str}, encoding= 'unicode_escape', sep = ';')
      year = annee[-2:]
      df_epci_com = pd.merge(df[['COM', 'P' + year + '_RP', 'P' + year + '_RP_LOCHLMV']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
      df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM','P'+ year +'_RP' , 'P'+ year + '_RP_LOCHLMV']]
      nb_residences = df_epci.loc[:, 'P'+ year + '_RP'].sum()
      nb_residences_hlm = df_epci.loc[:, 'P'+ year + '_RP_LOCHLMV'].sum()
      part_hlm = (nb_residences_hlm / nb_residences)*100
      df_part_hlm = pd.DataFrame(data=part_hlm, columns = ['Part des hlm ' + annee], index = [nom_epci])
      return df_part_hlm
    indice_part_hlm_epci = part_hlm_epci("./logement/base-ic-logement-" + select_annee + ".csv",code_epci,select_annee)

    # Département
    def part_hlm_departement(fichier, departement, annee):
      if int(annee) >= 2017:
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str},sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_dpt = pd.merge(df[['COM', 'P' + year +'_RP', 'P' + year + '_RP_LOCHLMV']], communes_select[['COM','DEP']],  on='COM', how='left')
        df_departement = df_dpt.loc[df_dpt["DEP"]==departement, ['DEP', 'COM','P'+ year +'_RP' , 'P'+ year + '_RP_LOCHLMV']]
        nb_residences = df_departement.loc[:, 'P'+ year + '_RP'].sum()
        nb_residences_hlm = df_departement.loc[:, 'P'+ year + '_RP_LOCHLMV'].sum()
        part_hlm = (nb_residences_hlm / nb_residences)*100
        df_part_hlm = pd.DataFrame(data=part_hlm, columns = ["Part des hlm " + annee], index = [nom_departement])
        return df_part_hlm
      else:
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str},sep = ';')
        year = annee[-2:]
        df_departement = df.loc[df["DEP"]==departement, ['P' + year + '_RP' , 'P' + year + '_RP_LOCHLMV']]
        nb_residences = df_departement.loc[:, 'P' + year + '_RP'].sum()
        nb_residences_hlm = df_departement.loc[:, 'P'+ year + '_RP_LOCHLMV'].sum()
        part_hlm = (nb_residences_hlm / nb_residences)*100
        df_part_hlm = pd.DataFrame(data=part_hlm, columns = ['Part des hlm ' + annee], index = [nom_departement])
        return df_part_hlm
    indice_part_hlm_dpt =part_hlm_departement("./logement/base-ic-logement-" + select_annee + ".csv",code_departement, select_annee)

      # Région
    def part_hlm_region(fichier, region, annee):
      if int(annee) >= 2017:
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str},sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_region = pd.merge(df[['COM', 'P' + year +'_RP', 'P' + year + '_RP_LOCHLMV']], communes_select[['COM','REG']],  on='COM', how='left')
        df_region = df_region.loc[df_region["REG"]==region, ['REG', 'COM','P'+ year +'_RP' , 'P'+ year + '_RP_LOCHLMV']]
        nb_residences = df_region.loc[:, 'P'+ year + '_RP'].sum()
        nb_residences_hlm = df_region.loc[:, 'P'+ year + '_RP_LOCHLMV'].sum()
        part_hlm = (nb_residences_hlm / nb_residences)*100
        df_part_hlm = pd.DataFrame(data=part_hlm, columns = ["Part des hlm " + annee], index = [nom_region])
        return df_part_hlm
      else:
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str},sep = ';')
        year = annee[-2:]
        df_region = df.loc[df["REG"]==region, ['P' + year + '_RP' , 'P' + year + '_RP_LOCHLMV']]
        nb_residences = df_region.loc[:, 'P' + year + '_RP'].sum()
        nb_residences_hlm = df_region.loc[:, 'P'+ year + '_RP_LOCHLMV'].sum()
        part_hlm = (nb_residences_hlm / nb_residences)*100
        df_part_hlm = pd.DataFrame(data=part_hlm, columns = ['Part des hlm ' + annee], index = [nom_region])
        return df_part_hlm
    indice_part_hlm_region =part_hlm_region("./logement/base-ic-logement-" + select_annee + ".csv",code_region, select_annee)

      # France
    def part_hlm_france(fichier, annee):
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
      year = annee[-2:]
      nb_residences = df.loc[:, 'P'+ year + '_RP'].sum()
      nb_residences_hlm = df.loc[:, 'P'+ year + '_RP_LOCHLMV'].sum()
      part_hlm = ( nb_residences_hlm / nb_residences ) * 100
      df_part_hlm = pd.DataFrame(data=part_hlm, columns = ["Part des hlm " + annee], index = ["France"])
      return df_part_hlm
    indice_part_hlm_fr = part_hlm_france("./logement/base-ic-logement-" + select_annee + ".csv",select_annee)

    # Comparaison
    def part_hlm_global(annee):
        df = pd.concat([indice_part_hlm_com,indice_part_hlm_epci, indice_part_hlm_dpt, indice_part_hlm_region, indice_part_hlm_fr])
        year = annee
        return df

    part_hlm_fin = part_hlm_global(select_annee)
    st.table(part_hlm_fin)

  st.subheader("b.Evolution")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    #FRANCE
    #2014
    valeur_part_hlm_fr_2014 = part_hlm_france("./logement/base-ic-logement-2014.csv",'2014')
    indice_2014 = valeur_part_hlm_fr_2014["Part des hlm 2014"][0]
    #2015
    valeur_part_hlm_fr_2015 = part_hlm_france("./logement/base-ic-logement-2015.csv",'2015')
    indice_2015 = valeur_part_hlm_fr_2015["Part des hlm 2015"][0]
    #2016
    valeur_part_hlm_fr_2016 = part_hlm_france("./logement/base-ic-logement-2016.csv",'2016')
    indice_2016 = valeur_part_hlm_fr_2016["Part des hlm 2016"][0]
    #2017
    valeur_part_hlm_fr_2017 = part_hlm_france("./logement/base-ic-logement-2017.csv",'2017')
    indice_2017 = valeur_part_hlm_fr_2017["Part des hlm 2017"][0]
    #2018
    valeur_part_hlm_fr_2018 = part_hlm_france("./logement/base-ic-logement-2018.csv",'2018')
    indice_2018 = valeur_part_hlm_fr_2018["Part des hlm 2018"][0]
    df_france_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=['France'])

    #RÉGION
    #2014
    valeur_part_hlm_region_2014 = part_hlm_region("./logement/base-ic-logement-2014.csv",code_region,'2014')
    indice_2014 = valeur_part_hlm_region_2014["Part des hlm 2014"][0]
    #2015
    valeur_part_hlm_region_2015 = part_hlm_region("./logement/base-ic-logement-2015.csv",code_region,'2015')
    indice_2015 = valeur_part_hlm_region_2015["Part des hlm 2015"][0]
    #2016
    valeur_part_hlm_region_2016 = part_hlm_region("./logement/base-ic-logement-2016.csv",code_region,'2016')
    indice_2016 = valeur_part_hlm_region_2016["Part des hlm 2016"][0]
    #2017
    valeur_part_hlm_region_2017 = part_hlm_region("./logement/base-ic-logement-2017.csv",code_region,'2017')
    indice_2017 = valeur_part_hlm_region_2017["Part des hlm 2017"][0]
    #2018
    valeur_part_hlm_region_2018 = part_hlm_region("./logement/base-ic-logement-2018.csv",code_region,'2018')
    indice_2018 = valeur_part_hlm_region_2018["Part des hlm 2018"][0]
    indice_2018
    df_region_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_region])

    #DÉPARTEMENT
    #2014
    valeur_part_hlm_departement_2014 = part_hlm_departement("./logement/base-ic-logement-2014.csv",code_departement,'2014')
    indice_2014 = valeur_part_hlm_departement_2014["Part des hlm 2014"][0]
    #2015
    valeur_part_hlm_departement_2015 = part_hlm_departement("./logement/base-ic-logement-2015.csv",code_departement,'2015')
    indice_2015 = valeur_part_hlm_departement_2015["Part des hlm 2015"][0]
    #2016
    valeur_part_hlm_departement_2016 = part_hlm_departement("./logement/base-ic-logement-2016.csv",code_departement,'2016')
    indice_2016 = valeur_part_hlm_departement_2016["Part des hlm 2016"][0]
    #2017
    valeur_part_hlm_departement_2017 = part_hlm_departement("./logement/base-ic-logement-2017.csv",code_departement,'2017')
    indice_2017 = valeur_part_hlm_departement_2017["Part des hlm 2017"][0]
    #2018
    valeur_part_hlm_departement_2018 = part_hlm_departement("./logement/base-ic-logement-2018.csv",code_departement,'2018')
    indice_2018 = valeur_part_hlm_departement_2018["Part des hlm 2018"][0]

    df_departement_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_departement])

    #EPCI
    #2014
    valeur_part_hlm_epci_2014 = part_hlm_epci("./logement/base-ic-logement-2014.csv",code_epci,'2014')
    indice_2014 = valeur_part_hlm_epci_2014["Part des hlm 2014"][0]
    #2015
    valeur_part_hlm_epci_2015 = part_hlm_epci("./logement/base-ic-logement-2015.csv",code_epci,'2015')
    indice_2015 = valeur_part_hlm_epci_2015["Part des hlm 2015"][0]
    #2016
    valeur_part_hlm_epci_2016 = part_hlm_epci("./logement/base-ic-logement-2016.csv",code_epci,'2016')
    indice_2016 = valeur_part_hlm_epci_2016["Part des hlm 2016"][0]
    #2017
    valeur_part_hlm_epci_2017 = part_hlm_epci("./logement/base-ic-logement-2017.csv",code_epci,'2017')
    indice_2017 = valeur_part_hlm_epci_2017["Part des hlm 2017"][0]
    #2018
    valeur_part_hlm_epci_2018 = part_hlm_epci("./logement/base-ic-logement-2018.csv",code_epci,'2018')
    indice_2018 = valeur_part_hlm_epci_2018["Part des hlm 2018"][0]

    df_epci_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_epci])

    #COMMUNE
    #2014
    valeur_part_hlm_commune_2014 = part_hlm_com("./logement/base-ic-logement-2014.csv",code_commune,'2014')
    indice_2014 = valeur_part_hlm_commune_2014["Part des hlm 2014"][0]
    #2015
    valeur_part_hlm_commune_2015 = part_hlm_com("./logement/base-ic-logement-2015.csv",code_commune,'2015')
    indice_2015 = valeur_part_hlm_commune_2015["Part des hlm 2015"][0]
    #2016
    valeur_part_hlm_commune_2016 = part_hlm_com("./logement/base-ic-logement-2016.csv",code_commune,'2016')
    indice_2016 = valeur_part_hlm_commune_2016["Part des hlm 2016"][0]
    #2017
    valeur_part_hlm_commune_2017 = part_hlm_com("./logement/base-ic-logement-2017.csv",code_commune,'2017')
    indice_2017 = valeur_part_hlm_commune_2017["Part des hlm 2017"][0]
    #2018
    valeur_part_hlm_commune_2018 = part_hlm_com("./logement/base-ic-logement-2018.csv",code_commune,'2018')
    indice_2018 = valeur_part_hlm_commune_2018["Part des hlm 2018"][0]

    df_commune_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_commune])

    df_glob_part_hlm = pd.concat([df_france_glob, df_region_glob, df_departement_glob, df_epci_glob, df_commune_glob])

    st.table(df_glob_part_hlm)

    df_glob_part_hlm_transposed = df_glob_part_hlm.T
    st.line_chart(df_glob_part_hlm_transposed)

  st.header('1.Part des résidences principales en suroccupation')

  st.subheader("Iris")
  def part_log_suroccup_iris(fichier, code, annee) :
    if int(annee) >= 2017:
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, sep=";")
      df_indice = df.loc[df['COM'] == code]
      year = annee[-2:]
      df_indice = df_indice[['COM','IRIS', 'P'+ year + '_RP','C' + year +'_RP_HSTU1P_SUROCC' ]]
      df_indice['P'+ year + '_RP'] = df_indice['P'+ year + '_RP'].astype(float).to_numpy()
      df_indice['C' + year +'_RP_HSTU1P_SUROCC'] = df_indice['C' + year +'_RP_HSTU1P_SUROCC'].astype(float).to_numpy()
      df_indice['indice'] = np.where(df_indice['P' + year +'_RP'] < 1,df_indice['P' + year +'_RP'], (df_indice['C'+ year + '_RP_HSTU1P_SUROCC'] / df_indice['P' + year +'_RP']*100))
      df_indice['indice'] = df_indice['indice'].astype(float).to_numpy()
      communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
      df_indice_com = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_indice[['IRIS','P' + year +'_RP', 'C' + year + '_RP_HSTU1P_SUROCC','indice']], left_on='CODE_IRIS', right_on="IRIS")
      df_indice_com = df_indice_com[['CODE_IRIS','LIB_IRIS','P' + year +'_RP', 'C' + year + '_RP_HSTU1P_SUROCC','indice']]
      df_indice_com['indice'] = df_indice_com['indice'].apply(np.int64)
      df_indice_com['P' + year +'_RP'] = df_indice_com['P' + year +'_RP'].apply(np.int64)
      df_indice_com['C' + year +'_RP_HSTU1P_SUROCC'] = df_indice_com['C' + year +'_RP_HSTU1P_SUROCC'].apply(np.int64)
      df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_RP':"Résidences principales (" + select_annee + ")" ,'P' + year + '_RP_HSTU1P_SUROCC':"résidences principales en suroccupation (" + select_annee + ")" ,'indice':"Part des résidences en suroccupation (" + select_annee + ")" })
      return df_indice_com

  if int(select_annee) >= 2017:
    indice_part_log_suroccup_iris =part_log_suroccup_iris("./logement/base-ic-logement-" + select_annee + ".csv",code_commune, select_annee)
    with st.expander("Visualiser le tableau des iris"):
      st.dataframe(indice_part_log_suroccup_iris)
  else:
    st.write("Pas de données des résidences en suroccupation pour l'année sélectionnée")


  st.subheader('Comparaison')
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    # Commune
    def part_suroccup_com(fichier, code_commune, annee):
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, sep = ';')
      year = annee[-2:]
      df_ville = df.loc[df["COM"]==code_commune]
      nb_residences_princ = df_ville.loc[:, 'P'+ year + '_RP'].sum()
      nb_residences_suroccup = (df_ville.loc[:, 'C'+ year + '_RP_HSTU1P_SUROCC'].sum())
      part_suroccup = (nb_residences_suroccup / nb_residences_princ)*100
      df_part_suroccup = pd.DataFrame(data=part_suroccup, columns = ['Part des suroccup ' + annee], index = [nom_commune])
      return df_part_suroccup
    if int(select_annee) >= 2017:
      indice_part_suroccup_com = part_suroccup_com("./logement/base-ic-logement-" + select_annee + ".csv",code_commune, select_annee)

    # EPCI
    def part_suroccup_epci(fichier, epci, annee):
      epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
      df = pd.read_csv(fichier, dtype={"IRIS": str, "TYP_IRIS": str, "MODIF_IRIS": str,"COM": str, "LAB_IRIS": str, "DEP": str, "UU2010": str, "GRD_QUART": str}, encoding= 'unicode_escape', sep = ';')
      year = annee[-2:]
      df_epci_com = pd.merge(df[['COM', 'P' + year + '_RP', 'C' + year + '_RP_HSTU1P_SUROCC']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
      df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM','P'+ year +'_RP' , 'C'+ year + '_RP_HSTU1P_SUROCC']]
      nb_residences = df_epci.loc[:, 'P'+ year + '_RP'].sum()
      nb_residences_suroccup = df_epci.loc[:, 'C'+ year + '_RP_HSTU1P_SUROCC'].sum()
      part_suroccup = (nb_residences_suroccup / nb_residences)*100
      df_part_suroccup = pd.DataFrame(data=part_suroccup, columns = ['Part des suroccup ' + annee], index = [nom_epci])
      return df_part_suroccup
    if int(select_annee) >= 2017:
      indice_part_suroccup_epci = part_suroccup_epci("./logement/base-ic-logement-" + select_annee + ".csv",code_epci,select_annee)

    # Département
    def part_suroccup_departement(fichier, departement, annee):
      if int(annee) >= 2017:
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str},sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_dpt = pd.merge(df[['COM', 'P' + year +'_RP', 'C' + year + '_RP_HSTU1P_SUROCC']], communes_select[['COM','DEP']],  on='COM', how='left')
        df_departement = df_dpt.loc[df_dpt["DEP"]==departement, ['DEP', 'COM','P'+ year +'_RP' , 'C'+ year + '_RP_HSTU1P_SUROCC']]
        nb_residences = df_departement.loc[:, 'P'+ year + '_RP'].sum()
        nb_residences_suroccup = df_departement.loc[:, 'C'+ year + '_RP_HSTU1P_SUROCC'].sum()
        part_suroccup = (nb_residences_suroccup / nb_residences)*100
        df_part_suroccup = pd.DataFrame(data=part_suroccup, columns = ["Part des suroccup " + annee], index = [nom_departement])
        return df_part_suroccup
    if int(select_annee) >= 2017:
      indice_part_suroccup_dpt =part_suroccup_departement("./logement/base-ic-logement-" + select_annee + ".csv",code_departement, select_annee)

      # Région
    def part_suroccup_region(fichier, region, annee):
      communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str},sep = ',')
      df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
      year = annee[-2:]
      df_region = pd.merge(df[['COM', 'P' + year +'_RP', 'C' + year + '_RP_HSTU1P_SUROCC']], communes_select[['COM','REG']],  on='COM', how='left')
      df_region = df_region.loc[df_region["REG"]==region, ['REG', 'COM','P'+ year +'_RP' , 'C'+ year + '_RP_HSTU1P_SUROCC']]
      nb_residences = df_region.loc[:, 'P'+ year + '_RP'].sum()
      nb_residences_suroccup = df_region.loc[:, 'C'+ year + '_RP_HSTU1P_SUROCC'].sum()
      part_suroccup = (nb_residences_suroccup / nb_residences)*100
      df_part_suroccup = pd.DataFrame(data=part_suroccup, columns = ["Part des suroccup " + annee], index = [nom_region])
      return df_part_suroccup
    if int(select_annee) >= 2017:
      indice_part_suroccup_region = part_suroccup_region("./logement/base-ic-logement-" + select_annee + ".csv",code_region, select_annee)

    # France
    def part_suroccup_france(fichier, annee):
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
      year = annee[-2:]
      nb_residences = df.loc[:, 'P'+ year + '_RP'].sum()
      nb_residences_suroccup = df.loc[:, 'C'+ year + '_RP_HSTU1P_SUROCC'].sum()
      part_suroccup = ( nb_residences_suroccup / nb_residences ) * 100
      df_part_suroccup = pd.DataFrame(data=part_suroccup, columns = ["Part des suroccup " + annee], index = ["France"])
      return df_part_suroccup
    if int(select_annee) >= 2017:
      indice_part_suroccup_fr = part_suroccup_france("./logement/base-ic-logement-" + select_annee + ".csv",select_annee)

    # Comparaison
    def part_suroccup_global(annee):
        df = pd.concat([indice_part_suroccup_com,indice_part_suroccup_epci, indice_part_suroccup_dpt, indice_part_suroccup_region, indice_part_suroccup_fr])
        year = annee
        return df

    if int(select_annee) >= 2017:
      part_suroccup_fin = part_suroccup_global(select_annee)
      st.table(part_suroccup_fin)
    else:
      st.write("Pas de données sur les résidences principales suroccupées pour l'année sélectionnée")

  st.subheader("b.Evolution")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    #FRANCE
    #2017
    valeur_part_suroccup_fr_2017 = part_suroccup_france("./logement/base-ic-logement-2017.csv",'2017')
    indice_2017 = valeur_part_suroccup_fr_2017["Part des suroccup 2017"][0]
    #2018
    valeur_part_suroccup_fr_2018 = part_suroccup_france("./logement/base-ic-logement-2018.csv",'2018')
    indice_2018 = valeur_part_suroccup_fr_2018["Part des suroccup 2018"][0]
    df_france_glob = pd.DataFrame(np.array([[indice_2017, indice_2018]]),
                       columns=['2017', '2018'], index=['France'])

    #RÉGION
    #2017
    valeur_part_suroccup_region_2017 = part_suroccup_region("./logement/base-ic-logement-2017.csv",code_region,'2017')
    indice_2017 = valeur_part_suroccup_region_2017["Part des suroccup 2017"][0]
    #2018
    valeur_part_suroccup_region_2018 = part_suroccup_region("./logement/base-ic-logement-2018.csv",code_region,'2018')
    indice_2018 = valeur_part_suroccup_region_2018["Part des suroccup 2018"][0]
    indice_2018
    df_region_glob = pd.DataFrame(np.array([[indice_2017, indice_2018]]),
                       columns=['2017', '2018'], index=[nom_region])

    #DÉPARTEMENT
    #2017
    valeur_part_suroccup_departement_2017 = part_suroccup_departement("./logement/base-ic-logement-2017.csv",code_departement,'2017')
    indice_2017 = valeur_part_suroccup_departement_2017["Part des suroccup 2017"][0]
    #2018
    valeur_part_suroccup_departement_2018 = part_suroccup_departement("./logement/base-ic-logement-2018.csv",code_departement,'2018')
    indice_2018 = valeur_part_suroccup_departement_2018["Part des suroccup 2018"][0]

    df_departement_glob = pd.DataFrame(np.array([[indice_2017, indice_2018]]),
                       columns=['2017', '2018'], index=[nom_departement])

    #EPCI
    #2017
    valeur_part_suroccup_epci_2017 = part_suroccup_epci("./logement/base-ic-logement-2017.csv",code_epci,'2017')
    indice_2017 = valeur_part_suroccup_epci_2017["Part des suroccup 2017"][0]
    #2018
    valeur_part_suroccup_epci_2018 = part_suroccup_epci("./logement/base-ic-logement-2018.csv",code_epci,'2018')
    indice_2018 = valeur_part_suroccup_epci_2018["Part des suroccup 2018"][0]

    df_epci_glob = pd.DataFrame(np.array([[indice_2017, indice_2018]]),
                       columns=['2017', '2018'], index=[nom_epci])

    #COMMUNE
    #2017
    valeur_part_suroccup_commune_2017 = part_suroccup_com("./logement/base-ic-logement-2017.csv",code_commune,'2017')
    indice_2017 = valeur_part_suroccup_commune_2017["Part des suroccup 2017"][0]
    #2018
    valeur_part_suroccup_commune_2018 = part_suroccup_com("./logement/base-ic-logement-2018.csv",code_commune,'2018')
    indice_2018 = valeur_part_suroccup_commune_2018["Part des suroccup 2018"][0]

    df_commune_glob = pd.DataFrame(np.array([[indice_2017, indice_2018]]),
                       columns=['2017', '2018'], index=[nom_commune])

    df_glob_part_suroccup = pd.concat([df_france_glob, df_region_glob, df_departement_glob, df_epci_glob, df_commune_glob])

    st.table(df_glob_part_suroccup)

    df_glob_part_suroccup_transposed = df_glob_part_suroccup.T
    st.line_chart(df_glob_part_suroccup_transposed)
