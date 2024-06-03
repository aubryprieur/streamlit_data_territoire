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
  st.caption("L’indicateur d’accessibilité potentielle localisée (APL) a été développé par la DREES et l’IRDES* pour mesurer \
              l’adéquation spatiale entre l’offre et la demande de soins de premier recours à un échelon géographique fin. \
              Il vise à améliorer les indicateurs usuels d’accessibilité aux soins (distance d’accès, densité par bassin de vie ou département…). \
              Il mobilise pour cela les données de l’Assurance maladie (SNIIR-AM) ainsi que les données de population de l’Insee.")
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
  st.header("Accessibilité potentielle localisée (APL) à la médecine libérale")
  st.caption("Source : SNDS, Système National des Données de Santé. Parue le XXXX - Millésime 2021")
  st.caption("L’Accessibilité Potentielle Localisée est un indicateur local, disponible au niveau de chaque commune, qui tient compte de l’offre et de la demande issue des communes environnantes. Calculé à l’échelle communale, l’APL met en évidence des disparités d’offre de soins. L’APL tient compte du niveau d’activité des professionnels en exercice ainsi que de la structure par âge de la population de chaque commune qui influence les besoins de soins. L’indicateur permet de quantifier la possibilité des habitants d’accéder aux soins des médecins généralistes libéraux.")

  last_year_apl = "2021"

  # Charger les données pour les médecins généralistes
  def load_data_generaliste(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str, "an": str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df['apl_mg_hmep'].values[0]

  # Médecins généralistes
  apl_com = load_data_generaliste("./sante/apl/medecin_generaliste/apl_medecin_generaliste_com_" + last_year_apl + ".csv", code_commune)
  apl_epci = load_data_generaliste("./sante/apl/medecin_generaliste/apl_medecin_generaliste_epci_" + last_year_apl + ".csv", code_epci)
  apl_dpt = load_data_generaliste("./sante/apl/medecin_generaliste/apl_medecin_generaliste_dpt_" + last_year_apl + ".csv", code_departement)
  apl_reg = load_data_generaliste("./sante/apl/medecin_generaliste/apl_medecin_generaliste_region_" + last_year_apl + ".csv", code_region)
  apl_fr = pd.read_csv("./sante/apl/medecin_generaliste/apl_medecin_generaliste_france_" + last_year_apl + ".csv", sep=';')['apl_mg_hmep'].values[0]

  data_medecin_generaliste = pd.DataFrame({
      'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'],
      "APL - " + last_year_apl: [apl_com, apl_epci, apl_dpt, apl_reg, apl_fr]
  })

  # Charger les données pour les chirurgiens dentistes
  def load_data_dentiste(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df['apl_chirurgiens_dentistes'].values[0]

  # Chirurgiens dentistes
  apl_dentistes_commune = load_data_dentiste("./sante/apl/chirurgiens_dentistes/apl_chirurgiens_dentistes_commune_" + last_year_apl + ".csv", code_commune)
  apl_dentistes_epci = load_data_dentiste("./sante/apl/chirurgiens_dentistes/apl_chirurgiens_dentistes_epci_" + last_year_apl + ".csv", code_epci)
  apl_dentistes_departement = load_data_dentiste("./sante/apl/chirurgiens_dentistes/apl_chirurgiens_dentistes_departement_" + last_year_apl + ".csv", code_departement)
  apl_dentistes_region = load_data_dentiste("./sante/apl/chirurgiens_dentistes/apl_chirurgiens_dentistes_region_" + last_year_apl + ".csv", code_region)
  apl_dentistes_france = pd.read_csv("./sante/apl/chirurgiens_dentistes/apl_chirurgiens_dentistes_france_" + last_year_apl + ".csv", sep=';')['apl_chirurgiens_dentistes'].values[0]

  data_chirurgiens_dentistes = pd.DataFrame({
      'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'],
      "APL - " + last_year_apl: [apl_dentistes_commune, apl_dentistes_epci, apl_dentistes_departement, apl_dentistes_region, apl_dentistes_france]
  })

  # Charger les données pour les sages-femmes
  def load_data_sages_femmes(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df['apl_sages_femmes'].values[0]

  # Sages-femmes
  apl_sages_femmes_commune = load_data_sages_femmes("./sante/apl/sages_femmes/apl_sages_femmes_commune_" + last_year_apl + ".csv", code_commune)
  apl_sages_femmes_epci = load_data_sages_femmes("./sante/apl/sages_femmes/apl_sages_femmes_epci_" + last_year_apl + ".csv", code_epci)
  apl_sages_femmes_departement = load_data_sages_femmes("./sante/apl/sages_femmes/apl_sages_femmes_departement_" + last_year_apl + ".csv", code_departement)
  apl_sages_femmes_region = load_data_sages_femmes("./sante/apl/sages_femmes/apl_sages_femmes_region_" + last_year_apl + ".csv", code_region)
  apl_sages_femmes_france = pd.read_csv("./sante/apl/sages_femmes/apl_sages_femmes_france_" + last_year_apl + ".csv", sep=';')['apl_sages_femmes'].values[0]

  data_sages_femmes = pd.DataFrame({
      'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'],
      "APL - " + last_year_apl: [apl_sages_femmes_commune, apl_sages_femmes_epci, apl_sages_femmes_departement, apl_sages_femmes_region, apl_sages_femmes_france]
  })

  # Charger les données pour les infirmiers
  def load_data_infirmiers(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df['apl_infirmiers'].values[0]

  # Infirmiers
  apl_infirmiers_commune = load_data_infirmiers("./sante/apl/infirmiers/apl_infirmiers_commune_" + last_year_apl + ".csv", code_commune)
  apl_infirmiers_epci = load_data_infirmiers("./sante/apl/infirmiers/apl_infirmiers_epci_" + last_year_apl + ".csv", code_epci)
  apl_infirmiers_departement = load_data_infirmiers("./sante/apl/infirmiers/apl_infirmiers_departement_" + last_year_apl + ".csv", code_departement)
  apl_infirmiers_region = load_data_infirmiers("./sante/apl/infirmiers/apl_infirmiers_region_" + last_year_apl + ".csv", code_region)
  apl_infirmiers_france = pd.read_csv("./sante/apl/infirmiers/apl_infirmiers_france_" + last_year_apl + ".csv", sep=';')['apl_infirmiers'].values[0]

  data_infirmiers = pd.DataFrame({
      'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'],
      "APL - " + last_year_apl: [apl_infirmiers_commune, apl_infirmiers_epci, apl_infirmiers_departement, apl_infirmiers_region, apl_infirmiers_france]
  })


  # Charger les données pour les kinés
  def load_data_kines(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df['apl_kines'].values[0]

  # Infirmiers
  apl_kines_commune = load_data_kines("./sante/apl/kines/apl_kines_commune_" + last_year_apl + ".csv", code_commune)
  apl_kines_epci = load_data_kines("./sante/apl/kines/apl_kines_epci_" + last_year_apl + ".csv", code_epci)
  apl_kines_departement = load_data_kines("./sante/apl/kines/apl_kines_departement_" + last_year_apl + ".csv", code_departement)
  apl_kines_region = load_data_kines("./sante/apl/kines/apl_kines_region_" + last_year_apl + ".csv", code_region)
  apl_kines_france = pd.read_csv("./sante/apl/kines/apl_kines_france_" + last_year_apl + ".csv", sep=';')['apl_kines'].values[0]

  data_kines = pd.DataFrame({
      'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'],
      "APL - " + last_year_apl: [apl_kines_commune, apl_kines_epci, apl_kines_departement, apl_kines_region, apl_kines_france]
  })

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Médecins Généralistes", "Chirurgiens Dentistes", "Sages Femmes", "Infirmiers", "Kinés"],  # required
      icons=["1-circle", "2-circle", "3-circle", "4-circle", "5-circle"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key8"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Médecins Généralistes":
      st.write("Données des Médecins Généralistes - Accessibilité Potentielle Localisée (APL)")
      st.dataframe(data_medecin_generaliste)
  elif selected == "Chirurgiens Dentistes":
      st.write("Données des Chirurgiens Dentistes de 65 ans et moins - Accessibilité Potentielle Localisée (APL)")
      st.dataframe(data_chirurgiens_dentistes)
      st.caption("L’accessibilité aux chirurgiens-dentistes pour la ville de " + nom_commune + " et de " + apl_dentistes_commune + " ETP pour 100 000 habitants en " + last_year_apl + ". Pour comparaison, l’accessibilité nationale moyenne est de 59,0 ETP pour 100 000 habitants en 2021." )
      if float(apl_dentistes_commune) > float(apl_dentistes_france):
        st.caption(f"Votre commune est donc mieux dotée en chirurgiens-dentistes, soit une accessibilité {round(float(apl_dentistes_commune) / float(apl_dentistes_france), 1)} fois plus élevée. A titre de comparaison, l’accessibilité moyenne des 10 % de la population les moins bien dotés en chirurgiens-dentistes est de 15,3 ETP pour 100 000 habitants. Celle des 10 % les mieux dotés en chirurgiens-dentistes est de 111,0 ETP pour 100 000 habitants.")
      st.caption("Pour plus d'information : l'article de la dress du 01/02/2023 sur [l'accessibilité aux chirurgiens-dentistes](https://drees.solidarites-sante.gouv.fr/jeux-de-donnees-communique-de-presse/accessibilite-aux-soins-de-premier-recours-de-fortes)")
  elif selected == "Sages Femmes":
      st.write("Données des Sages Femmes - Accessibilité Potentielle Localisée (APL)")
      st.dataframe(data_sages_femmes)
  elif selected == "Infirmiers":
      st.write("Données des Infirmiers de 65 ans et moins - Accessibilité Potentielle Localisée (APL)")
      st.dataframe(data_infirmiers)
  elif selected == "Kinés":
      st.write("Données des Kinés de 65 ans et moins - Accessibilité Potentielle Localisée (APL)")
      st.dataframe(data_kines)
  ############################################################################
  st.header("La prévention par le sport")
  st.subheader("Les licenciés sportifs - Sur la population totale")
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
  st.subheader("Les licenciés sportifs des 0-14 ans")
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
  st.subheader("Les licenciés sportifs des 15-29 ans")
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
  st.subheader("Les licenciés sportifs des 30-59 ans")
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
  st.subheader("Les licenciés sportifs des 60 ans et plus")
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

  #############################################
  st.header("Statistiques des Affections de Longue Durée (ALD)")
  st.caption("Source : xxx. Parue le XXXX - Millésime 2022")

  last_year_ald = "2022"
  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(file_path, code, column_code='codgeo'):
      df = pd.read_csv(file_path, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df['ald'].values[0]

  # Commune
  tx_ald_commune = load_data("./sante/ald/ald_commune_" + last_year_ald + ".csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], f"Taux de ALD {last_year_ald}": [tx_ald_commune]})

  # EPCI
  tx_ald_epci = load_data("./sante/ald/ald_epci_" + last_year_ald + ".csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], f"Taux de ALD {last_year_ald}": [tx_ald_epci]})

  # Département
  tx_ald_departement = load_data("./sante/ald/ald_departement_" + last_year_ald + ".csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], f"Taux de ALD {last_year_ald}": [tx_ald_departement]})

  # Région
  tx_ald_region = load_data("./sante/ald/ald_region_" + last_year_ald + ".csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], f"Taux de ALD {last_year_ald}": [tx_ald_region]})

  # France
  tx_ald_france = load_data("./sante/ald/ald_france_" + last_year_ald + ".csv", '1111', column_code='codgeo')
  data_france = pd.DataFrame({'Territoires': ['France'], f"Taux de ALD {last_year_ald}": [tx_ald_france]})

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Convertir la colonne 'Taux de ALD 2022' en numérique
  all_data[f"Taux de ALD {last_year_ald}"] = all_data[f"Taux de ALD {last_year_ald}"].apply(lambda x: str(x).replace(',', '.')).astype(float)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x=f"Taux de ALD {last_year_ald}", y='Territoires', orientation='h',
               title=f"Comparaison du taux de ALD en {last_year_ald}")

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique"],  # required
      icons=["table", "bar-chart"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key9"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write(f"Données des Affections de Longue Durée (ALD) en {last_year_ald}")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)
