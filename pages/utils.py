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
