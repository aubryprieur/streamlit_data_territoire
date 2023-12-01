import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
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

  ##################
  st.subheader("Les QPV")
  uploaded_file = st.file_uploader("Uploader un fichier csv contenant les coordonnées geo dans une colonne CODGEO")
  if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.header("REVENU ET PRÉCARITÉ")
    #RSA SOCLE
    st.subheader("Part des allocataires percevant le RSA socle")
    st.caption("Paru le : 14/03/2023 pour le Millésime 2019 et le 23/12/2019 pour le Millésime 2015")
    df_revn_1 = pd.read_csv('./QPV/Revenu/REVN_2023.csv', dtype={"CODGEO": str}, sep=";")
    df_revn_2 = pd.read_csv('./QPV/Revenu/REVN_2019.csv', dtype={"CODGEO": str}, sep=";")

    df_alloc_rsa_filtre_1 = df_revn_1[df_revn_1['CODGEO'].isin(df['CODGEO'])]
    df_alloc_rsa_filtre_1 = df_alloc_rsa_filtre_1[['CODGEO', 'LIBGEO', 'A', 'ARSAS']]
    df_alloc_rsa_filtre_1['ARSAS'] = pd.to_numeric(df_alloc_rsa_filtre_1['ARSAS'], errors='coerce')
    df_alloc_rsa_filtre_1['A'] = pd.to_numeric(df_alloc_rsa_filtre_1['A'], errors='coerce')
    df_alloc_rsa_filtre_1['tx_ARSAS'] = (df_alloc_rsa_filtre_1['ARSAS'] / df_alloc_rsa_filtre_1['A']) * 100
    df_alloc_rsa_filtre_1 = df_alloc_rsa_filtre_1.rename(columns={'tx_ARSAS': "Part des allocataires RSA socle 2019"})
    df_alloc_rsa_filtre_1.reset_index(inplace=True, drop=True)

    df_alloc_rsa_filtre_2 = df_revn_2[df_revn_2['CODGEO'].isin(df['CODGEO'])]
    df_alloc_rsa_filtre_2 = df_alloc_rsa_filtre_2[['CODGEO', 'LIBGEO', 'A', 'ARSAS']]
    df_alloc_rsa_filtre_2['ARSAS'] = pd.to_numeric(df_alloc_rsa_filtre_2['ARSAS'], errors='coerce')
    df_alloc_rsa_filtre_2['A'] = pd.to_numeric(df_alloc_rsa_filtre_2['A'], errors='coerce')
    df_alloc_rsa_filtre_2['tx_ARSAS'] = (df_alloc_rsa_filtre_2['ARSAS'] / df_alloc_rsa_filtre_2['A']) * 100
    df_alloc_rsa_filtre_2 = df_alloc_rsa_filtre_2.rename(columns={'tx_ARSAS': "Part des allocataires RSA socle 2015"})
    df_alloc_rsa_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_alloc_rsa_filtre_2.merge(df_alloc_rsa_filtre_1, on=['CODGEO', 'LIBGEO'])

    alloc_rsa_epci_1 = pd.read_csv('./QPV/Revenu/EPCI/REVN_2023.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = alloc_rsa_epci_1[alloc_rsa_epci_1['CODGEO'] == code_epci ]
    desired_row['ARSAS'] = desired_row['ARSAS'].str.replace('\u202f', '').astype(float)
    desired_row['A'] = desired_row['A'].str.replace('\u202f', '').astype(float)
    desired_row['tx_ARSAS'] = (desired_row['ARSAS'] / desired_row['A']) * 100
    alloc_rsa_epci_1 = desired_row['tx_ARSAS'].values[0]
    alloc_rsa_epci_2 = pd.read_csv('./QPV/Revenu/EPCI/REVN_2019.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = alloc_rsa_epci_2[alloc_rsa_epci_2['CODGEO'] == code_epci ]
    desired_row['ARSAS'] = desired_row['ARSAS'].str.replace('\u202f', '').astype(float)
    desired_row['A'] = desired_row['A'].astype(str).str.replace('\u202f', '').astype(float)
    desired_row['tx_ARSAS'] = (desired_row['ARSAS'] / desired_row['A']) * 100
    alloc_rsa_epci_2 = desired_row['tx_ARSAS'].values[0]
    st.write("Part allocataires RSA epci 2019: " + str(alloc_rsa_epci_1))
    st.write("Part allocataires RSA epci 2015: " + str(alloc_rsa_epci_2))

    # Ajout d'une colonne pour la différence entre la part des allocataires RSA socle 2019 et alloc_rsa_epci_1
    merged_data['Diff_RSA_socle_2019_vs_epci_1'] = merged_data['Part des allocataires RSA socle 2019'] - alloc_rsa_epci_1
    # Ajout d'une colonne pour la différence entre la part des allocataires RSA socle 2015 et alloc_rsa_epci_1
    merged_data['Diff_RSA_socle_2015_vs_epci_2'] = merged_data['Part des allocataires RSA socle 2015'] - alloc_rsa_epci_2
    # Calcul de la différence entre les deux colonnes de différence et ajout en tant que nouvelle colonne
    merged_data['Diff_2019_vs_2015'] = merged_data['Diff_RSA_socle_2019_vs_epci_1'] - merged_data['Diff_RSA_socle_2015_vs_epci_2']
    st.table(merged_data)

    # Calcul de la valeur médiane
    median_value = merged_data['Part des allocataires RSA socle 2019'].median()
    st.write("La valeur médiane QPV de la part des allocataires RSA socle en 2019 est : " + str(round(median_value,2)) + "%")
    # Calcul valeur max
    max_value = merged_data['Part des allocataires RSA socle 2019'].max()
    #Bilan
    bilan_rsa = max_value / alloc_rsa_epci_1
    st.write("En ce qui concerne le taux maximum au sein des qpv, c'est jusqu'à " + str(round(bilan_rsa, 2)) + " fois plus que le/la " + nom_epci)

    # Création du nuage de points interactif avec Plotly Express
    fig = px.scatter(merged_data,
                     x='Part des allocataires RSA socle 2019',
                     y='Diff_2019_vs_2015',
                     text='LIBGEO',
                     hover_data=['LIBGEO'])

    # Ajout de la ligne horizontale pour alloc_rsa_epci_1
    fig.add_hline(y=0, line_dash="dot",
                  annotation_text="(En dessous de la ligne les écarts se réduisent)",
                  annotation_position="bottom right")

    # Ajout d'une ligne verticale pointillée au niveau de alloc_rsa_epci_1
    fig.add_vline(x=alloc_rsa_epci_1, line_dash="dot",
                  annotation_text="(À la droite de la ligne : Taux QPV > EPCI)",
                  annotation_position="bottom right")

    # Ajout d'un point pour représenter alloc_rsa_epci_1 avec ordonnée 0
    fig.add_scatter(x=[alloc_rsa_epci_1], y=[0], mode='markers+text', text=[nom_epci], marker_color='red', textposition='top center')

    # Amélioration de la lisibilité en ajustant la superposition du texte
    fig.update_traces(textposition='top center')

    # Mise à jour des titres des axes et du graphique
    fig.update_layout(
        title="Nuage de points des allocataires RSA socle en 2019 et l'évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        xaxis_title='Part des allocataires RSA socle 2019',
        yaxis_title="Évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        showlegend=False
    )

    # Affichage du graphique dans Streamlit
    st.plotly_chart(fig, use_container_width=True)

    #PAUVRETÉ À 60% DU REVENU DÉCLARÉ
    st.subheader("Taux de pauvreté à 60% du revenu déclaré")
    st.caption("Paru le : 14/03/2023 pour le Millésime 2019 et le 23/12/2019 pour le Millésime 2015")
    df_revn_1 = pd.read_csv('./QPV/Revenu/REVN_2023.csv', dtype={"CODGEO": str}, sep=";")
    df_revn_2 = pd.read_csv('./QPV/Revenu/REVN_2019.csv', dtype={"CODGEO": str}, sep=";")

    df_txpauv_filtre_1 = df_revn_1[df_revn_1['CODGEO'].isin(df['CODGEO'])]
    df_txpauv_filtre_1 = df_txpauv_filtre_1[['CODGEO', 'LIBGEO', 'BREV']]
    df_txpauv_filtre_1['BREV'] = df_txpauv_filtre_1['BREV'].str.replace(',', '.').astype(float)
    df_txpauv_filtre_1 = df_txpauv_filtre_1.rename(columns={'BREV': "Taux de pauvreté à 60 revenu déclaré 2019"})
    df_txpauv_filtre_1.reset_index(inplace=True, drop=True)

    df_txpauv_filtre_2 = df_revn_2[df_revn_2['CODGEO'].isin(df['CODGEO'])]
    df_txpauv_filtre_2 = df_txpauv_filtre_2[['CODGEO', 'LIBGEO', 'BREV']]
    df_txpauv_filtre_2['BREV'] = df_txpauv_filtre_2['BREV'].str.replace(',', '.').astype(float)
    df_txpauv_filtre_2 = df_txpauv_filtre_2.rename(columns={'BREV': "Taux de pauvreté à 60 revenu déclaré 2015"})
    df_txpauv_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_txpauv_filtre_2.merge(df_txpauv_filtre_1, on=['CODGEO', 'LIBGEO'])

    indice_txpauv_epci_1 = pd.read_csv('./QPV/Revenu/EPCI/REVN_2023.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = indice_txpauv_epci_1[indice_txpauv_epci_1['CODGEO'] == code_epci ]
    indice_txpauv_epci_1 = desired_row['BREV'].values[0]
    indice_txpauv_epci_1 = indice_txpauv_epci_1.replace(',', '.')
    indice_txpauv_epci_1 = float(indice_txpauv_epci_1)

    indice_txpauv_epci_2 = pd.read_csv('./QPV/Revenu/EPCI/REVN_2019.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = indice_txpauv_epci_2[indice_txpauv_epci_2['CODGEO'] == code_epci ]
    indice_txpauv_epci_2 = desired_row['BREV'].values[0]
    indice_txpauv_epci_2 = indice_txpauv_epci_2.replace(',', '.')
    indice_txpauv_epci_2 = float(indice_txpauv_epci_2)
    st.write("Taux de pauvreté à 60% RD epci 2019: " + str(indice_txpauv_epci_1))
    st.write("Taux de pauvreté à 60% RD epci 2015: " + str(indice_txpauv_epci_2))

    merged_data['Diff_txpauv_2019_vs_txpauv_1'] = merged_data["Taux de pauvreté à 60 revenu déclaré 2019"] - indice_txpauv_epci_1
    merged_data['Diff_txpauv_2015_vs_txpauv_2'] = merged_data["Taux de pauvreté à 60 revenu déclaré 2015"] - indice_txpauv_epci_2
    merged_data['Diff_2019_vs_2015'] = merged_data['Diff_txpauv_2019_vs_txpauv_1'] - merged_data['Diff_txpauv_2015_vs_txpauv_2']
    st.table(merged_data)

    # Médiane et maxi
    median_value = merged_data["Taux de pauvreté à 60 revenu déclaré 2019"].median()
    st.write("La valeur médiane QPV du taux de pauvreté en 2019 est : " + str(round(median_value,2)) + "%")
    max_value = merged_data["Taux de pauvreté à 60 revenu déclaré 2019"].max()
    bilan_pauvrete = max_value / indice_txpauv_epci_1
    st.write("En ce qui concerne le taux maximum au sein des qpv, c'est jusqu'à " + str(round(bilan_pauvrete, 2)) + " fois plus que le/la " + nom_epci)

    # Graphique
    fig = px.scatter(merged_data,
                     x="Taux de pauvreté à 60 revenu déclaré 2019",
                     y='Diff_2019_vs_2015',
                     text='LIBGEO',
                     hover_data=['LIBGEO'])

    fig.add_hline(y=0, line_dash="dot",
                  annotation_text="(En dessous de la ligne les écarts se réduisent)",
                  annotation_position="bottom right")
    fig.add_vline(x=indice_txpauv_epci_1, line_dash="dot",
                  annotation_text="(À la droite de la ligne : Taux QPV > EPCI)",
                  annotation_position="bottom right")
    fig.add_scatter(x=[indice_txpauv_epci_1], y=[0], mode='markers+text', text=[nom_epci], marker_color='red', textposition='top center')
    fig.update_traces(textposition='top center')
    fig.update_layout(
        title="Nuage de points du taux de pauvreté en 2019 et l'évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        xaxis_title='Taux de pauvreté 2019',
        yaxis_title="Évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    # MÉDIANE DES REVENUS DÉCLARÉS
    st.subheader("Médiane des revenus déclarés")
    st.caption("Paru le : 31/03/2023 pour le Millésime 2020 et le 12/08/2019 pour le Millésime 2015")
    df_rev_1 = pd.read_csv('./QPV/Revenu/indic-revenu-declare-quartiers-2020.csv', dtype={"CODGEO": str}, sep=";")
    df_rev_2 = pd.read_csv('./QPV/Revenu/indic-revenu-declare-quartiers-2015.csv', dtype={"CODGEO": str}, sep=";")

    df_medrev_filtre_1 = df_rev_1[df_rev_1['CODGEO'].isin(df['CODGEO'])]
    df_medrev_filtre_1 = df_medrev_filtre_1[['CODGEO', 'LIBGEO', 'DEC_MED_A20']]
    df_medrev_filtre_1.reset_index(inplace=True, drop=True)
    df_medrev_filtre_2 = df_rev_2[df_rev_2['codgeo'].isin(df['CODGEO'])]
    df_medrev_filtre_2 = df_medrev_filtre_2[['codgeo', 'libgeo', 'decuc_q2_a15']]
    df_medrev_filtre_2.reset_index(inplace=True, drop=True)

    merged_df = df_medrev_filtre_1.merge(df_medrev_filtre_2, left_on='CODGEO', right_on='codgeo', how='inner')
    merged_df = merged_df[['CODGEO', 'LIBGEO', 'decuc_q2_a15', 'DEC_MED_A20']]
    merged_df['DEC_MED_A20'] = merged_df['DEC_MED_A20'].astype(str).str.replace('\u202f', '').astype(int)
    merged_df['decuc_q2_a15'] = merged_df['decuc_q2_a15'].astype(str).str.replace('\u202f', '').astype(int)
    merged_df = merged_df.rename(columns={'decuc_q2_a15': "Médiane des revenus déclarés 2015", 'DEC_MED_A20': "Médiane des revenus déclarés 2020"})
    st.table(merged_df)

    #Données EPCI
    df_medrev_epci_1 = pd.read_csv('./QPV/Revenu/EPCI/FILO2020_DEC_EPCI.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = df_medrev_epci_1[df_medrev_epci_1['CODGEO'] == code_epci ]
    indice_medrev_epci_1 = desired_row['Q220'].values[0]
    df_medrev_epci_2 = pd.read_csv('./QPV/Revenu/EPCI/FILO2015_DEC_EPCI.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = df_medrev_epci_2[df_medrev_epci_2['CODGEO'] == code_epci ]
    indice_medrev_epci_2 = desired_row['Q215'].values[0]
    indice_medrev_epci_2 = float(indice_medrev_epci_2.replace(',', '.'))
    st.write("A l'échelle de l'EPCI, la médiane des revenus déclarés en 2020: " + str(indice_medrev_epci_1))
    st.write("A l'échelle de l'EPCI, la médiane des revenus déclarés en 2015: " + str(indice_medrev_epci_2))


    merged_df['Diff_mediane_qpv_epci_2020'] = merged_df["Médiane des revenus déclarés 2020"] - indice_medrev_epci_1
    merged_df['Diff_mediane_qpv_epci_2015'] = merged_df["Médiane des revenus déclarés 2015"] - indice_medrev_epci_2
    merged_df['Diff_2020_2015'] = merged_df['Diff_mediane_qpv_epci_2020'] - merged_df['Diff_mediane_qpv_epci_2015']
    st.table(merged_df)

    # Graphique
    fig = px.scatter(merged_df,
                     x="Médiane des revenus déclarés 2020",
                     y='Diff_2020_2015',
                     text='LIBGEO',
                     hover_data=['LIBGEO'])

    fig.add_hline(y=0, line_dash="dot",
                  annotation_text="(En dessous de la ligne les écarts augmentent)",
                  annotation_position="bottom right")
    fig.add_vline(x=indice_medrev_epci_1, line_dash="dot",
                  annotation_text="(À la gauche de la ligne : Taux QPV < EPCI)",
                  annotation_position="bottom left")
    fig.add_scatter(x=[indice_medrev_epci_1], y=[0], mode='markers+text', text=[nom_epci], marker_color='red', textposition='top center')
    fig.update_traces(textposition='top center')
    fig.update_layout(
        title="Nuage de points de la médiane des révenus déclarés en 2020 et l'évolution des écarts 2015-2020 entre les QPV et l'EPCI",
        xaxis_title='Médiane des revenus déclarés 2020',
        yaxis_title="Évolution des écarts 2015-2020 entre les QPV et l'EPCI",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    st.header("POPULATION")
    #Population en qpv
    st.subheader("Population en qpv")
    st.caption("Paru le : 07/07/2023 pour le Millésime 2018 et le 23/12/2019 pour le Millésime 2013")
    df_pop_1 = pd.read_csv('./QPV/Demographie/DEMO_2023.csv', dtype={"CODGEO": str}, sep=";")
    df_pop_2 = pd.read_csv('./QPV/Demographie/DEMO_2017.csv', dtype={"CODGEO": str}, sep=";")

    df_pop_filtre_1 = df_pop_1[df_pop_1['CODGEO'].isin(df['CODGEO'])]
    df_pop_filtre_1 = df_pop_filtre_1[['CODGEO', 'LIBGEO', 'POP_MUN']]
    df_pop_filtre_1['POP_MUN'] = df_pop_filtre_1['POP_MUN'].astype(str).str.replace('\u202f', '').astype(int)
    df_pop_filtre_1 = df_pop_filtre_1.rename(columns={'POP_MUN': "Population en qpv 2018"})
    df_pop_filtre_1.reset_index(inplace=True, drop=True)

    df_pop_filtre_2 = df_pop_2[df_pop_2['CODGEO'].isin(df['CODGEO'])]
    df_pop_filtre_2 = df_pop_filtre_2[['CODGEO', 'LIBGEO', 'POP_MUN']]
    df_pop_filtre_2['POP_MUN'] = df_pop_filtre_2['POP_MUN'].astype(str).str.replace('\u202f', '').astype(int)
    df_pop_filtre_2 = df_pop_filtre_2.rename(columns={'POP_MUN': "Population en qpv 2013"})
    df_pop_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_pop_filtre_2.merge(df_pop_filtre_1, on=['CODGEO', 'LIBGEO'])
    merged_data["Evolution_pop"] = merged_data["Population en qpv 2018"] - merged_data["Population en qpv 2013"]
    st.table(merged_data)

    # Graphique
    fig = px.scatter(merged_data,
                     x="Population en qpv 2018",
                     y='Evolution_pop',
                     text='LIBGEO',
                     hover_data=['LIBGEO'])

    fig.add_hline(y=0, line_dash="dot",
                  annotation_text="(En dessous de la ligne la population baisse)",
                  annotation_position="bottom right")
    fig.update_traces(textposition='top center')
    fig.update_layout(
        title="Nuage de points de la population des qpv en 2018 et l'évolution de la population 2013-2018",
        xaxis_title='Population 2018',
        yaxis_title="Évolution 2013-2018 de la population",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    #Indice jeunesse
    st.subheader("indice jeunesse")
    st.caption("Paru le : 07/07/2023 pour le Millésime 2019 et le 23/12/2019 pour le Millésime 2015")

    #EPCI
    indice_jeune_epci_1 = pd.read_csv('./QPV/Demographie/EPCI/DEMO_2023.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = indice_jeune_epci_1[indice_jeune_epci_1['CODGEO'] == code_epci ]
    indice_jeune_epci_1 = desired_row['IND_JEUNE'].values[0]
    indice_jeune_epci_1 = float(indice_jeune_epci_1.replace(',', '.'))
    indice_jeune_epci_2 = pd.read_csv('./QPV/Demographie/EPCI/DEMO_2019.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = indice_jeune_epci_2[indice_jeune_epci_2['CODGEO'] == code_epci ]
    indice_jeune_epci_2 = desired_row['IND_JEUNE'].values[0]
    indice_jeune_epci_2 = float(indice_jeune_epci_2.replace(',', '.'))
    st.write("Indice jeunesse epci 2019: " + str(indice_jeune_epci_1))
    st.write("Indice jeunesse epci 2015: " + str(indice_jeune_epci_2))

    df_demo_1 = pd.read_csv('./QPV/Demographie/DEMO_2023.csv', dtype={"CODGEO": str}, sep=";")
    df_demo_2 = pd.read_csv('./QPV/Demographie/DEMO_2019.csv', dtype={"CODGEO": str}, sep=";")

    df_indice_jeune_filtre_1 = df_demo_1[df_demo_1['CODGEO'].isin(df['CODGEO'])]
    df_indice_jeune_filtre_1 = df_indice_jeune_filtre_1[['CODGEO', 'LIBGEO', 'IND_JEUNE']]
    df_indice_jeune_filtre_1['IND_JEUNE'] = df_indice_jeune_filtre_1['IND_JEUNE'].astype(str).str.replace(',', '.').astype(float)
    df_indice_jeune_filtre_1 = df_indice_jeune_filtre_1.rename(columns={'IND_JEUNE': "Indice jeunesse 2019"})
    df_indice_jeune_filtre_1.reset_index(inplace=True, drop=True)

    df_indice_jeune_filtre_2 = df_demo_2[df_demo_2['CODGEO'].isin(df['CODGEO'])]
    df_indice_jeune_filtre_2 = df_indice_jeune_filtre_2[['CODGEO', 'LIBGEO', 'IND_JEUNE']]
    df_indice_jeune_filtre_2['IND_JEUNE'] = df_indice_jeune_filtre_2['IND_JEUNE'].astype(str).str.replace(',', '.').astype(float)
    df_indice_jeune_filtre_2 = df_indice_jeune_filtre_2.rename(columns={'IND_JEUNE': "Indice jeunesse 2015"})
    df_indice_jeune_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_indice_jeune_filtre_2.merge(df_indice_jeune_filtre_1, on=['CODGEO', 'LIBGEO'])
    merged_data['Diff_ind_jeune_qpv_epci_2019'] = merged_data["Indice jeunesse 2019"] - indice_jeune_epci_1
    merged_data['Diff_ind_jeune_qpv_epci_2015'] = merged_data["Indice jeunesse 2015"] - indice_jeune_epci_2
    merged_data['Diff_2019_2015'] = merged_data['Diff_ind_jeune_qpv_epci_2019'] - merged_data['Diff_ind_jeune_qpv_epci_2015']
    st.table(merged_data)

    # Graphique
    fig = px.scatter(merged_data,
                     x="Indice jeunesse 2019",
                     y='Diff_2019_2015',
                     text='LIBGEO',
                     hover_data=['LIBGEO'])

    fig.add_hline(y=0, line_dash="dot",
                  annotation_text="(En dessous de la ligne les écarts se réduisent)",
                  annotation_position="bottom right")
    fig.add_vline(x=indice_jeune_epci_1, line_dash="dot",
                  annotation_text="(À la droite de la ligne : Taux QPV > EPCI)",
                  annotation_position="bottom right")
    fig.add_scatter(x=[indice_jeune_epci_1], y=[0], mode='markers+text', text=[nom_epci], marker_color='red', textposition='top center')
    fig.update_traces(textposition='top center')
    fig.update_layout(
        title="Nuage de points des indices jeunesse qpv en 2019 et l'évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        xaxis_title='Indice jeunesse 2019',
        yaxis_title="Évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    #Plus de 60 ans
    st.subheader("Part des plus de 60 ans")
    st.caption("Paru le : 07/07/2023 pour le Millésime 2019 et le 23/12/2019 pour le Millésime 2015")

    epci_60p_1 = pd.read_csv('./QPV/Demographie/EPCI/DEMO_2023.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = epci_60p_1[epci_60p_1['CODGEO'] == code_epci ]
    epci_60p_1 = desired_row['TX_TOT_60ETPLUS'].values[0]
    epci_60p_1 = float(epci_60p_1.replace(',', '.'))
    epci_60p_2 = pd.read_csv('./QPV/Demographie/EPCI/DEMO_2019.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = epci_60p_2[epci_60p_2['CODGEO'] == code_epci ]
    epci_60p_2 = desired_row['TX_TOT_60ETPLUS'].values[0]
    epci_60p_2 = float(epci_60p_2.replace(',', '.'))
    st.write("Part des plus de 60 ans epci 2019: " + str(epci_60p_1))
    st.write("Part des plus de 60 ans epci 2015: " + str(epci_60p_2))

    df_60p_filtre_1 = df_demo_1[df_demo_1['CODGEO'].isin(df['CODGEO'])]
    df_60p_filtre_1 = df_60p_filtre_1[['CODGEO', 'LIBGEO', 'TX_TOT_60ETPLUS']]
    df_60p_filtre_1['TX_TOT_60ETPLUS'] = df_60p_filtre_1['TX_TOT_60ETPLUS'].astype(str).str.replace(',', '.').astype(float)
    df_60p_filtre_1 = df_60p_filtre_1.rename(columns={'TX_TOT_60ETPLUS': "Part des plus de 60 ans 2019"})
    df_60p_filtre_1.reset_index(inplace=True, drop=True)

    df_60p_filtre_2 = df_demo_2[df_demo_2['CODGEO'].isin(df['CODGEO'])]
    df_60p_filtre_2 = df_60p_filtre_2[['CODGEO', 'LIBGEO', 'TX_TOT_60ETPLUS']]
    df_60p_filtre_2['TX_TOT_60ETPLUS'] = df_60p_filtre_2['TX_TOT_60ETPLUS'].astype(str).str.replace(',', '.').astype(float)
    df_60p_filtre_2 = df_60p_filtre_2.rename(columns={'TX_TOT_60ETPLUS': "Part des plus de 60 ans 2015"})
    df_60p_filtre_2.reset_index(inplace=True, drop=True)

    merged_data_60p = df_60p_filtre_2.merge(df_60p_filtre_1, on=['CODGEO', 'LIBGEO'])
    merged_data_60p['Diff_60p_qpv_epci_2019'] = merged_data_60p["Part des plus de 60 ans 2019"] - epci_60p_1
    merged_data_60p['Diff_60p_qpv_epci_2015'] = merged_data_60p["Part des plus de 60 ans 2015"] - epci_60p_2
    merged_data_60p['Diff_2019_2015'] = merged_data_60p['Diff_60p_qpv_epci_2019'] - merged_data_60p['Diff_60p_qpv_epci_2015']
    st.table(merged_data_60p)

    # Graphique
    fig = px.scatter(merged_data_60p,
                     x="Part des plus de 60 ans 2019",
                     y='Diff_2019_2015',
                     text='LIBGEO',
                     hover_data=['LIBGEO'])

    fig.add_hline(y=0, line_dash="dot",
                  annotation_text="(En dessous de la ligne les écarts se réduisent)",
                  annotation_position="bottom right")
    fig.add_vline(x=epci_60p_1, line_dash="dot",
                  annotation_text="(À la gauche de la ligne : Taux QPV < EPCI)",
                  annotation_position="bottom right")
    fig.add_scatter(x=[epci_60p_1], y=[0], mode='markers+text', text=[nom_epci], marker_color='red', textposition='top center')
    fig.update_traces(textposition='top center')
    fig.update_layout(
        title="Nuage de points du taux de 60 ans et plus en qpv en 2019 et l'évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        xaxis_title='Part des 60 ans et plus en 2019',
        yaxis_title="Évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    #Moins de 25 ans
    st.subheader("Part des moins de 25 ans")
    st.caption("Paru le : 07/07/2023 pour le Millésime 2019 et le 23/12/2019 pour le Millésime 2015")

    epci_25m_1 = pd.read_csv('./QPV/Demographie/EPCI/DEMO_2023.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = epci_25m_1[epci_25m_1['CODGEO'] == code_epci ]
    epci_25m_1 = desired_row['TX_TOT_0A24'].values[0]
    epci_25m_1 = float(epci_25m_1.replace(',', '.'))
    epci_25m_2 = pd.read_csv('./QPV/Demographie/EPCI/DEMO_2019.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = epci_25m_2[epci_25m_2['CODGEO'] == code_epci ]
    epci_25m_2 = desired_row['TX_TOT_0A24'].values[0]
    epci_25m_2 = float(epci_25m_2.replace(',', '.'))
    st.write("Part des moins de 25 ans epci 2019: " + str(epci_25m_1))
    st.write("Part des moins de 25 ans epci 2015: " + str(epci_25m_2))

    df_25m_filtre_1 = df_demo_1[df_demo_1['CODGEO'].isin(df['CODGEO'])]
    df_25m_filtre_1 = df_25m_filtre_1[['CODGEO', 'LIBGEO', 'TX_TOT_0A24']]
    df_25m_filtre_1['TX_TOT_0A24'] = df_25m_filtre_1['TX_TOT_0A24'].astype(str).str.replace(',', '.').astype(float)
    df_25m_filtre_1 = df_25m_filtre_1.rename(columns={'TX_TOT_0A24': "Part des moins de 25 ans 2019"})
    df_25m_filtre_1.reset_index(inplace=True, drop=True)

    df_25m_filtre_2 = df_demo_2[df_demo_2['CODGEO'].isin(df['CODGEO'])]
    df_25m_filtre_2 = df_25m_filtre_2[['CODGEO', 'LIBGEO', 'TX_TOT_0A24']]
    df_25m_filtre_2['TX_TOT_0A24'] = df_25m_filtre_2['TX_TOT_0A24'].astype(str).str.replace(',', '.').astype(float)
    df_25m_filtre_2 = df_25m_filtre_2.rename(columns={'TX_TOT_0A24': "Part des moins de 25 ans 2015"})
    df_25m_filtre_2.reset_index(inplace=True, drop=True)

    merged_data_25m = df_25m_filtre_2.merge(df_25m_filtre_1, on=['CODGEO', 'LIBGEO'])
    merged_data_25m['Diff_25m_qpv_epci_2019'] = merged_data_25m["Part des moins de 25 ans 2019"] - epci_25m_1
    merged_data_25m['Diff_25m_qpv_epci_2015'] = merged_data_25m["Part des moins de 25 ans 2015"] - epci_25m_2
    merged_data_25m['Diff_2019_2015'] = merged_data_25m['Diff_25m_qpv_epci_2019'] - merged_data_25m['Diff_25m_qpv_epci_2015']
    st.table(merged_data_25m)

    # Graphique
    fig = px.scatter(merged_data_25m,
                     x="Part des moins de 25 ans 2019",
                     y='Diff_2019_2015',
                     text='LIBGEO',
                     hover_data=['LIBGEO'])

    fig.add_hline(y=0, line_dash="dot",
                  annotation_text="(En dessous de la ligne les écarts se réduisent)",
                  annotation_position="bottom right")
    fig.add_vline(x=epci_25m_1, line_dash="dot",
                  annotation_text="(À la droite de la ligne : Taux QPV > EPCI)",
                  annotation_position="bottom right")
    fig.add_scatter(x=[epci_25m_1], y=[0], mode='markers+text', text=[nom_epci], marker_color='red', textposition='top center')
    fig.update_traces(textposition='top center')
    fig.update_layout(
        title="Nuage de points du taux de moins de 25 ans en qpv en 2019 et l'évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        xaxis_title='Part de moins de 25 ans en 2019',
        yaxis_title="Évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    #Ménages 1 personne
    st.subheader("Part des ménages d'une personne")
    st.caption("Paru le : 07/07/2023 pour le Millésime 2019 et le 23/12/2019 pour le Millésime 2015")

    epci_menage1_1 = pd.read_csv('./QPV/Demographie/EPCI/DEMO_2023.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = epci_menage1_1[epci_menage1_1['CODGEO'] == code_epci ]
    epci_menage1_1 = desired_row['TX_TOT_MEN1'].values[0]
    epci_menage1_1 = float(epci_menage1_1.replace(',', '.'))
    epci_menage1_2 = pd.read_csv('./QPV/Demographie/EPCI/DEMO_2019.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = epci_menage1_2[epci_menage1_2['CODGEO'] == code_epci ]
    epci_menage1_2 = desired_row['TX_TOT_MEN1'].values[0]
    epci_menage1_2 = float(epci_menage1_2.replace(',', '.'))
    st.write("Part des ménages 1 personne epci 2019: " + str(epci_menage1_1))
    st.write("Part des ménages 1 personne epci 2015: " + str(epci_menage1_2))

    df_menage1_filtre_1 = df_demo_1[df_demo_1['CODGEO'].isin(df['CODGEO'])]
    df_menage1_filtre_1 = df_menage1_filtre_1[['CODGEO', 'LIBGEO', 'TX_TOT_MEN1']]
    df_menage1_filtre_1['TX_TOT_MEN1'] = df_menage1_filtre_1['TX_TOT_MEN1'].astype(str).str.replace(',', '.').astype(float)
    df_menage1_filtre_1 = df_menage1_filtre_1.rename(columns={'TX_TOT_MEN1': "Part des ménages d'une personne 2019"})
    df_menage1_filtre_1.reset_index(inplace=True, drop=True)

    df_menage1_filtre_2 = df_demo_2[df_demo_2['CODGEO'].isin(df['CODGEO'])]
    df_menage1_filtre_2 = df_menage1_filtre_2[['CODGEO', 'LIBGEO', 'TX_TOT_MEN1']]
    df_menage1_filtre_2['TX_TOT_MEN1'] = df_menage1_filtre_2['TX_TOT_MEN1'].astype(str).str.replace(',', '.').astype(float)
    df_menage1_filtre_2 = df_menage1_filtre_2.rename(columns={'TX_TOT_MEN1': "Part des ménages d'une personne 2015"})
    df_menage1_filtre_2.reset_index(inplace=True, drop=True)

    merged_data_menage1 = df_menage1_filtre_2.merge(df_menage1_filtre_1, on=['CODGEO', 'LIBGEO'])
    merged_data_menage1['Diff_menage1_qpv_epci_2019'] = merged_data_menage1["Part des ménages d'une personne 2019"] - epci_menage1_1
    merged_data_menage1['Diff_menage1_qpv_epci_2015'] = merged_data_menage1["Part des ménages d'une personne 2015"] - epci_menage1_2
    merged_data_menage1['Diff_2019_2015'] = merged_data_menage1['Diff_menage1_qpv_epci_2019'] - merged_data_menage1['Diff_menage1_qpv_epci_2015']
    st.table(merged_data_menage1)

    # Graphique
    fig = px.scatter(merged_data_menage1,
                     x="Part des ménages d'une personne 2019",
                     y='Diff_2019_2015',
                     text='LIBGEO',
                     hover_data=['LIBGEO'])

    fig.add_hline(y=0, line_dash="dot",
                  annotation_text="(En dessous de la ligne les écarts se réduisent)",
                  annotation_position="bottom right")
    fig.add_vline(x=epci_menage1_1, line_dash="dot",
                  annotation_text="(À la droite de la ligne : Taux QPV > EPCI)",
                  annotation_position="bottom right")
    fig.add_scatter(x=[epci_menage1_1], y=[0], mode='markers+text', text=[nom_epci], marker_color='red', textposition='top center')
    fig.update_traces(textposition='top center')
    fig.update_layout(
        title="Nuage de points du taux de ménages d'une personne en qpv en 2019 et l'évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        xaxis_title="Part des ménages d'une personne en 2019",
        yaxis_title="Évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    #Ménages 6 personnes et plus
    st.subheader("Part des ménages de 6 personnes et plus")
    st.caption("Paru le : 07/07/2023 pour le Millésime 2019 et le 23/12/2019 pour le Millésime 2015")

    #EPCI
    epci_menage6p_1 = pd.read_csv('./QPV/Demographie/EPCI/DEMO_2023.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = epci_menage6p_1[epci_menage6p_1['CODGEO'] == code_epci ]
    epci_menage6p_1 = desired_row['TX_TOT_MEN6'].values[0]
    epci_menage6p_1 = float(epci_menage6p_1.replace(',', '.'))
    epci_menage6p_2 = pd.read_csv('./QPV/Demographie/EPCI/DEMO_2019.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = epci_menage6p_2[epci_menage6p_2['CODGEO'] == code_epci ]
    epci_menage6p_2 = desired_row['TX_TOT_MEN6'].values[0]
    epci_menage6p_2 = float(epci_menage6p_2.replace(',', '.'))
    st.write("Part des ménages de 6 personnes et plus epci 2019: " + str(epci_menage6p_1))
    st.write("Part des ménages de 6 personnes et plus 2015: " + str(epci_menage6p_2))

    #QPV
    df_menage6p_filtre_1 = df_demo_1[df_demo_1['CODGEO'].isin(df['CODGEO'])]
    df_menage6p_filtre_1 = df_menage6p_filtre_1[['CODGEO', 'LIBGEO', 'TX_TOT_MEN6']]
    df_menage6p_filtre_1['TX_TOT_MEN6'] = df_menage6p_filtre_1['TX_TOT_MEN6'].astype(str).str.replace(',', '.').astype(float)
    df_menage6p_filtre_1 = df_menage6p_filtre_1.rename(columns={'TX_TOT_MEN6': "Part des ménages de 6 personnes et plus 2019"})
    df_menage6p_filtre_1.reset_index(inplace=True, drop=True)

    df_menage6p_filtre_2 = df_demo_2[df_demo_2['CODGEO'].isin(df['CODGEO'])]
    df_menage6p_filtre_2 = df_menage6p_filtre_2[['CODGEO', 'LIBGEO', 'TX_TOT_MEN6']]
    df_menage6p_filtre_2['TX_TOT_MEN6'] = df_menage6p_filtre_2['TX_TOT_MEN6'].astype(str).str.replace(',', '.').astype(float)
    df_menage6p_filtre_2 = df_menage6p_filtre_2.rename(columns={'TX_TOT_MEN6': "Part des ménages de 6 personnes et plus 2015"})
    df_menage6p_filtre_2.reset_index(inplace=True, drop=True)

    merged_data_menage6p = df_menage6p_filtre_2.merge(df_menage6p_filtre_1, on=['CODGEO', 'LIBGEO'])
    merged_data_menage6p['Diff_menage6p_qpv_epci_2019'] = merged_data_menage6p["Part des ménages de 6 personnes et plus 2019"] - epci_menage6p_1
    merged_data_menage6p['Diff_menage6p_qpv_epci_2015'] = merged_data_menage6p["Part des ménages de 6 personnes et plus 2015"] - epci_menage6p_2
    merged_data_menage6p['Diff_2019_2015'] = merged_data_menage6p['Diff_menage6p_qpv_epci_2019'] - merged_data_menage6p['Diff_menage6p_qpv_epci_2015']
    st.table(merged_data_menage6p)

    # Graphique
    fig = px.scatter(merged_data_menage6p,
                     x="Part des ménages de 6 personnes et plus 2019",
                     y='Diff_2019_2015',
                     text='LIBGEO',
                     hover_data=['LIBGEO'])

    fig.add_hline(y=0, line_dash="dot",
                  annotation_text="(En dessous de la ligne les écarts se réduisent)",
                  annotation_position="bottom right")
    fig.add_vline(x=epci_menage6p_1, line_dash="dot",
                  annotation_text="(À la droite de la ligne : Taux QPV > EPCI)",
                  annotation_position="bottom right")
    fig.add_scatter(x=[epci_menage6p_1], y=[0], mode='markers+text', text=[nom_epci], marker_color='red', textposition='top center')
    fig.update_traces(textposition='top center')
    fig.update_layout(
        title="Nuage de points du taux de ménages de 6 personnes et plus en qpv en 2019 et l'évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        xaxis_title="Part des ménages de 6 personnes et plus en 2019",
        yaxis_title="Évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    #Part des allocataires mono-parent parmi les allocataires
    st.subheader("Part des allocataires monoparent parmi les allocataires")
    st.caption("Paru le : 07/07/2023 pour le Millésime 2019 et le XXX pour le Millésime 2015")
    df_demo_1 = pd.read_csv('./QPV/Demographie/DEMO_2023.csv', dtype={"CODGEO": str}, sep=";")
    df_demo_2 = pd.read_csv('./QPV/Demographie/DEMO_2019.csv', dtype={"CODGEO": str}, sep=";")


    #EPCI
    alloc_monoparent_epci_1 = pd.read_csv('./QPV/Demographie/EPCI/DEMO_2023.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = alloc_monoparent_epci_1[alloc_monoparent_epci_1['CODGEO'] == code_epci ]
    desired_row['AM'] = desired_row['AM'].str.replace('\u202f', '').astype(float)
    desired_row['A'] = desired_row['A'].str.replace('\u202f', '').astype(float)
    desired_row['tx_AM'] = desired_row['AM'] / desired_row['A']
    alloc_monoparent_epci_1 = desired_row['tx_AM'].values[0]
    alloc_monoparent_epci_2 = pd.read_csv('./QPV/Demographie/EPCI/DEMO_2019.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = alloc_monoparent_epci_2[alloc_monoparent_epci_2['CODGEO'] == code_epci ]
    desired_row['AM'] = desired_row['AM'].str.replace('\u202f', '').astype(float)
    desired_row['A'] = desired_row['A'].astype(str).str.replace('\u202f', '').astype(float)
    desired_row['tx_AM'] = desired_row['AM'] / desired_row['A']
    alloc_monoparent_epci_2 = desired_row['tx_AM'].values[0]
    st.write("Part allocataires monoparents epci 2019: " + str(alloc_monoparent_epci_1))
    st.write("Part allocataires monoparents epci 2015: " + str(alloc_monoparent_epci_2))

    #QPV
    df_alloc_monoparent_filtre_1 = df_demo_1[df_demo_1['CODGEO'].isin(df['CODGEO'])]
    df_alloc_monoparent_filtre_1 = df_alloc_monoparent_filtre_1[['CODGEO', 'LIBGEO', 'A', 'AM']]
    df_alloc_monoparent_filtre_1['AM'] = pd.to_numeric(df_alloc_monoparent_filtre_1['AM'], errors='coerce')
    df_alloc_monoparent_filtre_1['A'] = pd.to_numeric(df_alloc_monoparent_filtre_1['A'], errors='coerce')
    df_alloc_monoparent_filtre_1['tx_AM'] = df_alloc_monoparent_filtre_1['AM'] / df_alloc_monoparent_filtre_1['A']
    df_alloc_monoparent_filtre_1 = df_alloc_monoparent_filtre_1.rename(columns={'tx_AM': "Part des allocataires monoparents 2019"})
    df_alloc_monoparent_filtre_1.reset_index(inplace=True, drop=True)

    df_alloc_monoparent_filtre_2 = df_demo_2[df_demo_2['CODGEO'].isin(df['CODGEO'])]
    df_alloc_monoparent_filtre_2 = df_alloc_monoparent_filtre_2[['CODGEO', 'LIBGEO', 'A', 'AM']]
    df_alloc_monoparent_filtre_2['AM'] = pd.to_numeric(df_alloc_monoparent_filtre_2['AM'], errors='coerce')
    df_alloc_monoparent_filtre_2['A'] = pd.to_numeric(df_alloc_monoparent_filtre_2['A'], errors='coerce')
    df_alloc_monoparent_filtre_2['tx_AM'] = df_alloc_monoparent_filtre_2['AM'] / df_alloc_monoparent_filtre_2['A']
    df_alloc_monoparent_filtre_2 = df_alloc_monoparent_filtre_2.rename(columns={'tx_AM': "Part des allocataires monoparents 2015"})
    df_alloc_monoparent_filtre_2.reset_index(inplace=True, drop=True)

    merged_data_mono = df_alloc_monoparent_filtre_2.merge(df_alloc_monoparent_filtre_1, on=['CODGEO', 'LIBGEO'])
    merged_data_mono['Diff_mono_qpv_epci_2019'] = merged_data_mono["Part des allocataires monoparents 2019"] - alloc_monoparent_epci_1
    merged_data_mono['Diff_mono_qpv_epci_2015'] = merged_data_mono["Part des allocataires monoparents 2015"] - alloc_monoparent_epci_2
    merged_data_mono['Diff_2019_2015'] = merged_data_mono['Diff_mono_qpv_epci_2019'] - merged_data_mono['Diff_mono_qpv_epci_2015']
    st.table(merged_data_mono)

    # Graphique
    fig = px.scatter(merged_data_mono,
                     x="Part des allocataires monoparents 2019",
                     y='Diff_2019_2015',
                     text='LIBGEO',
                     hover_data=['LIBGEO'])

    fig.add_hline(y=0, line_dash="dot",
                  annotation_text="(En dessous de la ligne les écarts se réduisent)",
                  annotation_position="bottom right")
    fig.add_vline(x=alloc_monoparent_epci_1, line_dash="dot",
                  annotation_text="(À la droite de la ligne : Taux QPV > EPCI)",
                  annotation_position="bottom right")
    fig.add_scatter(x=[alloc_monoparent_epci_1], y=[0], mode='markers+text', text=[nom_epci], marker_color='red', textposition='top center')
    fig.update_traces(textposition='top center')
    fig.update_layout(
        title="Nuage de points du taux d'allocataires monoparents en qpv en 2021 et l'évolution des écarts 2015-2019 entre les QPV et l'EPCI",
        xaxis_title="Part des allocataires monoparents en 2019",
        yaxis_title="Évolution des écarts 2021-2019 entre les QPV et l'EPCI",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    st.header("LOGEMENTS ET LOGEMENTS SOCIAUX")

    #Nombre de logements sociaux
    st.subheader("nombre de logements sociaux")
    st.caption("Paru le : 07/07/2023 pour le Millésime RPLS 2021")
    df_nb_lgts_sociaux = pd.read_csv('./QPV/Logement/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_nb_lgts_sociaux_filtre = df_nb_lgts_sociaux[df_nb_lgts_sociaux['codGeo'].isin(df['CODGEO'])]
    df_nb_lgts_sociaux_filtre = df_nb_lgts_sociaux_filtre[['codGeo', 'libGeo', 'nbLsPls']]
    df_nb_lgts_sociaux_filtre['nbLsPls'] = df_nb_lgts_sociaux_filtre['nbLsPls'].astype(str).str.replace('\u202f', '').astype(float)
    df_nb_lgts_sociaux_filtre.reset_index(inplace=True, drop=True)
    st.table(df_nb_lgts_sociaux_filtre)

    df_nb_lgts_sociaux_epci = pd.read_csv('./QPV/Logement/EPCI/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_nb_lgts_sociaux_epci = df_nb_lgts_sociaux_epci[df_nb_lgts_sociaux_epci['codGeo'] == code_epci ]
    val_nb_lgts_sociaux_epci = df_nb_lgts_sociaux_epci['nbLsPls'].values[0]
    st.write("Nombre de logements sociaux epci 2021: " + val_nb_lgts_sociaux_epci)
    val_nb_lgts_sociaux_epci = float(val_nb_lgts_sociaux_epci.replace('\u202f', ''))

    # Calcul de la somme de la colonne 'nbLsPls'
    total_nbLsPls = df_nb_lgts_sociaux_filtre['nbLsPls'].sum()

    #Part qpv-EPCI
    part_qpv_epci = (total_nbLsPls / val_nb_lgts_sociaux_epci ) * 100
    st.write("La part des logements sociaux en qpv par rapport à l'EPCI en 2021 : " + str(round(part_qpv_epci,2)) + "%")

    #Part des logements sociaux parmi les résidences principales
    st.subheader("Part des logements sociaux parmi les résidences principales")
    st.caption("Paru le : 07/07/2023 pour le Millésime RPLS 2021 et le 23/05/2023 pour le Millésime RPLS 2019")

    #EPCI
    indice_lgtsociaux_epci_1 = pd.read_csv('./QPV/Logement/EPCI/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    desired_row = indice_lgtsociaux_epci_1[indice_lgtsociaux_epci_1['codGeo'] == code_epci ]
    indice_lgtsociaux_epci_1 = desired_row['txLsRp'].values[0]
    indice_lgtsociaux_epci_1 = float(indice_lgtsociaux_epci_1.replace(',', '.'))
    indice_lgtsociaux_epci_2 = pd.read_csv('./QPV/Logement/EPCI/LOGT_2021.csv', dtype={"codGeo": str}, sep=";")
    desired_row = indice_lgtsociaux_epci_2[indice_lgtsociaux_epci_2['codGeo'] == code_epci ]
    indice_lgtsociaux_epci_2 = desired_row['txLsRp'].values[0]
    indice_lgtsociaux_epci_2 = float(indice_lgtsociaux_epci_2.replace(',', '.'))
    st.write("Taux de logements sociaux epci 2021: " + str(indice_lgtsociaux_epci_1))
    st.write("Taux de logements sociaux epci 2019: " + str(indice_lgtsociaux_epci_2))

    #QPV
    df_lgtsociaux_1 = pd.read_csv('./QPV/Logement/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_lgtsociaux_2 = pd.read_csv('./QPV/Logement/LOGT_2021.csv', dtype={"CodGeo": str}, sep=";")

    df_lgtsociaux_filtre_1 = df_lgtsociaux_1[df_lgtsociaux_1['codGeo'].isin(df['CODGEO'])]
    df_lgtsociaux_filtre_1 = df_lgtsociaux_filtre_1[['codGeo', 'libGeo', 'txLsRp']]
    df_lgtsociaux_filtre_1['txLsRp'] = df_lgtsociaux_filtre_1['txLsRp'].astype(str).str.replace(',', '.').astype(float)
    df_lgtsociaux_filtre_1 = df_lgtsociaux_filtre_1.rename(columns={'txLsRp': "Taux des logements sociaux 2021"})
    df_lgtsociaux_filtre_1.reset_index(inplace=True, drop=True)

    df_lgtsociaux_filtre_2 = df_lgtsociaux_2[df_lgtsociaux_2['codGeo'].isin(df['CODGEO'])]
    df_lgtsociaux_filtre_2 = df_lgtsociaux_filtre_2[['codGeo', 'libGeo', 'txLsRp']]
    df_lgtsociaux_filtre_2['txLsRp'] = df_lgtsociaux_filtre_2['txLsRp'].astype(str).str.replace(',', '.').astype(float)
    df_lgtsociaux_filtre_2 = df_lgtsociaux_filtre_2.rename(columns={'txLsRp': "Taux des logements sociaux 2019"})
    df_lgtsociaux_filtre_2.reset_index(inplace=True, drop=True)

    merged_data_hlm = df_lgtsociaux_filtre_2.merge(df_lgtsociaux_filtre_1, on=['codGeo', 'libGeo'])
    merged_data_hlm['Diff_hlm_qpv_epci_2021'] = merged_data_hlm["Taux des logements sociaux 2021"] - indice_lgtsociaux_epci_1
    merged_data_hlm['Diff_hlm_qpv_epci_2019'] = merged_data_hlm["Taux des logements sociaux 2019"] - indice_lgtsociaux_epci_2
    merged_data_hlm['Diff_2021_2019'] = merged_data_hlm['Diff_hlm_qpv_epci_2021'] - merged_data_hlm['Diff_hlm_qpv_epci_2019']
    st.table(merged_data_hlm)

    # Graphique
    fig = px.scatter(merged_data_hlm,
                     x="Taux des logements sociaux 2021",
                     y='Diff_2021_2019',
                     text='libGeo',
                     hover_data=['libGeo'])

    fig.add_hline(y=0, line_dash="dot",
                  annotation_text="(En dessous de la ligne les écarts se réduisent)",
                  annotation_position="bottom right")
    fig.add_vline(x=indice_lgtsociaux_epci_1, line_dash="dot",
                  annotation_text="(À la droite de la ligne : Taux QPV > EPCI)",
                  annotation_position="bottom right")
    fig.add_scatter(x=[indice_lgtsociaux_epci_1], y=[0], mode='markers+text', text=[nom_epci], marker_color='red', textposition='top center')
    fig.update_traces(textposition='top center')
    fig.update_layout(
        title="Nuage de points du taux de logements sociaux en qpv en 2021 et l'évolution des écarts 2021-2019 entre les QPV et l'EPCI",
        xaxis_title="Part des logements sociaux en 2021",
        yaxis_title="Évolution des écarts 2021-2019 entre les QPV et l'EPCI",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


    #Taux de logements vacants
    st.subheader("Taux des logements vacants")
    st.caption("Paru le : 07/07/2023 pour le Millésime 2019 et le 23/05/2023 pour le Millésime 2017")
    df_vacants_1 = pd.read_csv('./QPV/Logement/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_vacants_2 = pd.read_csv('./QPV/Logement/LOGT_2021.csv', dtype={"CodGeo": str}, sep=";")

    df_txvacants_filtre_1 = df_vacants_1[df_vacants_1['codGeo'].isin(df['CODGEO'])]
    df_txvacants_filtre_1 = df_txvacants_filtre_1[['codGeo', 'libGeo', 'partResVac']]
    df_txvacants_filtre_1['partResVac'] = df_txvacants_filtre_1['partResVac'].astype(str).str.replace(',', '.').astype(float)
    df_txvacants_filtre_1 = df_txvacants_filtre_1.rename(columns={'partResVac': "Taux des logements vacants 2019"})
    df_txvacants_filtre_1.reset_index(inplace=True, drop=True)

    df_txvacants_filtre_2 = df_vacants_2[df_vacants_2['codGeo'].isin(df['CODGEO'])]
    df_txvacants_filtre_2 = df_txvacants_filtre_2[['codGeo', 'libGeo', 'partResVac']]
    df_txvacants_filtre_2['partResVac'] = df_txvacants_filtre_2['partResVac'].astype(str).str.replace(',', '.').astype(float)
    df_txvacants_filtre_2 = df_txvacants_filtre_2.rename(columns={'partResVac': "Taux des logements vacants 2017"})
    df_txvacants_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_txvacants_filtre_2.merge(df_txvacants_filtre_1, on=['codGeo', 'libGeo'])
    st.table(merged_data)

    indice_txvacants_epci_1 = pd.read_csv('./QPV/Logement/EPCI/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    desired_row = indice_txvacants_epci_1[indice_txvacants_epci_1['codGeo'] == code_epci ]
    indice_txvacants_epci_1 = desired_row['partResVac'].values[0]
    indice_txvacants_epci_1 = float(indice_txvacants_epci_1.replace(',', '.'))
    indice_txvacants_epci_2 = pd.read_csv('./QPV/Logement/EPCI/LOGT_2021.csv', dtype={"codGeo": str}, sep=";")
    desired_row = indice_txvacants_epci_2[indice_txvacants_epci_2['codGeo'] == code_epci ]
    indice_txvacants_epci_2 = desired_row['partResVac'].values[0]
    indice_txvacants_epci_2 = float(indice_txvacants_epci_2.replace(',', '.'))
    st.write("Taux des logements vacants epci 2019: " + str(indice_txvacants_epci_1))
    st.write("Taux des logements vacants epci 2017: " + str(indice_txvacants_epci_2))


    # Création d'un nouveau DataFrame avec les informations de l'EPCI
    new_row = pd.DataFrame({
        'codGeo': [code_epci],  # Utilisez le code EPCI réel ici
        'libGeo': [nom_epci],  # Utilisez le nom EPCI réel ici
        'Taux des logements vacants 2017': [indice_txvacants_epci_2],  # Utilisez la valeur réelle ici
        'Taux des logements vacants 2019': [indice_txvacants_epci_1]   # Utilisez la valeur réelle ici
    })

    # Ajout de la nouvelle ligne au DataFrame 'merged_data'
    merged_data = merged_data.append(new_row, ignore_index=True)

    merged_data['Color'] = 'Default Color'
    merged_data.loc[merged_data['libGeo'] == nom_epci, 'Color'] = 'EPCI Color'
    # Création du bar chart avec Plotly Express
    fig = px.bar(
        merged_data,
        x='libGeo',  # La colonne pour les labels de l'axe X
        y='Taux des logements vacants 2019',  # La colonne pour les valeurs de l'axe Y
        title='Taux des logements vacants par zone géographique en 2019',
        labels={'libGeo': 'Zone Géographique', 'Taux des logements vacants 2019': 'Taux de Logements Vacants (%)'},
        color='Color',  # Utilisez la colonne de couleur pour la couleur des barres
        color_discrete_map={  # Définir des couleurs spécifiques pour chaque valeur
            'Default Color': 'blue',  # Couleur par défaut pour les autres barres
            'EPCI Color': 'red'  # Couleur pour la barre de l'EPCI
        }
    )

    # Mise à jour des noms dans la légende
    fig.for_each_trace(lambda t: t.update(name = t.name.replace("Default Color", "QPV")))
    fig.for_each_trace(lambda t: t.update(name = t.name.replace("EPCI Color", "EPCI")))
    # Amélioration de la mise en forme du graphique si nécessaire
    fig.update_layout(
        legend_title_text='Territoires',
        xaxis_title="Zone Géographique",
        yaxis_title="Taux de Logements Vacants (%)",
        xaxis={'categoryorder':'total descending'}  # Optionnel: Ordonner les barres par ordre décroissant
    )

    # Ajouter une ligne horizontale en tirets pour la valeur de l'EPCI
    fig.add_hline(y=indice_txvacants_epci_1, line_dash="dot")

    # Affichage du bar chart dans Streamlit
    st.plotly_chart(fig, use_container_width=True)

    #Répartition des financements
    #txLsPlai txLsPlusAv77 txLsPlusAp77 txLsPls txLsPli
    st.subheader("Part des logements sociaux selon les financements")
    st.caption("Paru le : 07/07/2023 pour le Millésime RPLS 2021 et le 23/05/2023 pour le Millésime RPLS 2019")
    st.markdown("""
      - Les logements PLAI, financés par le Prêt Locatif Aidé d’Intégration, sont attribués aux locataires en situation de grande précarité.
      - Les logements PLUS, financés par le Prêt Locatif à Usage Social correspondent aux locations HLM (habitation à loyer modéré).
      - Les logements PLS, financés par le Prêt Locatif Social, ils sont attribués aux candidats locataires ne pouvant prétendre aux locations HLM, mais ne disposant pas de revenus suffisants pour se loger dans le privé.
      - Les logements PLI, financés par le Prêt Locatif Intermédiaire et également attribués aux personnes dont les revenus sont trop élevés pour pouvoir être éligible à un logement HLM, mais trop faibles pour se loger dans le parc privé.
      """)
    df_financement_ls = pd.read_csv('./QPV/Logement/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")

    df_financement_ls_filtre = df_financement_ls[df_financement_ls['codGeo'].isin(df['CODGEO'])]
    df_financement_ls_filtre = df_financement_ls_filtre[['codGeo', 'libGeo', 'txLsPlai', 'txLsPlusAv77', 'txLsPlusAp77', 'txLsPls', 'txLsPli']]
    df_financement_ls_filtre['txLsPlai'] = df_financement_ls_filtre['txLsPlai'].str.replace(',', '.').astype(float)
    df_financement_ls_filtre['txLsPlusAv77'] = df_financement_ls_filtre['txLsPlusAv77'].str.replace(',', '.').astype(float)
    df_financement_ls_filtre['txLsPlusAp77'] = df_financement_ls_filtre['txLsPlusAp77'].str.replace(',', '.').astype(float)
    df_financement_ls_filtre['txLsPls'] = df_financement_ls_filtre['txLsPls'].str.replace(',', '.').astype(float)
    df_financement_ls_filtre['txLsPli'] = df_financement_ls_filtre['txLsPli'].str.replace(',', '.').astype(float)
    df_financement_ls_filtre.reset_index(inplace=True, drop=True)
    st.table(df_financement_ls_filtre)

    #répartition EPCI
    df_financement_ls_epci = pd.read_csv('./QPV/Logement/EPCI/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_financement_ls_epci = df_financement_ls_epci[df_financement_ls_epci['codGeo'] == code_epci ]
    df_financement_ls_epci = df_financement_ls_epci[['libGeo','txLsPlai', 'txLsPlusAv77', 'txLsPlusAp77', 'txLsPls', 'txLsPli']]
    df_financement_ls_epci['txLsPlai'] = df_financement_ls_epci['txLsPlai'].str.replace(',', '.').astype(float)
    df_financement_ls_epci['txLsPlusAv77'] = df_financement_ls_epci['txLsPlusAv77'].str.replace(',', '.').astype(float)
    df_financement_ls_epci['txLsPlusAp77'] = df_financement_ls_epci['txLsPlusAp77'].str.replace(',', '.').astype(float)
    df_financement_ls_epci['txLsPls'] = df_financement_ls_epci['txLsPls'].str.replace(',', '.').astype(float)
    df_financement_ls_epci['txLsPli'] = df_financement_ls_epci['txLsPli'].str.replace(',', '.').astype(float)
    df_financement_ls_epci.reset_index(inplace=True, drop=True)
    st.table(df_financement_ls_epci)

    # Concaténer les dataframes pour le graphique
    df_concat = pd.concat([df_financement_ls_filtre, df_financement_ls_epci], ignore_index=True)

    # Création du graphique empilé horizontal
    fig = px.bar(df_concat,
                  y="libGeo",
                  x=['txLsPlai', 'txLsPlusAv77', 'txLsPlusAp77', 'txLsPls', 'txLsPli'],
                  title="Répartition des financements par zone géographique",
                  labels={
                    "value": "Taux de logements",
                    "variable": "Type de financement",
                    "libGeo": "Zone géographique"
                  },
                  barmode='stack',
                  orientation='h'  # Ceci indique que les barres doivent être horizontales
                )
    # Renommer les éléments de la légende
    legend_names = {'txLsPlai': "PLAI", 'txLsPlusAv77': "PLUS avant 77", 'txLsPlusAp77': "PLUS après 77", 'txLsPls': "PLS", 'txLsPli': "PLI"}
    for trace in fig.data:
        trace.name = legend_names[trace.name]

    st.plotly_chart(fig)

    #Répartition des logements selon l'age de construction
    st.subheader("Répartition des logements selon l'age de construction")
    st.caption("Paru le : 07/07/2023 pour le Millésime 2019")
    df_construction = pd.read_csv('./QPV/Logement/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_construction_filtre = df_construction[df_construction['codGeo'].isin(df['CODGEO'])]
    df_construction_filtre = df_construction_filtre[['codGeo', 'libGeo', 'partResPrincAch19', 'partResPrincAch19_45', 'partResPrincAch46_70', 'partResPrincAch71_90', 'partResPrincAch91_05', 'PartResPrincAch06_15']]
    df_construction_filtre['partResPrincAch19'] = df_construction_filtre['partResPrincAch19'].str.replace(',', '.').astype(float)
    df_construction_filtre['partResPrincAch19_45'] = df_construction_filtre['partResPrincAch19_45'].str.replace(',', '.').astype(float)
    df_construction_filtre['partResPrincAch46_70'] = df_construction_filtre['partResPrincAch46_70'].str.replace(',', '.').astype(float)
    df_construction_filtre['partResPrincAch71_90'] = df_construction_filtre['partResPrincAch71_90'].str.replace(',', '.').astype(float)
    df_construction_filtre['partResPrincAch91_05'] = df_construction_filtre['partResPrincAch91_05'].str.replace(',', '.').astype(float)
    df_construction_filtre['PartResPrincAch06_15'] = df_construction_filtre['PartResPrincAch06_15'].str.replace(',', '.').astype(float)
    st.write(df_construction_filtre)

    # Création du graphique à barres empilées horizontales
    fig = go.Figure(data=[
        go.Bar(name='partResPrincAch19', y=df_construction_filtre['libGeo'], x=df_construction_filtre['partResPrincAch19'], orientation='h'),
        go.Bar(name='partResPrincAch19_45', y=df_construction_filtre['libGeo'], x=df_construction_filtre['partResPrincAch19_45'], orientation='h'),
        go.Bar(name='partResPrincAch46_70', y=df_construction_filtre['libGeo'], x=df_construction_filtre['partResPrincAch46_70'], orientation='h'),
        go.Bar(name='partResPrincAch71_90', y=df_construction_filtre['libGeo'], x=df_construction_filtre['partResPrincAch71_90'], orientation='h'),
        go.Bar(name='partResPrincAch91_05', y=df_construction_filtre['libGeo'], x=df_construction_filtre['partResPrincAch91_05'], orientation='h'),
        go.Bar(name='PartResPrincAch06_15', y=df_construction_filtre['libGeo'], x=df_construction_filtre['PartResPrincAch06_15'], orientation='h'),
    ])

    # Changement du mode d'affichage pour avoir des barres empilées et ajuster la taille
    fig.update_layout(barmode='stack', width=800, height=600)

    # Affichage du graphique avec Streamlit
    st.plotly_chart(fig)

    #répartition EPCI
    df_construction_epci = pd.read_csv('./QPV/Logement/EPCI/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_construction_epci = df_construction_epci[df_construction_epci['codGeo'] == code_epci ]
    df_construction_epci = df_construction_epci[['libGeo','partResPrincAch19', 'partResPrincAch19_45', 'partResPrincAch46_70', 'partResPrincAch71_90', 'partResPrincAch91_05', 'PartResPrincAch06_15']]
    st.table(df_construction_epci)

    #Répartition des logements sociaux selon l'age de construction
    st.subheader("Répartition des logements sociaux selon l'age de construction")
    st.caption("Paru le : 07/07/2023 pour le Millésime RPLS 2021")
    df_construction_ls = pd.read_csv('./QPV/Logement/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_construction_ls_filtre = df_construction_ls[df_construction_ls['codGeo'].isin(df['CODGEO'])]
    df_construction_ls_filtre = df_construction_ls_filtre[['codGeo', 'libGeo', 'txLsAv49', 'txLs49a75', 'txLs76a88', 'txLs89a00', 'txLs01a13', 'txLsAp13']]
    df_construction_ls_filtre['txLsAv49'] = df_construction_ls_filtre['txLsAv49'].str.replace(',', '.').astype(float)
    df_construction_ls_filtre['txLs49a75'] = df_construction_ls_filtre['txLs49a75'].str.replace(',', '.').astype(float)
    df_construction_ls_filtre['txLs76a88'] = df_construction_ls_filtre['txLs76a88'].str.replace(',', '.').astype(float)
    df_construction_ls_filtre['txLs89a00'] = df_construction_ls_filtre['txLs89a00'].str.replace(',', '.').astype(float)
    df_construction_ls_filtre['txLs01a13'] = df_construction_ls_filtre['txLs01a13'].str.replace(',', '.').astype(float)
    df_construction_ls_filtre['txLsAp13'] = df_construction_ls_filtre['txLsAp13'].str.replace(',', '.').astype(float)
    st.write(df_construction_ls_filtre)

    colors = [
        'red',        # Construction avant 1919
        'darkorange', # Construction 1919-1945
        'gold',       # Construction 1946-1970
        'yellowgreen',# Construction 1971-1990
        'limegreen',  # Construction 1991-2005
        'green'       # Construction 2006-2015
    ]
    # Création du graphique à barres empilées horizontales
    fig = go.Figure(data=[
        go.Bar(name='avant 49', y=df_construction_ls_filtre['libGeo'], x=df_construction_ls_filtre['txLsAv49'], orientation='h', marker_color=colors[0]),
        go.Bar(name='entre 49 et 75', y=df_construction_ls_filtre['libGeo'], x=df_construction_ls_filtre['txLs49a75'], orientation='h', marker_color=colors[1]),
        go.Bar(name='entre 76 et 88', y=df_construction_ls_filtre['libGeo'], x=df_construction_ls_filtre['txLs76a88'], orientation='h', marker_color=colors[2]),
        go.Bar(name='entre 89 et 00', y=df_construction_ls_filtre['libGeo'], x=df_construction_ls_filtre['txLs89a00'], orientation='h', marker_color=colors[3]),
        go.Bar(name='entre 2001 et 13', y=df_construction_ls_filtre['libGeo'], x=df_construction_ls_filtre['txLs01a13'], orientation='h', marker_color=colors[4]),
        go.Bar(name='après 2013', y=df_construction_ls_filtre['libGeo'], x=df_construction_ls_filtre['txLsAp13'], orientation='h', marker_color=colors[5]),
    ])

    # Changement du mode d'affichage pour avoir des barres empilées et ajuster la taille
    fig.update_layout(title="Années de construction des logements sociaux",barmode='stack', width=800, height=600)

    # Affichage du graphique avec Streamlit
    st.plotly_chart(fig)

    #répartition EPCI
    df_construction_ls_epci = pd.read_csv('./QPV/Logement/EPCI/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_construction_ls_epci = df_construction_ls_epci[df_construction_ls_epci['codGeo'] == code_epci ]
    df_construction_ls_epci = df_construction_ls_epci[['libGeo','txLsAv49', 'txLs49a75', 'txLs76a88', 'txLs89a00', 'txLs01a13', 'txLsAp13']]
    st.table(df_construction_ls_epci)

    #Répartition des logements sociaux selon le nombre de pièces
    st.subheader("Répartition des logements sociaux selon le nombre de pièces")
    st.caption("Paru le : 07/07/2023 pour le Millésime RPLS 2021")
    df_pieces_ls = pd.read_csv('./QPV/Logement/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_pieces_ls_filtre = df_pieces_ls[df_pieces_ls['codGeo'].isin(df['CODGEO'])]
    df_pieces_ls_filtre = df_pieces_ls_filtre[['codGeo', 'libGeo', 'txLs1p', 'txLs2p', 'txLs3p', 'txLs4p', 'txLs5pp']]
    df_pieces_ls_filtre['txLs1p'] = df_pieces_ls_filtre['txLs1p'].str.replace(',', '.').astype(float)
    df_pieces_ls_filtre['txLs2p'] = df_pieces_ls_filtre['txLs2p'].str.replace(',', '.').astype(float)
    df_pieces_ls_filtre['txLs3p'] = df_pieces_ls_filtre['txLs3p'].str.replace(',', '.').astype(float)
    df_pieces_ls_filtre['txLs4p'] = df_pieces_ls_filtre['txLs4p'].str.replace(',', '.').astype(float)
    df_pieces_ls_filtre['txLs5pp'] = df_pieces_ls_filtre['txLs5pp'].str.replace(',', '.').astype(float)
    st.write(df_pieces_ls_filtre)

    colors = [
      '#D0E8F2',  # Bleu très clair
      '#A2C4E1',  # Bleu clair
      '#739DB9',  # Bleu moyen
      '#467091',  # Bleu foncé
      '#1A4569'   # Bleu très foncé
    ]
    # Création du graphique à barres empilées horizontales
    fig = go.Figure(data=[
        go.Bar(name='1 pièce', y=df_pieces_ls_filtre['libGeo'], x=df_pieces_ls_filtre['txLs1p'], orientation='h', marker_color=colors[0]),
        go.Bar(name='2 pièces', y=df_pieces_ls_filtre['libGeo'], x=df_pieces_ls_filtre['txLs2p'], orientation='h', marker_color=colors[1]),
        go.Bar(name='3 pièces', y=df_pieces_ls_filtre['libGeo'], x=df_pieces_ls_filtre['txLs3p'], orientation='h', marker_color=colors[2]),
        go.Bar(name='4 pièces', y=df_pieces_ls_filtre['libGeo'], x=df_pieces_ls_filtre['txLs4p'], orientation='h', marker_color=colors[3]),
        go.Bar(name='5 pièces et plus', y=df_pieces_ls_filtre['libGeo'], x=df_pieces_ls_filtre['txLs5pp'], orientation='h', marker_color=colors[4]),
    ])

    # Changement du mode d'affichage pour avoir des barres empilées et ajuster la taille
    fig.update_layout(title="nombre de pièces des logements sociaux",barmode='stack', width=800, height=600)

    # Affichage du graphique avec Streamlit
    st.plotly_chart(fig)

    #répartition EPCI
    df_pieces_ls_epci = pd.read_csv('./QPV/Logement/EPCI/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_pieces_ls_epci = df_pieces_ls_epci[df_pieces_ls_epci['codGeo'] == code_epci ]
    df_pieces_ls_epci = df_pieces_ls_epci[['libGeo','txLs1p', 'txLs2p', 'txLs3p', 'txLs4p', 'txLs5pp']]
    st.table(df_pieces_ls_epci)

    #Répartition de la suroccupation des logements selon le nombre de pièces
    st.subheader("Part des résidences principales suroccupées selon le nombre de pièces")
    st.caption("Paru le : 07/07/2023 pour le Millésime 2019")
    df_suroccup = pd.read_csv('./QPV/Logement/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_suroccup_filtre = df_suroccup[df_suroccup['codGeo'].isin(df['CODGEO'])]
    df_suroccup_filtre = df_suroccup_filtre[['codGeo', 'libGeo', 'partResPrincSurocc', 'partResPrincSurocc2pi', 'partResPrincSurocc3pi', 'partResPrincSurocc4pi', 'partResPrincSurocc5pi']]
    df_suroccup_filtre['partResPrincSurocc'] = df_suroccup_filtre['partResPrincSurocc'].str.replace(',', '.').astype(float)
    df_suroccup_filtre['partResPrincSurocc2pi'] = df_suroccup_filtre['partResPrincSurocc2pi'].str.replace(',', '.').astype(float)
    df_suroccup_filtre['partResPrincSurocc3pi'] = df_suroccup_filtre['partResPrincSurocc3pi'].str.replace(',', '.').astype(float)
    df_suroccup_filtre['partResPrincSurocc4pi'] = df_suroccup_filtre['partResPrincSurocc4pi'].str.replace(',', '.').astype(float)
    df_suroccup_filtre['partResPrincSurocc5pi'] = df_suroccup_filtre['partResPrincSurocc5pi'].str.replace(',', '.').astype(float)
    st.write(df_suroccup_filtre)

    colors = [
      '#D0E8F2',  # Bleu très clair
      '#A2C4E1',  # Bleu clair
      '#739DB9',  # Bleu moyen
      '#467091',  # Bleu foncé
      '#1A4569'   # Bleu très foncé
    ]
    fig = go.Figure(data=[
        go.Bar(name='1 pièce', y=df_suroccup_filtre['libGeo'], x=df_suroccup_filtre['partResPrincSurocc'], orientation='h', marker_color=colors[0]),
        go.Bar(name='2 pièces', y=df_suroccup_filtre['libGeo'], x=df_suroccup_filtre['partResPrincSurocc2pi'], orientation='h', marker_color=colors[1]),
        go.Bar(name='3 pièces', y=df_suroccup_filtre['libGeo'], x=df_suroccup_filtre['partResPrincSurocc3pi'], orientation='h', marker_color=colors[2]),
        go.Bar(name='4 pièces', y=df_suroccup_filtre['libGeo'], x=df_suroccup_filtre['partResPrincSurocc4pi'], orientation='h', marker_color=colors[3]),
        go.Bar(name='5 pièces et plus', y=df_suroccup_filtre['libGeo'], x=df_suroccup_filtre['partResPrincSurocc5pi'], orientation='h', marker_color=colors[4]),
    ])
    fig.update_layout(title="Taux de suroccupation des logements selon leur taille",barmode='stack', width=800, height=600)
    st.plotly_chart(fig)


    #Nombre de personnes par résidences principales
    st.subheader("Nombre de personnes par résidences principales")
    st.caption("Paru le : 07/07/2023 pour le Millésime 2019")
    df_occup = pd.read_csv('./QPV/Logement/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_occup_filtre = df_occup[df_occup['codGeo'].isin(df['CODGEO'])]
    df_occup_filtre = df_occup_filtre[['codGeo', 'libGeo', 'nbPersResPrinc']]
    st.table(df_occup_filtre)

    df_occup_epci = pd.read_csv('./QPV/Logement/EPCI/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_occup_epci = df_occup_epci[df_occup_epci['codGeo'] == code_epci ]
    val_occup_epci = df_occup_epci['nbPersResPrinc'].values[0]
    st.write("Nombre de personnes par résidence principale sur l'EPCI : " + val_occup_epci)

    #Part des ménages logés gratuitement
    st.subheader("Part des ménages logés gratuitement")
    st.caption("Paru le : 07/07/2023 pour le Millésime 2019 et le 23/05/2023 pour le Millésime 2017")
    df_gratuit_1 = pd.read_csv('./QPV/Logement/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    df_gratuit_2 = pd.read_csv('./QPV/Logement/LOGT_2021.csv', dtype={"CodGeo": str}, sep=";")

    df_gratuit_filtre_1 = df_gratuit_1[df_gratuit_1['codGeo'].isin(df['CODGEO'])]
    df_gratuit_filtre_1 = df_gratuit_filtre_1[['codGeo', 'libGeo', 'partMenLogGrat']]
    df_gratuit_filtre_1 = df_gratuit_filtre_1.rename(columns={'partMenLogGrat': "Taux des ménages logés gratuitement 2019"})
    df_gratuit_filtre_1.reset_index(inplace=True, drop=True)

    df_gratuit_filtre_2 = df_gratuit_2[df_gratuit_2['codGeo'].isin(df['CODGEO'])]
    df_gratuit_filtre_2 = df_gratuit_filtre_2[['codGeo', 'libGeo', 'partMenLogGrat']]
    df_gratuit_filtre_2 = df_gratuit_filtre_2.rename(columns={'partMenLogGrat': "Taux des ménages logés gratuitement 2017"})
    df_gratuit_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_gratuit_filtre_2.merge(df_gratuit_filtre_1, on=['codGeo', 'libGeo'])
    st.table(merged_data)

    indice_gratuit_epci_1 = pd.read_csv('./QPV/Logement/EPCI/LOGT_2023.csv', dtype={"codGeo": str}, sep=";")
    desired_row = indice_gratuit_epci_1[indice_gratuit_epci_1['codGeo'] == code_epci ]
    indice_gratuit_epci_1 = desired_row['partMenLogGrat'].values[0]
    indice_gratuit_epci_2 = pd.read_csv('./QPV/Logement/EPCI/LOGT_2021.csv', dtype={"codGeo": str}, sep=";")
    desired_row = indice_gratuit_epci_2[indice_gratuit_epci_2['codGeo'] == code_epci ]
    indice_gratuit_epci_2 = desired_row['partMenLogGrat'].values[0]
    st.write("Taux des ménages logés gratuitement epci 2019: " + indice_gratuit_epci_1)
    st.write("Taux des ménages logés gratuitement epci 2017: " + indice_gratuit_epci_2)



    st.header("ÉDUCATION ET FORMATION")
    #16-25 ans non scolarisés et sans emploi
    st.subheader("16-25 ans non scolarisés et sans emploi")
    st.caption("Paru le 14/12/2022 pour l'année 2020-2021 et le 23/01/2020 pour l'année scolaire 2017-2018")
    df_neet_1 = pd.read_csv('./QPV/Education/EDUC_2022.csv', dtype={"CODGEO": str}, sep=";")
    df_neet_2 = pd.read_csv('./QPV/Education/EDUC_2019.csv', dtype={"CODGEO": str}, sep=";")

    df_neet_filtre_1 = df_neet_1[df_neet_1['CODGEO'].isin(df['CODGEO'])]
    df_neet_filtre_1 = df_neet_filtre_1[['CODGEO', 'LIBGEO', 'TX_NSNE_16A25']]
    df_neet_filtre_1 = df_neet_filtre_1.rename(columns={'TX_NSNE_16A25': "NEETs 2020-2021"})
    df_neet_filtre_1.reset_index(inplace=True, drop=True)

    df_neet_filtre_2 = df_neet_2[df_neet_2['CODGEO'].isin(df['CODGEO'])]
    df_neet_filtre_2 = df_neet_filtre_2[['CODGEO', 'LIBGEO', 'TX_NSNE_16A25']]
    df_neet_filtre_2 = df_neet_filtre_2.rename(columns={'TX_NSNE_16A25': "NEETs 2017-2018"})
    df_neet_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_neet_filtre_2.merge(df_neet_filtre_1, on=['CODGEO', 'LIBGEO'])
    st.table(merged_data)

    indice_neet_epci_1 = pd.read_csv('./QPV/Education/EPCI/EDUC_2022.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = indice_neet_epci_1[indice_neet_epci_1['CODGEO'] == code_epci ]
    indice_neet_epci_1 = desired_row['TX_NSNE_16A25'].values[0]
    st.write("Taux de NEETs epci 2020-201: " + str(indice_neet_epci_1))

    indice_neet_epci_2 = pd.read_csv('./QPV/Education/EPCI/EDUC_2019.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = indice_neet_epci_2[indice_neet_epci_2['CODGEO'] == code_epci ]
    indice_neet_epci_2 = desired_row['TX_NSNE_16A25'].values[0]
    st.write("Taux de NEETs epci 2017-2018: " + str(indice_neet_epci_2))

    #Part des retards en 6e
    st.subheader("Part des retards en 6e")
    st.caption("Paru le : 14/12/2022 pour l'année scolaire 2020-2021 et le 01/2020 pour l'année scolaire 2015-2016")
    df_retard6e_1 = pd.read_csv('./QPV/Education/EDUC_2022.csv', dtype={"CODGEO": str}, sep=";")
    df_retard6e_2 = pd.read_csv('./QPV/Education/EDUC_2017.csv', dtype={"CODGEO": str}, sep=";")

    df_retard6e_filtre_1 = df_retard6e_1[df_retard6e_1['CODGEO'].isin(df['CODGEO'])]
    df_retard6e_filtre_1 = df_retard6e_filtre_1[['CODGEO', 'LIBGEO', 'EFF_E6', 'RET_E6']]
    df_retard6e_filtre_1['RET_E6'] = pd.to_numeric(df_retard6e_filtre_1['RET_E6'], errors='coerce')
    df_retard6e_filtre_1['EFF_E6'] = pd.to_numeric(df_retard6e_filtre_1['EFF_E6'], errors='coerce')
    df_retard6e_filtre_1['tx_retard6e'] = df_retard6e_filtre_1['RET_E6'] / df_retard6e_filtre_1['EFF_E6']
    df_retard6e_filtre_1 = df_retard6e_filtre_1.rename(columns={'tx_retard6e': "Taux de retard scolaire en 6e 2020-2021"})
    df_retard6e_filtre_1.reset_index(inplace=True, drop=True)
    df_retard6e_filtre_2 = df_retard6e_2[df_retard6e_2['CODGEO'].isin(df['CODGEO'])]
    df_retard6e_filtre_2 = df_retard6e_filtre_2[['CODGEO', 'LIBGEO', 'EFF_E6', 'RET_E6']]
    df_retard6e_filtre_2['RET_E6'] = pd.to_numeric(df_retard6e_filtre_2['RET_E6'], errors='coerce')
    df_retard6e_filtre_2['EFF_E6'] = pd.to_numeric(df_retard6e_filtre_2['EFF_E6'], errors='coerce')
    df_retard6e_filtre_2['tx_retard6e'] = df_retard6e_filtre_2['RET_E6'] / df_retard6e_filtre_2['EFF_E6']
    df_retard6e_filtre_2 = df_retard6e_filtre_2.rename(columns={'tx_retard6e': "Taux de retard scolaire en 6e 2015-2016"})
    df_retard6e_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_retard6e_filtre_2.merge(df_retard6e_filtre_1, on=['CODGEO', 'LIBGEO'])
    st.table(merged_data)

    retard6e_epci_1 = pd.read_csv('./QPV/Education/EPCI/EDUC_2022.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = retard6e_epci_1[retard6e_epci_1['CODGEO'] == code_epci ]
    desired_row['RET_E6'] = desired_row['RET_E6'].replace('\u202f', '').astype(float)
    desired_row['EFF_E6'] = desired_row['EFF_E6'].replace('\u202f', '').astype(float)
    desired_row['tx_retard6e'] = desired_row['RET_E6'] / desired_row['EFF_E6']
    retard6e_epci_1 = desired_row['tx_retard6e'].values[0]
    retard6e_epci_2 = pd.read_csv('./QPV/Education/EPCI/EDUC_2017.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = retard6e_epci_2[retard6e_epci_2['CODGEO'] == code_epci ]
    desired_row['RET_E6'] = desired_row['RET_E6'].replace('\u202f', '').astype(float)
    desired_row['EFF_E6'] = desired_row['EFF_E6'].astype(str).str.replace('\u202f', '').astype(float)
    desired_row['tx_retard6e'] = desired_row['RET_E6'] / desired_row['EFF_E6']
    retard6e_epci_2 = desired_row['tx_retard6e'].values[0]
    st.write("Taux de retard en 6e epci 2020-2021 : " + str(retard6e_epci_1))
    st.write("Taux de retard en 6e epci 2015-2016 : " + str(retard6e_epci_2))


    #Part des retards en 3e
    st.subheader("Part des retards en 3e")
    st.caption("Paru le : 14/12/2022 pour l'année scolaire 2020-2021 et le 01/2020 pour l'année scolaire 2015-2016")
    df_retard3e_1 = pd.read_csv('./QPV/Education/EDUC_2022.csv', dtype={"CODGEO": str}, sep=";")
    df_retard3e_2 = pd.read_csv('./QPV/Education/EDUC_2017.csv', dtype={"CODGEO": str}, sep=";")

    df_retard3e_filtre_1 = df_retard3e_1[df_retard3e_1['CODGEO'].isin(df['CODGEO'])]
    df_retard3e_filtre_1 = df_retard3e_filtre_1[['CODGEO', 'LIBGEO', 'EFF_E3', 'RET_E3']]
    df_retard3e_filtre_1['RET_E3'] = pd.to_numeric(df_retard3e_filtre_1['RET_E3'], errors='coerce')
    df_retard3e_filtre_1['EFF_E3'] = pd.to_numeric(df_retard3e_filtre_1['EFF_E3'], errors='coerce')
    df_retard3e_filtre_1['tx_retard3e'] = df_retard3e_filtre_1['RET_E3'] / df_retard3e_filtre_1['EFF_E3']
    df_retard3e_filtre_1 = df_retard3e_filtre_1.rename(columns={'tx_retard3e': "Taux de retard scolaire en 3e 2020-2021"})
    df_retard3e_filtre_1.reset_index(inplace=True, drop=True)
    df_retard3e_filtre_2 = df_retard3e_2[df_retard3e_2['CODGEO'].isin(df['CODGEO'])]
    df_retard3e_filtre_2 = df_retard3e_filtre_2[['CODGEO', 'LIBGEO', 'EFF_E3', 'RET_E3']]
    df_retard3e_filtre_2['RET_E3'] = pd.to_numeric(df_retard3e_filtre_2['RET_E3'], errors='coerce')
    df_retard3e_filtre_2['EFF_E3'] = pd.to_numeric(df_retard3e_filtre_2['EFF_E3'], errors='coerce')
    df_retard3e_filtre_2['tx_retard3e'] = df_retard3e_filtre_2['RET_E3'] / df_retard3e_filtre_2['EFF_E3']
    df_retard3e_filtre_2 = df_retard3e_filtre_2.rename(columns={'tx_retard3e': "Taux de retard scolaire en 3e 2015-2016"})
    df_retard3e_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_retard3e_filtre_2.merge(df_retard3e_filtre_1, on=['CODGEO', 'LIBGEO'])
    st.table(merged_data)

    retard3e_epci_1 = pd.read_csv('./QPV/Education/EPCI/EDUC_2022.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = retard3e_epci_1[retard3e_epci_1['CODGEO'] == code_epci ]
    desired_row['RET_E3'] = desired_row['RET_E3'].replace('\u202f', '').astype(float)
    desired_row['EFF_E3'] = desired_row['EFF_E3'].replace('\u202f', '').astype(float)
    desired_row['tx_retard3e'] = desired_row['RET_E3'] / desired_row['EFF_E3']
    retard3e_epci_1 = desired_row['tx_retard3e'].values[0]
    retard3e_epci_2 = pd.read_csv('./QPV/Education/EPCI/EDUC_2017.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = retard3e_epci_2[retard3e_epci_2['CODGEO'] == code_epci ]
    desired_row['RET_E3'] = desired_row['RET_E3'].replace('\u202f', '').astype(float)
    desired_row['EFF_E3'] = desired_row['EFF_E3'].astype(str).str.replace('\u202f', '').astype(float)
    desired_row['tx_retard3e'] = desired_row['RET_E3'] / desired_row['EFF_E3']
    retard3e_epci_2 = desired_row['tx_retard3e'].values[0]
    st.write("Taux de retard en 3e epci 2020-2021 : " + str(retard3e_epci_1))
    st.write("Taux de retard en 3e epci 2015-2016 : " + str(retard3e_epci_2))

    #Part des retards en terminale générale ou technologique
    st.subheader("Part des retards en terminale générale ou technologique")
    st.caption("Paru le : 14/12/2022 pour l'année scolaire 2020-2021 et le 01/2020 pour l'année scolaire 2015-2016")
    df_retardterminale_1 = pd.read_csv('./QPV/Education/EDUC_2022.csv', dtype={"CODGEO": str}, sep=";")
    df_retardterminale_2 = pd.read_csv('./QPV/Education/EDUC_2017.csv', dtype={"CODGEO": str}, sep=";")

    df_retardterminale_filtre_1 = df_retardterminale_1[df_retardterminale_1['CODGEO'].isin(df['CODGEO'])]
    df_retardterminale_filtre_1 = df_retardterminale_filtre_1[['CODGEO', 'LIBGEO', 'EFF_E0_GT', 'RET_E0_GT']]
    df_retardterminale_filtre_1['RET_E0_GT'] = pd.to_numeric(df_retardterminale_filtre_1['RET_E0_GT'], errors='coerce')
    df_retardterminale_filtre_1['EFF_E0_GT'] = pd.to_numeric(df_retardterminale_filtre_1['EFF_E0_GT'], errors='coerce')
    df_retardterminale_filtre_1['tx_retardterminale'] = df_retardterminale_filtre_1['RET_E0_GT'] / df_retardterminale_filtre_1['EFF_E0_GT']
    df_retardterminale_filtre_1 = df_retardterminale_filtre_1.rename(columns={'tx_retardterminale': "Taux de retard scolaire en terminale générale et technologique 2020-2021"})
    df_retardterminale_filtre_1.reset_index(inplace=True, drop=True)
    df_retardterminale_filtre_2 = df_retardterminale_2[df_retardterminale_2['CODGEO'].isin(df['CODGEO'])]
    df_retardterminale_filtre_2 = df_retardterminale_2[['CODGEO', 'LIBGEO', 'EFF_E0_GT', 'RET_E0_GT']]
    df_retardterminale_filtre_2['RET_E0_GT'] = pd.to_numeric(df_retardterminale_filtre_2['RET_E0_GT'], errors='coerce')
    df_retardterminale_filtre_2['EFF_E0_GT'] = pd.to_numeric(df_retardterminale_filtre_2['EFF_E0_GT'], errors='coerce')
    df_retardterminale_filtre_2['tx_retardterminale'] = df_retardterminale_filtre_2['RET_E0_GT'] / df_retardterminale_filtre_2['EFF_E0_GT']
    df_retardterminale_filtre_2 = df_retardterminale_filtre_2.rename(columns={'tx_retardterminale': "Taux de retard scolaire en terminale générale et technologique 2015-2016"})
    df_retardterminale_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_retardterminale_filtre_2.merge(df_retardterminale_filtre_1, on=['CODGEO', 'LIBGEO'])
    st.table(merged_data)

    retardterminale_epci_1 = pd.read_csv('./QPV/Education/EPCI/EDUC_2022.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = retardterminale_epci_1[retardterminale_epci_1['CODGEO'] == code_epci ]
    desired_row['RET_E0_GT'] = desired_row['RET_E0_GT'].replace('\u202f', '').astype(float)
    desired_row['EFF_E0_GT'] = desired_row['EFF_E0_GT'].replace('\u202f', '').astype(float)
    desired_row['tx_retardterminale'] = desired_row['RET_E0_GT'] / desired_row['EFF_E0_GT']
    retardterminale_epci_1 = desired_row['tx_retardterminale'].values[0]
    retardterminale_epci_2 = pd.read_csv('./QPV/Education/EPCI/EDUC_2017.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = retardterminale_epci_2[retardterminale_epci_2['CODGEO'] == code_epci ]
    desired_row['RET_E0_GT'] = desired_row['RET_E0_GT'].replace('\u202f', '').astype(float)
    desired_row['EFF_E0_GT'] = desired_row['EFF_E0_GT'].astype(str).str.replace('\u202f', '').astype(float)
    desired_row['tx_retardterminale'] = desired_row['RET_E0_GT'] / desired_row['EFF_E0_GT']
    retardterminale_epci_2 = desired_row['tx_retardterminale'].values[0]
    st.write("Taux de retard en terminale générale et technologique epci 2020-2021 : " + str(retardterminale_epci_1))
    st.write("Taux de retard en terminale générale et technologique epci 2015-2016 : " + str(retardterminale_epci_2))


    #Part des retards en terminale professionnelle
    st.subheader("Part des retards en terminale professionnelle")
    st.caption("Paru le : 14/12/2022 pour l'année scolaire 2020-2021 et le 01/2020 pour l'année scolaire 2015-2016")
    df_retardterminalepro_1 = pd.read_csv('./QPV/Education/EDUC_2022.csv', dtype={"CODGEO": str}, sep=";")
    df_retardterminalepro_2 = pd.read_csv('./QPV/Education/EDUC_2017.csv', dtype={"CODGEO": str}, sep=";")

    df_retardterminalepro_filtre_1 = df_retardterminalepro_1[df_retardterminalepro_1['CODGEO'].isin(df['CODGEO'])]
    df_retardterminalepro_filtre_1 = df_retardterminalepro_filtre_1[['CODGEO', 'LIBGEO', 'EFF_E0_PRO', 'RET_E0_PRO']]
    df_retardterminalepro_filtre_1['RET_E0_PRO'] = pd.to_numeric(df_retardterminalepro_filtre_1['RET_E0_PRO'], errors='coerce')
    df_retardterminalepro_filtre_1['EFF_E0_PRO'] = pd.to_numeric(df_retardterminalepro_filtre_1['EFF_E0_PRO'], errors='coerce')
    df_retardterminalepro_filtre_1['tx_retardterminalepro'] = df_retardterminalepro_filtre_1['RET_E0_PRO'] / df_retardterminalepro_filtre_1['EFF_E0_PRO']
    df_retardterminalepro_filtre_1 = df_retardterminalepro_filtre_1.rename(columns={'tx_retardterminalepro': "Taux de retard scolaire en terminale professionnelle 2020-2021"})
    df_retardterminalepro_filtre_1.reset_index(inplace=True, drop=True)
    df_retardterminalepro_filtre_2 = df_retardterminalepro_2[df_retardterminalepro_2['CODGEO'].isin(df['CODGEO'])]
    df_retardterminalepro_filtre_2 = df_retardterminalepro_filtre_2[['CODGEO', 'LIBGEO', 'EFF_E0_PRO', 'RET_E0_PRO']]
    df_retardterminalepro_filtre_2['RET_E0_PRO'] = pd.to_numeric(df_retardterminalepro_filtre_2['RET_E0_PRO'], errors='coerce')
    df_retardterminalepro_filtre_2['EFF_E0_PRO'] = pd.to_numeric(df_retardterminalepro_filtre_2['EFF_E0_PRO'], errors='coerce')
    df_retardterminalepro_filtre_2['tx_retardterminalepro'] = df_retardterminalepro_filtre_2['RET_E0_PRO'] / df_retardterminalepro_filtre_2['EFF_E0_PRO']
    df_retardterminalepro_filtre_2 = df_retardterminalepro_filtre_2.rename(columns={'tx_retardterminalepro': "Taux de retard scolaire en terminale professionnelle 2015-2016"})
    df_retardterminalepro_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_retardterminalepro_filtre_2.merge(df_retardterminalepro_filtre_1, on=['CODGEO', 'LIBGEO'])
    st.table(merged_data)

    retardterminalepro_epci_1 = pd.read_csv('./QPV/Education/EPCI/EDUC_2022.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = retardterminalepro_epci_1[retardterminalepro_epci_1['CODGEO'] == code_epci ]
    desired_row['RET_E0_PRO'] = desired_row['RET_E0_PRO'].replace('\u202f', '').astype(float)
    desired_row['EFF_E0_PRO'] = desired_row['EFF_E0_PRO'].replace('\u202f', '').astype(float)
    desired_row['tx_retardterminalepro'] = desired_row['RET_E0_PRO'] / desired_row['EFF_E0_PRO']
    retardterminalepro_epci_1 = desired_row['tx_retardterminalepro'].values[0]
    retardterminalepro_epci_2 = pd.read_csv('./QPV/Education/EPCI/EDUC_2017.csv', dtype={"CODGEO": str}, sep=";")
    desired_row = retardterminalepro_epci_2[retardterminalepro_epci_2['CODGEO'] == code_epci ]
    desired_row['RET_E0_PRO'] = desired_row['RET_E0_PRO'].replace('\u202f', '').astype(float)
    desired_row['EFF_E0_PRO'] = desired_row['EFF_E0_PRO'].astype(str).str.replace('\u202f', '').astype(float)
    desired_row['tx_retardterminalepro'] = desired_row['RET_E0_PRO'] / desired_row['EFF_E0_PRO']
    retardterminalepro_epci_2 = desired_row['tx_retardterminalepro'].values[0]
    st.write("Taux de retard en terminale professionnelle epci 2020-2021 : " + str(retardterminalepro_epci_1))
    st.write("Taux de retard en terminale professionnelle epci 2015-2016 : " + str(retardterminalepro_epci_2))

    st.header("EMPLOI")
    #DEFM ABCDE
    st.subheader("Nombre de DEFM ABCDE")
    st.caption("Paru le :  01/08/2023 pour le Millésime du 31/12/2022 et le 08/10/2018 pour le Millésime du 31/12/2016")
    df_defm_1 = pd.read_csv('./QPV/Emploi/DEFM2022.csv', dtype={"CODGEO": str}, sep=";")
    df_defm_2 = pd.read_csv('./QPV/Emploi/DEFM2016.csv', dtype={"CODGEO": str}, sep=";")

    df_defm_filtre_1 = df_defm_1[df_defm_1['CODGEO'].isin(df['CODGEO'])]
    df_defm_filtre_1 = df_defm_filtre_1[['CODGEO', 'LIBGEO', 'ABCDE']]
    df_defm_filtre_1 = df_defm_filtre_1.rename(columns={'ABCDE': "Nombre de DEFM ABCDE au 31/12/2022"})
    df_defm_filtre_1.reset_index(inplace=True, drop=True)

    df_defm_filtre_2 = df_defm_2[df_defm_2['CODGEO'].isin(df['CODGEO'])]
    df_defm_filtre_2 = df_defm_filtre_2[['CODGEO', 'LIBGEO', 'ABCDE']]
    df_defm_filtre_2 = df_defm_filtre_2.rename(columns={'ABCDE': "Nombre de DEFM ABCDE au 31/12/2016"})
    df_defm_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_defm_filtre_2.merge(df_defm_filtre_1, on=['CODGEO', 'LIBGEO'])
    st.table(merged_data)

    st.header("INSERTION PROFESSIONNELLE")
    #FILTRE QPV
    st.caption("Millésime 2017")
    df_insertion_pro = pd.read_csv('./QPV/insertion_pro/IPRO_2017.csv', dtype={"CODGEO": str}, sep=";")
    df_insertion_pro = df_insertion_pro[df_insertion_pro['CODGEO'].isin(df['CODGEO'])]
    def convert_df(df):
      # IMPORTANT: Cache the conversion to prevent computation on every rerun
      return df.to_csv().encode('utf-8')
    csv = convert_df(df_insertion_pro)
    st.download_button(
      label="💾 Télécharger les données",
      data=csv,
      file_name='insertion_pro_qpv_2017.csv',
      mime='text/csv',
    )

    st.caption("Millésime 2023")
    df_insertion_pro = pd.read_csv('./QPV/insertion_pro/IPRO_2023.csv', dtype={"CODGEO": str}, sep=";")
    df_insertion_pro = df_insertion_pro[df_insertion_pro['CODGEO'].isin(df['CODGEO'])]
    csv = convert_df(df_insertion_pro)
    st.download_button(
      label="💾 Télécharger les données",
      data=csv,
      file_name='insertion_pro_qpv_2023.csv',
      mime='text/csv',
    )

    st.header("TISSU ECONOMIQUE")
    #FILTRE QPV
    st.caption("Millésime 2017")
    df_tissu_eco = pd.read_csv('./QPV/tissu_eco/TECO_2017.csv', dtype={"CODGEO": str}, sep=";")
    df_tissu_eco = df_tissu_eco[df_tissu_eco['CODGEO'].isin(df['CODGEO'])]
    csv = convert_df(df_tissu_eco)
    st.download_button(
      label="💾 Télécharger les données",
      data=csv,
      file_name='df_tissu_eco_qpv_2017.csv',
      mime='text/csv',
    )

    st.caption("Millésime 2023")
    df_tissu_eco = pd.read_csv('./QPV/tissu_eco/TECO_2023.csv', dtype={"CODGEO": str}, sep=";")
    df_tissu_eco = df_tissu_eco[df_tissu_eco['CODGEO'].isin(df['CODGEO'])]
    csv = convert_df(df_tissu_eco)
    st.download_button(
      label="💾 Télécharger les données",
      data=csv,
      file_name='df_tissu_eco_qpv_2023.csv',
      mime='text/csv',
    )

  st.subheader("IRIS concernés par un QPV")
  uploaded_file_iris = st.file_uploader("Uploader un fichier csv contenant les coordonnées geo des IRIS dans une colonne CODGEO")
  if uploaded_file_iris is not None:
    df = pd.read_csv(uploaded_file_iris, dtype={"CODGEO": str}, sep=";")

    st.header("EDUCATION ET FORMATION (IRIS)")
    #Part des non scolarisés sans diplome
    st.subheader("Part des non scolarisés sans diplome")
    st.caption("Paru le 19/10/2023 pour le Millésime 2020 et le 18/10/2018 pour le Millésime 2015")
    df_sans_dipl_1 = pd.read_csv('./QPV/Education/IRIS/base-ic-diplomes-formation-2020.csv', dtype={"IRIS": str}, sep=";")
    df_sans_dipl_2 = pd.read_csv('./QPV/Education/IRIS/base-ic-diplomes-formation-2015.csv', dtype={"IRIS": str}, sep=";")
    df_sans_dipl_filtre_1 = df_sans_dipl_1[df_sans_dipl_1['IRIS'].isin(df['CODGEO'])]
    df_sans_dipl_filtre_1 = df_sans_dipl_filtre_1[['IRIS', 'LIBIRIS', 'P20_NSCOL15P', 'P20_NSCOL15P_DIPLMIN']]
    df_sans_dipl_filtre_1['P20_NSCOL15P'] = df_sans_dipl_filtre_1['P20_NSCOL15P'].astype(str).str.replace('\u202f', '').astype(float)
    df_sans_dipl_filtre_1['P20_NSCOL15P_DIPLMIN'] = df_sans_dipl_filtre_1['P20_NSCOL15P_DIPLMIN'].astype(str).str.replace('\u202f', '').astype(float)
    df_sans_dipl_filtre_1['tx_sans_dipl'] = ( df_sans_dipl_filtre_1['P20_NSCOL15P_DIPLMIN'] / df_sans_dipl_filtre_1['P20_NSCOL15P'] ) * 100
    df_sans_dipl_filtre_1.reset_index(inplace=True, drop=True)

    df_sans_dipl_filtre_2 = df_sans_dipl_2[df_sans_dipl_2['IRIS'].isin(df['CODGEO'])]
    df_sans_dipl_filtre_2 = df_sans_dipl_filtre_2[['IRIS', 'LIBIRIS', 'P15_NSCOL15P', 'P15_NSCOL15P_DIPLMIN']]
    df_sans_dipl_filtre_2['P15_NSCOL15P'] = df_sans_dipl_filtre_2['P15_NSCOL15P'].astype(str).str.replace('\u202f', '').astype(float)
    df_sans_dipl_filtre_2['P15_NSCOL15P_DIPLMIN'] = df_sans_dipl_filtre_2['P15_NSCOL15P_DIPLMIN'].astype(str).str.replace('\u202f', '').astype(float)
    df_sans_dipl_filtre_2['tx_sans_dipl'] = ( df_sans_dipl_filtre_2['P15_NSCOL15P_DIPLMIN'] / df_sans_dipl_filtre_2['P15_NSCOL15P'] ) * 100
    df_sans_dipl_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_sans_dipl_filtre_2.merge(df_sans_dipl_filtre_1, on=['IRIS'])
    st.table(merged_data)

    #Part des non scolarisés diplome études supérieures
    st.subheader("Part des personnes non scolarisées de 15 ans ou plus titulaires d'un diplôme de l'enseignement supérieur de niveau Bac + 2 et plus")
    st.caption("Paru le 19/10/2023 pour le Millésime 2020 et le 18/10/2018 pour le Millésime 2015")
    df_dipl_sup_1 = pd.read_csv('./QPV/Education/IRIS/base-ic-diplomes-formation-2020.csv', dtype={"IRIS": str}, sep=";")
    df_dipl_sup_2 = pd.read_csv('./QPV/Education/IRIS/base-ic-diplomes-formation-2015.csv', dtype={"IRIS": str}, sep=";")
    df_dipl_sup_filtre_1 = df_dipl_sup_1[df_dipl_sup_1['IRIS'].isin(df['CODGEO'])]
    df_dipl_sup_filtre_1 = df_dipl_sup_filtre_1[['IRIS', 'LIBIRIS', 'P20_NSCOL15P', 'P20_NSCOL15P_SUP2', 'P20_NSCOL15P_SUP34', 'P20_NSCOL15P_SUP5']]
    df_dipl_sup_filtre_1['P20_NSCOL15P'] = df_dipl_sup_filtre_1['P20_NSCOL15P'].astype(str).str.replace('\u202f', '').astype(float)
    df_dipl_sup_filtre_1['P20_NSCOL15P_SUP2'] = df_dipl_sup_filtre_1['P20_NSCOL15P_SUP2'].astype(str).str.replace('\u202f', '').astype(float)
    df_dipl_sup_filtre_1['P20_NSCOL15P_SUP34'] = df_dipl_sup_filtre_1['P20_NSCOL15P_SUP34'].astype(str).str.replace('\u202f', '').astype(float)
    df_dipl_sup_filtre_1['P20_NSCOL15P_SUP5'] = df_dipl_sup_filtre_1['P20_NSCOL15P_SUP5'].astype(str).str.replace('\u202f', '').astype(float)
    df_dipl_sup_filtre_1['tx_dipl_etude_sup'] = ( ( df_dipl_sup_filtre_1['P20_NSCOL15P_SUP2'] + df_dipl_sup_filtre_1['P20_NSCOL15P_SUP34'] + df_dipl_sup_filtre_1['P20_NSCOL15P_SUP5'] ) / df_dipl_sup_filtre_1['P20_NSCOL15P'] ) * 100
    df_dipl_sup_filtre_1.reset_index(inplace=True, drop=True)

    df_dipl_sup_filtre_2 = df_dipl_sup_2[df_dipl_sup_2['IRIS'].isin(df['CODGEO'])]
    df_dipl_sup_filtre_2 = df_dipl_sup_filtre_2[['IRIS', 'LIBIRIS', 'P15_NSCOL15P', 'P15_NSCOL15P_SUP']]
    df_dipl_sup_filtre_2['P15_NSCOL15P'] = df_dipl_sup_filtre_2['P15_NSCOL15P'].astype(str).str.replace('\u202f', '').astype(float)
    df_dipl_sup_filtre_2['P15_NSCOL15P_SUP'] = df_dipl_sup_filtre_2['P15_NSCOL15P_SUP'].astype(str).str.replace('\u202f', '').astype(float)
    df_dipl_sup_filtre_2['tx_dipl_etude_sup'] = ( df_dipl_sup_filtre_2['P15_NSCOL15P_SUP'] / df_dipl_sup_filtre_2['P15_NSCOL15P'] ) * 100
    df_dipl_sup_filtre_2.reset_index(inplace=True, drop=True)

    merged_data = df_dipl_sup_filtre_2.merge(df_dipl_sup_filtre_1, on=['IRIS'])
    st.table(merged_data)




