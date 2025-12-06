import Stockcsv
from Main import Individual, Group
from typing import List
import json
import os

NOTES_FILE = 'notes.json'
STUDENTS_FILE = 'students.json'

class DataManager:
    """Classe de pont entre les entités et le gestionnaire de CSV."""

    @staticmethod
    def parse_data_string(data_string: str) -> List[float]:
        """Convertit une chaîne de données en une liste de flottants."""
        try:
            return [float(x.strip()) for x in data_string.split(',')]
        except:
            return []
        
    @staticmethod
    def load_all_individuals() -> List[Individual]:
        """Charge toutes les entrées individuelles.

        Priorité aux étudiants définis dans `students.json` (format JSON).
        Si absent ou vide, on retombe sur le CSV `Bd.csv`.
        """
        individuals = []

        # si students.json existe, l'utiliser
        if os.path.isfile(STUDENTS_FILE):
            try:
                with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                    students = json.load(f)
                # charger l'ordre des notes si présent
                notes = []
                if os.path.isfile(NOTES_FILE):
                    try:
                        with open(NOTES_FILE, 'r', encoding='utf-8') as nf:
                            notes = json.load(nf)
                    except Exception:
                        notes = []

                for s in students:
                    nom = s.get('nom','').strip()
                    prenom = s.get('prenom','').strip()
                    groupe = s.get('groupe','').strip()
                    scores = s.get('scores', {})
                    # build data list following notes order, fallback to values if missing
                    if notes:
                        data = [float(scores.get(n.get('name'), 0)) for n in notes]
                    else:
                        # if no notes defined, flatten numeric values
                        data = [float(v) for v in scores.values()] if isinstance(scores, dict) else []
                    ind = Individual(nom, prenom, groupe, data, scores=scores)
                    individuals.append(ind)
                return individuals
            except Exception:
                # fallback to CSV on failure
                pass

        # fallback: read CSV
        csv_data = Stockcsv.ReadCsv()
        for entry in csv_data:
            nom = entry.get("Nom", "").strip()
            prenom = entry.get("Prénom", "").strip()
            groupe = entry.get("Groupe", "").strip()
            data_str = entry.get("Données", "").strip()

            data = DataManager.parse_data_string(data_str)

            if nom and prenom:
                ind = Individual(nom, prenom, groupe, data)
                individuals.append(ind)
        
        return individuals

    @staticmethod
    def load_notes():
        """Charge la liste des notes (assessments) depuis `notes.json`."""
        if not os.path.isfile(NOTES_FILE):
            return []
        try:
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def save_notes(notes_list):
        try:
            with open(NOTES_FILE, 'w', encoding='utf-8') as f:
                json.dump(notes_list, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @staticmethod
    def load_students():
        """Charge les étudiants depuis `students.json` (raw dicts)."""
        if not os.path.isfile(STUDENTS_FILE):
            return []
        try:
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def save_student(student_dict):
        """Ajoute ou met à jour un étudiant dans `students.json`."""
        students = []
        if os.path.isfile(STUDENTS_FILE):
            try:
                with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                    students = json.load(f)
            except Exception:
                students = []

        # find existing by nom+prenom
        updated = False
        for s in students:
            if s.get('nom') == student_dict.get('nom') and s.get('prenom') == student_dict.get('prenom'):
                s.update(student_dict)
                updated = True
                break
        if not updated:
            students.append(student_dict)

        try:
            with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(students, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @staticmethod
    def delete_student(nom: str, prenom: str):
        students = DataManager.load_students()
        new = [s for s in students if not (s.get('nom')==nom and s.get('prenom')==prenom)]
        try:
            with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(new, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    @staticmethod
    def save_individual(individual: Individual):
        """Sauvegarde ou met à jour une entrée individuelle dans le CSV."""
        data_str = ','.join([str(x) for x in individual.data])
        Stockcsv.AddEntry(individual.nom, individual.prenom, individual.groupe, data_str)

    @staticmethod
    def load_groups() -> List[Group]:
        """Charge les groupes d'entrées depuis le CSV."""
        individuals  = DataManager.load_all_individuals()
        groups_dict = {}
        for ind in individuals:
            if ind.groupe:
                if ind.groupe not in groups_dict:
                    groups_dict[ind.groupe] = []
                groups_dict[ind.groupe].append(ind)

        groups = []
        for groupe_nom, members in groups_dict.items():
            if groupe_nom: # Eviter les groupes vides
                group = Group(groupe_nom, members)
                groups.append(group)

        return groups
    
    @staticmethod
    def delete_individual(nom: str, prenom: str):
        """Supprime une entrée individuelle du CSV."""
        Stockcsv.DeleteEntry(nom, prenom)
