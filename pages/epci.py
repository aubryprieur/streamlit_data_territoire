import streamlit as st
from .utils import afficher_infos_commune
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
import plotly.express as px

def app():
  # Appeler la fonction et récupérer les informations
  (code_commune, nom_commune, code_epci, nom_epci, code_departement, nom_departement, code_region, nom_region) = afficher_infos_commune()

  #############################################################################
  st.title('EPCI')
  ################################
  last_year = "2020"
  ################################

  st.subheader("Taux de pauvreté à 60% - 2020")
  #Commune
  df_pauv_com = pd.read_csv("./revenu/pauvrete/FILO2020_DISP_PAUVRES_COM.csv", dtype={"CODGEO": str},sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df_pauv_com, df_epci[['CODGEO', 'EPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci_com = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci_com = df_epci_com[['CODGEO', 'LIBGEO', 'TP6020', 'TP60Q220' ]]
  df_epci_com = df_epci_com.reset_index(drop=True)
  st.write(df_epci_com)
  ################################
  st.write("Page reprenant des données pour la mission Petite enfance EPCI.")
  ##############################

  st.header('1.Evolution de la population')
  df_pop_hist = pd.read_csv('./population/base-cc-serie-historique-2019.csv', dtype={"CODGEO": str},sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_pop_epci = pd.merge(df_pop_hist, df_epci[['CODGEO', 'EPCI']], left_on='CODGEO', right_on='CODGEO')
  df_pop_epci = df_pop_epci.loc[df_pop_epci["EPCI"] == str(code_epci)]
  df_pop_epci = df_pop_epci.reset_index(drop=True)
  df_pop_epci = df_pop_epci.loc[:, 'LIBGEO' : 'D68_POP']
  df_pop_epci = df_pop_epci.rename(columns={'P19_POP': '2019','P13_POP': '2013','P08_POP': '2008','D99_POP': '1999','D90_POP': '1990','D82_POP': '1982','D75_POP': '1975','D68_POP': '1968' })
  df_pop_epci = df_pop_epci[['LIBGEO', '1968', '1975', '1982', '1990', '1999', '2008', '2013', '2019' ]]
  st.write(df_pop_epci)
  ##################################

  st.header('Évolution annuelle moyenne de la population')
  #Solde migratoire
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_solde_migratoire = pd.read_csv('./population/solde/insee_rp_evol_1968_taux_migratoire.csv', dtype={"codgeo": str},sep=";")
  df_solde_migratoire_epci = pd.merge(df_solde_migratoire, df_epci[['CODGEO', 'EPCI']], left_on='codgeo', right_on='CODGEO')
  df_solde_migratoire_epci = df_solde_migratoire_epci.loc[df_solde_migratoire_epci["EPCI"]== str(code_epci)]
  df_solde_migratoire_epci = df_solde_migratoire_epci.reset_index(drop=True)
  df_solde_migratoire_epci = df_solde_migratoire_epci[["codgeo", "libgeo", "an", "tx_var_pop_part_sm"]]
  df_solde_migratoire_epci.rename(columns={"tx_var_pop_part_sm": "solde migratoire"}, inplace=True)
  #Solde naturel
  df_solde_naturel = pd.read_csv('./population/solde/insee_rp_evol_1968_taux_naturel.csv', dtype={"codgeo": str},sep=";")
  df_epci_solde_naturel = pd.merge(df_solde_naturel, df_epci[['CODGEO', 'EPCI']], left_on='codgeo', right_on='CODGEO')
  df_epci_solde_naturel = df_epci_solde_naturel.loc[df_epci_solde_naturel["EPCI"]== str(code_epci)]
  df_epci_solde_naturel = df_epci_solde_naturel.reset_index(drop=True)
  #Fusion solde naturel et migratoire
  df_solde_migratoire_epci["solde naturel"] = df_epci_solde_naturel["tx_var_pop_part_sn"]
  #Calcul variation population
  df_solde_migratoire_epci["solde naturel"] = df_solde_migratoire_epci["solde naturel"].str.replace(',','.')
  df_solde_migratoire_epci["solde migratoire"] = df_solde_migratoire_epci["solde migratoire"].str.replace(',','.')
  df_solde_migratoire_epci["solde migratoire"] = df_solde_migratoire_epci["solde migratoire"].astype(float)
  df_solde_migratoire_epci["solde naturel"] = df_solde_migratoire_epci["solde naturel"].astype(float)
  df_solde_migratoire_epci["variation population"] = df_solde_migratoire_epci["solde naturel"] + df_solde_migratoire_epci["solde migratoire"]
  st.write(df_solde_migratoire_epci)
  ###########################################################

  st.header('Population')
  df_pop_hist = pd.read_csv('./population/base-cc-serie-historique-2019.csv', dtype={"CODGEO": str},sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df_pop_hist, df_epci[['CODGEO', 'EPCI']], left_on='CODGEO', right_on='CODGEO')
  df_pop = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_pop = df_pop.reset_index()
  df_pop = df_pop[['CODGEO', 'LIBGEO', 'P19_POP']]
  st.table(df_pop)
  ###################################

  st.subheader("Types de famille selon le statut professionnel et l'âge des enfants")
  #Commune
  df = pd.read_csv("./famille/caf/BTX_TD_FAM6_2019.csv", dtype={"CODGEO": str, "LIBGEO": str},sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO', 'EPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci_com = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci_com = df_epci_com[['CODGEO', 'LIBGEO', 'AGEFOR500_TF1211','AGEFOR500_TF1212', 'AGEFOR500_TF1221', 'AGEFOR500_TF1222', 'AGEFOR500_TF1241', 'AGEFOR500_TF1242', 'AGEFOR500_TF1243', 'AGEFOR500_TF1244',
   'AGEFOR503_TF1211','AGEFOR503_TF1212', 'AGEFOR503_TF1221', 'AGEFOR503_TF1222', 'AGEFOR503_TF1241', 'AGEFOR503_TF1242', 'AGEFOR503_TF1243', 'AGEFOR503_TF1244']]
  df_epci_com = df_epci_com.reset_index(drop=True)
  st.write(df_epci_com)

  #pour les moins de 3 ans
  df_epci_com["FAM_MONO_ACTIF_EMPLOI_ENFANT00"] = df_epci_com["AGEFOR500_TF1211"] + df_epci_com["AGEFOR500_TF1221"]
  df_epci_com["FAM_MONO_AUTRE_ACTIF_EMPLOI_ENFANT00"] = df_epci_com["AGEFOR500_TF1212"] + df_epci_com["AGEFOR500_TF1222"]
  df_epci_com["COUPLE_ACTIF_EMPLOI_AUTRE_ACTIF_EMPLOI_ENFANT00"] = df_epci_com["AGEFOR500_TF1242"] + df_epci_com["AGEFOR500_TF1243"]

  df_epci_enfants00 = df_epci_com[['CODGEO','LIBGEO','FAM_MONO_ACTIF_EMPLOI_ENFANT00', 'FAM_MONO_AUTRE_ACTIF_EMPLOI_ENFANT00', 'COUPLE_ACTIF_EMPLOI_AUTRE_ACTIF_EMPLOI_ENFANT00', 'AGEFOR500_TF1241', 'AGEFOR500_TF1244']]
  df_epci_enfants00 = df_epci_enfants00.rename(columns={'AGEFOR500_TF1241': "COUPLE_ACTIF_EMPLOI_ENFANT00",'AGEFOR500_TF1244': "COUPLE_AUTRE_ACTIF_EMPLOI_ENFANT00" })
  st.write(df_epci_enfants00)

  fig = px.bar(df_epci_enfants00, x="LIBGEO", y=['FAM_MONO_ACTIF_EMPLOI_ENFANT00','FAM_MONO_AUTRE_ACTIF_EMPLOI_ENFANT00', 'COUPLE_ACTIF_EMPLOI_AUTRE_ACTIF_EMPLOI_ENFANT00', 'COUPLE_ACTIF_EMPLOI_ENFANT00', 'COUPLE_AUTRE_ACTIF_EMPLOI_ENFANT00'], title="Répartition des familles avec enfants de moins de 3 ans", height=600, width=1000)
  st.plotly_chart(fig, use_container_width=False)

  #pour les 3 à 5 ans
  df_epci_com["FAM_MONO_ACTIF_EMPLOI_ENFANT35"] = df_epci_com["AGEFOR503_TF1211"] + df_epci_com["AGEFOR503_TF1221"]
  df_epci_com["FAM_MONO_AUTRE_ACTIF_EMPLOI_ENFANT35"] = df_epci_com["AGEFOR503_TF1212"] + df_epci_com["AGEFOR503_TF1222"]
  df_epci_com["COUPLE_ACTIF_EMPLOI_AUTRE_ACTIF_EMPLOI_ENFANT35"] = df_epci_com["AGEFOR503_TF1242"] + df_epci_com["AGEFOR503_TF1243"]

  df_epci_enfants35 = df_epci_com[['CODGEO','LIBGEO','FAM_MONO_ACTIF_EMPLOI_ENFANT35', 'FAM_MONO_AUTRE_ACTIF_EMPLOI_ENFANT35', 'COUPLE_ACTIF_EMPLOI_AUTRE_ACTIF_EMPLOI_ENFANT35', 'AGEFOR503_TF1241', 'AGEFOR503_TF1244']]
  df_epci_enfants35 = df_epci_enfants35.rename(columns={'AGEFOR503_TF1241': "COUPLE_ACTIF_EMPLOI_ENFANT35",'AGEFOR503_TF1244': "COUPLE_AUTRE_ACTIF_EMPLOI_ENFANT35" })
  st.write(df_epci_enfants35)

  fig = px.bar(df_epci_enfants35, x="LIBGEO", y=['FAM_MONO_ACTIF_EMPLOI_ENFANT35','FAM_MONO_AUTRE_ACTIF_EMPLOI_ENFANT35', 'COUPLE_ACTIF_EMPLOI_AUTRE_ACTIF_EMPLOI_ENFANT35', 'COUPLE_ACTIF_EMPLOI_ENFANT35', 'COUPLE_AUTRE_ACTIF_EMPLOI_ENFANT35'], title="Répartition des familles avec enfants de 3 à 5 ans", height=600, width=1000)
  st.plotly_chart(fig, use_container_width=False)
  ##################################

  st.subheader("Allocataires CAF ressources à 100%")
  #Commune
  df_alloc_100_com = pd.read_csv("./revenu/caf/caf_alloc_100_com_2019.csv", dtype={"codgeo": str, "an": str},sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df_alloc_100_com, df_epci[['CODGEO', 'EPCI']], left_on='codgeo', right_on='CODGEO')
  df_epci_com = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci_com = df_epci_com.loc[df_epci_com["an"] == '2019']
  df_epci_com = df_epci_com[['codgeo', 'libgeo', 'part_alloc_100pct' ]]
  df_epci_com = df_epci_com.reset_index(drop=True)
  st.write(df_epci_com)

  #EPCI
  df_alloc_100_epci = pd.read_csv("./revenu/caf/caf_alloc_100_EPCI_2019.csv", dtype={"codgeo": str, "an": str},sep=";")
  df_epci = df_alloc_100_epci.loc[df_alloc_100_epci["codgeo"] == str(code_epci)]
  df_epci = df_epci.loc[df_epci["an"] == '2019']
  df_epci = df_epci[['codgeo', 'libgeo', 'part_alloc_100pct' ]]
  df_epci = df_epci.reset_index(drop=True)
  st.write(df_epci)
  #############################

  st.subheader("Taux de pauvreté à 60%")
  #Commune
  df_pauv_com = pd.read_csv("./revenu/pauvrete/FILO2019_DISP_PAUVRES_COM.csv", dtype={"CODGEO": str},sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df_pauv_com, df_epci[['CODGEO', 'EPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci_com = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci_com = df_epci_com[['CODGEO', 'LIBGEO', 'TP6019', 'TP60Q219' ]]
  df_epci_com = df_epci_com.reset_index(drop=True)
  st.write(df_epci_com)

  #Comparaison
  #EPCI
  df_pauv_epci = pd.read_csv("./revenu/pauvrete/FILO2019_DISP_PAUVRES_EPCI.csv", dtype={"CODGEO": str},sep=";")
  df_pauv_epci = df_pauv_epci.loc[df_pauv_epci["CODGEO"] == code_epci ]
  taux_pauvrete_epci = df_pauv_epci["TP6019"].values[0]
  #Département
  df_pauv_dep = pd.read_csv("./revenu/pauvrete/FILO2019_DISP_PAUVRES_DEP.csv", dtype={"CODGEO": str},sep=";")
  df_pauv_dep = df_pauv_dep.loc[df_pauv_dep["CODGEO"] == code_departement ]
  taux_pauvrete_dep = df_pauv_dep["TP6019"].values[0]
  #Région
  df_pauv_reg = pd.read_csv("./revenu/pauvrete/FILO2019_DISP_PAUVRES_REG.csv", dtype={"CODGEO": str},sep=";")
  df_pauv_reg = df_pauv_reg.loc[df_pauv_reg["CODGEO"] == str(code_region) ]
  taux_pauvrete_reg = df_pauv_reg["TP6019"].values[0]
  #France
  df_pauv_fr = pd.read_csv("./revenu/pauvrete/FILO2019_DISP_PAUVRES_METROPOLE.csv", dtype={"CODGEO": str},sep=";")
  taux_pauvrete_fr = df_pauv_fr["TP6019"].values[0]
  #Comparaison
  d = {'Territoires': [nom_epci, nom_departement, nom_region, 'France'], "Taux de pauvreté à 60% (2019) (en %)": [taux_pauvrete_epci, taux_pauvrete_dep, taux_pauvrete_reg, taux_pauvrete_fr]}
  df = pd.DataFrame(data=d)
  st.write(df)
  ############################

  # PAJE
  #Commune
  st.subheader("Paje")
  df = pd.read_csv("./famille/caf/PAJECOM.csv", dtype={'Codes_Insee': str}, sep = ';')
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO', 'LIBGEO', 'EPCI']], left_on='Codes_Insee', right_on='CODGEO')
  df_epci_com = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci_com = df_epci_com.loc[df_epci_com["DTREF"] == "31/12/2021"]
  df_epci_com = df_epci_com[["Communes", "Codes_Insee", "NB_Allocataires", "ALL_PAJE"]]
  df_epci_com['PART_ALL_PAJE'] = round((df_epci_com['ALL_PAJE'] / df_epci_com['NB_Allocataires']) * 100, 2)
  df_epci_com = df_epci_com.reset_index(drop=True)
  st.write(df_epci_com)

  #EPCI
  df_epci = pd.read_csv("./famille/caf/PAJEEPCI.csv", dtype={'NUMEPCI': str}, sep = ';')
  df_epci = df_epci.loc[df_epci["NUMEPCI"] == str(code_epci)]
  df_epci = df_epci.loc[df_epci["DTREF"] == "31/12/2021"]
  df_epci = df_epci[["NOMEPCI", "NUMEPCI", "NB_Allocataires", "ALL_PAJE"]]
  df_epci['PART_ALL_PAJE'] = round((df_epci['ALL_PAJE'] / df_epci['NB_Allocataires']) * 100, 2)
  df_epci = df_epci.reset_index(drop=True)
  st.write(df_epci)
  ################################

  # Familles monoparentales
  st.subheader("Familles monoparentales")
  df = pd.read_csv("./famille/commune/base-cc-coupl-fam-men-2019.csv", dtype={'CODGEO': str}, sep = ';')
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO', 'LIBGEO', 'EPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci_com = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci_com = df_epci_com[["CODGEO", "LIBGEO", "C19_FAM", "C19_FAMMONO"]]
  df_epci_com['PART_FAM_MONO'] = round((df_epci_com['C19_FAMMONO'] / df_epci_com['C19_FAM']) * 100, 2)
  df_epci_com = df_epci_com.reset_index(drop=True)
  st.write(df_epci_com)

  #Comparaison
  # EPCI
  def part_fam_mono_epci(fichier, epci, annee):
      epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
      df = pd.read_csv(fichier, dtype={"IRIS": str, "TYP_IRIS": str, "MODIF_IRIS": str,"COM": str, "LAB_IRIS": str, "DEP": str, "UU2010": str, "GRD_QUART": str}, encoding= 'unicode_escape', sep = ';')
      year = annee[-2:]
      df_epci_com = pd.merge(df[['COM', 'C' + year + '_FAM', 'C' + year + '_FAMMONO']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
      df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM','C'+ year +'_FAM' , 'C'+ year + '_FAMMONO']]
      familles = df_epci.loc[:, 'C'+ year + '_FAM']
      familles_mono = df_epci.loc[:, 'C'+ year + '_FAMMONO']
      df_familles = pd.DataFrame(data=familles)
      df_familles_mono = pd.DataFrame(data=familles_mono)
      Somme_familles = df_familles.sum(axis = 0, skipna = True)
      Somme_familles_mono = df_familles_mono.sum(axis = 0, skipna = True)
      val_familles = Somme_familles.values[0]
      val_familles_mono = Somme_familles_mono.values[0]
      part_familles_mono = round((val_familles_mono / val_familles)*100,2)
      df_Part_familles_mono = pd.DataFrame(data=part_familles_mono, columns = ['Part des familles monoparentales ' + annee], index = [nom_epci])
      return df_Part_familles_mono
  indice_fam_mono_epci = part_fam_mono_epci("./famille/base-ic-couples-familles-menages-" + last_year + ".csv",code_epci,last_year)

  # Département
  def part_fam_mono_departement_M2017(fichier, departement, annee):
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape',sep = ';')
      year = annee[-2:]
      df_departement = df.loc[df["DEP"]==departement, 'C'+ year +'_FAM' : 'C'+ year + '_FAMMONO']
      familles = df_departement.loc[:, 'C'+ year + '_FAM']
      familles_mono = df_departement.loc[:, 'C'+ year + '_FAMMONO']
      df_familles = pd.DataFrame(data=familles)
      df_familles_mono = pd.DataFrame(data=familles_mono)
      Somme_familles = df_familles.sum(axis = 0, skipna = True)
      Somme_familles_mono = df_familles_mono.sum(axis = 0, skipna = True)
      val_familles = Somme_familles.values[0]
      val_familles_mono = Somme_familles_mono.values[0]
      part_familles_mono = round((val_familles_mono / val_familles)*100,2)
      df_Part_familles_mono = pd.DataFrame(data=part_familles_mono, columns = ['Part des familles monoparentales ' + annee], index = [nom_departement])
      return df_Part_familles_mono

  def part_fam_mono_departement_P2017(fichier, departement, annee):
      communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, encoding= 'unicode_escape',sep = ',')
      df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
      year = annee[-2:]
      df_dpt = pd.merge(df[['COM', 'C' + year +'_FAM', 'C' + year + '_FAMMONO']], communes_select[['COM','DEP']],  on='COM', how='left')
      df_departement = df_dpt.loc[df_dpt["DEP"]==departement, ['DEP', 'COM','C'+ year +'_FAM' , 'C'+ year + '_FAMMONO']]
      familles = df_departement.loc[:, 'C'+ year + '_FAM']
      familles_mono = df_departement.loc[:, 'C'+ year + '_FAMMONO']
      df_familles = pd.DataFrame(data=familles)
      df_familles_mono = pd.DataFrame(data=familles_mono)
      Somme_familles = df_familles.sum(axis = 0, skipna = True)
      Somme_familles_mono = df_familles_mono.sum(axis = 0, skipna = True)
      val_familles = Somme_familles.values[0]
      val_familles_mono = Somme_familles_mono.values[0]
      part_familles_mono = round((val_familles_mono / val_familles)*100,2)
      df_Part_familles_mono = pd.DataFrame(data=part_familles_mono, columns = ['Part des familles monoparentales ' + annee], index = [nom_departement])
      return df_Part_familles_mono

  if int(select_annee) < 2017:
      valeurs_fam_mono_dep = part_fam_mono_departement_M2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_departement,select_annee)
  else :
      valeurs_fam_mono_dep = part_fam_mono_departement_P2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_departement,select_annee)

  # Région
  #si année de 2014 à 2016 (inclus)
  def part_fam_mono_region_M2017(fichier, region, annee):
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
      year = annee[-2:]
      df_regions = df.loc[df["REG"]==str(region), 'C'+ year +'_FAM' : 'C'+ year + '_FAMMONO']
      familles = df_regions.loc[:, 'C'+ year + '_FAM']
      familles_mono = df_regions.loc[:, 'C'+ year + '_FAMMONO']
      df_familles = pd.DataFrame(data=familles)
      df_familles_mono = pd.DataFrame(data=familles_mono)
      Somme_familles = df_familles.sum(axis = 0, skipna = True)
      Somme_familles_mono = df_familles_mono.sum(axis = 0, skipna = True)
      val_familles = Somme_familles.values[0]
      val_familles_mono = Somme_familles_mono.values[0]
      part_familles_mono = round((val_familles_mono / val_familles)*100,0)
      df_Part_familles_mono = pd.DataFrame(data=part_familles_mono, columns = ['Part des familles monoparentales ' + annee], index = [nom_region])
      return df_Part_familles_mono

  #si année de 2017 à ... (inclus)
  def part_fam_mono_region_P2017(fichier, region, annee):
      communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, encoding= 'unicode_escape', sep = ',')
      df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
      year = annee[-2:]
      df_regions = pd.merge(df[['COM', 'C' + year +'_FAM', 'C' + year + '_FAMMONO']], communes_select[['COM','REG']],  on='COM', how='left')
      df_region = df_regions.loc[df_regions["REG"]==str(region), ['REG', 'COM','C'+ year +'_FAM' , 'C'+ year + '_FAMMONO']]
      familles = df_region.loc[:, 'C'+ year + '_FAM']
      familles_mono = df_region.loc[:, 'C'+ year + '_FAMMONO']
      df_familles = pd.DataFrame(data=familles)
      df_familles_mono = pd.DataFrame(data=familles_mono)
      Somme_familles = df_familles.sum(axis = 0, skipna = True)
      Somme_familles_mono = df_familles_mono.sum(axis = 0, skipna = True)
      val_familles = Somme_familles.values[0]
      val_familles_mono =Somme_familles_mono.values[0]
      part_familles_mono = round((val_familles_mono / val_familles)*100,2)
      df_Part_familles_mono = pd.DataFrame(data=part_familles_mono, columns = ['Part des familles monoparentales ' + annee], index = [nom_region])
      return df_Part_familles_mono

  if int(select_annee) < 2017:
      valeurs_fam_mono_reg = part_fam_mono_region_M2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",str(round(code_region)),select_annee)
  else :
      valeurs_fam_mono_reg = part_fam_mono_region_P2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",str(round(code_region)),select_annee)

  # France
  def part_fam_mono_France(fichier, annee):
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
      year = annee[-2:]
      familles = df.loc[:, 'C'+ year + '_FAM']
      familles_mono = df.loc[:, 'C'+ year + '_FAMMONO']
      df_familles = pd.DataFrame(data=familles)
      df_familles_mono = pd.DataFrame(data=familles_mono)
      Somme_familles = df_familles.sum(axis = 0, skipna = True)
      Somme_familles_mono = df_familles_mono.sum(axis = 0, skipna = True)
      val_familles = Somme_familles.values[0]
      val_familles_mono = Somme_familles_mono.values[0]
      part_familles_mono = round((val_familles_mono / val_familles)*100, 2)
      df_Part_familles_mono = pd.DataFrame(data=part_familles_mono, columns = ['Part des familles monoparentales ' + annee], index = ["France"])
      return df_Part_familles_mono

  valeur_part_fam_mono_fr = part_fam_mono_France("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",select_annee)

  # Comparaison
  def fam_mono_global(annee):
      df = pd.concat([indice_fam_mono_epci, valeurs_fam_mono_dep, valeurs_fam_mono_reg, valeur_part_fam_mono_fr])
      year = annee
      return df

  fam_mono_fin = fam_mono_global(select_annee)
  st.table(fam_mono_fin)
  ################################

  # Familles nombreuses
  st.subheader("Familles nombreuses")
  df = pd.read_csv("./famille/commune/base-cc-coupl-fam-men-2019.csv", dtype={'CODGEO': str}, sep = ';')
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO', 'LIBGEO', 'EPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci_com = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci_com = df_epci_com[["CODGEO", "LIBGEO", "C19_FAM", "C19_NE24F3", "C19_NE24F4P"]]
  df_epci_com['FAM_NBREUSES'] = df_epci_com['C19_NE24F3'] + df_epci_com['C19_NE24F4P']
  df_epci_com['PART_FAM_NBREUSES'] = round((df_epci_com['FAM_NBREUSES'] / df_epci_com['C19_FAM']) * 100, 2)
  df_epci_com = df_epci_com.reset_index(drop=True)
  st.write(df_epci_com)

  #Comparaison
  # EPCI
  def part_fam_nombreuses_epci(fichier, epci, annee):
      epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
      df = pd.read_csv(fichier, dtype={"IRIS": str, "TYP_IRIS": str, "MODIF_IRIS": str,"COM": str, "LAB_IRIS": str, "DEP": str, "UU2010": str, "GRD_QUART": str}, encoding= 'unicode_escape', sep = ';')
      year = annee[-2:]
      df_epci_com = pd.merge(df[['COM', 'C' + year + '_FAM', 'C' + year + '_NE24F3', 'C' + year + '_NE24F4P']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
      df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM','C'+ year +'_FAM' , 'C'+ year + '_NE24F3' , 'C'+ year + '_NE24F4P']]
      familles = df_epci.loc[:, 'C'+ year + '_FAM'].sum(axis = 0, skipna = True)
      familles_nombreuses = (df_epci.loc[:, 'C'+ year + '_NE24F3'].astype(float).sum(axis = 0, skipna = True)) + (df_epci.loc[:, 'C'+ year + '_NE24F4P'].astype(float).sum(axis = 0, skipna = True))
      part_familles_nombreuses = round((familles_nombreuses / familles)*100,2)
      df_part_familles_nombreuses = pd.DataFrame(data=part_familles_nombreuses, columns = ['Part des familles nombreuses ' + annee], index = [nom_epci])
      return df_part_familles_nombreuses
  indice_fam_nombreuses_epci = part_fam_nombreuses_epci("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_epci,select_annee)

  # Département
  def part_fam_nombreuses_departement_M2017(fichier, departement, annee):
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape',sep = ';')
      year = annee[-2:]
      df_departement = df.loc[df["DEP"]==departement, 'C'+ year +'_FAM' : 'C'+ year + '_NE24F4P']
      familles = df_departement.loc[:, 'C'+ year + '_FAM'].sum(axis = 0, skipna = True)
      familles_nombreuses = (df_departement.loc[:, 'C'+ year + '_NE24F3'].astype(float).sum(axis = 0, skipna = True)) + (df_departement.loc[:, 'C'+ year + '_NE24F4P'].astype(float).sum(axis = 0, skipna = True))
      part_familles_nombreuses = round((familles_nombreuses / familles)*100,2)
      df_Part_familles_nombreuses = pd.DataFrame(data=part_familles_nombreuses, columns = ['Part des familles nombreuses ' + annee], index = [nom_departement])
      return df_Part_familles_nombreuses

  def part_fam_nombreuses_departement_P2017(fichier, departement, annee):
      communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, encoding= 'unicode_escape',sep = ',')
      df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
      year = annee[-2:]
      df_dpt = pd.merge(df[['COM', 'C' + year +'_FAM', 'C' + year + '_NE24F3', 'C' + year + '_NE24F4P']], communes_select[['COM','DEP']],  on='COM', how='left')
      df_departement = df_dpt.loc[df_dpt["DEP"]==departement, ['DEP', 'COM','C'+ year +'_FAM' , 'C'+ year + '_NE24F3', 'C'+ year + '_NE24F4P']]
      familles = df_departement.loc[:, 'C'+ year + '_FAM'].sum(axis = 0, skipna = True)
      familles_nombreuses = (df_departement.loc[:, 'C'+ year + '_NE24F3'].astype(float).sum(axis = 0, skipna = True)) + (df_departement.loc[:, 'C'+ year + '_NE24F4P'].astype(float).sum(axis = 0, skipna = True))
      part_familles_nombreuses = round((familles_nombreuses / familles)*100,2)
      df_part_familles_nombreuses = pd.DataFrame(data=part_familles_nombreuses, columns = ['Part des familles nombreuses ' + annee], index = [nom_departement])
      return df_part_familles_nombreuses

  if int(select_annee) < 2017:
      valeurs_fam_nombreuses_dep = part_fam_nombreuses_departement_M2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_departement,select_annee)
  else :
      valeurs_fam_nombreuses_dep = part_fam_nombreuses_departement_P2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_departement,select_annee)

  # Région
  #si année de 2014 à 2016 (inclus)
  def part_fam_nombreuses_region_M2017(fichier, region, annee):
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
      year = annee[-2:]
      df_regions = df.loc[df["REG"]==str(region), 'C'+ year +'_FAM' : 'C'+ year + '_NE24F4P']
      familles = df_regions.loc[:, 'C'+ year + '_FAM'].sum(axis = 0, skipna = True)
      familles_nombreuses = (df_regions.loc[:, 'C'+ year + '_NE24F3'].astype(float).sum(axis = 0, skipna = True)) + (df_regions.loc[:, 'C'+ year + '_NE24F4P'].astype(float).sum(axis = 0, skipna = True))
      part_familles_nombreuses = round((familles_nombreuses / familles)*100,0)
      df_part_familles_nombreuses = pd.DataFrame(data=part_familles_nombreuses, columns = ['Part des familles nombreuses ' + annee], index = [nom_region])
      return df_part_familles_nombreuses

  #si année de 2017 à ... (inclus)
  def part_fam_nombreuses_region_P2017(fichier, region, annee):
      communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, encoding= 'unicode_escape', sep = ',')
      df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
      year = annee[-2:]
      df_regions = pd.merge(df[['COM', 'C' + year +'_FAM', 'C' + year + '_NE24F3', 'C' + year + '_NE24F4P']], communes_select[['COM','REG']],  on='COM', how='left')
      df_region = df_regions.loc[df_regions["REG"]==str(region), ['REG', 'COM','C'+ year +'_FAM' , 'C'+ year + '_NE24F3', 'C'+ year + '_NE24F4P']]
      familles = df_region.loc[:, 'C'+ year + '_FAM'].sum(axis = 0, skipna = True)
      familles_nombreuses = (df_region.loc[:, 'C'+ year + '_NE24F3'].astype(float).sum(axis = 0, skipna = True)) + (df_region.loc[:, 'C'+ year + '_NE24F4P'].astype(float).sum(axis = 0, skipna = True))
      part_familles_nombreuses = round((familles_nombreuses / familles)*100,2)
      df_part_familles_nombreuses = pd.DataFrame(data=part_familles_nombreuses, columns = ['Part des familles nombreuses ' + annee], index = [nom_region])
      return df_part_familles_nombreuses

  if int(select_annee) < 2017:
      valeurs_fam_nombreuses_reg = part_fam_nombreuses_region_M2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",str(round(code_region)),select_annee)
  else :
      valeurs_fam_nombreuses_reg = part_fam_nombreuses_region_P2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",str(round(code_region)),select_annee)

  # France
  def part_fam_nombreuses_France(fichier, annee):
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
      year = annee[-2:]
      familles = df.loc[:, 'C'+ year + '_FAM']
      familles_nombreuses = df.loc[:, 'C'+ year + '_NE24F3' : 'C'+ year + '_NE24F4P']
      Somme_familles = familles.sum(axis = 0, skipna = True)
      Somme_familles_nombreuses = (familles_nombreuses.loc[:, 'C'+ year + '_NE24F3'].astype(float).sum(axis = 0, skipna = True)) + (familles_nombreuses.loc[:, 'C'+ year + '_NE24F4P'].astype(float).sum(axis = 0, skipna = True))
      part_familles_nombreuses = round((Somme_familles_nombreuses / Somme_familles)*100, 2)
      df_part_familles_nombreuses = pd.DataFrame(data=part_familles_nombreuses, columns = ['Part des familles nombreuses ' + annee], index = ["France"])
      return df_part_familles_nombreuses

  valeur_part_fam_nombreuses_fr = part_fam_nombreuses_France("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",select_annee)

  # Comparaison
  def fam_nombreuses_global(annee):
      df = pd.concat([indice_fam_nombreuses_epci, valeurs_fam_nombreuses_dep, valeurs_fam_nombreuses_reg, valeur_part_fam_nombreuses_fr])
      year = annee
      return df

  fam_nombreuses_fin = fam_nombreuses_global(select_annee)
  st.table(fam_nombreuses_fin)
  #################################

  st.subheader("3.Taux de couverture global - Accueil jeune enfant")
  st.caption("Capacité théorique d'accueil des enfants de moins de 3 ans par les modes d'accueil 'formels' pour 100 enfants de moins de 3 ans.")
  st.caption("Les modes d'accueil formels regroupent : l'assistant(e) maternel(le) employé(e) directement par des particuliers, le salarié(e) à domicile, l'accueil en Eaje (collectif, familial et parental, micro-crèches) et l'école maternelle")
  st.caption("Source : CAF 2020")
  df = pd.read_csv("./petite_enfance/caf/TAUXCOUV2020.csv", dtype={"NUM_COM": str, "NUM_EPCI": str}, sep=";")
  df_com_epci = df.loc[df['NUM_EPCI'] == str(code_epci)]
  df_com_epci = df_com_epci[["NUM_COM", "NOM_COM", "TAUXCOUV_COMM"]]
  df_com_epci = df_com_epci.reset_index(drop=True)
  df_com_epci = df_com_epci.rename(columns={'NUM_COM': "Code commune",'NOM_COM': "Commune", 'TAUXCOUV_COMM':"Taux de couverture global" })
  st.write(df_com_epci)

  #Comparaison
  df = df.loc[df['NUM_COM'] == code_commune]
  tx_epci = df.iloc[0]['TAUXCOUV_EPCI']
  tx_dep = float(df.iloc[0]['TAUXCOUV_DEP'])
  tx_reg = float(df.iloc[0]['TAUXCOUV_REG'])
  tx_nat = df.iloc[0]['TAUXCOUV_NAT']
  d = {'Territoires': [nom_epci, nom_departement, nom_region, 'France'], "Taux de couverture globale - 2020 (en %)": [tx_epci, tx_dep, tx_reg, tx_nat]}
  df = pd.DataFrame(data=d)
  st.write(df)
  #######################################

  st.subheader("Niveau de vie médian")
  df = pd.read_csv("./revenu/revenu_commune/FILO2019_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO', 'LIBGEO', 'EPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci = df_epci [["CODGEO", "LIBGEO_x", "Q219"]]
  df_epci = df_epci.reset_index(drop=True)
  st.write(df_epci)

  st.subheader("Comparaison :")
  #Position de la commune
  df = pd.read_csv("./revenu/revenu_commune/FILO" + select_annee + "_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
  year = select_annee[-2:]
  df_ville = df[['CODGEO','LIBGEO','Q2' + year]]
  if int(year) <= 15:
    df_ville['Q2' + year] = df_ville['Q2' + year].str.replace(',', '.').astype(float)
  df_ville = df_ville.sort_values(by=['Q2' + year], ascending=False)
  df_ville.reset_index(inplace=True, drop=True)
  indice = df_ville[df_ville['CODGEO']==code_commune].index.values.item()+1
  total_indice = len(df_ville['Q2' + year])
  st.write("La commune de " + nom_commune + " se situe en " + str(indice) + "eme position sur " + str(total_indice) + " communes")

  #Comparaison
  #EPCI
  def niveau_vie_median_epci(fichier, cod_epci, annee) :
    df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
    year = annee[-2:]
    df_epci = df.loc[df["CODGEO"]== cod_epci]
    df_epci = df_epci.replace(',','.', regex=True)
    epci = df.loc[df["CODGEO"]== cod_epci]
    if epci.empty:
      st.write("l'agglo n'est pas répartoriée par l'insee")
    else:
      nvm = epci[[ 'LIBGEO' ,'Q2'+ year]]
      return nvm
  nvm_epci =niveau_vie_median_epci("./revenu/revenu_epci/FILO" + select_annee + "_DISP_EPCI.csv",str(code_epci), select_annee)
  #Département
  def niveau_vie_median_departement(fichier, nom_departement, annee) :
      df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
      year = annee[-2:]
      df_departement = df.loc[df["LIBGEO"]== nom_departement]
      df_departement = df_departement.replace(',','.', regex=True)
      departement = df.loc[df["LIBGEO"]== nom_departement]
      nvm = departement[[ 'LIBGEO' ,'Q2'+ year]]
      return nvm
  nvm_departement =niveau_vie_median_departement("./revenu/revenu_dpt/FILO" + select_annee + "_DISP_DEP.csv",nom_departement, select_annee)
  #Région
  def niveau_vie_median_region(fichier, nom_region, annee) :
      df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
      year = annee[-2:]
      df_region = df.loc[df["LIBGEO"]== nom_region]
      df_region = df_region.replace(',','.', regex=True)
      region = df.loc[df["LIBGEO"]== nom_region]
      nvm = region[[ 'LIBGEO' ,'Q2'+ year]]
      return nvm
  nvm_region =niveau_vie_median_region("./revenu/revenu_region/FILO" + select_annee + "_DISP_REG.csv",nom_region, select_annee)
  #France
  def niveau_vie_median_france(fichier, annee) :
      df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
      df = df.replace(',','.', regex=True)
      year = annee[-2:]
      nvm = df[[ 'LIBGEO' ,'Q2'+ year]]
      return nvm
  nvm_france =niveau_vie_median_france("./revenu/revenu_france/FILO" + select_annee + "_DISP_METROPOLE.csv", select_annee)
  #Global
  test_tab = pd.concat([nvm_epci, nvm_departement, nvm_region, nvm_france])
  test_tab = test_tab.reset_index(drop=True)
  test_tab = test_tab.rename(columns={'LIBGEO': "Territoire",'Q2' + select_annee[-2:] : "Niveau de vie " + select_annee})
  st.write(test_tab)
  ###############################################

  st.subheader("1.Les naissances")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df = pd.read_csv("./petite_enfance/naissance/base_naissances_2021.csv", dtype={"CODGEO": str}, sep=";")

  df_epci_merge = pd.merge(df, df_epci[['CODGEO', 'LIBGEO', 'EPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]

  cols = ["NAISD14", "NAISD15", "NAISD16", "NAISD17", "NAISD18", "NAISD19", "NAISD20", "NAISD21"]
  df_epci[cols] = df_epci[cols].astype(int)
  df_epci = df_epci[['CODGEO', 'LIBGEO', 'NAISD14', "NAISD15", "NAISD16", "NAISD17", "NAISD18", "NAISD19", "NAISD20", "NAISD21"]]
  df_epci = df_epci.rename(columns={"LIBGEO": "Commune", "NAISD14": "2014", "NAISD15": "2015", "NAISD16": "2016", "NAISD17": "2017", "NAISD18": "2018", "NAISD19": "2019", "NAISD20": "2020", "NAISD21": "2021", })
  df_epci = df_epci.reset_index(drop=True)
  st.write(df_epci)
  ##########################

  st.header('2.Les moins de 3 ans')
  df = pd.read_csv("./petite_enfance/commune/BTX_TD_POP1A_" + select_annee + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci["pop_0003_epci"] = df_epci['SEXE1_AGEPYR1000'] + df_epci['SEXE2_AGEPYR1000']
  df_epci["total_pop_epci"] = (df_epci.iloc[:,2:22].sum(axis=1))
  df_epci["part_pop0003_epci"] = round(((df_epci["pop_0003_epci"] / df_epci["total_pop_epci"]) * 100), 2)
  df_part_pop_0003_epci = df_epci[["CODGEO", "LIBGEO", "pop_0003_epci", "total_pop_epci", "part_pop0003_epci"]]
  df_part_pop_0003_epci = df_part_pop_0003_epci.reset_index(drop=True)
  st.write(df_part_pop_0003_epci)

  st.subheader("Comparaison :")
  #EPCI
  df = pd.read_csv("./petite_enfance/commune/BTX_TD_POP1A_" + select_annee + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  pop_0003_epci = df_epci['SEXE1_AGEPYR1000'].sum() + df_epci['SEXE2_AGEPYR1000'].sum()
  total_pop_epci = (df_epci.iloc[:,2:22].sum(axis=1)).sum()
  part_pop0003_epci = round(((pop_0003_epci / total_pop_epci) * 100), 2)
  #Département
  df_dpt = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, sep = ',')
  df_dpt_merge = pd.merge(df, df_dpt[['COM','DEP']], left_on='CODGEO', right_on='COM')
  df_dpt = df_dpt_merge.loc[df_dpt_merge["DEP"] == str(code_departement)]
  pop_0003_dpt = df_dpt['SEXE1_AGEPYR1000'].sum() + df_dpt['SEXE2_AGEPYR1000'].sum()
  total_pop_dpt = (df_dpt.iloc[:,2:22].sum(axis=1)).sum()
  part_pop0003_dpt = round(((pop_0003_dpt / total_pop_dpt) * 100), 2)
  #Région
  df_region = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
  df_region_merge = pd.merge(df, df_region[['COM','REG']], left_on='CODGEO', right_on='COM')
  df_region = df_region_merge.loc[df_region_merge["REG"] == str(code_region)]
  pop_0003_region = df_region['SEXE1_AGEPYR1000'].sum() + df_region['SEXE2_AGEPYR1000'].sum()
  total_pop_region = (df_region.iloc[:,2:22].sum(axis=1)).sum()
  part_pop0003_region = round(((pop_0003_region / total_pop_region) * 100), 2)
  #France
  df = pd.read_csv("./petite_enfance/commune/BTX_TD_POP1A_" + select_annee + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  total_pop_france = df.sum(axis = 1).values[0]
  pop_0003_france =  (df['SEXE1_AGEPYR1000'] + df['SEXE2_AGEPYR1000']).values[0]
  part_pop0003_france = round(((pop_0003_france / total_pop_france) * 100), 2)
  #Comparaison
  d = {'Territoires': [nom_epci, nom_departement, nom_region, 'France'], "Part des 0-3 ans - " + select_annee + " (en %)": [part_pop0003_epci, part_pop0003_dpt, part_pop0003_region, part_pop0003_france]}
  df = pd.DataFrame(data=d)
  st.write(df)
  ####################

  st.subheader('2.Les enfants de 3 à 5 ans')
  df = pd.read_csv("./petite_enfance/commune/BTX_TD_POP1A_" + select_annee + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci["pop_0305_epci"] = df_epci['SEXE1_AGEPYR1003'] + df_epci['SEXE2_AGEPYR1003']
  df_epci["total_pop_epci"] = (df_epci.iloc[:,2:22].sum(axis=1))
  df_epci["part_pop0305_epci"] = round(((df_epci["pop_0305_epci"] / df_epci["total_pop_epci"]) * 100), 2)
  df_part_pop_0305_epci = df_epci[["CODGEO", "LIBGEO", "pop_0305_epci", "total_pop_epci", "part_pop0305_epci"]]
  df_part_pop_0305_epci = df_part_pop_0305_epci.reset_index(drop=True)
  st.write(df_part_pop_0305_epci)

  st.subheader("Comparaison : ")
  #EPCI
  df = pd.read_csv("./petite_enfance/commune/BTX_TD_POP1A_" + select_annee + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  pop_0305_epci = df_epci['SEXE1_AGEPYR1003'].sum() + df_epci['SEXE2_AGEPYR1003'].sum()
  total_pop_epci = (df_epci.iloc[:,2:22].sum(axis=1)).sum()
  part_pop0305_epci = round(((pop_0305_epci / total_pop_epci) * 100), 2)
  #Département
  df_dpt = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, sep = ',')
  df_dpt_merge = pd.merge(df, df_dpt[['COM','DEP']], left_on='CODGEO', right_on='COM')
  df_dpt = df_dpt_merge.loc[df_dpt_merge["DEP"] == str(code_departement)]
  pop_0305_dpt = df_dpt['SEXE1_AGEPYR1003'].sum() + df_dpt['SEXE2_AGEPYR1003'].sum()
  total_pop_dpt = (df_dpt.iloc[:,2:22].sum(axis=1)).sum()
  part_pop0305_dpt = round(((pop_0305_dpt / total_pop_dpt) * 100), 2)
  #Région
  df_region = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
  df_region_merge = pd.merge(df, df_region[['COM','REG']], left_on='CODGEO', right_on='COM')
  df_region = df_region_merge.loc[df_region_merge["REG"] == str(code_region)]
  pop_0305_region = df_region['SEXE1_AGEPYR1003'].sum() + df_region['SEXE2_AGEPYR1003'].sum()
  total_pop_region = (df_region.iloc[:,2:22].sum(axis=1)).sum()
  part_pop0305_region = round(((pop_0305_region / total_pop_region) * 100), 2)
  #France
  df = pd.read_csv("./petite_enfance/commune/BTX_TD_POP1A_" + select_annee + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  total_pop_france = df.sum(axis = 1).values[0]
  pop_0305_france =  (df['SEXE1_AGEPYR1003'] + df['SEXE2_AGEPYR1003']).values[0]
  part_pop0305_france = round(((pop_0305_france / total_pop_france) * 100), 2)
  #Comparaison
  d = {'Territoires': [nom_epci, nom_departement, nom_region, 'France'], "Part des 3-5 ans - " + select_annee + " (en %)": [part_pop0305_epci, part_pop0305_dpt, part_pop0305_region, part_pop0305_france]}
  df = pd.DataFrame(data=d)
  st.write(df)
  #########################################################################

  st.subheader('4.La scolarisation des enfants de 2 ans')
  df = pd.read_csv("./petite_enfance/scol_2ans/BTT_TD_FOR1_2019.csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci = df_epci.loc[df_epci['AGEFORD'] == 2]
  #df_scol02_epci = df_epci.groupby(['ILETUR'])['NB']
  #non_scol_02_epci = df_scol02_epci['Z']
  #pop_02_epci = df_epci['NB']
  #scol_02_epci = pop_02_epci - non_scol_02_epci
  #tx_scol_02_epci = (scol_02_epci / pop_02_epci) * 100
  st.write(df_epci)
  st.write("A retravailler")
