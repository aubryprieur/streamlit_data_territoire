import streamlit as st
from multiapp import MultiApp
from pages import accueil, population, revenu, activite, personnes_agees, familles, petite_enfance, jeunesse, diplomes, logement, caf, sante, tranquilite, epci, qpv # import your app modules here

app = MultiApp()

# Add all your application here
app.add_app("Accueil", accueil.app)
app.add_app("Population", population.app)
app.add_app("Revenu", revenu.app)
app.add_app("Activité-Emploi", activite.app)
app.add_app("Personnes âgées", personnes_agees.app)
app.add_app("Familles", familles.app)
app.add_app("Petite enfance", petite_enfance.app)
app.add_app("Jeunesse", jeunesse.app)
app.add_app("Diplômes", diplomes.app)
app.add_app("Logement", logement.app)
app.add_app("CAF", caf.app)
app.add_app("Santé", sante.app)
app.add_app("Tranquilité", tranquilite.app)
app.add_app("Epci", epci.app)
app.add_app("Qpv", qpv.app)

# The main app
app.run()
