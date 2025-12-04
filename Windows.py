import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import Main


class StatisticsWindow:
    """Fenêtre d'analyse statistique pour entrées individuelles et groupes"""
    
    def __init__(self, root: tk.Tk, db_manager: "quantivdata.db"):
        """
        Initialise la fenêtre d'analyse statistique
        
        Args:
            root: Fenêtre principale tkinter
            db_manager: Gestionnaire de base de données
        """
        self.root = root
        self.db = db_manager
        
        
        
        # Configuration de la fenêtre
        self.root.title("Quantiv - Analyse Statistique")
        self.root.geometry("1200x700")

        self.root.update_idletasks()
        width = 1200
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        
        # Variables de données
        self.entrees_data = []
        self.groupes_data = []
        self.filtered_entrees = []
        self.filtered_groupes = []
        
        # Création de l'interface
        self.create_menu()
        self.create_main_interface()
        self.apply_styles()
        self.load_initial_data()
        
    
        
    def create_menu(self):
        """Crée la barre de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Actualiser les données", command=self.refresh_data)
        file_menu.add_command(label="Exporter les statistiques", command=self.export_stats)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Menu Analyse
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analyse", menu=analysis_menu)
        analysis_menu.add_command(label="Statistiques globales", command=self.show_global_stats)
        analysis_menu.add_command(label="Comparaison groupes", command=self.compare_groups)
        analysis_menu.add_command(label="Ajouter des chiffres de reference", command=self.show_trends)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Guide d'utilisation", command=self.show_help)
        help_menu.add_command(label="À propos", command=self.show_about)
        
    def create_main_interface(self):
        """Crée l'interface principale avec onglets"""

        # Frame principal avec padding
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill='both', expand=True)
        
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Onglet Entrées individuelles
        self.create_entrees_tab()
        
        # Onglet Groupes
        self.create_groupes_tab()
        
        # Onglet Comparaisons
        self.create_comparison_tab()
        
        # Barre de statut
        self.create_status_bar()
        
    def create_entrees_tab(self):
        """Crée l'onglet d'analyse des entrées individuelles"""
        entree_frame = ttk.Frame(self.notebook)
        self.notebook.add(entree_frame, text=" Entrées Individuelles")
        
        # Frame supérieur - Recherche et filtres
        top_frame = ttk.LabelFrame(entree_frame, text="Recherche et Filtres", padding="10")
        top_frame.pack(fill='x', padx=5, pady=5)
        
        # Barre de recherche
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text=" Rechercher:").pack(side='left', padx=5)
        self.entree_search_var = tk.StringVar()
        self.entree_search_var.trace('w', lambda *args: self.search_entrees())
        ttk.Entry(search_frame, textvariable=self.entree_search_var, width=40).pack(side='left', padx=5)
        
        # Filtres
        filter_frame = ttk.Frame(top_frame)
        filter_frame.pack(fill='x', pady=5)
        
        ttk.Label(filter_frame, text="Groupe:").pack(side='left', padx=5)
        self.entree_groupe_filter = ttk.Combobox(filter_frame, width=20, state='readonly')
        self.entree_groupe_filter.pack(side='left', padx=5)
        self.entree_groupe_filter.bind('<<ComboboxSelected>>', lambda e: self.apply_entree_filters())
        
        ttk.Label(filter_frame, text="Période:").pack(side='left', padx=5)
        self.entree_periode_filter = ttk.Combobox(filter_frame, width=15, state='readonly',
                                                   values=["Aujourd'hui", "7 derniers jours", "30 derniers jours", "Tout"])
        self.entree_periode_filter.current(3)
        self.entree_periode_filter.pack(side='left', padx=5)
        self.entree_periode_filter.bind('<<ComboboxSelected>>', lambda e: self.apply_entree_filters())
        
        ttk.Button(filter_frame, text="Réinitialiser", command=self.reset_entree_filters).pack(side='left', padx=5)
        
        # Frame central - Tableau et statistiques
        content_frame = ttk.Frame(entree_frame)
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Frame gauche - Tableau
        left_frame = ttk.LabelFrame(content_frame, text="Liste des Entrées", padding="5")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Treeview avec scrollbars
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill='both', expand=True)
        
        columns = ('ID', 'Nom', 'Prénom', 'Groupe', 'Score', 'Date', 'Statut')
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.entree_tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.entree_tree.yview)
        hsb.config(command=self.entree_tree.xview)
        
        # Configuration des colonnes
        column_config = {
            'ID': 50,
            'Nom': 120,
            'Prénom': 120,
            'Groupe': 100,
            'Score': 80,
            'Date': 100,
            'Statut': 100
        }
        
        for col in columns:
            self.entree_tree.heading(col, text=col, command=lambda c=col: self.sort_entrees(c))
            self.entree_tree.column(col, width=column_config.get(col, 100), anchor='center')
        
        self.entree_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Binding pour sélection
        self.entree_tree.bind('<<TreeviewSelect>>', self.on_entree_select)
        
        # Frame droit - Statistiques individuelles
        right_frame = ttk.LabelFrame(content_frame, text="Statistiques Détaillées", padding="10")
        right_frame.pack(side='right', fill='both', padx=(5, 0))
        right_frame.config(width=300)
        
        # Info entrée sélectionnée
        self.entree_info_frame = ttk.Frame(right_frame)
        self.entree_info_frame.pack(fill='both', expand=True)
        
        ttk.Label(self.entree_info_frame, text="Sélectionnez une entrée", 
                 font=('Arial', 10, 'italic')).pack(pady=20)
        
        # Frame inférieur - Actions
        action_frame = ttk.Frame(entree_frame)
        action_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(action_frame, text=" Nouvelle Entrée", 
                  command=self.add_entree).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" Modifier", 
                  command=self.edit_entree).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" Supprimer", 
                  command=self.delete_entree).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" Voir Graphiques", 
                  command=self.show_entree_charts).pack(side='left', padx=5)
        ttk.Button(action_frame, text="📄 Générer Rapport", 
                  command=self.generate_entree_report).pack(side='right', padx=5)
        
    def create_groupes_tab(self):
        """Crée l'onglet d'analyse des groupes"""
        groupe_frame = ttk.Frame(self.notebook)
        self.notebook.add(groupe_frame, text=" Groupes")
        
        # Frame supérieur - Recherche
        top_frame = ttk.LabelFrame(groupe_frame, text="Recherche", padding="10")
        top_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(top_frame, text=" Rechercher:").pack(side='left', padx=5)
        self.groupe_search_var = tk.StringVar()
        self.groupe_search_var.trace('w', lambda *args: self.search_groupes())
        ttk.Entry(top_frame, textvariable=self.groupe_search_var, width=40).pack(side='left', padx=5)
        
        # Frame central - Tableau et statistiques
        content_frame = ttk.Frame(groupe_frame)
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Frame gauche - Tableau
        left_frame = ttk.LabelFrame(content_frame, text="Liste des Groupes", padding="5")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill='both', expand=True)
        
        columns = ('ID', 'Nom Groupe', 'Nb Entrées', 'Moyenne', 'Min', 'Max', 'Écart-type')
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.groupe_tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.groupe_tree.yview)
        hsb.config(command=self.groupe_tree.xview)
        
        column_config = {
            'ID': 50,
            'Nom Groupe': 150,
            'Nb Entrées': 100,
            'Moyenne': 100,
            'Min': 80,
            'Max': 80,
            'Écart-type': 100
        }
        
        for col in columns:
            self.groupe_tree.heading(col, text=col, command=lambda c=col: self.sort_groupes(c))
            self.groupe_tree.column(col, width=column_config.get(col, 100), anchor='center')
        
        self.groupe_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.groupe_tree.bind('<<TreeviewSelect>>', self.on_groupe_select)
        
        # Frame droit - Statistiques groupe
        right_frame = ttk.LabelFrame(content_frame, text="Statistiques du Groupe", padding="10")
        right_frame.pack(side='right', fill='both', padx=(5, 0))
        right_frame.config(width=300)
        
        self.groupe_info_frame = ttk.Frame(right_frame)
        self.groupe_info_frame.pack(fill='both', expand=True)
        
        ttk.Label(self.groupe_info_frame, text="Sélectionnez un groupe", 
                 font=('Arial', 10, 'italic')).pack(pady=20)
        
        # Frame inférieur - Actions
        action_frame = ttk.Frame(groupe_frame)
        action_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(action_frame, text=" Nouveau Groupe", 
                  command=self.add_groupe).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" Modifier", 
                  command=self.edit_groupe).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" Supprimer", 
                  command=self.delete_groupe).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" Voir Graphique", 
                  command=self.show_groupe_distribution).pack(side='left', padx=5)
        ttk.Button(action_frame, text="📄 Générer Rapport", 
                  command=self.generate_groupe_report).pack(side='right', padx=5)
        
    def create_comparison_tab(self):
        """Crée l'onglet de comparaison"""
        comp_frame = ttk.Frame(self.notebook)
        self.notebook.add(comp_frame, text=" Comparaisons")
        
        # Contenu à implémenter
        ttk.Label(comp_frame, text="Outil de comparaison entre entrées et groupes", 
                 font=('Arial', 12)).pack(pady=20)
        
    def create_status_bar(self):
        """Crée la barre de statut"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side='bottom', fill='x')
        
        self.status_label = ttk.Label(status_frame, text="Prêt", relief=tk.SUNKEN)
        self.status_label.pack(side='left', fill='x', expand=True)
        
        self.count_label = ttk.Label(status_frame, text="Entrées: 0 | Groupes: 0", relief=tk.SUNKEN)
        self.count_label.pack(side='right')
        
    def apply_styles(self):
        """Applique les styles personnalisés"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Style pour le notebook
        # Réduire le padding et la police pour raccourcir visuellement les onglets
        style.configure('TNotebook.Tab', padding=[6, 2], font=('Helvetica', 9))
        
    # Méthodes de gestion des données
    def load_initial_data(self):
        """Charge les données initiales"""
        self.refresh_data()
        
    def refresh_data(self):
        """Actualise toutes les données"""
        self.update_status("Actualisation des données...")
        # Implémenter le chargement depuis la base de données
        self.load_entrees()
        self.load_groupes()
        self.update_counts()
        self.update_status("Données actualisées")
        
    def load_entrees(self):
        """Charge les entrées depuis la base de données"""
        # À implémenter avec self.db
        pass
        
    def load_groupes(self):
        """Charge les groupes depuis la base de données"""
        # À implémenter avec self.db
        pass
        
    def search_entrees(self):
        """Recherche dans les entrées"""
        search_term = self.entree_search_var.get().lower()
        # Implémenter la logique de recherche
        
    def search_groupes(self):
        """Recherche dans les groupes"""
        search_term = self.groupe_search_var.get().lower()
        # Implémenter la logique de recherche
        
    def apply_entree_filters(self):
        """Applique les filtres sur les entrées"""
        pass
        
    def reset_entree_filters(self):
        """Réinitialise les filtres"""
        self.entree_search_var.set("")
        self.entree_groupe_filter.set("")
        self.entree_periode_filter.current(3)
        
    def sort_entrees(self, column):
        """Trie les entrées par colonne"""
        pass
        
    def sort_groupes(self, column):
        """Trie les groupes par colonne"""
        pass
        
    def on_entree_select(self, event):
        """Gère la sélection d'une entrée"""
        selection = self.entree_tree.selection()
        if selection:
            # Afficher les statistiques détaillées
            pass
            
    def on_groupe_select(self, event):
        """Gère la sélection d'un groupe"""
        selection = self.groupe_tree.selection()
        if selection:
            # Afficher les statistiques du groupe
            pass
            
    # Méthodes d'actions
    def add_entree(self):
        """Ajoute une nouvelle entrée"""
        messagebox.showinfo("Info", "Fonction d'ajout d'entrée")
        
    def edit_entree(self):
        """Modifie une entrée"""
        messagebox.showinfo("Info", "Fonction de modification d'entrée")
        
    def delete_entree(self):
        """Supprime une entrée"""
        if messagebox.askyesno("Confirmation", "Supprimer cette entrée ?"):
            pass
            
    def add_groupe(self):
        """Ajoute un nouveau groupe"""
        messagebox.showinfo("Info", "Fonction d'ajout de groupe")
        
    def edit_groupe(self):
        """Modifie un groupe"""
        messagebox.showinfo("Info", "Fonction de modification de groupe")
        
    def delete_groupe(self):
        """Supprime un groupe"""
        if messagebox.askyesno("Confirmation", "Supprimer ce groupe ?"):
            pass
            
    # Méthodes d'analyse
    def show_entree_charts(self):
        """Affiche les graphiques pour une entrée"""
        messagebox.showinfo("Info", "Affichage des graphiques")
        
    def show_groupe_distribution(self):
        """Affiche la distribution d'un groupe"""
        messagebox.showinfo("Info", "Affichage de la distribution")
        
    def generate_entree_report(self):
        """Génère un rapport pour les entrées"""
        messagebox.showinfo("Info", "Génération du rapport")
        
    def generate_groupe_report(self):
        """Génère un rapport pour les groupes"""
        messagebox.showinfo("Info", "Génération du rapport")
        
    def show_global_stats(self):
        """Affiche les statistiques globales"""
        messagebox.showinfo("Info", "Statistiques globales")
        
    def compare_groups(self):
        """Compare les groupes"""
        messagebox.showinfo("Info", "Comparaison des groupes")
        
    def show_trends(self):
        """Affiche les tendances temporelles"""
        messagebox.showinfo("Info", "Tendances temporelles")
        
    def export_stats(self):
        """Exporte les statistiques"""
        messagebox.showinfo("Info", "Export des statistiques")
        
    def show_help(self):
        """Affiche l'aide"""
        messagebox.showinfo("Aide", "Guide d'utilisation de l'application")
        
    def show_about(self):
        """Affiche les informations À propos"""
        messagebox.showinfo("À propos", 
                           "Quantiv - Analyse Statistique\nVersion 1.0\n\nAnalyse de données pour entrées et groupes")
        
    def update_status(self, message):
        """Met à jour la barre de statut"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def update_counts(self):
        """Met à jour les compteurs"""
        nb_entrees = len(self.entrees_data)
        nb_groupes = len(self.groupes_data)
        self.count_label.config(text=f"Entrées: {nb_entrees} | Groupes: {nb_groupes}")


def main():
    """Fonction principale pour lancer l'application"""
    root = tk.Tk()
    
    # Initialiser le gestionnaire de base de données (à remplacer par votre classe)
    # db_manager = YourDatabaseManager()
    db_manager = None  # Placeholder
    
    app = StatisticsWindow(root, db_manager)
    root.mainloop()


if __name__ == "__main__":
    main()
