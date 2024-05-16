import streamlit as st
from pages.utils import afficher_infos_commune
from pages.utils import remove_comma, round_to_two, round_to_zero
import pandas as pd
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
import jenkspy

def app(code_commune, nom_commune, code_epci, nom_epci, code_departement, nom_departement, code_region, nom_region):
  # Appeler la fonction et récupérer les informations

  #############################################################################

  st.title('🧑‍🍳👷‍♂️👩‍🔧👨‍⚕️ ACTIVITÉ ET EMPLOI')
  st.header("Taux de personnes salariées en temps partiel ")
  st.caption("Paru le : 19/10/2023 - dernier millésime 2020")
  annee_reference = "2020"
  year = annee_reference[-2:]
  df = pd.read_csv("./activite/iris/base-ic-activite-residents-" + annee_reference + ".csv", dtype={"IRIS":str, "REG": str, "DEP": str, "UU2020": str, "COM": str, "TRIRIS": str, "GRD_QUART": str, "MODIF_IRIS": str, "LAB_IRIS": str}, sep=";")
  df_iris = df.loc[df['COM'] == code_commune]
  df_iris = df_iris[["IRIS", "LIBIRIS", "P" + year + "_SAL15P_TP", "P" + year + "_SAL15P"]]
  df_iris = df_iris.reset_index(drop=True)
  df_iris["tx_temps_partiel"] = ( df_iris["P" + year + "_SAL15P_TP"] / df_iris["P" + year + "_SAL15P"] ) * 100
  df_iris["tx_temps_partiel"] = df_iris["tx_temps_partiel"].round(2)
  st.write(df_iris)

  #################################
  #Comparaison
  #Commune
  df = pd.read_csv("./activite/commune/base-cc-caract_emp-" + annee_reference + ".csv", dtype={"CODGEO":str, "REG": str, "DEP": str}, sep=";")
  df_com = df.loc[df['CODGEO'] == code_commune]
  df_com = df_com[["CODGEO", "LIBGEO", "P" + year + "_SAL15P_TP", "P" + year + "_SAL15P"]]
  df_com = df_com.reset_index(drop=True)
  tpartiel_com = ( df_com["P" + year +"_SAL15P_TP"].iloc[0] / df_com["P" + year +"_SAL15P"].iloc[0] ) * 100
  #EPCI
  epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci = pd.merge(df[['CODGEO', "P" + year + "_SAL15P_TP", "P" + year + "_SAL15P" ]], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci.loc[df_epci["EPCI"] == str(code_epci), ['EPCI', 'LIBEPCI', 'CODGEO',"P" + year + "_SAL15P_TP", "P" + year + "_SAL15P"]]
  df_epci = df_epci.reset_index(drop=True)
  tpartiel_epci = (df_epci.loc[:, "P" + year +"_SAL15P_TP"].sum() / df_epci["P" + year +"_SAL15P"].sum()) * 100
  #DEP
  df_dep = df.loc[df['DEP'] == code_departement]
  df_dep = df_dep[["P" + year + "_SAL15P_TP", "P" + year + "_SAL15P"]]
  df_dep = df_dep.reset_index(drop=True)
  tpartiel_dep = (df_dep.loc[:, "P" + year +"_SAL15P_TP"].sum() / df_dep["P" + year +"_SAL15P"].sum()) * 100
  #REG
  df_reg = df.loc[df['REG'] == code_region]
  df_reg = df_reg[["P" + year + "_SAL15P_TP", "P" + year + "_SAL15P"]]
  df_reg = df_reg.reset_index(drop=True)
  tpartiel_reg = (df_reg.loc[:, "P" + year +"_SAL15P_TP"].sum() / df_reg["P" + year +"_SAL15P"].sum()) * 100
  #France
  tpartiel_fr = (df.loc[:, "P" + year +"_SAL15P_TP"].sum() / df["P" + year +"_SAL15P"].sum()) * 100
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Part du temps partiel de 15 à 64 ans - " + annee_reference + " (en %)": [tpartiel_com, tpartiel_epci, tpartiel_dep, tpartiel_reg, tpartiel_fr]}
  df_global_tp = pd.DataFrame(data=d)
  df_global_tp["tx_temps_partiel"] = df_global_tp["Part du temps partiel de 15 à 64 ans - " + annee_reference + " (en %)"].round(2)
  st.write(df_global_tp)
  #####################
  # Carte Temps partiel
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
  gdf = gdf.merge(df_iris, left_on='fields.iris_code', right_on="IRIS")

  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]

  # Nettoyer les données en supprimant les NaN et en s'assurant que toutes les valeurs sont numériques
  gdf['tx_temps_partiel'] = pd.to_numeric(gdf['tx_temps_partiel'], errors='coerce')
  gdf = gdf.dropna(subset=['tx_temps_partiel'])

  # Vérifier le nombre de valeurs uniques
  unique_values = gdf['tx_temps_partiel'].nunique()

  if unique_values >= 5:
      # Assez de valeurs uniques pour calculer 5 breaks avec la méthode de Jenks
      breaks = jenkspy.jenks_breaks(gdf['tx_temps_partiel'], 5)
      m = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

      # Ajouter la carte choroplèthe
      folium.Choropleth(
          geo_data=gdf.set_index("IRIS"),
          name='choropleth',
          data=gdf,
          columns=["IRIS", "tx_temps_partiel"],
          key_on='feature.id',
          fill_color='YlOrRd',
          fill_opacity=0.7,
          line_opacity=0.2,
          color='#ffffff',
          weight=3,
          opacity=1.0,
          legend_name='Taux de temps partiel',
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
              fields=["LIBIRIS", "tx_temps_partiel"],
              aliases=['Iris: ', "Taux de temps partiel :"],
              style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
          )
      )
      m.add_child(NIL)
      m.keep_in_front(NIL)
      st.subheader("Taux de temps partiel par IRIS")
      # Afficher la carte dans Streamlit
      folium_st.folium_static(m)
  else:
      # Pas assez de valeurs uniques pour une visualisation significative
      st.warning("Pas assez de diversité dans les données pour afficher une carte choroplèthe significative.")

  ###########################################################################
  st.header("Taux de chomage des 15-64 ans")
  st.caption("Paru le : 19/10/2023 - dernier millésime 2020")
  last_year = "2020"
  year = last_year[-2:]
  df = pd.read_csv("./activite/iris/base-ic-activite-residents-" + last_year + ".csv", dtype={"IRIS":str, "REG": str, "DEP": str, "UU2020": str, "COM": str, "TRIRIS": str, "GRD_QUART": str, "MODIF_IRIS": str, "LAB_IRIS": str}, sep=";")
  df_iris = df.loc[df['COM'] == code_commune]
  df_iris = df_iris[["IRIS", "LIBIRIS", "P" + year + "_CHOM1564", "P" + year +"_ACT1564"]]
  df_iris = df_iris.reset_index(drop=True)
  df_iris["tx_chomage"] = ( df_iris["P" + year + "_CHOM1564"] / df_iris["P" + year + "_ACT1564"] ) * 100
  df_iris["tx_chomage"] = df_iris["tx_chomage"].round(2)
  df_iris["P" + year +"_ACT1564"] = df_iris["P" + year +"_ACT1564"].apply(remove_comma)
  st.write(df_iris)
  #############################

  # Comparaison
  #Commune
  df = pd.read_csv("./activite/commune/base-cc-emploi-pop-active-" + last_year + ".csv", dtype={"CODGEO":str, "REG": str, "DEP": str}, sep=";")
  df_com = df.loc[df['CODGEO'] == code_commune]
  df_com = df_com[["CODGEO", "LIBGEO", "P" + year + "_CHOM1564", "P" + year + "_ACT1564"]]
  df_com = df_com.reset_index(drop=True)
  chom_com = (df_com.loc[:, "P" + year +"_CHOM1564"].iloc[0] / df_com["P" + year +"_ACT1564"].iloc[0]) * 100
  #EPCI
  epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci = pd.merge(df[['CODGEO', "P" + year + "_CHOM1564", "P" + year + "_ACT1564" ]], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci.loc[df_epci["EPCI"] == str(code_epci), ['EPCI', 'LIBEPCI', 'CODGEO',"P" + year + "_CHOM1564", "P" + year + "_ACT1564"]]
  df_epci = df_epci.reset_index(drop=True)
  chom_epci = (df_epci.loc[:, "P" + year +"_CHOM1564"].sum() / df_epci["P" + year +"_ACT1564"].sum()) * 100
  #DEP
  df_dep = df.loc[df['DEP'] == code_departement]
  df_dep = df_dep[["P" + year + "_CHOM1564", "P" + year + "_ACT1564"]]
  df_dep = df_dep.reset_index(drop=True)
  chom_dep = (df_dep.loc[:, "P" + year +"_CHOM1564"].sum() / df_dep["P" + year +"_ACT1564"].sum()) * 100
  #REG
  df_reg = df.loc[df['REG'] == code_region]
  df_reg = df_reg[["P" + year + "_CHOM1564", "P" + year + "_ACT1564"]]
  df_reg = df_reg.reset_index(drop=True)
  chom_reg = (df_reg.loc[:, "P" + year +"_CHOM1564"].sum() / df_reg["P" + year +"_ACT1564"].sum()) * 100
  #France
  chom_fr = (df.loc[:, "P" + year +"_CHOM1564"].sum() / df["P" + year +"_ACT1564"].sum()) * 100
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Part des chômeurs de 15 à 64 ans - " + annee_reference + " (en %)": [chom_com, chom_epci, chom_dep, chom_reg, chom_fr]}
  df = pd.DataFrame(data=d)
  df["Part des chômeurs de 15 à 64 ans - " + annee_reference + " (en %)"] = df["Part des chômeurs de 15 à 64 ans - " + annee_reference + " (en %)"].round(2)
  st.write(df)
  ########################

  # Carte Taux de comage
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
  gdf = gdf.merge(df_iris, left_on='fields.iris_code', right_on="IRIS")

  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]

  # Nettoyage des données en supprimant les NaN et conversion en numérique
  gdf['tx_chomage'] = pd.to_numeric(gdf['tx_chomage'], errors='coerce')
  gdf = gdf.dropna(subset=['tx_chomage'])

  # Vérification du nombre de valeurs uniques
  unique_values = gdf['tx_chomage'].nunique()

  if unique_values >= 5:
      # Calcul des breaks avec la méthode de Jenks si suffisamment de valeurs uniques
      breaks = jenkspy.jenks_breaks(gdf['tx_chomage'], 5)
      m = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

      # Ajouter la carte choroplèthe
      folium.Choropleth(
          geo_data=gdf.set_index("IRIS"),
          name='choropleth',
          data=gdf,
          columns=["IRIS", "tx_chomage"],
          key_on='feature.id',
          fill_color='YlOrRd',
          fill_opacity=0.7,
          line_opacity=0.2,
          color='#ffffff',
          weight=3,
          opacity=1.0,
          legend_name='Part des chômeurs de 15-64 ans',
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
              fields=["LIBIRIS", "tx_chomage"],
              aliases=['Iris: ', "Taux de chômage :"],
              style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
          )
      )
      m.add_child(NIL)
      m.keep_in_front(NIL)
      st.subheader("Part des chômeurs de 15-64 ans par IRIS")
      # Afficher la carte dans Streamlit
      folium_st.folium_static(m)
  else:
      # Pas assez de valeurs uniques pour une visualisation significative
      st.warning("Pas assez de diversité dans les données pour afficher une carte choroplèthe significative.")

  ###########################################################################

  st.header("Taux d'emploi des 15-64 ans")
  st.subheader("Zoom QPV")
  last_year_qpv = "2022"
  def tx_emploi_qpv(fichier, nom_ville, annee) :
    fp_qpv = "./qpv.geojson"
    map_qpv_df = gpd.read_file(fp_qpv)
    year = annee[-2:]
    df = pd.read_csv(fichier, dtype={"CODGEO": str}, sep=";")
    map_qpv_df_code_insee = map_qpv_df.merge(df, left_on='code_qp', right_on='CODGEO')
    map_qpv_df_code_insee_extract = map_qpv_df_code_insee[['nom_qp', 'code_qp', 'commune_qp','code_insee', 'TX_TOT_EMPL' ]]
    map_qpv_df_code_insee_extract
    df_qpv = map_qpv_df_code_insee_extract.loc[map_qpv_df_code_insee_extract["commune_qp"].str.contains(r'(?<!-)\b{}\b'.format(nom_ville))]
    df_qpv = df_qpv.reset_index(drop=True)
    df_qpv = df_qpv[['code_qp', 'nom_qp','commune_qp', 'TX_TOT_EMPL']]
    df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", 'TX_TOT_EMPL' : "Taux d'emploi des 15/65 ans " + last_year_qpv})
    return df_qpv

  tx_emploi_qpv = tx_emploi_qpv('./activite/insertion-pro-qpv/IPRO_' + last_year_qpv + '.csv', nom_commune, last_year_qpv)
  st.table(tx_emploi_qpv)

  st.header("Part des emplois à durée limitée parmi les emplois (ou emplois précaires)")
  st.subheader("Zoom QPV")

  def tx_emploi_limit_qpv(fichier, nom_ville, annee) :
    fp_qpv = "./qpv.geojson"
    map_qpv_df = gpd.read_file(fp_qpv)
    year = annee[-2:]
    df = pd.read_csv(fichier, dtype={"CODGEO": str}, sep=";")
    map_qpv_df_code_insee = map_qpv_df.merge(df, left_on='code_qp', right_on='CODGEO')
    if int(annee) >= 2021:
      map_qpv_df_code_insee_extract = map_qpv_df_code_insee[['nom_qp', 'code_qp', 'commune_qp','code_insee', 'TX_TOT_EDLIM' ]]
      map_qpv_df_code_insee_extract
      df_qpv = map_qpv_df_code_insee_extract.loc[map_qpv_df_code_insee_extract["commune_qp"].str.contains(r'(?<!-)\b{}\b'.format(nom_ville))]
      df_qpv = df_qpv.reset_index(drop=True)
      df_qpv = df_qpv[['code_qp', 'nom_qp','commune_qp', 'TX_TOT_EDLIM']]
      df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", 'TX_TOT_EDLIM' : "Part des emplois à durée limitée " + last_year_qpv})
    else:
      map_qpv_df_code_insee_extract = map_qpv_df_code_insee[['nom_qp', 'code_qp', 'commune_qp','code_insee', 'TX_TOT_EPREC' ]]
      map_qpv_df_code_insee_extract
      df_qpv = map_qpv_df_code_insee_extract.loc[map_qpv_df_code_insee_extract["commune_qp"].str.contains(r'(?<!-)\b{}\b'.format(nom_ville))]
      df_qpv = df_qpv.reset_index(drop=True)
      df_qpv = df_qpv[['code_qp', 'nom_qp','commune_qp', 'TX_TOT_EPREC']]
      df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", 'TX_TOT_EPREC' : "Part des emplois à durée limitée " + last_year_qpv})
    return df_qpv

  tx_emploi_limit_qpv = tx_emploi_limit_qpv('./activite/insertion-pro-qpv/IPRO_' + last_year_qpv + '.csv', nom_commune, last_year_qpv)
  st.table(tx_emploi_limit_qpv)

  st.caption("Emploi à durée limitée : contrat d'apprentissage, Placés par une agence d'intérim, Emplois-jeunes, CES, contrats de qualification, stagiaires rémunérés en entreprise, autres emplois à durée limitée")
