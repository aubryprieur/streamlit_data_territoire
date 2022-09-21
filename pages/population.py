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
import plotly.express as px

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
  st.title("POPULATION")
  st.header('1.Evolution de la population')

  ville = code_commune
  df_pop_hist = pd.read_csv('./population/base-cc-serie-historique-2019.csv', dtype={"CODGEO": str},sep=";")
  df_pop_hist_ville = df_pop_hist.loc[df_pop_hist["CODGEO"]==code_commune]
  df_pop_hist_ville = df_pop_hist_ville.reset_index()
  df_pop_hist_ville = df_pop_hist_ville.loc[:, 'P19_POP' : 'D68_POP']
  df_pop_hist_ville = df_pop_hist_ville.rename(columns={'P19_POP': '2019','P13_POP': '2013','P08_POP': '2008','D99_POP': '1999','D90_POP': '1990','D82_POP': '1982','D75_POP': '1975','D68_POP': '1968' })
  dt_test = df_pop_hist_ville.T
  df_pop_hist_ville.insert(0, 'Commune', nom_commune)
  st.table(df_pop_hist_ville)
  #Télécharger les données
  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(df_pop_hist_ville)

  st.download_button(
       label="💾 Télécharger les données",
       data=csv,
       file_name='evolution_population.csv',
       mime='text/csv',
   )
  # Chart
  st.area_chart(data=dt_test, height=300, use_container_width=True)

  #Indicateurs clés
  evol_68_19 = df_pop_hist_ville.iloc[0]["2019"] - df_pop_hist_ville.iloc[0]["1968"]
  st.metric(label="Population 2019", value='{:,.0f}'.format(df_pop_hist_ville.iloc[0]["2019"]).replace(",", " "), delta=str('{:,.0f}'.format(evol_68_19.item()).replace(",", " ")) + " hab. depuis 1968")

  ##########################################################################

  ############################################################################
  st.header("2.Répartition de la population par tranches d'âge")
  st.subheader('Comparaison entre iris')
  #P18_POP0014 P18_POP1529 P18_POP3044 P18_POP4559 P18_POP6074 P18_POP75P
  df = pd.read_csv("./population/base-ic-evol-struct-pop-" + select_annee + ".csv", dtype={"IRIS": str , "COM": str},sep=";")
  year = select_annee[-2:]
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

  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(df_tranche_age_iris)

  st.download_button(
       label="💾 Télécharger les données",
       data=csv,
       file_name='tranches_ages.csv',
       mime='text/csv',
      )

  fig = px.bar(df_tranche_age_iris, x="Nom de l'iris", y=["00-14 ans","15-29 ans", "30-44 ans", "45-59 ans" ,"60-74 ans" , "Plus de 75 ans"], title="Répartition de la population", height=600, width=800)
  st.plotly_chart(fig, use_container_width=False)

  #################
  st.subheader('Comparaison entre territoires')
  #Commune
  def tranche_age_com(fichier, commune, annee):
    df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "MODIF_IRIS" : str, "LAB_IRIS" : str}, sep = ';')
    year = annee[-2:]
    df = df.loc[df["COM"] == commune]
    df = df[["IRIS","P" + year +"_POP","P" + year +"_POP0014", "P" + year +"_POP1529", "P" + year +"_POP3044", "P" + year +"_POP4559", "P" + year +"_POP6074", "P" + year +"_POP75P"]]
    pop0014 = (df.loc[:, "P" + year +"_POP0014"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop1529 = (df.loc[:, "P" + year +"_POP1529"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop3044 = (df.loc[:, "P" + year +"_POP3044"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop4559 = (df.loc[:, "P" + year +"_POP4559"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop6074 = (df.loc[:, "P" + year +"_POP6074"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop75P = (df.loc[:, "P" + year +"_POP75P"].sum() / df["P" + year +"_POP"].sum()) * 100
    df_tranches_age_com = pd.DataFrame(data=[[nom_commune,pop0014,pop1529,pop3044,pop4559,pop6074,pop75P]], columns = ["territoire","pop0014","pop1529","pop3044", "pop4559","pop6074", "pop75P"])
    return df_tranches_age_com
  tranches_age_com = tranche_age_com("./population/base-ic-evol-struct-pop-" + select_annee + ".csv", code_commune, select_annee)

  #EPCI
  def tranche_age_epci(fichier, epci, annee):
    epci_select = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
    df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "MODIF_IRIS" : str, "LAB_IRIS" : str}, sep = ';')
    year = annee[-2:]
    df_epci = pd.merge(df, epci_select[['CODGEO','EPCI', 'LIBEPCI']], left_on='COM', right_on='CODGEO')
    df_epci = df_epci.loc[df_epci["EPCI"]==str(epci), ['EPCI', 'LIBEPCI', 'COM',"P" + year +"_POP", "P" + year +"_POP0014" , "P" + year +"_POP1529","P" + year +"_POP3044", "P" + year +"_POP4559","P" + year +"_POP6074","P" + year +"_POP75P"]]
    pop0014 = (df_epci.loc[:, "P" + year +"_POP0014"].sum() / df_epci["P" + year +"_POP"].sum()) * 100
    pop1529 = (df_epci.loc[:, "P" + year +"_POP1529"].sum() / df_epci["P" + year +"_POP"].sum()) * 100
    pop3044 = (df_epci.loc[:, "P" + year +"_POP3044"].sum() / df_epci["P" + year +"_POP"].sum()) * 100
    pop4559 = (df_epci.loc[:, "P" + year +"_POP4559"].sum() / df_epci["P" + year +"_POP"].sum()) * 100
    pop6074 = (df_epci.loc[:, "P" + year +"_POP6074"].sum() / df_epci["P" + year +"_POP"].sum()) * 100
    pop75P = (df_epci.loc[:, "P" + year +"_POP75P"].sum() / df_epci["P" + year +"_POP"].sum()) * 100
    df_tranches_age_epci = pd.DataFrame(data=[[nom_epci,pop0014,pop1529,pop3044,pop4559,pop6074,pop75P]], columns = ["territoire","pop0014","pop1529","pop3044", "pop4559","pop6074", "pop75P"])
    return df_tranches_age_epci
  tranches_age_epci = tranche_age_epci("./population/base-ic-evol-struct-pop-" + select_annee + ".csv", code_epci, select_annee)

  #Dpt
  def tranche_age_departement(fichier, departement, annee):
    if int(annee) >= 2017:
      communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str},sep = ',')
      df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
      year = annee[-2:]
      df_dpt = pd.merge(df, communes_select[['COM','DEP']],  on='COM', how='left')
      df_departement = df_dpt.loc[df_dpt["DEP"]==departement, ['DEP', 'COM',"P" + year +"_POP", "P" + year +"_POP0014" , "P" + year +"_POP1529","P" + year +"_POP3044", "P" + year +"_POP4559","P" + year +"_POP6074","P" + year +"_POP75P"]]
      pop0014 = (df_departement.loc[:, "P" + year +"_POP0014"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
      pop1529 = (df_departement.loc[:, "P" + year +"_POP1529"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
      pop3044 = (df_departement.loc[:, "P" + year +"_POP3044"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
      pop4559 = (df_departement.loc[:, "P" + year +"_POP4559"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
      pop6074 = (df_departement.loc[:, "P" + year +"_POP6074"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
      pop75P = (df_departement.loc[:, "P" + year +"_POP75P"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
      df_tranches_age_dpt = pd.DataFrame(data=[[nom_departement,pop0014,pop1529,pop3044,pop4559,pop6074,pop75P]], columns = ["territoire","pop0014","pop1529","pop3044", "pop4559","pop6074", "pop75P"])
      return df_tranches_age_dpt
    else:
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str},sep = ';')
      year = annee[-2:]
      df_departement = df.loc[df["DEP"]==departement, ["P" + year +"_POP", "P" + year +"_POP0014" , "P" + year +"_POP1529","P" + year +"_POP3044", "P" + year +"_POP4559","P" + year +"_POP6074","P" + year +"_POP75P"]]
      pop0014 = (df_departement.loc[:, "P" + year +"_POP0014"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
      pop1529 = (df_departement.loc[:, "P" + year +"_POP1529"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
      pop3044 = (df_departement.loc[:, "P" + year +"_POP3044"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
      pop4559 = (df_departement.loc[:, "P" + year +"_POP4559"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
      pop6074 = (df_departement.loc[:, "P" + year +"_POP6074"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
      pop75P = (df_departement.loc[:, "P" + year +"_POP75P"].sum() / df_departement["P" + year +"_POP"].sum()) * 100
      df_tranches_age_dpt = pd.DataFrame(data=[[nom_departement,pop0014,pop1529,pop3044,pop4559,pop6074,pop75P]], columns = ["territoire","pop0014","pop1529","pop3044", "pop4559","pop6074", "pop75P"])
      return df_tranches_age_dpt
  tranche_age_departement = tranche_age_departement("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_departement, select_annee)

  #Région
  def tranche_age_region(fichier, region, annee):
    if int(annee) >= 2017:
      communes_select = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str},sep = ',')
      df = pd.read_csv(fichier, dtype={"IRIS": str, "COM": str, "LAB_IRIS": str}, sep = ';')
      year = annee[-2:]
      df_region = pd.merge(df, communes_select[['COM','REG']],  on='COM', how='left')
      df_region = df_region.loc[df_region["REG"]== region, ['REG', 'COM',"P" + year +"_POP", "P" + year +"_POP0014" , "P" + year +"_POP1529","P" + year +"_POP3044", "P" + year +"_POP4559","P" + year +"_POP6074","P" + year +"_POP75P"]]
      pop0014 = (df_region.loc[:, "P" + year +"_POP0014"].sum() / df_region["P" + year +"_POP"].sum()) * 100
      pop1529 = (df_region.loc[:, "P" + year +"_POP1529"].sum() / df_region["P" + year +"_POP"].sum()) * 100
      pop3044 = (df_region.loc[:, "P" + year +"_POP3044"].sum() / df_region["P" + year +"_POP"].sum()) * 100
      pop4559 = (df_region.loc[:, "P" + year +"_POP4559"].sum() / df_region["P" + year +"_POP"].sum()) * 100
      pop6074 = (df_region.loc[:, "P" + year +"_POP6074"].sum() / df_region["P" + year +"_POP"].sum()) * 100
      pop75P = (df_region.loc[:, "P" + year +"_POP75P"].sum() / df_region["P" + year +"_POP"].sum()) * 100
      df_tranches_age_region = pd.DataFrame(data=[[nom_region,pop0014,pop1529,pop3044,pop4559,pop6074,pop75P]], columns = ["territoire","pop0014","pop1529","pop3044", "pop4559","pop6074", "pop75P"])
      return df_tranches_age_region
    else:
      df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str},sep = ';')
      year = annee[-2:]
      df_region = df.loc[df["REG"]== region, ["P" + year +"_POP", "P" + year +"_POP0014" , "P" + year +"_POP1529","P" + year +"_POP3044", "P" + year +"_POP4559","P" + year +"_POP6074","P" + year +"_POP75P"]]
      pop0014 = (df_region.loc[:, "P" + year +"_POP0014"].sum() / df_region["P" + year +"_POP"].sum()) * 100
      pop1529 = (df_region.loc[:, "P" + year +"_POP1529"].sum() / df_region["P" + year +"_POP"].sum()) * 100
      pop3044 = (df_region.loc[:, "P" + year +"_POP3044"].sum() / df_region["P" + year +"_POP"].sum()) * 100
      pop4559 = (df_region.loc[:, "P" + year +"_POP4559"].sum() / df_region["P" + year +"_POP"].sum()) * 100
      pop6074 = (df_region.loc[:, "P" + year +"_POP6074"].sum() / df_region["P" + year +"_POP"].sum()) * 100
      pop75P = (df_region.loc[:, "P" + year +"_POP75P"].sum() / df_region["P" + year +"_POP"].sum()) * 100
      df_tranches_age_region = pd.DataFrame(data=[[nom_region,pop0014,pop1529,pop3044,pop4559,pop6074,pop75P]], columns = ["territoire","pop0014","pop1529","pop3044", "pop4559","pop6074", "pop75P"])
      return df_tranches_age_region
  tranche_age_region = tranche_age_region("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_region, select_annee)

  # France
  def tranche_age_france(fichier, annee):
    df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
    year = annee[-2:]
    pop0014 = (df.loc[:, "P" + year +"_POP0014"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop1529 = (df.loc[:, "P" + year +"_POP1529"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop3044 = (df.loc[:, "P" + year +"_POP3044"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop4559 = (df.loc[:, "P" + year +"_POP4559"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop6074 = (df.loc[:, "P" + year +"_POP6074"].sum() / df["P" + year +"_POP"].sum()) * 100
    pop75P = (df.loc[:, "P" + year +"_POP75P"].sum() / df["P" + year +"_POP"].sum()) * 100
    df_tranches_age_france = pd.DataFrame(data=[["France",pop0014,pop1529,pop3044,pop4559,pop6074,pop75P]], columns = ["territoire","pop0014","pop1529","pop3044", "pop4559","pop6074", "pop75P"])
    return df_tranches_age_france
  tranche_age_france = tranche_age_france("./population/base-ic-evol-struct-pop-" + select_annee + ".csv", select_annee)

  df_glob_tranches_age = pd.concat([tranches_age_com, tranches_age_epci, tranche_age_departement, tranche_age_region, tranche_age_france])
  df_glob_tranches_age = df_glob_tranches_age.rename(columns={'territoire': "Territoires",'pop0014': "00-14 ans", "pop1529" : '15-29 ans' , "pop3044" : '30-44 ans' , "pop4559" : "45-59 ans", "pop6074" : "60-74 ans", "pop75P" : "Plus de 75 ans"})
  df_glob_tranches_age = df_glob_tranches_age.reset_index(drop=True)
  st.write('Tableau')
  st.write(df_glob_tranches_age)

  @st.cache
  def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

  csv = convert_df(df_glob_tranches_age)

  st.download_button(
    label="💾 Télécharger les données",
    data=csv,
    file_name='tranches_ages_comparaison.csv',
    mime='text/csv',
  )

  fig = px.bar(df_glob_tranches_age, x="Territoires", y=["00-14 ans","15-29 ans", "30-44 ans", "45-59 ans" ,"60-74 ans" , "Plus de 75 ans"], title="Graphique", height=600, width=800)
  st.plotly_chart(fig, use_container_width=False)
  ###########################################################################
  st.header('3.Personnes immigrées')
  st.caption("Selon la définition adoptée par le Haut Conseil à l’Intégration, un immigré est une personne née étrangère à l’étranger et résidant en France. Les personnes nées françaises à l’étranger et vivant en France ne sont donc pas comptabilisées. À l’inverse, certains immigrés ont pu devenir français, les autres restant étrangers. Les populations étrangère et immigrée ne se confondent pas totalement : un immigré n’est pas nécessairement étranger et réciproquement, certains étrangers sont nés en France (essentiellement des mineurs). La qualité d’immigré est permanente : un individu continue à appartenir à la population immigrée même s’il devient français par acquisition. C’est le pays de naissance, et non la nationalité à la naissance, qui définit l'origine géographique d’un immigré.")
  @st.cache()
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
  indice_imm_iris = part_pers_imm_iris("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_commune, select_annee)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(indice_imm_iris)

  ##########################################################################
  st.header('4.Personnes étrangères')
  st.caption("Un étranger est une personne qui réside en France et ne possède pas la nationalité française, soit qu'elle possède une autre nationalité (à titre exclusif), soit qu'elle n'en ait aucune (c'est le cas des personnes apatrides). Les personnes de nationalité française possédant une autre nationalité (ou plusieurs) sont considérées en France comme françaises. Un étranger n'est pas forcément immigré, il peut être né en France (les mineurs notamment).")
  @st.cache()
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
  indice_etr_iris = part_pers_etr_iris("./population/base-ic-evol-struct-pop-" + select_annee + ".csv",code_commune, select_annee)
  with st.expander("Visualiser le tableau des iris"):
    st.dataframe(indice_etr_iris)
############################
  st.caption("Zoom sur les QPV")
  # Preparation carto QPV
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
    df_qpv = df_qpv.rename(columns={'nom_qp': "Nom du quartier",'code_qp' : "Code du quartier", "commune_qp" : "Communes concernées", "TX_TOT_ET" : "Part des étrangers " + select_annee})
    return df_qpv
  part_etrangers_qpv = part_etrangers_qpv('./population/qpv/data_DEMO_' + select_annee + '_V1_QP.csv', nom_commune, select_annee)
  st.table(part_etrangers_qpv)
############################################################################


