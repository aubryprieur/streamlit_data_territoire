import pandas as pd
import streamlit as st

# Fonction pour enlever les virgules des milliers
def remove_comma(x):
    try:
        # Convertir en float et formater sans virgules
        return '{:.0f}'.format(float(x))
    except ValueError:
        # Retourner la valeur originale si la conversion échoue
        return x

# Arrondir à 2 chiffres après la virgule
def round_to_two(x):
    try:
        # Convertir en float et arrondir à deux chiffres après la virgule
        return round(float(x), 2)
    except (ValueError, TypeError):
        # Retourner la valeur originale si la conversion ou l'arrondi échoue
        return x

# Arrondir à 0 chiffre après la virgule
def round_to_zero(x):
    try:
        # Convertir en float et arrondir à l'entier le plus proche
        return round(float(x))
    except (ValueError, TypeError):
        # Retourner la valeur originale si la conversion ou l'arrondi échoue
        return x

# Sidebar et sélection des territoires
def afficher_infos_commune():
    # Lecture du fichier CSV des communes
    df_commune = pd.read_csv("./commune_2021.csv", sep=",")
    # Fusionner les colonnes "LIBELLE" et "COM" pour créer des options uniques
    df_commune['LIBELLE_COM'] = df_commune['LIBELLE'] + ' - ' + df_commune['COM'].astype(str)
    # Création de la liste des options pour la selectbox
    list_commune = df_commune['LIBELLE_COM']

    # Création de la selectbox avec les options fusionnées
    selection = st.sidebar.selectbox("Sélectionnez votre commune :", options=list_commune)

    # Extraire le nom de la commune et le code INSEE à partir de l'option sélectionnée
    selected_commune = df_commune[df_commune['LIBELLE_COM'] == selection]
    nom_commune = selected_commune['LIBELLE'].iloc[0]
    code_commune = selected_commune['COM'].iloc[0]

    # Affichage des résultats dans la sidebar
    st.sidebar.write('Ma commune:', code_commune, nom_commune)

    # Lecture du fichier CSV des EPCI
    df_epci = pd.read_csv("./EPCI_2020.csv", sep=";")
    nom_epci = df_epci.loc[df_epci['CODGEO'] == code_commune, 'LIBEPCI'].iloc[0]
    code_epci = df_epci.loc[df_epci['CODGEO'] == code_commune, 'EPCI'].iloc[0]
    st.sidebar.write('Mon EPCI:', code_epci, nom_epci)

    # Déterminer le département
    code_departement = df_commune.loc[df_commune['COM'] == code_commune, 'DEP'].iloc[0]
    df_departement = pd.read_csv("./departement2021.csv", dtype={"CHEFLIEU": str}, sep=",")
    nom_departement = df_departement.loc[df_departement['DEP'] == code_departement, 'LIBELLE'].iloc[0]
    st.sidebar.write('Mon département:', code_departement, nom_departement)

    # Déterminer la région
    code_region = df_commune.loc[df_commune['COM'] == code_commune, 'REG'].iloc[0]
    code_region = str(round(code_region))
    # Lecture du fichier CSV des régions
    df_region = pd.read_csv("./region2021.csv", dtype={"REG": str, "CHEFLIEU": str}, sep=",")
    # Vérifier la correspondance avant d'accéder à l'élément
    if code_region in df_region['REG'].values:
        nom_region = df_region.loc[df_region['REG'] == code_region, 'LIBELLE'].iloc[0]
    else:
        nom_region = "Région non trouvée"
    st.sidebar.write('Ma région:', code_region, nom_region)

    return code_commune, nom_commune, code_epci, nom_epci, code_departement, nom_departement, code_region, nom_region

