import os
import csv


def CreateCsv():
    """Crée un fichier CSV vide avec les en-têtes appropriés s'il n'existe pas déjà."""
    filename = "Bd.csv"
    if not os.path.isfile(filename):
        with open(filename, 'w', encoding="utf-8", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Nom", "Prénom", "Groupe", "Données"])


def ReadCsv():
    """Lit le fichier CSV et retourne les données sous forme de liste de dictionnaires."""
    filename = "Bd.csv"
    data = []
    if os.path.isfile(filename):
        with open(filename, 'r', encoding="utf-8", newline='') as file:
            reader = csv.DictReader(file)
            data = list(reader)
    return data


def AddEntry(nom, prenom, groupe, donnees):
    """Ajoute une nouvelle entrée dans le fichier CSV."""
    filename = "Bd.csv"
    # S'assurer que le fichier existe
    if not os.path.isfile(filename):
        CreateCsv()
    
    with open(filename, 'a', encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([nom, prenom, groupe, donnees])
    print(f"Entrée ajoutée : {nom} {prenom}")


def UpdateCsv(data):
    """Remplace complètement le contenu du CSV avec les nouvelles données."""
    filename = "Bd.csv"
    with open(filename, 'w', encoding="utf-8", newline='') as file:
        if data:
            writer = csv.DictWriter(file, fieldnames=["Nom", "Prénom", "Groupe", "Données"])
            writer.writeheader()
            writer.writerows(data)
        else:
            # Si data est vide, on recrée juste les en-têtes
            writer = csv.writer(file)
            writer.writerow(["Nom", "Prénom", "Groupe", "Données"])


def DeleteEntry(nom, prenom):
    """Supprime une entrée spécifique du fichier CSV en fonction du nom et du prénom."""
    filename = "Bd.csv"
    
    if not os.path.isfile(filename):
        print("Le fichier CSV n'existe pas.")
        return
    
    data = ReadCsv()
    initial_count = len(data)
    
    # Filtrer pour garder toutes les entrées SAUF celle à supprimer
    data = [entry for entry in data 
            if not (entry.get("Nom", "").strip() == nom.strip() and 
                   entry.get("Prénom", "").strip() == prenom.strip())]
    
    if len(data) == initial_count:
        print(f"Aucune entrée trouvée pour {nom} {prenom}")
    else:
        UpdateCsv(data)
        print(f"Entrée supprimée : {nom} {prenom}")


def ClearCsv():
    """Efface tout le contenu du fichier CSV (garde seulement les en-têtes)."""
    filename = "Bd.csv"
    with open(filename, 'w', encoding="utf-8", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Nom", "Prénom", "Groupe", "Données"])
    print("CSV effacé.")


def DeleteCsv():
    """Supprime complètement le fichier CSV."""
    filename = "Bd.csv"
    if os.path.isfile(filename):
        os.remove(filename)
        print("Fichier CSV supprimé.")
    else:
        print("Le fichier CSV n'existe pas.")


# Fonctions utilitaires supplémentaires

def SearchByName(nom, prenom):
    """Recherche une personne par nom et prénom."""
    data = ReadCsv()
    results = [entry for entry in data 
               if entry.get("Nom", "").strip().lower() == nom.strip().lower() and
                  entry.get("Prénom", "").strip().lower() == prenom.strip().lower()]
    return results


def SearchByGroupe(groupe):
    """Retourne toutes les personnes d'un groupe donné."""
    data = ReadCsv()
    results = [entry for entry in data 
               if entry.get("Groupe", "").strip().lower() == groupe.strip().lower()]
    return results


def UpdateEntry(nom, prenom, nouveau_groupe=None, nouvelles_donnees=None):
    """Met à jour le groupe et/ou les données d'une personne."""
    data = ReadCsv()
    found = False
    
    for entry in data:
        if (entry.get("Nom", "").strip() == nom.strip() and 
            entry.get("Prénom", "").strip() == prenom.strip()):
            if nouveau_groupe is not None:
                entry["Groupe"] = nouveau_groupe
            if nouvelles_donnees is not None:
                entry["Données"] = nouvelles_donnees
            found = True
            break
    
    if found:
        UpdateCsv(data)
        print(f"Entrée mise à jour : {nom} {prenom}")
    else:
        print(f"Aucune entrée trouvée pour {nom} {prenom}")

"""
# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le CSV
    CreateCsv()
    
    # Ajouter des entrées
    AddEntry("Dupont", "Jean", "A1", "12,15,18")
    AddEntry("Martin", "Sophie", "B2", "14,16,17")
    AddEntry("Durand", "Pierre", "A1", "10,11,13")
    
    # Lire toutes les données
    print("\n--- Toutes les données ---")
    all_data = ReadCsv()
    for entry in all_data:
        print(entry)
    
    # Rechercher par groupe
    print("\n--- Groupe A1 ---")
    groupe_a1 = SearchByGroupe("A1")
    for entry in groupe_a1:
        print(entry)
    
    # Mettre à jour une entrée
    UpdateEntry("Dupont", "Jean", nouvelles_donnees="12,15,18,20")
    
    # Supprimer une entrée
    DeleteEntry("Martin", "Sophie")
    
    print("\n--- Après modifications ---")
    all_data = ReadCsv()
    for entry in all_data:
        print(entry)
"""


        

        