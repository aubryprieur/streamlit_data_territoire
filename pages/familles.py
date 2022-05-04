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
  st.title("FAMILLES")
  st.header('1.Part des familles monoparentales')

  st.subheader("Iris")
  def part_fam_mono_iris(fichier, code, annee) :
    df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, encoding= 'unicode_escape', sep=";", header=0)
    df_indice = df.loc[df['COM'] == code]
    year = annee[-2:]
    df_indice = df_indice[['COM','IRIS', 'C'+ year + '_FAMMONO','C' + year +'_FAM' ]]
    df_indice = df_indice.replace(',','.', regex=True)
    df_indice['C'+ year + '_FAM'] = df_indice['C'+ year + '_FAM'].astype(float).to_numpy()
    df_indice['C' + year +'_FAMMONO'] = df_indice['C' + year +'_FAMMONO'].astype(float).to_numpy()
    df_indice['indice'] = np.where(df_indice['C' + year +'_FAM'] < 1,df_indice['C' + year +'_FAM'], (df_indice['C'+ year + '_FAMMONO'] / df_indice['C' + year +'_FAM']*100))
    df_indice['indice'] = df_indice['indice'].astype(float).to_numpy()
    communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
    df_indice_com = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_indice[['IRIS','C' + year +'_FAM', 'C' + year + '_FAMMONO','indice']], left_on='CODE_IRIS', right_on="IRIS")
    df_indice_com = df_indice_com[['CODE_IRIS','LIB_IRIS','C' + year +'_FAM', 'C' + year + '_FAMMONO','indice']]
    df_indice_com['indice'] = df_indice_com['indice'].apply(np.int64)
    df_indice_com['C' + year +'_FAM'] = df_indice_com['C' + year +'_FAM'].apply(np.int64)
    df_indice_com['C' + year +'_FAMMONO'] = df_indice_com['C' + year +'_FAMMONO'].apply(np.int64)
    df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'C' + year +'_FAMMONO':"Familles monoparentales (" + select_annee + ")" ,'C' + year + '_FAM':"Familles (" + select_annee + ")" ,'indice':"Part des familles monoparentales (" + select_annee + ")" })
    return df_indice_com
  indice_part_fam_mono_iris =part_fam_mono_iris("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_commune, select_annee)
  with st.expander("Visualiser le tableau des iris"):
    st.table(indice_part_fam_mono_iris)

  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(indice_part_fam_mono_iris)

  st.download_button(
    label="💾 Télécharger les données",
    data=csv,
    file_name='fam_monop_iris.csv',
    mime='text/csv',
  )

  st.subheader("a.Comparaison sur une année")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    # Commune
    def part_fam_mono_com(fichier, code_commune, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        df_ville = df.loc[df["COM"]==code_commune,]
        nom_ville = df_ville.loc[df["COM"]==code_commune, 'COM']
        familles = df_ville.loc[:, 'C'+ year + '_FAM'].astype(float).sum(axis = 0, skipna = True)
        familles_mono = df_ville.loc[:, 'C'+ year + '_FAMMONO'].astype(float).sum(axis = 0, skipna = True)
        part_fam_mono = round((familles_mono / familles)*100,2)
        df_Part_fam_mono = pd.DataFrame(data=part_fam_mono, columns = ['Part des familles monoparentales ' + annee], index = [nom_commune])
        return df_Part_fam_mono
    indice_fam_mono_com = part_fam_mono_com("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_commune, select_annee)

    # EPCI
    def part_fam_mono_epci(fichier, epci, annee):
        epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "TYP_IRIS": str, "MODIF_IRIS": str,"COM": str, "LAB_IRIS": str, "DEP": str, "UU2010": str, "GRD_QUART": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        df_epci_com = pd.merge(df[['COM', 'C' + year + '_FAM', 'C' + year + '_FAMMONO']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
        df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM','C'+ year +'_FAM' , 'C'+ year + '_FAMMONO']]
        familles = df_epci.loc[:, 'C'+ year + '_FAM']
        familles_mono = df_epci.loc[:, 'C'+ year + '_FAMMONO']
        df_familles = pd.DataFrame(data=familles)
        df_familles_mono = pd.DataFrame(data=familles_mono)
        Somme_familles = df_familles.sum(axis = 0, skipna = True)
        Somme_familles_mono = df_familles_mono.sum(axis = 0, skipna = True)
        val_familles = Somme_familles.values[0]
        val_familles_mono = Somme_familles_mono.values[0]
        part_familles_mono = round((val_familles_mono / val_familles)*100,2)
        df_Part_familles_mono = pd.DataFrame(data=part_familles_mono, columns = ['Part des familles monoparentales ' + annee], index = [nom_epci])
        return df_Part_familles_mono
    indice_fam_mono_epci = part_fam_mono_epci("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_epci,select_annee)

    # Département
    def part_fam_mono_departement_M2017(fichier, departement, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape',sep = ';')
        year = annee[-2:]
        df_departement = df.loc[df["DEP"]==departement, 'C'+ year +'_FAM' : 'C'+ year + '_FAMMONO']
        familles = df_departement.loc[:, 'C'+ year + '_FAM']
        familles_mono = df_departement.loc[:, 'C'+ year + '_FAMMONO']
        df_familles = pd.DataFrame(data=familles)
        df_familles_mono = pd.DataFrame(data=familles_mono)
        Somme_familles = df_familles.sum(axis = 0, skipna = True)
        Somme_familles_mono = df_familles_mono.sum(axis = 0, skipna = True)
        val_familles = Somme_familles.values[0]
        val_familles_mono = Somme_familles_mono.values[0]
        part_familles_mono = round((val_familles_mono / val_familles)*100,2)
        df_Part_familles_mono = pd.DataFrame(data=part_familles_mono, columns = ['Part des familles monoparentales ' + annee], index = [nom_departement])
        return df_Part_familles_mono

    def part_fam_mono_departement_P2017(fichier, departement, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, encoding= 'unicode_escape',sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_dpt = pd.merge(df[['COM', 'C' + year +'_FAM', 'C' + year + '_FAMMONO']], communes_select[['COM','DEP']],  on='COM', how='left')
        df_departement = df_dpt.loc[df_dpt["DEP"]==departement, ['DEP', 'COM','C'+ year +'_FAM' , 'C'+ year + '_FAMMONO']]
        familles = df_departement.loc[:, 'C'+ year + '_FAM']
        familles_mono = df_departement.loc[:, 'C'+ year + '_FAMMONO']
        df_familles = pd.DataFrame(data=familles)
        df_familles_mono = pd.DataFrame(data=familles_mono)
        Somme_familles = df_familles.sum(axis = 0, skipna = True)
        Somme_familles_mono = df_familles_mono.sum(axis = 0, skipna = True)
        val_familles = Somme_familles.values[0]
        val_familles_mono = Somme_familles_mono.values[0]
        part_familles_mono = round((val_familles_mono / val_familles)*100,2)
        df_Part_familles_mono = pd.DataFrame(data=part_familles_mono, columns = ['Part des familles monoparentales ' + annee], index = [nom_departement])
        return df_Part_familles_mono

    if int(select_annee) < 2017:
        valeurs_fam_mono_dep = part_fam_mono_departement_M2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_departement,select_annee)
    else :
        valeurs_fam_mono_dep = part_fam_mono_departement_P2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_departement,select_annee)

    # Région
    #si année de 2014 à 2016 (inclus)
    def part_fam_mono_region_M2017(fichier, region, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        df_regions = df.loc[df["REG"]==str(region), 'C'+ year +'_FAM' : 'C'+ year + '_FAMMONO']
        familles = df_regions.loc[:, 'C'+ year + '_FAM']
        familles_mono = df_regions.loc[:, 'C'+ year + '_FAMMONO']
        df_familles = pd.DataFrame(data=familles)
        df_familles_mono = pd.DataFrame(data=familles_mono)
        Somme_familles = df_familles.sum(axis = 0, skipna = True)
        Somme_familles_mono = df_familles_mono.sum(axis = 0, skipna = True)
        val_familles = Somme_familles.values[0]
        val_familles_mono = Somme_familles_mono.values[0]
        part_familles_mono = round((val_familles_mono / val_familles)*100,0)
        df_Part_familles_mono = pd.DataFrame(data=part_familles_mono, columns = ['Part des familles monoparentales ' + annee], index = [nom_region])
        return df_Part_familles_mono

    #si année de 2017 à ... (inclus)
    def part_fam_mono_region_P2017(fichier, region, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, encoding= 'unicode_escape', sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_regions = pd.merge(df[['COM', 'C' + year +'_FAM', 'C' + year + '_FAMMONO']], communes_select[['COM','REG']],  on='COM', how='left')
        df_region = df_regions.loc[df_regions["REG"]==str(region), ['REG', 'COM','C'+ year +'_FAM' , 'C'+ year + '_FAMMONO']]
        familles = df_region.loc[:, 'C'+ year + '_FAM']
        familles_mono = df_region.loc[:, 'C'+ year + '_FAMMONO']
        df_familles = pd.DataFrame(data=familles)
        df_familles_mono = pd.DataFrame(data=familles_mono)
        Somme_familles = df_familles.sum(axis = 0, skipna = True)
        Somme_familles_mono = df_familles_mono.sum(axis = 0, skipna = True)
        val_familles = Somme_familles.values[0]
        val_familles_mono =Somme_familles_mono.values[0]
        part_familles_mono = round((val_familles_mono / val_familles)*100,2)
        df_Part_familles_mono = pd.DataFrame(data=part_familles_mono, columns = ['Part des familles monoparentales ' + annee], index = [nom_region])
        return df_Part_familles_mono

    if int(select_annee) < 2017:
        valeurs_fam_mono_reg = part_fam_mono_region_M2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",str(round(code_region)),select_annee)
    else :
        valeurs_fam_mono_reg = part_fam_mono_region_P2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",str(round(code_region)),select_annee)

    # France
    def part_fam_mono_France(fichier, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        familles = df.loc[:, 'C'+ year + '_FAM']
        familles_mono = df.loc[:, 'C'+ year + '_FAMMONO']
        df_familles = pd.DataFrame(data=familles)
        df_familles_mono = pd.DataFrame(data=familles_mono)
        Somme_familles = df_familles.sum(axis = 0, skipna = True)
        Somme_familles_mono = df_familles_mono.sum(axis = 0, skipna = True)
        val_familles = Somme_familles.values[0]
        val_familles_mono = Somme_familles_mono.values[0]
        part_familles_mono = round((val_familles_mono / val_familles)*100, 2)
        df_Part_familles_mono = pd.DataFrame(data=part_familles_mono, columns = ['Part des familles monoparentales ' + annee], index = ["France"])
        return df_Part_familles_mono

    valeur_part_fam_mono_fr = part_fam_mono_France("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",select_annee)

    # Comparaison
    def fam_mono_global(annee):
        df = pd.concat([indice_fam_mono_com,indice_fam_mono_epci, valeurs_fam_mono_dep, valeurs_fam_mono_reg, valeur_part_fam_mono_fr])
        year = annee
        return df

    fam_mono_fin = fam_mono_global(select_annee)
    st.table(fam_mono_fin)

    @st.cache
    def convert_df(df):
      # IMPORTANT: Cache the conversion to prevent computation on every rerun
      return df.to_csv().encode('utf-8')

    csv = convert_df(fam_mono_fin)

    st.download_button(
      label="💾 Télécharger les données",
      data=csv,
      file_name='fam_monop_comparaison.csv',
      mime='text/csv',
    )

  st.subheader("b.Evolution")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    #FRANCE
    #2014
    valeur_part_fam_mono_fr_2014 = part_fam_mono_France("./famille/base-ic-couples-familles-menages-2014.csv",'2014')
    indice_2014 = valeur_part_fam_mono_fr_2014['Part des familles monoparentales 2014'][0]
    #2015
    valeur_part_fam_mono_fr_2015 = part_fam_mono_France("./famille/base-ic-couples-familles-menages-2015.csv",'2015')
    indice_2015 = valeur_part_fam_mono_fr_2015['Part des familles monoparentales 2015'][0]
    #2016
    valeur_part_fam_mono_fr_2016 = part_fam_mono_France("./famille/base-ic-couples-familles-menages-2016.csv",'2016')
    indice_2016 = valeur_part_fam_mono_fr_2016['Part des familles monoparentales 2016'][0]
    #2017
    valeur_part_fam_mono_fr_2017 = part_fam_mono_France("./famille/base-ic-couples-familles-menages-2017.csv",'2017')
    indice_2017 = valeur_part_fam_mono_fr_2017['Part des familles monoparentales 2017'][0]
    #2018
    valeur_part_fam_mono_fr_2018 = part_fam_mono_France("./famille/base-ic-couples-familles-menages-2018.csv",'2018')
    indice_2018 = valeur_part_fam_mono_fr_2018['Part des familles monoparentales 2018'][0]

    df_france_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=['France'])

    #RÉGION
    #2014
    valeur_part_fam_mono_region_2014 = part_fam_mono_region_M2017("./famille/base-ic-couples-familles-menages-2014.csv",str(round(code_region)),'2014')
    indice_2014 = valeur_part_fam_mono_region_2014['Part des familles monoparentales 2014'][0]
    #2015
    valeur_part_fam_mono_region_2015 = part_fam_mono_region_M2017("./famille/base-ic-couples-familles-menages-2015.csv",str(round(code_region)),'2015')
    indice_2015 = valeur_part_fam_mono_region_2015['Part des familles monoparentales 2015'][0]
    #2016
    valeur_part_fam_mono_region_2016 = part_fam_mono_region_M2017("./famille/base-ic-couples-familles-menages-2016.csv",str(round(code_region)),'2016')
    indice_2016 = valeur_part_fam_mono_region_2016['Part des familles monoparentales 2016'][0]
    #2017
    valeur_part_fam_mono_region_2017 = part_fam_mono_region_P2017("./famille/base-ic-couples-familles-menages-2017.csv",str(round(code_region)),'2017')
    indice_2017 = valeur_part_fam_mono_region_2017['Part des familles monoparentales 2017'][0]
    #2018
    valeur_part_fam_mono_region_2018 = part_fam_mono_region_P2017("./famille/base-ic-couples-familles-menages-2018.csv",str(round(code_region)),'2018')
    indice_2018 = valeur_part_fam_mono_region_2018['Part des familles monoparentales 2018'][0]

    df_region_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_region])

    #DÉPARTEMENT
    #2014
    valeur_part_fam_mono_departement_2014 = part_fam_mono_departement_M2017("./famille/base-ic-couples-familles-menages-2014.csv",code_departement,'2014')
    indice_2014 = valeur_part_fam_mono_departement_2014['Part des familles monoparentales 2014'][0]
    #2015
    valeur_part_fam_mono_departement_2015 = part_fam_mono_departement_M2017("./famille/base-ic-couples-familles-menages-2015.csv",code_departement,'2015')
    indice_2015 = valeur_part_fam_mono_departement_2015['Part des familles monoparentales 2015'][0]
    #2016
    valeur_part_fam_mono_departement_2016 = part_fam_mono_departement_M2017("./famille/base-ic-couples-familles-menages-2016.csv",code_departement,'2016')
    indice_2016 = valeur_part_fam_mono_departement_2016['Part des familles monoparentales 2016'][0]
    #2017
    valeur_part_fam_mono_departement_2017 = part_fam_mono_departement_P2017("./famille/base-ic-couples-familles-menages-2017.csv",code_departement,'2017')
    indice_2017 = valeur_part_fam_mono_departement_2017['Part des familles monoparentales 2017'][0]
    #2018
    valeur_part_fam_mono_departement_2018 = part_fam_mono_departement_P2017("./famille/base-ic-couples-familles-menages-2018.csv",code_departement,'2018')
    indice_2017 = valeur_part_fam_mono_departement_2018['Part des familles monoparentales 2018'][0]

    df_departement_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_departement])

    #EPCI
    #2014
    valeur_part_fam_mono_epci_2014 = part_fam_mono_epci("./famille/base-ic-couples-familles-menages-2014.csv",code_epci,'2014')
    indice_2014 = valeur_part_fam_mono_epci_2014['Part des familles monoparentales 2014'][0]
    #2015
    valeur_part_fam_mono_epci_2015 = part_fam_mono_epci("./famille/base-ic-couples-familles-menages-2015.csv",code_epci,'2015')
    indice_2015 = valeur_part_fam_mono_epci_2015['Part des familles monoparentales 2015'][0]
    #2016
    valeur_part_fam_mono_epci_2016 = part_fam_mono_epci("./famille/base-ic-couples-familles-menages-2016.csv",code_epci,'2016')
    indice_2016 = valeur_part_fam_mono_epci_2016['Part des familles monoparentales 2016'][0]
    #2017
    valeur_part_fam_mono_epci_2017 = part_fam_mono_epci("./famille/base-ic-couples-familles-menages-2017.csv",code_epci,'2017')
    indice_2017 = valeur_part_fam_mono_epci_2017['Part des familles monoparentales 2017'][0]
    #2018
    valeur_part_fam_mono_epci_2018 = part_fam_mono_epci("./famille/base-ic-couples-familles-menages-2018.csv",code_epci,'2018')
    indice_2018 = valeur_part_fam_mono_epci_2018['Part des familles monoparentales 2018'][0]

    df_epci_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_epci])

    #COMMUNE
    #2014
    valeur_part_fam_mono_commune_2014 = part_fam_mono_com("./famille/base-ic-couples-familles-menages-2014.csv",code_commune,'2014')
    indice_2014 = valeur_part_fam_mono_commune_2014['Part des familles monoparentales 2014'][0]
    #2015
    valeur_part_fam_mono_commune_2015 = part_fam_mono_com("./famille/base-ic-couples-familles-menages-2015.csv",code_commune,'2015')
    indice_2015 = valeur_part_fam_mono_commune_2015['Part des familles monoparentales 2015'][0]
    #2016
    valeur_part_fam_mono_commune_2016 = part_fam_mono_com("./famille/base-ic-couples-familles-menages-2016.csv",code_commune,'2016')
    indice_2016 = valeur_part_fam_mono_commune_2016['Part des familles monoparentales 2016'][0]
    #2017
    valeur_part_fam_mono_commune_2017 = part_fam_mono_com("./famille/base-ic-couples-familles-menages-2017.csv",code_commune,'2017')
    indice_2017 = valeur_part_fam_mono_commune_2017['Part des familles monoparentales 2017'][0]
    #2018
    valeur_part_fam_mono_commune_2018 = part_fam_mono_com("./famille/base-ic-couples-familles-menages-2018.csv",code_commune,'2018')
    indice_2018 = valeur_part_fam_mono_commune_2018['Part des familles monoparentales 2018'][0]

    df_commune_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_commune])

    df_glob_fam_monop = pd.concat([df_france_glob, df_region_glob, df_departement_glob, df_epci_glob, df_commune_glob])

    st.table(df_glob_fam_monop)

    df_glob_fam_monop_transposed = df_glob_fam_monop.T
    st.line_chart(df_glob_fam_monop_transposed)

  st.header('2.Part des familles nombreuses')

  st.subheader("Iris")
  def part_fam_nombreuses_iris(fichier, code, annee) :
    df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, encoding= 'unicode_escape', sep=";", header=0)
    df_indice = df.loc[df['COM'] == code]
    year = annee[-2:]
    df_indice = df_indice[['COM','IRIS', 'C'+ year + '_NE24F3', 'C'+ year + '_NE24F4P','C' + year +'_FAM' ]]
    df_indice = df_indice.replace(',','.', regex=True)
    df_indice['C'+ year + '_FAM'] = df_indice['C'+ year + '_FAM'].astype(float).to_numpy()
    df_indice['C' + year +'_NE24F3'] = df_indice['C' + year +'_NE24F3'].astype(float).to_numpy()
    df_indice['C' + year +'_NE24F4P'] = df_indice['C' + year +'_NE24F4P'].astype(float).to_numpy()
    df_indice['indice'] = np.where(df_indice['C' + year +'_FAM'] < 1,df_indice['C' + year +'_FAM'], ((df_indice['C'+ year + '_NE24F3'] + df_indice['C'+ year + '_NE24F4P'])/ df_indice['C' + year +'_FAM']*100))
    df_indice['indice'] = df_indice['indice'].astype(float).to_numpy()
    communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
    df_indice_com = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df_indice[['IRIS','C' + year +'_FAM', 'C' + year + '_NE24F3','C'+ year + '_NE24F4P','indice']], left_on='CODE_IRIS', right_on="IRIS")
    df_indice_com = df_indice_com[['CODE_IRIS','LIB_IRIS','C' + year +'_FAM', 'C' + year + '_NE24F3','C'+ year + '_NE24F4P','indice']]
    #df_indice_com['indice'] = df_indice_com['indice'].apply(np.int64)
    df_indice_com['C' + year +'_FAM'] = df_indice_com['C' + year +'_FAM'].apply(np.int64)
    df_indice_com['C' + year +'_NE24F3'] = df_indice_com['C' + year +'_NE24F3'].apply(np.int64)
    df_indice_com['C' + year +'_NE24F4P'] = df_indice_com['C' + year +'_NE24F4P'].apply(np.int64)
    df_indice_com = df_indice_com.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'C' + year +'_NE24F3':"Familles nombreuses 3 enfants (" + select_annee + ")", 'C' + year +'_NE24F4P':"Familles nombreuses 4 enfants et + (" + select_annee + ")" ,'C' + year + '_FAM':"Familles (" + select_annee + ")" ,'indice':"Part des familles nombreuses (" + select_annee + ") en %" })
    return df_indice_com
  indice_part_fam_nombreuses_iris =part_fam_nombreuses_iris("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_commune, select_annee)
  with st.expander("Visualiser le tableau des iris"):
    st.table(indice_part_fam_nombreuses_iris)

  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(indice_part_fam_nombreuses_iris)

  st.download_button(
    label="💾 Télécharger les données",
    data=csv,
    file_name='fam_nombreuses_iris.csv',
    mime='text/csv',
  )

  st.subheader("a.Comparaison sur une année")
  st.caption("Une famille est dite nombreuse lorsqu'elle comprend trois enfants ou plus - définition INSEE")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    # Commune
    def part_fam_nombreuses_com(fichier, code_commune, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        df_ville = df.loc[df["COM"]==code_commune,]
        nom_ville = df_ville.loc[df["COM"]==code_commune, 'COM']
        familles = df_ville.loc[:, 'C'+ year + '_FAM'].astype(float).sum(axis = 0, skipna = True)
        familles_nombreuses = (df_ville.loc[:, 'C'+ year + '_NE24F3'].astype(float).sum(axis = 0, skipna = True)) + (df_ville.loc[:, 'C'+ year + '_NE24F4P'].astype(float).sum(axis = 0, skipna = True))
        part_fam_nombreuses = round((familles_nombreuses / familles)*100,2)
        df_Part_fam_nombreuses = pd.DataFrame(data=part_fam_nombreuses, columns = ['Part des familles nombreuses ' + annee], index = [nom_commune])
        return df_Part_fam_nombreuses
    indice_fam_nombreuses_com = part_fam_nombreuses_com("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_commune, select_annee)

    # EPCI
    def part_fam_nombreuses_epci(fichier, epci, annee):
        epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "TYP_IRIS": str, "MODIF_IRIS": str,"COM": str, "LAB_IRIS": str, "DEP": str, "UU2010": str, "GRD_QUART": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        df_epci_com = pd.merge(df[['COM', 'C' + year + '_FAM', 'C' + year + '_NE24F3', 'C' + year + '_NE24F4P']], epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
        df_epci = df_epci_com.loc[df_epci_com["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM','C'+ year +'_FAM' , 'C'+ year + '_NE24F3' , 'C'+ year + '_NE24F4P']]
        familles = df_epci.loc[:, 'C'+ year + '_FAM'].sum(axis = 0, skipna = True)
        familles_nombreuses = (df_epci.loc[:, 'C'+ year + '_NE24F3'].astype(float).sum(axis = 0, skipna = True)) + (df_epci.loc[:, 'C'+ year + '_NE24F4P'].astype(float).sum(axis = 0, skipna = True))
        part_familles_nombreuses = round((familles_nombreuses / familles)*100,2)
        df_part_familles_nombreuses = pd.DataFrame(data=part_familles_nombreuses, columns = ['Part des familles nombreuses ' + annee], index = [nom_epci])
        return df_part_familles_nombreuses
    indice_fam_nombreuses_epci = part_fam_nombreuses_epci("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_epci,select_annee)


    # Département
    def part_fam_nombreuses_departement_M2017(fichier, departement, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape',sep = ';')
        year = annee[-2:]
        df_departement = df.loc[df["DEP"]==departement, 'C'+ year +'_FAM' : 'C'+ year + '_NE24F4P']
        familles = df_departement.loc[:, 'C'+ year + '_FAM'].sum(axis = 0, skipna = True)
        familles_nombreuses = (df_departement.loc[:, 'C'+ year + '_NE24F3'].astype(float).sum(axis = 0, skipna = True)) + (df_departement.loc[:, 'C'+ year + '_NE24F4P'].astype(float).sum(axis = 0, skipna = True))
        part_familles_nombreuses = round((familles_nombreuses / familles)*100,2)
        df_Part_familles_nombreuses = pd.DataFrame(data=part_familles_nombreuses, columns = ['Part des familles nombreuses ' + annee], index = [nom_departement])
        return df_Part_familles_nombreuses

    def part_fam_nombreuses_departement_P2017(fichier, departement, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, encoding= 'unicode_escape',sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_dpt = pd.merge(df[['COM', 'C' + year +'_FAM', 'C' + year + '_NE24F3', 'C' + year + '_NE24F4P']], communes_select[['COM','DEP']],  on='COM', how='left')
        df_departement = df_dpt.loc[df_dpt["DEP"]==departement, ['DEP', 'COM','C'+ year +'_FAM' , 'C'+ year + '_NE24F3', 'C'+ year + '_NE24F4P']]
        familles = df_departement.loc[:, 'C'+ year + '_FAM'].sum(axis = 0, skipna = True)
        familles_nombreuses = (df_departement.loc[:, 'C'+ year + '_NE24F3'].astype(float).sum(axis = 0, skipna = True)) + (df_departement.loc[:, 'C'+ year + '_NE24F4P'].astype(float).sum(axis = 0, skipna = True))
        part_familles_nombreuses = round((familles_nombreuses / familles)*100,2)
        df_part_familles_nombreuses = pd.DataFrame(data=part_familles_nombreuses, columns = ['Part des familles nombreuses ' + annee], index = [nom_departement])
        return df_part_familles_nombreuses

    if int(select_annee) < 2017:
        valeurs_fam_nombreuses_dep = part_fam_nombreuses_departement_M2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_departement,select_annee)
    else :
        valeurs_fam_nombreuses_dep = part_fam_nombreuses_departement_P2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",code_departement,select_annee)

    # Région
    #si année de 2014 à 2016 (inclus)
    def part_fam_nombreuses_region_M2017(fichier, region, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        df_regions = df.loc[df["REG"]==str(region), 'C'+ year +'_FAM' : 'C'+ year + '_NE24F4P']
        familles = df_regions.loc[:, 'C'+ year + '_FAM'].sum(axis = 0, skipna = True)
        familles_nombreuses = (df_regions.loc[:, 'C'+ year + '_NE24F3'].astype(float).sum(axis = 0, skipna = True)) + (df_regions.loc[:, 'C'+ year + '_NE24F4P'].astype(float).sum(axis = 0, skipna = True))
        part_familles_nombreuses = round((familles_nombreuses / familles)*100,0)
        df_part_familles_nombreuses = pd.DataFrame(data=part_familles_nombreuses, columns = ['Part des familles nombreuses ' + annee], index = [nom_region])
        return df_part_familles_nombreuses

    #si année de 2017 à ... (inclus)
    def part_fam_nombreuses_region_P2017(fichier, region, annee):
        communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, encoding= 'unicode_escape', sep = ',')
        df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
        year = annee[-2:]
        df_regions = pd.merge(df[['COM', 'C' + year +'_FAM', 'C' + year + '_NE24F3', 'C' + year + '_NE24F4P']], communes_select[['COM','REG']],  on='COM', how='left')
        df_region = df_regions.loc[df_regions["REG"]==str(region), ['REG', 'COM','C'+ year +'_FAM' , 'C'+ year + '_NE24F3', 'C'+ year + '_NE24F4P']]
        familles = df_region.loc[:, 'C'+ year + '_FAM'].sum(axis = 0, skipna = True)
        familles_nombreuses = (df_region.loc[:, 'C'+ year + '_NE24F3'].astype(float).sum(axis = 0, skipna = True)) + (df_region.loc[:, 'C'+ year + '_NE24F4P'].astype(float).sum(axis = 0, skipna = True))
        part_familles_nombreuses = round((familles_nombreuses / familles)*100,2)
        df_part_familles_nombreuses = pd.DataFrame(data=part_familles_nombreuses, columns = ['Part des familles nombreuses ' + annee], index = [nom_region])
        return df_part_familles_nombreuses

    if int(select_annee) < 2017:
        valeurs_fam_nombreuses_reg = part_fam_nombreuses_region_M2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",str(round(code_region)),select_annee)
    else :
        valeurs_fam_nombreuses_reg = part_fam_nombreuses_region_P2017("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",str(round(code_region)),select_annee)

    # France
    def part_fam_nombreuses_France(fichier, annee):
        df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, encoding= 'unicode_escape', sep = ';')
        year = annee[-2:]
        familles = df.loc[:, 'C'+ year + '_FAM']
        familles_nombreuses = df.loc[:, 'C'+ year + '_NE24F3' : 'C'+ year + '_NE24F4P']
        Somme_familles = familles.sum(axis = 0, skipna = True)
        Somme_familles_nombreuses = (familles_nombreuses.loc[:, 'C'+ year + '_NE24F3'].astype(float).sum(axis = 0, skipna = True)) + (familles_nombreuses.loc[:, 'C'+ year + '_NE24F4P'].astype(float).sum(axis = 0, skipna = True))
        part_familles_nombreuses = round((Somme_familles_nombreuses / Somme_familles)*100, 2)
        df_part_familles_nombreuses = pd.DataFrame(data=part_familles_nombreuses, columns = ['Part des familles nombreuses ' + annee], index = ["France"])
        return df_part_familles_nombreuses

    valeur_part_fam_nombreuses_fr = part_fam_nombreuses_France("./famille/base-ic-couples-familles-menages-" + select_annee + ".csv",select_annee)


    # Comparaison
    def fam_nombreuses_global(annee):
        df = pd.concat([indice_fam_nombreuses_com,indice_fam_nombreuses_epci, valeurs_fam_nombreuses_dep, valeurs_fam_nombreuses_reg, valeur_part_fam_nombreuses_fr])
        year = annee
        return df

    fam_nombreuses_fin = fam_nombreuses_global(select_annee)
    st.table(fam_nombreuses_fin)

    @st.cache
    def convert_df(df):
      # IMPORTANT: Cache the conversion to prevent computation on every rerun
      return df.to_csv().encode('utf-8')

    csv = convert_df(fam_nombreuses_fin)

    st.download_button(
      label="💾 Télécharger les données",
      data=csv,
      file_name='fam_nombreuses_comparaison.csv',
      mime='text/csv',
    )

  st.subheader("b.Evolution")
  with st.spinner('Nous générons votre tableau de données personnalisé...'):
    #FRANCE
    #2014
    valeur_part_fam_nombreuses_fr_2014 = part_fam_nombreuses_France("./famille/base-ic-couples-familles-menages-2014.csv",'2014')
    indice_2014 = valeur_part_fam_nombreuses_fr_2014['Part des familles nombreuses 2014'][0]
    #2015
    valeur_part_fam_nombreuses_fr_2015 = part_fam_nombreuses_France("./famille/base-ic-couples-familles-menages-2015.csv",'2015')
    indice_2015 = valeur_part_fam_nombreuses_fr_2015['Part des familles nombreuses 2015'][0]
    #2016
    valeur_part_fam_nombreuses_fr_2016 = part_fam_nombreuses_France("./famille/base-ic-couples-familles-menages-2016.csv",'2016')
    indice_2016 = valeur_part_fam_nombreuses_fr_2016['Part des familles nombreuses 2016'][0]
    #2017
    valeur_part_fam_nombreuses_fr_2017 = part_fam_nombreuses_France("./famille/base-ic-couples-familles-menages-2017.csv",'2017')
    indice_2017 = valeur_part_fam_nombreuses_fr_2017['Part des familles nombreuses 2017'][0]
    #2018
    valeur_part_fam_nombreuses_fr_2018 = part_fam_nombreuses_France("./famille/base-ic-couples-familles-menages-2018.csv",'2018')
    indice_2018 = valeur_part_fam_nombreuses_fr_2018['Part des familles nombreuses 2018'][0]
    df_france_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=['France'])

    #RÉGION
    #2014
    valeur_part_fam_nombreuses_region_2014 = part_fam_nombreuses_region_M2017("./famille/base-ic-couples-familles-menages-2014.csv",str(round(code_region)),'2014')
    indice_2014 = valeur_part_fam_nombreuses_region_2014['Part des familles nombreuses 2014'][0]
    #2015
    valeur_part_fam_nombreuses_region_2015 = part_fam_nombreuses_region_M2017("./famille/base-ic-couples-familles-menages-2015.csv",str(round(code_region)),'2015')
    indice_2015 = valeur_part_fam_nombreuses_region_2015['Part des familles nombreuses 2015'][0]
    #2016
    valeur_part_fam_nombreuses_region_2016 = part_fam_nombreuses_region_M2017("./famille/base-ic-couples-familles-menages-2016.csv",str(round(code_region)),'2016')
    indice_2016 = valeur_part_fam_nombreuses_region_2016['Part des familles nombreuses 2016'][0]
    #2017
    valeur_part_fam_nombreuses_region_2017 = part_fam_nombreuses_region_P2017("./famille/base-ic-couples-familles-menages-2017.csv",str(round(code_region)),'2017')
    indice_2017 = valeur_part_fam_nombreuses_region_2017['Part des familles nombreuses 2017'][0]
    #2018
    valeur_part_fam_nombreuses_region_2018 = part_fam_nombreuses_region_P2017("./famille/base-ic-couples-familles-menages-2018.csv",str(round(code_region)),'2018')
    indice_2018 = valeur_part_fam_nombreuses_region_2018['Part des familles nombreuses 2018'][0]
    df_region_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_region])

    #DÉPARTEMENT
    #2014
    valeur_part_fam_nombreuses_departement_2014 = part_fam_nombreuses_departement_M2017("./famille/base-ic-couples-familles-menages-2014.csv",code_departement,'2014')
    indice_2014 = valeur_part_fam_nombreuses_departement_2014['Part des familles nombreuses 2014'][0]
    #2015
    valeur_part_fam_nombreuses_departement_2015 = part_fam_nombreuses_departement_M2017("./famille/base-ic-couples-familles-menages-2015.csv",code_departement,'2015')
    indice_2015 = valeur_part_fam_nombreuses_departement_2015['Part des familles nombreuses 2015'][0]
    #2016
    valeur_part_fam_nombreuses_departement_2016 = part_fam_nombreuses_departement_M2017("./famille/base-ic-couples-familles-menages-2016.csv",code_departement,'2016')
    indice_2016 = valeur_part_fam_nombreuses_departement_2016['Part des familles nombreuses 2016'][0]
    #2017
    valeur_part_fam_nombreuses_departement_2017 = part_fam_nombreuses_departement_P2017("./famille/base-ic-couples-familles-menages-2017.csv",code_departement,'2017')
    indice_2017 = valeur_part_fam_nombreuses_departement_2017['Part des familles nombreuses 2017'][0]
    #2018
    valeur_part_fam_nombreuses_departement_2018 = part_fam_nombreuses_departement_P2017("./famille/base-ic-couples-familles-menages-2018.csv",code_departement,'2018')
    indice_2018 = valeur_part_fam_nombreuses_departement_2018['Part des familles nombreuses 2018'][0]

    df_departement_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_departement])

    #EPCI
    #2014
    valeur_part_fam_nombreuses_epci_2014 = part_fam_nombreuses_epci("./famille/base-ic-couples-familles-menages-2014.csv",code_epci,'2014')
    indice_2014 = valeur_part_fam_nombreuses_epci_2014['Part des familles nombreuses 2014'][0]
    #2015
    valeur_part_fam_nombreuses_epci_2015 = part_fam_nombreuses_epci("./famille/base-ic-couples-familles-menages-2015.csv",code_epci,'2015')
    indice_2015 = valeur_part_fam_nombreuses_epci_2015['Part des familles nombreuses 2015'][0]
    #2016
    valeur_part_fam_nombreuses_epci_2016 = part_fam_nombreuses_epci("./famille/base-ic-couples-familles-menages-2016.csv",code_epci,'2016')
    indice_2016 = valeur_part_fam_nombreuses_epci_2016['Part des familles nombreuses 2016'][0]
    #2017
    valeur_part_fam_nombreuses_epci_2017 = part_fam_nombreuses_epci("./famille/base-ic-couples-familles-menages-2017.csv",code_epci,'2017')
    indice_2017 = valeur_part_fam_nombreuses_epci_2017['Part des familles nombreuses 2017'][0]
    #2018
    valeur_part_fam_nombreuses_epci_2018 = part_fam_nombreuses_epci("./famille/base-ic-couples-familles-menages-2018.csv",code_epci,'2018')
    indice_2018 = valeur_part_fam_nombreuses_epci_2018['Part des familles nombreuses 2018'][0]

    df_epci_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_epci])

    #COMMUNE
    #2014
    valeur_part_fam_nombreuses_commune_2014 = part_fam_nombreuses_com("./famille/base-ic-couples-familles-menages-2014.csv",code_commune,'2014')
    indice_2014 = valeur_part_fam_nombreuses_commune_2014['Part des familles nombreuses 2014'][0]
    #2015
    valeur_part_fam_nombreuses_commune_2015 = part_fam_nombreuses_com("./famille/base-ic-couples-familles-menages-2015.csv",code_commune,'2015')
    indice_2015 = valeur_part_fam_nombreuses_commune_2015['Part des familles nombreuses 2015'][0]
    #2016
    valeur_part_fam_nombreuses_commune_2016 = part_fam_nombreuses_com("./famille/base-ic-couples-familles-menages-2016.csv",code_commune,'2016')
    indice_2016 = valeur_part_fam_nombreuses_commune_2016['Part des familles nombreuses 2016'][0]
    #2017
    valeur_part_fam_nombreuses_commune_2017 = part_fam_nombreuses_com("./famille/base-ic-couples-familles-menages-2017.csv",code_commune,'2017')
    indice_2017 = valeur_part_fam_nombreuses_commune_2017['Part des familles nombreuses 2017'][0]
    #2018
    valeur_part_fam_nombreuses_commune_2018 = part_fam_nombreuses_com("./famille/base-ic-couples-familles-menages-2018.csv",code_commune,'2018')
    indice_2018 = valeur_part_fam_nombreuses_commune_2018['Part des familles nombreuses 2018'][0]

    df_commune_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                       columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_commune])

    df_glob_fam_nombreuses = pd.concat([df_france_glob, df_region_glob, df_departement_glob, df_epci_glob, df_commune_glob])

    st.table(df_glob_fam_nombreuses)

    df_glob_fam_nombreuses_transposed = df_glob_fam_nombreuses.T
    st.line_chart(df_glob_fam_nombreuses_transposed)

    ########################################################################
    st.subheader('Taille moyenne des ménages')
    def taille_moyen_menages_iris(fichier, ville, annee) :
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, sep=";")
      df = df.loc[df['COM'] == ville]
      year = annee[-2:]
      df = df[['COM','IRIS', 'P'+ year + '_NPER_RP', 'P'+ year + '_RP' ]]
      communes_select = pd.read_csv('./iris_2021.csv', dtype={"CODE_IRIS": str, "GRD_QUART": str, "DEPCOM": str, "UU2020": str, "REG": str, "DEP": str}, sep = ';')
      df_nb_pers_resid = pd.merge(communes_select[['CODE_IRIS','LIB_IRIS']], df[['IRIS','P'+ year + '_NPER_RP','P'+ year + '_RP']], left_on='CODE_IRIS', right_on="IRIS")
      df_nb_pers_resid['indice'] = df_nb_pers_resid['P'+ year + '_NPER_RP'] / df_nb_pers_resid['P'+ year + '_RP']
      df_nb_pers_resid = df_nb_pers_resid[['CODE_IRIS', 'LIB_IRIS', 'P'+ year + '_NPER_RP', 'P'+ year + '_RP', 'indice' ]]
      df_nb_pers_resid = df_nb_pers_resid.rename(columns={'CODE_IRIS': "Code de l'iris",'LIB_IRIS': "Nom de l'iris", 'P' + year +'_RP':"Résidences principales (" + select_annee + ")" ,'P' + year + '_NPER_RP':"Nombre de personnes des résidences principales (" + select_annee + ")" ,'indice':"Taille moyenne des ménages (" + select_annee + ")" })
      return df_nb_pers_resid
    taille_menages = taille_moyen_menages_iris("./logement/base-ic-logement-" + select_annee + ".csv", code_commune, select_annee )
    st.write(taille_menages)

    ########################################################################
    st.subheader("Les ménages d'une personne")
