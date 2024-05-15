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
import streamlit_folium as folium_st
from shapely.geometry import Polygon, MultiPolygon
import streamlit.components.v1 as components
import fiona
import matplotlib.pyplot as plt
import plotly.express as px
import jenkspy

def app():
  # Appeler la fonction et récupérer les informations
  (code_commune, nom_commune, code_epci, nom_epci, code_departement, nom_departement, code_region, nom_region) = afficher_infos_commune()

  #############################################################################
  st.title("🏘 Logement")
  last_year = "2020"
  st.header('1.Part des logements HLM')
  st.subheader("Iris")
  st.caption("Paru le 19/10/2023 - Millésime 2020")
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
    df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_RP':"Résidences principales (" + annee + ")" ,'P' + year + '_RP_LOCHLMV':"résidences principales HLM loué vide (" + annee + ")" ,'indice':"Part des résidences principales HLM (" + annee + ")" })
    return df_indice_com

  indice_part_log_hlm_iris =part_log_hlm_iris("./logement/base-ic-logement-" + last_year + ".csv",code_commune, last_year)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(indice_part_log_hlm_iris)
  ####################
  # Carte Part logements sociaux
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
  gdf = gdf.merge(indice_part_log_hlm_iris, left_on='fields.iris_code', right_on="Code de l'iris")

  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]

  # Nettoyage des données en supprimant les NaN et conversion en numérique
  gdf["Part des résidences principales HLM (" + last_year + ")"] = pd.to_numeric(gdf["Part des résidences principales HLM (" + last_year + ")"], errors='coerce')
  gdf = gdf.dropna(subset=["Part des résidences principales HLM (" + last_year + ")"])

  # Vérification du nombre de valeurs uniques
  unique_values = gdf["Part des résidences principales HLM (" + last_year + ")"].nunique()

  if unique_values >= 5:
      # Calcul des breaks avec la méthode de Jenks si suffisamment de valeurs uniques
      breaks = jenkspy.jenks_breaks(gdf["Part des résidences principales HLM (" + last_year + ")"], 5)
      m = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

      # Ajouter la carte choroplèthe
      folium.Choropleth(
          geo_data=gdf.set_index("Code de l'iris"),
          name='choropleth',
          data=gdf,
          columns=["Code de l'iris", "Part des résidences principales HLM (" + last_year + ")"],
          key_on='feature.id',
          fill_color='YlOrRd',
          fill_opacity=0.7,
          line_opacity=0.2,
          color='#ffffff',
          weight=3,
          opacity=1.0,
          legend_name='Part des logements HLM parmi les résidences principales',
          bins=breaks
      ).add_to(m)

      style_function = lambda x: {'fillColor': '#ffffff', 'color':'#000000', 'fillOpacity': 0.1, 'weight': 0.1}
      highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.50, 'weight': 0.1}
      NIL = folium.features.GeoJson(
          gdf,
          style_function=style_function,
          control=False,
          highlight_function=highlight_function,
          tooltip=folium.features.GeoJsonTooltip(
              fields=["Nom de l'iris", "Part des résidences principales HLM (" + last_year + ")"],
              aliases=['Iris: ', "Part des logements sociaux :"],
              style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
          )
      )
      m.add_child(NIL)
      m.keep_in_front(NIL)
      st.subheader("Part des logements HLM parmi les résidences principales par IRIS")
      folium_st.folium_static(m)
  else:
      # Pas assez de valeurs uniques pour une visualisation significative
      st.warning("Pas assez de diversité dans les données pour afficher une carte choroplèthe significative.")


  #################################
  st.subheader('Comparaison')
  st.caption("Agrégation à partir de l'échelle communale. Paru le 27/06/2023 - Millésime 2020")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    # Commune
    def part_hlm_com(fichier, code_commune, annee):
      df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str,"REG": str}, sep = ';')
      year = annee[-2:]
      df_ville = df.loc[df["CODGEO"]==code_commune]
      nb_residences_princ = df_ville['P'+ year + '_RP'].iloc[0]
      nb_residences_hlm = df_ville['P'+ year + '_RP_LOCHLMV'].iloc[0]
      part_hlm = (nb_residences_hlm / nb_residences_princ)*100
      df_part_hlm = pd.DataFrame(data=part_hlm, columns = ['Part des hlm ' + annee], index = [nom_commune])
      return df_part_hlm
    indice_part_hlm_com = part_hlm_com("./logement/commune/base-cc-logement-" + last_year + ".csv",code_commune, last_year)
    # EPCI
    def part_hlm_epci(fichier, epci, annee):
      epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
      df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str,"REG": str}, sep = ';')
      year = annee[-2:]
      df_epci_com = pd.merge(df[['CODGEO', 'P' + year + '_RP', 'P' + year + '_RP_LOCHLMV']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
      df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI','P'+ year +'_RP' , 'P'+ year + '_RP_LOCHLMV']]
      nb_residences = df_epci.loc[:, 'P'+ year + '_RP'].sum()
      nb_residences_hlm = df_epci.loc[:, 'P'+ year + '_RP_LOCHLMV'].sum()
      part_hlm = (nb_residences_hlm / nb_residences)*100
      df_part_hlm = pd.DataFrame(data=part_hlm, columns = ['Part des hlm ' + annee], index = [nom_epci])
      return df_part_hlm
    indice_part_hlm_epci = part_hlm_epci("./logement/commune/base-cc-logement-" + last_year + ".csv",code_epci,last_year)
    # Département
    def part_hlm_departement(fichier, departement, annee):
      df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str,"REG": str},sep = ';')
      year = annee[-2:]
      df_departement = df.loc[df["DEP"]==departement, ['P' + year + '_RP' , 'P' + year + '_RP_LOCHLMV']]
      nb_residences = df_departement.loc[:, 'P' + year + '_RP'].sum()
      nb_residences_hlm = df_departement.loc[:, 'P'+ year + '_RP_LOCHLMV'].sum()
      part_hlm = (nb_residences_hlm / nb_residences)*100
      df_part_hlm = pd.DataFrame(data=part_hlm, columns = ['Part des hlm ' + annee], index = [nom_departement])
      return df_part_hlm
    indice_part_hlm_dpt =part_hlm_departement("./logement/commune/base-cc-logement-" + last_year + ".csv",code_departement, last_year)
    # Région
    def part_hlm_region(fichier, region, annee):
      df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str, "REG": str},sep = ';')
      year = annee[-2:]
      df_region = df.loc[df["REG"]==region, ['P' + year + '_RP' , 'P' + year + '_RP_LOCHLMV']]
      nb_residences = df_region.loc[:, 'P' + year + '_RP'].sum()
      nb_residences_hlm = df_region.loc[:, 'P'+ year + '_RP_LOCHLMV'].sum()
      part_hlm = (nb_residences_hlm / nb_residences)*100
      df_part_hlm = pd.DataFrame(data=part_hlm, columns = ['Part des hlm ' + annee], index = [nom_region])
      return df_part_hlm
    indice_part_hlm_region =part_hlm_region("./logement/commune/base-cc-logement-" + last_year + ".csv",code_region, last_year)
    # France
    def part_hlm_france(fichier, annee):
      df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str, "REG": str}, sep = ';')
      year = annee[-2:]
      nb_residences = df.loc[:, 'P'+ year + '_RP'].sum()
      nb_residences_hlm = df.loc[:, 'P'+ year + '_RP_LOCHLMV'].sum()
      part_hlm = ( nb_residences_hlm / nb_residences ) * 100
      df_part_hlm = pd.DataFrame(data=part_hlm, columns = ["Part des hlm " + annee], index = ["France"])
      return df_part_hlm
    indice_part_hlm_fr = part_hlm_france("./logement/commune/base-cc-logement-" + last_year + ".csv",last_year)
    # Comparaison
    def part_hlm_global(annee):
        df = pd.concat([indice_part_hlm_com,indice_part_hlm_epci, indice_part_hlm_dpt, indice_part_hlm_region, indice_part_hlm_fr])
        year = annee
        return df
    part_hlm_fin = part_hlm_global(last_year)
    st.table(part_hlm_fin)
  #################################
  st.subheader("Évolution")
  st.caption("Agrégation à partir de l'échelle communale. Paru le 27/06/2023 - Millésime 2020")

  def evolution_part_hlm(generate_data_function, *args):
    evolution = []
    for annee in range(2015, 2021):
        fichier = f"./logement/commune/base-cc-logement-{annee}.csv"
        df_part_hlm = generate_data_function(fichier, *args, str(annee))
        if not df_part_hlm.empty:
            part_hlm = df_part_hlm.iloc[0, 0]  # Première colonne de la première ligne
            evolution.append({'Année': annee, 'Part HLM': part_hlm})
        else:
            evolution.append({'Année': annee, 'Part HLM': None})
    return pd.DataFrame(evolution)

  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    df_evolution_hlm_com = evolution_part_hlm(part_hlm_com, code_commune)
    df_evolution_hlm_epci = evolution_part_hlm(part_hlm_epci, code_epci)
    df_evolution_hlm_departement = evolution_part_hlm(part_hlm_departement, code_departement)
    df_evolution_hlm_region = evolution_part_hlm(part_hlm_region, code_region)
    df_evolution_hlm_France = evolution_part_hlm(part_hlm_france)

    df_evolution_hlm_final = df_evolution_hlm_com.merge(df_evolution_hlm_epci, on='Année', suffixes=('_com', '_epci'))\
                                                 .merge(df_evolution_hlm_departement, on='Année')\
                                                 .merge(df_evolution_hlm_region, on='Année', suffixes=('_dep', '_reg'))\
                                                 .merge(df_evolution_hlm_France, on='Année')
    # Renommez les colonnes pour clarifier
    df_evolution_hlm_final.columns = ['Année', nom_commune, nom_epci, nom_departement, nom_region, 'France']
    # Graphique
    fig = px.line(df_evolution_hlm_final, x='Année', y=df_evolution_hlm_final.columns[1:],
                  title='Évolution de la part des HLM par territoire',
                  labels={'value': 'Part des HLM (%)', 'variable': 'Territoire'})
    fig.update_traces(mode='lines+markers')
    st.plotly_chart(fig)
  ###############################################################################
  st.header('2.Part des résidences principales en suroccupation')
  st.subheader("Iris")
  st.caption("Paru le 19/10/2023 - Millésime 2020")
  def part_log_suroccup_iris(fichier, code, annee) :
    df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, sep=";")
    year = annee[-2:]
    df_indice = df.loc[df['COM'] == code]
    df_indice = df_indice[['IRIS', 'LIBIRIS', 'P'+ year + '_RP','C' + year +'_RP_HSTU1P_SUROCC']]
    df_indice['indice'] = (df_indice['C'+ year + '_RP_HSTU1P_SUROCC'] / df_indice['P' + year +'_RP']) * 100
    df_indice_com = df_indice.rename(columns={'IRIS': "Code de l'iris",'LIBIRIS': "Nom de l'iris", 'P' + year +'_RP':"Résidences principales (" + annee + ")" ,'P' + year + '_RP_HSTU1P_SUROCC':"résidences principales en suroccupation (" + annee + ")" ,'indice':"Part des résidences en suroccupation (" + annee + ")" })
    return df_indice_com
  indice_part_log_suroccup_iris = part_log_suroccup_iris("./logement/base-ic-logement-" + last_year + ".csv",code_commune, last_year)

  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(indice_part_log_suroccup_iris)

  ####################
  # Carte Part logements suroccupés
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
  gdf = gdf.merge(indice_part_log_suroccup_iris, left_on='fields.iris_code', right_on="Code de l'iris")

  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]

  # Nettoyage des données en supprimant les NaN et conversion en numérique
  gdf["Part des résidences en suroccupation (" + last_year + ")"] = pd.to_numeric(gdf["Part des résidences en suroccupation (" + last_year + ")"], errors='coerce')
  gdf = gdf.dropna(subset=["Part des résidences en suroccupation (" + last_year + ")"])

  # Vérification du nombre de valeurs uniques
  unique_values = gdf["Part des résidences en suroccupation (" + last_year + ")"].nunique()

  if unique_values >= 5:
      # Calcul des breaks avec la méthode de Jenks si suffisamment de valeurs uniques
      breaks = jenkspy.jenks_breaks(gdf["Part des résidences en suroccupation (" + last_year + ")"], 5)
      m = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

      # Ajouter la carte choroplèthe
      folium.Choropleth(
          geo_data=gdf.set_index("Code de l'iris"),
          name='choropleth',
          data=gdf,
          columns=["Code de l'iris", "Part des résidences en suroccupation (" + last_year + ")"],
          key_on='feature.id',
          fill_color='YlOrRd',
          fill_opacity=0.7,
          line_opacity=0.2,
          color='#ffffff',
          weight=3,
          opacity=1.0,
          legend_name='Part des logements suroccupés',
          bins=breaks
      ).add_to(m)

      style_function = lambda x: {'fillColor': '#ffffff', 'color':'#000000', 'fillOpacity': 0.1, 'weight': 0.1}
      highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.50, 'weight': 0.1}
      NIL = folium.features.GeoJson(
          gdf,
          style_function=style_function,
          control=False,
          highlight_function=highlight_function,
          tooltip=folium.features.GeoJsonTooltip(
              fields=["Nom de l'iris", "Part des résidences en suroccupation (" + last_year + ")"],
              aliases=['Iris: ', "Part des logements suroccupés :"],
              style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
          )
      )
      m.add_child(NIL)
      m.keep_in_front(NIL)
      st.subheader("Part des logements suroccupés par IRIS")
      # Afficher la carte dans Streamlit
      folium_st.folium_static(m)
  else:
      # Pas assez de valeurs uniques pour une visualisation significative
      st.warning("Pas assez de diversité dans les données pour afficher une carte choroplèthe significative.")

  #############
  st.subheader('Comparaison')
  st.caption("Agrégation à partir de l'échelle communale. Paru le 27/06/2023 - Millésime 2020")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    # Commune
    def part_suroccup_com(fichier, code_commune, annee):
      df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str,"REG": str}, sep = ';')
      year = annee[-2:]
      df_ville = df.loc[df["CODGEO"] == code_commune]
      nb_residences_princ = df_ville['P'+ year + '_RP'].iloc[0]
      nb_residences_suroccup = df_ville['C'+ year + '_RP_HSTU1P_SUROCC'].iloc[0]
      part_suroccup = (nb_residences_suroccup / nb_residences_princ) * 100
      df_part_suroccup = pd.DataFrame(data=part_suroccup, columns = ['Part des suroccup ' + annee], index = [nom_commune])
      return df_part_suroccup
    indice_part_suroccup_com = part_suroccup_com("./logement/commune/base-cc-logement-" + last_year + ".csv",code_commune, last_year)
    # EPCI
    def part_suroccup_epci(fichier, epci, annee):
      epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
      df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str, "REG": str}, sep = ';')
      year = annee[-2:]
      df_epci_com = pd.merge(df[['CODGEO', 'P' + year + '_RP', 'C' + year + '_RP_HSTU1P_SUROCC']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
      df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI','P'+ year +'_RP' , 'C'+ year + '_RP_HSTU1P_SUROCC']]
      nb_residences = df_epci.loc[:, 'P'+ year + '_RP'].sum()
      nb_residences_suroccup = df_epci.loc[:, 'C'+ year + '_RP_HSTU1P_SUROCC'].sum()
      part_suroccup = (nb_residences_suroccup / nb_residences)*100
      df_part_suroccup = pd.DataFrame(data=part_suroccup, columns = ['Part des suroccup ' + annee], index = [nom_epci])
      return df_part_suroccup
    indice_part_suroccup_epci = part_suroccup_epci("./logement/commune/base-cc-logement-" + last_year + ".csv",code_epci,last_year)
    # Département
    def part_suroccup_departement(fichier, departement, annee):
      df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str, "REG": str}, sep = ';')
      year = annee[-2:]
      df_departement = df.loc[df["DEP"] == departement, ['DEP','P'+ year +'_RP' , 'C'+ year + '_RP_HSTU1P_SUROCC']]
      nb_residences = df_departement.loc[:, 'P'+ year + '_RP'].sum()
      nb_residences_suroccup = df_departement.loc[:, 'C'+ year + '_RP_HSTU1P_SUROCC'].sum()
      part_suroccup = (nb_residences_suroccup / nb_residences)*100
      df_part_suroccup = pd.DataFrame(data=part_suroccup, columns = ["Part des suroccup " + annee], index = [nom_departement])
      return df_part_suroccup
    indice_part_suroccup_dpt =part_suroccup_departement("./logement/commune/base-cc-logement-" + last_year + ".csv",code_departement, last_year)
    # Région
    def part_suroccup_region(fichier, region, annee):
      df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str, "REG": str}, sep = ';')
      year = annee[-2:]
      df_region = df.loc[df["REG"] == region, ['REG', 'P'+ year +'_RP' , 'C'+ year + '_RP_HSTU1P_SUROCC']]
      nb_residences = df_region.loc[:, 'P'+ year + '_RP'].sum()
      nb_residences_suroccup = df_region.loc[:, 'C'+ year + '_RP_HSTU1P_SUROCC'].sum()
      part_suroccup = (nb_residences_suroccup / nb_residences)*100
      df_part_suroccup = pd.DataFrame(data=part_suroccup, columns = ["Part des suroccup " + annee], index = [nom_region])
      return df_part_suroccup
    indice_part_suroccup_region = part_suroccup_region("./logement/commune/base-cc-logement-" + last_year + ".csv",code_region, last_year)
    # France
    def part_suroccup_france(fichier, annee):
      df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str, "REG": str}, sep = ';')
      year = annee[-2:]
      nb_residences = df.loc[:, 'P'+ year + '_RP'].sum()
      nb_residences_suroccup = df.loc[:, 'C'+ year + '_RP_HSTU1P_SUROCC'].sum()
      part_suroccup = ( nb_residences_suroccup / nb_residences ) * 100
      df_part_suroccup = pd.DataFrame(data=part_suroccup, columns = ["Part des suroccup " + annee], index = ["France"])
      return df_part_suroccup
    indice_part_suroccup_fr = part_suroccup_france("./logement/commune/base-cc-logement-" + last_year + ".csv",last_year)
    # Comparaison
    def part_suroccup_global(annee):
        df = pd.concat([indice_part_suroccup_com,indice_part_suroccup_epci, indice_part_suroccup_dpt, indice_part_suroccup_region, indice_part_suroccup_fr])
        year = annee
        return df
    part_suroccup_fin = part_suroccup_global(last_year)
    st.write(part_suroccup_fin)
  ##############
  st.subheader("b.Evolution")
  st.caption("Agrégation à partir de l'échelle communale. Paru le 27/06/2023 - Millésime 2020")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    def evolution_part_suroccup(generate_data_function, *args):
      evolution = []
      for annee in range(2017, 2021):  # De 2017 à 2020
          fichier = f"./logement/commune/base-cc-logement-{annee}.csv"
          df_part_suroccup = generate_data_function(fichier, *args, str(annee))
          if not df_part_suroccup.empty:
              part_suroccup = df_part_suroccup.iloc[0, 0]  # Première colonne de la première ligne
              evolution.append({'Année': annee, 'Part suroccup': part_suroccup})
          else:
              evolution.append({'Année': annee, 'Part suroccup': None})

      return pd.DataFrame(evolution)
    df_evolution_suroccup_com = evolution_part_suroccup(part_suroccup_com, code_commune)
    df_evolution_suroccup_epci = evolution_part_suroccup(part_suroccup_epci, code_epci)
    df_evolution_suroccup_departement = evolution_part_suroccup(part_suroccup_departement, code_departement)
    df_evolution_suroccup_region = evolution_part_suroccup(part_suroccup_region, code_region)
    df_evolution_suroccup_France = evolution_part_suroccup(part_suroccup_france)

    df_evolution_suroccup_final = df_evolution_suroccup_com.merge(df_evolution_suroccup_epci, on='Année', suffixes=('_com', '_epci'))\
                                                          .merge(df_evolution_suroccup_departement, on='Année')\
                                                          .merge(df_evolution_suroccup_region, on='Année', suffixes=('_dep', '_reg'))\
                                                          .merge(df_evolution_suroccup_France, on='Année')

    df_evolution_suroccup_final.columns = ['Année', nom_commune, nom_epci, nom_departement, nom_region, 'France']
    # Graphique
    fig = px.line(df_evolution_suroccup_final, x='Année', y=df_evolution_suroccup_final.columns[1:],
                  title='Évolution de la part des logements en suroccupation par territoire',
                  labels={'value': 'Part des logements en suroccupation (%)', 'variable': 'Territoire'})

    fig.update_traces(mode='lines+markers')
    # Traitement des années comme des catégories
    fig.update_xaxes(type='category')
    # Afficher le graphique dans Streamlit
    st.plotly_chart(fig)

