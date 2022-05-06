import streamlit as st
from multiapp import MultiApp
from pages import test, carte, population, revenu, activite, personnes_agees, familles, jeunesse, diplomes, logement, caf, sante, synthese # import your app modules here

app = MultiApp()

# Add all your application here
app.add_app("Accueil", test.app)
app.add_app("Test carte", carte.app)
app.add_app("Population", population.app)
app.add_app("Revenu", revenu.app)
app.add_app("Activité-Emploi", activite.app)
app.add_app("Personnes âgées", personnes_agees.app)
app.add_app("Familles", familles.app)
app.add_app("Jeunesse", jeunesse.app)
app.add_app("Diplômes", diplomes.app)
app.add_app("Logement", logement.app)
app.add_app("CAF", caf.app)
app.add_app("Santé", sante.app)
app.add_app("Synthèse", synthese.app)

# The main app
app.run()
