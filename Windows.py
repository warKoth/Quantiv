import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import Main
import Bd

class MainWindow:
    
    def __init__(self, root: tk.Tk, db_manager:):
        """
        Initialise l'application principale
        
        Args:
            root: Fenêtre principale tkinter
            db_manager: Gestionnaire de base de données
        """
        self.root = root
        self.db = db_manager
        
        # Configuration de la fenêtre principale
        self.root.title("Quantiv - Data spider analizer")
        self.root.geometry("1200x700")
        
        # Centrer la fenêtre
        self.root.update_idletasks()
        width = 1200
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.create_menu()
        self.create_widgets()
        self.refresh_all_data()
        
        
        
    def create_menu(self):
        """Crée la barre de menu principale"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Rafraîchir", command=self.refresh_all_data)
        file_menu.add_separator()
        file_menu.add_command(label="Déconnexion", command=self.logout)
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)
        
        
    def create_widgets(self):
        """Crée l'interface principale avec onglets"""
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Onglet éleves
        self.entree_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.entree_frame, text="Entrée")
        self.create_entree_tab()
        
        # Onglet Groupes
        self.groupe_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.groupe_frame, text="Groupes")
        self.create_groupe_tab()
        
        # Barre de statut
        self.status_bar = ttk.Label(self.root, text="Prêt", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        
        
    def create_entree_tab(self):
        """Créer le tableau d'entrée seul"""
        # Frame de recherche et boutons
        search_frame = ttk.Frame(self.entree_frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(search_frame, text="Rechercher:").pack(side='left', padx=5)
        self.entree_search_var = tk.StringVar()
        self.entree_search_var.trace('w', lambda *args: self.search_entree())
        search_entry = ttk.Entry(search_frame, textvariable=self.entree_search_var, width=30)
        search_entry.pack(side='left', padx=5)
        
        #Bouton principal
        ttk.Button(search_frame, text="Nouvelle entrée", command=self.add_entree).pack(side='right', padx=5)
        ttk.Button(search_frame, text="Modifier", command=self.edit_entree).pack(side='right', padx=5)
        ttk.Button(search_frame, text="Supprimer", command=self.delete_entree).pack(side='right', padx=5)
        
        #Treeview
        columns = ('ID', 'nom', 'Prenom', 'Groupe')
        
        tree_frame = ttk.Frame(self.entree_frame)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        #Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.entree_tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                       yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.books_tree.yview)
        hsb.config(command=self.books_tree.xview)
        
        # Configuration des colonnes
        column_widths = {'ID': 40, 'Nom': 60, 'Prenom': 60, 'Groupe': 40}
        
        for col in columns:
            self.entree_tree.heading(col, text=col)
            self.entree_tree.column(col, width=column_widths.get(col, 100)
                                    
        # Placement
        self.entree_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
