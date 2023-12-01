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
import streamlit_folium as folium_st
from shapely.geometry import Polygon, MultiPolygon
import streamlit.components.v1 as components
import fiona
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
  st.title("👶 PETITE ENFANCE")
  last_year = "2020"
  last_year_birth = "2022"
  st.header('1.Les naissances')
  st.caption("Parue le 07/11/2023 - Millésime 2014 à 2022")
  df = pd.read_csv("./petite_enfance/naissance/base_naissances_" + last_year_birth + ".csv", dtype={"CODGEO": str}, sep=";")
  df = df.loc[df['CODGEO'] == code_commune]
  df = df.reset_index(drop=True)
  df['CODGEO'] = nom_commune
  cols = ["NAISD14", "NAISD15", "NAISD16", "NAISD17", "NAISD18", "NAISD19", "NAISD20", "NAISD21", "NAISD22"]
  df[cols] = df[cols].astype(int)
  df = df.rename(columns={"CODGEO": "Commune", "NAISD14": "2014", "NAISD15": "2015", "NAISD16": "2016", "NAISD17": "2017", "NAISD18": "2018", "NAISD19": "2019", "NAISD20": "2020", "NAISD21": "2021", "NAISD22": "2022" })
  st.write(df)

  tx_croissance_nat = (((df["2022"] - df["2014"]) / df["2014"])*100)[0]
  if tx_croissance_nat < 0:
    st.write("La commune connait une baisse des naissances depuis 2014 de l'ordre de " + str(round(tx_croissance_nat)) + "%.")
    st.write("Il est à noter que cette baisse ne peut être totalement imputée au contexte pandémique, en effet, selon l'INSEE au niveau national le nombre de naissance a augmenté en 2021 après 6 années de baisse. [lien](https://www.insee.fr/fr/statistiques/6531925#:~:text=n%C2%B0%20274-,Malgr%C3%A9%20le%20contexte%20pand%C3%A9mique%2C%20les%20naissances%20augmentent%20en,apr%C3%A8s%20six%20ann%C3%A9es%20de%20baisse&text=En%202021%2C%20742%20100%20b%C3%A9b%C3%A9s,observ%C3%A9es%20entre%202015%20et%202020.)")
  ####################

  st.header('2.Les moins de 3 ans')
  st.caption("Paru le 27/06/2023 - Millésime 2020")
  st.caption("Calcul des territoires issu de l'échelle communale")
  #Commune
  def part_0003(code_commune, last_year):
    df = pd.read_csv("./petite_enfance/commune/BTX_TD_POP1A_" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
    df_commune = df.loc[df['CODGEO'] == code_commune]
    total_pop_commune = df_commune.sum(axis = 1).values[0]
    pop_0003_commune =  (df_commune['SEXE1_AGEPYR1000'] + df_commune['SEXE2_AGEPYR1000']).values[0]
    part_pop0003_commune = round(((pop_0003_commune / total_pop_commune) * 100), 2)
    return part_pop0003_commune, pop_0003_commune
  part_pop0003_commune = part_0003(code_commune, last_year)
  st.write("En " + last_year + ", la commune de " + nom_commune + " compte " + str(part_pop0003_commune[1]) + " enfants de moins de 3 ans.")
  #EPCI
  df = pd.read_csv("./petite_enfance/commune/BTX_TD_POP1A_" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  pop_0003_epci = df_epci['SEXE1_AGEPYR1000'].sum() + df_epci['SEXE2_AGEPYR1000'].sum()
  total_pop_epci = (df_epci.iloc[:,2:22].sum(axis=1)).sum()
  part_pop0003_epci = round(((pop_0003_epci / total_pop_epci) * 100), 2)
  #Département
  df_dpt = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, sep = ',')
  df_dpt_merge = pd.merge(df, df_dpt[['COM','DEP']], left_on='CODGEO', right_on='COM')
  df_dpt = df_dpt_merge.loc[df_dpt_merge["DEP"] == str(code_departement)]
  pop_0003_dpt = df_dpt['SEXE1_AGEPYR1000'].sum() + df_dpt['SEXE2_AGEPYR1000'].sum()
  total_pop_dpt = (df_dpt.iloc[:,2:22].sum(axis=1)).sum()
  part_pop0003_dpt = round(((pop_0003_dpt / total_pop_dpt) * 100), 2)
  #Région
  df_region = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
  df_region_merge = pd.merge(df, df_region[['COM','REG']], left_on='CODGEO', right_on='COM')
  df_region = df_region_merge.loc[df_region_merge["REG"] == str(code_region)]
  pop_0003_region = df_region['SEXE1_AGEPYR1000'].sum() + df_region['SEXE2_AGEPYR1000'].sum()
  total_pop_region = (df_region.iloc[:,2:22].sum(axis=1)).sum()
  part_pop0003_region = round(((pop_0003_region / total_pop_region) * 100), 2)
  #France
  df = pd.read_csv("./petite_enfance/commune/BTX_TD_POP1A_" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  total_pop_france = df.sum(axis = 1).values[0]
  pop_0003_france =  (df['SEXE1_AGEPYR1000'] + df['SEXE2_AGEPYR1000']).values[0]
  part_pop0003_france = round(((pop_0003_france / total_pop_france) * 100), 2)
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Part des 0-3 ans - " + last_year + " (en %)": [part_pop0003_commune[0], part_pop0003_epci, part_pop0003_dpt, part_pop0003_region, part_pop0003_france]}
  df = pd.DataFrame(data=d)
  st.write(df)

  #Evolution de la commune
  part_0003_commune_2020 = part_0003(code_commune, last_year)
  part_0003_commune_2015 = part_0003(code_commune, '2015')
  evolution_2015_2020 = ((part_0003_commune_2020[1] - part_0003_commune_2015[1])/part_0003_commune_2015[1])*100
  if evolution_2015_2020 > 0:
    st.write("Le nombre d'enfants de moins de 3 ans de la commune de " + nom_commune + " a augmenté de " + str(round(evolution_2015_2020,2)) + "% depuis 2015.")
  else:
    st.write("Le nombre d'enfants de moins de 3 ans de la commune de " + nom_commune + " a baissé de " + str(round(evolution_2015_2020,2)) + "% depuis 2015.")

  #Surrepresentation de la commune
  if part_pop0003_commune[0] > part_pop0003_epci and part_pop0003_commune[0] > part_pop0003_dpt and part_pop0003_commune[0] > part_pop0003_region and part_pop0003_commune[0] >  part_pop0003_france:
    st.write("La commune connait une surreprésentation de la population des moins de 3 ans comparativement à l'ensemble des autres echelles.")
    st.write("Cette surreprésentation doit amener la collectivité à s'interroger sur l'adaptation de capacités d’accueil des jeunes enfants.")

  #################################
  st.subheader("3.Taux de couverture global - Accueil jeune enfant")
  st.caption("Capacité théorique d'accueil des enfants de moins de 3 ans par les modes d'accueil 'formels' pour 100 enfants de moins de 3 ans.")
  st.caption("Les modes d'accueil formels regroupent : l'assistant(e) maternel(le) employé(e) directement par des particuliers, le salarié(e) à domicile, l'accueil en Eaje (collectif, familial et parental, micro-crèches) et l'école maternelle")
  st.caption("Source : CAF 2020")
  df = pd.read_csv("./petite_enfance/caf/TAUXCOUV2020.csv", dtype={"NUM_COM": str}, sep=";")
  df = df.loc[df['NUM_COM'] == code_commune]
  tx_com = df.iloc[0]['TAUXCOUV_COMM']
  tx_epci = df.iloc[0]['TAUXCOUV_EPCI']
  tx_dep = float(df.iloc[0]['TAUXCOUV_DEP'])
  tx_reg = float(df.iloc[0]['TAUXCOUV_REG'])
  tx_nat = df.iloc[0]['TAUXCOUV_NAT']
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Taux de couverture globale - 2020 (en %)": [tx_com, tx_epci, tx_dep, tx_reg, tx_nat]}
  df = pd.DataFrame(data=d)
  st.write(df)

  #Surrepresentation de la commune
  if tx_com < tx_epci and tx_com < tx_dep and tx_com < tx_reg and tx_com < tx_nat:
    st.write("La commune connait un sous-équipement concernant les modes d'accueil des jeunes enfants comparativement à l'ensemble des autres echelles.")

  ############
  st.header('2.Les enfants de 3 à 5 ans')
  st.caption("Paru le 27/06/2023 - Millésime 2020")
  st.caption("Calcul des territoires issu de l'échelle communale")
  #Commune
  def part_0305(code_commune, last_year):
    df = pd.read_csv("./petite_enfance/commune/BTX_TD_POP1A_" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
    df_commune = df.loc[df['CODGEO'] == code_commune]
    total_pop_commune = df_commune.sum(axis = 1).values[0]
    pop_0305_commune =  (df_commune['SEXE1_AGEPYR1003'] + df_commune['SEXE2_AGEPYR1003']).values[0]
    part_pop0305_commune = round(((pop_0305_commune / total_pop_commune) * 100), 2)
    return part_pop0305_commune, pop_0305_commune
  part_pop0305_commune = part_0305(code_commune, last_year)
  st.write("En " + last_year + ", la commune de " + nom_commune + " compte " + str(part_pop0305_commune[1]) + " enfants de 3 à 5 ans.")
  #EPCI
  df = pd.read_csv("./petite_enfance/commune/BTX_TD_POP1A_" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  pop_0305_epci = df_epci['SEXE1_AGEPYR1003'].sum() + df_epci['SEXE2_AGEPYR1003'].sum()
  total_pop_epci = (df_epci.iloc[:,2:22].sum(axis=1)).sum()
  part_pop0305_epci = round(((pop_0305_epci / total_pop_epci) * 100), 2)
  #Département
  df_dpt = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, sep = ',')
  df_dpt_merge = pd.merge(df, df_dpt[['COM','DEP']], left_on='CODGEO', right_on='COM')
  df_dpt = df_dpt_merge.loc[df_dpt_merge["DEP"] == str(code_departement)]
  pop_0305_dpt = df_dpt['SEXE1_AGEPYR1003'].sum() + df_dpt['SEXE2_AGEPYR1003'].sum()
  total_pop_dpt = (df_dpt.iloc[:,2:22].sum(axis=1)).sum()
  part_pop0305_dpt = round(((pop_0305_dpt / total_pop_dpt) * 100), 2)
  #Région
  df_region = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
  df_region_merge = pd.merge(df, df_region[['COM','REG']], left_on='CODGEO', right_on='COM')
  df_region = df_region_merge.loc[df_region_merge["REG"] == str(code_region)]
  pop_0305_region = df_region['SEXE1_AGEPYR1003'].sum() + df_region['SEXE2_AGEPYR1003'].sum()
  total_pop_region = (df_region.iloc[:,2:22].sum(axis=1)).sum()
  part_pop0305_region = round(((pop_0305_region / total_pop_region) * 100), 2)
  #France
  df = pd.read_csv("./petite_enfance/commune/BTX_TD_POP1A_" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  total_pop_france = df.sum(axis = 1).values[0]
  pop_0305_france =  (df['SEXE1_AGEPYR1003'] + df['SEXE2_AGEPYR1003']).values[0]
  part_pop0305_france = round(((pop_0305_france / total_pop_france) * 100), 2)
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Part des 3-5 ans - " + last_year + " (en %)": [part_pop0305_commune[0], part_pop0305_epci, part_pop0305_dpt, part_pop0305_region, part_pop0305_france]}
  df = pd.DataFrame(data=d)
  st.write(df)

  #Evolution de la commune
  part_0305_commune_2020 = part_0305(code_commune, last_year)
  part_0305_commune_2015 = part_0305(code_commune, '2015')
  evolution_2015_2020 = ((part_0305_commune_2020[1] - part_0305_commune_2015[1])/part_0305_commune_2015[1])*100
  if evolution_2015_2020 > 0:
    st.write("Le nombre d'enfants de 3 à 5 ans de la commune de " + nom_commune + " a augmenté de " + str(round(evolution_2015_2020,2)) + "% depuis 2015.")
  else:
    st.write("Le nombre d'enfants de 3 à 5 ans de la commune de " + nom_commune + " a baissé de " + str(round(evolution_2015_2020,2)) + "% depuis 2015.")

  #############
  st.header('4.La scolarisation des enfants de 2 ans')
  st.caption("Paru le 27/06/2023 - Millésime 2020")
  st.caption("Calcul des territoires issu de l'échelle communale")
  #Commune 2020
  df = pd.read_csv("./petite_enfance/scol_2ans/BTT_TD_FOR1_" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  df_com = df.loc[df['CODGEO'] == code_commune]
  df_com = df_com.loc[df['AGEFORD'] == 2]
  df_scol02 = df_com.groupby(['ILETUR'])['NB'].sum()
  non_scol_02 = df_scol02['Z']
  pop_02 = df_com['NB'].sum()
  scol_02 = pop_02 - non_scol_02
  tx_scol_02 = (scol_02 / pop_02) * 100
  st.write("En " + last_year + ", " + str(round(scol_02)) + " enfants de moins de 2 ans sont scolarisés. Ce qui représente " + str(round(tx_scol_02, 2)) + "% des enfants de moins de 2 ans de la commune.")

  #EPCI
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  df_epci = df_epci.loc[df_epci['AGEFORD'] == 2]
  df_scol02_epci = df_epci.groupby(['ILETUR'])['NB'].sum()
  non_scol_02_epci = df_scol02_epci['Z']
  pop_02_epci = df_epci['NB'].sum()
  scol_02_epci = pop_02_epci - non_scol_02_epci
  tx_scol_02_epci = (scol_02_epci / pop_02_epci) * 100

  #Departement
  df_dpt = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str}, sep = ',')
  df_dpt_merge = pd.merge(df, df_dpt[['COM','DEP']], left_on='CODGEO', right_on='COM')
  df_dpt = df_dpt_merge.loc[df_dpt_merge["DEP"] == str(code_departement)]
  df_dpt = df_dpt.loc[df_dpt['AGEFORD'] == 2]
  df_scol02_dpt = df_dpt.groupby(['ILETUR'])['NB'].sum()
  non_scol_02_dpt = df_scol02_dpt['Z']
  pop_02_dpt = df_dpt['NB'].sum()
  scol_02_dpt = pop_02_dpt - non_scol_02_dpt
  tx_scol_02_dpt = (scol_02_dpt / pop_02_dpt) * 100

  #Région
  df_region = pd.read_csv('./commune_2021.csv', dtype={"COM": str, "DEP": str, "REG": str}, sep = ',')
  df_region_merge = pd.merge(df, df_region[['COM','REG']], left_on='CODGEO', right_on='COM')
  df_region = df_region_merge.loc[df_region_merge["REG"] == str(code_region)]
  df_region = df_region.loc[df_region['AGEFORD'] == 2]
  df_scol02_region = df_region.groupby(['ILETUR'])['NB'].sum()
  non_scol_02_region = df_scol02_region['Z']
  pop_02_region = df_region['NB'].sum()
  scol_02_region = pop_02_region - non_scol_02_region
  tx_scol_02_region = (scol_02_region / pop_02_region) * 100

  #France
  df_fr = pd.read_csv("./petite_enfance/scol_2ans/BTT_TD_FOR1_" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  df_fr = df_fr.loc[df['AGEFORD'] == 2]
  df_scol02_fr = df_fr.groupby(['ILETUR'])['NB'].sum()
  non_scol_02_fr = df_scol02_fr['Z']
  pop_02_fr = df_fr['NB'].sum()
  scol_02_fr = pop_02_fr - non_scol_02_fr
  tx_scol_02_fr = (scol_02_fr / pop_02_fr) * 100

  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Taux de scolarisation des enfants de 2 ans - " + last_year + " (en %)": [tx_scol_02, tx_scol_02_epci, tx_scol_02_dpt, tx_scol_02_region, tx_scol_02_fr]}
  df_scol_02 = pd.DataFrame(data=d)
  st.write(df_scol_02)

  #############

  st.header('4.La scolarisation des moins de 6 ans')
  st.caption("Paru le  27/06/2023 - Millésime 2020")
  st.caption("Calcul des territoires issu de l'échelle communale")

  #Commune
  def part_scol_0205(code_commune, last_year):
    df = pd.read_csv("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
    df_commune = df.loc[df['CODGEO'] == code_commune]
    total_pop0205_commune = df_commune["P" + last_year[-2:] + "_POP0205"].values[0]
    pop_scol0205_commune = df_commune["P" + last_year[-2:] + "_SCOL0205"].values[0]
    part_scol0205_commune = (pop_scol0205_commune / total_pop0205_commune) * 100
    return part_scol0205_commune, pop_scol0205_commune
  part_pop_scol0205_commune = part_scol_0205(code_commune, last_year)
  st.write("En " + last_year + ", la commune de " + nom_commune + " compte " + str(part_pop_scol0205_commune[1]) + " enfants de moins de 6 ans scolarisés.")
  #EPCI
  df = pd.read_csv("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  df_epci = pd.read_csv('./EPCI_2020.csv', dtype={"CODGEO": str, "DEP": str, "REG": str, "EPCI":str}, sep = ';')
  df_epci_merge = pd.merge(df, df_epci[['CODGEO','EPCI', 'LIBEPCI']], left_on='CODGEO', right_on='CODGEO')
  df_epci = df_epci_merge.loc[df_epci_merge["EPCI"] == str(code_epci)]
  pop_0205_epci = df_epci["P" + last_year[-2:] + "_POP0205"].sum()
  pop_scol0205__epci = df_epci["P" + last_year[-2:] + "_SCOL0205"].sum()
  part_pop_scol0205_epci = round(((pop_scol0205__epci / pop_0205_epci) * 100), 2)
  #Département
  df = pd.read_csv("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str, "DEP": str}, sep=";")
  df_dpt = df.loc[df['DEP'] == code_departement]
  pop_0205_dpt = df_dpt["P" + last_year[-2:] + "_POP0205"].sum()
  pop_scol_0205_dpt = df_dpt["P" + last_year[-2:] + "_SCOL0205"].sum()
  part_pop_scol0205_dpt = round(((pop_scol_0205_dpt / pop_0205_dpt) * 100), 2)
  #Région
  df = pd.read_csv("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str, "REG": str}, sep=";")
  df_region = df.loc[df['REG'] == str(code_region)]
  pop_0205_region = df_region["P" + last_year[-2:] + "_POP0205"].sum()
  pop_scol_0205_region = df_region["P" + last_year[-2:] + "_SCOL0205"].sum()
  part_pop_scol0205_region = round(((pop_scol_0205_region / pop_0205_region) * 100), 2)
  #France
  df = pd.read_csv("./diplome/commune/base-cc-diplomes-formation-" + last_year + ".csv", dtype={"CODGEO": str, "LIBGEO": str}, sep=";")
  pop_0205_france = df["P" + last_year[-2:] + "_POP0205"].sum()
  pop_scol_0205_france = df["P" + last_year[-2:] + "_SCOL0205"].sum()
  part_pop_scol_0205_france = round(((pop_scol_0205_france / pop_0205_france) * 100), 2)
  #Comparaison
  d = {'Territoires': [nom_commune, nom_epci, nom_departement, nom_region, 'France'], "Part de la population scolarisée de 2-5 ans - " + last_year + " (en %)": [part_pop_scol0205_commune[0], part_pop_scol0205_epci, part_pop_scol0205_dpt, part_pop_scol0205_region, part_pop_scol_0205_france]}
  df = pd.DataFrame(data=d)
  st.write(df)

  #Evolution de la commune
  pop_scol0205_commune_2020 = part_scol_0205(code_commune, last_year)
  pop_scol0205_commune_2015 = part_scol_0205(code_commune, '2015')
  evolution_2015_2020 = ((pop_scol0205_commune_2020[1] - pop_scol0205_commune_2015[1])/pop_scol0205_commune_2015[1])*100
  if evolution_2015_2020 > 0:
    st.write("Le nombre d'enfants de moins de 6 ans scolarisés de la commune de " + nom_commune + " a augmenté de " + str(round(evolution_2015_2020,2)) + "% depuis 2015.")
  else:
    st.write("Le nombre d'enfants de moins de 6 ans scolarisés de la commune de " + nom_commune + " a baissé de " + str(round(evolution_2015_2020,2)) + "% depuis 2015.")

  #Iris
  #def part_scol0205_iris(fichier, code, annee) :
  st.subheader('Comparaison entre iris')
  st.caption("Paru le 19/10/2023 - Millésime 2020")
  df = pd.read_csv("./diplome/base-ic-diplomes-formation-" + last_year + ".csv", dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, sep=";", header=0)
  df_scol_0205 = df.loc[df['COM'] == code_commune]
  df_scol_0205["Part_scol0205"] = (df_scol_0205["P" + last_year[-2:] + "_SCOL0205"] / df_scol_0205["P" + last_year[-2:] + "_POP0205"]) * 100
  df_scol_0205 = df_scol_0205[["IRIS", "LIBIRIS", "P" + last_year[-2:] + "_POP0205", "P" + last_year[-2:] + "_SCOL0205", "Part_scol0205"]]
  #df = df.rename(columns={'IRIS': "Code de l'iris",'LIBIRIS': "Nom de l'iris", "P" + last_year[-2:] + "_POP0205":"Population des 02 à 5 ans (" + last_year + ")", 'P' + last_year[-2:] +'_SCOL0205':"Personnes scolarisées de 02 à 05 ans (" + last_year + ")" ,'Part_scol0205': "Part des personnes scolarisées de 02 à 05 ans (" + last_year + ") en %" })
  st.write(df_scol_0205)

  # Carte Scolarisation des moins de 6 ans
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
  gdf = gdf.merge(df_scol_0205, left_on='fields.iris_code', right_on="IRIS")

  # Créer une carte centrée autour de la latitude et longitude moyenne
  map_center = [gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()]
  breaks = jenkspy.jenks_breaks(gdf["Part_scol0205"], 5)
  m = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles='cartodb positron', attr='SCOP COPAS')

  # Ajouter la carte choroplèthe
  folium.Choropleth(
    geo_data=gdf.set_index("IRIS"),
    name='choropleth',
    data=gdf,
    columns=["IRIS", "Part_scol0205"],
    key_on='feature.id',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    color='#ffffff',
    weight=3,
    opacity=1.0,
    legend_name='Part des enfants de 2 à 5 ans scolarisés',
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
        fields=["LIBIRIS", "Part_scol0205"],
        aliases=['Iris: ', "Part des enfants de 2 à 5 ans scolarisés :"],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
    )
  )
  m.add_child(NIL)
  m.keep_in_front(NIL)
  st.subheader("Part des enfants de 2 à 5 ans scolarisés par IRIS")
  # Afficher la carte dans Streamlit
  folium_st.folium_static(m)



