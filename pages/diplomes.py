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
  st.title('🧑‍🎓👨‍🎓 DIPLÔME')

  ####################
  # st.subheader("Mobilité scolaire")
  # df = pd.read_csv("./diplome/FD_MOBSCO_2018.csv", dtype={"COMMUNE": str}, sep = ';')
  # df_commune = df.loc[df["COMMUNE"] == code_commune]
  # iletud = df_commune.groupby(by="ILETUD").agg('count')
  # st.write(iletud)

  # st.caption("1 Dans la commune de résidence actuelle / 2 Dans une autre commune du département de résidence / 3 Dans un autre département de la région de résidence / 4 Hors de la région de résidence actuelle : en métropole / 5 Hors de la région de résidence actuelle : dans un DOM / 6 Hors de la région de résidence actuelle : dans une COM / 7 À l'étranger / Z Sans objet (pas d'inscription dans un établissement d'enseignement)")

  ####################
  # st.subheader("Taux de scolarisée des 2/17 ans")
  # #IRIS
  # df = pd.read_csv("./diplome/base-ic-diplomes-formation-2018-test.csv", dtype={"IRIS": str, "COM": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, sep = ';')
  # df_commune = df.loc[df["COM"] == code_commune]
  # df_commune['P18_POP0217'] = df_commune['P18_POP0205'] + df_commune['P18_POP0610'] + df_commune['P18_POP1114'] + df_commune['P18_POP1517']
  # df_commune['P18_SCOL0217'] = df_commune['P18_SCOL0205'] + df_commune['P18_SCOL0610'] + df_commune['P18_SCOL1114'] + df_commune['P18_SCOL1517']
  # df_commune['PART_SCOL0217'] = df_commune['P18_SCOL0217'] / df_commune['P18_POP0217'] * 100
  # df_commune = df_commune[['P18_SCOL0217','P18_POP0217','PART_SCOL0217']]
  # st.write(df_commune)

  # # Commune
  # def part_scol0217_com(fichier, code_commune, annee):
  #     df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "CODGEO": str,"LAB_IRIS": str}, sep = ';')
  #     year = annee[-2:]
  #     df_ville = df.loc[df["CODGEO"] == code_commune]
  #     df_ville['P18_POP0217'] = df_ville['P18_POP0205'] + df_ville['P18_POP0610'] + df_ville['P18_POP1114'] + df_ville['P18_POP1517']
  #     df_ville['P18_SCOL0217'] = df_ville['P18_SCOL0205'] + df_ville['P18_SCOL0610'] + df_ville['P18_SCOL1114'] + df_ville['P18_SCOL1517']
  #     part_scol0217 = (df_ville['P18_SCOL0217'] / df_ville['P18_POP0217']) * 100
  #     df_part_scol0217 = pd.DataFrame(data=part_scol0217.iloc[0], columns = ['Part de la population 02/17 ans scolarisée ' + annee], index = [nom_commune])
  #     return df_part_scol0217
  # indice_pop_scol0217_com = part_scol0217_com("./diplome/base-cc-diplomes-formation-" + select_annee + ".csv",code_commune, select_annee)
  # st.write(indice_pop_scol0217_com)

  # # Département
  # def part_scol0217_dpt(fichier, code_dpt, annee):
  #     df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "CODGEO": str,"LAB_IRIS": str}, sep = ';')
  #     year = annee[-2:]
  #     df_dpt = df.loc[df["DEP"] == code_dpt]
  #     df_dpt['P18_POP0217'] = df_dpt['P18_POP0205'] + df_dpt['P18_POP0610'] + df_dpt['P18_POP1114'] + df_dpt['P18_POP1517']
  #     df_dpt['P18_SCOL0217'] =  df_dpt['P18_SCOL0205'] + df_dpt['P18_SCOL0610'] + df_dpt['P18_SCOL1114'] + df_dpt['P18_SCOL1517']
  #     pop_scol0217 = df_dpt.loc[:, 'P18_SCOL0217'].sum()
  #     pop0217 = df_dpt.loc[:, 'P18_POP0217'].sum()
  #     part_scol0217 = (pop_scol0217  / pop0217) * 100
  #     df_part_scol0217 = pd.DataFrame(data=part_scol0217, columns = ['Part de la population 02/17 ans scolarisée ' + annee], index = [nom_departement])
  #     return df_part_scol0217
  # indice_pop_scol0217_dpt = part_scol0217_dpt("./diplome/base-cc-diplomes-formation-" + select_annee + ".csv",code_departement, select_annee)
  # st.write(indice_pop_scol0217_dpt)

  ###############
  st.header('1.Sans diplome')
  st.caption("La part de non diplômés parmi les individus de 15 ans et plus non scolarisés nous renseigne \
  significativement sur la part des personnes a priori les plus vulnérables sur le marché de l’emploi. En effet, \
  plus le niveau d’étude obtenu est bas plus les risques de chômage et/ou de non emploi sont élevés. Cette \
  part étant par ailleurs très corrélée avec la catégorie sociale des individus, cet indicateur nous renseigne \
  par ailleurs sur le degré de précarité d’une population. \
  Son intérêt réside principalement dans sa prise en compte dans les politiques publiques :\
   - Politique de l’emploi et d’insertion professionnelle\
   - Etudes et formation")
  st.subheader("Iris")
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
    df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_NSCOL15P':"Personnes non scolarisées de 15 ans ou plus (" + select_annee + ")", 'P' + year +'_NSCOL15P_DIPLMIN':"Personnes non scolarisées de 15 ans ou plus titulaires d'aucun diplôme ou au plus un CEP (" + select_annee + ")" ,'indice':"Part des personnes non scolarisées sans diplôme (" + select_annee + ") en %" })
    return df_indice_com
  indice_part_sans_diplome_iris =part_sans_diplome_iris("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",str(code_commune), select_annee)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(indice_part_sans_diplome_iris)

  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(indice_part_sans_diplome_iris)

  st.download_button(
    label="💾 Télécharger les données",
    data=csv,
    file_name='sans_diplome.csv',
    mime='text/csv',
  )

  st.subheader('Comparaison')
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    # Commune
    def part_sans_diplome_com(fichier, code_commune, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_ville = df.loc[df["COM"]==code_commune]
        pop_non_scol = df_ville.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        pop_non_scol_sans_diplome = (df_ville.loc[:, 'P'+ year + '_NSCOL15P_DIPLMIN'].sum())
        part_sans_diplome = round((pop_non_scol_sans_diplome / pop_non_scol)*100,2)
        df_part_sans_diplome = pd.DataFrame(data=part_sans_diplome, columns = ['Part des personnes sans diplôme ' + annee], index = [nom_commune])
        return df_part_sans_diplome
    indice_sans_diplome_com = part_sans_diplome_com("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",code_commune, select_annee)

    # EPCI
    def part_sans_diplome_epci(fichier, epci, annee):
        epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "TYP_IRIS": str, "MODIF_IRIS": str,"COM": str, "LAB_IRIS": str, "DEP": str, "UU2010": str, "GRD_QUART": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        df_epci_com = pd.merge(df[['COM', 'P' + year + '_NSCOL15P', 'P' + year + '_NSCOL15P_DIPLMIN']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
        df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM','P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_DIPLMIN']]
        pop_non_scol = df_epci.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        pop_non_scol_sans_diplome = df_epci.loc[:, 'P'+ year + '_NSCOL15P_DIPLMIN'].astype(float).sum()
        part_pop_non_scol_sans_diplome = round((pop_non_scol_sans_diplome / pop_non_scol)*100,2)
        df_part_sans_diplome = pd.DataFrame(data=part_pop_non_scol_sans_diplome, columns = ['Part des personnes sans diplôme ' + annee], index = [nom_epci])
        return df_part_sans_diplome
    indice_sans_diplome_epci = part_sans_diplome_epci("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",code_epci,select_annee)


    # Département
    def part_sans_diplome_departement_M2017(fichier, departement, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape',sep = ';')
        year = annee[-2:]
        df_departement = df.loc[df["DEP"]==departement, 'P' + year + '_NSCOL15P' : 'P' + year + '_NSCOL15P_DIPLMIN']
        pop_non_scol = df_departement.loc[:, 'P' + year + '_NSCOL15P'].sum()
        pop_non_scol_sans_diplome = df_departement.loc[:, 'P'+ year + '_NSCOL15P_DIPLMIN'].astype(float).sum()
        part_non_scol_sans_diplome = round((pop_non_scol_sans_diplome / pop_non_scol)*100,2)
        df_part_non_scol_sans_diplome = pd.DataFrame(data=part_non_scol_sans_diplome, columns = ['Part des personnes sans diplôme ' + annee], index = [nom_departement])
        return df_part_non_scol_sans_diplome

    def part_sans_diplome_departement_P2017(fichier, departement, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, encoding= 'unicode_escape',sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_dpt = pd.merge(df[['COM', 'P' + year +'_NSCOL15P', 'P' + year + '_NSCOL15P_DIPLMIN']], communes_select[['COM','DEP']],  on='COM', how='left')
        df_departement = df_dpt.loc[df_dpt["DEP"]==departement, ['DEP', 'COM','P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_DIPLMIN']]
        pop_non_scol = df_departement.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        pop_non_scol_sans_diplome = df_departement.loc[:, 'P'+ year + '_NSCOL15P_DIPLMIN'].astype(float).sum()
        part_non_scol_sans_diplome = round((pop_non_scol_sans_diplome / pop_non_scol)*100,2)
        df_part_non_scol_sans_diplome = pd.DataFrame(data=part_non_scol_sans_diplome, columns = ['Part des personnes sans diplôme ' + annee], index = [nom_departement])
        return df_part_non_scol_sans_diplome

    if int(select_annee) < 2017:
        valeurs_sans_diplome_dep = part_sans_diplome_departement_M2017("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",code_departement,select_annee)
    else :
        valeurs_sans_diplome_dep = part_sans_diplome_departement_P2017("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",code_departement,select_annee)

    # Région
    #si année de 2014 à 2016 (inclus)
    def part_sans_diplome_region_M2017(fichier, region, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        df_regions = df.loc[df["REG"]==str(region), 'P'+ year +'_NSCOL15P' : 'P'+ year + '_NSCOL15P_DIPLMIN']
        pop_non_scol = df_regions.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        pop_non_scol_sans_diplome = df_regions.loc[:, 'P'+ year + '_NSCOL15P_DIPLMIN'].astype(float).sum()
        part_pop_non_scol_sans_diplome = round((pop_non_scol_sans_diplome / pop_non_scol)*100,0)
        df_part_pop_non_scol_sans_diplome = pd.DataFrame(data=part_pop_non_scol_sans_diplome, columns = ['Part des personnes sans diplôme ' + annee], index = [nom_region])
        return df_part_pop_non_scol_sans_diplome

    #si année de 2017 à ... (inclus)
    def part_sans_diplome_region_P2017(fichier, region, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, encoding= 'unicode_escape', sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_regions = pd.merge(df[['COM', 'P' + year +'_NSCOL15P', 'P' + year + '_NSCOL15P_DIPLMIN']], communes_select[['COM','REG']],  on='COM', how='left')
        df_region = df_regions.loc[df_regions["REG"]==str(region), ['REG', 'COM','P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_DIPLMIN']]
        pop_non_scol = df_region.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        pop_non_scol_sans_diplome = df_region.loc[:, 'P'+ year + '_NSCOL15P_DIPLMIN'].astype(float).sum()
        part_pop_non_scol_sans_diplome = round((pop_non_scol_sans_diplome / pop_non_scol)*100,2)
        df_part_pop_non_scol_sans_diplome = pd.DataFrame(data=part_pop_non_scol_sans_diplome, columns = ['Part des personnes sans diplôme ' + annee], index = [nom_region])
        return df_part_pop_non_scol_sans_diplome

    if int(select_annee) < 2017:
        valeurs_sans_diplome_reg = part_sans_diplome_region_M2017("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",str(round(code_region)),select_annee)
    else :
        valeurs_sans_diplome_reg = part_sans_diplome_region_P2017("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",str(round(code_region)),select_annee)

    # France
    def part_sans_diplome_France(fichier, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        select_pop_non_scol = df.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        select_pop_non_scol_sans_diplome = df.loc[:, 'P'+ year + '_NSCOL15P_DIPLMIN'].astype(float).sum()
        part_pop_non_scol_sans_diplome = round((select_pop_non_scol_sans_diplome / select_pop_non_scol)*100, 2)
        df_part_pop_non_scol_sans_diplome = pd.DataFrame(data=part_pop_non_scol_sans_diplome, columns = ['Part des personnes sans diplôme ' + annee], index = ["France"])
        return df_part_pop_non_scol_sans_diplome

    valeur_part_sans_diplome_fr = part_sans_diplome_France("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",select_annee)

    # Comparaison
    def sans_diplome_global(annee):
        df = pd.concat([indice_sans_diplome_com,indice_sans_diplome_epci, valeurs_sans_diplome_dep, valeurs_sans_diplome_reg, valeur_part_sans_diplome_fr])
        year = annee
        return df

    part_sans_diplome_fin = sans_diplome_global(select_annee)
    st.table(part_sans_diplome_fin)

    @st.cache
    def convert_df(df):
      # IMPORTANT: Cache the conversion to prevent computation on every rerun
      return df.to_csv().encode('utf-8')

    csv = convert_df(part_sans_diplome_fin)

    st.download_button(
      label="💾 Télécharger les données",
      data=csv,
      file_name='sans_diplome_comparaison.csv',
      mime='text/csv',
    )

  st.subheader("b.Evolution")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    valeur_part_sans_diplome_fr_2014 = part_sans_diplome_France("./diplome/base-ic-diplomes-formation-2014-test.csv",'2014')
    valeur_part_sans_diplome_fr_2014.loc['France', 'Part des personnes sans diplôme 2014'].squeeze()

    #FRANCE
    #2014
    valeur_part_sans_diplome_fr_2014 = part_sans_diplome_France("./diplome/base-ic-diplomes-formation-2014-test.csv",'2014')
    indice_2014 = valeur_part_sans_diplome_fr_2014['Part des personnes sans diplôme 2014'][0]
    #2015
    valeur_part_sans_diplome_fr_2015 = part_sans_diplome_France("./diplome/base-ic-diplomes-formation-2015-test.csv",'2015')
    indice_2015 = valeur_part_sans_diplome_fr_2015['Part des personnes sans diplôme 2015'][0]
    #2016
    valeur_part_sans_diplome_fr_2016 = part_sans_diplome_France("./diplome/base-ic-diplomes-formation-2016-test.csv",'2016')
    indice_2016 = valeur_part_sans_diplome_fr_2016['Part des personnes sans diplôme 2016'][0]
    #2017
    valeur_part_sans_diplome_fr_2017 = part_sans_diplome_France("./diplome/base-ic-diplomes-formation-2017-test.csv",'2017')
    indice_2017 = valeur_part_sans_diplome_fr_2017['Part des personnes sans diplôme 2017'][0]
    #2018
    valeur_part_sans_diplome_fr_2018 = part_sans_diplome_France("./diplome/base-ic-diplomes-formation-2018-test.csv",'2018')
    indice_2018 = valeur_part_sans_diplome_fr_2018['Part des personnes sans diplôme 2018'][0]
    df_france_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=['France'])

    #RÉGION
    #2014
    valeur_part_sans_diplome_region_2014 = part_sans_diplome_region_M2017("./diplome/base-ic-diplomes-formation-2014-test.csv",str(round(code_region)),'2014')
    indice_2014 = valeur_part_sans_diplome_region_2014['Part des personnes sans diplôme 2014'][0]
    #2015
    valeur_part_sans_diplome_region_2015 = part_sans_diplome_region_M2017("./diplome/base-ic-diplomes-formation-2015-test.csv",str(round(code_region)),'2015')
    indice_2015 = valeur_part_sans_diplome_region_2015['Part des personnes sans diplôme 2015'][0]
    #2016
    valeur_part_sans_diplome_region_2016 = part_sans_diplome_region_M2017("./diplome/base-ic-diplomes-formation-2016-test.csv",str(round(code_region)),'2016')
    indice_2016 = valeur_part_sans_diplome_region_2016['Part des personnes sans diplôme 2016'][0]
    #2017
    valeur_part_sans_diplome_region_2017 = part_sans_diplome_region_P2017("./diplome/base-ic-diplomes-formation-2017-test.csv",str(round(code_region)),'2017')
    indice_2017 = valeur_part_sans_diplome_region_2017['Part des personnes sans diplôme 2017'][0]
    #2018
    valeur_part_sans_diplome_region_2018 = part_sans_diplome_region_P2017("./diplome/base-ic-diplomes-formation-2018-test.csv",str(round(code_region)),'2018')
    indice_2018 = valeur_part_sans_diplome_region_2018['Part des personnes sans diplôme 2018'][0]
    df_region_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_region])

    #DÉPARTEMENT
    #2014
    valeur_part_sans_diplome_departement_2014 = part_sans_diplome_departement_M2017("./diplome/base-ic-diplomes-formation-2014-test.csv",code_departement,'2014')
    indice_2014 = valeur_part_sans_diplome_departement_2014['Part des personnes sans diplôme 2014'][0]
    #2015
    valeur_part_sans_diplome_departement_2015 = part_sans_diplome_departement_M2017("./diplome/base-ic-diplomes-formation-2015-test.csv",code_departement,'2015')
    indice_2015 = valeur_part_sans_diplome_departement_2015['Part des personnes sans diplôme 2015'][0]
    #2016
    valeur_part_sans_diplome_departement_2016 = part_sans_diplome_departement_M2017("./diplome/base-ic-diplomes-formation-2016-test.csv",code_departement,'2016')
    indice_2016 = valeur_part_sans_diplome_departement_2016['Part des personnes sans diplôme 2016'][0]
    #2017
    valeur_part_sans_diplome_departement_2017 = part_sans_diplome_departement_P2017("./diplome/base-ic-diplomes-formation-2017-test.csv",code_departement,'2017')
    indice_2017 = valeur_part_sans_diplome_departement_2017['Part des personnes sans diplôme 2017'][0]
    #2018
    valeur_part_sans_diplome_departement_2018 = part_sans_diplome_departement_P2017("./diplome/base-ic-diplomes-formation-2018-test.csv",code_departement,'2018')
    indice_2018 = valeur_part_sans_diplome_departement_2018['Part des personnes sans diplôme 2018'][0]

    df_departement_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_departement])

    #EPCI
    #2014
    valeur_part_sans_diplome_epci_2014 = part_sans_diplome_epci("./diplome/base-ic-diplomes-formation-2014-test.csv",code_epci,'2014')
    indice_2014 = valeur_part_sans_diplome_epci_2014['Part des personnes sans diplôme 2014'][0]
    #2015
    valeur_part_sans_diplome_epci_2015 = part_sans_diplome_epci("./diplome/base-ic-diplomes-formation-2015-test.csv",code_epci,'2015')
    indice_2015 = valeur_part_sans_diplome_epci_2015['Part des personnes sans diplôme 2015'][0]
    #2016
    valeur_part_sans_diplome_epci_2016 = part_sans_diplome_epci("./diplome/base-ic-diplomes-formation-2016-test.csv",code_epci,'2016')
    indice_2016 = valeur_part_sans_diplome_epci_2016['Part des personnes sans diplôme 2016'][0]
    #2017
    valeur_part_sans_diplome_epci_2017 = part_sans_diplome_epci("./diplome/base-ic-diplomes-formation-2017-test.csv",code_epci,'2017')
    indice_2017 = valeur_part_sans_diplome_epci_2017['Part des personnes sans diplôme 2017'][0]
    #2018
    valeur_part_sans_diplome_epci_2018 = part_sans_diplome_epci("./diplome/base-ic-diplomes-formation-2018-test.csv",code_epci,'2018')
    indice_2018 = valeur_part_sans_diplome_epci_2018['Part des personnes sans diplôme 2018'][0]

    df_epci_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_epci])

    #COMMUNE
    #2014
    valeur_part_sans_diplome_commune_2014 = part_sans_diplome_com("./diplome/base-ic-diplomes-formation-2014-test.csv",code_commune,'2014')
    indice_2014 = valeur_part_sans_diplome_commune_2014['Part des personnes sans diplôme 2014'][0]
    #2015
    valeur_part_sans_diplome_commune_2015 = part_sans_diplome_com("./diplome/base-ic-diplomes-formation-2015-test.csv",code_commune,'2015')
    indice_2015 = valeur_part_sans_diplome_commune_2015['Part des personnes sans diplôme 2015'][0]
    #2016
    valeur_part_sans_diplome_commune_2016 = part_sans_diplome_com("./diplome/base-ic-diplomes-formation-2016-test.csv",code_commune,'2016')
    indice_2016 = valeur_part_sans_diplome_commune_2016['Part des personnes sans diplôme 2016'][0]
    #2017
    valeur_part_sans_diplome_commune_2017 = part_sans_diplome_com("./diplome/base-ic-diplomes-formation-2017-test.csv",code_commune,'2017')
    indice_2017 = valeur_part_sans_diplome_commune_2017['Part des personnes sans diplôme 2017'][0]
    #2018
    valeur_part_sans_diplome_commune_2018 = part_sans_diplome_com("./diplome/base-ic-diplomes-formation-2018-test.csv",code_commune,'2018')
    indice_2018 = valeur_part_sans_diplome_commune_2018['Part des personnes sans diplôme 2018'][0]

    df_commune_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_commune])

    df_glob_sans_diplome= pd.concat([df_france_glob, df_region_glob, df_departement_glob, df_epci_glob, df_commune_glob])

    st.table(df_glob_sans_diplome)

    df_glob_sans_diplome_transposed = df_glob_sans_diplome.T
    st.line_chart(df_glob_sans_diplome_transposed)

    #Indicateurs clés
    evol_14_18_com = df_glob_sans_diplome.iloc[4]["2018"] - df_glob_sans_diplome.iloc[4]["2014"]
    evol_14_18_fr = df_glob_sans_diplome.iloc[0]["2018"] - df_glob_sans_diplome.iloc[0]["2014"]

    col1, col2 = st.columns(2)
    col1.metric(label=nom_commune + " " + select_annee, value=str('{:,.0f}'.format(df_glob_sans_diplome.iloc[4]["2018"]).replace(",", " ") + "%"), delta=str('{:,.0f}'.format(evol_14_18_com.item()).replace(",", " ")) + " points de % depuis 2014",delta_color="inverse")
    col2.metric(label="France " + select_annee, value=str('{:,.0f}'.format(df_glob_sans_diplome.iloc[0]["2018"]).replace(",", " ") + "%"), delta=str('{:,.0f}'.format(evol_14_18_fr.item()).replace(",", " ")) + " points de % depuis 2014",delta_color="inverse")

  ##############################################################################
  #P18_NSCOL15P_SUP2
  #P18_NSCOL15P_SUP34
  #P18_NSCOL15P_SUP5

  st.header('2.Études supérieures')
  st.subheader("Iris")

  @st.cache(persist=True)
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
      df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_NSCOL15P':"Personnes non scolarisées de 15 ans ou plus (" + select_annee + ")", 'P' + year +'_NSCOL15P_SUP2':"Titulaire d'un BAC+2 (" + select_annee + ")" ,'P' + year +'_NSCOL15P_SUP34':"Titulaire d'un BAC+3 ou 4 (" + select_annee + ")" ,'P' + year +'_NSCOL15P_SUP5':"Titulaire d'un BAC+5 ou sup (" + select_annee + ")" ,'indice':"Part des personnes non scolarisées titulaires d'un diplôme de l'enseignement supérieur (" + select_annee + ") en %" })
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
      df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_NSCOL15P':"Personnes non scolarisées de 15 ans ou plus (" + select_annee + ")", 'P' + year +'_NSCOL15P_SUP':"Titulaire d'un diplôme de l'enseignement supérieur (" + select_annee + ")" ,'indice':"Part des personnes non scolarisées titulaires d'un diplôme de l'enseignement supérieur (" + select_annee + ") en %" })
      return df_indice_com

  indice_part_etude_sup_iris =part_etude_sup_iris("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",code_commune, select_annee)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(indice_part_etude_sup_iris)

  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(indice_part_etude_sup_iris)

  st.download_button(
    label="💾 Télécharger les données",
    data=csv,
    file_name='etude_sup_iris.csv',
    mime='text/csv',
  )

  st.subheader('Comparaison')
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    # Commune
    @st.cache(persist=True)
    def part_etude_sup_com(fichier, code_commune, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        if int(annee) >= 2017:
          df_ville = df.loc[df["COM"]==code_commune]
          pop_non_scol = df_ville.loc[:, 'P'+ year + '_NSCOL15P'].sum()
          pop_non_scol_bac2 = (df_ville.loc[:, 'P'+ year + '_NSCOL15P_SUP2'].sum())
          pop_non_scol_bac34 = (df_ville.loc[:, 'P'+ year + '_NSCOL15P_SUP34'].sum())
          pop_non_scol_bac5 = (df_ville.loc[:, 'P'+ year + '_NSCOL15P_SUP5'].sum())
          part_etude_sup = ((pop_non_scol_bac2 + pop_non_scol_bac34 + pop_non_scol_bac5) / pop_non_scol) * 100
          df_part_etude_sup = pd.DataFrame(data=part_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_commune])
          return df_part_etude_sup
        else:
          df_ville = df.loc[df["COM"]==code_commune]
          pop_non_scol = df_ville.loc[:, 'P'+ year + '_NSCOL15P'].sum()
          pop_non_scol_etude_sup = (df_ville.loc[:, 'P'+ year + '_NSCOL15P_SUP'].sum())
          part_etude_sup = (pop_non_scol_etude_sup / pop_non_scol) * 100
          df_part_etude_sup = pd.DataFrame(data=part_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_commune])
          return df_part_etude_sup
    indice_sans_diplome_com = part_etude_sup_com("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",code_commune, select_annee)

    # EPCI
    @st.cache(persist=True)
    def part_etude_sup_epci(fichier, epci, annee):
        epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "TYP_IRIS": str, "MODIF_IRIS": str,"COM": str, "LAB_IRIS": str, "DEP": str, "UU2010": str, "GRD_QUART": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        if int(annee) >= 2017:
          df_epci_com = pd.merge(df[['COM', 'P' + year + '_NSCOL15P', 'P' + year + '_NSCOL15P_SUP2', 'P' + year + '_NSCOL15P_SUP34', 'P' + year + '_NSCOL15P_SUP5']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
          df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM','P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_SUP2', 'P'+ year + '_NSCOL15P_SUP34', 'P'+ year + '_NSCOL15P_SUP5']]
          pop_non_scol = df_epci.loc[:, 'P'+ year + '_NSCOL15P'].sum()
          pop_bac_sup2 = df_epci.loc[:, 'P'+ year + '_NSCOL15P_SUP2'].sum()
          pop_bac_sup34 = df_epci.loc[:, 'P'+ year + '_NSCOL15P_SUP34'].sum()
          pop_bac_sup5 = df_epci.loc[:, 'P'+ year + '_NSCOL15P_SUP5'].sum()
          part_pop_non_scol_etude_sup = ((pop_bac_sup2 + pop_bac_sup34 + pop_bac_sup5) / pop_non_scol)*100
          df_part_etude_sup = pd.DataFrame(data=part_pop_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_epci])
          return df_part_etude_sup
        else:
          df_epci_com = pd.merge(df[['COM', 'P' + year + '_NSCOL15P', 'P' + year + '_NSCOL15P_SUP']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
          df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM','P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_SUP']]
          pop_non_scol = df_epci.loc[:, 'P'+ year + '_NSCOL15P'].sum()
          pop_bac_sup = df_epci.loc[:, 'P'+ year + '_NSCOL15P_SUP'].sum()
          part_pop_non_scol_etude_sup = (pop_bac_sup / pop_non_scol)*100
          df_part_etude_sup = pd.DataFrame(data=part_pop_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_epci])
          return df_part_etude_sup
    indice_etude_sup_epci = part_etude_sup_epci("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",code_epci,select_annee)

    # Département
    @st.cache(persist=True)
    def part_etude_sup_departement(fichier, departement, annee):
      if int(annee) >= 2017:
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str},sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_dpt = pd.merge(df[['COM', 'P' + year +'_NSCOL15P', 'P' + year + '_NSCOL15P_SUP2', 'P' + year + '_NSCOL15P_SUP34', 'P' + year + '_NSCOL15P_SUP5']], communes_select[['COM','DEP']],  on='COM', how='left')
        df_departement = df_dpt.loc[df_dpt["DEP"]==departement, ['DEP', 'COM','P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_SUP2', 'P' + year + '_NSCOL15P_SUP34', 'P' + year + '_NSCOL15P_SUP5']]
        pop_non_scol = df_departement.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        pop_non_scol_bac2 = df_departement.loc[:, 'P'+ year + '_NSCOL15P_SUP2'].sum()
        pop_non_scol_bac34 = df_departement.loc[:, 'P'+ year + '_NSCOL15P_SUP34'].sum()
        pop_non_scol_bac5P = df_departement.loc[:, 'P'+ year + '_NSCOL15P_SUP5'].sum()
        part_non_scol_etude_sup = ((pop_non_scol_bac2 + pop_non_scol_bac34 + pop_non_scol_bac5P ) / pop_non_scol)*100
        df_part_non_scol_etude_sup = pd.DataFrame(data=part_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_departement])
        return df_part_non_scol_etude_sup
      else:
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str},sep = ';')
        year = annee[-2:]
        df_departement = df.loc[df["DEP"]==departement, 'P' + year + '_NSCOL15P' : 'P' + year + '_NSCOL15P_SUP']
        pop_non_scol = df_departement.loc[:, 'P' + year + '_NSCOL15P'].sum()
        pop_non_scol_etude_sup = df_departement.loc[:, 'P'+ year + '_NSCOL15P_SUP'].sum()
        part_non_scol_etude_sup = (pop_non_scol_etude_sup / pop_non_scol)*100
        df_part_non_scol_etude_sup = pd.DataFrame(data=part_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_departement])
        return df_part_non_scol_etude_sup

    valeurs_etude_sup_dep = part_etude_sup_departement("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",code_departement,select_annee)

    # Région
    @st.cache(persist=True)
    def part_etude_sup_region(fichier, region, annee):
      if int(annee) >= 2017:
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_regions = pd.merge(df[['COM', 'P' + year +'_NSCOL15P', 'P' + year + '_NSCOL15P_SUP2', 'P' + year + '_NSCOL15P_SUP34', 'P' + year + '_NSCOL15P_SUP5']], communes_select[['COM','REG']],  on='COM', how='left')
        df_region = df_regions.loc[df_regions["REG"]==region, ['REG', 'COM','P'+ year +'_NSCOL15P' , 'P'+ year + '_NSCOL15P_SUP2', 'P'+ year + '_NSCOL15P_SUP34', 'P'+ year + '_NSCOL15P_SUP5']]
        pop_non_scol = df_region.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        pop_non_scol_bac2 = df_region.loc[:, 'P'+ year + '_NSCOL15P_SUP2'].sum()
        pop_non_scol_bac34 = df_region.loc[:, 'P'+ year + '_NSCOL15P_SUP34'].sum()
        pop_non_scol_bac5 = df_region.loc[:, 'P'+ year + '_NSCOL15P_SUP5'].sum()
        part_pop_non_scol_etude_sup = ((pop_non_scol_bac2 + pop_non_scol_bac34 + pop_non_scol_bac5) / pop_non_scol)*100
        df_part_pop_non_scol_etude_sup = pd.DataFrame(data=part_pop_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_region])
        return df_part_pop_non_scol_etude_sup
      else:
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_regions = df.loc[df["REG"]==region, 'P'+ year +'_NSCOL15P' : 'P'+ year + '_NSCOL15P_SUP']
        pop_non_scol = df_regions.loc[:, 'P'+ year + '_NSCOL15P'].sum()
        pop_non_scol_etude_sup = df_regions.loc[:, 'P'+ year + '_NSCOL15P_SUP'].sum()
        part_pop_non_scol_etude_sup = (pop_non_scol_etude_sup / pop_non_scol)*100
        df_part_pop_non_scol_etude_sup = pd.DataFrame(data=part_pop_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_region])
        return df_part_pop_non_scol_etude_sup

    valeurs_etude_sup_reg = part_etude_sup_region("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",str(round(code_region)),select_annee)

    # France
    @st.cache(persist=True)
    def part_etude_sup_France(fichier, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
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

    valeur_part_etude_sup_fr = part_etude_sup_France("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",select_annee)

    # Comparaison
    @st.cache(persist=True)
    def etude_sup_global(annee):
        df = pd.concat([indice_sans_diplome_com,indice_etude_sup_epci, valeurs_etude_sup_dep, valeurs_etude_sup_reg, valeur_part_etude_sup_fr])
        year = annee
        return df

    part_etude_sup_fin = etude_sup_global(select_annee)
    st.table(part_etude_sup_fin)

    @st.cache
    def convert_df(df):
      # IMPORTANT: Cache the conversion to prevent computation on every rerun
      return df.to_csv().encode('utf-8')

    csv = convert_df(part_etude_sup_fin)

    st.download_button(
      label="💾 Télécharger les données",
      data=csv,
      file_name='etude_sup_comparaison.csv',
      mime='text/csv',
    )

  st.subheader("b.Evolution")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    #FRANCE
    #2014
    valeur_part_etude_sup_fr_2014 = part_etude_sup_France("./diplome/base-ic-diplomes-formation-2014-test.csv",'2014')
    indice_2014 = valeur_part_etude_sup_fr_2014["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2014"][0]
    #2015
    valeur_part_etude_sup_fr_2015 = part_etude_sup_France("./diplome/base-ic-diplomes-formation-2015-test.csv",'2015')
    indice_2015 = valeur_part_etude_sup_fr_2015["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2015"][0]
    #2016
    valeur_part_etude_sup_fr_2016 = part_etude_sup_France("./diplome/base-ic-diplomes-formation-2016-test.csv",'2016')
    indice_2016 = valeur_part_etude_sup_fr_2016["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2016"][0]
    #2017
    valeur_part_etude_sup_fr_2017 = part_etude_sup_France("./diplome/base-ic-diplomes-formation-2017-test.csv",'2017')
    indice_2017 = valeur_part_etude_sup_fr_2017["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2017"][0]
    #2018
    valeur_part_etude_sup_fr_2018 = part_etude_sup_France("./diplome/base-ic-diplomes-formation-2018-test.csv",'2018')
    indice_2018 = valeur_part_etude_sup_fr_2018["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2018"][0]
    df_france_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=['France'])

    #RÉGION
    #2014
    valeur_part_etude_sup_region_2014 = part_etude_sup_region("./diplome/base-ic-diplomes-formation-2014-test.csv",str(round(code_region)),'2014')
    indice_2014 = valeur_part_etude_sup_region_2014["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2014"][0]
    #2015
    valeur_part_etude_sup_region_2015 = part_etude_sup_region("./diplome/base-ic-diplomes-formation-2015-test.csv",str(round(code_region)),'2015')
    indice_2015 = valeur_part_etude_sup_region_2015["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2015"][0]
    #2016
    valeur_part_etude_sup_region_2016 = part_etude_sup_region("./diplome/base-ic-diplomes-formation-2016-test.csv",str(round(code_region)),'2016')
    indice_2016 = valeur_part_etude_sup_region_2016["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2016"][0]
    #2017
    valeur_part_etude_sup_region_2017 = part_etude_sup_region("./diplome/base-ic-diplomes-formation-2017-test.csv",str(round(code_region)),'2017')
    indice_2017 = valeur_part_etude_sup_region_2017["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2017"][0]
    #2018
    valeur_part_etude_sup_region_2018 = part_etude_sup_region("./diplome/base-ic-diplomes-formation-2018-test.csv",str(round(code_region)),'2018')
    indice_2018 = valeur_part_etude_sup_region_2018["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2018"][0]
    indice_2018
    df_region_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_region])
    df_region_glob

    #DÉPARTEMENT
    #2014
    valeur_part_etude_sup_departement_2014 = part_etude_sup_departement("./diplome/base-ic-diplomes-formation-2014-test.csv",code_departement,'2014')
    indice_2014 = valeur_part_etude_sup_departement_2014["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2014"][0]
    #2015
    valeur_part_etude_sup_departement_2015 = part_etude_sup_departement("./diplome/base-ic-diplomes-formation-2015-test.csv",code_departement,'2015')
    indice_2015 = valeur_part_etude_sup_departement_2015["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2015"][0]
    #2016
    valeur_part_etude_sup_departement_2016 = part_etude_sup_departement("./diplome/base-ic-diplomes-formation-2016-test.csv",code_departement,'2016')
    indice_2016 = valeur_part_etude_sup_departement_2016["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2016"][0]
    #2017
    valeur_part_etude_sup_departement_2017 = part_etude_sup_departement("./diplome/base-ic-diplomes-formation-2017-test.csv",code_departement,'2017')
    indice_2017 = valeur_part_etude_sup_departement_2017["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2017"][0]
    #2018
    valeur_part_etude_sup_departement_2018 = part_etude_sup_departement("./diplome/base-ic-diplomes-formation-2018-test.csv",code_departement,'2018')
    indice_2018 = valeur_part_etude_sup_departement_2018["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2018"][0]

    df_departement_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_departement])

    #EPCI
    #2014
    valeur_part_etude_sup_epci_2014 = part_etude_sup_epci("./diplome/base-ic-diplomes-formation-2014-test.csv",code_epci,'2014')
    indice_2014 = valeur_part_etude_sup_epci_2014["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2014"][0]
    #2015
    valeur_part_etude_sup_epci_2015 = part_etude_sup_epci("./diplome/base-ic-diplomes-formation-2015-test.csv",code_epci,'2015')
    indice_2015 = valeur_part_etude_sup_epci_2015["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2015"][0]
    #2016
    valeur_part_etude_sup_epci_2016 = part_etude_sup_epci("./diplome/base-ic-diplomes-formation-2016-test.csv",code_epci,'2016')
    indice_2016 = valeur_part_etude_sup_epci_2016["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2016"][0]
    #2017
    valeur_part_etude_sup_epci_2017 = part_etude_sup_epci("./diplome/base-ic-diplomes-formation-2017-test.csv",code_epci,'2017')
    indice_2017 = valeur_part_etude_sup_epci_2017["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2017"][0]
    #2018
    valeur_part_etude_sup_epci_2018 = part_etude_sup_epci("./diplome/base-ic-diplomes-formation-2018-test.csv",code_epci,'2018')
    indice_2018 = valeur_part_etude_sup_epci_2018["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2018"][0]

    df_epci_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_epci])

    #COMMUNE
    #2014
    valeur_part_etude_sup_commune_2014 = part_etude_sup_com("./diplome/base-ic-diplomes-formation-2014-test.csv",code_commune,'2014')
    indice_2014 = valeur_part_etude_sup_commune_2014["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2014"][0]
    #2015
    valeur_part_etude_sup_commune_2015 = part_etude_sup_com("./diplome/base-ic-diplomes-formation-2015-test.csv",code_commune,'2015')
    indice_2015 = valeur_part_etude_sup_commune_2015["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2015"][0]
    #2016
    valeur_part_etude_sup_commune_2016 = part_etude_sup_com("./diplome/base-ic-diplomes-formation-2016-test.csv",code_commune,'2016')
    indice_2016 = valeur_part_etude_sup_commune_2016["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2016"][0]
    #2017
    valeur_part_etude_sup_commune_2017 = part_etude_sup_com("./diplome/base-ic-diplomes-formation-2017-test.csv",code_commune,'2017')
    indice_2017 = valeur_part_etude_sup_commune_2017["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2017"][0]
    #2018
    valeur_part_etude_sup_commune_2018 = part_etude_sup_com("./diplome/base-ic-diplomes-formation-2018-test.csv",code_commune,'2018')
    indice_2018 = valeur_part_etude_sup_commune_2018["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2018"][0]

    df_commune_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_commune])

    df_glob_sans_diplome= pd.concat([df_france_glob, df_region_glob, df_departement_glob, df_epci_glob, df_commune_glob])

    st.table(df_glob_sans_diplome)

    df_glob_sans_diplome_transposed = df_glob_sans_diplome.T
    st.line_chart(df_glob_sans_diplome_transposed)





