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
  st.title("👴👵 PERSONNES ÂGÉES")
  st.header('1.Indice de vieillissement')
  st.caption("L'indice de vieillissement est le rapport de la population des 65 ans et plus sur celle des moins de 20 ans. Un indice autour de 100 indique que les 65 ans et plus et les moins de 20 ans sont présents dans à peu près les mêmes proportions sur le territoire; plus l’indice est faible plus le rapport est favorable aux jeunes, plus il est élevé plus il est favorable aux personnes âgées.")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    st.subheader("Iris")
    def indice_vieux_iris(fichier, code, annee) :
      df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep=";", header=0)
      df_indice = df.loc[df['COM'] == code]
      year = annee[-2:]
      df_indice = df_indice[['COM','IRIS', 'P'+ year + '_POP65P','P' + year +'_POP0019' ]]
      df_indice = df_indice.replace(',','.', regex=True)
      df_indice['P'+ year + '_POP65P'] = df_indice['P'+ year + '_POP65P'].astype(float).to_numpy()
      df_indice['P' + year +'_POP0019'] = df_indice['P' + year +'_POP0019'].astype(float).to_numpy()
      df_indice['indice'] = np.where(df_indice['P' + year +'_POP0019'] < 1,df_indice['P' + year +'_POP0019'], (df_indice['P'+ year + '_POP65P'] / df_indice['P' + year +'_POP0019']*100))
      df_indice['indice'] = df_indice['indice'].astype(float).to_numpy()
      communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
      df_indice_com = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_indice[['IRIS','P' + year +'_POP0019', 'P' + year + '_POP65P','indice']], left_on='CODE_IRIS', right_on="IRIS")
      df_indice_com = df_indice_com[['CODE_IRIS','LIB_IRIS','P' + year +'_POP0019', 'P' + year + '_POP65P','indice']]
      df_indice_com['indice'] = df_indice_com['indice'].apply(np.int64)
      df_indice_com['P' + year +'_POP0019'] = df_indice_com['P' + year +'_POP0019'].apply(np.int64)
      df_indice_com['P' + year +'_POP65P'] = df_indice_com['P' + year +'_POP65P'].apply(np.int64)
      df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_POP0019':"Moins de 20 ans (" + select_annee + ")" ,'P' + year + '_POP65P':"Plus de 65 ans (" + select_annee + ")",'indice':"Indice de vieillissement (" + select_annee + ")" })
      return df_indice_com
    nvm_iris =indice_vieux_iris("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_commune, select_annee)
    with st.expander("Visualiser le tableau des iris"):
      st.table(nvm_iris)

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
        IV = round((Plus_de_65 / Moins_de_20)*100,2)
        df_iv = pd.DataFrame(data=IV, columns = ['Indice de vieillissement en ' + annee], index = [nom_commune])
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
        IV = round((P65 / M20)*100,2)
        df_ind_epci = pd.DataFrame(data=IV, columns = ["Indice de vieillissement en " + annee], index = [nom_epci])
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
        IV = round((P65 / M20)*100,2)
        df_dep = pd.DataFrame(data=IV, columns = ['Indice de vieillissement en ' + annee], index = [nom_departement])
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
        IV = round((P65 / M20)*100,2)
        df_dep = pd.DataFrame(data=IV, columns = ['Indice de vieillissement en ' + annee], index = [nom_departement])
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
        IV = round((P65 / M20)*100,2)
        df_reg = pd.DataFrame(data=IV, columns = ['Indice de vieillissement en ' + annee], index = [nom_region])
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
        IV = round((P65 / M20)*100,2)
        df_reg = pd.DataFrame(data=IV, columns = ['Indice de vieillissement en ' + annee], index = [nom_region])
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
        IV = round((P65 / M20)*100, 2)
        df_fr = pd.DataFrame(data=IV, columns = ['Indice de vieillissement en ' + annee], index = ["France"])
        return df_fr

    valeur_iv_fr = IV_France("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",select_annee)

    # Comparaison
    def IV_global(annee):
        df = pd.concat([valeur_comiv,valeurs_ind_epci, valeurs_dep_iv, valeurs_reg_iv, valeur_iv_fr])
        year = annee
        return df

    pop_global = IV_global(select_annee)
    st.table(pop_global)


  st.subheader('b.Évolution')
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    #FRANCE
    #2014
    valeur_iv_fr_2014 = IV_France("./population/base-ic-evol-struct-pop-2014.csv",'2014')
    indice_2014 = valeur_iv_fr_2014['Indice de vieillissement en 2014'][0]
    #2015
    valeur_iv_fr_2015 = IV_France("./population/base-ic-evol-struct-pop-2015.csv",'2015')
    indice_2015 = valeur_iv_fr_2015['Indice de vieillissement en 2015'][0]
    #2016
    valeur_iv_fr_2016 = IV_France("./population/base-ic-evol-struct-pop-2016.csv",'2016')
    indice_2016 = valeur_iv_fr_2016['Indice de vieillissement en 2016'][0]
    #2017
    valeur_iv_fr_2017 = IV_France("./population/base-ic-evol-struct-pop-2017.csv",'2017')
    indice_2017 = valeur_iv_fr_2017['Indice de vieillissement en 2017'][0]
    #2018
    valeur_iv_fr_2018 = IV_France("./population/base-ic-evol-struct-pop-2018.csv",'2018')
    indice_2018 = valeur_iv_fr_2018['Indice de vieillissement en 2018'][0]
    df_france_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=['France'])

    #RÉGION
    #2014
    valeur_iv_region_2014 = IV_region_M2017("./population/base-ic-evol-struct-pop-2014.csv",str(round(code_region)),'2014')
    indice_2014 = valeur_iv_region_2014['Indice de vieillissement en 2014'][0]
    #2015
    valeur_iv_region_2015 = IV_region_M2017("./population/base-ic-evol-struct-pop-2015.csv",str(round(code_region)),'2015')
    indice_2015 = valeur_iv_region_2015['Indice de vieillissement en 2015'][0]
    #2016
    valeur_iv_region_2016 = IV_region_M2017("./population/base-ic-evol-struct-pop-2016.csv",str(round(code_region)),'2016')
    indice_2016 = valeur_iv_region_2016['Indice de vieillissement en 2016'][0]
    #2017
    valeur_iv_region_2017 = IV_region_P2017("./population/base-ic-evol-struct-pop-2017.csv",str(round(code_region)),'2017')
    indice_2017 = valeur_iv_region_2017['Indice de vieillissement en 2017'][0]
    #2018
    valeur_iv_region_2018 = IV_region_P2017("./population/base-ic-evol-struct-pop-2018.csv",str(round(code_region)),'2018')
    indice_2018 = valeur_iv_region_2018['Indice de vieillissement en 2018'][0]
    df_region_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_region])

    #DÉPARTEMENT
    #2014
    valeur_iv_departement_2014 = IV_departement_M2017("./population/base-ic-evol-struct-pop-2014.csv",code_departement,'2014')
    indice_2014 = valeur_iv_departement_2014['Indice de vieillissement en 2014'][0]
    #2015
    valeur_iv_departement_2015 = IV_departement_M2017("./population/base-ic-evol-struct-pop-2015.csv",code_departement,'2015')
    indice_2015 = valeur_iv_departement_2015['Indice de vieillissement en 2015'][0]
    #2016
    valeur_iv_departement_2016 = IV_departement_M2017("./population/base-ic-evol-struct-pop-2016.csv",code_departement,'2016')
    indice_2016 = valeur_iv_departement_2016['Indice de vieillissement en 2016'][0]
    #2017
    valeur_iv_departement_2017 = IV_departement_P2017("./population/base-ic-evol-struct-pop-2017.csv",code_departement,'2017')
    indice_2017 = valeur_iv_departement_2017['Indice de vieillissement en 2017'][0]
    #2018
    valeur_iv_departement_2018 = IV_departement_P2017("./population/base-ic-evol-struct-pop-2018.csv",code_departement,'2018')
    indice_2018 = valeur_iv_departement_2018['Indice de vieillissement en 2018'][0]
    df_departement_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_departement])

    #EPCI
    #2014
    valeur_iv_epci_2014 = IV_epci("./population/base-ic-evol-struct-pop-2014.csv",code_epci,'2014')
    indice_2014 = valeur_iv_epci_2014['Indice de vieillissement en 2014'][0]
    #2015
    valeur_iv_epci_2015 = IV_epci("./population/base-ic-evol-struct-pop-2015.csv",code_epci,'2015')
    indice_2015 = valeur_iv_epci_2015['Indice de vieillissement en 2015'][0]
    #2016
    valeur_iv_epci_2016 = IV_epci("./population/base-ic-evol-struct-pop-2016.csv",code_epci,'2016')
    indice_2016 = valeur_iv_epci_2016['Indice de vieillissement en 2016'][0]
    #2017
    valeur_iv_epci_2017 = IV_epci("./population/base-ic-evol-struct-pop-2017.csv",code_epci,'2017')
    indice_2017 = valeur_iv_epci_2017['Indice de vieillissement en 2017'][0]
    #2018
    valeur_iv_epci_2018 = IV_epci("./population/base-ic-evol-struct-pop-2018.csv",code_epci,'2018')
    indice_2018 = valeur_iv_epci_2018['Indice de vieillissement en 2018'][0]
    df_epci_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_epci])

    #COMMUNE
    #2014
    valeur_iv_commune_2014 = IV_commune("./population/base-ic-evol-struct-pop-2014.csv",code_commune,'2014')
    indice_2014 = valeur_iv_commune_2014['Indice de vieillissement en 2014'][0]
    #2015
    valeur_iv_commune_2015 = IV_commune("./population/base-ic-evol-struct-pop-2015.csv",code_commune,'2015')
    indice_2015 = valeur_iv_commune_2015['Indice de vieillissement en 2015'][0]
    #2016
    valeur_iv_commune_2016 = IV_commune("./population/base-ic-evol-struct-pop-2016.csv",code_commune,'2016')
    indice_2016 = valeur_iv_commune_2016['Indice de vieillissement en 2016'][0]
    #2017
    valeur_iv_commune_2017 = IV_commune("./population/base-ic-evol-struct-pop-2017.csv",code_commune,'2017')
    indice_2017 = valeur_iv_commune_2017['Indice de vieillissement en 2017'][0]
    #2018
    valeur_iv_commune_2018 = IV_commune("./population/base-ic-evol-struct-pop-2018.csv",code_commune,'2018')
    indice_2018 = valeur_iv_commune_2018['Indice de vieillissement en 2018'][0]
    df_commune_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_commune])

    df_glob_indice_vieux = pd.concat([df_france_glob, df_region_glob, df_departement_glob, df_epci_glob, df_commune_glob])

    st.table(df_glob_indice_vieux)

    df_indice_vieux_transposed = df_glob_indice_vieux.T
    st.line_chart(df_indice_vieux_transposed)


  st.header("2.Part des personnes de 80 ans et plus vivant seules")

  st.subheader("Iris")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    def part80_seules_iris(fichier, code, annee) :
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, encoding= 'unicode_escape', sep=";", header=0)
      df_indice = df.loc[df['COM'] == code]
      year = annee[-2:]
      df_indice = df_indice[['COM','IRIS', 'P'+ year + '_POP80P','P' + year +'_POP80P_PSEUL' ]]
      df_indice = df_indice.replace(',','.', regex=True)
      df_indice['P'+ year + '_POP80P'] = df_indice['P'+ year + '_POP80P'].astype(float).to_numpy()
      df_indice['P' + year +'_POP80P_PSEUL'] = df_indice['P' + year +'_POP80P_PSEUL'].astype(float).to_numpy()
      df_indice['indice'] = np.where(df_indice['P' + year +'_POP80P'] < 1,df_indice['P' + year +'_POP80P'], (df_indice['P'+ year + '_POP80P_PSEUL'] / df_indice['P' + year +'_POP80P']*100))
      df_indice['indice'] = df_indice['indice'].astype(float).to_numpy()
      communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
      df_indice_com = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_indice[['IRIS','P' + year +'_POP80P', 'P' + year + '_POP80P_PSEUL','indice']], left_on='CODE_IRIS', right_on="IRIS")
      df_indice_com = df_indice_com[['CODE_IRIS','LIB_IRIS','P' + year +'_POP80P', 'P' + year + '_POP80P_PSEUL','indice']]
      df_indice_com['indice'] = df_indice_com['indice'].apply(np.int64)
      df_indice_com['P' + year +'_POP80P'] = df_indice_com['P' + year +'_POP80P'].apply(np.int64)
      df_indice_com['P' + year +'_POP80P_PSEUL'] = df_indice_com['P' + year +'_POP80P_PSEUL'].apply(np.int64)
      df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_POP80P':"Plus de 80 ans (" + select_annee + ")" ,'P' + year + '_POP80P_PSEUL':"Plus de 80 ans vivant seules (" + select_annee + ")" ,'indice':"Part des personnes de plus de 80 ans vivant seules (" + select_annee + ")" })
      return df_indice_com
    indice_80_seules_iris =part80_seules_iris("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_commune, select_annee)
    with st.expander("Visualiser le tableau des iris"):
      st.table(indice_80_seules_iris)


  st.subheader("a.Comparaison des territoires sur une année")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    # Commune
    def part80_seules_com(fichier, code_commune, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        df_ville = df.loc[df["COM"]==code_commune,]
        nom_ville = df_ville.loc[df["COM"]==code_commune, 'COM']
        Plus_de_80 = df_ville.loc[:, 'P'+ year + '_POP80P'].astype(float).sum(axis = 0, skipna = True)
        Plus_de_80_seules = df_ville.loc[:, 'P'+ year + '_POP80P_PSEUL'].astype(float).sum(axis = 0, skipna = True)
        part_80_seules = round((Plus_de_80_seules / Plus_de_80)*100,0)
        df_Part_pers_80_seules = pd.DataFrame(data=part_80_seules, columns = ['Part des personnes de plus de 80 ans vivant seules ' + annee], index = [nom_commune])
        return df_Part_pers_80_seules
    indice_80_seules_com = part80_seules_com("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_commune, select_annee)

    # EPCI
    def part80_seules_epci(fichier, epci, annee):
        epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "TYP_IRIS": str, "MODIF_IRIS": str,"COM": str, "LAB_IRIS": str, "DEP": str, "UU2010": str, "GRD_QUART": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        df_epci_com = pd.merge(df[['COM', 'P' + year + '_POP80P', 'P' + year + '_POP80P_PSEUL']], epci_select[['CODGEO','EPCI', 'LIBEPCI']],  left_on='COM', right_on='CODGEO')
        df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM','P'+ year +'_POP80P' , 'P'+ year + '_POP80P_PSEUL']]
        Plus_de_80 = df_epci.loc[:, 'P'+ year + '_POP80P']
        Plus_de_80_seules = df_epci.loc[:, 'P'+ year + '_POP80P_PSEUL']
        df_P80 = pd.DataFrame(data=Plus_de_80)
        df_P80_seules = pd.DataFrame(data=Plus_de_80_seules)
        Somme_P80 = df_P80.sum(axis = 0, skipna = True)
        Somme_P80_seules = df_P80_seules.sum(axis = 0, skipna = True)
        P80= Somme_P80.values[0]
        M80_seules=Somme_P80_seules.values[0]
        part_80_seules = round((M80_seules / P80)*100,0)
        df_Part_pers_80_seules = pd.DataFrame(data=part_80_seules, columns = ['Part des personnes de plus de 80 ans vivant seules ' + annee], index = [nom_epci])
        return df_Part_pers_80_seules
    valeurs_part80_seules_epci = part80_seules_epci("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_epci,select_annee)

    # Département
    def part80_seules_departement_M2017(fichier, departement, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape',sep = ';')
        year = annee[-2:]
        df_departement = df.loc[df["DEP"]==departement, 'P'+ year +'_POP80P' : 'P'+ year + '_POP80P_PSEUL']
        Plus_de_80 = df_departement.loc[:, 'P'+ year + '_POP80P']
        Plus_de_80_seules = df_departement.loc[:, 'P'+ year + '_POP80P_PSEUL']
        df_P80 = pd.DataFrame(data=Plus_de_80)
        df_P80_seules = pd.DataFrame(data=Plus_de_80_seules)
        Somme_P80 = df_P80.sum(axis = 0, skipna = True)
        Somme_P80_seules = df_P80_seules.sum(axis = 0, skipna = True)
        P80 = Somme_P80.values[0]
        P80_seules =Somme_P80_seules.values[0]
        part_80_seules = round((P80_seules / P80)*100,0)
        df_dep = pd.DataFrame(data=part_80_seules, columns = ['Part des personnes de plus de 80 ans vivant seules ' + annee], index = [nom_departement])
        return df_dep

    def part80_seules_departement_P2017(fichier, departement, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, encoding= 'unicode_escape',sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_dpt = pd.merge(df[['COM', 'P' + year +'_POP80P', 'P' + year + '_POP80P_PSEUL']], communes_select[['COM','DEP']],  on='COM', how='left')
        df_departement = df_dpt.loc[df_dpt["DEP"]==departement, ['DEP', 'COM','P'+ year +'_POP80P' , 'P'+ year + '_POP80P_PSEUL']]
        Plus_de_80 = df_departement.loc[:, 'P'+ year + '_POP80P']
        Plus_de_80_seules = df_departement.loc[:, 'P'+ year + '_POP80P_PSEUL']
        df_P80 = pd.DataFrame(data=Plus_de_80)
        df_P80_seules = pd.DataFrame(data=Plus_de_80_seules)
        Somme_P80 = df_P80.sum(axis = 0, skipna = True)
        Somme_P80_seules = df_P80_seules.sum(axis = 0, skipna = True)
        P80= Somme_P80.values[0]
        P80_seules=Somme_P80_seules.values[0]
        part_80_seules = round((P80_seules / P80)*100,0)
        df_dep = pd.DataFrame(data=part_80_seules, columns = ['Part des personnes de plus de 80 ans vivant seules ' + annee], index = [nom_departement])
        return df_dep

    if int(select_annee) < 2017:
        valeurs_dep_iv = part80_seules_departement_M2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_departement,select_annee)
    else :
        valeurs_dep_iv = part80_seules_departement_P2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_departement,select_annee)

    # Région
    #si année de 2014 à 2016 (inclus)
    def IV_region_M2017(fichier, region, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        df_regions = df.loc[df["REG"]==str(region), 'P'+ year +'_POP80P' : 'P'+ year + '_POP80P_PSEUL']
        Plus_de_80 = df_regions.loc[:, 'P'+ year + '_POP80P']
        Plus_de_80_seules = df_regions.loc[:, 'P'+ year + '_POP80P_PSEUL']
        df_P80 = pd.DataFrame(data=Plus_de_80)
        df_P80_seules = pd.DataFrame(data=Plus_de_80_seules)
        Somme_P80 = df_P80.sum(axis = 0, skipna = True)
        Somme_P80_seules = df_P80_seules.sum(axis = 0, skipna = True)
        P80= Somme_P80.values[0]
        P80_seules=Somme_P80_seules.values[0]
        part_80_seules = round((P80_seules / P80)*100,0)
        df_reg = pd.DataFrame(data=part_80_seules, columns = ['Part des personnes de plus de 80 ans vivant seules ' + annee], index = [nom_region])
        return df_reg

    #si année de 2017 à ... (inclus)
    def IV_region_P2017(fichier, region, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, encoding= 'unicode_escape', sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_regions = pd.merge(df[['COM', 'P' + year +'_POP80P', 'P' + year + '_POP80P_PSEUL']], communes_select[['COM','REG']],  on='COM', how='left')
        df_region = df_regions.loc[df_regions["REG"]==str(region), ['REG', 'COM','P'+ year +'_POP80P' , 'P'+ year + '_POP80P_PSEUL']]
        Plus_de_80 = df_region.loc[:, 'P'+ year + '_POP80P']
        Plus_de_80_seules = df_region.loc[:, 'P'+ year + '_POP80P_PSEUL']
        df_P80 = pd.DataFrame(data=Plus_de_80)
        df_P80_seules = pd.DataFrame(data=Plus_de_80_seules)
        Somme_P80 = df_P80.sum(axis = 0, skipna = True)
        Somme_P80_seules = df_P80_seules.sum(axis = 0, skipna = True)
        P80= Somme_P80.values[0]
        M80_seules=Somme_P80_seules.values[0]
        part_80_seules = round((M80_seules / P80)*100,0)
        df_reg = pd.DataFrame(data=part_80_seules, columns = ['Part des personnes de plus de 80 ans vivant seules ' + annee], index = [nom_region])
        return df_reg

    if int(select_annee) < 2017:
        valeurs_reg_iv = IV_region_M2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",str(round(code_region)),select_annee)
    else :
        valeurs_reg_iv = IV_region_P2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",str(round(code_region)),select_annee)

    # France
    def part80_seules_France(fichier, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        Plus_de_80 = df.loc[:, 'P'+ year + '_POP80P']
        Plus_de_80_seules = df.loc[:, 'P'+ year + '_POP80P_PSEUL']
        df_P80 = pd.DataFrame(data=Plus_de_80)
        df_P80_seules = pd.DataFrame(data=Plus_de_80_seules)
        Somme_P80 = df_P80.sum(axis = 0, skipna = True)
        Somme_P80_seules = df_P80_seules.sum(axis = 0, skipna = True)
        P80= Somme_P80.values[0]
        P80_seules=Somme_P80_seules.values[0]
        part_80_seules = round((P80_seules / P80)*100, 0)
        df_fr = pd.DataFrame(data=part_80_seules, columns = ['Part des personnes de plus de 80 ans vivant seules ' + annee], index = ["France"])
        return df_fr

    valeur_part80_seules_fr = part80_seules_France("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",select_annee)

    # Comparaison
    def IV_global(annee):
        df = pd.concat([indice_80_seules_com,valeurs_part80_seules_epci, valeurs_dep_iv, valeurs_reg_iv, valeur_part80_seules_fr])
        year = annee
        return df

    indice_80_seules = IV_global(select_annee)
    st.table(indice_80_seules)

  st.subheader("b.Evolution")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    #FRANCE
    #2014
    valeur_part80_seules_fr_2014 = part80_seules_France("./famille/base-ic-couples-familles-menages-2014.csv",'2014')
    indice_2014 = valeur_part80_seules_fr_2014['Part des personnes de plus de 80 ans vivant seules 2014'][0]
    #2015
    valeur_part80_seules_fr_2015 = part80_seules_France("./famille/base-ic-couples-familles-menages-2015.csv",'2015')
    indice_2015 = valeur_part80_seules_fr_2015['Part des personnes de plus de 80 ans vivant seules 2015'][0]
    #2016
    valeur_part80_seules_fr_2016 = part80_seules_France("./famille/base-ic-couples-familles-menages-2016.csv",'2016')
    indice_2016 = valeur_part80_seules_fr_2016['Part des personnes de plus de 80 ans vivant seules 2016'][0]
    #2017
    valeur_part80_seules_fr_2017 = part80_seules_France("./famille/base-ic-couples-familles-menages-2017.csv",'2017')
    indice_2017 = valeur_part80_seules_fr_2017['Part des personnes de plus de 80 ans vivant seules 2017'][0]
    #2018
    valeur_part80_seules_fr_2018 = part80_seules_France("./famille/base-ic-couples-familles-menages-2018.csv",'2018')
    indice_2018 = valeur_part80_seules_fr_2018['Part des personnes de plus de 80 ans vivant seules 2018'][0]

    df_france_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017,indice_2018]]),
                       columns=['2014', '2015', '2016', '2017','2018'], index=['France'])

    #RÉGION
    #2014
    valeur_part80_seules_region_2014 = IV_region_M2017("./famille/base-ic-couples-familles-menages-2014.csv",str(round(code_region)),'2014')
    indice_2014 = valeur_part80_seules_region_2014['Part des personnes de plus de 80 ans vivant seules 2014'][0]
    #2015
    valeur_part80_seules_region_2015 = IV_region_M2017("./famille/base-ic-couples-familles-menages-2015.csv",str(round(code_region)),'2015')
    indice_2015 = valeur_part80_seules_region_2015['Part des personnes de plus de 80 ans vivant seules 2015'][0]
    #2016
    valeur_part80_seules_region_2016 = IV_region_M2017("./famille/base-ic-couples-familles-menages-2016.csv",str(round(code_region)),'2016')
    indice_2016 = valeur_part80_seules_region_2016['Part des personnes de plus de 80 ans vivant seules 2016'][0]
    #2017
    valeur_part80_seules_region_2017 = IV_region_P2017("./famille/base-ic-couples-familles-menages-2017.csv",str(round(code_region)),'2017')
    indice_2017 = valeur_part80_seules_region_2017['Part des personnes de plus de 80 ans vivant seules 2017'][0]
    #2018
    valeur_part80_seules_region_2018 = IV_region_P2017("./famille/base-ic-couples-familles-menages-2018.csv",str(round(code_region)),'2018')
    indice_2018 = valeur_part80_seules_region_2018['Part des personnes de plus de 80 ans vivant seules 2018'][0]

    df_region_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017,indice_2018]]),
                       columns=['2014', '2015', '2016', '2017','2018'], index=[nom_region])

    #DÉPARTEMENT
    #2014
    valeur_part80_seules_departement_2014 = part80_seules_departement_M2017("./famille/base-ic-couples-familles-menages-2014.csv",code_departement,'2014')
    indice_2014 = valeur_part80_seules_departement_2014['Part des personnes de plus de 80 ans vivant seules 2014'][0]
    #2015
    valeur_part80_seules_departement_2015 = part80_seules_departement_M2017("./famille/base-ic-couples-familles-menages-2015.csv",code_departement,'2015')
    indice_2015 = valeur_part80_seules_departement_2015['Part des personnes de plus de 80 ans vivant seules 2015'][0]
    #2016
    valeur_part80_seules_departement_2016 = part80_seules_departement_M2017("./famille/base-ic-couples-familles-menages-2016.csv",code_departement,'2016')
    indice_2016 = valeur_part80_seules_departement_2016['Part des personnes de plus de 80 ans vivant seules 2016'][0]
    #2017
    valeur_part80_seules_departement_2017 = part80_seules_departement_P2017("./famille/base-ic-couples-familles-menages-2017.csv",code_departement,'2017')
    indice_2017 = valeur_part80_seules_departement_2017['Part des personnes de plus de 80 ans vivant seules 2017'][0]
    #2018
    valeur_part80_seules_departement_2018 = part80_seules_departement_P2017("./famille/base-ic-couples-familles-menages-2018.csv",code_departement,'2018')
    indice_2018 = valeur_part80_seules_departement_2018['Part des personnes de plus de 80 ans vivant seules 2018'][0]

    df_departement_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017,indice_2018]]),
                       columns=['2014', '2015', '2016', '2017','2018'], index=[nom_departement])

    #EPCI
    #2014
    valeur_part80_seules_epci_2014 = part80_seules_epci("./famille/base-ic-couples-familles-menages-2014.csv",code_epci,'2014')
    indice_2014 = valeur_part80_seules_epci_2014['Part des personnes de plus de 80 ans vivant seules 2014'][0]
    #2015
    valeur_part80_seules_epci_2015 = part80_seules_epci("./famille/base-ic-couples-familles-menages-2015.csv",code_epci,'2015')
    indice_2015 = valeur_part80_seules_epci_2015['Part des personnes de plus de 80 ans vivant seules 2015'][0]
    #2016
    valeur_part80_seules_epci_2016 = part80_seules_epci("./famille/base-ic-couples-familles-menages-2016.csv",code_epci,'2016')
    indice_2016 = valeur_part80_seules_epci_2016['Part des personnes de plus de 80 ans vivant seules 2016'][0]
    #2017
    valeur_part80_seules_epci_2017 = part80_seules_epci("./famille/base-ic-couples-familles-menages-2017.csv",code_epci,'2017')
    indice_2017 = valeur_part80_seules_epci_2017['Part des personnes de plus de 80 ans vivant seules 2017'][0]
    #2018
    valeur_part80_seules_epci_2018 = part80_seules_epci("./famille/base-ic-couples-familles-menages-2018.csv",code_epci,'2018')
    indice_2018 = valeur_part80_seules_epci_2018['Part des personnes de plus de 80 ans vivant seules 2018'][0]

    df_epci_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017,indice_2018]]),
                       columns=['2014', '2015', '2016', '2017','2018'], index=[nom_epci])

    #COMMUNE
    #2014
    valeur_part80_seules_commune_2014 = part80_seules_com("./famille/base-ic-couples-familles-menages-2014.csv",code_commune,'2014')
    indice_2014 = valeur_part80_seules_commune_2014['Part des personnes de plus de 80 ans vivant seules 2014'][0]
    #2015
    valeur_part80_seules_commune_2015 = part80_seules_com("./famille/base-ic-couples-familles-menages-2015.csv",code_commune,'2015')
    indice_2015 = valeur_part80_seules_commune_2015['Part des personnes de plus de 80 ans vivant seules 2015'][0]
    #2016
    valeur_part80_seules_commune_2016 = part80_seules_com("./famille/base-ic-couples-familles-menages-2016.csv",code_commune,'2016')
    indice_2016 = valeur_part80_seules_commune_2016['Part des personnes de plus de 80 ans vivant seules 2016'][0]
    #2017
    valeur_part80_seules_commune_2017 = part80_seules_com("./famille/base-ic-couples-familles-menages-2017.csv",code_commune,'2017')
    indice_2017 = valeur_part80_seules_commune_2017['Part des personnes de plus de 80 ans vivant seules 2017'][0]
    #2018
    valeur_part80_seules_commune_2018 = part80_seules_com("./famille/base-ic-couples-familles-menages-2018.csv",code_commune,'2018')
    indice_2018 = valeur_part80_seules_commune_2018['Part des personnes de plus de 80 ans vivant seules 2018'][0]

    df_commune_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017,indice_2018]]),
                       columns=['2014', '2015', '2016', '2017','2018'], index=[nom_commune])

    df_glob_indice_vieux = pd.concat([df_france_glob, df_region_glob, df_departement_glob, df_epci_glob, df_commune_glob])

    st.table(df_glob_indice_vieux)

    df_glob_indice_vieux_transposed = df_glob_indice_vieux.T
    st.line_chart(df_glob_indice_vieux_transposed)



  st.header("3.Indice d'évolution des générations âgées")

  st.subheader("Iris")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    def indice_remplacement_iris(fichier, code, annee) :
      df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep=";", header=0)
      df_indice = df.loc[df['COM'] == code]
      year = annee[-2:]
      df_indice = df_indice[['COM','IRIS', 'P'+ year + '_POP6074','P' + year +'_POP75P' ]]
      df_indice = df_indice.replace(',','.', regex=True)
      df_indice['P'+ year + '_POP6074'] = df_indice['P'+ year + '_POP6074'].astype(float).to_numpy()
      df_indice['P' + year +'_POP75P'] = df_indice['P' + year +'_POP75P'].astype(float).to_numpy()
      df_indice['indice'] = np.where(df_indice['P' + year +'_POP75P'] < 1,df_indice['P' + year +'_POP75P'], (df_indice['P'+ year + '_POP6074'] / df_indice['P' + year +'_POP75P']))
      df_indice['indice'] = df_indice['indice'].astype(float).to_numpy()
      communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
      df_indice_com = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_indice[['IRIS','P' + year +'_POP6074', 'P' + year + '_POP75P','indice']], left_on='CODE_IRIS', right_on="IRIS")
      df_indice_com = df_indice_com[['CODE_IRIS','LIB_IRIS','P' + year +'_POP6074', 'P' + year + '_POP75P','indice']]
      df_indice_com['indice'].round(decimals = 2)
      df_indice_com['P' + year +'_POP6074'] = df_indice_com['P' + year +'_POP6074'].apply(np.int64)
      df_indice_com['P' + year +'_POP75P'] = df_indice_com['P' + year +'_POP75P'].apply(np.int64)
      df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_POP6074':"60 à 74 ans (" + select_annee + ")" ,'P' + year + '_POP75P':"Plus de 75 ans (" + select_annee + ")",'indice':"Indice d'évolution des générations âgées (" + select_annee + ")" })
      return df_indice_com
    nvm_iris =indice_remplacement_iris("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_commune, select_annee)
    with st.expander("Visualiser le tableau des iris"):
      st.table(nvm_iris)

  st.subheader("a.Comparaison entre territoires sur une année")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    # Commune
    def part_remplacement_com(fichier, code_commune, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        df_ville = df.loc[df["COM"]==code_commune,]
        nom_ville = df_ville.loc[df["COM"]==code_commune, 'COM']
        Pop_6074 = df_ville.loc[:, 'P'+ year + '_POP6074'].astype(float).sum(axis = 0, skipna = True)
        Pop_75P = df_ville.loc[:, 'P'+ year + '_POP75P'].astype(float).sum(axis = 0, skipna = True)
        part_remplacement = round((Pop_6074 / Pop_75P),2)
        df_part_remplacement = pd.DataFrame(data=part_remplacement, columns = ['Indice de renouvellement des générations âgées ' + annee], index = [nom_commune])
        return df_part_remplacement
    indice_remplacement_com = part_remplacement_com("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_commune, select_annee)

    # EPCI
    def part_remplacement_epci(fichier, epci, annee):
        epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "TYP_IRIS": str, "MODIF_IRIS": str,"COM": str, "LAB_IRIS": str, "DEP": str, "UU2010": str, "GRD_QUART": str}, sep = ';')
        year = annee[-2:]
        df_epci_com = pd.merge(df[['COM', 'P'+ year + '_POP6074', 'P' + year + '_POP75P']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
        df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM','P'+ year +'_POP6074' , 'P'+ year + '_POP75P']]
        Pop_6074 = df_epci.loc[:, 'P'+ year + '_POP6074']
        Pop_75P = df_epci.loc[:, 'P'+ year + '_POP75P']
        df_P60 = pd.DataFrame(data=Pop_6074)
        df_P75 = pd.DataFrame(data=Pop_75P)
        Somme_P60 = df_P60.sum(axis = 0, skipna = True)
        Somme_P75 = df_P75.sum(axis = 0, skipna = True)
        P60= Somme_P60.values[0]
        P75=Somme_P75.values[0]
        part_remplacement = round((P60 / P75),2)
        df_part_remplacement = pd.DataFrame(data=part_remplacement, columns = ['Indice de renouvellement des générations âgées ' + annee], index = [nom_epci])
        return df_part_remplacement
    indice_remplacement_epci = part_remplacement_epci("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_epci,select_annee)

    # Département
    def part_remplacement_M2017(fichier, departement, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape',sep = ';')
        year = annee[-2:]
        df_departement = df.loc[df["DEP"]==departement, 'P'+ year +'_POP6074' : 'P'+ year + '_POP75P']
        Pop_6074 = df_departement.loc[:, 'P'+ year + '_POP6074']
        Pop_75P = df_departement.loc[:, 'P'+ year + '_POP75P']
        df_P60 = pd.DataFrame(data=Pop_6074)
        df_P75 = pd.DataFrame(data=Pop_75P)
        Somme_P60 = df_P60.sum(axis = 0, skipna = True)
        Somme_P75 = df_P75.sum(axis = 0, skipna = True)
        P60 = Somme_P60.values[0]
        P75 =Somme_P75.values[0]
        part_remplacement = round((P60 / P75),2)
        df_dep = pd.DataFrame(data=part_remplacement, columns = ['Indice de renouvellement des générations âgées ' + annee], index = [nom_departement])
        return df_dep

    def part_remplacement_P2017(fichier, departement, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, encoding= 'unicode_escape',sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_dpt = pd.merge(df[['COM', 'P' + year +'_POP6074', 'P' + year + '_POP75P']], communes_select[['COM','DEP']],  on='COM', how='left')
        df_departement = df_dpt.loc[df_dpt["DEP"]==departement, ['DEP', 'COM','P'+ year +'_POP6074' , 'P'+ year + '_POP75P']]
        Pop_6074 = df_departement.loc[:, 'P'+ year + '_POP6074']
        Pop_75P = df_departement.loc[:, 'P'+ year + '_POP75P']
        df_P60 = pd.DataFrame(data=Pop_6074)
        df_P75 = pd.DataFrame(data=Pop_75P)
        Somme_P60 = df_P60.sum(axis = 0, skipna = True)
        Somme_P75 = df_P75.sum(axis = 0, skipna = True)
        P60= Somme_P60.values[0]
        P75=Somme_P75.values[0]
        part_remplacement = round((P60 / P75),2)
        df_dep = pd.DataFrame(data=part_remplacement, columns = ['Indice de renouvellement des générations âgées ' + annee], index = [nom_departement])
        return df_dep

    if int(select_annee) < 2017:
        indice_remplacement_dep = part_remplacement_M2017("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_departement,select_annee)
    else :
        indice_remplacement_dep = part_remplacement_P2017("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_departement,select_annee)

    # Région
    #si année de 2014 à 2016 (inclus)
    def part_remplacement_region_M2017(fichier, region, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_regions = df.loc[df["REG"]==str(region), 'P'+ year +'_POP6074' : 'P'+ year + '_POP75P']
        P6074 = df_regions.loc[:, 'P'+ year + '_POP6074']
        P75P = df_regions.loc[:, 'P'+ year + '_POP75P']
        df_P60 = pd.DataFrame(data=P6074)
        df_P75 = pd.DataFrame(data=P75P)
        Somme_P60 = df_P60.sum(axis = 0, skipna = True)
        Somme_P75 = df_P75.sum(axis = 0, skipna = True)
        P60 = Somme_P60.values[0]
        P75 = Somme_P75.values[0]
        part_remplacement = round((P60 / P75),2)
        df_reg = pd.DataFrame(data=part_remplacement, columns = ['Indice de renouvellement des générations âgées ' + annee], index = [nom_region])
        return df_reg

    #si année de 2017 à ... (inclus)
    def part_remplacement_region_P2017(fichier, region, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_regions = pd.merge(df[['COM', 'P' + year +'_POP6074', 'P' + year + '_POP75P']], communes_select[['COM','REG']],  on='COM', how='left')
        df_region = df_regions.loc[df_regions["REG"]==str(region), ['REG', 'COM','P'+ year +'_POP6074' , 'P'+ year + '_POP75P']]
        P6074 = df_region.loc[:, 'P'+ year + '_POP6074']
        P75P = df_region.loc[:, 'P'+ year + '_POP75P']
        df_P60 = pd.DataFrame(data=P6074)
        df_P75 = pd.DataFrame(data=P75P)
        Somme_P60 = df_P60.sum(axis = 0, skipna = True)
        Somme_P75 = df_P75.sum(axis = 0, skipna = True)
        P60= Somme_P60.values[0]
        P75=Somme_P75.values[0]
        part_remplacement = round((P60 / P75),2)
        df_reg = pd.DataFrame(data=part_remplacement, columns = ['Indice de renouvellement des générations âgées ' + annee], index = [nom_region])
        return df_reg

    if int(select_annee) < 2017:
        indice_remplacement_reg = part_remplacement_region_M2017("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",str(round(code_region)),select_annee)
    else :
        indice_remplacement_reg = part_remplacement_region_P2017("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",str(round(code_region)),select_annee)

    # France
    def part_remplacement_France(fichier, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        P6074 = df.loc[:, 'P'+ year + '_POP6074']
        P75P = df.loc[:, 'P'+ year + '_POP75P']
        df_P60 = pd.DataFrame(data=P6074)
        df_P75 = pd.DataFrame(data=P75P)
        Somme_P60 = df_P60.sum(axis = 0, skipna = True)
        Somme_P75= df_P75.sum(axis = 0, skipna = True)
        P60 = Somme_P60.values[0]
        P75 = Somme_P75.values[0]
        part_remplacement = round((P60 / P75), 2)
        df_fr = pd.DataFrame(data=part_remplacement, columns = ['Indice de renouvellement des générations âgées ' + annee], index = ["France"])
        return df_fr

    indice_remplacement_fr = part_remplacement_France("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",select_annee)

    # Comparaison
    def indice_remplacement_global(annee):
        df = pd.concat([indice_remplacement_com,indice_remplacement_epci, indice_remplacement_dep, indice_remplacement_reg, indice_remplacement_fr])
        year = annee
        return df

    indice_remplacement = indice_remplacement_global(select_annee)
    st.table(indice_remplacement)


  st.subheader("b.Evolution")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    #FRANCE
    #2014
    valeur_part_remplacement_fr_2014 = part_remplacement_France("./population/base-ic-evol-struct-pop-2014.csv",'2014')
    indice_2014 = valeur_part_remplacement_fr_2014['Indice de renouvellement des générations âgées 2014'][0]
    #2015
    valeur_part_remplacement_fr_2015 = part_remplacement_France("./population/base-ic-evol-struct-pop-2015.csv",'2015')
    indice_2015 = valeur_part_remplacement_fr_2015['Indice de renouvellement des générations âgées 2015'][0]
    #2016
    valeur_part_remplacement_fr_2016 = part_remplacement_France("./population/base-ic-evol-struct-pop-2016.csv",'2016')
    indice_2016 = valeur_part_remplacement_fr_2016['Indice de renouvellement des générations âgées 2016'][0]
    #2017
    valeur_part_remplacement_fr_2017 = part_remplacement_France("./population/base-ic-evol-struct-pop-2017.csv",'2017')
    indice_2017 = valeur_part_remplacement_fr_2017['Indice de renouvellement des générations âgées 2017'][0]
    #2018
    valeur_part_remplacement_fr_2018 = part_remplacement_France("./population/base-ic-evol-struct-pop-2018.csv",'2018')
    indice_2018 = valeur_part_remplacement_fr_2018['Indice de renouvellement des générations âgées 2018'][0]

    df_france_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017,indice_2018]]),
                       columns=['2014', '2015', '2016', '2017','2018'], index=['France'])

    #RÉGION
    #2014
    valeur_part_remplacement_region_2014 = part_remplacement_region_M2017("./population/base-ic-evol-struct-pop-2014.csv",str(round(code_region)),'2014')
    indice_2014 = valeur_part_remplacement_region_2014['Indice de renouvellement des générations âgées 2014'][0]
    #2015
    valeur_part_remplacement_region_2015 = part_remplacement_region_M2017("./population/base-ic-evol-struct-pop-2015.csv",str(round(code_region)),'2015')
    indice_2015 = valeur_part_remplacement_region_2015['Indice de renouvellement des générations âgées 2015'][0]
    #2016
    valeur_part_remplacement_region_2016 = part_remplacement_region_M2017("./population/base-ic-evol-struct-pop-2016.csv",str(round(code_region)),'2016')
    indice_2016 = valeur_part_remplacement_region_2016['Indice de renouvellement des générations âgées 2016'][0]
    #2017
    valeur_part_remplacement_region_2017 = part_remplacement_region_P2017("./population/base-ic-evol-struct-pop-2017.csv",str(round(code_region)),'2017')
    indice_2017 = valeur_part_remplacement_region_2017['Indice de renouvellement des générations âgées 2017'][0]
    #2018
    valeur_part_remplacement_region_2018 = part_remplacement_region_P2017("./population/base-ic-evol-struct-pop-2018.csv",str(round(code_region)),'2018')
    indice_2018 = valeur_part_remplacement_region_2018['Indice de renouvellement des générations âgées 2018'][0]

    df_region_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017,indice_2018]]),
                       columns=['2014', '2015', '2016', '2017','2018'], index=[nom_region])

    #DÉPARTEMENT
    #2014
    valeur_part_remplacement_departement_2014 = part_remplacement_M2017("./population/base-ic-evol-struct-pop-2014.csv",code_departement,'2014')
    indice_2014 = valeur_part_remplacement_departement_2014['Indice de renouvellement des générations âgées 2014'][0]
    #2015
    valeur_part_remplacement_departement_2015 = part_remplacement_M2017("./population/base-ic-evol-struct-pop-2015.csv",code_departement,'2015')
    indice_2015 = valeur_part_remplacement_departement_2015['Indice de renouvellement des générations âgées 2015'][0]
    #2016
    valeur_part_remplacement_departement_2016 = part_remplacement_M2017("./population/base-ic-evol-struct-pop-2016.csv",code_departement,'2016')
    indice_2016 = valeur_part_remplacement_departement_2016['Indice de renouvellement des générations âgées 2016'][0]
    #2017
    valeur_part_remplacement_departement_2017 = part_remplacement_P2017("./population/base-ic-evol-struct-pop-2017.csv",code_departement,'2017')
    indice_2017 = valeur_part_remplacement_departement_2017['Indice de renouvellement des générations âgées 2017'][0]
    #2018
    valeur_part_remplacement_departement_2018 = part_remplacement_P2017("./population/base-ic-evol-struct-pop-2018.csv",code_departement,'2018')
    indice_2018 = valeur_part_remplacement_departement_2018['Indice de renouvellement des générations âgées 2018'][0]

    df_departement_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017,indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_departement])

    #EPCI
    #2014
    valeur_part_remplacement_epci_2014 = part_remplacement_epci("./population/base-ic-evol-struct-pop-2014.csv",code_epci,'2014')
    indice_2014 = valeur_part_remplacement_epci_2014['Indice de renouvellement des générations âgées 2014'][0]
    #2015
    valeur_part_remplacement_epci_2015 = part_remplacement_epci("./population/base-ic-evol-struct-pop-2015.csv",code_epci,'2015')
    indice_2015 = valeur_part_remplacement_epci_2015['Indice de renouvellement des générations âgées 2015'][0]
    #2016
    valeur_part_remplacement_epci_2016 = part_remplacement_epci("./population/base-ic-evol-struct-pop-2016.csv",code_epci,'2016')
    indice_2016 = valeur_part_remplacement_epci_2016['Indice de renouvellement des générations âgées 2016'][0]
    #2017
    valeur_part_remplacement_epci_2017 = part_remplacement_epci("./population/base-ic-evol-struct-pop-2017.csv",code_epci,'2017')
    indice_2017 = valeur_part_remplacement_epci_2017['Indice de renouvellement des générations âgées 2017'][0]
    #2018
    valeur_part_remplacement_epci_2018 = part_remplacement_epci("./population/base-ic-evol-struct-pop-2018.csv",code_epci,'2018')
    indice_2018 = valeur_part_remplacement_epci_2018['Indice de renouvellement des générations âgées 2018'][0]

    df_epci_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017,indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_epci])

    #COMMUNE
    #2014
    valeur_part_remplacement_commune_2014 = part_remplacement_com("./population/base-ic-evol-struct-pop-2014.csv",code_commune,'2014')
    indice_2014 = valeur_part_remplacement_commune_2014['Indice de renouvellement des générations âgées 2014'][0]
    #2015
    valeur_part_remplacement_commune_2015 = part_remplacement_com("./population/base-ic-evol-struct-pop-2015.csv",code_commune,'2015')
    indice_2015 = valeur_part_remplacement_commune_2015['Indice de renouvellement des générations âgées 2015'][0]
    #2016
    valeur_part_remplacement_commune_2016 = part_remplacement_com("./population/base-ic-evol-struct-pop-2016.csv",code_commune,'2016')
    indice_2016 = valeur_part_remplacement_commune_2016['Indice de renouvellement des générations âgées 2016'][0]
    #2017
    valeur_part_remplacement_commune_2017 = part_remplacement_com("./population/base-ic-evol-struct-pop-2017.csv",code_commune,'2017')
    indice_2017 = valeur_part_remplacement_commune_2017['Indice de renouvellement des générations âgées 2017'][0]
    #2018
    valeur_part_remplacement_commune_2018 = part_remplacement_com("./population/base-ic-evol-struct-pop-2018.csv",code_commune,'2018')
    indice_2018 = valeur_part_remplacement_commune_2018['Indice de renouvellement des générations âgées 2018'][0]

    df_commune_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017,indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_commune])

    df_glob_remplacement = pd.concat([df_france_glob, df_region_glob, df_departement_glob, df_epci_glob, df_commune_glob])

    st.table(df_glob_remplacement)

    df_glob_remplacement_transposed = df_glob_remplacement.T
    st.line_chart(df_glob_remplacement_transposed)


    #################################
    st.header("Part des personnes de 60 ans ou plus parmi la population")
    st.subheader("Zoom QPV")

    #Année
    select_annee_60plus = st.select_slider(
         "Sélection de l'année",
         options=['2017', '2018', '2019', '2020', '2021', '2022'],
         value=('2022'))
    st.write('Mon année :', select_annee_60plus)

    def part_60plus_qpv(fichier, nom_ville, annee) :
      fp_qpv = "./qpv.geojson"
      map_qpv_df = gpd.read_file(fp_qpv)
      year = annee[-2:]
      df = pd.read_csv(fichier, dtype={"CODGEO": str}, sep=";")
      map_qpv_df_code_insee = map_qpv_df.merge(df, left_on='code_qp', right_on='CODGEO')
      map_qpv_df_code_insee_extract = map_qpv_df_code_insee[['nom_qp', 'code_qp', 'commune_qp','code_insee', 'TX_TOT_60ETPLUS' ]]
      map_qpv_df_code_insee_extract
      df_qpv = map_qpv_df_code_insee_extract.loc[map_qpv_df_code_insee_extract["commune_qp"].str.contains(nom_ville + "(,|$)")]
      df_qpv = df_qpv.reset_index(drop=True)
      df_qpv = df_qpv[['code_qp', 'nom_qp','commune_qp', 'TX_TOT_60ETPLUS']]
      df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", 'TX_TOT_60ETPLUS' : "Part des 60 ans ou plus " + select_annee_60plus})
      return df_qpv

    part_60plus_qpv = part_60plus_qpv('./population/demographie_qpv/DEMO_' + select_annee_60plus + '.csv', nom_commune, select_annee_60plus)
    st.table(part_60plus_qpv)
