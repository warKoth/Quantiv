import os 


def CreateCsv():
    """Crée un fichier CSV vide avec les en-têtes appropriés s'il n'existe pas déjà."""
    filename = "Bd.csv"
    if not os.path.isfile(filename):
        with open( filename, 'w', encoding = "utf-8") as file:
            file.write("Nom, Prénom, Groupe, [Données] \n")

def ReadCsv():
    """Lit le fichier CSV et retourne les données sous forme de liste de dictionnaires."""
    filename = "Bd.csv"
    data = []
    if os.path.isfile(filename):
        with open( filename, 'r', encoding = "utf-8") as file:
            lines = file.readlines()
            headers = lines[0].strip().split(", ")
            for line in lines[1:]:
                values = line.strip().split(", ")
                entry = {headers[i]: values[i] for i in range(len(headers))}
                data.append(entry)
    return data

def WriteCsv(data):
    """Écrit les données dans le fichier CSV."""
    filename = "Bd.csv"
    with open( filename, 'a', encoding = "utf-8") as file:
        if data:
            headers = data[0].keys()
            file.write(", ".join(headers) + "\n")
            for entry in data:
                values = [str(entry[header]) for header in headers]
                file.write(", ".join(values) + "\n")
        else:
            file.write("Nom, Prénom, Groupe, [Données] \n")

def delete_entry_from_csv(nom, prenom):
    """Supprime une entrée spécifique du fichier CSV en fonction du nom et du prénom."""
    filename = "Bd.csv"
    lines_to_keep = []
    value_to_delete = f"{nom}, {prenom}"
    key = "Nom, Prénom"
    with open(filename, 'r', encoding="utf-8") as file:
        lines = file.readlines()
        headers = lines[0].strip()
        lines_to_keep.append(headers)  # Garder l'en-tête
        for line in lines[1:]:
            if line.strip().startswith(value_to_delete):
                continue  # Ne pas ajouter cette ligne
            lines_to_keep.append(line.strip())
    with open(filename, 'w', encoding="utf-8") as file:
        for line in lines_to_keep:
            file.write(line + "\n") 


    print(f"Ligne(s) où {key} = {value_to_delete} supprimée(s) avec succès.")   
                
def ClearCsv():
    """Efface le contenu du fichier CSV."""
    filename = "Bd.csv"
    with open( filename, 'w', encoding = "utf-8") as file:
        file.write("Nom, Prénom, Groupe, [Données] \n")

def DeleteCsv():
    """Supprime le fichier CSV."""
    filename = "Bd.csv"
    if os.path.isfile(filename):
        os.remove(filename)



        

        