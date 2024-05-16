import streamlit as st
from pages.utils import afficher_infos_commune
from pages.utils import remove_comma, round_to_zero
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
import jenkspy
import plotly.express as px


def app(code_commune, nom_commune, code_epci, nom_epci, code_departement, nom_departement, code_region, nom_region):
  # Appeler la fonction et récupérer les informations

  ################################################################################
  st.title("💶 RESSOURCES - PAUVRETÉ")
  #################################################################
  # Recherche code epci alternatif
  df_epci_bis = pd.read_csv("./EPCI.csv", dtype={"COM": str}, sep=";")
  nom_epci_bis = df_epci_bis.loc[df_epci_bis['COM'] == code_commune, 'LIBEPCI'].iloc[0]
  code_epci_bis = df_epci_bis.loc[df_epci_bis['COM'] == code_commune, 'EPCI'].iloc[0]
  st.subheader('Le niveau de vie médian')
  st.caption("La médiane du revenu disponible correspond au niveau au-dessous duquel se situent 50 % de ces revenus. C'est de manière équivalente le niveau au-dessus duquel se situent 50 % des revenus.")
  st.caption("Le revenu disponible est le revenu à la disposition du ménage pour consommer et épargner. Il comprend les revenus d'activité (nets des cotisations sociales), indemnités de chômage, retraites et pensions, revenus fonciers, les revenus financiers et les prestations sociales reçues (prestations familiales, minima sociaux et prestations logements). Au total de ces ressources, on déduit les impôts directs (impôt sur le revenu, taxe d'habitation) et les prélèvements sociaux (CSG, CRDS).")
  st.caption("Le revenu disponible par unité de consommation (UC), également appelé *niveau de vie*, est le revenu disponible par *équivalent adulte*. Il est calculé en rapportant le revenu disponible du ménage au nombre d'unités de consommation qui le composent. Toutes les personnes rattachées au même ménage fiscal ont le même revenu disponible par UC (ou niveau de vie).")
  st.subheader("Comparaison des iris de la commune")

  reference_year = "2020"

  st.write("Dernière année disponible : " + reference_year + ". Paru le : 31/03/2023")
  def niveau_vie_median_iris(fichier, nom_ville, annee) :
      df = pd.read_csv(fichier, dtype={"IRIS": str , "COM": str},sep=";")
      year = annee[-2:]
      df_ville = df.loc[df["LIBCOM"] == nom_ville]
      df_ville = df_ville.replace(',','.', regex=True)
      df_ville = df_ville[['IRIS','LIBIRIS','DISP_MED'+ year]]
      if year == "14":
        df_ville['DISP_MED' + year] = df_ville['DISP_MED' + year].str.replace(',','.').astype(float)
      if year == "20":
        # Remplacer les valeurs "ns", "nd" et "s" par NaN
        df_ville = df_ville.replace(['ns', 'nd', 's'], pd.NA)
        # Supprimer les lignes contenant NaN
        df_ville = df_ville.dropna()
      df_ville['DISP_MED' + year] = df_ville['DISP_MED' + year].astype(int)
      df_ville.reset_index(inplace=True, drop=True)
      df_ville = df_ville.rename(columns={'IRIS': "Code de l'iris",'LIBIRIS': "Nom de l'iris", 'DISP_MED'+ year:"Niveau de vie " + annee + " en €" })
      return df_ville

  nvm_iris = niveau_vie_median_iris("./revenu/revenu_iris/BASE_TD_FILO_DISP_IRIS_" + reference_year + ".csv",nom_commune, reference_year)
  # Créer une copie du DataFrame original
  nvm_iris_display = nvm_iris.copy()
  # Appliquer la fonction remove_comma uniquement à la colonne P20_POP
  nvm_iris_display["Niveau de vie " + reference_year + " en €"] = nvm_iris_display["Niveau de vie " + reference_year + " en €"].apply(remove_comma)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(nvm_iris_display)

  # Carte Niveau de vie
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
  gdf = gdf.merge(nvm_iris, left_on='fields.iris_code', right_on="Code de l'iris")

  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]

  # Supprimer les lignes avec NaN pour le calcul de la méthode de Jenks et assurer que toutes les valeurs sont finies
  gdf["Niveau de vie " + reference_year + " en €"] = pd.to_numeric(gdf["Niveau de vie " + reference_year + " en €"], errors='coerce')
  gdf = gdf.dropna(subset=["Niveau de vie " + reference_year + " en €"])

  # Vérification du nombre de valeurs uniques
  unique_values = gdf["Niveau de vie " + reference_year + " en €"].nunique()

  if unique_values >= 5:
      # Assez de valeurs uniques pour 5 classes
      breaks = jenkspy.jenks_breaks(gdf["Niveau de vie " + reference_year + " en €"], 5)
      m = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

      # Ajouter la carte choroplèthe
      folium.Choropleth(
          geo_data=gdf.set_index("Code de l'iris"),
          name='choropleth',
          data=gdf,
          columns=["Code de l'iris", "Niveau de vie " + reference_year + " en €"],
          key_on='feature.id',
          fill_color='YlOrRd',
          fill_opacity=0.7,
          line_opacity=0.2,
          color='#ffffff',
          weight=3,
          opacity=1.0,
          legend_name='Médiane des revenus disponibles',
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
              fields=["Nom de l'iris", "Niveau de vie " + reference_year + " en €"],
              aliases=['Iris: ', "Médiane des revenus disponibles :"],
              style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
          )
      )
      m.add_child(NIL)
      m.keep_in_front(NIL)
      st.subheader("Médiane des revenus disponibles par IRIS")
      # Afficher la carte dans Streamlit
      folium_st.folium_static(m)
  else:
      # Pas assez de valeurs uniques pour une visualisation significative
      st.warning("Pas assez de diversité dans les données pour afficher une carte choroplèthe significative.")

############################
  st.caption("Zoom sur les QPV")

  st.subheader("Zoom QPV")
  #Année
  select_annee_med_revenu = st.select_slider(
       "Sélection de l'année",
       options=['2017', '2018', '2019', '2020', '2021', '2022', '2023'],
       value=('2023'),
       key = 'med_revenu')
  st.write('Mon année :', select_annee_med_revenu)

  st.write("Dernière année disponible : " + select_annee_med_revenu + ". Paru le : 14/03/2023." )

  def med_disp_qpv(fichier, nom_ville, annee) :
    fp_qpv = "./qpv.geojson"
    map_qpv_df = gpd.read_file(fp_qpv)
    year = annee[-2:]
    df = pd.read_csv(fichier, dtype={"CODGEO": str}, sep=";")
    map_qpv_df_code_insee = map_qpv_df.merge(df, left_on='code_qp', right_on='CODGEO')
    map_qpv_df_code_insee_extract = map_qpv_df_code_insee[['nom_qp', 'code_qp', 'commune_qp','code_insee', 'DISP_Q2' ]]
    map_qpv_df_code_insee_extract
    df_qpv = map_qpv_df_code_insee_extract.loc[map_qpv_df_code_insee_extract["commune_qp"].str.contains(nom_ville + "(,|$)")]
    df_qpv = df_qpv.reset_index(drop=True)
    df_qpv = df_qpv[['code_qp', 'nom_qp','commune_qp', 'DISP_Q2']]
    df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", 'DISP_Q2' : "Mediane des revenus disponibles " + select_annee_med_revenu})
    return df_qpv

  med_disp_qpv = med_disp_qpv('./revenu/revenu_qpv/REVN_' + select_annee_med_revenu + '.csv', nom_commune, select_annee_med_revenu)
  st.table(med_disp_qpv)

##################################
  st.subheader('Comparaison entre territoires')
  reference_year_comparaison = "2021"
  st.write("Dernière année disponible : " + reference_year_comparaison + ". Paru le : 29/01/2024")

  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    #Position de la commune
    df = pd.read_csv("./revenu/revenu_commune/FILO" + reference_year_comparaison + "_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
    year = reference_year_comparaison[-2:]
    df_ville = df[['CODGEO','LIBGEO','Q2' + year]]
    if int(year) <= 15:
      df_ville['Q2' + year] = df_ville['Q2' + year].str.replace(',', '.').astype(float)
    df_ville = df_ville.sort_values(by=['Q2' + year], ascending=False)
    df_ville.reset_index(inplace=True, drop=True)
    indice = df_ville[df_ville['CODGEO']==code_commune].index.values.item()+1
    total_indice = len(df_ville['Q2' + year])
    st.write("La commune de " + nom_commune + " se situe en " + str(indice) + "eme position sur " + str(total_indice) + " communes")

    #Commune
    def niveau_vie_median_commune(fichier, nom_ville, annee) :
        df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
        year = annee[-2:]
        df_ville = df.loc[df["LIBGEO"]== nom_ville]
        df_ville = df_ville.replace(',','.', regex=True)
        ville = df.loc[df["LIBGEO"]== nom_ville]
        nvm = ville[[ 'LIBGEO' ,'Q2'+ year]]
        return nvm
    nvm_ville = niveau_vie_median_commune("./revenu/revenu_commune/FILO" + reference_year_comparaison + "_DISP_COM.csv",nom_commune, reference_year_comparaison)
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
    nvm_epci =niveau_vie_median_epci("./revenu/revenu_epci/FILO" + reference_year_comparaison + "_DISP_EPCI.csv",str(code_epci), reference_year_comparaison)
    #Département
    def niveau_vie_median_departement(fichier, nom_departement, annee) :
        df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
        year = annee[-2:]
        df_departement = df.loc[df["LIBGEO"]== nom_departement]
        df_departement = df_departement.replace(',','.', regex=True)
        departement = df.loc[df["LIBGEO"]== nom_departement]
        nvm = departement[[ 'LIBGEO' ,'Q2'+ year]]
        return nvm
    nvm_departement =niveau_vie_median_departement("./revenu/revenu_dpt/FILO" + reference_year_comparaison + "_DISP_DEP.csv",nom_departement, reference_year_comparaison)
    #Région
    def niveau_vie_median_region(fichier, nom_region, annee) :
        df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
        year = annee[-2:]
        df_region = df.loc[df["LIBGEO"]== nom_region]
        df_region = df_region.replace(',','.', regex=True)
        region = df.loc[df["LIBGEO"]== nom_region]
        nvm = region[[ 'LIBGEO' ,'Q2'+ year]]
        return nvm
    nvm_region =niveau_vie_median_region("./revenu/revenu_region/FILO" + reference_year_comparaison + "_DISP_REG.csv",nom_region, reference_year_comparaison)
    #France
    def niveau_vie_median_france(fichier, annee) :
        df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
        df = df.replace(',','.', regex=True)
        year = annee[-2:]
        nvm = df[[ 'LIBGEO' ,'Q2'+ year]].iloc[:1]
        return nvm
    nvm_france =niveau_vie_median_france("./revenu/revenu_france/FILO" + reference_year_comparaison + "_DISP_METROPOLE.csv", reference_year_comparaison)
    #Global
    test_tab = pd.concat([nvm_ville, nvm_epci, nvm_departement, nvm_region, nvm_france])
    test_tab = test_tab.reset_index(drop=True)
    test_tab = test_tab.rename(columns={'LIBGEO': "Territoire",'Q2' + reference_year_comparaison[-2:] : "Niveau de vie " + reference_year_comparaison})
    test_tab["Niveau de vie " + reference_year_comparaison] = test_tab["Niveau de vie " + reference_year_comparaison].apply(round_to_zero).apply(remove_comma)
    st.write(test_tab)

##################################
  st.subheader("Évolution sur les 7 dernières années disponibles")
  st.write("Dernière année disponible : " + reference_year_comparaison + ". Paru le : 29/01/2024")

  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    annees = ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']

    #France
    def read_indice_csv_file(year):
      df = pd.read_csv(f"./revenu/revenu_france/FILO{year}_DISP_METROPOLE.csv", dtype={"CODGEO": str}, sep=";")
      df = df.replace(',', '.', regex=True)
      nvm = df.loc[:, f'Q2{year[2:]}'].to_numpy().astype(float)
      return nvm[0]
    years = ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']
    indices = [read_indice_csv_file(year) for year in years]
    df_france_glob = pd.DataFrame([indices], columns=years, index=['France'])
    #Region
    df_region_glob = pd.DataFrame(columns=annees, index=[nom_region])
    for annee in annees:
      df = pd.read_csv(f"./revenu/revenu_region/FILO{annee}_DISP_REG.csv", dtype={"CODGEO": str}, sep=";")
      df = df.loc[df["LIBGEO"] == nom_region]
      df = df.replace(',', '.', regex=True)
      nvm = df.loc[:, f'Q2{annee[2:]}'].to_numpy().astype(float)
      indice = nvm[0]
      df_region_glob[annee] = indice
    #département
    df_dpt_glob = pd.DataFrame(columns=annees, index=[nom_departement])
    for annee in annees:
      df = pd.read_csv(f"./revenu/revenu_dpt/FILO{annee}_DISP_DEP.csv", dtype={"CODGEO": str}, sep=";")
      df = df.loc[df["LIBGEO"] == nom_departement]
      df = df.replace(',', '.', regex=True)
      nvm = df.loc[:, f'Q2{annee[2:]}'].to_numpy().astype(float)
      indice = nvm[0]
      df_dpt_glob[annee] = indice
    # EPCI
    df_epci_glob = pd.DataFrame(columns=annees, index=[nom_epci])
    for annee in annees:
      df = pd.read_csv(f"./revenu/revenu_epci/FILO{annee}_DISP_EPCI.csv", dtype={"CODGEO": str}, sep=";")
      df = df.replace(',', '.', regex=True)

      # Filtrage initial avec code_epci
      df_filtered = df.loc[df["CODGEO"] == code_epci]

      # Si df_filtered est vide, filtrer avec code_epci_bis
      if df_filtered.empty:
          df_filtered = df.loc[df["CODGEO"] == code_epci_bis]

      if not df_filtered.empty:
          nvm = df_filtered.loc[:, f'Q2{annee[2:]}'].to_numpy().astype(float)
          indice = nvm[0]
          df_epci_glob[annee] = indice
      else:
          # Gérer le cas où les deux filtrages sont vides
          df_epci_glob[annee] = None  # ou toute autre valeur par défaut appropriée
    #Commune
    df_commune_glob = pd.DataFrame(columns=annees, index=[nom_commune])
    for annee in annees:
      df = pd.read_csv(f"./revenu/revenu_commune/FILO{annee}_DISP_COM.csv", dtype={"CODGEO": str}, sep=";")
      df = df.loc[df["LIBGEO"] == nom_commune]
      df = df.replace(',', '.', regex=True)
      nvm = df.loc[:, f'Q2{annee[2:]}'].to_numpy().astype(float)
      indice = nvm[0]
      df_commune_glob[annee] = indice
    df_glob = pd.concat([df_france_glob, df_region_glob, df_dpt_glob, df_epci_glob, df_commune_glob])
    # Pour chaque colonne dans df_glob
    for col in df_glob.columns:
      # Appliquer remove_comma puis round_to_zero
      df_glob[col] = df_glob[col].apply(remove_comma).apply(round_to_zero)
    st.table(df_glob)
  # Afficher le graphique avec st.line_chart
  df1_transposed = df_glob.T

  #Graphique évolution des écarts de revenu par rapport à la France.
  # 'France' est l'entité de référence
  # Supposons que df1_transposed est votre DataFrame
  # 'France' est l'entité de référence
  ecart_reference = df1_transposed['France']

  # Calculer l'écart pour chaque entité par rapport à la référence
  for col in df1_transposed.columns:
      df1_transposed[col] = df1_transposed[col] - ecart_reference

  # Supprimer la colonne 'France' du DataFrame
  df1_transposed.drop('France', axis=1, inplace=True)

  # Création d'un graphique à lignes avec Plotly
  fig = px.line(df1_transposed, x=df1_transposed.index, y=df1_transposed.columns,
                title='Évolution des écarts par rapport à la France au fil du temps',
                labels={'value': 'Écart', 'index': 'Année'})

  # Ajouter des annotations pour chaque entité
  for col in df1_transposed.columns:
      ecart_diff = df1_transposed[col].iloc[-1] - df1_transposed[col].iloc[0]
      fig.add_annotation(
          x=df1_transposed.index[-1],
          y=df1_transposed[col].iloc[-1],
          text=f'{ecart_diff:+.0f}€',  # Formatage sans chiffre après la virgule et ajout du symbole €
          showarrow=True,
          arrowhead=1,
          ax=20
      )

  # Mise à jour du layout si nécessaire
  fig.update_layout(
      xaxis_title='Année',
      yaxis_title='Écart par rapport à la France',
      legend_title='Entité'
  )

  # Afficher le graphique dans Streamlit
  st.plotly_chart(fig)

  # Phrase d'analyse
  # Initialiser une liste pour stocker les territoires avec un écart accru
  territoires_ecart_accru = []

  # Parcourir les colonnes pour identifier les territoires avec un écart accru
  for col in df1_transposed.columns:
      if df1_transposed[col].iloc[-1] < df1_transposed[col].iloc[0]:
          territoires_ecart_accru.append(col)

  # Formuler la phrase
  phrase = "Les territoires dont l'écart de revenu avec la France s'est agrandi au cours de la période sont : " + ", ".join(territoires_ecart_accru) + "."

  # Afficher la phrase sous le graphique
  st.write(phrase)

  ############################################################################

  st.header("2.Taux de pauvreté au seuil de 60% du revenu disponible par UC médian métropolitain")
  st.caption("Mise en ligne 31/03/2023 - Millésime 2020")
  annee_reference = "2020"
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    def pauvrete_60_iris(fichier, code_ville, annee) :
        df = pd.read_csv(fichier, dtype={"IRIS": str , "COM": str},sep=";")
        year = annee[-2:]
        df_ville = df.loc[df["COM"] == code_ville]
        df_ville = df_ville.replace(',','.', regex=True)
        df_ville = df_ville[['IRIS','LIBIRIS','DISP_TP60'+ year]]
        if year == "20":
          # Remplacer les valeurs "ns", "nd" et "s" par NaN
          df_ville = df_ville.replace(['ns', 'nd', 's'], pd.NA)
          # Supprimer les lignes contenant NaN
          df_ville = df_ville.dropna()
        df_ville['DISP_TP60' + year] = df_ville['DISP_TP60' + year].str.replace(',','.').astype(float)
        df_ville.reset_index(inplace=True, drop=True)
        df_ville = df_ville.rename(columns={'IRIS': "Code de l'iris",'LIBIRIS': "Nom de l'iris", 'DISP_TP60'+ year:"Taux de pauvreté " + annee + " en %" })
        return df_ville
    taux_pauvrete_iris = pauvrete_60_iris("./revenu/revenu_iris/BASE_TD_FILO_DISP_IRIS_" + annee_reference + ".csv",code_commune, annee_reference)
    with st.expander("Visualiser le tableau des iris"):
      st.dataframe(taux_pauvrete_iris)


  #CARTE
  # Carte Pauvreté
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
  gdf = gdf.merge(taux_pauvrete_iris, left_on='fields.iris_code', right_on="Code de l'iris")

  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]

  # Convertir en numérique et supprimer les NaN
  gdf["Taux de pauvreté " + annee_reference + " en %"] = pd.to_numeric(gdf["Taux de pauvreté " + annee_reference + " en %"], errors='coerce')
  gdf = gdf.dropna(subset=["Taux de pauvreté " + annee_reference + " en %"])

  # Vérification du nombre de valeurs uniques
  unique_values = gdf["Taux de pauvreté " + annee_reference + " en %"].nunique()

  if unique_values >= 5:
      # Assez de valeurs uniques pour 5 classes
      breaks = jenkspy.jenks_breaks(gdf["Taux de pauvreté " + annee_reference + " en %"], 5)
      m = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

      # Ajouter la carte choroplèthe
      folium.Choropleth(
          geo_data=gdf.set_index("Code de l'iris"),
          name='choropleth',
          data=gdf,
          columns=["Code de l'iris", "Taux de pauvreté " + annee_reference + " en %"],
          key_on='feature.id',
          fill_color='YlOrRd',
          fill_opacity=0.7,
          line_opacity=0.2,
          color='#ffffff',
          weight=3,
          opacity=1.0,
          legend_name='Taux de pauvreté à 60% du revenu disponible',
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
              fields=["Nom de l'iris", "Taux de pauvreté " + annee_reference + " en %"],
              aliases=['Iris: ', "Taux de pauvreté à 60% du revenu disponible :"],
              style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
          )
      )
      m.add_child(NIL)
      m.keep_in_front(NIL)
      st.subheader("Taux de pauvreté à 60% du revenu disponible par IRIS")
      # Afficher la carte dans Streamlit
      folium_st.folium_static(m)
  else:
      # Pas assez de valeurs uniques pour une visualisation significative
      st.warning("Pas assez de diversité dans les données pour afficher une carte choroplèthe significative.")


  ###########
  st.subheader("Taux de pauvreté Comparaison")
  annee = "2020"
  st.write("Dernière année disponible : " + annee + ". Paru le : 31/03/2023")
  #Commune
  df_pauv_com = pd.read_csv("./revenu/pauvrete/FILO" + annee + "_DISP_PAUVRES_COM.csv", dtype={"CODGEO": str},sep=";")
  df_pauv_com = df_pauv_com.loc[df_pauv_com["CODGEO"] == code_commune ]
  taux_pauvrete_com = df_pauv_com["TP60" + annee[-2:]].values[0]
  mediane_pauvrete_com = df_pauv_com["TP60Q2" + annee[-2:]].values[0]
  #EPCI
  df_pauv_epci = pd.read_csv("./revenu/pauvrete/FILO" + annee + "_DISP_PAUVRES_EPCI.csv", dtype={"CODGEO": str},sep=";")
  # Filtrage initial avec code_epci
  df_pauv_epci_filtered = df_pauv_epci.loc[df_pauv_epci["CODGEO"] == code_epci]
  # Si df_pauv_epci_filtered est vide, filtrer avec code_epci_bis
  if df_pauv_epci_filtered.empty:
      df_pauv_epci_filtered = df_pauv_epci.loc[df_pauv_epci["CODGEO"] == code_epci_bis]
  # Vérifier si le DataFrame filtré est encore vide
  if not df_pauv_epci_filtered.empty:
      taux_pauvrete_epci = df_pauv_epci_filtered["TP60" + annee[-2:]].values[0]
  else:
      taux_pauvrete_epci = None  # ou toute autre valeur par défaut appropriée
  #Département
  df_pauv_dep = pd.read_csv("./revenu/pauvrete/FILO" + annee + "_DISP_PAUVRES_DEP.csv", dtype={"CODGEO": str},sep=";")
  df_pauv_dep = df_pauv_dep.loc[df_pauv_dep["CODGEO"] == code_departement ]
  taux_pauvrete_dep = df_pauv_dep["TP60" + annee[-2:]].values[0]
  #Région
  df_pauv_reg = pd.read_csv("./revenu/pauvrete/FILO" + annee + "_DISP_PAUVRES_REG.csv", dtype={"CODGEO": str},sep=";")
  df_pauv_reg = df_pauv_reg.loc[df_pauv_reg["CODGEO"] == str(code_region) ]
  taux_pauvrete_reg = df_pauv_reg["TP60" + annee[-2:]].values[0]
  #France
  df_pauv_fr = pd.read_csv("./revenu/pauvrete/FILO" + annee + "_DISP_PAUVRES_METROPOLE.csv", dtype={"CODGEO": str},sep=";")
  taux_pauvrete_fr = df_pauv_fr["TP60" + annee[-2:]].values[0]
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Taux de pauvreté à 60% (" + annee + ") (en %)": [taux_pauvrete_com, taux_pauvrete_epci, taux_pauvrete_dep, taux_pauvrete_reg, taux_pauvrete_fr]}
  df = pd.DataFrame(data=d)
  st.write(df)

  #Texte
  st.write("La commune compte en " + annee + " " + taux_pauvrete_com + "% de sa population vivant sous le seuil de pauvreté (60% du revenu médian national de l'année).")
  st.write("La médiane de cette sous-population se situe à " + str(mediane_pauvrete_com) + "€. Soit " + str(float(mediane_pauvrete_com)/12) + "€ mensuel.")
  if taux_pauvrete_com > taux_pauvrete_epci and taux_pauvrete_com > taux_pauvrete_dep and taux_pauvrete_com > taux_pauvrete_reg and taux_pauvrete_com > taux_pauvrete_fr:
    st.write("La commune connait une sur-représentation de sa population vivant sous le seuil de pauvreté comparativement aux territoires de comparaison.")

  ##############
  st.subheader("Zoom QPV")

  #Année
  select_annee_tp60 = st.select_slider(
       "Sélection de l'année",
       options=['2017', '2018', '2019', '2020', '2021', '2022'],
       value=('2022'),
       key = 'tp60')
  st.write('Mon année :', select_annee_tp60)

  def tp60_qpv(fichier, nom_ville, annee) :
    fp_qpv = "./qpv.geojson"
    map_qpv_df = gpd.read_file(fp_qpv)
    year = annee[-2:]
    df = pd.read_csv(fichier, dtype={"CODGEO": str}, sep=";")
    map_qpv_df_code_insee = map_qpv_df.merge(df, left_on='code_qp', right_on='CODGEO')
    map_qpv_df_code_insee_extract = map_qpv_df_code_insee[['nom_qp', 'code_qp', 'commune_qp','code_insee', 'TP60' ]]
    map_qpv_df_code_insee_extract
    df_qpv = map_qpv_df_code_insee_extract.loc[map_qpv_df_code_insee_extract["commune_qp"].str.contains(nom_ville + "(,|$)")]
    df_qpv = df_qpv.reset_index(drop=True)
    df_qpv = df_qpv[['code_qp', 'nom_qp','commune_qp', 'TP60']]
    df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", 'TP60' : "Taux de pauvreté à 60% " + select_annee_tp60})
    return df_qpv

  tp60_qpv = tp60_qpv('./revenu/revenu_qpv/REVN_' + select_annee_tp60 + '.csv', nom_commune, select_annee_tp60)
  st.table(tp60_qpv)
  ############################################################################

  st.subheader("Part des allocataires percevant une aide au logement (APL, ALF, ALS)")
  #Commune
  df_aal = pd.read_csv("./revenu/rsa/data_CAF2021_COM.csv", dtype={"CODGEO": str, "EPCI": str, "REG": str},sep=";")
  df_aal_com = df_aal.loc[df_aal["CODGEO"] == code_commune ]
  alloc_aal_com = df_aal_com["AAL"].values[0]
  alloc_com = df_aal_com["A"].values[0]
  part_alloc_aal_com = round((alloc_aal_com / alloc_com) * 100 , 2)
  st.write("En 2021, le nombre d'allocataires bénénficiant d'une aide au logement : " + str(round(alloc_aal_com)))
  st.write("Ce qui représente " + str(part_alloc_aal_com) + "% des allocataires sur la commune.")
  #EPCI
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df_aal, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_aal_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  alloc_aal_epci = df_aal_epci["AAL"].sum()
  alloc_epci = df_aal_epci["A"].sum()
  part_alloc_aal_epci = round((alloc_aal_epci / alloc_epci) * 100 , 2)
  #Département
  df_dep = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, sep = ',')
  df_dep_merge = pd.merge(df_aal, df_dep[['COM','DEP']], left_on='CODGEO', right_on='COM')
  df_aal_dep = df_dep_merge.loc[df_dep_merge["DEP"] == str(code_departement)]
  alloc_aal_dep = df_aal_dep["AAL"].sum()
  alloc_dep = df_aal_dep["A"].sum()
  part_alloc_aal_dep = round((alloc_aal_dep / alloc_dep) * 100 , 2)
  #Région
  df_reg = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
  df_reg_merge = pd.merge(df_aal, df_reg[['COM','REG']], left_on='CODGEO', right_on='COM')
  df_aal_reg = df_reg_merge.loc[df_reg_merge["REG"] == str(code_region)]
  alloc_aal_reg = df_aal_reg["AAL"].sum()
  alloc_reg = df_aal_reg["A"].sum()
  part_alloc_aal_reg = round((alloc_aal_reg / alloc_reg) * 100 , 2)
  #France
  alloc_aal_fr = df_aal["AAL"].sum()
  alloc_fr = df_aal["A"].sum()
  part_alloc_aal_fr = round((alloc_aal_fr / alloc_fr) * 100 , 2)
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Part des allocataires bénéficiaires d'une aide au logement (2021) (en %)": [part_alloc_aal_com, part_alloc_aal_epci, part_alloc_aal_dep, part_alloc_aal_reg, part_alloc_aal_fr]}
  df = pd.DataFrame(data=d)
  st.write(df)
  ###########################

  st.subheader("Allocataires bénéficiaires de l'AAH")
  st.caption("a etudier si calcul par rapportà la population totale à partir de 20 ans (c'est l'age mini mais avec derogation possible à partir 16 ans)")
  #Commune
  df_aah = pd.read_csv("./revenu/rsa/data_CAF2021_COM.csv", dtype={"CODGEO": str, "EPCI": str, "REG": str},sep=";")
  df_aah_com = df_aah.loc[df_aah["CODGEO"] == code_commune ]
  alloc_aah_com = df_aah_com["AAAH"].values[0]
  alloc_com = df_aah_com["A"].values[0]
  part_alloc_aah_com = round((alloc_aah_com / alloc_com) * 100 , 2)
  st.write("En 2021, le nombre d'allocataires bénénficiant de l'Allocation Adulte Handicapé : " + str(round(alloc_aah_com)))
  st.write("Ce qui représente " + str(part_alloc_aah_com) + "% des allocataires sur la commune.")
  #EPCI
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df_aah, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_aah_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  alloc_aah_epci = df_aah_epci["AAAH"].sum()
  alloc_epci = df_aah_epci["A"].sum()
  part_alloc_aah_epci = round((alloc_aah_epci / alloc_epci) * 100 , 2)
  #Département
  df_dep = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, sep = ',')
  df_dep_merge = pd.merge(df_aah, df_dep[['COM','DEP']], left_on='CODGEO', right_on='COM')
  df_aah_dep = df_dep_merge.loc[df_dep_merge["DEP"] == str(code_departement)]
  alloc_aah_dep = df_aah_dep["AAAH"].sum()
  alloc_dep = df_aah_dep["A"].sum()
  part_alloc_aah_dep = round((alloc_aah_dep / alloc_dep) * 100 , 2)
  #Région
  df_reg = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
  df_reg_merge = pd.merge(df_aah, df_reg[['COM','REG']], left_on='CODGEO', right_on='COM')
  df_aah_reg = df_reg_merge.loc[df_reg_merge["REG"] == str(code_region)]
  alloc_aah_reg = df_aah_reg["AAAH"].sum()
  alloc_reg = df_aah_reg["A"].sum()
  part_alloc_aah_reg = round((alloc_aah_reg / alloc_reg) * 100 , 2)
  #France
  alloc_aah_fr = df_aah["AAAH"].sum()
  alloc_fr = df_aah["A"].sum()
  part_alloc_aah_fr = round((alloc_aah_fr / alloc_fr) * 100 , 2)
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Part des allocataires bénéficiaires de l'AAH (2021) (en %)": [part_alloc_aah_com, part_alloc_aah_epci, part_alloc_aah_dep, part_alloc_aah_reg, part_alloc_aah_fr]}
  df = pd.DataFrame(data=d)
  st.write(df)

  ###########################
  st.subheader("Population couverte bénéficiaire de la C2S non participative (ex-CMUC)")
  st.caption("def - + Attention toutes les communes ne sont pas présentes dans la Bdd,les caculs sont des estimations qui favorisent les comparaisons.")
  df_c2s = pd.read_csv("./revenu/cnam/data_CNAM2022_COM.csv", dtype={"CODGEO": str},sep=";")
  #Commune
  df_c2s_com = df_c2s.loc[df_c2s["CODGEO"] == code_commune ]
  if not df_c2s_com.empty:
    pop_couv_c2s_com = df_c2s_com["C_C2SNP"].values[0]
    pop_couv_com = df_c2s_com["C"].values[0]
    taux_pop_couv_c2s_com = round((pop_couv_c2s_com / pop_couv_com) * 100 , 2)
    st.write("En 2022, " + str(taux_pop_couv_c2s_com) + "% de la population couverte bénéficie de la C2s non participative. ")
  else:
    taux_pop_couv_c2s_com = "N.D."
    st.write("La commune n'est pas référencée par les services de l'assurance maladie - cnam - pour cette indicateur (secret statistique).")
  #EPCI
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df_c2s, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_c2s_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  pop_couv_c2s_epci = df_c2s_epci["C_C2SNP"].sum()
  pop_couv_epci = df_c2s_epci["C"].sum()
  taux_pop_couv_c2s_epci = round((pop_couv_c2s_epci / pop_couv_epci) * 100 , 2)
  #Département
  df_dep = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, sep = ',')
  df_dep_merge = pd.merge(df_c2s, df_dep[['COM','DEP']], left_on='CODGEO', right_on='COM')
  df_c2s_dep = df_dep_merge.loc[df_dep_merge["DEP"] == str(code_departement)]
  pop_couv_c2s_dep = df_c2s_dep["C_C2SNP"].sum()
  pop_couv_dep = df_c2s_dep["C"].sum()
  taux_pop_couv_c2s_dep = round((pop_couv_c2s_dep / pop_couv_dep) * 100 , 2)
  #Région
  df_reg = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
  df_reg_merge = pd.merge(df_c2s, df_reg[['COM','REG']], left_on='CODGEO', right_on='COM')
  df_c2s_reg = df_reg_merge.loc[df_reg_merge["REG"] == str(code_region)]
  pop_couv_c2s_reg = df_c2s_reg["C_C2SNP"].sum()
  pop_couv_reg = df_c2s_reg["C"].sum()
  taux_pop_couv_c2s_reg = round((pop_couv_c2s_reg / pop_couv_reg) * 100 , 2)
  #France
  pop_couv_c2s_fr = df_c2s["C_C2SNP"].sum()
  pop_couv_fr = df_c2s["C"].sum()
  taux_pop_couv_c2s_fr = round((pop_couv_c2s_fr / pop_couv_fr) * 100 , 2)
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Taux de personnes couvertes par la C2S parmi les personnes couvertes (2022) (en %)": [str(taux_pop_couv_c2s_com), str(taux_pop_couv_c2s_epci), str(taux_pop_couv_c2s_dep), str(taux_pop_couv_c2s_reg), str(taux_pop_couv_c2s_fr)]}
  df = pd.DataFrame(data=d)
  st.write(df)
  ###############################################################@

  st.subheader("Bénéficiaires du RSA socle")
  #Commune
  df_rsa = pd.read_csv("./revenu/rsa/data_CAF2021_COM.csv", dtype={"CODGEO": str, "EPCI": str, "REG": str},sep=";")
  df_rsa_com = df_rsa.loc[df_rsa["CODGEO"]== code_commune ]
  alloc_rsa = df_rsa_com["ARSAS"].values[0]
  df = pd.read_csv("./petite_enfance/commune/BTX_TD_POP1A_2019.csv", dtype={"CODGEO": str},sep=";")
  df_pop_25p = df.loc[df["CODGEO"]== code_commune ]
  df_pop_25p["pop_25p"] = (df_pop_25p["SEXE1_AGEPYR1025"] + df_pop_25p["SEXE1_AGEPYR1040"] + df_pop_25p["SEXE1_AGEPYR1055"] + df_pop_25p["SEXE1_AGEPYR1065"] + df_pop_25p["SEXE1_AGEPYR1080"]) + (df_pop_25p["SEXE2_AGEPYR1025"] + df_pop_25p["SEXE2_AGEPYR1040"] + df_pop_25p["SEXE2_AGEPYR1055"] + df_pop_25p["SEXE2_AGEPYR1065"] + df_pop_25p["SEXE2_AGEPYR1080"])
  pop_25p = df_pop_25p["pop_25p"].values[0]
  rsa_commune = round((alloc_rsa / pop_25p) * 100 , 2)
  #EPCI
  #pop 25 et plus
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_pop_25p_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  pop_25p_epci = df_pop_25p_epci["SEXE1_AGEPYR1025"].sum() + df_pop_25p_epci["SEXE1_AGEPYR1040"].sum() + df_pop_25p_epci["SEXE1_AGEPYR1055"].sum() + df_pop_25p_epci["SEXE1_AGEPYR1065"].sum() + df_pop_25p_epci["SEXE1_AGEPYR1080"].sum() + df_pop_25p_epci["SEXE2_AGEPYR1025"].sum() + df_pop_25p_epci["SEXE2_AGEPYR1040"].sum() + df_pop_25p_epci["SEXE2_AGEPYR1055"].sum() + df_pop_25p_epci["SEXE2_AGEPYR1065"].sum() + df_pop_25p_epci["SEXE2_AGEPYR1080"].sum()
  ##rsa
  df_rsa_epci_merge = pd.merge(df_rsa, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_rsa_epci = df_rsa_epci_merge.loc[df_rsa_epci_merge["EPCI"] == str(code_epci)]
  pop_rsa_epci = df_rsa_epci["ARSAS"].sum()
  rsa_epci = round((pop_rsa_epci / pop_25p_epci) * 100 , 2)
  #Département
  #pop 25 et plus
  df_dpt = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, sep = ',')
  df_dpt_merge = pd.merge(df, df_dpt[['COM','DEP']], left_on='CODGEO', right_on='COM')
  df_pop_25p_dpt = df_dpt_merge.loc[df_dpt_merge["DEP"] == str(code_departement)]
  pop_25p_dpt = df_pop_25p_dpt["SEXE1_AGEPYR1025"].sum() + df_pop_25p_dpt["SEXE1_AGEPYR1040"].sum() + df_pop_25p_dpt["SEXE1_AGEPYR1055"].sum() + df_pop_25p_dpt["SEXE1_AGEPYR1065"].sum() + df_pop_25p_dpt["SEXE1_AGEPYR1080"].sum() + df_pop_25p_dpt["SEXE2_AGEPYR1025"].sum() + df_pop_25p_dpt["SEXE2_AGEPYR1040"].sum() + df_pop_25p_dpt["SEXE2_AGEPYR1055"].sum() + df_pop_25p_dpt["SEXE2_AGEPYR1065"].sum() + df_pop_25p_dpt["SEXE2_AGEPYR1080"].sum()
  ##rsa
  df_rsa_dpt_merge = pd.merge(df_rsa, df_dpt[['COM','DEP']], left_on='CODGEO', right_on='COM')
  df_rsa_dpt = df_rsa_dpt_merge.loc[df_rsa_dpt_merge["DEP"] == str(code_departement)]
  pop_rsa_dpt = df_rsa_dpt["ARSAS"].sum()
  rsa_dpt = round((pop_rsa_dpt/ pop_25p_dpt) * 100 , 2)
  #Région
  ##pop 25 et plus
  df_reg = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
  df_reg_merge = pd.merge(df, df_reg[['COM','REG']], left_on='CODGEO', right_on='COM')
  df_pop_25p_reg = df_reg_merge.loc[df_reg_merge["REG"] == str(code_region)]
  pop_25p_reg = df_pop_25p_reg["SEXE1_AGEPYR1025"].sum() + df_pop_25p_reg["SEXE1_AGEPYR1040"].sum() + df_pop_25p_reg["SEXE1_AGEPYR1055"].sum() + df_pop_25p_reg["SEXE1_AGEPYR1065"].sum() + df_pop_25p_reg["SEXE1_AGEPYR1080"].sum() + df_pop_25p_reg["SEXE2_AGEPYR1025"].sum() + df_pop_25p_reg["SEXE2_AGEPYR1040"].sum() + df_pop_25p_reg["SEXE2_AGEPYR1055"].sum() + df_pop_25p_reg["SEXE2_AGEPYR1065"].sum() + df_pop_25p_reg["SEXE2_AGEPYR1080"].sum()
  ##rsa
  df_rsa_reg_merge = pd.merge(df_rsa, df_reg[['COM','REG']], left_on='CODGEO', right_on='COM')
  df_rsa_reg = df_rsa_reg_merge.loc[df_rsa_reg_merge["REG"] == str(code_region)]
  pop_rsa_reg = df_rsa_reg["ARSAS"].sum()
  rsa_reg = round((pop_rsa_reg/ pop_25p_reg) * 100 , 2)
  #France
  ##pop 25 et plus
  pop_25p_fr = df["SEXE1_AGEPYR1025"].sum() + df["SEXE1_AGEPYR1040"].sum() + df["SEXE1_AGEPYR1055"].sum() + df["SEXE1_AGEPYR1065"].sum() + df["SEXE1_AGEPYR1080"].sum() + df["SEXE2_AGEPYR1025"].sum() + df["SEXE2_AGEPYR1040"].sum() + df["SEXE2_AGEPYR1055"].sum() + df["SEXE2_AGEPYR1065"].sum() + df["SEXE2_AGEPYR1080"].sum()
  pop_rsa_fr = df_rsa["ARSAS"].sum()
  rsa_fr = round((pop_rsa_fr/ pop_25p_fr) * 100 , 2)
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Estimation de la part allocataires des RSA (31/12/2021) parmi les personnes de plus de 25 ans (2019) (en %)": [rsa_commune, rsa_epci, rsa_dpt, rsa_reg, rsa_fr]}
  df = pd.DataFrame(data=d)
  st.write(df)

  st.write("La commune compte au 31/12/2021 " + str(alloc_rsa) + " allocataires du RSA socle.")
  if rsa_commune > rsa_epci and rsa_commune > rsa_dpt and rsa_commune > rsa_reg and rsa_commune > rsa_fr:
    st.write("La commune connait une sur-représentation des allocataires du RSA comparativement aux territoires de comparaison.")

  #Commune 2018
  df_rsa_2018 = pd.read_csv("./revenu/rsa/data_CAF2018_COM.csv", dtype={"CODGEO": str, "EPCI": str, "REG": str},sep=";")
  df_rsa_com_2018 = df_rsa_2018.loc[df_rsa_2018["CODGEO"]== code_commune ]
  alloc_rsa_2018 = df_rsa_com_2018["ARSAS"].values[0]
  if alloc_rsa < alloc_rsa_2018:
    st.write("Le nombre d'allocataire du RSA socle a baissé de " + str(alloc_rsa - alloc_rsa_2018) + " depuis 2018")
  else:
    st.write("Le nombre d'allocataire du RSA socle a augmenté de " + str(alloc_rsa_2018 - alloc_rsa) + " depuis 2018")


