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

  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(fichier, code, period):
      df = pd.read_csv(fichier, dtype={"codgeo": str}, sep=';')
      df = df.loc[df["codgeo"] == code]
      df = df.loc[df["an"] == period]
      return df

  tx_mortalite_ville = load_data("./sante/taux_de_mortalite/insee_rp_evol_1968_communes_" + last_year_mortal + ".csv", code_commune, period)
  tx_mortalite_epci = load_data("./sante/taux_de_mortalite/insee_rp_evol_1968_epci_" + last_year_mortal + ".csv", code_epci, period)
  tx_mortalite_dpt = load_data("./sante/taux_de_mortalite/insee_rp_evol_1968_departement_" + last_year_mortal + ".csv", code_departement, period)
  tx_mortalite_reg = load_data("./sante/taux_de_mortalite/insee_rp_evol_1968_region_" + last_year_mortal + ".csv", code_region, period)

  # France
  def load_data_france(fichier, period):
      df = pd.read_csv(fichier, dtype={"codgeo": str}, sep=';')
      df = df.loc[df["an"] == period]
      return df

  tx_mortalite_france = load_data_france("./sante/taux_de_mortalite/insee_rp_evol_1968_france_" + last_year_mortal + ".csv", period)

  # Fusionner les données
  result = pd.concat([tx_mortalite_ville, tx_mortalite_epci, tx_mortalite_dpt, tx_mortalite_reg, tx_mortalite_france])

  # Épurer le tableau
  result = result[['libgeo', 'tx_morta']]
  result.columns = ['Territoires', 'Taux de mortalité']
  result['Taux de mortalité'] = result['Taux de mortalité'].str.replace(',', '.').astype(float)
  result.reset_index(drop=True, inplace=True)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(result, x='Taux de mortalité', y='Territoires', orientation='h',
               title='Comparaison du taux de mortalité')

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
      st.write("Données des taux de mortalité")
      st.dataframe(result)
  elif selected == "Graphique":
      st.plotly_chart(fig)
  ############################################################################
  st.header("2.L'accessibilité aux soins")
  st.subheader("Accessibilité potentielle localisée (APL) à la médecine libérale")
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
      key="key2"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Médecins Généralistes":
      st.write("Données des Médecins Généralistes - Accessibilité Potentielle Localisée (APL)")
      st.caption("Unité : nombre de consultations accessibles par an et par habitant")
      st.dataframe(data_medecin_generaliste)
  elif selected == "Chirurgiens Dentistes":
      st.write("Données des Chirurgiens Dentistes de 65 ans et moins - Accessibilité Potentielle Localisée (APL)")
      st.caption("Unité : nombre d'équivalents temps-plein (ETP) accessibles pour 100 000 habitants standardisés")
      st.dataframe(data_chirurgiens_dentistes)
      st.caption("L’accessibilité aux chirurgiens-dentistes pour la ville de " + nom_commune + " et de " + apl_dentistes_commune + " ETP pour 100 000 habitants en " + last_year_apl + ". Pour comparaison, l’accessibilité nationale moyenne est de 59,0 ETP pour 100 000 habitants en 2021." )
      if float(apl_dentistes_commune) > float(apl_dentistes_france):
        st.caption(f"Votre commune est donc mieux dotée en chirurgiens-dentistes, soit une accessibilité {round(float(apl_dentistes_commune) / float(apl_dentistes_france), 1)} fois plus élevée. A titre de comparaison, l’accessibilité moyenne des 10 % de la population les moins bien dotés en chirurgiens-dentistes est de 15,3 ETP pour 100 000 habitants. Celle des 10 % les mieux dotés en chirurgiens-dentistes est de 111,0 ETP pour 100 000 habitants.")
      st.caption("Pour plus d'information : l'article de la dress du 01/02/2023 sur [l'accessibilité aux chirurgiens-dentistes](https://drees.solidarites-sante.gouv.fr/jeux-de-donnees-communique-de-presse/accessibilite-aux-soins-de-premier-recours-de-fortes)")
  elif selected == "Sages Femmes":
      st.write("Données des Sages Femmes - Accessibilité Potentielle Localisée (APL)")
      st.caption("Unité : nombre d'équivalents temps-plein (ETP) accessibles pour 100 000 habitants standardisés")
      st.dataframe(data_sages_femmes)
  elif selected == "Infirmiers":
      st.write("Données des Infirmiers de 65 ans et moins - Accessibilité Potentielle Localisée (APL)")
      st.caption("Unité : nombre d'équivalents temps-plein (ETP) accessibles pour 100 000 habitants standardisés")
      st.dataframe(data_infirmiers)
  elif selected == "Kinés":
      st.write("Données des Kinés de 65 ans et moins - Accessibilité Potentielle Localisée (APL)")
      st.caption("Unité : nombre d'équivalents temps-plein (ETP) accessibles pour 100 000 habitants standardisés")
      st.dataframe(data_kines)


  #############################################
  st.header("3. Accès aux droits et aux soins")
  st.subheader("Les Affections de Longue Durée (ALD)")
  st.caption("Source : xxx. Parue le XXXX - Millésime 2022")
  st.caption("L’allocation affection de longue durée (ALD) permet la prise en charge à 100% \
              des soins apportés à une personne souffrant de maladies chroniques.  \
              Ces maladies reconnues figurent dans une liste officielle d’une trentaine \
              d’affections. On peut y voir le diabète, les maladies de Parkinson et \
              d’Alzheimer, la scoliose ou encore la tuberculose.")

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
      key="key3"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write(f"Données des Affections de Longue Durée (ALD) en {last_year_ald}")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)

  #####################
  st.subheader("Les bénéficiaires de la CSS")
  st.caption("Source : xxx. Parue le XXXX - Millésime 2023")
  last_year_css = "2023"

  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(fichier, code, column_code='codgeo'):
      df = pd.read_csv(fichier, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df

  # Commune
  df_css_non_participative_commune = load_data(f"./sante/acces_droits/css_non_participative/css_non_participative_commune_{last_year_css}.csv", code_commune)
  df_css_participative_commune = load_data(f"./sante/acces_droits/css_participative/css_participative_commune_{last_year_css}.csv", code_commune)
  data_commune = pd.DataFrame({
      'Territoires': [nom_commune],
      'CSS non participative': df_css_non_participative_commune['css_non_participative'].values[0],
      'CSS participative': df_css_participative_commune['css_participative'].values[0]
  })

  # EPCI
  df_css_non_participative_epci = load_data(f"./sante/acces_droits/css_non_participative/css_non_participative_epci_{last_year_css}.csv", code_epci)
  df_css_participative_epci = load_data(f"./sante/acces_droits/css_participative/css_participative_epci_{last_year_css}.csv", code_epci)
  data_epci = pd.DataFrame({
      'Territoires': [nom_epci],
      'CSS non participative': df_css_non_participative_epci['css_non_participative'].values[0],
      'CSS participative': df_css_participative_epci['css_participative'].values[0]
  })

  # Département
  df_css_non_participative_departement = load_data(f"./sante/acces_droits/css_non_participative/css_non_participative_departement_{last_year_css}.csv", code_departement)
  df_css_participative_departement = load_data(f"./sante/acces_droits/css_participative/css_participative_departement_{last_year_css}.csv", code_departement)
  data_departement = pd.DataFrame({
      'Territoires': [nom_departement],
      'CSS non participative': df_css_non_participative_departement['css_non_participative'].values[0],
      'CSS participative': df_css_participative_departement['css_participative'].values[0]
  })

  # Région
  df_css_non_participative_region = load_data(f"./sante/acces_droits/css_non_participative/css_non_participative_region_{last_year_css}.csv", code_region)
  df_css_participative_region = load_data(f"./sante/acces_droits/css_participative/css_participative_region_{last_year_css}.csv", code_region)
  data_region = pd.DataFrame({
      'Territoires': [nom_region],
      'CSS non participative': df_css_non_participative_region['css_non_participative'].values[0],
      'CSS participative': df_css_participative_region['css_participative'].values[0]
  })

  # France
  df_css_non_participative_france = load_data(f"./sante/acces_droits/css_non_participative/css_non_participative_france_{last_year_css}.csv", '1111')
  df_css_participative_france = load_data(f"./sante/acces_droits/css_participative/css_participative_france_{last_year_css}.csv", '1111')
  data_france = pd.DataFrame({
      'Territoires': ['France'],
      'CSS non participative': df_css_non_participative_france['css_non_participative'].values[0],
      'CSS participative': df_css_participative_france['css_participative'].values[0]
  })

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Convertir les colonnes 'CSS non participative' et 'CSS participative' en numérique si nécessaire
  all_data['CSS non participative'] = all_data['CSS non participative'].astype(str).str.replace(',', '.').astype(float)
  all_data['CSS participative'] = all_data['CSS participative'].astype(str).str.replace(',', '.').astype(float)

  # Créer le graphique interactif en barres horizontales pour les deux variables
  fig = px.bar(all_data.melt(id_vars='Territoires', value_vars=['CSS non participative', 'CSS participative']),
               x='value', y='Territoires', color='variable', barmode='group',
               title=f"Comparaison des parts de CSS non participative et participative en {last_year_css}",
               labels={'value': 'Part des bénéficiaires', 'variable': 'Type de CSS'})

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique"],  # required
      icons=["table", "bar-chart"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key15"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write(f"Part des bénéficiaires de la CSS non participative et participative en {last_year_css}")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)


  #####################
  st.subheader("Part des bénéficiaires de la pension d'invalidité")
  st.caption("Source : xxx. Parue le XXXX - Millésime 2023")

  last_year_pension = "2023"

  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(fichier, code, column_code='codgeo'):
      df = pd.read_csv(fichier, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df

  # Commune
  df_pension_invalidite_commune = load_data(f"./sante/acces_droits/pension_invalidite/pension_invalidite_commune_{last_year_pension}.csv", code_commune)
  data_commune = pd.DataFrame({
      'Territoires': [nom_commune],
      'Pension d\'invalidité': df_pension_invalidite_commune['pension_invalidite'].values[0]
  })

  # EPCI
  df_pension_invalidite_epci = load_data(f"./sante/acces_droits/pension_invalidite/pension_invalidite_epci_{last_year_pension}.csv", code_epci)
  data_epci = pd.DataFrame({
      'Territoires': [nom_epci],
      'Pension d\'invalidité': df_pension_invalidite_epci['pension_invalidite'].values[0]
  })

  # Département
  df_pension_invalidite_departement = load_data(f"./sante/acces_droits/pension_invalidite/pension_invalidite_departement_{last_year_pension}.csv", code_departement)
  data_departement = pd.DataFrame({
      'Territoires': [nom_departement],
      'Pension d\'invalidité': df_pension_invalidite_departement['pension_invalidite'].values[0]
  })

  # Région
  df_pension_invalidite_region = load_data(f"./sante/acces_droits/pension_invalidite/pension_invalidite_region_{last_year_pension}.csv", code_region)
  data_region = pd.DataFrame({
      'Territoires': [nom_region],
      'Pension d\'invalidité': df_pension_invalidite_region['pension_invalidite'].values[0]
  })

  # France
  df_pension_invalidite_france = load_data(f"./sante/acces_droits/pension_invalidite/pension_invalidite_france_{last_year_pension}.csv", '1111')
  data_france = pd.DataFrame({
      'Territoires': ['France'],
      'Pension d\'invalidité': df_pension_invalidite_france['pension_invalidite'].values[0]
  })

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Convertir la colonne 'Pension d'invalidité' en numérique si nécessaire
  all_data['Pension d\'invalidité'] = all_data['Pension d\'invalidité'].astype(str).str.replace(',', '.').astype(float)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Pension d\'invalidité', y='Territoires', orientation='h',
               title=f"Comparaison de la part des bénéficiaires de la pension d'invalidité en {last_year_pension}")

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique"],  # required
      icons=["table", "bar-chart"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key16"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write(f"Part des bénéficiaires de la pension d'invalidité en {last_year_pension}")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)

  ####################
  st.subheader('Part des bénéficiaires sans médecin traitant déclaré')
  st.caption("Source : xxx. Parue le XXXX - Millésime 2023")

  last_year_medecin = "2023"
  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(fichier, code, column_code='codgeo'):
      df = pd.read_csv(fichier, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df

  # Commune
  df_sans_medecin_commune = load_data(f"./sante/acces_droits/sans_medecin_traitant_declare/sans_medecin_traitant_declare_commune_{last_year_medecin}.csv", code_commune)
  data_commune = pd.DataFrame({
      'Territoires': [nom_commune],
      'Sans médecin traitant déclaré': df_sans_medecin_commune['sans_medecin_traitant_declare'].values[0]
  })

  # EPCI
  df_sans_medecin_epci = load_data(f"./sante/acces_droits/sans_medecin_traitant_declare/sans_medecin_traitant_declare_epci_{last_year_medecin}.csv", code_epci)
  data_epci = pd.DataFrame({
      'Territoires': [nom_epci],
      'Sans médecin traitant déclaré': df_sans_medecin_epci['sans_medecin_traitant_declare'].values[0]
  })

  # Département
  df_sans_medecin_departement = load_data(f"./sante/acces_droits/sans_medecin_traitant_declare/sans_medecin_traitant_declare_departement_{last_year_medecin}.csv", code_departement)
  data_departement = pd.DataFrame({
      'Territoires': [nom_departement],
      'Sans médecin traitant déclaré': df_sans_medecin_departement['sans_medecin_traitant_declare'].values[0]
  })

  # Région
  df_sans_medecin_region = load_data(f"./sante/acces_droits/sans_medecin_traitant_declare/sans_medecin_traitant_declare_region_{last_year_medecin}.csv", code_region)
  data_region = pd.DataFrame({
      'Territoires': [nom_region],
      'Sans médecin traitant déclaré': df_sans_medecin_region['sans_medecin_traitant_declare'].values[0]
  })

  # France
  df_sans_medecin_france = load_data(f"./sante/acces_droits/sans_medecin_traitant_declare/sans_medecin_traitant_declare_france_{last_year_medecin}.csv", '1111')
  data_france = pd.DataFrame({
      'Territoires': ['France'],
      'Sans médecin traitant déclaré': df_sans_medecin_france['sans_medecin_traitant_declare'].values[0]
  })

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Convertir la colonne 'Sans médecin traitant déclaré' en numérique si nécessaire
  all_data['Sans médecin traitant déclaré'] = all_data['Sans médecin traitant déclaré'].astype(str).str.replace(',', '.').astype(float)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Sans médecin traitant déclaré', y='Territoires', orientation='h',
               title=f"Comparaison de la part des bénéficiaires sans médecin traitant déclaré en {last_year_medecin}")

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique"],  # required
      icons=["table", "bar-chart"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key17"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write(f"Part des bénéficiaires sans médecin traitant déclaré en {last_year_medecin}")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)

  #####################
  st.subheader('Part des bénéficiaires sans acte généraliste sur les 24 derniers mois')
  st.caption("Source : xxx. Parue le XXXX - Millésime 2023")

  last_year_generaliste = "2023"
  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(fichier, code, column_code='codgeo'):
      df = pd.read_csv(fichier, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df

  # Commune
  df_sans_acte_generaliste_commune = load_data(f"./sante/acces_droits/sans_acte_generaliste_24mois/sans_acte_generaliste_24mois_commune_{last_year_generaliste}.csv", code_commune)
  data_commune = pd.DataFrame({
      'Territoires': [nom_commune],
      'Sans acte généraliste 24 mois': df_sans_acte_generaliste_commune['sans_acte_generaliste_24mois'].values[0]
  })

  # EPCI
  df_sans_acte_generaliste_epci = load_data(f"./sante/acces_droits/sans_acte_generaliste_24mois/sans_acte_generaliste_24mois_epci_{last_year_generaliste}.csv", code_epci)
  data_epci = pd.DataFrame({
      'Territoires': [nom_epci],
      'Sans acte généraliste 24 mois': df_sans_acte_generaliste_epci['sans_acte_generaliste_24mois'].values[0]
  })

  # Département
  df_sans_acte_generaliste_departement = load_data(f"./sante/acces_droits/sans_acte_generaliste_24mois/sans_acte_generaliste_24mois_departement_{last_year_generaliste}.csv", code_departement)
  data_departement = pd.DataFrame({
      'Territoires': [nom_departement],
      'Sans acte généraliste 24 mois': df_sans_acte_generaliste_departement['sans_acte_generaliste_24mois'].values[0]
  })

  # Région
  df_sans_acte_generaliste_region = load_data(f"./sante/acces_droits/sans_acte_generaliste_24mois/sans_acte_generaliste_24mois_region_{last_year_generaliste}.csv", code_region)
  data_region = pd.DataFrame({
      'Territoires': [nom_region],
      'Sans acte généraliste 24 mois': df_sans_acte_generaliste_region['sans_acte_generaliste_24mois'].values[0]
  })

  # France
  df_sans_acte_generaliste_france = load_data(f"./sante/acces_droits/sans_acte_generaliste_24mois/sans_acte_generaliste_24mois_france_{last_year_generaliste}.csv", '1111')
  data_france = pd.DataFrame({
      'Territoires': ['France'],
      'Sans acte généraliste 24 mois': df_sans_acte_generaliste_france['sans_acte_generaliste_24mois'].values[0]
  })

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Convertir la colonne 'Sans acte généraliste 24 mois' en numérique si nécessaire
  all_data['Sans acte généraliste 24 mois'] = all_data['Sans acte généraliste 24 mois'].astype(str).str.replace(',', '.').astype(float)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Sans acte généraliste 24 mois', y='Territoires', orientation='h',
               title=f"Comparaison de la part des bénéficiaires sans acte généraliste sur 24 mois en {last_year_generaliste}")

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique"],  # required
      icons=["table", "bar-chart"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key18"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write(f"Part des bénéficiaires sans acte généraliste sur 24 mois en {last_year_generaliste}")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)


  #########################
  st.subheader('Part des bénéficiaires sans consultation dentiste sur les 24 derniers mois')
  st.caption("Source : xxx. Parue le XXXX - Millésime 2023")
  last_year_dentiste = "2023"

  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(fichier, code, column_code='codgeo'):
      df = pd.read_csv(fichier, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df

  # Commune
  df_sans_consultation_dentiste_commune = load_data(f"./sante/acces_droits/sans_consultation_dentiste_24mois/sans_consultation_dentiste_24mois_commune_{last_year_dentiste}.csv", code_commune)
  data_commune = pd.DataFrame({
      'Territoires': [nom_commune],
      'Sans consultation dentiste 24 mois': df_sans_consultation_dentiste_commune['sans_consultation_dentiste_24mois'].values[0]
  })

  # EPCI
  df_sans_consultation_dentiste_epci = load_data(f"./sante/acces_droits/sans_consultation_dentiste_24mois/sans_consultation_dentiste_24mois_epci_{last_year_dentiste}.csv", code_epci)
  data_epci = pd.DataFrame({
      'Territoires': [nom_epci],
      'Sans consultation dentiste 24 mois': df_sans_consultation_dentiste_epci['sans_consultation_dentiste_24mois'].values[0]
  })

  # Département
  df_sans_consultation_dentiste_departement = load_data(f"./sante/acces_droits/sans_consultation_dentiste_24mois/sans_consultation_dentiste_24mois_departement_{last_year_dentiste}.csv", code_departement)
  data_departement = pd.DataFrame({
      'Territoires': [nom_departement],
      'Sans consultation dentiste 24 mois': df_sans_consultation_dentiste_departement['sans_consultation_dentiste_24mois'].values[0]
  })

  # Région
  df_sans_consultation_dentiste_region = load_data(f"./sante/acces_droits/sans_consultation_dentiste_24mois/sans_consultation_dentiste_24mois_region_{last_year_dentiste}.csv", code_region)
  data_region = pd.DataFrame({
      'Territoires': [nom_region],
      'Sans consultation dentiste 24 mois': df_sans_consultation_dentiste_region['sans_consultation_dentiste_24mois'].values[0]
  })

  # France
  df_sans_consultation_dentiste_france = load_data(f"./sante/acces_droits/sans_consultation_dentiste_24mois/sans_consultation_dentiste_24mois_france_{last_year_dentiste}.csv", '1111')
  data_france = pd.DataFrame({
      'Territoires': ['France'],
      'Sans consultation dentiste 24 mois': df_sans_consultation_dentiste_france['sans_consultation_dentiste_24mois'].values[0]
  })

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Convertir la colonne 'Sans consultation dentiste 24 mois' en numérique si nécessaire
  all_data['Sans consultation dentiste 24 mois'] = all_data['Sans consultation dentiste 24 mois'].astype(str).str.replace(',', '.').astype(float)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Sans consultation dentiste 24 mois', y='Territoires', orientation='h',
               title=f"Comparaison de la part des bénéficiaires sans consultation dentiste sur 24 mois en {last_year_dentiste}")

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique"],  # required
      icons=["table", "bar-chart"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key19"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write(f"Part des bénéficiaires sans consultation dentiste sur 24 mois en {last_year_dentiste}")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)

  #########################################
  st.subheader('Part des bénéficiaires sans recours aux soins sur les 24 derniers mois')
  st.caption("Source : xxx. Parue le XXXX - Millésime 2023")

  last_year_soins = "2023"

  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(fichier, code, column_code='codgeo'):
      df = pd.read_csv(fichier, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df

  # Commune
  df_sans_recours_soins_commune = load_data(f"./sante/acces_droits/sans_recours_soins_24mois/sans_recours_soins_24mois_commune_{last_year_soins}.csv", code_commune)
  data_commune = pd.DataFrame({
      'Territoires': [nom_commune],
      'Sans recours aux soins 24 mois': df_sans_recours_soins_commune['sans_recours_soins_24mois'].values[0]
  })

  # EPCI
  df_sans_recours_soins_epci = load_data(f"./sante/acces_droits/sans_recours_soins_24mois/sans_recours_soins_24mois_epci_{last_year_soins}.csv", code_epci)
  data_epci = pd.DataFrame({
      'Territoires': [nom_epci],
      'Sans recours aux soins 24 mois': df_sans_recours_soins_epci['sans_recours_soins_24mois'].values[0]
  })

  # Département
  df_sans_recours_soins_departement = load_data(f"./sante/acces_droits/sans_recours_soins_24mois/sans_recours_soins_24mois_departement_{last_year_soins}.csv", code_departement)
  data_departement = pd.DataFrame({
      'Territoires': [nom_departement],
      'Sans recours aux soins 24 mois': df_sans_recours_soins_departement['sans_recours_soins_24mois'].values[0]
  })

  # Région
  df_sans_recours_soins_region = load_data(f"./sante/acces_droits/sans_recours_soins_24mois/sans_recours_soins_24mois_region_{last_year_soins}.csv", code_region)
  data_region = pd.DataFrame({
      'Territoires': [nom_region],
      'Sans recours aux soins 24 mois': df_sans_recours_soins_region['sans_recours_soins_24mois'].values[0]
  })

  # France
  df_sans_recours_soins_france = load_data(f"./sante/acces_droits/sans_recours_soins_24mois/sans_recours_soins_24mois_france_{last_year_soins}.csv", '1111')
  data_france = pd.DataFrame({
      'Territoires': ['France'],
      'Sans recours aux soins 24 mois': df_sans_recours_soins_france['sans_recours_soins_24mois'].values[0]
  })

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Convertir la colonne 'Sans recours aux soins 24 mois' en numérique si nécessaire
  all_data['Sans recours aux soins 24 mois'] = all_data['Sans recours aux soins 24 mois'].astype(str).str.replace(',', '.').astype(float)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Sans recours aux soins 24 mois', y='Territoires', orientation='h',
               title=f"Comparaison de la part des bénéficiaires sans recours aux soins sur 24 mois en {last_year_soins}")

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique"],  # required
      icons=["table", "bar-chart"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key20"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write(f"Part des bénéficiaires sans recours aux soins sur 24 mois en {last_year_soins}")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)

  #############################################
  st.header("4. La prévention")
  st.subheader("Les bénéficiaires éligibles sans recours à la VAG sur les 24 derniers mois")
  st.caption("Source : Observatoire interrégime des situaitons de fragilité. Parue le XXXX - Millésime 2023")

  last_year_vag = "2023"

  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(fichier, code, column_code='codgeo'):
      df = pd.read_csv(fichier, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df['sans_vag_24mois'].values[0]

  # Commune
  tx_sans_vag_commune = load_data(f"./sante/prevention/vag/sans_vag_commune_{last_year_vag}.csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], 'Taux sans VAG 24 mois': [tx_sans_vag_commune]})

  # EPCI
  tx_sans_vag_epci = load_data(f"./sante/prevention/vag/sans_vag_epci_{last_year_vag}.csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], 'Taux sans VAG 24 mois': [tx_sans_vag_epci]})

  # Département
  tx_sans_vag_departement = load_data(f"./sante/prevention/vag/sans_vag_departement_{last_year_vag}.csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], 'Taux sans VAG 24 mois': [tx_sans_vag_departement]})

  # Région
  tx_sans_vag_region = load_data(f"./sante/prevention/vag/sans_vag_region_{last_year_vag}.csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], 'Taux sans VAG 24 mois': [tx_sans_vag_region]})

  # France
  tx_sans_vag_france = load_data(f"./sante/prevention/vag/sans_vag_france_{last_year_vag}.csv", '1111')
  data_france = pd.DataFrame({'Territoires': ['France'], 'Taux sans VAG 24 mois': [tx_sans_vag_france]})

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Taux sans VAG 24 mois', y='Territoires', orientation='h',
               title=f"Comparaison du taux sans VAG sur 24 mois en {last_year_vag}")

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique"],  # required
      icons=["table", "bar-chart"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key4"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write(f"Données des bénéficiaires éligibles sans recours à la VAG sur les 24 derniers mois en {last_year_vag}")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)


  ##############################
  st.subheader("Les bénéficiaires du Régime Général de 65 ans et plus sans recours à la VAG sur les 24 derniers mois")
  st.caption("Source : Observatoire interrégime des situaitons de fragilité. Parue le XXXX - Millésime 2023")

  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(fichier, code, column_code='codgeo'):
      df = pd.read_csv(fichier, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df['sans_vag_65p_24mois'].values[0]

  # Commune
  tx_sans_vag_65p_commune = load_data(f"./sante/prevention/vag_65p/sans_vag_65p_commune_{last_year_vag}.csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], 'Taux sans VAG 65 ans et plus 24 mois': [tx_sans_vag_65p_commune]})

  # EPCI
  tx_sans_vag_65p_epci = load_data(f"./sante/prevention/vag_65p/sans_vag_65p_epci_{last_year_vag}.csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], 'Taux sans VAG 65 ans et plus 24 mois': [tx_sans_vag_65p_epci]})

  # Département
  tx_sans_vag_65p_departement = load_data(f"./sante/prevention/vag_65p/sans_vag_65p_departement_{last_year_vag}.csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], 'Taux sans VAG 65 ans et plus 24 mois': [tx_sans_vag_65p_departement]})

  # Région
  tx_sans_vag_65p_region = load_data(f"./sante/prevention/vag_65p/sans_vag_65p_region_{last_year_vag}.csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], 'Taux sans VAG 65 ans et plus 24 mois': [tx_sans_vag_65p_region]})

  # France
  tx_sans_vag_65p_france = load_data(f"./sante/prevention/vag_65p/sans_vag_65p_france_{last_year_vag}.csv", '1111')
  data_france = pd.DataFrame({'Territoires': ['France'], 'Taux sans VAG 65 ans et plus 24 mois': [tx_sans_vag_65p_france]})

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Taux sans VAG 65 ans et plus 24 mois', y='Territoires', orientation='h',
               title=f"Comparaison du taux sans VAG sur 24 mois pour les 65 ans et plus en {last_year_vag}")

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique"],  # required
      icons=["table", "bar-chart"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key5"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write(f"Données des bénéficiaires éligibles sans recours à la VAG sur les 24 derniers mois pour les 65 ans et plus en {last_year_vag}")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)


  ##############################
  st.subheader('Les femmes de 20 à 64 ans sans consultation gynécologique sur les 24 derniers mois')
  st.caption("Source : xxx. Parue le XXXX - Millésime 2023")

  last_year_gynecologue = "2023"
  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(fichier, code, column_code='codgeo'):
      df = pd.read_csv(fichier, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df['sans_consultation_gynecologue_24mois'].values[0]

  # Commune
  tx_sans_gynecologue_commune = load_data(f"./sante/prevention/gynecologue/sans_consultation_gynecologue_24mois_commune_{last_year_gynecologue}.csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], 'Taux sans consultation gynécologique 24 mois': [tx_sans_gynecologue_commune]})

  # EPCI
  tx_sans_gynecologue_epci = load_data(f"./sante/prevention/gynecologue/sans_consultation_gynecologue_24mois_epci_{last_year_gynecologue}.csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], 'Taux sans consultation gynécologique 24 mois': [tx_sans_gynecologue_epci]})

  # Département
  tx_sans_gynecologue_departement = load_data(f"./sante/prevention/gynecologue/sans_consultation_gynecologue_24mois_departement_{last_year_gynecologue}.csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], 'Taux sans consultation gynécologique 24 mois': [tx_sans_gynecologue_departement]})

  # Région
  tx_sans_gynecologue_region = load_data(f"./sante/prevention/gynecologue/sans_consultation_gynecologue_24mois_region_{last_year_gynecologue}.csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], 'Taux sans consultation gynécologique 24 mois': [tx_sans_gynecologue_region]})

  # France
  tx_sans_gynecologue_france = load_data(f"./sante/prevention/gynecologue/sans_consultation_gynecologue_24mois_france_{last_year_gynecologue}.csv", '1111')
  data_france = pd.DataFrame({'Territoires': ['France'], 'Taux sans consultation gynécologique 24 mois': [tx_sans_gynecologue_france]})

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Taux sans consultation gynécologique 24 mois', y='Territoires', orientation='h',
               title=f"Comparaison du taux sans consultation gynécologique sur 24 mois en {last_year_gynecologue}")

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique"],  # required
      icons=["table", "bar-chart"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key6"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write(f"Données des bénéficiaires éligibles de 20 à 64 ans sans consultation gynécologique sur les 24 derniers mois en {last_year_gynecologue}")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)

  ##############################
  st.subheader("Les femmes de 50 à 74 ans n'ayant pas eu d'acte de mammographie sur les 24 derniers mois")
  st.caption("Source : Observatoire Interrégime des situations de fragilité. Parue le XXXX - Millésime 2023")

  last_year_mammographie = "2023"
  # Charger et filtrer les données pour chaque niveau géographique
  def load_data(fichier, code, column_code='codgeo'):
      df = pd.read_csv(fichier, dtype={column_code: str}, sep=';')
      df = df.loc[df[column_code] == code]
      return df['sans_mammographie_24mois'].values[0]

  # Commune
  tx_sans_mammographie_commune = load_data(f"./sante/prevention/mammographie/sans_mammographie_24mois_commune_{last_year_mammographie}.csv", code_commune)
  data_commune = pd.DataFrame({'Territoires': [nom_commune], 'Taux des femmes sans acte de mammographie 24 mois': [tx_sans_mammographie_commune]})

  # EPCI
  tx_sans_mammographie_epci = load_data(f"./sante/prevention/mammographie/sans_mammographie_24mois_epci_{last_year_mammographie}.csv", code_epci)
  data_epci = pd.DataFrame({'Territoires': [nom_epci], 'Taux des femmes sans acte de mammographie 24 mois': [tx_sans_mammographie_epci]})

  # Département
  tx_sans_mammographie_departement = load_data(f"./sante/prevention/mammographie/sans_mammographie_24mois_departement_{last_year_mammographie}.csv", code_departement)
  data_departement = pd.DataFrame({'Territoires': [nom_departement], 'Taux des femmes sans acte de mammographie 24 mois': [tx_sans_mammographie_departement]})

  # Région
  tx_sans_mammographie_region = load_data(f"./sante/prevention/mammographie/sans_mammographie_24mois_region_{last_year_mammographie}.csv", code_region)
  data_region = pd.DataFrame({'Territoires': [nom_region], 'Taux des femmes sans acte de mammographie 24 mois': [tx_sans_mammographie_region]})

  # France
  tx_sans_mammographie_france = load_data(f"./sante/prevention/mammographie/sans_mammographie_24mois_france_{last_year_mammographie}.csv", '1111')
  data_france = pd.DataFrame({'Territoires': ['France'], 'Taux des femmes sans acte de mammographie 24 mois': [tx_sans_mammographie_france]})

  # Fusionner les données
  all_data = pd.concat([data_commune, data_epci, data_departement, data_region, data_france])

  # Réinitialiser l'index et renommer les colonnes
  all_data.reset_index(drop=True, inplace=True)

  # Créer le graphique interactif en barres horizontales
  fig = px.bar(all_data, x='Taux des femmes sans acte de mammographie 24 mois', y='Territoires', orientation='h',
               title=f"Comparaison du taux des femmes sans acte de mammographie sur 24 mois en {last_year_mammographie}")

  # Créer le menu d'options pour les onglets
  selected = option_menu(
      menu_title=None,  # required
      options=["Tableau", "Graphique"],  # required
      icons=["table", "bar-chart"],  # optional
      menu_icon="cast",  # optional
      default_index=0,  # optional
      orientation="horizontal",
      key="key7"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write(f"Données des bénéficiaires femmes de 50 à 74 ans n'ayant pas eu un acte de mammographie sur les 24 derniers mois en {last_year_mammographie}")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)

  ###############################################################
  st.header("5.La prévention par le sport")
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
      key="key8"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write("Données des licenciés sportifs en 2019")
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)

  ###################################################
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
      key="key9"
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
      key="key10"
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
      key="key11"
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
      key="key12"
  )

  # Afficher le contenu basé sur l'onglet sélectionné
  if selected == "Tableau":
      st.write("Données des licenciés sportifs de 60 ans et plus en " +  last_year_licsport)
      st.dataframe(all_data)
  elif selected == "Graphique":
      st.plotly_chart(fig)
  elif selected == "Dont femmes":
      st.dataframe(all_data_f)
