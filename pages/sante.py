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
from streamlit_option_menu import option_menu


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

  ############################################################################
  st.header("Les licenciés sportifs")
  st.subheader("Population générale")
  st.caption("Source : xxx. Parue le XXXX - Millésime 2019")
  last_year_licsport = "2019"

  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str, "an": str}, sep=';')
      df = df.loc[(df[column_code] == code) & (df['an'] == last_year_licsport)]
      return df['p_licsport'].values[0]

  # Commune
  tx_licencies_sportifs_commune = load_data("./sante/licencies_sportifs/global/licsport_commune_" + last_year_licsport + ".csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], 'Taux de licenciés sportifs 2019': [tx_licencies_sportifs_commune]})

  # EPCI
  tx_licencies_sportifs_epci = load_data("./sante/licencies_sportifs/global/licsport_epci_" + last_year_licsport + ".csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], 'Taux de licenciés sportifs 2019': [tx_licencies_sportifs_epci]})

  # Département
  tx_licencies_sportifs_departement = load_data("./sante/licencies_sportifs/global/licsport_departement_" + last_year_licsport + ".csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], 'Taux de licenciés sportifs 2019': [tx_licencies_sportifs_departement]})

  # Région
  tx_licencies_sportifs_region = load_data("./sante/licencies_sportifs/global/licsport_région_" + last_year_licsport + ".csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], 'Taux de licenciés sportifs 2019': [tx_licencies_sportifs_region]})

  # France
  tx_licencies_sportifs_france = load_data("./sante/licencies_sportifs/global/licsport_france_" + last_year_licsport + ".csv", '1111', column_code='codgeo')
  data_france = pd.DataFrame({'Territoires': ['France'], 'Taux de licenciés sportifs 2019': [tx_licencies_sportifs_france]})

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Convertir la colonne 'taux de licenciés sportifs 2019' en numérique
  all_data['Taux de licenciés sportifs 2019'] = all_data['Taux de licenciés sportifs 2019'].str.replace(',', '.').astype(float)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Taux de licenciés sportifs 2019', y='Territoires', orientation='h',
               title='Comparaison du taux de licenciés sportifs en 2019')

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique"],  # required
      icons=["table", "bar-chart"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key1"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write("Données des licenciés sportifs en 2019")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)

  ##############################################
  st.subheader("Population des 0-14 ans")
  st.caption("Source : xxx. Parue le XXXX - Millésime 2019")

  last_year_licsport = "2019"

  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str, "an": str}, sep=';')
      df = df.loc[(df[column_code] == code) & (df['an'] == last_year_licsport)]
      return df['p_licsport014'].values[0]

  # Commune
  tx_licencies_sportifs_0014_commune = load_data("./sante/licencies_sportifs/00-14/licsport_0014_communes_" + last_year_licsport + ".csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], 'Taux de licenciés sportifs de 0 à 14 ans ' + last_year_licsport : [tx_licencies_sportifs_0014_commune]})

  # EPCI
  tx_licencies_sportifs_0014_epci = load_data("./sante/licencies_sportifs/00-14/licsport_0014_epci_" + last_year_licsport + ".csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], 'Taux de licenciés sportifs de 0 à 14 ans ' + last_year_licsport : [tx_licencies_sportifs_0014_epci]})

  # Département
  tx_licencies_sportifs_0014_departement = load_data("./sante/licencies_sportifs/00-14/licsport_0014_departement_" + last_year_licsport + ".csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], 'Taux de licenciés sportifs de 0 à 14 ans ' + last_year_licsport : [tx_licencies_sportifs_0014_departement]})

  # Région
  tx_licencies_sportifs_0014_region = load_data("./sante/licencies_sportifs/00-14/licsport_0014_region_" + last_year_licsport + ".csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], 'Taux de licenciés sportifs de 0 à 14 ans ' + last_year_licsport : [tx_licencies_sportifs_0014_region]})

  # France
  tx_licencies_sportifs_0014_france = load_data("./sante/licencies_sportifs/00-14/licsport_0014_france_" + last_year_licsport + ".csv", '1111', column_code='codgeo')
  data_france = pd.DataFrame({'Territoires': ['France'], 'Taux de licenciés sportifs de 0 à 14 ans ' + last_year_licsport : [tx_licencies_sportifs_0014_france]})

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Convertir la colonne des taux en numérique
  all_data['Taux de licenciés sportifs de 0 à 14 ans ' + last_year_licsport] = all_data['Taux de licenciés sportifs de 0 à 14 ans ' + last_year_licsport].str.replace(',', '.').astype(float)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Taux de licenciés sportifs de 0 à 14 ans ' +  last_year_licsport, y='Territoires', orientation='h',
               title='Comparaison du taux de licenciés sportifs de 0 à 14 ans en ' + last_year_licsport)


  #Dont filles
  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str, "an": str}, sep=';')
      df = df.loc[(df[column_code] == code) & (df['an'] == last_year_licsport)]
      return df['p_licsport014_f'].values[0]

  # Commune
  tx_licencies_sportifs_014_f_commune = load_data("./sante/licencies_sportifs/00-14/filles/licsport_0014_f_communes_" + last_year_licsport + ".csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], 'Taux de licenciés sportifs de 00 à 14 ans filles ' + last_year_licsport: [tx_licencies_sportifs_014_f_commune]})

  # EPCI
  tx_licencies_sportifs_014_f_epci = load_data("./sante/licencies_sportifs/00-14/filles/licsport_0014_f_epci_" + last_year_licsport + ".csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], 'Taux de licenciés sportifs de 00 à 14 ans filles ' + last_year_licsport: [tx_licencies_sportifs_014_f_epci]})

  # Département
  tx_licencies_sportifs_014_f_departement = load_data("./sante/licencies_sportifs/00-14/filles/licsport_0014_f_departement_" + last_year_licsport + ".csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], 'Taux de licenciés sportifs de 00 à 14 ans filles ' + last_year_licsport: [tx_licencies_sportifs_014_f_departement]})

  # Région
  tx_licencies_sportifs_014_f_region = load_data("./sante/licencies_sportifs/00-14/filles/licsport_0014_f_region_" + last_year_licsport + ".csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], 'Taux de licenciés sportifs de 00 à 14 ans filles ' + last_year_licsport: [tx_licencies_sportifs_014_f_region]})

  # France
  tx_licencies_sportifs_014_f_france = load_data("./sante/licencies_sportifs/00-14/filles/licsport_0014_f_france_" + last_year_licsport + ".csv", '1111', column_code='codgeo')
  data_france = pd.DataFrame({'Territoires': ['France'], 'Taux de licenciés sportifs de 00 à 14 ans filles ' + last_year_licsport: [tx_licencies_sportifs_014_f_france]})

  # Fusionner les données
  all_data_f = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data_f.reset_index(drop=True, inplace=True)

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique", "Dont filles"],  # required
      icons=["table", "bar-chart", "gender-female"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key2"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write("Données des licenciés sportifs de 0 à 14 ans en " +  last_year_licsport)
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)
  elif selected == "Dont filles":
      st.dataframe(all_data_f)

  ##############################################
  st.subheader("Population des 15-29 ans")
  st.caption("Source : xxx. Parue le XXXX - Millésime 2019")

  last_year_licsport = "2019"

  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str, "an": str}, sep=';')
      df = df.loc[(df[column_code] == code) & (df['an'] == last_year_licsport)]
      return df['p_licsport1529'].values[0]

  # Commune
  tx_licencies_sportifs_1529_commune = load_data("./sante/licencies_sportifs/15-29/licsport_1529_communes_" + last_year_licsport + ".csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], 'Taux de licenciés sportifs de 15 à 29 ans ' + last_year_licsport : [tx_licencies_sportifs_1529_commune]})

  # EPCI
  tx_licencies_sportifs_1529_epci = load_data("./sante/licencies_sportifs/15-29/licsport_1529_epci_" + last_year_licsport + ".csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], 'Taux de licenciés sportifs de 15 à 29 ans ' + last_year_licsport : [tx_licencies_sportifs_1529_epci]})

  # Département
  tx_licencies_sportifs_1529_departement = load_data("./sante/licencies_sportifs/15-29/licsport_1529_departement_" + last_year_licsport + ".csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], 'Taux de licenciés sportifs de 15 à 29 ans ' + last_year_licsport : [tx_licencies_sportifs_1529_departement]})

  # Région
  tx_licencies_sportifs_1529_region = load_data("./sante/licencies_sportifs/15-29/licsport_1529_region_" + last_year_licsport + ".csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], 'Taux de licenciés sportifs de 15 à 29 ans ' + last_year_licsport : [tx_licencies_sportifs_1529_region]})

  # France
  tx_licencies_sportifs_1529_france = load_data("./sante/licencies_sportifs/15-29/licsport_1529_france_" + last_year_licsport + ".csv", '1111', column_code='codgeo')
  data_france = pd.DataFrame({'Territoires': ['France'], 'Taux de licenciés sportifs de 15 à 29 ans ' + last_year_licsport : [tx_licencies_sportifs_1529_france]})

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Convertir la colonne des taux en numérique
  all_data['Taux de licenciés sportifs de 15 à 29 ans ' + last_year_licsport] = all_data['Taux de licenciés sportifs de 15 à 29 ans ' + last_year_licsport].str.replace(',', '.').astype(float)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Taux de licenciés sportifs de 15 à 29 ans ' +  last_year_licsport, y='Territoires', orientation='h',
               title='Comparaison du taux de licenciés sportifs de 15 à 29 ans en ' + last_year_licsport)

  # Dont femmes
  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str, "an": str}, sep=';')
      df = df.loc[(df[column_code] == code) & (df['an'] == last_year_licsport)]
      return df['p_licsport1529_f'].values[0]

  # Commune
  tx_licencies_sportifs_1529_commune = load_data("./sante/licencies_sportifs/15-29/femmes/licsport_1529_f_communes_" + last_year_licsport + ".csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], 'Taux de licenciés sportifs de 15 à 29 ans femmes ' + last_year_licsport: [tx_licencies_sportifs_1529_commune]})

  # EPCI
  tx_licencies_sportifs_1529_epci = load_data("./sante/licencies_sportifs/15-29/femmes/licsport_1529_f_epci_" + last_year_licsport + ".csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], 'Taux de licenciés sportifs de 15 à 29 ans femmes ' + last_year_licsport: [tx_licencies_sportifs_1529_epci]})

  # Département
  tx_licencies_sportifs_1529_departement = load_data("./sante/licencies_sportifs/15-29/femmes/licsport_1529_f_departement_" + last_year_licsport + ".csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], 'Taux de licenciés sportifs de 15 à 29 ans femmes ' + last_year_licsport: [tx_licencies_sportifs_1529_departement]})

  # Région
  tx_licencies_sportifs_1529_region = load_data("./sante/licencies_sportifs/15-29/femmes/licsport_1529_f_region_" + last_year_licsport + ".csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], 'Taux de licenciés sportifs de 15 à 29 ans femmes ' + last_year_licsport: [tx_licencies_sportifs_1529_region]})

  # France
  tx_licencies_sportifs_1529_france = load_data("./sante/licencies_sportifs/15-29/femmes/licsport_1529_f_france_" + last_year_licsport + ".csv", '1111', column_code='codgeo')
  data_france = pd.DataFrame({'Territoires': ['France'], 'Taux de licenciés sportifs de 15 à 29 ans femmes ' + last_year_licsport: [tx_licencies_sportifs_1529_france]})

  # Fusionner les données
  all_data_f = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data_f.reset_index(drop=True, inplace=True)


  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique", "Dont femmes"],  # required
      icons=["table", "bar-chart", "gender-female"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key3"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write("Données des licenciés sportifs de 15 à 29 ans en " +  last_year_licsport)
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)
  elif selected == "Dont femmes":
      st.dataframe(all_data_f)

  ##############################################
  st.subheader("Population des 30-59 ans")
  st.caption("Source : xxx. Parue le XXXX - Millésime 2019")

  last_year_licsport = "2019"

  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str, "an": str}, sep=';')
      df = df.loc[(df[column_code] == code) & (df['an'] == last_year_licsport)]
      return df['p_licsport3059'].values[0]

  # Commune
  tx_licencies_sportifs_3059_commune = load_data("./sante/licencies_sportifs/30-59/licsport_3059_communes_" + last_year_licsport + ".csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], 'Taux de licenciés sportifs de 30 à 59 ans ' + last_year_licsport : [tx_licencies_sportifs_3059_commune]})

  # EPCI
  tx_licencies_sportifs_3059_epci = load_data("./sante/licencies_sportifs/30-59/licsport_3059_epci_" + last_year_licsport + ".csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], 'Taux de licenciés sportifs de 30 à 59 ans ' + last_year_licsport : [tx_licencies_sportifs_3059_epci]})

  # Département
  tx_licencies_sportifs_3059_departement = load_data("./sante/licencies_sportifs/30-59/licsport_3059_departement_" + last_year_licsport + ".csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], 'Taux de licenciés sportifs de 30 à 59 ans ' + last_year_licsport : [tx_licencies_sportifs_3059_departement]})

  # Région
  tx_licencies_sportifs_3059_region = load_data("./sante/licencies_sportifs/30-59/licsport_3059_region_" + last_year_licsport + ".csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], 'Taux de licenciés sportifs de 30 à 59 ans ' + last_year_licsport : [tx_licencies_sportifs_3059_region]})

  # France
  tx_licencies_sportifs_3059_france = load_data("./sante/licencies_sportifs/30-59/licsport_3059_france_" + last_year_licsport + ".csv", '1111', column_code='codgeo')
  data_france = pd.DataFrame({'Territoires': ['France'], 'Taux de licenciés sportifs de 30 à 59 ans ' + last_year_licsport : [tx_licencies_sportifs_3059_france]})

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Convertir la colonne des taux en numérique
  all_data['Taux de licenciés sportifs de 30 à 59 ans ' + last_year_licsport] = all_data['Taux de licenciés sportifs de 30 à 59 ans ' + last_year_licsport].str.replace(',', '.').astype(float)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Taux de licenciés sportifs de 30 à 59 ans ' +  last_year_licsport, y='Territoires', orientation='h',
               title='Comparaison du taux de licenciés sportifs de 30 à 59 ans en ' + last_year_licsport)


  # Dont femmes
  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str, "an": str}, sep=';')
      df = df.loc[(df[column_code] == code) & (df['an'] == last_year_licsport)]
      return df['p_licsport3059_f'].values[0]

  # Commune
  tx_licencies_sportifs_3059_commune = load_data("./sante/licencies_sportifs/30-59/femmes/licsport_3059_f_communes_" + last_year_licsport + ".csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], 'Taux de licenciés sportifs de 30 à 59 ans femmes ' + last_year_licsport: [tx_licencies_sportifs_3059_commune]})

  # EPCI
  tx_licencies_sportifs_3059_epci = load_data("./sante/licencies_sportifs/30-59/femmes/licsport_3059_f_epci_" + last_year_licsport + ".csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], 'Taux de licenciés sportifs de 30 à 59 ans femmes ' + last_year_licsport: [tx_licencies_sportifs_3059_epci]})

  # Département
  tx_licencies_sportifs_3059_departement = load_data("./sante/licencies_sportifs/30-59/femmes/licsport_3059_f_departement_" + last_year_licsport + ".csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], 'Taux de licenciés sportifs de 30 à 59 ans femmes ' + last_year_licsport: [tx_licencies_sportifs_3059_departement]})

  # Région
  tx_licencies_sportifs_3059_region = load_data("./sante/licencies_sportifs/30-59/femmes/licsport_3059_f_region_" + last_year_licsport + ".csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], 'Taux de licenciés sportifs de 30 à 59 ans femmes ' + last_year_licsport: [tx_licencies_sportifs_3059_region]})

  # France
  tx_licencies_sportifs_3059_france = load_data("./sante/licencies_sportifs/30-59/femmes/licsport_3059_f_france_" + last_year_licsport + ".csv", '1111', column_code='codgeo')
  data_france = pd.DataFrame({'Territoires': ['France'], 'Taux de licenciés sportifs de 30 à 59 ans femmes ' + last_year_licsport: [tx_licencies_sportifs_3059_france]})

  # Fusionner les données
  all_data_f = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data_f.reset_index(drop=True, inplace=True)

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique", "Dont femmes"],  # required
      icons=["table", "bar-chart", "gender-female"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key4"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write("Données des licenciés sportifs de 30 à 59 ans en " +  last_year_licsport)
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)
  elif selected == "Dont femmes":
      st.dataframe(all_data_f)

  ##############################################
  st.subheader("Population des 60 ans et plus")
  st.caption("Source : xxx. Parue le XXXX - Millésime 2019")

  last_year_licsport = "2019"

  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str, "an": str}, sep=';')
      df = df.loc[(df[column_code] == code) & (df['an'] == last_year_licsport)]
      return df['p_licsport60'].values[0]

  # Commune
  tx_licencies_sportifs_60P_commune = load_data("./sante/licencies_sportifs/60P/licsport_60P_communes_" + last_year_licsport + ".csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], 'Taux de licenciés sportifs de 60 ans et plus ' + last_year_licsport : [tx_licencies_sportifs_60P_commune]})

  # EPCI
  tx_licencies_sportifs_60P_epci = load_data("./sante/licencies_sportifs/60P/licsport_60P_epci_" + last_year_licsport + ".csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], 'Taux de licenciés sportifs de 60 ans et plus ' + last_year_licsport : [tx_licencies_sportifs_60P_epci]})

  # Département
  tx_licencies_sportifs_60P_departement = load_data("./sante/licencies_sportifs/60P/licsport_60P_departement_" + last_year_licsport + ".csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], 'Taux de licenciés sportifs de 60 ans et plus ' + last_year_licsport : [tx_licencies_sportifs_60P_departement]})

  # Région
  tx_licencies_sportifs_60P_region = load_data("./sante/licencies_sportifs/60P/licsport_60P_region_" + last_year_licsport + ".csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], 'Taux de licenciés sportifs de 60 ans et plus ' + last_year_licsport : [tx_licencies_sportifs_60P_region]})

  # France
  tx_licencies_sportifs_60P_france = load_data("./sante/licencies_sportifs/60P/licsport_60P_france_" + last_year_licsport + ".csv", '1111', column_code='codgeo')
  data_france = pd.DataFrame({'Territoires': ['France'], 'Taux de licenciés sportifs de 60 ans et plus ' + last_year_licsport : [tx_licencies_sportifs_60P_france]})

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Convertir la colonne des taux en numérique
  all_data['Taux de licenciés sportifs de 60 ans et plus ' + last_year_licsport] = all_data['Taux de licenciés sportifs de 60 ans et plus ' + last_year_licsport].str.replace(',', '.').astype(float)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Taux de licenciés sportifs de 60 ans et plus ' +  last_year_licsport, y='Territoires', orientation='h',
               title='Comparaison du taux de licenciés sportifs de 60 ans et plus en ' + last_year_licsport)


  # Dont femmes
  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str, "an": str}, sep=';')
      df = df.loc[(df[column_code] == code) & (df['an'] == last_year_licsport)]
      return df['p_licsport60_f'].values[0]

  # Commune
  tx_licencies_sportifs_60P_commune = load_data("./sante/licencies_sportifs/60P/femmes/licsport_60P_f_communes_" + last_year_licsport + ".csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], 'Taux de licenciés sportifs de 60 ans et plus femmes ' + last_year_licsport: [tx_licencies_sportifs_60P_commune]})

  # EPCI
  tx_licencies_sportifs_60P_epci = load_data("./sante/licencies_sportifs/60P/femmes/licsport_60P_f_epci_" + last_year_licsport + ".csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], 'Taux de licenciés sportifs de 60 ans et plus femmes ' + last_year_licsport: [tx_licencies_sportifs_60P_epci]})

  # Département
  tx_licencies_sportifs_60P_departement = load_data("./sante/licencies_sportifs/60P/femmes/licsport_60P_f_departement_" + last_year_licsport + ".csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], 'Taux de licenciés sportifs de 60 ans et plus femmes ' + last_year_licsport: [tx_licencies_sportifs_60P_departement]})

  # Région
  tx_licencies_sportifs_60P_region = load_data("./sante/licencies_sportifs/60P/femmes/licsport_60P_f_region_" + last_year_licsport + ".csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], 'Taux de licenciés sportifs de 60 ans et plus femmes ' + last_year_licsport: [tx_licencies_sportifs_60P_region]})

  # France
  tx_licencies_sportifs_60P_france = load_data("./sante/licencies_sportifs/60P/femmes/licsport_60P_f_france_" + last_year_licsport + ".csv", '1111', column_code='codgeo')
  data_france = pd.DataFrame({'Territoires': ['France'], 'Taux de licenciés sportifs de 60 ans et plus femmes ' + last_year_licsport: [tx_licencies_sportifs_60P_france]})

  # Fusionner les données
  all_data_f = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data_f.reset_index(drop=True, inplace=True)

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique", "Dont femmes"],  # required
      icons=["table", "bar-chart", "gender-female"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key5"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write("Données des licenciés sportifs de 60 ans et plus en " +  last_year_licsport)
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)
  elif selected == "Dont femmes":
      st.dataframe(all_data_f)
