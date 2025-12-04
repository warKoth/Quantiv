"""Class principal des fenêtres d'analyse statistique."""

import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from typing import List

#Classes d'entités analysables
class Entity(ABC):
    """Classe abstraite représentant une entité analysable."""

    def __init__(self, nom: str, ):
        """Initialise l'entité avec un nom.

        Args:
            name (str): Le nom de l'entité.
            
        """
        self.nom = nom

    @abstractmethod
    def get_data(self) -> List[float]:
        """Retourne les données associées à l'entité."""
        pass

# Classe représentant une entrée individuelle
class Individual(Entity):
    """Classe représentant une entrée individuelle."""

    def __init__(self, nom: str, prenom: str, data: List[float]):
        """Initialise l'entrée individuelle avec des données.

        Args:
            nom (str): Le nom de l'entrée.
            prénom (str): Le prénom de l'entrée.
            data (List[float]): Les données associées à l'entrée.
        """
        super().__init__(nom)
        self.data = data
        self.prenom = prenom

    def ajouter_donnée(self, valeur: float):
        """Ajoute une donnée à l'entrée individuelle."""
        self.data.append(valeur)

    def supprimer_donnée(self, valeur: float):
        """Supprime une donnée de l'entrée individuelle."""
        self.data.remove(valeur)

    def get_data(self) -> List[float]:
        """Retourne les données associées à l'entrée individuelle."""
        return self.data
    
    
    
# Classe représentant un groupe d'entrées
class Group(Entity):
    """Classe représentant un groupe d'entrées."""

    def __init__(self, nom: str, members: List[Individual]):
        """Initialise le groupe avec ses membres.

        Args:
            nom (str): Le nom du groupe.
            prénom (str): Le prénom du groupe.
            members (List[Individual]): La liste des membres du groupe.
        """
        super().__init__(nom)
        self.members = members


    def add_member(self, member: Individual):
        """Ajoute un membre au groupe."""
        self.members.append(member)

    def delete_member(self, member: Individual):
        """Supprime un membre du groupe. """
        self.members.remove(member)

    def moyenne(self) -> float:
        """Calcule la moyenne des données agrégées des membres du groupe."""
        all_data = self.get_data()
        if all_data:
            return sum(all_data) / len(all_data)
        return 0.0
    
    def mediane(self) -> float:
        """Calcule la médiane des données agrégées des membres du groupe."""
        all_data = self.get_data()
        if all_data:
            return np.median(all_data)
        return 0.0

    def get_data(self) -> List[float]:
        """Retourne les données agrégées des membres du groupe."""
        all_data = []
        for member in self.members:
            all_data.extend(member.get_data())
        return all_data

class StatistiqueAnalysis:
    """ Classe pour afficher les statistique d'un sujet ou d'un groupe sous forme de graphe araignée. """

    def __init__(self, entity: Entity):
        """ Initialise l'analyse statistique pour une entité donnée.

        Args:
            entity (Entity): L'entité (individu ou groupe) à analyser.
        """
        self.entity = entity

    def plot_radar_chart(self):
        """Permet de tracer un graphique radar des données de l'entité."""
        data = self.entity.get_data()
        if not data:
            print("Aucune donnée disponible pour l'entité.")
            return
        
        num_vars = len(data)
        angles = np.linspace(0, 2 * np.pi , num_vars, endpoint=False).tolist()
        data += data[:1]
        angles += angles[:1]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.fill(angles, data, color='blue', alpha=0.25)
        ax.plot(angles, data, color='blue', linewidth=2)
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([f'Var {i+1}' for i in range(num_vars)])
        plt.title(f'Graphique Radar pour {self.entity.nom}')
        plt.show()

