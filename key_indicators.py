import streamlit as st
st.set_page_config(
     page_title="Ex-stream-ly Cool App",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
 )
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

# bootstrap 4 collapse example
components.html(
    """
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    <!-- Image and text -->
    <nav class="navbar navbar-dark bg-dark">
      <div class="navbar-brand">
        <img src="https://www.copas.coop/images/navbar/logo_site-bf86e09e.png" width="50" height="30" class="d-inline-block align-top mr-4" alt="">
        Data de territoire
      </div>
    </nav>
    """
)
st.title("Sommaire")

st.markdown("[Population](#i-population)", unsafe_allow_html=True)
st.markdown("[Niveau de vie](#ii-le-niveau-de-vie-m-dian)", unsafe_allow_html=True)
st.markdown("[Indice de vieillissement](#1-indice-de-vieillissement)", unsafe_allow_html=True)
st.markdown("[Personnes de 80 ans et + vivant seules](#2-part-des-personnes-de-80-ans-et-plus-vivant-seules)", unsafe_allow_html=True)
st.markdown("[Indice d'évolution des générations âgées](#3-indice-d-volution-des-g-n-rations-g-es)", unsafe_allow_html=True)
st.markdown("[Familles monoparentales](#1-part-des-familles-monoparentales)", unsafe_allow_html=True)
st.markdown("[Familles nombreuses](#2-part-des-familles-nombreuses)", unsafe_allow_html=True)
st.markdown("[Sans diplôme](#1-sans-diplome)", unsafe_allow_html=True)
st.markdown("[Études supérieures](#2-tudes-sup-rieures)", unsafe_allow_html=True)


########################
#Commune
df_commune = pd.read_csv("./commune_2021.csv", sep=",")
list_commune = df_commune.loc[:, 'LIBELLE']
nom_commune = st.sidebar.selectbox(
     "Commune",
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

##########################
#TEST

#P18_NSCOL15P_SUP2
#P18_NSCOL15P_SUP34
#P18_NSCOL15P_SUP5
#"Part des personnes titulaires d'un diplôme de l'enseignement supérieur "

#if int(annee) >= 2017:

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
    # df_regions['P'+ year + '_NSCOL15P'] = df_regions['P'+ year + '_NSCOL15P'].to_numpy().astype(int)
    # df_regions['P'+ year + '_NSCOL15P_SUP'] = df_regions['P'+ year + '_NSCOL15P_SUP'].to_numpy().astype(int)
    pop_non_scol = df_regions.loc[:, 'P'+ year + '_NSCOL15P'].sum()
    pop_non_scol_etude_sup = df_regions.loc[:, 'P'+ year + '_NSCOL15P_SUP'].sum()
    part_pop_non_scol_etude_sup = (pop_non_scol_etude_sup / pop_non_scol)*100
    df_part_pop_non_scol_etude_sup = pd.DataFrame(data=part_pop_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur " + annee], index = [nom_region])
    return df_part_pop_non_scol_etude_sup

valeurs_etude_sup_reg = part_etude_sup_region("./diplome/base-ic-diplomes-formation-" + select_annee + "-test.csv",str(round(code_region)),select_annee)
valeurs_etude_sup_reg

# Région
#df = pd.read_csv("./diplome/base-ic-diplomes-formation-2014-test.csv", dtype={"IRIS": str, "DEP": str, "REG": str, "UU2010": str, "COM": str, "GRD_QUART": str, "LAB_IRIS": str}, sep = ';')
#year = "2014"[-2:]
#df_regions = df.loc[df["REG"]== str(round(code_region))]
#pop_non_scol = df_regions.loc[:, 'P'+ year + '_NSCOL15P'].sum()
#pop_non_scol_etude_sup = df_regions.loc[:, 'P'+ year + '_NSCOL15P_SUP'].sum()
# part_pop_non_scol_etude_sup = (pop_non_scol_etude_sup / pop_non_scol)*100,0
# df_part_pop_non_scol_etude_sup = pd.DataFrame(data=part_pop_non_scol_etude_sup, columns = ["Part des personnes titulaires d'un diplôme de l'enseignement supérieur 2014"], index = [nom_region])
#df_regions
###########################


# commande : streamlit run streamlit_test.py

st.title('I.POPULATION')
st.header('1.Evolution de la population')


ville = code_commune
df_pop_hist = pd.read_csv('./population/base-cc-serie-historique-2018.CSV', dtype={"CODGEO": str},sep=";")
df_pop_hist_ville = df_pop_hist.loc[df_pop_hist["CODGEO"]==code_commune]
df_pop_hist_ville = df_pop_hist_ville.reset_index()
df_pop_hist_ville = df_pop_hist_ville.loc[:, 'P18_POP' : 'D68_POP']
df_pop_hist_ville = df_pop_hist_ville.rename(columns={'P18_POP': '2018','P13_POP': '2013','P08_POP': '2008','D99_POP': '1999','D90_POP': '1990','D82_POP': '1982','D75_POP': '1975','D68_POP': '1968' })
df_pop_hist_ville.insert(0, 'Commune', nom_commune)
st.table(df_pop_hist_ville)
# inverting values
#df1_transposed = df_pop_hist_ville.T
#st.table(df1_transposed)

#st.area_chart(data=df_pop_hist_ville, height=300, use_container_width=True)

#Indicateurs clés
evol_68_18 = df_pop_hist_ville.iloc[0]["2018"] - df_pop_hist_ville.iloc[0]["1968"]
st.metric(label="Population 2018", value='{:,.0f}'.format(df_pop_hist_ville.iloc[0]["2018"]).replace(",", " "), delta=str('{:,.0f}'.format(evol_68_18.item()).replace(",", " ")) + " hab. depuis 1968")

st.title('II.LE NIVEAU DE VIE MÉDIAN')
st.markdown("La médiane du revenu disponible correspond au niveau au-dessous duquel se situent 50 % de ces revenus. C'est de manière équivalente le niveau au-dessus duquel se situent 50 % des revenus.")
st.markdown("Le revenu disponible est le revenu à la disposition du ménage pour consommer et épargner. Il comprend les revenus d'activité (nets des cotisations sociales), indemnités de chômage, retraites et pensions, revenus fonciers, les revenus financiers et les prestations sociales reçues (prestations familiales, minima sociaux et prestations logements). Au total de ces ressources, on déduit les impôts directs (impôt sur le revenu, taxe d'habitation) et les prélèvements sociaux (CSG, CRDS).")
st.markdown("Le revenu disponible par unité de consommation (UC), également appelé *niveau de vie*, est le revenu disponible par *équivalent adulte*. Il est calculé en rapportant le revenu disponible du ménage au nombre d'unités de consommation qui le composent. Toutes les personnes rattachées au même ménage fiscal ont le même revenu disponible par UC (ou niveau de vie).")

st.header("iris")
@st.cache(persist=True)
def niveau_vie_median_iris(fichier, nom_ville, annee) :
    df = pd.read_csv(fichier, dtype={"IRIS": str , "COM": str},sep=";")
    year = select_annee[-2:]
    df_ville = df.loc[df["LIBCOM"]==nom_ville]
    df_ville = df_ville.replace(',','.', regex=True)
    df_ville = df_ville[['IRIS','LIBIRIS','DISP_MED'+ year]]
    #noms_iris = df.loc[df["LIBCOM"]==nom_ville,'LIBIRIS']
    df_ville['DISP_MED'+ year ] =df_ville['DISP_MED'+ year ].to_numpy().astype(int)
    df_ville.reset_index(inplace=True, drop=True)
    df_ville = df_ville.rename(columns={'IRIS': "Code de l'iris",'LIBIRIS': "Nom de l'iris", 'DISP_MED'+ year:"Niveau de vie " + select_annee + " en €" })

    return df_ville
nvm_iris = niveau_vie_median_iris("./revenu/revenu_iris/BASE_TD_FILO_DISP_IRIS_" + select_annee + ".csv",nom_commune, select_annee)
with st.expander("Visualiser le tableau des iris"):
  st.dataframe(nvm_iris)


@st.cache(persist=True)
def map(geojson):
  map_df = gpd.read_file(geojson)
  return map_df

map_df = map('georef-france-iris-millesime.geojson')
#map_df
# Selectionner les iris de la carte
select_map_df = map_df.loc[(map_df['com_code'] == code_commune) & (map_df['year'] == '2020')]
select_map = select_map_df[['iris_code','iris_name','geometry']]
result = select_map.merge(nvm_iris, left_on='iris_code', right_on="Code de l'iris")
#st.write(result)

m = folium.Map()
folium.GeoJson(data=result["geometry"]).add_to(m)

########################
#test avec folium
#m.choropleth(
#    geo_data=result,
#    data=result,
   # columns=['iris_code', 'Niveau de vie 2018 en €'],
   #  fill_color='YlGnBu',
   #  fill_opacity=1,
   #  line_opacity=1,
   #  legend_name='Births per 1000 inhabitants',
   #  smooth_factor=0)

folium_static(m, width=800, height=400)
#########################

st.header('Test map 2')
##############
#Test avec https://rsandstroem.github.io/GeoMapsFoliumDemo.html

map = folium.Map(location=[50.531036, 2.63926],
                   tiles='OpenStreetMap', zoom_start=12)
map.choropleth(geo_data=select_map['geometry'])
folium_static(map, width=800, height=400)
#############

st.header('a.Comparaison entre territoires')
#Commune
@st.cache(persist=True)
def niveau_vie_median_commune(fichier, nom_ville, annee) :
    df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
    year = select_annee[-2:]
    df_ville = df.loc[df["LIBGEO"]== nom_ville]
    df_ville = df_ville.replace(',','.', regex=True)
    ville = df.loc[df["LIBGEO"]== nom_ville]
    ville = ville.iloc[0]["LIBGEO"]
    nvm =df_ville.loc[:, 'Q2'+ year ].to_numpy()
    df2 = pd.DataFrame(nvm,  columns = ['Niveau de vie médian en ' + select_annee], index=[ville])
    return df2
nvm_ville =niveau_vie_median_commune("./revenu/revenu_commune/FILO" + select_annee + "_DISP_COM.csv",nom_commune, select_annee)

#EPCI
@st.cache(persist=True)
def niveau_vie_median_epci(fichier, cod_epci, annee) :
    df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
    year = select_annee[-2:]
    df_epci = df.loc[df["CODGEO"]== cod_epci]
    df_epci = df_epci.replace(',','.', regex=True)
    epci = df.loc[df["CODGEO"]== cod_epci]
    if epci.empty:
      st.write("l'agglo n'est pas répartoriée par l'insee")
    else:
      epci = epci.iloc[0]["LIBGEO"]
      nvm =df_epci.loc[:, 'Q2'+ year ].to_numpy()
      df2 = pd.DataFrame(nvm,  columns = ['Niveau de vie médian en ' + select_annee], index=[epci])
      return df2

nvm_epci =niveau_vie_median_epci("./revenu/revenu_epci/FILO" + select_annee + "_DISP_EPCI.csv",str(code_epci), select_annee)

#Département
@st.cache(persist=True)
def niveau_vie_median_departement(fichier, nom_departement, annee) :
    df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
    year = select_annee[-2:]
    df_departement = df.loc[df["LIBGEO"]== nom_departement]
    df_departement = df_departement.replace(',','.', regex=True)
    departement = df.loc[df["LIBGEO"]== nom_departement]
    departement = departement.iloc[0]["LIBGEO"]
    nvm =df_departement.loc[:, 'Q2'+ year ].to_numpy()
    df2 = pd.DataFrame(nvm,  columns = ['Niveau de vie médian en ' + select_annee], index=[departement])
    return df2
nvm_departement =niveau_vie_median_departement("./revenu/revenu_dpt/FILO" + select_annee + "_DISP_DEP.csv",nom_departement, select_annee)

#Région
@st.cache(persist=True)
def niveau_vie_median_region(fichier, nom_region, annee) :
    df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
    year = select_annee[-2:]
    df_region = df.loc[df["LIBGEO"]== nom_region]
    df_region = df_region.replace(',','.', regex=True)
    region = df.loc[df["LIBGEO"]== nom_region]
    region = region.iloc[0]["LIBGEO"]
    nvm =df_region.loc[:, 'Q2'+ year ].to_numpy()
    df2 = pd.DataFrame(nvm,  columns = ['Niveau de vie médian en ' + select_annee], index=[region])
    return df2
nvm_region =niveau_vie_median_region("./revenu/revenu_region/FILO" + select_annee + "_DISP_REG.csv",nom_region, select_annee)

#France
@st.cache(persist=True)
def niveau_vie_median_france(fichier, annee) :
    df = pd.read_csv(fichier, dtype={"CODGEO": str},sep=";")
    df = df.replace(',','.', regex=True)
    year = select_annee[-2:]
    france = "France"
    nvm =df.loc[:, 'Q2'+ year ].to_numpy()
    df2 = pd.DataFrame(nvm,  columns = ['Niveau de vie médian en ' + select_annee], index=[france])
    return df2
nvm_france =niveau_vie_median_france("./revenu/revenu_france/FILO" + select_annee + "_DISP_METROPOLE.csv", select_annee)

#Comparaison
@st.cache(persist=True)
def nvm_global(annee) :
    df = pd.concat([nvm_ville, nvm_epci, nvm_departement, nvm_region, nvm_france])
    year = annee
    return df
revenu_global = nvm_global(select_annee)
st.table(revenu_global)

st.header("b.Evolution des territoires")

#France

#2014
df_2014 = pd.read_csv("./revenu/revenu_france/FILO2014_DISP_METROPOLE.csv", dtype={"CODGEO": str},sep=";")
df_2014 = df_2014.replace(',','.', regex=True)
nvm_2014 =df_2014.loc[:, 'Q214'].to_numpy()
indice_2014 = nvm_2014[0]

#2015
df_2015 = pd.read_csv("./revenu/revenu_france/FILO2015_DISP_METROPOLE.csv", dtype={"CODGEO": str},sep=";")
df_2015 = df_2015.replace(',','.', regex=True)
nvm_2015 =df_2015.loc[:, 'Q215'].to_numpy()
indice_2015 = nvm_2015[0]

#2016
df_2016 = pd.read_csv("./revenu/revenu_france/FILO2016_DISP_METROPOLE.csv", dtype={"CODGEO": str},sep=";")
df_2016 = df_2016.replace(',','.', regex=True)
nvm_2016 =df_2016.loc[:, 'Q216'].to_numpy()
indice_2016 = nvm_2016[0]

#2017
df_2017 = pd.read_csv("./revenu/revenu_france/FILO2017_DISP_METROPOLE.csv", dtype={"CODGEO": str},sep=";")
df_2017 = df_2017.replace(',','.', regex=True)
nvm_2017 =df_2017.loc[:, 'Q217'].to_numpy()
indice_2017 = nvm_2017[0]

#2018
df_2018 = pd.read_csv("./revenu/revenu_france/FILO2018_DISP_METROPOLE.csv", dtype={"CODGEO": str},sep=";")
df_2018 = df_2018.replace(',','.', regex=True)
nvm_2018 =df_2018.loc[:, 'Q218'].to_numpy()
indice_2018 = nvm_2018[0]

df_france_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                   columns=['2014', '2015', '2016', '2017', '2018'], index=['France'])

#Région
#2014
df_2014 = pd.read_csv("./revenu/revenu_region/FILO2014_DISP_REG.csv", dtype={"CODGEO": str},sep=";")
df_2014 = df_2014.replace(',','.', regex=True)
df_2014 = df_2014.loc[df_2014["LIBGEO"]== nom_region]
nvm_2014 =df_2014.loc[:, 'Q214'].to_numpy()
indice_2014 = nvm_2014[0]

#2015
df_2015 = pd.read_csv("./revenu/revenu_region/FILO2015_DISP_REG.csv", dtype={"CODGEO": str},sep=";")
df_2015 = df_2015.replace(',','.', regex=True)
df_2015 = df_2015.loc[df_2015["LIBGEO"]== nom_region]
nvm_2015 =df_2015.loc[:, 'Q215'].to_numpy()
indice_2015 = nvm_2015[0]

#2016
df_2016 = pd.read_csv("./revenu/revenu_region/FILO2016_DISP_REG.csv", dtype={"CODGEO": str},sep=";")
df_2016 = df_2016.replace(',','.', regex=True)
df_2016 = df_2016.loc[df_2016["LIBGEO"]== nom_region]
nvm_2016 =df_2016.loc[:, 'Q216'].to_numpy()
indice_2016 = nvm_2016[0]

#2017
df_2017 = pd.read_csv("./revenu/revenu_region/FILO2017_DISP_REG.csv", dtype={"CODGEO": str},sep=";")
df_2017 = df_2017.replace(',','.', regex=True)
df_2017 = df_2017.loc[df_2017["LIBGEO"]== nom_region]
nvm_2017 =df_2017.loc[:, 'Q217'].to_numpy()
indice_2017 = nvm_2017[0]

#2018
df_2018 = pd.read_csv("./revenu/revenu_region/FILO2018_DISP_REG.csv", dtype={"CODGEO": str},sep=";")
df_2018 = df_2018.replace(',','.', regex=True)
df_2018 = df_2018.loc[df_2018["LIBGEO"]== nom_region]
nvm_2018 =df_2018.loc[:, 'Q218'].to_numpy()
indice_2018 = nvm_2018[0]

df_region_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                   columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_region])

#Departement
#2014
df_2014 = pd.read_csv("./revenu/revenu_dpt/FILO2014_DISP_DEP.csv", dtype={"CODGEO": str},sep=";")
df_2014 = df_2014.replace(',','.', regex=True)
df_2014 = df_2014.loc[df_2014["LIBGEO"]== nom_departement]
nvm_2014 =df_2014.loc[:, 'Q214'].to_numpy()
indice_2014 = nvm_2014[0]

#2015
df_2015 = pd.read_csv("./revenu/revenu_dpt/FILO2015_DISP_DEP.csv", dtype={"CODGEO": str},sep=";")
df_2015 = df_2015.replace(',','.', regex=True)
df_2015 = df_2015.loc[df_2015["LIBGEO"]== nom_departement]
nvm_2015 =df_2015.loc[:, 'Q215'].to_numpy()
indice_2015 = nvm_2015[0]

#2016
df_2016 = pd.read_csv("./revenu/revenu_dpt/FILO2016_DISP_DEP.csv", dtype={"CODGEO": str},sep=";")
df_2016 = df_2016.replace(',','.', regex=True)
df_2016 = df_2016.loc[df_2016["LIBGEO"]== nom_departement]
nvm_2016 =df_2016.loc[:, 'Q216'].to_numpy()
indice_2016 = nvm_2016[0]

#2017
df_2017 = pd.read_csv("./revenu/revenu_dpt/FILO2017_DISP_DEP.csv", dtype={"CODGEO": str},sep=";")
df_2017 = df_2017.replace(',','.', regex=True)
df_2017 = df_2017.loc[df_2017["LIBGEO"]== nom_departement]
nvm_2017 =df_2017.loc[:, 'Q217'].to_numpy()
indice_2017 = nvm_2017[0]

#2018
df_2018 = pd.read_csv("./revenu/revenu_dpt/FILO2018_DISP_DEP.csv", dtype={"CODGEO": str},sep=";")
df_2018 = df_2018.replace(',','.', regex=True)
df_2018 = df_2018.loc[df_2018["LIBGEO"]== nom_departement]
nvm_2018 =df_2018.loc[:, 'Q218'].to_numpy()
indice_2018 = nvm_2018[0]

df_departement_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                   columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_departement])

# EPCI
#2014
df_2014 = pd.read_csv("./revenu/revenu_epci/FILO2014_DISP_EPCI.csv", dtype={"CODGEO": str},sep=";")
df_2014 = df_2014.replace(',','.', regex=True)
df_2014 = df_2014.loc[df_2014["CODGEO"]== code_epci]
if df_2014.empty:
  st.write("L'EPCI n'est pas répertorié pas l'insee pour 2014")
else:
  nvm_2014 =df_2014.loc[:, 'Q214'].to_numpy()
  indice_2014 = nvm_2014[0]


#2015
df_2015 = pd.read_csv("./revenu/revenu_epci/FILO2015_DISP_EPCI.csv", dtype={"CODGEO": str},sep=";")
df_2015 = df_2015.replace(',','.', regex=True)
df_2015 = df_2015.loc[df_2015["CODGEO"]== code_epci]
if df_2015.empty:
  st.write("L'EPCI n'est pas répertorié pas l'insee pour 2015")
else:
  nvm_2015 =df_2015.loc[:, 'Q215'].to_numpy()
  indice_2015 = nvm_2015[0]

#2016
df_2016 = pd.read_csv("./revenu/revenu_epci/FILO2016_DISP_EPCI.csv", dtype={"CODGEO": str},sep=";")
df_2016 = df_2016.replace(',','.', regex=True)
df_2016 = df_2016.loc[df_2016["CODGEO"]== code_epci]
nvm_2016 =df_2016.loc[:, 'Q216'].to_numpy()
indice_2016 = nvm_2016[0]

#2017
df_2017 = pd.read_csv("./revenu/revenu_epci/FILO2017_DISP_EPCI.csv", dtype={"CODGEO": str},sep=";")
df_2017 = df_2017.replace(',','.', regex=True)
df_2017 = df_2017.loc[df_2017["CODGEO"]== code_epci]
nvm_2017 =df_2017.loc[:, 'Q217'].to_numpy()
indice_2017 = nvm_2017[0]

#2018
df_2018 = pd.read_csv("./revenu/revenu_epci/FILO2018_DISP_EPCI.csv", dtype={"CODGEO": str},sep=";")
df_2018 = df_2018.replace(',','.', regex=True)
df_2018 = df_2018.loc[df_2018["CODGEO"]== code_epci]
nvm_2018 =df_2018.loc[:, 'Q218'].to_numpy()
indice_2018 = nvm_2018[0]

df_epci_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                   columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_epci])

#commune
#2014
df_2014 = pd.read_csv("./revenu/revenu_commune/FILO2014_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
df_2014 = df_2014.replace(',','.', regex=True)
df_2014 = df_2014.loc[df_2014["LIBGEO"]== nom_commune]
nvm_2014 =df_2014.loc[:, 'Q214'].to_numpy()
indice_2014 = nvm_2014[0]

#2015
df_2015 = pd.read_csv("./revenu/revenu_commune/FILO2015_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
df_2015 = df_2015.replace(',','.', regex=True)
df_2015 = df_2015.loc[df_2015["LIBGEO"]== nom_commune]
nvm_2015 =df_2015.loc[:, 'Q215'].to_numpy()
indice_2015 = nvm_2015[0]

#2016
df_2016 = pd.read_csv("./revenu/revenu_commune/FILO2016_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
df_2016 = df_2016.replace(',','.', regex=True)
df_2016 = df_2016.loc[df_2016["LIBGEO"]== nom_commune]
nvm_2016 =df_2016.loc[:, 'Q216'].to_numpy()
indice_2016 = nvm_2016[0]

#2017
df_2017 = pd.read_csv("./revenu/revenu_commune/FILO2017_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
df_2017 = df_2017.replace(',','.', regex=True)
df_2017 = df_2017.loc[df_2017["LIBGEO"]== nom_commune]
nvm_2017 =df_2017.loc[:, 'Q217'].to_numpy()
indice_2017 = nvm_2017[0]

#2018
df_2018 = pd.read_csv("./revenu/revenu_commune/FILO2018_DISP_COM.csv", dtype={"CODGEO": str},sep=";")
df_2018 = df_2018.replace(',','.', regex=True)
df_2018 = df_2018.loc[df_2018["LIBGEO"]== nom_commune]
nvm_2018 =df_2018.loc[:, 'Q218'].to_numpy()
indice_2018 = nvm_2018[0]

df_ville_glob = pd.DataFrame(np.array([[indice_2014, indice_2015, indice_2016, indice_2017, indice_2018]]),
                   columns=['2014', '2015', '2016', '2017', '2018'], index=[nom_commune])

df_glob = pd.concat([df_france_glob, df_region_glob, df_departement_glob, df_epci_glob, df_ville_glob])

st.table(df_glob)

df1_transposed = df_glob.T
st.line_chart(df1_transposed)



st.title('II.PERSONNES ÂGÉES')

st.header('1.Indice de vieillissement')
st.caption("L'indice de vieillissement est le rapport de la population des 65 ans et plus sur celle des moins de 20 ans. Un indice autour de 100 indique que les 65 ans et plus et les moins de 20 ans sont présents dans à peu près les mêmes proportions sur le territoire; plus l’indice est faible plus le rapport est favorable aux jeunes, plus il est élevé plus il est favorable aux personnes âgées.")

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










st.title('III.FAMILLES')
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

st.subheader("a.Comparaison sur une année")
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


st.subheader("b.Evolution")
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

st.subheader("a.Comparaison sur une année")
st.caption("Une famille est dite nombreuse lorsqu'elle comprend trois enfants ou plus - définition INSEE")
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

st.subheader("b.Evolution")
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


st.title('IV.DIPLOME')
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
  df = pd.read_csv(fichier, dtype={"IRIS": str, "DEP": str,"UU2010": str, "GRD_QUART": str, "COM": str,"LAB_IRIS": str}, encoding= 'unicode_escape', sep=";", header=0)
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

st.subheader('Comparaison')

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

st.subheader("b.Evolution")

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
evol_14_18 = df_glob_sans_diplome.iloc[4]["2018"] - df_glob_sans_diplome.iloc[4]["2014"]
col1, col2 = st.columns(2)
col1.metric(label=nom_commune + " " + select_annee, value=str('{:,.0f}'.format(df_glob_sans_diplome.iloc[4]["2018"]).replace(",", " ") + "%"), delta=str('{:,.0f}'.format(evol_14_18.item()).replace(",", " ")) + " points de % depuis 2014",delta_color="inverse")
col2.metric(label="France " + select_annee, value=str('{:,.0f}'.format(df_glob_sans_diplome.iloc[0]["2018"]).replace(",", " ") + "%"), delta=str('{:,.0f}'.format(evol_14_18.item()).replace(",", " ")) + " points de % depuis 2014",delta_color="inverse")

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


st.subheader('Comparaison')

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

st.subheader("b.Evolution")

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

