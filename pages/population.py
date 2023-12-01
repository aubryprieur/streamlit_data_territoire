import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from pandas.io.json import json_normalize
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
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import plotly.graph_objs as go
import jenkspy

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
  code_region = round(code_region)
  df_region = pd.read_csv("./region2021.csv", dtype={"CHEFLIEU": str}, sep=",")
  nom_region = df_region.loc[df_region['REG'] == code_region, 'LIBELLE'].iloc[0]
  st.sidebar.write('Ma région:', str(round(code_region)), nom_region)

  #############################################################################
  st.title("👵👧👨‍👩‍👧‍👦👨 POPULATION")
  ############
  st.header('1.Répartition de la population')
  st.subheader("Echelle IRIS")
  last_year = "2020"
  st.caption("Dernier millésime " + last_year + " - Paru le : 19/10/2023")
  #year = annee_pers_seule[-2:]
  df_pop_iris = pd.read_csv("./population/base-ic-evol-struct-pop-" + last_year + ".csv", dtype={"IRIS": str, "COM": str, "MODIF_IRIS": str, "LAB_IRIS": str}, sep=";")
  df_iris = pd.read_csv("./iris_2021.csv", dtype={"CODE_IRIS": str}, sep=";")
  df_pop_iris = df_pop_iris.loc[df_pop_iris["COM"] == code_commune]
  df_pop_iris = df_pop_iris[["IRIS", "P" + last_year[-2:] + "_POP"]]
  df_pop_iris["P" + last_year[-2:] + "_POP"] = df_pop_iris["P" + last_year[-2:] + "_POP"].astype(int)
  df_pop_iris = pd.merge(df_pop_iris, df_iris[["CODE_IRIS","LIB_IRIS"]], left_on='IRIS', right_on="CODE_IRIS")
  df_pop_iris = df_pop_iris[["CODE_IRIS","LIB_IRIS", "P" + last_year[-2:] + "_POP"]]
  df_pop_iris["PART_POP"] = (df_pop_iris["P" + last_year[-2:] + "_POP"] / df_pop_iris["P" + last_year[-2:] + "_POP"].sum())* 100
  st.write(df_pop_iris)

  #Carte
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
  gdf = gdf.merge(df_pop_iris, left_on='fields.iris_code', right_on='CODE_IRIS')
  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]
  # Supprimer les lignes avec NaN pour le calcul de la méthode de Jenks
  gdf = gdf.dropna(subset=["P" + last_year[-2:] + "_POP"])
  # S'assurer que toutes les valeurs sont finies
  gdf = gdf[pd.to_numeric(gdf["P" + last_year[-2:] + "_POP"], errors='coerce').notnull()]
  breaks = jenkspy.jenks_breaks(gdf["P" + last_year[-2:] + "_POP"], 5)
  m3 = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

  # Ajouter la carte choroplèthe
  folium.Choropleth(
    geo_data=gdf.set_index('CODE_IRIS'),
    name='choropleth',
    data=df_pop_iris,
    columns=["CODE_IRIS", "P" + last_year[-2:] + "_POP"],
    key_on='feature.id',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    color='#ffffff',
    weight=3,
    opacity=1.0,
    legend_name="Répartition de la population - " + last_year,
    bins=breaks
  ).add_to(m3)

  folium.LayerControl().add_to(m3)

  style_function = lambda x: {'fillColor': '#ffffff',
                          'color':'#000000',
                          'fillOpacity': 0.1,
                          'weight': 0.1}
  highlight_function = lambda x: {'fillColor': '#000000',
                                'color':'#000000',
                                'fillOpacity': 0.50,
                                'weight': 0.1}
  NIL = folium.features.GeoJson(
    gdf,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=["LIB_IRIS", "P" + last_year[-2:] + "_POP"],
        aliases=['Iris: ', "Nombre d'habitants :"],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
    )
  )
  m3.add_child(NIL)
  m3.keep_in_front(NIL)
  st.subheader("Répartition de la population par IRIS - " + last_year)
  # Afficher la carte dans Streamlit
  folium_st.folium_static(m3)

  ############
  st.subheader("Echelle qpv")
  year = "2022"
  df_qpv = pd.read_csv("./population/demographie_qpv/DEMO_" + year + ".csv", dtype={"CODGEO": str}, sep=";")
  df_qpv = df_qpv.loc[df_qpv["LIB_COM"].str.contains(r'(?<!-)\b{}\b'.format(nom_commune))]
  df_qpv = df_qpv[["CODGEO", "LIB_COM", "LIBGEO", "POP_MUN"]]
  st.write(df_qpv)

  #################################################################
  st.header("2.Evolution de la population")
  ############
  st.header('Evolution de la population')
  ville = code_commune
  df_pop_hist = pd.read_csv('./population/base-cc-serie-historique-2019.csv', dtype={"CODGEO": str},sep=";")
  df_pop_hist_ville = df_pop_hist.loc[df_pop_hist["CODGEO"]==code_commune]
  df_pop_hist_ville = df_pop_hist_ville.reset_index()
  df_pop_hist_ville = df_pop_hist_ville.loc[:, 'P19_POP' : 'D68_POP']
  df_pop_hist_ville = df_pop_hist_ville.rename(columns={'P19_POP': '2019','P13_POP': '2013','P08_POP': '2008','D99_POP': '1999','D90_POP': '1990','D82_POP': '1982','D75_POP': '1975','D68_POP': '1968' })
  df_pop_2020 = pd.read_csv('./population/commune_pop_2020.csv', dtype={"Code région": str, "Code département": str, "Code arrondissement": str, "Code canton": str, "Code commune": str},sep=";")
  df_pop_2020["CODGEO"] = df_pop_2020["Code département"] + df_pop_2020["Code commune"]
  df_pop_2020 = df_pop_2020.loc[df_pop_2020["CODGEO"]== code_commune]
  df_pop_2020_com = df_pop_2020['Population municipale'].iloc[0]
  df_pop_2020_com = df_pop_2020_com.replace('\u202f', '')
  df_pop_hist_ville.insert(0, '2020', float(df_pop_2020_com))
  dt_test = df_pop_hist_ville.T
  df_pop_hist_ville.insert(0, 'Commune', nom_commune)
  cols = list(df_pop_hist_ville.columns)
  cols.remove('Commune')
  df_pop_hist_ville = df_pop_hist_ville[['Commune'] + cols[::-1]]
  st.table(df_pop_hist_ville)

  st.caption("Ajouter comparaison évolution de l'EPCI, dpt et région. Permet d'indiquer que c'est une dynamioque propre ou dans un contexte général. ")

  # Graphique
  # Transposition du DataFrame pour le graphique
  df_plot = df_pop_hist_ville.T
  df_plot.columns = ['Population']
  df_plot = df_plot.drop('Commune')  # Supprimer la ligne 'Commune' si elle existe
  # Création du graphique
  fig = go.Figure()
  # Ajout d'une trace pour l'évolution de la population
  fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Population'], mode='lines+markers', name='Population'))
  # Mise à jour du layout
  fig.update_layout(
      title='Évolution de la population',
      xaxis_title='Année',
      yaxis_title='Population',
      hovermode='x'
  )
  # Affichage du graphique dans Streamlit
  st.plotly_chart(fig)

  #Indicateurs clés
  evol_68_20 = df_pop_hist_ville.iloc[0]["2020"] - df_pop_hist_ville.iloc[0]["1968"]
  st.metric(label="Population 2020", value='{:,.0f}'.format(df_pop_hist_ville.iloc[0]["2020"]).replace(",", " "), delta=str('{:,.0f}'.format(evol_68_20.item()).replace(",", " ")) + " hab. depuis 1968")

  ############
  st.subheader('Évolution des soldes migratoires et naturels')
  df_solde_migratoire = pd.read_csv('./population/solde/insee_rp_evol_1968_taux_migratoire.csv', dtype={"codgeo": str},sep=";")
  df_solde_migratoire = df_solde_migratoire.loc[df_solde_migratoire["codgeo"]== code_commune]
  df_solde_naturel = pd.read_csv('./population/solde/insee_rp_evol_1968_taux_naturel.csv', dtype={"codgeo": str},sep=";")
  df_solde_naturel = df_solde_naturel.loc[df_solde_naturel["codgeo"]== code_commune]
  df_solde_migratoire["solde naturel"] = df_solde_naturel["tx_var_pop_part_sn"]
  df_solde_migratoire["solde naturel"] = df_solde_migratoire["solde naturel"].str.replace(',','.')
  df_solde_migratoire["tx_var_pop_part_sm"] = df_solde_migratoire["tx_var_pop_part_sm"].str.replace(',','.')
  df_solde_migratoire["tx_var_pop_part_sm"] = df_solde_migratoire["tx_var_pop_part_sm"].astype(float)
  df_solde_migratoire["solde naturel"] = df_solde_migratoire["solde naturel"].astype(float)
  df_solde_migratoire["variation population"] = df_solde_migratoire["solde naturel"] + df_solde_migratoire["tx_var_pop_part_sm"]
  st.write(df_solde_migratoire)
  ############################################################################
  st.header('3.Les naissances et décès')
  st.caption("Source INSEE: Paru le 07/11/2023 - Millésime 2014-2022")
  last_year_death_birth = "2022"
  # Décès
  df_death = pd.read_csv("./population/deces/base_deces_" + last_year_death_birth + ".csv", dtype={"CODGEO": str}, sep=";")
  df_death = df_death.loc[df_death['CODGEO'] == code_commune]
  df_death = df_death.reset_index(drop=True)
  df_death['CODGEO'] = nom_commune
  cols = ["DECESD14", "DECESD15", "DECESD16", "DECESD17", "DECESD18", "DECESD19", "DECESD20", "DECESD21", "DECESD22"]
  df_death[cols] = df_death[cols].astype(int)
  df_death = df_death.rename(columns={"CODGEO": "Commune", "DECESD14": "2014", "DECESD15": "2015", "DECESD16": "2016", "DECESD17": "2017", "DECESD18": "2018", "DECESD19": "2019", "DECESD20": "2020", "DECESD21": "2021", "DECESD22": "2022"})
  df_death = df_death[["Commune", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022"]]

  # Naissance
  df_birth = pd.read_csv("./petite_enfance/naissance/base_naissances_" + last_year_death_birth + ".csv", dtype={"CODGEO": str}, sep=";")
  df_birth = df_birth.loc[df_birth['CODGEO'] == code_commune]
  df_birth = df_birth.reset_index(drop=True)
  df_birth['CODGEO'] = nom_commune
  cols_naissances = ["NAISD14", "NAISD15", "NAISD16", "NAISD17", "NAISD18", "NAISD19", "NAISD20", "NAISD21", "NAISD22"]
  df_birth = df_birth.rename(columns=dict(zip(cols_naissances, ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022"])))
  df_birth = df_birth.rename(columns={"CODGEO": "Commune"})
  df_birth = df_birth[["Commune", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022"]]

  # Fusion
  df_death['Type'] = 'Décès'
  df_birth['Type'] = 'Naissances'
  df_combined = pd.concat([df_death, df_birth])
  # Réorganisation des colonnes pour mettre 'Type' en première position
  cols = df_combined.columns.tolist()
  cols = [cols[-1]] + cols[:-1]
  df_combined = df_combined[cols]
  df_combined = df_combined.reset_index(drop=True)
  st.write(df_combined)

  # Graphique combiné
  # Création d'une figure Plotly
  fig = go.Figure()
  # Ajout de la ligne pour les décès
  fig.add_trace(go.Scatter(x=df_combined.columns[1:], y=df_combined.iloc[0, 1:], mode='lines+markers', name='Décès'))
  # Ajout de la ligne pour les naissances
  fig.add_trace(go.Scatter(x=df_combined.columns[1:], y=df_combined.iloc[1, 1:], mode='lines+markers', name='Naissances'))
  # Mise à jour du layout pour ajouter des titres et des légendes
  fig.update_layout(
      title='Évolution des naissances et des décès',
      xaxis_title='Année',
      yaxis_title='Nombre',
      legend_title='Type'
  )
  # Calcul du taux de croissance entre 2019 et 2020 pour les décès
  taux_croissance = ((df_combined.loc[0, '2020'] - df_combined.loc[0, '2019']) / df_combined.loc[0, '2019']) * 100
  # Ajouter une ligne verticale pour marquer le début du Covid
  # Convertir toutes les colonnes sauf la première en numérique
  for col in df_combined.columns[1:]:
      df_combined[col] = pd.to_numeric(df_combined[col], errors='coerce')
  fig.add_shape(
      go.layout.Shape(
          type="line",
          x0='2020', y0=min(df_combined.iloc[0, 1:].min(), df_combined.iloc[1, 1:].min()),  # x0 et y0 définissent le point de départ de la ligne
          x1='2020', y1=max(df_combined.iloc[0, 1:].max(), df_combined.iloc[1, 1:].max()),  # Prendre le max entre naissances et décès
          line=dict(color="Red", width=2, dash="dash")
      )
  )
  # Ajouter une annotation pour le début du Covid
  fig.add_annotation(
      go.layout.Annotation(
          text="Début du Covid: +" + str(round(taux_croissance, 2)) + "% de décès",
          x='2020', y=max(df_combined.loc[0, '2020'], df_combined.loc[1, '2020']),
          showarrow=True,
          arrowhead=1,
          xanchor='left',
          yanchor='top'
      )
  )
  # Affichage du graphique dans Streamlit
  st.plotly_chart(fig)

  # Texte évolution
  tx_croissance_deces = (((df_death["2022"] - df_death["2014"]) / df_death["2014"])*100)[0]
  if tx_croissance_deces < 0:
    st.write("La commune connait une baisse des décès depuis 2014 de l'ordre de " + str(round(tx_croissance_deces)) + "%.")
  ############################################################################
  st.header('4.Pyramide des âges')
  st.caption("Dernière année : 2019")
  df = pd.read_csv("./population/pyramide/pop-sexe-age-quinquennal6819.csv", dtype={"RR": str, "DR": str, "CR": str, "STABLE": str, "DR21": str}, sep=";")
  df["CODGEO"] = df["DR"] + df["CR"]
  df = df.loc[df['CODGEO'] == code_commune]
  df_homme = df[["ageq_rec01s1rpop2019", "ageq_rec02s1rpop2019", "ageq_rec03s1rpop2019", "ageq_rec04s1rpop2019", "ageq_rec05s1rpop2019", "ageq_rec06s1rpop2019", "ageq_rec07s1rpop2019", "ageq_rec08s1rpop2019", "ageq_rec09s1rpop2019", "ageq_rec10s1rpop2019", "ageq_rec11s1rpop2019", "ageq_rec12s1rpop2019", "ageq_rec13s1rpop2019", "ageq_rec14s1rpop2019", "ageq_rec15s1rpop2019", "ageq_rec16s1rpop2019", "ageq_rec17s1rpop2019", "ageq_rec18s1rpop2019", "ageq_rec19s1rpop2019", "ageq_rec20s1rpop2019"]]
  df_homme_new = df_homme.rename(columns={'ageq_rec01s1rpop2019': '0-4', 'ageq_rec02s1rpop2019': '5-9', 'ageq_rec03s1rpop2019': '10-14', 'ageq_rec04s1rpop2019': '15-19', 'ageq_rec05s1rpop2019': '20-24', 'ageq_rec06s1rpop2019': '25-29', 'ageq_rec07s1rpop2019': '30-34', 'ageq_rec08s1rpop2019': '35-39', 'ageq_rec09s1rpop2019': '40-44', 'ageq_rec10s1rpop2019': '45-49', 'ageq_rec11s1rpop2019': '50-54', 'ageq_rec12s1rpop2019': '55-59', 'ageq_rec13s1rpop2019': '60-64', 'ageq_rec14s1rpop2019': '65-69', 'ageq_rec15s1rpop2019': '70-74', 'ageq_rec16s1rpop2019': '75-79', 'ageq_rec17s1rpop2019': '80-84', 'ageq_rec18s1rpop2019': '85-89', 'ageq_rec19s1rpop2019': '90-94', 'ageq_rec20s1rpop2019': '95+'})
  df_femme = df[["ageq_rec01s2rpop2019", "ageq_rec02s2rpop2019", "ageq_rec03s2rpop2019", "ageq_rec04s2rpop2019", "ageq_rec05s2rpop2019", "ageq_rec06s2rpop2019", "ageq_rec07s2rpop2019", "ageq_rec08s2rpop2019", "ageq_rec09s2rpop2019", "ageq_rec10s2rpop2019", "ageq_rec11s2rpop2019", "ageq_rec12s2rpop2019", "ageq_rec13s2rpop2019", "ageq_rec14s2rpop2019", "ageq_rec15s2rpop2019", "ageq_rec16s2rpop2019", "ageq_rec17s2rpop2019", "ageq_rec18s2rpop2019", "ageq_rec19s2rpop2019", "ageq_rec20s2rpop2019"]]
  df_femme_new = df_femme.rename(columns={'ageq_rec01s2rpop2019': '0-4', 'ageq_rec02s2rpop2019': '5-9', 'ageq_rec03s2rpop2019': '10-14', 'ageq_rec04s2rpop2019': '15-19', 'ageq_rec05s2rpop2019': '20-24', 'ageq_rec06s2rpop2019': '25-29', 'ageq_rec07s2rpop2019': '30-34', 'ageq_rec08s2rpop2019': '35-39', 'ageq_rec09s2rpop2019': '40-44', 'ageq_rec10s2rpop2019': '45-49', 'ageq_rec11s2rpop2019': '50-54', 'ageq_rec12s2rpop2019': '55-59', 'ageq_rec13s2rpop2019': '60-64', 'ageq_rec14s2rpop2019': '65-69', 'ageq_rec15s2rpop2019': '70-74', 'ageq_rec16s2rpop2019': '75-79', 'ageq_rec17s2rpop2019': '80-84', 'ageq_rec18s2rpop2019': '85-89', 'ageq_rec19s2rpop2019': '90-94', 'ageq_rec20s2rpop2019': '95+'})
  AgeClass = ['0-4','5-9','10-14','15-19','20-24','25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85-89', '90-94', '95+']
  for col in df_homme_new.columns:
    df_homme_new[col] = df_homme_new[col].apply(lambda x: str(x).replace('\u202f', ''))
    df_homme_new[col] = df_homme_new[col].astype(float)
  for col in df_femme_new.columns:
    df_femme_new[col] = df_femme_new[col].apply(lambda x: str(x).replace('\u202f', ''))
    df_femme_new[col] = df_femme_new[col].astype(float)
  ############
  # Graphique
  # Extraction des valeurs
  hommes = df_homme_new.iloc[0, :].values
  femmes = df_femme_new.iloc[0, :].values
  # Création de la figure Plotly
  fig = go.Figure()
  # Ajout des barres pour les hommes
  fig.add_trace(go.Bar(
      y=AgeClass,
      x=hommes,
      name='Hommes',
      orientation='h',
      marker=dict(color='#2B3499'),
      customdata=hommes,
      hovertemplate="%{y}ans : %{customdata}<extra></extra>"
  ))
  # Ajout des barres pour les femmes (avec des valeurs négatives)
  fig.add_trace(go.Bar(
      y=AgeClass,
      x=-femmes,  # Stockées comme négatives pour le positionnement
      name='Femmes',
      orientation='h',
      marker=dict(color='#FF6C22'),
      customdata=femmes,  # Customdata stocke les valeurs originales positives
      hovertemplate="%{y} ans: %{customdata}<extra></extra>"
  ))
  # Mise à jour du layout
  fig.update_layout(
      title_text='Pyramide des âges',
      xaxis_title='Population',
      yaxis_title='Tranche d\'âge',
      legend_title='Genre',
      barmode='relative',
      bargap=0.1,
      xaxis=dict(tickvals=[-max(femmes), -max(femmes)/2, 0, max(hommes)/2, max(hommes)],
                 ticktext=[max(femmes), max(femmes)/2, 0, max(hommes)/2, max(hommes)])
  )
  st.plotly_chart(fig)

  ############
  #TABLEAU
  # Ajouter une colonne 'Sexe' à chaque dataframe
  df_homme_new['Sexe'] = 'Homme'
  df_femme_new['Sexe'] = 'Femme'
  # Concaténer les dataframes
  df_total = pd.concat([df_homme_new, df_femme_new], axis=0)
  # Réorganiser les colonnes pour que 'Sexe' soit la première colonne
  cols = df_total.columns.tolist()
  cols = cols[-1:] + cols[:-1]
  df_total = df_total[cols]
  # Réinitialiser l'index
  df_total = df_total.reset_index(drop=True)
  st.write(df_total)
  ######################################################################
  st.header('4.Dépendance de la population')
  st.caption("Mise en ligne le 27/06/2023 - Millésime 2020")
  st.caption("L’indicateur de dépendance économique est le rapport entre la population des jeunes et des personnes âgées (moins de 20 ans et plus de 59 ans) sur la population en âge de travailler (20 à 59 ans). Il permet d’appréhender la charge, en termes économiques, que représentent les jeunes et les personnes âgées, par rapport à la population en âge de travailler.")
  df = pd.read_csv("./population/commune/ages_tranche_1_an/TD_POP1B_" + last_year + ".csv", dtype={"CODGEO": str}, sep=";")
  df_commune = df[df['CODGEO'] == code_commune ]
  tranches_age_00_19 = [f'AGED1000{age:02d}' for age in range(20)]
  tranches_age_00_19_HF = [f'SEXE{sexe}_{age}' for sexe in [1, 2] for age in tranches_age_00_19]
  age_00_19 = df_commune[tranches_age_00_19_HF].sum(axis=1)
  tranches_age_60_et_plus = [f'AGED1000{age}' for age in range(60, 100)] + ['AGED100100']
  tranches_age_60_et_plus_HF = [f'SEXE{sexe}_{age}' for sexe in [1, 2] for age in tranches_age_60_et_plus]
  age_60P = df_commune[tranches_age_60_et_plus_HF].sum(axis=1)
  tranches_age_20_a_59 = [f'AGED1000{age}' for age in range(20, 60)]
  tranches_age_20_a_59_HF = [f'SEXE{sexe}_{age}' for sexe in [1, 2] for age in tranches_age_20_a_59]
  total_20_a_59 = df_commune[tranches_age_20_a_59_HF].sum(axis=1)
  population_dependante = age_00_19 + age_60P
  indice_dependance = (population_dependante / total_20_a_59) * 100
  valeur_indice_dependance = indice_dependance.iloc[0]
  st.metric("L'indice de dépendance de la commune est de ", str(round(valeur_indice_dependance)))
  if valeur_indice_dependance > 100:
    st.warning("Un indice de dépendance supérieur à 100 indique une proportion plus importante de population non active (jeunes et personnes âgées) par rapport à la population active. Cela peut être dû à des taux de natalité élevés, une longévité accrue, ou une combinaison des deux. La dynamique migratoire locale (comme une émigration des jeunes adultes) peut également influencer cet indice.un tel indice peut avoir des implications possible sur la fiscalité ou encore il peut y avoir une demande accrue pour des services de santé et de soins aux personnes âgées, ainsi que pour l'éducation et les services pour les jeunes.")
  else :
    st.info("Cela suggère une plus grande proportion de la population en âge de travailler par rapport aux personnes dépendantes. Indique une population relativement jeune et active, offrant des avantages économiques mais nécessitant également une gestion efficace pour assurer des opportunités d'emploi ou encore l'accessibilité au logement. La commune peut bénéficier d'une base fiscale plus large et offre une plus grande capacité d'investissement dans les infrastructures publiques, l'éducation, la santé, et d'autres services essentiels.")
  ############################################################################

  st.header("5.Répartition de la population par tranches d'âge")
  st.subheader('Comparaison entre iris')
  st.caption("Dernier millésime " + last_year + " - Paru le : 19/10/2023")
  df = pd.read_csv("./population/base-ic-evol-struct-pop-" + last_year + ".csv", dtype={"IRIS": str , "COM": str},sep=";")
  year = last_year[-2:]
  df_tranche_age = df.loc[df["COM"] == code_commune]
  df_tranche_age = df_tranche_age[["IRIS","P" + year +"_POP","P" + year +"_POP0014", "P" + year +"_POP1529", "P" + year +"_POP3044", "P" + year +"_POP4559", "P" + year +"_POP6074", "P" + year +"_POP75P"]]
  df_tranche_age["part_pop0014"] = df_tranche_age["P" + year +"_POP0014"] / df_tranche_age["P" + year +"_POP"] * 100
  df_tranche_age["part_pop1529"] = df_tranche_age["P" + year +"_POP1529"] / df_tranche_age["P" + year +"_POP"] * 100
  df_tranche_age["part_pop3044"] = df_tranche_age["P" + year +"_POP3044"] / df_tranche_age["P" + year +"_POP"] * 100
  df_tranche_age["part_pop4559"] = df_tranche_age["P" + year +"_POP4559"] / df_tranche_age["P" + year +"_POP"] * 100
  df_tranche_age["part_pop6074"] = df_tranche_age["P" + year +"_POP6074"] / df_tranche_age["P" + year +"_POP"] * 100
  df_tranche_age["part_pop75P"] = df_tranche_age["P" + year +"_POP75P"] / df_tranche_age["P" + year +"_POP"] * 100
  df_tranche_age = df_tranche_age[["IRIS","part_pop0014","part_pop1529", "part_pop3044", "part_pop4559" ,"part_pop6074" , "part_pop75P"]]
  communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
  df_tranche_age_iris = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_tranche_age[["IRIS","part_pop0014","part_pop1529", "part_pop3044", "part_pop4559" ,"part_pop6074" , "part_pop75P"]], left_on='CODE_IRIS', right_on="IRIS")
  df_tranche_age_iris = df_tranche_age_iris[["IRIS","LIB_IRIS","part_pop0014","part_pop1529", "part_pop3044", "part_pop4559" ,"part_pop6074" , "part_pop75P"]]
  df_tranche_age_iris = df_tranche_age_iris.reset_index(drop=True)
  df_tranche_age_iris = df_tranche_age_iris.rename(columns={'LIB_IRIS': "Nom de l'iris",'IRIS': "Code de l'iris", "part_pop0014" : '00-14 ans' , "part_pop1529" : '15-29 ans' , "part_pop3044" : "30-44 ans", "part_pop4559" : "45-59 ans", "part_pop6074" : "60-74 ans", "part_pop75P" : "Plus de 75 ans"})
  st.write(df_tranche_age_iris)

  fig = px.bar(df_tranche_age_iris, x="Nom de l'iris", y=["00-14 ans","15-29 ans", "30-44 ans", "45-59 ans" ,"60-74 ans" , "Plus de 75 ans"], title="Répartition de la population", height=600, width=800)
  st.plotly_chart(fig, use_container_width=False)
  #################
  st.subheader('Comparaison entre territoires')
  st.caption("Agrégation à partir de l'échelle communale.")
  #Commune
  def tranche_age_com(fichier, commune, annee):
    df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str, "REG" : str}, sep = ';')
    year = annee[-2:]
    df = df.loc[df["CODGEO"] == commune]
    df = df[["CODGEO","LIBGEO", "P" + year +"_POP","P" + year +"_POP0014", "P" + year +"_POP1529", "P" + year +"_POP3044", "P" + year +"_POP4559", "P" + year +"_POP6074", "P" + year +"_POP7589", "P" + year +"_POP90P"]]
    pop0014 = (df["P" + year +"_POP0014"] / df["P" + year +"_POP"] * 100).iloc[0]
    pop1529 = (df["P" + year +"_POP1529"] / df["P" + year +"_POP"] * 100).iloc[0]
    pop3044 = (df["P" + year +"_POP3044"] / df["P" + year +"_POP"] * 100).iloc[0]
    pop4559 = (df["P" + year +"_POP4559"] / df["P" + year +"_POP"] * 100).iloc[0]
    pop6074 = (df["P" + year +"_POP6074"] / df["P" + year +"_POP"] * 100).iloc[0]
    pop75P = ((df["P" + year +"_POP7589"] + df["P" + year +"_POP90P"]) / df["P" + year +"_POP"] * 100).iloc[0]
    nom = df["LIBGEO"].iloc[0]
    df_tranches_age_com = pd.DataFrame(data=[[nom,pop0014,pop1529,pop3044,pop4559,pop6074,pop75P]], columns = ["territoire","pop0014","pop1529","pop3044", "pop4559","pop6074", "pop75P"])
    return df_tranches_age_com
  tranches_age_com = tranche_age_com("./population/commune/base-cc-evol-struct-pop-" + last_year + ".csv", code_commune, last_year)
  #EPCI
  def tranche_age_epci(fichier, epci, annee):
    epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
    df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str, "REG" : str}, sep = ';')
    year = annee[-2:]
    df_epci = pd.merge(df, epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
    df_epci = df_epci.loc[df_epci["EPCI"]==str(epci), ['EPCI', 'LIBEPCI',"P" + year +"_POP", "P" + year +"_POP0014" , "P" + year +"_POP1529","P" + year +"_POP3044", "P" + year +"_POP4559","P" + year +"_POP6074", "P" + year +"_POP7589", "P" + year +"_POP90P"]]
    pop0014 = (df_epci.loc[:, "P" + year +"_POP0014"].sum() / df_epci["P" + year +"_POP"].sum()) * 100
    pop1529 = (df_epci.loc[:, "P" + year +"_POP1529"].sum() / df_epci["P" + year +"_POP"].sum()) * 100
    pop3044 = (df_epci.loc[:, "P" + year +"_POP3044"].sum() / df_epci["P" + year +"_POP"].sum()) * 100
    pop4559 = (df_epci.loc[:, "P" + year +"_POP4559"].sum() / df_epci["P" + year +"_POP"].sum()) * 100
    pop6074 = (df_epci.loc[:, "P" + year +"_POP6074"].sum() / df_epci["P" + year +"_POP"].sum()) * 100
    pop75P = ((df_epci.loc[:, "P" + year +"_POP7589"].sum() + df_epci.loc[:, "P" + year +"_POP90P"].sum())  / df_epci["P" + year +"_POP"].sum()) * 100
    df_tranches_age_epci = pd.DataFrame(data=[[nom_epci,pop0014,pop1529,pop3044,pop4559,pop6074,pop75P]], columns = ["territoire","pop0014","pop1529","pop3044", "pop4559","pop6074", "pop75P"])
    return df_tranches_age_epci
  tranches_age_epci = tranche_age_epci("./population/commune/base-cc-evol-struct-pop-" + last_year + ".csv", code_epci, last_year)
  #Dpt
  def tranche_age_departement(fichier, departement, annee):
    df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str, "REG": str},sep = ';')
    year = annee[-2:]
    df_departement = df.loc[df["DEP"] == departement, ["P" + year +"_POP", "P" + year +"_POP0014" , "P" + year +"_POP1529","P" + year +"_POP3044", "P" + year +"_POP4559","P" + year +"_POP6074","P" + year +"_POP7589","P" + year +"_POP90P"]]
    pop0014 = (df_departement.loc[:, "P" + year +"_POP0014"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
    pop1529 = (df_departement.loc[:, "P" + year +"_POP1529"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
    pop3044 = (df_departement.loc[:, "P" + year +"_POP3044"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
    pop4559 = (df_departement.loc[:, "P" + year +"_POP4559"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
    pop6074 = (df_departement.loc[:, "P" + year +"_POP6074"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
    pop75P = ((df_departement.loc[:, "P" + year +"_POP7589"].sum() + df_departement.loc[:, "P" + year +"_POP90P"].sum()) / df_departement["P" + year +"_POP"].sum()) * 100
    df_tranches_age_dpt = pd.DataFrame(data=[[nom_departement,pop0014,pop1529,pop3044,pop4559,pop6074,pop75P]], columns = ["territoire","pop0014","pop1529","pop3044", "pop4559","pop6074", "pop75P"])
    return df_tranches_age_dpt
  tranche_age_departement = tranche_age_departement("./population/commune/base-cc-evol-struct-pop-" + last_year + ".csv", code_departement, last_year)
  #Région
  def tranche_age_region(fichier, region, annee):
    df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str, "REG": str},sep = ';')
    year = annee[-2:]
    df_region = df.loc[df["REG"]== region, ["P" + year +"_POP", "P" + year +"_POP0014" , "P" + year +"_POP1529","P" + year +"_POP3044", "P" + year +"_POP4559","P" + year +"_POP6074","P" + year +"_POP7589","P" + year +"_POP90P"]]
    pop0014 = (df_region.loc[:, "P" + year +"_POP0014"].sum() / df_region["P" + year +"_POP"].sum()) * 100
    pop1529 = (df_region.loc[:, "P" + year +"_POP1529"].sum() / df_region["P" + year +"_POP"].sum()) * 100
    pop3044 = (df_region.loc[:, "P" + year +"_POP3044"].sum() / df_region["P" + year +"_POP"].sum()) * 100
    pop4559 = (df_region.loc[:, "P" + year +"_POP4559"].sum() / df_region["P" + year +"_POP"].sum()) * 100
    pop6074 = (df_region.loc[:, "P" + year +"_POP6074"].sum() / df_region["P" + year +"_POP"].sum()) * 100
    pop75P = ((df_region.loc[:, "P" + year +"_POP7589"].sum() + df_region.loc[:, "P" + year +"_POP90P"].sum() )/ df_region["P" + year +"_POP"].sum()) * 100
    df_tranches_age_region = pd.DataFrame(data=[[nom_region,pop0014,pop1529,pop3044,pop4559,pop6074,pop75P]], columns = ["territoire","pop0014","pop1529","pop3044", "pop4559","pop6074", "pop75P"])
    return df_tranches_age_region
  tranche_age_region = tranche_age_region("./population/commune/base-cc-evol-struct-pop-" + last_year + ".csv",str(round(code_region)), last_year)
  # France
  def tranche_age_france(fichier, annee):
    df = pd.read_csv(fichier, dtype={"CODGEO": str, "DEP": str, "REG": str}, sep = ';')
    year = annee[-2:]
    pop0014 = (df.loc[:, "P" + year +"_POP0014"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop1529 = (df.loc[:, "P" + year +"_POP1529"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop3044 = (df.loc[:, "P" + year +"_POP3044"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop4559 = (df.loc[:, "P" + year +"_POP4559"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop6074 = (df.loc[:, "P" + year +"_POP6074"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop75P = ((df.loc[:, "P" + year +"_POP7589"].sum() + df.loc[:, "P" + year +"_POP90P"].sum()) / df["P" + year +"_POP"].sum()) * 100
    df_tranches_age_france = pd.DataFrame(data=[["France",pop0014,pop1529,pop3044,pop4559,pop6074,pop75P]], columns = ["territoire","pop0014","pop1529","pop3044", "pop4559","pop6074", "pop75P"])
    return df_tranches_age_france
  tranche_age_france = tranche_age_france("./population/commune/base-cc-evol-struct-pop-" + last_year + ".csv", last_year)

  df_glob_tranches_age = pd.concat([tranches_age_com, tranches_age_epci, tranche_age_departement, tranche_age_region, tranche_age_france])
  df_glob_tranches_age = df_glob_tranches_age.rename(columns={'territoire': "Territoires",'pop0014': "00-14 ans", "pop1529" : '15-29 ans' , "pop3044" : '30-44 ans' , "pop4559" : "45-59 ans", "pop6074" : "60-74 ans", "pop75P" : "Plus de 75 ans"})
  df_glob_tranches_age = df_glob_tranches_age.reset_index(drop=True)
  st.write('Tableau')
  st.write(df_glob_tranches_age)

  fig = px.bar(df_glob_tranches_age, x="Territoires", y=["00-14 ans","15-29 ans", "30-44 ans", "45-59 ans" ,"60-74 ans" , "Plus de 75 ans"], title="Graphique", height=600, width=800)
  st.plotly_chart(fig, use_container_width=False)
  ###########################################################################
  st.header("6.Personnes vivant seules")
  last_year = "2020"
  year = last_year[-2:]
  st.caption("Dernier millésime : " + last_year + " - Paru le : 27/06/2023")
  st.caption("Calculs à partir des communes. Je ne retrouve pas le meme résultat (en dehors de l'échelle commune) si je compare avec le site Statistiques Locales de l'INSEE.")
  df = pd.read_csv("./population/pers_seules/base-cc-coupl-fam-men-" + last_year + ".csv", dtype={"CODGEO": str, "REG": str, "DEP": str, "LIBGEO": str}, sep=";")
  #Commune
  df_com = df.loc[df['CODGEO'] == code_commune]
  df_com["1519_seul"] = (df_com['P' + year + '_POP1519_PSEUL'] / df_com['P' + year + '_POP1519']) * 100
  df_com["2024_seul"] = (df_com['P' + year + '_POP2024_PSEUL'] / df_com['P' + year + '_POP2024']) * 100
  df_com["2539_seul"] = (df_com['P' + year + '_POP2539_PSEUL'] / df_com['P' + year + '_POP2539']) * 100
  df_com["4054_seul"] = (df_com['P' + year + '_POP4054_PSEUL'] / df_com['P' + year + '_POP4054']) * 100
  df_com["5564_seul"] = (df_com['P' + year + '_POP5564_PSEUL'] / df_com['P' + year + '_POP5564']) * 100
  df_com["6579_seul"] = (df_com['P' + year + '_POP6579_PSEUL'] / df_com['P' + year + '_POP6579']) * 100
  df_com["80P_seul"] = (df_com['P' + year + '_POP80P_PSEUL'] / df_com['P' + year + '_POP80P']) * 100
  df_pop_seule_com = df_com[["LIBGEO", "1519_seul", "2024_seul", "2539_seul", "4054_seul", "5564_seul", "6579_seul", "80P_seul" ]]
  df_pop_seule_com = df_pop_seule_com.reset_index(drop=True)
  #EPCI
  epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci = pd.merge(df, epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci.loc[df_epci["EPCI"]==str(code_epci), ['LIBEPCI', "P" + year + "_POP1519_PSEUL", 'P' + year + '_POP2024_PSEUL', 'P' + year + '_POP2539_PSEUL', 'P' + year + '_POP4054_PSEUL', 'P' + year + '_POP5564_PSEUL', 'P' + year + '_POP6579_PSEUL', 'P' + year + '_POP80P_PSEUL', "P" + year + "_POP1519", 'P' + year + '_POP2024', 'P' + year + '_POP2539', 'P' + year + '_POP4054', 'P' + year + '_POP5564', 'P' + year + '_POP6579', 'P' + year + '_POP80P']]
  pop1519seul = ( df_epci['P' + year + '_POP1519_PSEUL'].sum() / df_epci['P' + year +'_POP1519'].sum() ) * 100
  pop2024seul = ( df_epci['P' + year + '_POP2024_PSEUL'].sum() / df_epci['P' + year + '_POP2024'].sum()) * 100
  pop2539seul = ( df_epci['P' + year + '_POP2539_PSEUL'].sum() / df_epci['P' + year + '_POP2539'].sum()) * 100
  pop4054seul = ( df_epci['P' + year + '_POP4054_PSEUL'].sum() / df_epci['P' + year + '_POP4054'].sum()) * 100
  pop5564seul = ( df_epci['P' + year + '_POP5564_PSEUL'].sum() / df_epci['P' + year + '_POP5564'].sum()) * 100
  pop6579seul = ( df_epci['P' + year + '_POP6579_PSEUL'].sum() / df_epci['P' + year + '_POP6579'].sum()) * 100
  pop80Pseul = (df_epci['P' + year + '_POP80P_PSEUL'].sum() / df_epci['P' + year + '_POP80P'].sum()) * 100
  df_pop_seule_epci = pd.DataFrame(data=[[nom_epci,pop1519seul,pop2024seul,pop2539seul,pop4054seul,pop5564seul,pop6579seul, pop80Pseul]], columns = ["LIBGEO", "1519_seul", "2024_seul", "2539_seul", "4054_seul", "5564_seul", "6579_seul", "80P_seul"])
  #Département
  df_dep = df.loc[df['DEP'] == code_departement]
  df_dep = df_dep[["DEP", "P" + year + "_POP1519_PSEUL", 'P' + year + '_POP2024_PSEUL', 'P' + year + '_POP2539_PSEUL', 'P' + year + '_POP4054_PSEUL', 'P' + year + '_POP5564_PSEUL', 'P' + year + '_POP6579_PSEUL', 'P' + year + '_POP80P_PSEUL', "P" + year + "_POP1519", 'P' + year + '_POP2024', 'P' + year + '_POP2539', 'P' + year + '_POP4054', 'P' + year + '_POP5564', 'P' + year + '_POP6579', 'P' + year + '_POP80P']]
  pop1519seul = ( df_dep['P' + year + '_POP1519_PSEUL'].sum() / df_dep['P' + year +'_POP1519'].sum() ) * 100
  pop2024seul = ( df_dep['P' + year + '_POP2024_PSEUL'].sum() / df_dep['P' + year + '_POP2024'].sum()) * 100
  pop2539seul = ( df_dep['P' + year + '_POP2539_PSEUL'].sum() / df_dep['P' + year + '_POP2539'].sum()) * 100
  pop4054seul = ( df_dep['P' + year + '_POP4054_PSEUL'].sum() / df_dep['P' + year + '_POP4054'].sum()) * 100
  pop5564seul = ( df_dep['P' + year + '_POP5564_PSEUL'].sum() / df_dep['P' + year + '_POP5564'].sum()) * 100
  pop6579seul = ( df_dep['P' + year + '_POP6579_PSEUL'].sum() / df_dep['P' + year + '_POP6579'].sum()) * 100
  pop80Pseul = (df_dep['P' + year + '_POP80P_PSEUL'].sum() / df_dep['P' + year + '_POP80P'].sum()) * 100
  df_pop_seule_dep = pd.DataFrame(data=[[nom_departement,pop1519seul,pop2024seul,pop2539seul,pop4054seul,pop5564seul,pop6579seul, pop80Pseul]], columns = ["LIBGEO", "1519_seul", "2024_seul", "2539_seul", "4054_seul", "5564_seul", "6579_seul", "80P_seul"])
  #Région
  df_reg = df.loc[df['REG'] == str(code_region)]
  df_reg = df_reg[["REG", "P" + year + "_POP1519_PSEUL", 'P' + year + '_POP2024_PSEUL', 'P' + year + '_POP2539_PSEUL', 'P' + year + '_POP4054_PSEUL', 'P' + year + '_POP5564_PSEUL', 'P' + year + '_POP6579_PSEUL', 'P' + year + '_POP80P_PSEUL', "P" + year + "_POP1519", 'P' + year + '_POP2024', 'P' + year + '_POP2539', 'P' + year + '_POP4054', 'P' + year + '_POP5564', 'P' + year + '_POP6579', 'P' + year + '_POP80P']]
  pop1519seul = ( df_reg['P' + year + '_POP1519_PSEUL'].sum() / df_reg['P' + year +'_POP1519'].sum() ) * 100
  pop2024seul = ( df_reg['P' + year + '_POP2024_PSEUL'].sum() / df_reg['P' + year + '_POP2024'].sum()) * 100
  pop2539seul = ( df_reg['P' + year + '_POP2539_PSEUL'].sum() / df_reg['P' + year + '_POP2539'].sum()) * 100
  pop4054seul = ( df_reg['P' + year + '_POP4054_PSEUL'].sum() / df_reg['P' + year + '_POP4054'].sum()) * 100
  pop5564seul = ( df_reg['P' + year + '_POP5564_PSEUL'].sum() / df_reg['P' + year + '_POP5564'].sum()) * 100
  pop6579seul = ( df_reg['P' + year + '_POP6579_PSEUL'].sum() / df_reg['P' + year + '_POP6579'].sum()) * 100
  pop80Pseul = (df_reg['P' + year + '_POP80P_PSEUL'].sum() / df_reg['P' + year + '_POP80P'].sum()) * 100
  df_pop_seule_reg = pd.DataFrame(data=[[nom_region,pop1519seul,pop2024seul,pop2539seul,pop4054seul,pop5564seul,pop6579seul, pop80Pseul]], columns = ["LIBGEO", "1519_seul", "2024_seul", "2539_seul", "4054_seul", "5564_seul", "6579_seul", "80P_seul"])
  #France
  df_fr = df[["REG", "P" + year + "_POP1519_PSEUL", 'P' + year + '_POP2024_PSEUL', 'P' + year + '_POP2539_PSEUL', 'P' + year + '_POP4054_PSEUL', 'P' + year + '_POP5564_PSEUL', 'P' + year + '_POP6579_PSEUL', 'P' + year + '_POP80P_PSEUL', "P" + year + "_POP1519", 'P' + year + '_POP2024', 'P' + year + '_POP2539', 'P' + year + '_POP4054', 'P' + year + '_POP5564', 'P' + year + '_POP6579', 'P' + year + '_POP80P']]
  pop1519seul = ( df_fr['P' + year + '_POP1519_PSEUL'].sum() / df_fr['P' + year +'_POP1519'].sum() ) * 100
  pop2024seul = ( df_fr['P' + year + '_POP2024_PSEUL'].sum() / df_fr['P' + year + '_POP2024'].sum()) * 100
  pop2539seul = ( df_fr['P' + year + '_POP2539_PSEUL'].sum() / df_fr['P' + year + '_POP2539'].sum()) * 100
  pop4054seul = ( df_fr['P' + year + '_POP4054_PSEUL'].sum() / df_fr['P' + year + '_POP4054'].sum()) * 100
  pop5564seul = ( df_fr['P' + year + '_POP5564_PSEUL'].sum() / df_fr['P' + year + '_POP5564'].sum()) * 100
  pop6579seul = ( df_fr['P' + year + '_POP6579_PSEUL'].sum() / df_fr['P' + year + '_POP6579'].sum()) * 100
  pop80Pseul = ( df_fr['P' + year + '_POP80P_PSEUL'].sum() / df_fr['P' + year + '_POP80P'].sum()) * 100
  df_pop_seule_fr = pd.DataFrame(data=[["France",pop1519seul,pop2024seul,pop2539seul,pop4054seul,pop5564seul,pop6579seul, pop80Pseul]], columns = ["LIBGEO", "1519_seul", "2024_seul", "2539_seul", "4054_seul", "5564_seul", "6579_seul", "80P_seul"])

  df_glob_pers_seules = pd.concat([df_pop_seule_com, df_pop_seule_epci, df_pop_seule_dep, df_pop_seule_reg, df_pop_seule_fr])
  st.write(df_glob_pers_seules)

  ###########
  #IRIS
  st.caption("Dernier millésime " + last_year + " - Paru le : 19/10/2023")
  df_iris = pd.read_csv("./population/pers_seules/base-ic-couples-familles-menages-" + last_year + ".csv", dtype={"IRIS": str, "REG": str, "DEP": str, "UU2020": str, "COM": str, "TRIRIS": str, "GRD_QUART": str, "TYP_IRIS": str, "MODIF_IRIS": str, "LABIRIS": str}, sep=";")
  df_iris = df_iris.loc[df_iris['COM'] == code_commune]
  df_iris["pop1524seul"] = ( df_iris['P' + last_year[-2:] + '_POP1524_PSEUL'] / df_iris['P' + last_year[-2:] + '_POP1524']) * 100
  df_iris["pop2554seul"] = ( df_iris['P' + last_year[-2:] + '_POP2554_PSEUL'] / df_iris['P' + last_year[-2:] + '_POP2554']) * 100
  df_iris["pop5579seul"] = ( df_iris['P' + last_year[-2:] + '_POP5579_PSEUL'] / df_iris['P' + last_year[-2:] + '_POP5579']) * 100
  df_iris["pop80Pseul"] = ( df_iris['P' + last_year[-2:] + '_POP80P_PSEUL'] / df_iris['P' + last_year[-2:] + '_POP80P']) * 100
  df_iris = df_iris[["IRIS", "LIBIRIS", "pop1524seul", "pop2554seul", "pop5579seul", "pop80Pseul"]]
  df_iris = df_iris.reset_index(drop=True)
  st.write(df_iris)

  #Carte 15-25 ans vivant seuls
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
  gdf = gdf.merge(df_iris, left_on='fields.iris_code', right_on='IRIS')

  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]
  # Supprimer les lignes avec NaN pour le calcul de la méthode de Jenks
  gdf = gdf.dropna(subset=['pop1524seul'])
  # S'assurer que toutes les valeurs sont finies
  gdf = gdf[pd.to_numeric(gdf['pop1524seul'], errors='coerce').notnull()]
  breaks = jenkspy.jenks_breaks(gdf['pop1524seul'], 5)
  m = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

  # Ajouter la carte choroplèthe
  folium.Choropleth(
    geo_data=gdf.set_index('IRIS'),
    name='choropleth',
    data=df_iris,
    columns=['IRIS', 'pop1524seul'],
    key_on='feature.id',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    color='#ffffff',
    weight=3,
    opacity=1.0,
    legend_name='Part des 15-24 ans vivant seuls',
    bins=breaks
  ).add_to(m)

  folium.LayerControl().add_to(m)

  style_function = lambda x: {'fillColor': '#ffffff',
                          'color':'#000000',
                          'fillOpacity': 0.1,
                          'weight': 0.1}
  highlight_function = lambda x: {'fillColor': '#000000',
                                'color':'#000000',
                                'fillOpacity': 0.50,
                                'weight': 0.1}
  NIL = folium.features.GeoJson(
    gdf,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=["LIBIRIS", "pop1524seul"],
        aliases=['Iris: ', "Part des 15-24 ans vivant seuls :"],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
    )
  )
  m.add_child(NIL)
  m.keep_in_front(NIL)
  st.subheader("Les 15-24 ans vivant seuls par IRIS - " + last_year)
  # Afficher la carte dans Streamlit
  folium_st.folium_static(m)

  # Carte IRIS Plus de 80 ans vivant seuls
  # Créer une nouvelle carte pour les plus de 80 ans vivant seuls
  # Supprimer les lignes avec NaN pour le calcul de la méthode de Jenks
  gdf = gdf.dropna(subset=['pop80Pseul'])
  # S'assurer que toutes les valeurs sont finies
  gdf = gdf[pd.to_numeric(gdf['pop80Pseul'], errors='coerce').notnull()]
  breaks = jenkspy.jenks_breaks(gdf['pop80Pseul'], 5)
  m2 = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

  # Ajouter la carte choroplèthe
  folium.Choropleth(
    geo_data=gdf.set_index('IRIS'),
    name='choropleth',
    data=df_iris,
    columns=['IRIS', 'pop80Pseul'],
    key_on='feature.id',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    color='#ffffff',
    weight=3,
    opacity=1.0,
    legend_name='Part des plus de 80 ans vivant seuls',
    bins=breaks
  ).add_to(m2)

  folium.LayerControl().add_to(m2)

  style_function = lambda x: {'fillColor': '#ffffff',
                          'color':'#000000',
                          'fillOpacity': 0.1,
                          'weight': 0.1}
  highlight_function = lambda x: {'fillColor': '#000000',
                                'color':'#000000',
                                'fillOpacity': 0.50,
                                'weight': 0.1}
  NIL = folium.features.GeoJson(
    gdf,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=["LIBIRIS", "pop80Pseul"],
        aliases=['Iris: ', "Part des plus de 80 ans vivant seuls :"],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
    )
  )
  m2.add_child(NIL)
  m2.keep_in_front(NIL)
  st.subheader("Les plus de 80 ans ans vivant seuls par IRIS")
  # Afficher la carte dans Streamlit
  folium_st.folium_static(m2)
  #############################################################################
  st.header('7.Personnes immigrées')
  st.caption("Dernier millésime " + last_year + " - Paru le : 19/10/2023")
  st.caption("Selon la définition adoptée par le Haut Conseil à l’Intégration, un immigré est une personne née étrangère à l’étranger et résidant en France. Les personnes nées françaises à l’étranger et vivant en France ne sont donc pas comptabilisées. À l’inverse, certains immigrés ont pu devenir français, les autres restant étrangers. Les populations étrangère et immigrée ne se confondent pas totalement : un immigré n’est pas nécessairement étranger et réciproquement, certains étrangers sont nés en France (essentiellement des mineurs). La qualité d’immigré est permanente : un individu continue à appartenir à la population immigrée même s’il devient français par acquisition. C’est le pays de naissance, et non la nationalité à la naissance, qui définit l'origine géographique d’un immigré.")

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
  indice_imm_iris = part_pers_imm_iris("./population/base-ic-evol-struct-pop-" + last_year + ".csv",code_commune, last_year)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(indice_imm_iris)
  ###############
  #CARTE
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
  gdf = gdf.merge(indice_imm_iris, left_on='fields.iris_code', right_on="Code de l'iris")
  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]
  # Créer une nouvelle carte pour la répartition de la population par iris
  # Supprimer les lignes avec NaN pour le calcul de la méthode de Jenks
  gdf = gdf.dropna(subset=["Part des personnes immigrées"])
  # S'assurer que toutes les valeurs sont finies
  gdf = gdf[pd.to_numeric(gdf["Part des personnes immigrées"], errors='coerce').notnull()]
  breaks = jenkspy.jenks_breaks(gdf["Part des personnes immigrées"], 5)
  m3 = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

  # Ajouter la carte choroplèthe
  folium.Choropleth(
    geo_data=gdf.set_index("fields.iris_code"),
    name='choropleth',
    data=indice_imm_iris,
    columns=["Code de l'iris", "Part des personnes immigrées"],
    key_on='feature.id',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    color='#ffffff',
    weight=3,
    opacity=1.0,
    legend_name='Part des personnes immigrées',
    bins=breaks
  ).add_to(m3)

  folium.LayerControl().add_to(m3)

  style_function = lambda x: {'fillColor': '#ffffff',
                          'color':'#000000',
                          'fillOpacity': 0.1,
                          'weight': 0.1}
  highlight_function = lambda x: {'fillColor': '#000000',
                                'color':'#000000',
                                'fillOpacity': 0.50,
                                'weight': 0.1}
  NIL = folium.features.GeoJson(
    gdf,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=["Nom de l'iris", "Part des personnes immigrées"],
        aliases=['Iris: ', "Part des personnes immigrées :"],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
    )
  )
  m3.add_child(NIL)
  m3.keep_in_front(NIL)
  st.subheader("Part des personnes immigrées")
  # Afficher la carte dans Streamlit
  folium_st.folium_static(m3)
  #############
  st.subheader("Comparaison")
  st.caption("ATTENTION, pour agréger j'ai repris les IRIS, pour agrégé à partir de l'échelle commune les bases imm et etrangers sont isolées, à refaire....")
  #Commune
  df_imm = pd.read_csv("./population/base-ic-evol-struct-pop-" + last_year + ".csv", dtype={"CODGEO": str , "DEP": str , "REG": str},sep=";")
  df_imm_com = df_imm.loc[df_imm["COM"] == code_commune ]
  pop_imm = df_imm_com['P' + last_year[-2:] + '_POP_IMM'].sum()
  pop = df_imm_com['P' + last_year[-2:] + '_POP'].sum()
  part_pop_imm_commune = round(((pop_imm / pop) * 100), 2)
  #EPCI
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_imm_epci = pd.merge(df_imm, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
  df_imm_epci = df_imm_epci.loc[df_imm_epci["EPCI"] == str(code_epci)]
  pop_imm_epci = df_imm_epci['P' + last_year[-2:] + '_POP_IMM'].sum()
  pop_epci = df_imm_epci['P' + last_year[-2:] + '_POP'].sum()
  part_pop_imm_epci = round(((pop_imm_epci / pop_epci) * 100), 2)
  #Département
  df_dpt = pd.read_csv("./population/base-ic-evol-struct-pop-" + last_year + ".csv", dtype={"COM": str, "DEP": str}, sep = ';')
  df_dpt = df_dpt.loc[df_dpt["DEP"] == str(code_departement)]
  pop_imm_dpt = df_dpt['P' + last_year[-2:] + '_POP_IMM'].sum()
  pop_dpt = df_dpt['P' + last_year[-2:] + '_POP'].sum()
  part_pop_imm_dpt = round(((pop_imm_dpt / pop_dpt) * 100), 2)
  #Région
  df_reg = pd.read_csv("./population/base-ic-evol-struct-pop-" + last_year + ".csv", dtype={"COM": str, "DEP": str, "REG": str}, sep = ';')
  df_reg = df_reg.loc[df_reg["REG"] == str(code_region)]
  pop_imm_reg = df_reg['P' + last_year[-2:] + '_POP_IMM'].sum()
  pop_reg = df_reg['P' + last_year[-2:] + '_POP'].sum()
  part_pop_imm_reg = round(((pop_imm_reg / pop_reg) * 100), 2)
  #France
  pop_imm_fr = df_imm['P' + last_year[-2:] + '_POP_IMM'].sum()
  pop_fr = df_imm['P' + last_year[-2:] + '_POP'].sum()
  part_pop_imm_fr = round(((pop_imm_fr / pop_fr) * 100), 2)
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Part des immigrées - " + last_year + " (en %)": [part_pop_imm_commune, part_pop_imm_epci, part_pop_imm_dpt, part_pop_imm_reg, part_pop_imm_fr]}
  df = pd.DataFrame(data=d)
  st.write(df)
  ##########################################################################
  st.header('8.Personnes étrangères')
  st.caption("Dernier millésime " + last_year + " - Paru le : 19/10/2023")
  st.caption("Un étranger est une personne qui réside en France et ne possède pas la nationalité française, soit qu'elle possède une autre nationalité (à titre exclusif), soit qu'elle n'en ait aucune (c'est le cas des personnes apatrides). Les personnes de nationalité française possédant une autre nationalité (ou plusieurs) sont considérées en France comme françaises. Un étranger n'est pas forcément immigré, il peut être né en France (les mineurs notamment).")
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
  indice_etr_iris = part_pers_etr_iris("./population/base-ic-evol-struct-pop-" + last_year + ".csv",code_commune, last_year)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(indice_etr_iris)
  ###############
  #CARTE
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
  gdf = gdf.merge(indice_etr_iris, left_on='fields.iris_code', right_on="Code de l'iris")
  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]
  # Créer une nouvelle carte pour la répartition de la population par iris
  # Supprimer les lignes avec NaN pour le calcul de la méthode de Jenks
  gdf = gdf.dropna(subset=["Part des personnes étrangères"])
  # S'assurer que toutes les valeurs sont finies
  gdf = gdf[pd.to_numeric(gdf["Part des personnes étrangères"], errors='coerce').notnull()]
  breaks = jenkspy.jenks_breaks(gdf["Part des personnes étrangères"], 5)
  m4 = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

  # Ajouter la carte choroplèthe
  folium.Choropleth(
    geo_data=gdf.set_index("fields.iris_code"),
    name='choropleth',
    data=indice_etr_iris,
    columns=["Code de l'iris", "Part des personnes étrangères"],
    key_on='feature.id',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    color='#ffffff',
    weight=3,
    opacity=1.0,
    legend_name='Part des personnes étrangères',
    bins=breaks
  ).add_to(m4)

  folium.LayerControl().add_to(m4)

  style_function = lambda x: {'fillColor': '#ffffff',
                          'color':'#000000',
                          'fillOpacity': 0.1,
                          'weight': 0.1}
  highlight_function = lambda x: {'fillColor': '#000000',
                                'color':'#000000',
                                'fillOpacity': 0.50,
                                'weight': 0.1}
  NIL = folium.features.GeoJson(
    gdf,
    style_function=style_function,
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=["Nom de l'iris", "Part des personnes étrangères"],
        aliases=['Iris: ', "Part des personnes étrangères :"],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
    )
  )
  m4.add_child(NIL)
  m4.keep_in_front(NIL)
  st.subheader("Part des personnes étrangères")
  # Afficher la carte dans Streamlit
  folium_st.folium_static(m4)

  #############
  st.subheader("Comparaison")
  #Commune
  df_etr = pd.read_csv("./population/base-ic-evol-struct-pop-" + last_year + ".csv", dtype={"IRIS": str , "COM": str},sep=";")
  df_etr_com = df_etr.loc[df_etr["COM"] == code_commune ]
  pop_etr = df_etr_com['P' + last_year[-2:] + '_POP_ETR'].sum()
  pop = df_etr_com['P' + last_year[-2:] + '_POP'].sum()
  part_pop_etr_commune = round(((pop_etr / pop) * 100), 2)
  #EPCI
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_etr_epci = pd.merge(df_etr, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
  df_etr_epci = df_etr_epci.loc[df_etr_epci["EPCI"] == str(code_epci)]
  pop_etr_epci = df_etr_epci['P' + last_year[-2:] + '_POP_ETR'].sum()
  pop_epci = df_etr_epci['P' + last_year[-2:] + '_POP'].sum()
  part_pop_etr_epci = round(((pop_etr_epci / pop_epci) * 100), 2)
  #Département
  df_dpt = pd.read_csv("./population/base-ic-evol-struct-pop-" + last_year + ".csv", dtype={"COM": str, "DEP": str}, sep = ';')
  df_etr_dpt = df_dpt.loc[df_dpt["DEP"] == str(code_departement)]
  pop_etr_dpt = df_etr_dpt['P' + last_year[-2:] + '_POP_ETR'].sum()
  pop_dpt = df_etr_dpt['P' + last_year[-2:] + '_POP'].sum()
  part_pop_etr_dpt = round(((pop_etr_dpt / pop_dpt) * 100), 2)
  #Région
  df_reg = pd.read_csv("./population/base-ic-evol-struct-pop-" + last_year + ".csv", dtype={"COM": str, "DEP": str, "REG": str}, sep = ';')
  df_etr_reg = df_reg.loc[df_reg["REG"] == str(code_region)]
  pop_etr_reg = df_etr_reg['P' + last_year[-2:] + '_POP_ETR'].sum()
  pop_reg = df_etr_reg['P' + last_year[-2:] + '_POP'].sum()
  part_pop_etr_reg = round(((pop_etr_reg / pop_reg) * 100), 2)
  #France
  pop_etr_fr = df_etr['P' + last_year[-2:] + '_POP_ETR'].sum()
  pop_fr = df_etr['P' + last_year[-2:] + '_POP'].sum()
  part_pop_etr_fr = round(((pop_etr_fr / pop_fr) * 100), 2)
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Part des étrangers - " + last_year + " (en %)": [part_pop_etr_commune, part_pop_etr_epci, part_pop_etr_dpt, part_pop_etr_reg, part_pop_etr_fr]}
  df = pd.DataFrame(data=d)
  st.write(df)
  ###########
  st.caption("Zoom sur les QPV")
  #Année
  select_annee_pop_etr = st.select_slider(
       "Sélection de l'année",
       options=['2017', '2018', '2019', '2020', '2021', '2022'],
       value=('2022'))
  st.write('Mon année :', select_annee_pop_etr)

  def part_etrangers_qpv(fichier, nom_ville, annee) :
    fp_qpv = "./qpv.geojson"
    map_qpv_df = gpd.read_file(fp_qpv)
    year = annee[-2:]
    df = pd.read_csv(fichier, dtype={"CODGEO": str}, sep=";")
    map_qpv_df_code_insee = map_qpv_df.merge(df, left_on='code_qp', right_on='CODGEO')
    map_qpv_df_code_insee_extract = map_qpv_df_code_insee[['nom_qp', 'code_qp', 'commune_qp','code_insee', "TX_TOT_ET" ]]
    map_qpv_df_code_insee_extract
    df_qpv = map_qpv_df_code_insee_extract.loc[map_qpv_df_code_insee_extract["commune_qp"].str.contains(nom_ville + "(,|$)")]
    df_qpv = df_qpv.reset_index(drop=True)
    df_qpv = df_qpv[['code_qp', 'nom_qp','commune_qp','TX_TOT_ET']]
    df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", "TX_TOT_ET" : "Part des étrangers " + select_annee_pop_etr})
    return df_qpv
  part_etrangers_qpv = part_etrangers_qpv('./population/demographie_qpv/DEMO_' + select_annee_pop_etr + '.csv', nom_commune, select_annee_pop_etr)
  st.table(part_etrangers_qpv)
  ############################################################################


