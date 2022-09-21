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
       options=['2014', '2015', '2016', '2017', '2018', '2019'],
       value=('2019'))
  st.sidebar.write('Mon année :', select_annee)

  #############################################################################
  st.title("RESSOURCES")
  st.header('1.Le niveau de vie médian')
  st.subheader("Définition")
  st.caption("La médiane du revenu disponible correspond au niveau au-dessous duquel se situent 50 % de ces revenus. C'est de manière équivalente le niveau au-dessus duquel se situent 50 % des revenus.")
  st.caption("Le revenu disponible est le revenu à la disposition du ménage pour consommer et épargner. Il comprend les revenus d'activité (nets des cotisations sociales), indemnités de chômage, retraites et pensions, revenus fonciers, les revenus financiers et les prestations sociales reçues (prestations familiales, minima sociaux et prestations logements). Au total de ces ressources, on déduit les impôts directs (impôt sur le revenu, taxe d'habitation) et les prélèvements sociaux (CSG, CRDS).")
  st.caption("Le revenu disponible par unité de consommation (UC), également appelé *niveau de vie*, est le revenu disponible par *équivalent adulte*. Il est calculé en rapportant le revenu disponible du ménage au nombre d'unités de consommation qui le composent. Toutes les personnes rattachées au même ménage fiscal ont le même revenu disponible par UC (ou niveau de vie).")
  st.subheader("Pourquoi suivre cet indicateur ?")
  st.header("Comparaison des iris de la commune")

  @st.cache()
  def niveau_vie_median_iris(fichier, nom_ville, annee) :
      df = pd.read_csv(fichier, dtype={"IRIS": str , "COM": str},sep=";")
      year = annee[-2:]
      df_ville = df.loc[df["LIBCOM"]==nom_ville]
      df_ville = df_ville.replace(',','.', regex=True)
      df_ville = df_ville[['IRIS','LIBIRIS','DISP_MED'+ year]]
      if year == "14":
        df_ville['DISP_MED' + year] = df_ville['DISP_MED' + year].str.replace(',','.').astype(float)
      df_ville['DISP_MED' + year] = df_ville['DISP_MED' + year].astype(int)
      df_ville.reset_index(inplace=True, drop=True)
      df_ville = df_ville.rename(columns={'IRIS': "Code de l'iris",'LIBIRIS': "Nom de l'iris", 'DISP_MED'+ year:"Niveau de vie " + select_annee + " en €" })

      return df_ville
  nvm_iris = niveau_vie_median_iris("./revenu/revenu_iris/BASE_TD_FILO_DISP_IRIS_" + select_annee + ".csv",nom_commune, select_annee)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(nvm_iris)

  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(nvm_iris)

  st.download_button(
    label="💾 Télécharger les données",
    data=csv,
    file_name='niveau_de_vie_iris.csv',
    mime='text/csv',
  )
############################
  st.caption("Zoom sur les QPV")
  # Preparation carto QPV
  def niveau_vie_median_qpv(fichier, nom_ville, annee) :
    fp_qpv = "./qpv.geojson"
    map_qpv_df = gpd.read_file(fp_qpv)
    year = annee[-2:]
    df = pd.read_csv(fichier, dtype={"CODGEO": str}, sep=";")
    map_qpv_df_code_insee = map_qpv_df.merge(df, left_on='code_qp', right_on='CODGEO')
    map_qpv_df_code_insee_extract = map_qpv_df_code_insee[['nom_qp', 'code_qp', 'commune_qp','code_insee', 'DISP_MED_A' + year[-2:] ]]
    map_qpv_df_code_insee_extract
    df_qpv = map_qpv_df_code_insee_extract.loc[map_qpv_df_code_insee_extract["commune_qp"].str.contains(nom_ville + "(,|$)")]
    df_qpv = df_qpv.reset_index(drop=True)
    df_qpv = df_qpv[['code_qp', 'nom_qp','commune_qp','DISP_MED_A' + year]]
    df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", "DISP_MED_A" + year : "Niveau de vie " + select_annee})
    return df_qpv
  revenu_disp_qpv = niveau_vie_median_qpv('./revenu/revenu_qpv/data_filo' + select_annee[-2:] + '_qp_revdis.csv', nom_commune, select_annee)
  st.table(revenu_disp_qpv)

  # texte
  def part_quartier_pauvre(indice, total_indice):
    if ((indice/total_indice)*100) > 90:
      st.caption("Le QPV de " + revenu_disp_qpv["Nom du quartier"].iloc[i] + " se situe en " + str(indice) + "eme position sur " + str(total_indice) + " QPV, soit dans les 10% des quartiers QPV les plus pauvres")
    elif ((indice/total_indice)*100) > 75 and ((indice/total_indice)*100) <= 90:
      st.caption("Le QPV de " + revenu_disp_qpv["Nom du quartier"].iloc[i] + " se situe en " + str(indice) + "eme position sur " + str(total_indice) + " QPV, soit dans les 25% des quartiers QPV les plus pauvres")
    elif ((indice/total_indice)*100) > 50 and ((indice/total_indice)*100) <= 75:
      st.caption("Le QPV de " + revenu_disp_qpv["Nom du quartier"].iloc[i] + " se situe en " + str(indice) + "eme position sur " + str(total_indice) + " QPV, soit dans les 50% des quartiers QPV les plus pauvres")
    elif ((indice/total_indice)*100) > 25 and ((indice/total_indice)*100) <= 50:
      st.caption("Le QPV de " + revenu_disp_qpv["Nom du quartier"].iloc[i] + " se situe en " + str(indice) + "eme position sur " + str(total_indice) + " QPV, soit dans les 50% des quartiers QPV les plus riches")
    elif ((indice/total_indice)*100) > 10 and ((indice/total_indice)*100) <= 25:
      st.caption("Le QPV de " + revenu_disp_qpv["Nom du quartier"].iloc[i] + " se situe en " + str(indice) + "eme position sur " + str(total_indice) + " QPV, soit dans les 25% des quartiers QPV les plus riches")
    elif ((indice/total_indice)*100) > 0 and ((indice/total_indice)*100) <= 10 :
      st.caption("Le QPV de " + revenu_disp_qpv["Nom du quartier"].iloc[i] + " se situe en " + str(indice) + "eme position sur " + str(total_indice) + " QPV, soit dans les 10% des quartiers QPV les plus riches")

  #Position d'un QPV
  df_qpv_lenght = len(revenu_disp_qpv.index)
  df = pd.read_csv('./revenu/revenu_qpv/data_filo' + select_annee[-2:] + '_qp_revdis.csv', dtype={"CODGEO": str},sep=";")
  year = select_annee[-2:]
  df_qpv = df[['CODGEO','DISP_MED_A' + year]]
  df_qpv = df_qpv.sort_values(by=['DISP_MED_A' + year], ascending=False)
  df_qpv.reset_index(inplace=True, drop=True)
  i = 0
  while i < df_qpv_lenght:
    indice = df_qpv[df_qpv['CODGEO']== revenu_disp_qpv["Code du quartier"].iloc[i]].index.values.item()+1
    total_indice = len(df_qpv['DISP_MED_A' + year])
    part_quartier_pauvre(indice, total_indice)
    i += 1

  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(revenu_disp_qpv)

  st.download_button(
    label="💾 Télécharger les données",
    data=csv,
    file_name='niveau_de_vie_qpv.csv',
    mime='text/csv',
  )
##################################
  st.subheader('Comparaison entre territoires la dernière année')
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
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

    #Commune
    def niveau_vie_median_commune(fichier, nom_ville, annee) :
        df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
        year = annee[-2:]
        df_ville = df.loc[df["LIBGEO"]== nom_ville]
        df_ville = df_ville.replace(',','.', regex=True)
        ville = df.loc[df["LIBGEO"]== nom_ville]
        nvm = ville[[ 'LIBGEO' ,'Q2'+ year]]
        return nvm
    nvm_ville = niveau_vie_median_commune("./revenu/revenu_commune/FILO" + select_annee + "_DISP_COM.csv",nom_commune, select_annee)
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
    test_tab = pd.concat([nvm_ville, nvm_epci, nvm_departement, nvm_region, nvm_france])
    test_tab = test_tab.reset_index(drop=True)
    test_tab = test_tab.rename(columns={'LIBGEO': "Territoire",'Q2' + select_annee[-2:] : "Niveau de vie " + select_annee})
    st.write(test_tab)

    @st.cache
    def convert_df(df):
      # IMPORTANT: Cache the conversion to prevent computation on every rerun
      return df.to_csv().encode('utf-8')

    csv = convert_df(test_tab)

    st.download_button(
      label="💾 Télécharger les données",
      data=csv,
      file_name='niveau_de_vie_comparaison.csv',
      mime='text/csv',
    )
##################################
  st.subheader("Évolution sur les 6 dernières années disponibles")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    #France
    #2014
    df_2014 = pd.read_csv("./revenu/revenu_france/FILO2014_DISP_METROPOLE.csv", dtype={"CODGEO": str},sep=";")
    df_2014 = df_2014.replace(',','.', regex=True)
    nvm_2014 =df_2014.loc[:, 'Q214'].to_numpy().astype(float)
    indice_2014 = nvm_2014[0]

    #2015
    df_2015 = pd.read_csv("./revenu/revenu_france/FILO2015_DISP_METROPOLE.csv", dtype={"CODGEO": str},sep=";")
    df_2015 = df_2015.replace(',','.', regex=True)
    nvm_2015 =df_2015.loc[:, 'Q215'].to_numpy().astype(float)
    indice_2015 = nvm_2015[0]

    #2016
    df_2016 = pd.read_csv("./revenu/revenu_france/FILO2016_DISP_METROPOLE.csv", dtype={"CODGEO": str},sep=";")
    df_2016 = df_2016.replace(',','.', regex=True)
    nvm_2016 =df_2016.loc[:, 'Q216'].to_numpy().astype(float)
    indice_2016 = nvm_2016[0]

    #2017
    df_2017 = pd.read_csv("./revenu/revenu_france/FILO2017_DISP_METROPOLE.csv", dtype={"CODGEO": str},sep=";")
    df_2017 = df_2017.replace(',','.', regex=True)
    nvm_2017 =df_2017.loc[:, 'Q217'].to_numpy().astype(float)
    indice_2017 = nvm_2017[0]

    #2018
    df_2018 = pd.read_csv("./revenu/revenu_france/FILO2018_DISP_METROPOLE.csv", dtype={"CODGEO": str},sep=";")
    df_2018 = df_2018.replace(',','.', regex=True)
    nvm_2018 =df_2018.loc[:, 'Q218'].to_numpy().astype(float)
    indice_2018 = nvm_2018[0]

    #2019
    df_2019 = pd.read_csv("./revenu/revenu_france/FILO2019_DISP_METROPOLE.csv", dtype={"CODGEO": str},sep=";")
    df_2019 = df_2019.replace(',','.', regex=True)
    nvm_2019 =df_2019.loc[:, 'Q219'].to_numpy().astype(float)
    indice_2019 = nvm_2019[0]

    df_france_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018, indice_2019]]),
                       columns=['2014', '2015', '2016', '2017', '2018', '2019'], index=['France'])

    #Région
    #2014
    df_2014 = pd.read_csv("./revenu/revenu_region/FILO2014_DISP_REG.csv", dtype={"CODGEO": str},sep=";")
    df_2014 = df_2014.replace(',','.', regex=True)
    df_2014 = df_2014.loc[df_2014["LIBGEO"]== nom_region]
    nvm_2014 =df_2014.loc[:, 'Q214'].to_numpy().astype(float)
    indice_2014 = nvm_2014[0]

    #2015
    df_2015 = pd.read_csv("./revenu/revenu_region/FILO2015_DISP_REG.csv", dtype={"CODGEO": str},sep=";")
    df_2015 = df_2015.replace(',','.', regex=True)
    df_2015 = df_2015.loc[df_2015["LIBGEO"]== nom_region]
    nvm_2015 =df_2015.loc[:, 'Q215'].to_numpy().astype(float)
    indice_2015 = nvm_2015[0]

    #2016
    df_2016 = pd.read_csv("./revenu/revenu_region/FILO2016_DISP_REG.csv", dtype={"CODGEO": str},sep=";")
    df_2016 = df_2016.replace(',','.', regex=True)
    df_2016 = df_2016.loc[df_2016["LIBGEO"]== nom_region]
    nvm_2016 =df_2016.loc[:, 'Q216'].to_numpy().astype(float)
    indice_2016 = nvm_2016[0]

    #2017
    df_2017 = pd.read_csv("./revenu/revenu_region/FILO2017_DISP_REG.csv", dtype={"CODGEO": str},sep=";")
    df_2017 = df_2017.replace(',','.', regex=True)
    df_2017 = df_2017.loc[df_2017["LIBGEO"]== nom_region]
    nvm_2017 =df_2017.loc[:, 'Q217'].to_numpy().astype(float)
    indice_2017 = nvm_2017[0]

    #2018
    df_2018 = pd.read_csv("./revenu/revenu_region/FILO2018_DISP_REG.csv", dtype={"CODGEO": str},sep=";")
    df_2018 = df_2018.replace(',','.', regex=True)
    df_2018 = df_2018.loc[df_2018["LIBGEO"]== nom_region]
    nvm_2018 =df_2018.loc[:, 'Q218'].to_numpy().astype(float)
    indice_2018 = nvm_2018[0]

    #2019
    df_2019 = pd.read_csv("./revenu/revenu_region/FILO2019_DISP_REG.csv", dtype={"CODGEO": str},sep=";")
    df_2019 = df_2019.replace(',','.', regex=True)
    df_2019 = df_2019.loc[df_2019["LIBGEO"]== nom_region]
    nvm_2019 =df_2019.loc[:, 'Q219'].to_numpy().astype(float)
    indice_2019 = nvm_2019[0]

    df_region_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018, indice_2019]]),
                       columns=['2014', '2015', '2016', '2017', '2018', '2019'], index=[nom_region])

    #Departement
    #2014
    df_2014 = pd.read_csv("./revenu/revenu_dpt/FILO2014_DISP_DEP.csv", dtype={"CODGEO": str},sep=";")
    df_2014 = df_2014.replace(',','.', regex=True)
    df_2014 = df_2014.loc[df_2014["LIBGEO"]== nom_departement]
    nvm_2014 =df_2014.loc[:, 'Q214'].to_numpy().astype(float)
    indice_2014 = nvm_2014[0]

    #2015
    df_2015 = pd.read_csv("./revenu/revenu_dpt/FILO2015_DISP_DEP.csv", dtype={"CODGEO": str},sep=";")
    df_2015 = df_2015.replace(',','.', regex=True)
    df_2015 = df_2015.loc[df_2015["LIBGEO"]== nom_departement]
    nvm_2015 =df_2015.loc[:, 'Q215'].to_numpy().astype(float)
    indice_2015 = nvm_2015[0]

    #2016
    df_2016 = pd.read_csv("./revenu/revenu_dpt/FILO2016_DISP_DEP.csv", dtype={"CODGEO": str},sep=";")
    df_2016 = df_2016.replace(',','.', regex=True)
    df_2016 = df_2016.loc[df_2016["LIBGEO"]== nom_departement]
    nvm_2016 =df_2016.loc[:, 'Q216'].to_numpy().astype(float)
    indice_2016 = nvm_2016[0]

    #2017
    df_2017 = pd.read_csv("./revenu/revenu_dpt/FILO2017_DISP_DEP.csv", dtype={"CODGEO": str},sep=";")
    df_2017 = df_2017.replace(',','.', regex=True)
    df_2017 = df_2017.loc[df_2017["LIBGEO"]== nom_departement]
    nvm_2017 =df_2017.loc[:, 'Q217'].to_numpy().astype(float)
    indice_2017 = nvm_2017[0]

    #2018
    df_2018 = pd.read_csv("./revenu/revenu_dpt/FILO2018_DISP_DEP.csv", dtype={"CODGEO": str},sep=";")
    df_2018 = df_2018.replace(',','.', regex=True)
    df_2018 = df_2018.loc[df_2018["LIBGEO"]== nom_departement]
    nvm_2018 =df_2018.loc[:, 'Q218'].to_numpy().astype(float)
    indice_2018 = nvm_2018[0]

    #2019
    df_2019 = pd.read_csv("./revenu/revenu_dpt/FILO2019_DISP_DEP.csv", dtype={"CODGEO": str},sep=";")
    df_2019 = df_2019.replace(',','.', regex=True)
    df_2019 = df_2019.loc[df_2019["LIBGEO"]== nom_departement]
    nvm_2019 =df_2019.loc[:, 'Q219'].to_numpy().astype(float)
    indice_2019 = nvm_2019[0]

    df_departement_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018, indice_2019]]),
                       columns=['2014', '2015', '2016', '2017', '2018', '2019'], index=[nom_departement])

    # EPCI
    #2014
    df_2014 = pd.read_csv("./revenu/revenu_epci/FILO2014_DISP_EPCI.csv", dtype={"CODGEO": str},sep=";")
    df_2014 = df_2014.replace(',','.', regex=True)
    df_2014 = df_2014.loc[df_2014["CODGEO"]== code_epci]
    if df_2014.empty:
      st.write("L'EPCI n'est pas répertorié pas l'insee pour 2014")
    else:
      nvm_2014 =df_2014.loc[:, 'Q214'].to_numpy().astype(float)
      indice_2014 = nvm_2014[0]

    #2015
    df_2015 = pd.read_csv("./revenu/revenu_epci/FILO2015_DISP_EPCI.csv", dtype={"CODGEO": str},sep=";")
    df_2015 = df_2015.replace(',','.', regex=True)
    df_2015 = df_2015.loc[df_2015["CODGEO"]== code_epci]
    if df_2015.empty:
      st.write("L'EPCI n'est pas répertorié pas l'insee pour 2015")
    else:
      nvm_2015 =df_2015.loc[:, 'Q215'].to_numpy().astype(float)
      indice_2015 = nvm_2015[0]

    #2016
    df_2016 = pd.read_csv("./revenu/revenu_epci/FILO2016_DISP_EPCI.csv", dtype={"CODGEO": str},sep=";")
    df_2016 = df_2016.replace(',','.', regex=True)
    df_2016 = df_2016.loc[df_2016["CODGEO"]== code_epci]
    nvm_2016 =df_2016.loc[:, 'Q216'].to_numpy().astype(float)
    indice_2016 = nvm_2016[0]

    #2017
    df_2017 = pd.read_csv("./revenu/revenu_epci/FILO2017_DISP_EPCI.csv", dtype={"CODGEO": str},sep=";")
    df_2017 = df_2017.replace(',','.', regex=True)
    df_2017 = df_2017.loc[df_2017["CODGEO"]== code_epci]
    nvm_2017 =df_2017.loc[:, 'Q217'].to_numpy().astype(float)
    indice_2017 = nvm_2017[0]

    #2018
    df_2018 = pd.read_csv("./revenu/revenu_epci/FILO2018_DISP_EPCI.csv", dtype={"CODGEO": str},sep=";")
    df_2018 = df_2018.replace(',','.', regex=True)
    df_2018 = df_2018.loc[df_2018["CODGEO"]== code_epci]
    nvm_2018 =df_2018.loc[:, 'Q218'].to_numpy().astype(float)
    indice_2018 = nvm_2018[0]

    #2019
    df_2019 = pd.read_csv("./revenu/revenu_epci/FILO2019_DISP_EPCI.csv", dtype={"CODGEO": str},sep=";")
    df_2019 = df_2019.replace(',','.', regex=True)
    df_2019 = df_2019.loc[df_2019["CODGEO"]== code_epci]
    nvm_2019 =df_2019.loc[:, 'Q219'].to_numpy().astype(float)
    indice_2019 = nvm_2019[0]

    df_epci_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018, indice_2019]]),
                       columns=['2014', '2015', '2016', '2017', '2018', '2019'], index=[nom_epci])

    #commune
    #2014
    df_2014 = pd.read_csv("./revenu/revenu_commune/FILO2014_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
    df_2014 = df_2014.replace(',','.', regex=True)
    df_2014 = df_2014.loc[df_2014["LIBGEO"]== nom_commune]
    nvm_2014 =df_2014.loc[:, 'Q214'].to_numpy().astype(float)
    indice_2014 = nvm_2014[0]

    #2015
    df_2015 = pd.read_csv("./revenu/revenu_commune/FILO2015_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
    df_2015 = df_2015.replace(',','.', regex=True)
    df_2015 = df_2015.loc[df_2015["LIBGEO"]== nom_commune]
    nvm_2015 =df_2015.loc[:, 'Q215'].to_numpy().astype(float)
    indice_2015 = nvm_2015[0]

    #2016
    df_2016 = pd.read_csv("./revenu/revenu_commune/FILO2016_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
    df_2016 = df_2016.replace(',','.', regex=True)
    df_2016 = df_2016.loc[df_2016["LIBGEO"]== nom_commune]
    nvm_2016 =df_2016.loc[:, 'Q216'].to_numpy().astype(float)
    indice_2016 = nvm_2016[0]

    #2017
    df_2017 = pd.read_csv("./revenu/revenu_commune/FILO2017_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
    df_2017 = df_2017.replace(',','.', regex=True)
    df_2017 = df_2017.loc[df_2017["LIBGEO"]== nom_commune]
    nvm_2017 =df_2017.loc[:, 'Q217'].to_numpy().astype(float)
    indice_2017 = nvm_2017[0]

    #2018
    df_2018 = pd.read_csv("./revenu/revenu_commune/FILO2018_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
    df_2018 = df_2018.replace(',','.', regex=True)
    df_2018 = df_2018.loc[df_2018["LIBGEO"]== nom_commune]
    nvm_2018 =df_2018.loc[:, 'Q218'].to_numpy().astype(float)
    indice_2018 = nvm_2018[0]

    #2019
    df_2019 = pd.read_csv("./revenu/revenu_commune/FILO2019_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
    df_2019 = df_2019.replace(',','.', regex=True)
    df_2019 = df_2019.loc[df_2019["LIBGEO"]== nom_commune]
    nvm_2019 =df_2019.loc[:, 'Q219'].to_numpy().astype(float)
    indice_2019 = nvm_2019[0]

    df_ville_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018, indice_2019]]),
                       columns=['2014', '2015', '2016', '2017', '2018', '2019'], index=[nom_commune])

    df_glob = pd.concat([df_france_glob, df_region_glob, df_departement_glob, df_epci_glob, df_ville_glob])

    st.table(df_glob)

    df1_transposed = df_glob.T
    st.line_chart(df1_transposed)
############################################################################
  st.header("2.Taux de pauvreté au seuil de 60% du revenu disponible par UC médian métropolitain")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    def pauvrete_60_iris(fichier, code_ville, annee) :
        df = pd.read_csv(fichier, dtype={"IRIS": str , "COM": str},sep=";")
        year = select_annee[-2:]
        df_ville = df.loc[df["COM"]==code_ville]
        df_ville = df_ville.replace(',','.', regex=True)
        df_ville = df_ville[['IRIS','LIBIRIS','DISP_TP60'+ year]]
        df_ville['DISP_TP60' + year] = df_ville['DISP_TP60' + year].str.replace(',','.').astype(float)
        df_ville.reset_index(inplace=True, drop=True)
        df_ville = df_ville.rename(columns={'IRIS': "Code de l'iris",'LIBIRIS': "Nom de l'iris", 'DISP_TP60'+ year:"Taux de pauvreté " + select_annee + " en %" })
        return df_ville
    taux_pauvrete_iris = pauvrete_60_iris("./revenu/revenu_iris/BASE_TD_FILO_DISP_IRIS_" + select_annee + ".csv",code_commune, select_annee)
    with st.expander("Visualiser le tableau des iris"):
      st.dataframe(taux_pauvrete_iris)
############################
  st.caption("Zoom sur les QPV")
  # Preparation carto QPV
  def niveau_vie_median_qpv(fichier, nom_ville, annee) :
    fp_qpv = "./qpv.geojson"
    map_qpv_df = gpd.read_file(fp_qpv)
    year = annee[-2:]
    df = pd.read_csv(fichier, dtype={"CODGEO": str}, sep=";")
    map_qpv_df_code_insee = map_qpv_df.merge(df, left_on='code_qp', right_on='CODGEO')
    map_qpv_df_code_insee_extract = map_qpv_df_code_insee[['nom_qp', 'code_qp', 'commune_qp','code_insee', 'DISP_TP60_A' + year[-2:] ]]
    map_qpv_df_code_insee_extract
    df_qpv = map_qpv_df_code_insee_extract.loc[map_qpv_df_code_insee_extract["commune_qp"].str.contains(nom_ville + "(,|$)")]
    df_qpv = df_qpv.reset_index(drop=True)
    df_qpv = df_qpv[['code_qp', 'nom_qp','commune_qp','DISP_TP60_A' + year]]
    df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", "DISP_TP60_A" + year : "Taux de pauvreté " + select_annee})
    return df_qpv
  revenu_disp_qpv = niveau_vie_median_qpv('./revenu/revenu_qpv/data_filo' + select_annee[-2:] + '_qp_revdis.csv', nom_commune, select_annee)
  st.table(revenu_disp_qpv)
############################################################################
  st.header("Taux de couverture des assurés sociaux - CMUC")


