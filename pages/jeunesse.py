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
       options=['2014', '2015', '2016', '2017', '2018'],
       value=('2018'))
  st.sidebar.write('Mon année :', select_annee)

  #############################################################################

  st.title("👦👧 JEUNESSE")
  st.header('1.Indice de jeunesse')
  st.caption("L'indice de jeunesse est le rapport de la population des moins de 20 ans sur celle des 65 ans et plus. Un indice autour de 100 indique que les 65 ans et plus et les moins de 20 ans sont présents dans à peu près les mêmes proportions sur le territoire; plus l’indice est faible plus le rapport est favorable aux personnes âgées, plus il est élevé plus il est favorable à la jeunesse.")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    st.subheader("Iris")
    def indice_jeunesse_iris(fichier, code, annee) :
      df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep=";", header=0)
      df_indice = df.loc[df['COM'] == code]
      year = annee[-2:]
      df_indice = df_indice[['COM','IRIS', 'P'+ year + '_POP65P','P' + year +'_POP0019' ]]
      df_indice = df_indice.replace(',','.', regex=True)
      df_indice['P'+ year + '_POP65P'] = df_indice['P'+ year + '_POP65P'].astype(float).to_numpy()
      df_indice['P' + year +'_POP0019'] = df_indice['P' + year +'_POP0019'].astype(float).to_numpy()
      df_indice['indice'] = np.where(df_indice['P' + year +'_POP65P'] < 1,df_indice['P' + year +'_POP65P'], (df_indice['P'+ year + '_POP0019'] / df_indice['P' + year +'_POP65P']*100))
      df_indice['indice'] = df_indice['indice'].astype(float).to_numpy()
      communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
      df_indice_com = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_indice[['IRIS','P' + year +'_POP0019', 'P' + year + '_POP65P','indice']], left_on='CODE_IRIS', right_on="IRIS")
      df_indice_com = df_indice_com[['CODE_IRIS','LIB_IRIS','P' + year +'_POP0019', 'P' + year + '_POP65P','indice']]
      df_indice_com['indice'] = df_indice_com['indice'].apply(np.int64)
      df_indice_com['P' + year +'_POP0019'] = df_indice_com['P' + year +'_POP0019'].apply(np.int64)
      df_indice_com['P' + year +'_POP65P'] = df_indice_com['P' + year +'_POP65P'].apply(np.int64)
      df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_POP0019':"Moins de 20 ans (" + select_annee + ")" ,'P' + year + '_POP65P':"Plus de 65 ans (" + select_annee + ")",'indice':"Indice de jeunesse (" + select_annee + ")" })
      return df_indice_com
    ind_jeunesse_iris =indice_jeunesse_iris("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_commune, select_annee)
    with st.expander("Visualiser le tableau des iris"):
      st.table(ind_jeunesse_iris)

  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(ind_jeunesse_iris)

  st.download_button(
    label="💾 Télécharger les données",
    data=csv,
    file_name='ind_jeunesse_iris.csv',
    mime='text/csv',
  )

  #################################
  st.header("Indice de jeunesse")
  st.subheader("Zoom QPV")

  #Année
  select_annee_0024 = st.select_slider(
       "Sélection de l'année",
       options=['2017', '2018', '2019', '2020', '2021', '2022'],
       value=('2022'))
  st.write('Mon année :', select_annee_0024)

  def indice_jeunesse_qpv(fichier, nom_ville, annee) :
    fp_qpv = "./qpv.geojson"
    map_qpv_df = gpd.read_file(fp_qpv)
    year = annee[-2:]
    df = pd.read_csv(fichier, dtype={"CODGEO": str}, sep=";")
    map_qpv_df_code_insee = map_qpv_df.merge(df, left_on='code_qp', right_on='CODGEO')
    map_qpv_df_code_insee_extract = map_qpv_df_code_insee[['nom_qp', 'code_qp', 'commune_qp','code_insee', 'IND_JEUNE' ]]
    map_qpv_df_code_insee_extract
    df_qpv = map_qpv_df_code_insee_extract.loc[map_qpv_df_code_insee_extract["commune_qp"].str.contains(nom_ville + "(,|$)")]
    df_qpv = df_qpv.reset_index(drop=True)
    df_qpv = df_qpv[['code_qp', 'nom_qp','commune_qp', 'IND_JEUNE']]
    df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", 'IND_JEUNE' : "Indice de jeunesse " + select_annee_0024})
    return df_qpv

  ind_jeunesse_qpv = indice_jeunesse_qpv('./population/demographie_qpv/DEMO_' + select_annee_0024 + '.csv', nom_commune, select_annee_0024)
  st.table(ind_jeunesse_qpv)

  st.caption("Attention, calcul de l'indice jeunesse pour les QPV : population de 0 à 19 ans / population de 60 ans et plus")
  ########################

  st.subheader('a.Comparaison sur une année')
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    #comparaison des territoires
    # Commune
    def IV_commune(fichier, code_ville, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_ville = df.loc[df["COM"]==code_ville,]
        nom_ville = df_ville.loc[df["COM"]==code_ville, 'COM']
        Plus_de_65 = df_ville.loc[:, 'P'+ year + '_POP65P'].astype(float).sum(axis = 0, skipna = True)
        Moins_de_20 = df_ville.loc[:, 'P'+ year + '_POP0019'].astype(float).sum(axis = 0, skipna = True)
        IV = round((Moins_de_20 / Plus_de_65 )*100,2)
        df_iv = pd.DataFrame(data=IV, columns = ['Indice de jeunesse en ' + annee], index = [nom_commune])
        return df_iv
    valeur_comiv = IV_commune("./population/base-ic-evol-struct-pop-" + select_annee + ".csv", code_commune, select_annee)

    # EPCI
    def IV_epci(fichier, epci, annee):
        epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "TYP_IRIS": str, "MODIF_IRIS": str,"COM": str, "LAB_IRIS": str, "DEP": str, "UU2010": str, "GRD_QUART": str}, sep = ';')
        year = annee[-2:]
        df_epci_com = pd.merge(df[['COM', 'P' + year + '_POP0019', 'P' + year + '_POP65P']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
        df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM','P'+ year +'_POP0019' , 'P'+ year + '_POP65P']]
        Plus_de_65 = df_epci.loc[:, 'P'+ year + '_POP65P']
        Moins_de_20 = df_epci.loc[:, 'P'+ year + '_POP0019']
        df_P65 = pd.DataFrame(data=Plus_de_65)
        df_M20 = pd.DataFrame(data=Moins_de_20)
        Somme_P65 = df_P65.sum(axis = 0, skipna = True)
        Somme_M20 = df_M20.sum(axis = 0, skipna = True)
        P65= Somme_P65.values[0]
        M20=Somme_M20.values[0]
        IV = round((M20/P65)*100,2)
        df_ind_epci = pd.DataFrame(data=IV, columns = ["Indice de jeunesse en " + annee], index = [nom_epci])
        return df_ind_epci
    valeurs_ind_epci = IV_epci("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_epci,select_annee)

    # Département
    def IV_departement_M2017(fichier, departement, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_departement = df.loc[df["DEP"]==departement, 'P'+ year +'_POP0019' : 'P'+ year + '_POP65P']
        Plus_de_65 = df_departement.loc[:, 'P'+ year + '_POP65P']
        Moins_de_20 = df_departement.loc[:, 'P'+ year + '_POP0019']
        df_P65 = pd.DataFrame(data=Plus_de_65)
        df_M20 = pd.DataFrame(data=Moins_de_20)
        Somme_P65 = df_P65.sum(axis = 0, skipna = True)
        Somme_M20 = df_M20.sum(axis = 0, skipna = True)
        P65= Somme_P65.values[0]
        M20=Somme_M20.values[0]
        IV = round((M20/P65)*100,2)
        df_dep = pd.DataFrame(data=IV, columns = ['Indice de jeunesse en ' + annee], index = [nom_departement])
        return df_dep

    def IV_departement_P2017(fichier, departement, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_dpt = pd.merge(df[['COM', 'P' + year +'_POP0019', 'P' + year + '_POP65P']], communes_select[['COM','DEP']],  on='COM', how='left')
        df_departement = df_dpt.loc[df_dpt["DEP"]==departement, ['DEP', 'COM','P'+ year +'_POP0019' , 'P'+ year + '_POP65P']]
        Plus_de_65 = df_departement.loc[:, 'P'+ year + '_POP65P']
        Moins_de_20 = df_departement.loc[:, 'P'+ year + '_POP0019']
        df_P65 = pd.DataFrame(data=Plus_de_65)
        df_M20 = pd.DataFrame(data=Moins_de_20)
        Somme_P65 = df_P65.sum(axis = 0, skipna = True)
        Somme_M20 = df_M20.sum(axis = 0, skipna = True)
        P65= Somme_P65.values[0]
        M20=Somme_M20.values[0]
        IV = round((M20/P65)*100,2)
        df_dep = pd.DataFrame(data=IV, columns = ['Indice de jeunesse en ' + annee], index = [nom_departement])
        return df_dep

    if int(select_annee) < 2017:
        valeurs_dep_iv = IV_departement_M2017("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_departement,select_annee)
    else :
        valeurs_dep_iv = IV_departement_P2017("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_departement,select_annee)


    # Région
    #si année de 2014 à 2016 (inclus)
    def IV_region_M2017(fichier, region, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_regions = df.loc[df["REG"]==region, 'P'+ year +'_POP0019' : 'P'+ year + '_POP65P']
        Plus_de_65 = df_regions.loc[:, 'P'+ year + '_POP65P']
        Moins_de_20 = df_regions.loc[:, 'P'+ year + '_POP0019']
        df_P65 = pd.DataFrame(data=Plus_de_65)
        df_M20 = pd.DataFrame(data=Moins_de_20)
        Somme_P65 = df_P65.sum(axis = 0, skipna = True)
        Somme_M20 = df_M20.sum(axis = 0, skipna = True)
        P65= Somme_P65.values[0]
        M20=Somme_M20.values[0]
        IV = round((M20/P65)*100,2)
        df_reg = pd.DataFrame(data=IV, columns = ['Indice de jeunesse en ' + annee], index = [nom_region])
        return df_reg

    #si année de 2017 à ... (inclus)
    def IV_region_P2017(fichier, region, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_regions = pd.merge(df[['COM', 'P' + year +'_POP0019', 'P' + year + '_POP65P']], communes_select[['COM','REG']],  on='COM', how='left')
        df_region = df_regions.loc[df_regions["REG"]==region, ['REG', 'COM','P'+ year +'_POP0019' , 'P'+ year + '_POP65P']]
        Plus_de_65 = df_region.loc[:, 'P'+ year + '_POP65P']
        Moins_de_20 = df_region.loc[:, 'P'+ year + '_POP0019']
        df_P65 = pd.DataFrame(data=Plus_de_65)
        df_M20 = pd.DataFrame(data=Moins_de_20)
        Somme_P65 = df_P65.sum(axis = 0, skipna = True)
        Somme_M20 = df_M20.sum(axis = 0, skipna = True)
        P65= Somme_P65.values[0]
        M20=Somme_M20.values[0]
        IV = round((M20/P65)*100,2)
        df_reg = pd.DataFrame(data=IV, columns = ['Indice de jeunesse en ' + annee], index = [nom_region])
        return df_reg

    if int(select_annee) < 2017:
        valeurs_reg_iv = IV_region_M2017("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",str(round(code_region)),select_annee)
    else :
        valeurs_reg_iv = IV_region_P2017("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",str(round(code_region)),select_annee)

    # France
    def IV_France(fichier, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        Plus_de_65 = df.loc[:, 'P'+ year + '_POP65P']
        Moins_de_20 = df.loc[:, 'P'+ year + '_POP0019']
        df_P65 = pd.DataFrame(data=Plus_de_65)
        df_M20 = pd.DataFrame(data=Moins_de_20)
        Somme_P65 = df_P65.sum(axis = 0, skipna = True)
        Somme_M20 = df_M20.sum(axis = 0, skipna = True)
        P65= Somme_P65.values[0]
        M20=Somme_M20.values[0]
        IV = round((M20/P65)*100, 2)
        df_fr = pd.DataFrame(data=IV, columns = ['Indice de jeunesse en ' + annee], index = ["France"])
        return df_fr

    valeur_iv_fr = IV_France("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",select_annee)

    # Comparaison
    def IV_global(annee):
        df = pd.concat([valeur_comiv,valeurs_ind_epci, valeurs_dep_iv, valeurs_reg_iv, valeur_iv_fr])
        year = annee
        return df

    pop_global = IV_global(select_annee)
    st.table(pop_global)

    @st.cache
    def convert_df(df):
      # IMPORTANT: Cache the conversion to prevent computation on every rerun
      return df.to_csv().encode('utf-8')

    csv = convert_df(pop_global)

    st.download_button(
      label="💾 Télécharger les données",
      data=csv,
      file_name='ind_jeunesse_comparaison.csv',
      mime='text/csv',
    )


  #################################
  st.header("Taux de 00-24 ans")
  st.subheader("Zoom QPV")

  #Année
  select_annee_0024 = st.select_slider(
       "Sélection de l'année",
       options=['2017', '2018', '2019', '2020', '2021', '2022'],
       value=('2022'))
  st.write('Mon année :', select_annee_0024)

  def tx_0024_qpv(fichier, nom_ville, annee) :
    fp_qpv = "./qpv.geojson"
    map_qpv_df = gpd.read_file(fp_qpv)
    year = annee[-2:]
    df = pd.read_csv(fichier, dtype={"CODGEO": str}, sep=";")
    map_qpv_df_code_insee = map_qpv_df.merge(df, left_on='code_qp', right_on='CODGEO')
    map_qpv_df_code_insee_extract = map_qpv_df_code_insee[['nom_qp', 'code_qp', 'commune_qp','code_insee', 'TX_TOT_0A24' ]]
    map_qpv_df_code_insee_extract
    df_qpv = map_qpv_df_code_insee_extract.loc[map_qpv_df_code_insee_extract["commune_qp"].str.contains(nom_ville + "(,|$)")]
    df_qpv = df_qpv.reset_index(drop=True)
    df_qpv = df_qpv[['code_qp', 'nom_qp','commune_qp', 'TX_TOT_0A24']]
    df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", 'TX_TOT_0A24' : "Taux des 00/24 ans " + select_annee_0024})
    return df_qpv

  tx_0024_qpv = tx_0024_qpv('./population/demographie_qpv/DEMO_' + select_annee_0024 + '.csv', nom_commune, select_annee_0024)
  st.table(tx_0024_qpv)

  ##################################
  st.subheader('2. Les NEET')
  st.caption("Un NEET (neither in employment nor in education or training) est une personne entre 16 et 25 ans qui n’est ni en emploi, ni en études, ni en formation (formelle ou non formelle).")

  #Commune
  def neet_commune(fichier, nom_ville, annee) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_ville = df.loc[df["libgeo"] == nom_ville]
    df_ville = df_ville.loc[df_ville["an"] == annee]
    return df_ville
  neet_ville = neet_commune("./jeunesse/neet/neet_communes_" + select_annee + ".csv",nom_commune, select_annee)

  #EPCI
  def neet_epci(fichier, epci, annee) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_epci = df.loc[df["codgeo"] == epci]
    df_epci = df_epci.loc[df_epci["an"] == annee]
    return df_epci
  neet_epci = neet_epci("./jeunesse/neet/neet_epci_" + select_annee + ".csv",code_epci, select_annee)

  #Département
  def neet_departement(fichier, departement, annee) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_departement = df.loc[df["codgeo"] == departement]
    df_departement = df_departement.loc[df_departement["an"] == annee]
    return df_departement
  neet_dpt = neet_departement("./jeunesse/neet/neet_dpt_" + select_annee + ".csv",code_departement, select_annee)

  #Région
  def neet_region(fichier, region, annee) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_region = df.loc[df["codgeo"] == region]
    df_region = df_region.loc[df_region["an"] == annee]
    return df_region
  neet_reg = neet_region("./jeunesse/neet/neet_region_" + select_annee + ".csv",str(round(code_region)), select_annee)

  #France
  data = {'codgeo':['1'],
          'libgeo':['France'],
          'an':['2018'],
          'part_non_inseres':['16,30']
          }
  neet_france = pd.DataFrame(data)

  #Global
  result = pd.concat([neet_ville,neet_epci, neet_dpt, neet_reg, neet_france])
  st.write(result)

  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(result)

  st.download_button(
    label="💾 Télécharger les données",
    data=csv,
    file_name='neet_comparaison.csv',
    mime='text/csv',
  )

  ###########
  st.header('2.Part des licenciés sportifs 0/14 ans')

  #Commune
  def tx_licence_sport_0_14_commune(fichier, nom_ville) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_ville = df.loc[df["libgeo"] == nom_ville]
    return df_ville
  tx_lic_sport_0_14_ville = tx_licence_sport_0_14_commune("./sante/sport/licsport_communes_2018.csv",nom_commune)

  #EPCI
  def tx_licence_sport_0_14_epci(fichier, epci) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_epci = df.loc[df["codgeo"] == epci]
    return df_epci
  tx_lic_sport_0_14_epci = tx_licence_sport_0_14_epci("./sante/sport/licsport_epci_2018.csv",code_epci)

  #Département
  def tx_licence_sport_0_14_departement(fichier, departement) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_departement = df.loc[df["codgeo"] == departement]
    df_departement = df_departement.loc[df_departement["an"] == "2018"]
    return df_departement
  tx_lic_sport_0_14_dpt = tx_licence_sport_0_14_departement("./sante/sport/licsport_departement_2018.csv",code_departement)

  #Région
  def tx_licence_sport_0_14_region(fichier, region) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_region = df.loc[df["codgeo"] == region]
    df_region = df_region.loc[df_region["an"] == "2018"]
    return df_region
  tx_lic_sport_0_14_reg = tx_licence_sport_0_14_region("./sante/sport/licsport_region_2018.csv",str(round(code_region)))

  #France
  data = {'codgeo':['1'],
          'libgeo':['France'],
          'an':['2018'],
          'p_licsport014':['47,6']
          }
  tx_lic_sport_0_14_france = pd.DataFrame(data)

  #Global
  result = pd.concat([tx_lic_sport_0_14_ville,tx_lic_sport_0_14_epci, tx_lic_sport_0_14_dpt, tx_lic_sport_0_14_reg, tx_lic_sport_0_14_france])
  st.write(result)

  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(result)

  st.download_button(
    label="💾 Télécharger les données",
    data=csv,
    file_name='tx_licencie_sport_014_comparaison.csv',
    mime='text/csv',
  )


  ###############################
  st.header('3.Part des filles parmi les licenciés sportifs de 0-14 ans')

  #Commune
  def tx_licence_sport_0_14_filles_commune(fichier, nom_ville) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_ville = df.loc[df["libgeo"] == nom_ville]
    return df_ville
  tx_lic_sport_0_14_filles_ville = tx_licence_sport_0_14_filles_commune("./sante/sport/sport_014_filles/licsport_014_filles_commune.csv",nom_commune)

  #EPCI
  def tx_licence_sport_0_14_filles_epci(fichier, epci) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_epci = df.loc[df["codgeo"] == epci]
    return df_epci
  tx_lic_sport_0_14_filles_epci = tx_licence_sport_0_14_filles_epci("./sante/sport/sport_014_filles/licsport_014_filles_epci.csv",code_epci)

  #Département
  def tx_licence_sport_0_14_filles_departement(fichier, departement) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_departement = df.loc[df["codgeo"] == departement]
    df_departement = df_departement.loc[df_departement["an"] == "2018"]
    return df_departement
  tx_lic_sport_0_14_filles_dpt = tx_licence_sport_0_14_filles_departement("./sante/sport/sport_014_filles/licsport_014_filles_departement.csv",code_departement)

  #Région
  def tx_licence_sport_0_14_filles_region(fichier, region) :
    df = pd.read_csv(fichier, dtype={"codgeo": str, "an": str},sep=";")
    df_region = df.loc[df["codgeo"] == region]
    df_region = df_region.loc[df_region["an"] == "2018"]
    return df_region
  tx_lic_sport_0_14_filles_reg = tx_licence_sport_0_14_filles_region("./sante/sport/sport_014_filles/licsport_014_filles_region.csv",str(round(code_region)))

  #France
  data = {'codgeo':['1'],
          'libgeo':['France'],
          'an':['2018'],
          'p_licsport014_f':['39,8']
          }
  tx_lic_sport_0_14_filles_france = pd.DataFrame(data)

  #Global
  result = pd.concat([tx_lic_sport_0_14_filles_ville,tx_lic_sport_0_14_filles_epci, tx_lic_sport_0_14_filles_dpt, tx_lic_sport_0_14_filles_reg, tx_lic_sport_0_14_filles_france])
  st.write(result)

  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(result)

  st.download_button(
    label="💾 Télécharger les données",
    data=csv,
    file_name='tx_licencie_sport_014_filles_comparaison.csv',
    mime='text/csv',
  )

