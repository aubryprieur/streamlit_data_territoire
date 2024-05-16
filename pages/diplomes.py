import streamlit as st
from pages.utils import afficher_infos_commune
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
import plotly.express as px
import jenkspy


def app(code_commune, nom_commune, code_epci, nom_epci, code_departement, nom_departement, code_region, nom_region):
  # Appeler la fonction et récupérer les informations

  #############################################################################
  st.title('🧑‍🎓👨‍🎓 DIPLÔME')
  st.header('1.Sans diplome')
  last_year = "2020"
  st.caption("La part de non diplômés parmi les individus de 15 ans et plus non scolarisés nous renseigne \
  significativement sur la part des personnes a priori les plus vulnérables sur le marché de l’emploi. En effet, \
  plus le niveau d’étude obtenu est bas plus les risques de chômage et/ou de non emploi sont élevés. Cette \
  part étant par ailleurs très corrélée avec la catégorie sociale des individus, cet indicateur nous renseigne \
  par ailleurs sur le degré de précarité d’une population. \
  Son intérêt réside principalement dans sa prise en compte dans les politiques publiques :\
   - Politique de l’emploi et d’insertion professionnelle\
   - Etudes et formation")
  st.subheader("Iris")
  st.caption("Paru le 19/10/2023 - Millésime 2020")
  def part_sans_diplome_iris(fichier, code, annee) :
    df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, sep=";", header=0)
    df_indice = df.loc[df['COM'] == code]
    year = annee[-2:]
    df_indice = df_indice[['COM','IRIS', 'P' + year + '_NSCOL15P_DIPLMIN', 'P' + year + '_NSCOL15P']]
    df_indice = df_indice.replace(',','.', regex=True)
    df_indice['P'+ year + '_NSCOL15P_DIPLMIN'] = df_indice['P'+ year + '_NSCOL15P_DIPLMIN'].astype(float).to_numpy()
    df_indice['P' + year +'_NSCOL15P'] = df_indice['P' + year +'_NSCOL15P'].astype(float).to_numpy()
    df_indice['indice'] = np.where(df_indice['P' + year +'_NSCOL15P'] < 1,df_indice['P' + year +'_NSCOL15P'], (df_indice['P'+ year + '_NSCOL15P_DIPLMIN']/ df_indice['P' + year +'_NSCOL15P']*100))
    df_indice['indice'] = df_indice['indice'].astype(float).to_numpy()
    communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
    df_indice_com = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_indice[['IRIS','P' + year +'_NSCOL15P', 'P' + year + '_NSCOL15P_DIPLMIN','indice']], left_on='CODE_IRIS', right_on="IRIS")
    df_indice_com = df_indice_com[['CODE_IRIS','LIB_IRIS','P' + year +'_NSCOL15P', 'P' + year + '_NSCOL15P_DIPLMIN','indice']]
    df_indice_com['P' + year +'_NSCOL15P'] = df_indice_com['P' + year +'_NSCOL15P'].apply(np.int64)
    df_indice_com['P' + year +'_NSCOL15P_DIPLMIN'] = df_indice_com['P' + year +'_NSCOL15P_DIPLMIN'].apply(np.int64)
    df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_NSCOL15P':"Personnes non scolarisées de 15 ans ou plus (" + annee + ")", 'P' + year +'_NSCOL15P_DIPLMIN':"Personnes non scolarisées de 15 ans ou plus titulaires d'aucun diplôme ou au plus un CEP (" + annee + ")" ,'indice':"Part des personnes non scolarisées sans diplôme (" + annee + ") en %" })
    return df_indice_com
  indice_part_sans_diplome_iris =part_sans_diplome_iris("./diplome/base-ic-diplomes-formation-" + last_year + ".csv",str(code_commune), last_year)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(indice_part_sans_diplome_iris)

 ####################
  # Carte Sans diplome
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
  gdf = gdf.merge(indice_part_sans_diplome_iris, left_on='fields.iris_code', right_on="Code de l'iris")

  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]

  # Nettoyage des données en supprimant les NaN et conversion en numérique
  gdf["Part des personnes non scolarisées sans diplôme (" + last_year + ") en %"] = pd.to_numeric(gdf["Part des personnes non scolarisées sans diplôme (" + last_year + ") en %"], errors='coerce')
  gdf = gdf.dropna(subset=["Part des personnes non scolarisées sans diplôme (" + last_year + ") en %"])

  # Vérification du nombre de valeurs uniques
  unique_values = gdf["Part des personnes non scolarisées sans diplôme (" + last_year + ") en %"].nunique()

  if unique_values >= 5:
      # Calcul des breaks avec la méthode de Jenks si suffisamment de valeurs uniques
      breaks = jenkspy.jenks_breaks(gdf["Part des personnes non scolarisées sans diplôme (" + last_year + ") en %"], 5)
      m = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

      # Ajouter la carte choroplèthe
      folium.Choropleth(
          geo_data=gdf.set_index("Code de l'iris"),
          name='choropleth',
          data=gdf,
          columns=["Code de l'iris", "Part des personnes non scolarisées sans diplôme (" + last_year + ") en %"],
          key_on='feature.id',
          fill_color='YlOrRd',
          fill_opacity=0.7,
          line_opacity=0.2,
          color='#ffffff',
          weight=3,
          opacity=1.0,
          legend_name='Part des personnes non scolarisées sans diplôme',
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
              fields=["Nom de l'iris", "Part des personnes non scolarisées sans diplôme (" + last_year + ") en %"],
              aliases=['Iris: ', "Part des personnes non scolarisées sans diplôme :"],
              style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
          )
      )
      m.add_child(NIL)
      m.keep_in_front(NIL)
      st.subheader("Part des personnes non scolarisées sans diplôme par IRIS")
      # Afficher la carte dans Streamlit
      folium_st.folium_static(m)
  else:
      # Pas assez de valeurs uniques pour une visualisation significative
      st.warning("Pas assez de diversité dans les données pour afficher une carte choroplèthe significative.")


  #################################
  st.subheader('Comparaison')
  st.caption("Agrégation à partir de l'échelle communale. Paru le 27/06/2023 - Millésime 2020")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    # Commune
    def part_sans_diplome_com(fichier, code_commune, annee):
        df = pd.read_csv(fichier, dtype={"DEP": str, "REG": str, "CODGEO": str}, sep = ';')
        year = annee[-2:]
        df_ville = df.loc[ df["CODGEO"] == code_commune ]
        df_ville["part_sans_diplome"] = round((df_ville['P' + year + '_NSCOL15P_DIPLMIN'] / df_ville['P' + year + '_NSCOL15P'])*100,2)
        df_part_sans_diplome = df_ville[["LIBGEO", "part_sans_diplome"]]
        return df_part_sans_diplome
    indice_sans_diplome_com = part_sans_diplome_com("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv",code_commune, last_year)
    # EPCI
    def part_sans_diplome_epci(fichier, epci, annee):
        epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
        df = pd.read_csv(fichier, dtype={"DEP": str, "REG": str, "CODGEO": str}, sep = ';')
        year = annee[-2:]
        df_epci_com = pd.merge(df[['CODGEO', 'LIBGEO', 'P' + year + '_NSCOL15P', 'P' + year + '_NSCOL15P_DIPLMIN']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
        df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'LIBGEO','P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_DIPLMIN']]
        pop_non_scol = df_epci.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        pop_non_scol_sans_diplome = df_epci.loc[:, 'P'+ year + '_NSCOL15P_DIPLMIN'].astype(float).sum()
        part_pop_non_scol_sans_diplome = round((pop_non_scol_sans_diplome / pop_non_scol)*100,2)
        df_part_sans_diplome = pd.DataFrame({'part_sans_diplome': [part_pop_non_scol_sans_diplome]})
        df_part_sans_diplome['LIBGEO'] = df_epci['LIBEPCI'].unique()[0]
        return df_part_sans_diplome
    indice_sans_diplome_epci = part_sans_diplome_epci("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv",code_epci,last_year)
    # Département
    def part_sans_diplome_departement(fichier, departement, nom_departement, annee):
        df = pd.read_csv(fichier, dtype={"DEP": str, "REG": str, "CODGEO": str},sep = ';')
        year = annee[-2:]
        df_departement = df.loc[df["DEP"] == departement, ['DEP', 'P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_DIPLMIN']]
        pop_non_scol = df_departement.loc[:, 'P' + year + '_NSCOL15P'].sum()
        pop_non_scol_sans_diplome = df_departement.loc[:, 'P'+ year + '_NSCOL15P_DIPLMIN'].astype(float).sum()
        part_pop_non_scol_sans_diplome = round((pop_non_scol_sans_diplome / pop_non_scol)*100,2)
        df_part_sans_diplome = pd.DataFrame({'part_sans_diplome': [part_pop_non_scol_sans_diplome]})
        df_part_sans_diplome['LIBGEO'] = nom_departement
        return df_part_sans_diplome
    valeurs_sans_diplome_dep = part_sans_diplome_departement("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv",code_departement, nom_departement, last_year)
    # Région
    def part_sans_diplome_region(fichier, region, nom_region, annee):
        df = pd.read_csv(fichier, dtype={"DEP": str, "REG": str, "CODGEO": str},sep = ';')
        year = annee[-2:]
        df_region = df.loc[df["REG"] == region, ['REG', 'P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_DIPLMIN']]
        pop_non_scol = df_region.loc[:, 'P' + year + '_NSCOL15P'].sum()
        pop_non_scol_sans_diplome = df_region.loc[:, 'P'+ year + '_NSCOL15P_DIPLMIN'].astype(float).sum()
        part_pop_non_scol_sans_diplome = round((pop_non_scol_sans_diplome / pop_non_scol)*100,2)
        df_part_sans_diplome = pd.DataFrame({'part_sans_diplome': [part_pop_non_scol_sans_diplome]})
        df_part_sans_diplome['LIBGEO'] = nom_region
        return df_part_sans_diplome
    valeurs_sans_diplome_reg = part_sans_diplome_region("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv",code_region, nom_region, last_year)
    # France
    def part_sans_diplome_France(fichier, annee):
        df = pd.read_csv(fichier, dtype={"DEP": str, "REG": str, "CODGEO": str}, sep = ';')
        year = annee[-2:]
        select_pop_non_scol = df.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        select_pop_non_scol_sans_diplome = df.loc[:, 'P'+ year + '_NSCOL15P_DIPLMIN'].astype(float).sum()
        part_pop_non_scol_sans_diplome = round((select_pop_non_scol_sans_diplome / select_pop_non_scol)*100, 2)
        df_part_sans_diplome = pd.DataFrame({'part_sans_diplome': [part_pop_non_scol_sans_diplome]})
        df_part_sans_diplome['LIBGEO'] = "France"
        return df_part_sans_diplome
    valeur_part_sans_diplome_fr = part_sans_diplome_France("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv",last_year)

    # Comparaison
    def sans_diplome_global(annee):
        df = pd.concat([indice_sans_diplome_com,indice_sans_diplome_epci, valeurs_sans_diplome_dep, valeurs_sans_diplome_reg, valeur_part_sans_diplome_fr])
        year = annee
        df = df.reset_index(drop=True)
        return df
    part_sans_diplome_fin = sans_diplome_global(last_year)
    st.table(part_sans_diplome_fin)
  #########################################
  st.subheader("b.Evolution")
  st.caption("Agrégation à partir de l'échelle communale. Paru le 27/06/2023 - Millésime 2020")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    def evolution_part_sans_diplome(generate_data_function, column_name, *args):
        evolution = []
        for annee in range(2015, 2021):
            fichier = f"./diplome/commune/base-cc-diplomes-formation-{annee}.csv"
            df_part_sans_diplome = generate_data_function(fichier, *args, str(annee))
            if not df_part_sans_diplome.empty:
                part_sans_diplome = df_part_sans_diplome['part_sans_diplome'].iloc[0]
                evolution.append({'Année': annee, column_name: part_sans_diplome})
            else:
                evolution.append({'Année': annee, column_name: None})

        return pd.DataFrame(evolution)

    df_evolution_com = evolution_part_sans_diplome(part_sans_diplome_com, nom_commune, code_commune)
    df_evolution_epci = evolution_part_sans_diplome(part_sans_diplome_epci, nom_epci, code_epci)
    df_evolution_departement = evolution_part_sans_diplome(part_sans_diplome_departement, nom_departement, code_departement, nom_departement)
    df_evolution_region = evolution_part_sans_diplome(part_sans_diplome_region, nom_region, code_region, nom_region)
    df_evolution_France = evolution_part_sans_diplome(part_sans_diplome_France, 'France')
    df_evolution_final = df_evolution_com.merge(df_evolution_epci, on='Année')\
                                         .merge(df_evolution_departement, on='Année')\
                                         .merge(df_evolution_region, on='Année')\
                                         .merge(df_evolution_France, on='Année')
    st.write(df_evolution_final)
    #Graphique
    fig = px.line(df_evolution_final, x='Année', y=[nom_commune,
                                                     nom_epci,
                                                     nom_departement,
                                                     nom_region,
                                                     'France'],
                  labels={'value': 'Part des personnes sans diplôme (%)', 'variable': 'Territoire'},
                  title='Évolution de la part des personnes sans diplôme par territoire')
    fig.update_traces(mode='lines+markers')
    st.plotly_chart(fig)
  ##############################################################################
  st.header('2.Études supérieures')
  st.subheader("Iris")
  st.caption("Paru le 19/10/2023 - Millésime 2020")
  def part_etude_sup_iris(fichier, code, annee) :
    df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, sep=";", header=0)
    year = annee[-2:]
    df_indice = df.loc[df['COM'] == code]
    if int(annee) >= 2017:
      df_indice = df_indice[['COM','IRIS', 'P' + year + '_NSCOL15P_SUP2','P' + year + '_NSCOL15P_SUP34','P' + year + '_NSCOL15P_SUP5', 'P' + year + '_NSCOL15P']]
      df_indice = df_indice.replace(',','.', regex=True)
      df_indice['P'+ year + '_NSCOL15P_SUP2'] = df_indice['P'+ year + '_NSCOL15P_SUP2'].astype(float).to_numpy()
      df_indice['P'+ year + '_NSCOL15P_SUP34'] = df_indice['P'+ year + '_NSCOL15P_SUP34'].astype(float).to_numpy()
      df_indice['P'+ year + '_NSCOL15P_SUP5'] = df_indice['P'+ year + '_NSCOL15P_SUP5'].astype(float).to_numpy()
      df_indice['P' + year +'_NSCOL15P'] = df_indice['P' + year +'_NSCOL15P'].astype(float).to_numpy()
      df_indice['indice'] = np.where(df_indice['P' + year +'_NSCOL15P'] < 1,df_indice['P' + year +'_NSCOL15P'], ((df_indice['P'+ year + '_NSCOL15P_SUP2'] + df_indice['P'+ year + '_NSCOL15P_SUP34'] + df_indice['P'+ year + '_NSCOL15P_SUP5'])/ df_indice['P' + year +'_NSCOL15P']*100))
      df_indice['indice'] = df_indice['indice'].astype(float).to_numpy()
      communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
      df_indice_com = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_indice[['IRIS','P' + year +'_NSCOL15P', 'P' + year + '_NSCOL15P_SUP2','P' + year + '_NSCOL15P_SUP34','P' + year + '_NSCOL15P_SUP5','indice']], left_on='CODE_IRIS', right_on="IRIS")
      df_indice_com = df_indice_com[['CODE_IRIS','LIB_IRIS','P' + year +'_NSCOL15P', 'P' + year + '_NSCOL15P_SUP2','P' + year + '_NSCOL15P_SUP34','P' + year + '_NSCOL15P_SUP5','indice']]
      df_indice_com['P' + year +'_NSCOL15P'] = df_indice_com['P' + year +'_NSCOL15P'].apply(np.int64)
      df_indice_com['P' + year +'_NSCOL15P_SUP2'] = df_indice_com['P' + year +'_NSCOL15P_SUP2'].apply(np.int64)
      df_indice_com['P' + year +'_NSCOL15P_SUP34'] = df_indice_com['P' + year +'_NSCOL15P_SUP34'].apply(np.int64)
      df_indice_com['P' + year +'_NSCOL15P_SUP5'] = df_indice_com['P' + year +'_NSCOL15P_SUP5'].apply(np.int64)
      df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_NSCOL15P':"Personnes non scolarisées de 15 ans ou plus (" + annee + ")", 'P' + year +'_NSCOL15P_SUP2':"Titulaire d'un BAC+2 (" + annee + ")" ,'P' + year +'_NSCOL15P_SUP34':"Titulaire d'un BAC+3 ou 4 (" + annee + ")" ,'P' + year +'_NSCOL15P_SUP5':"Titulaire d'un BAC+5 ou sup (" + annee + ")" ,'indice':"Part des personnes non scolarisées titulaires d'un diplôme de l'enseignement supérieur (" + annee + ") en %" })
      return df_indice_com
    else:
      df_indice = df.loc[df['COM'] == code]
      df_indice = df_indice[['IRIS','COM', 'P' + year + '_NSCOL15P_SUP', 'P' + year + '_NSCOL15P']]
      df_indice = df_indice.replace(',','.', regex=True)
      df_indice['P'+ year + '_NSCOL15P_SUP'] = df_indice['P'+ year + '_NSCOL15P_SUP'].astype(float).to_numpy()
      df_indice['P' + year +'_NSCOL15P'] = df_indice['P' + year +'_NSCOL15P'].astype(float).to_numpy()
      df_indice['indice'] = np.where(df_indice['P' + year +'_NSCOL15P'] < 1,df_indice['P' + year +'_NSCOL15P'], (df_indice['P'+ year + '_NSCOL15P_SUP']/ df_indice['P' + year +'_NSCOL15P']*100))
      df_indice['indice'] = df_indice['indice'].astype(float).to_numpy()
      communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
      df_indice_com = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_indice[['IRIS','P' + year +'_NSCOL15P', 'P' + year + '_NSCOL15P_SUP','indice']], left_on='CODE_IRIS', right_on="IRIS")
      df_indice_com = df_indice_com[['CODE_IRIS','LIB_IRIS','P' + year +'_NSCOL15P', 'P' + year + '_NSCOL15P_SUP','indice']]
      df_indice_com['P' + year +'_NSCOL15P'] = df_indice_com['P' + year +'_NSCOL15P'].apply(np.int64)
      df_indice_com['P' + year +'_NSCOL15P_SUP'] = df_indice_com['P' + year +'_NSCOL15P_SUP'].apply(np.int64)
      df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_NSCOL15P':"Personnes non scolarisées de 15 ans ou plus (" + annee + ")", 'P' + year +'_NSCOL15P_SUP':"Titulaire d'un diplôme de l'enseignement supérieur (" + annee + ")" ,'indice':"Part des personnes non scolarisées titulaires d'un diplôme de l'enseignement supérieur (" + annee + ") en %" })
      return df_indice_com

  indice_part_etude_sup_iris =part_etude_sup_iris("./diplome/base-ic-diplomes-formation-" + last_year + ".csv",code_commune, last_year)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(indice_part_etude_sup_iris)
  #################
  # Carte Part diplome etudes supérieures
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
  gdf = gdf.merge(indice_part_etude_sup_iris, left_on='fields.iris_code', right_on="Code de l'iris")

  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]

  # Nettoyage des données en supprimant les NaN et conversion en numérique
  gdf["Part des personnes non scolarisées titulaires d'un diplôme de l'enseignement supérieur (" + last_year + ") en %"] = pd.to_numeric(gdf["Part des personnes non scolarisées titulaires d'un diplôme de l'enseignement supérieur (" + last_year + ") en %"], errors='coerce')
  gdf = gdf.dropna(subset=["Part des personnes non scolarisées titulaires d'un diplôme de l'enseignement supérieur (" + last_year + ") en %"])

  # Vérification du nombre de valeurs uniques
  unique_values = gdf["Part des personnes non scolarisées titulaires d'un diplôme de l'enseignement supérieur (" + last_year + ") en %"].nunique()

  if unique_values >= 5:
      # Calcul des breaks avec la méthode de Jenks si suffisamment de valeurs uniques
      breaks = jenkspy.jenks_breaks(gdf["Part des personnes non scolarisées titulaires d'un diplôme de l'enseignement supérieur (" + last_year + ") en %"], 5)
      m = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

      # Ajouter la carte choroplèthe
      folium.Choropleth(
          geo_data=gdf.set_index("Code de l'iris"),
          name='choropleth',
          data=gdf,
          columns=["Code de l'iris", "Part des personnes non scolarisées titulaires d'un diplôme de l'enseignement supérieur (" + last_year + ") en %"],
          key_on='feature.id',
          fill_color='YlOrRd',
          fill_opacity=0.7,
          line_opacity=0.2,
          color='#ffffff',
          weight=3,
          opacity=1.0,
          legend_name="Part des personnes non scolarisées avec diplôme d'études supérieures",
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
              fields=["Nom de l'iris", "Part des personnes non scolarisées titulaires d'un diplôme de l'enseignement supérieur (" + last_year + ") en %"],
              aliases=['Iris: ', "Part des personnes non scolarisées avec diplôme d'études supérieures :"],
              style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
          )
      )
      m.add_child(NIL)
      m.keep_in_front(NIL)
      st.subheader("Part des personnes non scolarisées avec diplôme d'études supérieures par IRIS")
      # Afficher la carte dans Streamlit
      folium_st.folium_static(m)
  else:
      # Pas assez de valeurs uniques pour une visualisation significative
      st.warning("Pas assez de diversité dans les données pour afficher une carte choroplèthe significative.")


  ################
  st.subheader('Comparaison')
  st.caption("Agrégation à partir de l'échelle communale. Paru le 27/06/2023 - Millésime 2020")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    # Commune
    def part_etude_sup_com(fichier, code_commune, annee):
      df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str,"REG": str}, sep = ';')
      year = annee[-2:]
      if int(annee) >= 2017:
        df_ville = df.loc[df["CODGEO"]==code_commune]
        pop_non_scol = df_ville['P'+ year + '_NSCOL15P'].iloc[0]
        pop_non_scol_bac2 = df_ville['P'+ year + '_NSCOL15P_SUP2'].iloc[0]
        pop_non_scol_bac34 = df_ville['P'+ year + '_NSCOL15P_SUP34'].iloc[0]
        pop_non_scol_bac5 = df_ville['P'+ year + '_NSCOL15P_SUP5'].iloc[0]
        part_etude_sup = ((pop_non_scol_bac2 + pop_non_scol_bac34 + pop_non_scol_bac5) / pop_non_scol) * 100
        df_part_etude_sup = pd.DataFrame(data=part_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_commune])
        return df_part_etude_sup
      else:
        df_ville = df.loc[df["CODGEO"]==code_commune]
        pop_non_scol = df_ville['P'+ year + '_NSCOL15P'].iloc[0]
        pop_non_scol_etude_sup = df_ville['P'+ year + '_NSCOL15P_SUP'].iloc[0]
        part_etude_sup = (pop_non_scol_etude_sup / pop_non_scol) * 100
        df_part_etude_sup = pd.DataFrame(data=part_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_commune])
        return df_part_etude_sup
    indice_sans_diplome_com = part_etude_sup_com("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv",code_commune, last_year)
    # EPCI
    def part_etude_sup_epci(fichier, epci, annee):
        epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
        df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str,"REG": str}, sep = ';')
        year = annee[-2:]
        if int(annee) >= 2017:
          df_epci_com = pd.merge(df[['CODGEO', 'P' + year + '_NSCOL15P', 'P' + year + '_NSCOL15P_SUP2', 'P' + year + '_NSCOL15P_SUP34', 'P' + year + '_NSCOL15P_SUP5']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
          df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI','P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_SUP2', 'P'+ year + '_NSCOL15P_SUP34', 'P'+ year + '_NSCOL15P_SUP5']]
          pop_non_scol = df_epci.loc[:, 'P'+ year + '_NSCOL15P'].sum()
          pop_bac_sup2 = df_epci.loc[:, 'P'+ year + '_NSCOL15P_SUP2'].sum()
          pop_bac_sup34 = df_epci.loc[:, 'P'+ year + '_NSCOL15P_SUP34'].sum()
          pop_bac_sup5 = df_epci.loc[:, 'P'+ year + '_NSCOL15P_SUP5'].sum()
          part_pop_non_scol_etude_sup = ((pop_bac_sup2 + pop_bac_sup34 + pop_bac_sup5) / pop_non_scol)*100
          df_part_etude_sup = pd.DataFrame(data=part_pop_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_epci])
          return df_part_etude_sup
        else:
          df_epci_com = pd.merge(df[['CODGEO', 'P' + year + '_NSCOL15P', 'P' + year + '_NSCOL15P_SUP']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
          df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI','P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_SUP']]
          pop_non_scol = df_epci.loc[:, 'P'+ year + '_NSCOL15P'].sum()
          pop_bac_sup = df_epci.loc[:, 'P'+ year + '_NSCOL15P_SUP'].sum()
          part_pop_non_scol_etude_sup = (pop_bac_sup / pop_non_scol)*100
          df_part_etude_sup = pd.DataFrame(data=part_pop_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_epci])
          return df_part_etude_sup
    indice_etude_sup_epci = part_etude_sup_epci("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv",code_epci,last_year)
    # Département
    def part_etude_sup_departement(fichier, departement, annee):
      if int(annee) >= 2017:
        df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str,"REG": str}, sep = ';')
        year = annee[-2:]
        df_departement = df.loc[df["DEP"]==departement, ['DEP','P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_SUP2', 'P' + year + '_NSCOL15P_SUP34', 'P' + year + '_NSCOL15P_SUP5']]
        pop_non_scol = df_departement.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        pop_non_scol_bac2 = df_departement.loc[:, 'P'+ year + '_NSCOL15P_SUP2'].sum()
        pop_non_scol_bac34 = df_departement.loc[:, 'P'+ year + '_NSCOL15P_SUP34'].sum()
        pop_non_scol_bac5P = df_departement.loc[:, 'P'+ year + '_NSCOL15P_SUP5'].sum()
        part_non_scol_etude_sup = ((pop_non_scol_bac2 + pop_non_scol_bac34 + pop_non_scol_bac5P ) / pop_non_scol)*100
        df_part_non_scol_etude_sup = pd.DataFrame(data=part_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_departement])
        return df_part_non_scol_etude_sup
      else:
        df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str,"REG": str}, sep = ';')
        year = annee[-2:]
        df_departement = df.loc[df["DEP"]==departement, 'P' + year + '_NSCOL15P' : 'P' + year + '_NSCOL15P_SUP']
        pop_non_scol = df_departement.loc[:, 'P' + year + '_NSCOL15P'].sum()
        pop_non_scol_etude_sup = df_departement.loc[:, 'P'+ year + '_NSCOL15P_SUP'].sum()
        part_non_scol_etude_sup = (pop_non_scol_etude_sup / pop_non_scol)*100
        df_part_non_scol_etude_sup = pd.DataFrame(data=part_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_departement])
        return df_part_non_scol_etude_sup
    valeurs_etude_sup_dep = part_etude_sup_departement("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv",code_departement,last_year)
    # Région
    def part_etude_sup_region(fichier, region, annee):
      if int(annee) >= 2017:
        df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str,"REG": str}, sep = ';')
        year = annee[-2:]
        df_region = df.loc[df["REG"]==region, ['REG','P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_SUP2', 'P'+ year + '_NSCOL15P_SUP34', 'P'+ year + '_NSCOL15P_SUP5']]
        pop_non_scol = df_region.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        pop_non_scol_bac2 = df_region.loc[:, 'P'+ year + '_NSCOL15P_SUP2'].sum()
        pop_non_scol_bac34 = df_region.loc[:, 'P'+ year + '_NSCOL15P_SUP34'].sum()
        pop_non_scol_bac5 = df_region.loc[:, 'P'+ year + '_NSCOL15P_SUP5'].sum()
        part_pop_non_scol_etude_sup = ((pop_non_scol_bac2 + pop_non_scol_bac34 + pop_non_scol_bac5) / pop_non_scol)*100
        df_part_pop_non_scol_etude_sup = pd.DataFrame(data=part_pop_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_region])
        return df_part_pop_non_scol_etude_sup
      else:
        df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str,"REG": str}, sep = ';')
        year = annee[-2:]
        df_regions = df.loc[df["REG"]==region, 'P'+ year +'_NSCOL15P' : 'P'+ year + '_NSCOL15P_SUP']
        pop_non_scol = df_regions.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        pop_non_scol_etude_sup = df_regions.loc[:, 'P'+ year + '_NSCOL15P_SUP'].sum()
        part_pop_non_scol_etude_sup = (pop_non_scol_etude_sup / pop_non_scol)*100
        df_part_pop_non_scol_etude_sup = pd.DataFrame(data=part_pop_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_region])
        return df_part_pop_non_scol_etude_sup
    valeurs_etude_sup_reg = part_etude_sup_region("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv",code_region,last_year)
    # France
    def part_etude_sup_France(fichier, annee):
        df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str, "REG": str}, sep = ';')
        year = annee[-2:]
        if int(annee) >= 2017:
          select_pop_non_scol = df.loc[:, 'P'+ year + '_NSCOL15P'].sum()
          select_pop_non_scol_bac2 = df.loc[:, 'P'+ year + '_NSCOL15P_SUP2'].sum()
          select_pop_non_scol_bac34 = df.loc[:, 'P'+ year + '_NSCOL15P_SUP34'].sum()
          select_pop_non_scol_bac5 = df.loc[:, 'P'+ year + '_NSCOL15P_SUP5'].sum()
          part_pop_non_scol_etude_sup = ((select_pop_non_scol_bac2 + select_pop_non_scol_bac34 + select_pop_non_scol_bac5) / select_pop_non_scol ) * 100
          df_part_pop_non_scol_etude_sup = pd.DataFrame(data=part_pop_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = ["France"])
          return df_part_pop_non_scol_etude_sup
        else:
          select_pop_non_scol = df.loc[:, 'P'+ year + '_NSCOL15P'].sum()
          select_pop_non_scol_etude_sup = df.loc[:, 'P'+ year + '_NSCOL15P_SUP'].sum()
          part_pop_non_scol_etude_sup = (select_pop_non_scol_etude_sup / select_pop_non_scol ) * 100
          df_part_pop_non_scol_etude_sup = pd.DataFrame(data=part_pop_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = ["France"])
          return df_part_pop_non_scol_etude_sup
    valeur_part_etude_sup_fr = part_etude_sup_France("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv",last_year)
    # Fusion
    def etude_sup_global(annee):
        df = pd.concat([indice_sans_diplome_com,indice_etude_sup_epci, valeurs_etude_sup_dep, valeurs_etude_sup_reg, valeur_part_etude_sup_fr])
        year = annee
        return df
    part_etude_sup_fin = etude_sup_global(last_year)
    st.table(part_etude_sup_fin)
  ##############################
  st.subheader("b.Evolution")
  st.caption("Agrégation à partir de l'échelle communale. Paru le 27/06/2023 - Millésime 2020")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    def evolution_part_etudes_sup(generate_data_function, *args):
      evolution = []
      for annee in range(2015, 2021):
          fichier = f"./diplome/commune/base-cc-diplomes-formation-{annee}.csv"
          df_part_etudes_sup = generate_data_function(fichier, *args, str(annee))
          if not df_part_etudes_sup.empty:
              part_etudes_sup = df_part_etudes_sup.iloc[0, 0]  # Première colonne de la première ligne
              evolution.append({'Année': annee, 'Part études supérieures': part_etudes_sup})
          else:
              evolution.append({'Année': annee, 'Part études supérieures': None})

      return pd.DataFrame(evolution)
    df_evolution_etudes_sup_com = evolution_part_etudes_sup(part_etude_sup_com, code_commune)
    df_evolution_etudes_sup_epci = evolution_part_etudes_sup(part_etude_sup_epci, code_epci)
    df_evolution_etudes_sup_departement = evolution_part_etudes_sup(part_etude_sup_departement, code_departement)
    df_evolution_etudes_sup_region = evolution_part_etudes_sup(part_etude_sup_region, code_region)
    df_evolution_etudes_sup_France = evolution_part_etudes_sup(part_etude_sup_France)

    df_evolution_etudes_sup_final = df_evolution_etudes_sup_com.merge(df_evolution_etudes_sup_epci, on='Année', suffixes=('_com', '_epci'))\
                                                              .merge(df_evolution_etudes_sup_departement, on='Année')\
                                                              .merge(df_evolution_etudes_sup_region, on='Année', suffixes=('_dep', '_reg'))\
                                                              .merge(df_evolution_etudes_sup_France, on='Année')
    # Renommez les colonnes pour clarifier
    df_evolution_etudes_sup_final.columns = ['Année', nom_commune, nom_epci, nom_departement, nom_region, 'France']
    st.write(df_evolution_etudes_sup_final)

    # Créer le graphique
    fig = px.line(df_evolution_etudes_sup_final, x='Année', y=df_evolution_etudes_sup_final.columns[1:],
                  title='Évolution de la part des personnes avec études supérieures par territoire',
                  labels={'value': 'Part des personnes avec études supérieures (%)', 'variable': 'Territoire'})

    # Rendre le graphique interactif
    fig.update_traces(mode='lines+markers')
    st.plotly_chart(fig)
