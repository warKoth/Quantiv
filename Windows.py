import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime
import numpy as np
import Main
from DataManager import DataManager

# Les imports vers d'autres modules de l'application sont faits localement
# pour éviter les erreurs si le module n'est pas disponible lors d'une importation partielle.


class StatisticsWindow:
    """Fenêtre d'analyse statistique pour entrées individuelles et groupes"""

    def __init__(self, root: tk.Tk):
        """Initialise la fenêtre et les composants de base."""
        self.root = root
        # Style global : police par défaut plus lisible sous Windows
        try:
            # Mettre à jour les polices Tk par défaut de manière sûre
            default_font = tkfont.nametofont("TkDefaultFont")
            default_font.configure(family="Segoe UI", size=10)
            text_font = tkfont.nametofont("TkTextFont")
            text_font.configure(family="Segoe UI", size=10)
        except Exception:
            pass

        # Données
        self.individuals = []
        self.groups = []
        self.filtered_individuals = []
        self.filtered_groups = []

        # Interface
        self.root.title("Quantiv - Analyse Statistique")
        self.root.geometry("1200x700")

        self.create_menu()
        self.create_main_interface()
        self.apply_styles()
        self.load_initial_data()

    def apply_styles(self):
        """Applique un style compact pour les onglets et le thème."""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # Raccourcir visuellement les onglets
        style.configure('TNotebook.Tab', padding=[6, 2], font=('Helvetica', 9))
        style.configure('TNotebook', tabmargins=[2, 2, 0, 0])
        # Boutons et labels légèrement espacés pour meilleure lisibilité
        try:
            style.configure('TButton', padding=6)
            style.configure('TLabel', font=('Segoe UI', 10))
        except Exception:
            pass

    def create_menu(self):
        """Crée la barre de menu principale."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Actualiser les données", command=self.refresh_data)
        file_menu.add_command(label="Exporter les statistiques", command=self.export_stats)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)

        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analyse", menu=analysis_menu)
        analysis_menu.add_command(label="Statistiques globales", command=self.show_global_stats)
        analysis_menu.add_command(label="Comparaison groupes", command=self.compare_groups)
        analysis_menu.add_command(label="Gérer les notes", command=self.manage_notes)
        analysis_menu.add_command(label="Tendances", command=self.show_trends)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Guide d'utilisation", command=self.show_help)
        help_menu.add_command(label="À propos", command=self.show_about)

    def create_main_interface(self):
        """Construit le notebook et les onglets principaux."""
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill='both', expand=True)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        self.create_entrees_tab()
        self.create_groupes_tab()
        self.create_comparison_tab()

        self.create_status_bar()

    def create_entrees_tab(self):
        entree_frame = ttk.Frame(self.notebook)
        self.notebook.add(entree_frame, text="Entrées Individuelles")

        top_frame = ttk.LabelFrame(entree_frame, text="Recherche et Filtres", padding="10")
        top_frame.pack(fill='x', padx=5, pady=5)

        search_frame = ttk.Frame(top_frame)
        search_frame.pack(fill='x', pady=5)

        ttk.Label(search_frame, text="Rechercher:").pack(side='left', padx=5)
        self.entree_search_var = tk.StringVar()
        self.entree_search_var.trace('w', lambda *a: self.search_entrees())
        ttk.Entry(search_frame, textvariable=self.entree_search_var, width=40).pack(side='left', padx=5)

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

        # Contenu principal - tableaux
        content_frame = ttk.Frame(entree_frame)
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)

        left_frame = ttk.LabelFrame(content_frame, text="Liste des Entrées", padding="5")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill='both', expand=True)

        columns = ('ID', 'Nom', 'Prénom', 'Groupe', 'Score', 'Date', 'Statut')
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        self.entree_tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.entree_tree.yview)
        hsb.config(command=self.entree_tree.xview)

        column_config = {'ID': 50, 'Nom': 120, 'Prénom': 120, 'Groupe': 100, 'Score': 80, 'Date': 100, 'Statut': 100}
        for col in columns:
            self.entree_tree.heading(col, text=col)
            self.entree_tree.column(col, width=column_config.get(col, 100), anchor='center')
        # placer le treeview et ses scrollbars
        self.entree_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        self.entree_tree.bind('<<TreeviewSelect>>', self.on_entree_select)

        # Panel droit pour détails individuels
        right_frame = ttk.LabelFrame(content_frame, text="Statistiques Détaillées", padding="10")
        right_frame.pack(side='right', fill='both', padx=(5, 0))
        right_frame.config(width=300)
        self.entree_info_frame = ttk.Frame(right_frame)
        self.entree_info_frame.pack(fill='both', expand=True)
        ttk.Label(self.entree_info_frame, text="Sélectionnez une entrée", font=('Arial', 10, 'italic')).pack(pady=20)

        # Frame inférieur - Actions
        action_frame = ttk.Frame(entree_frame)
        action_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(action_frame, text=" Nouvelle Entrée", command=self.add_entree).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" Modifier", command=self.edit_entree).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" Supprimer", command=self.delete_entree).pack(side='left', padx=5)
        ttk.Button(action_frame, text=" Voir Graphiques", command=self.show_entree_charts).pack(side='left', padx=5)
        ttk.Button(action_frame, text="📄 Générer Rapport", command=self.generate_entree_report).pack(side='right', padx=5)
        

    def create_status_bar(self):
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side='bottom', fill='x')

        self.status_label = ttk.Label(status_frame, text="Prêt", relief=tk.SUNKEN)
        self.status_label.pack(side='left', fill='x', expand=True)

        self.count_label = ttk.Label(status_frame, text="Entrées: 0 | Groupes: 0", relief=tk.SUNKEN)
        self.count_label.pack(side='right')

    def load_initial_data(self):
        """Charge les données initiales depuis DataManager si disponible."""
        try:
            # Utiliser la classe DataManager importée en haut du fichier
            self.individuals = DataManager.load_all_individuals()
            self.filtered_individuals = self.individuals.copy()
            self.groups = DataManager.load_groups()
            self.filtered_groups = self.groups.copy()
        except Exception:
            # Pas de DataManager disponible ou échec: on garde les listes vides
            self.individuals = []
            self.filtered_individuals = []
            self.groups = []
            self.filtered_groups = []

        self.refresh_data()

    def refresh_data(self):
        self.update_status("Actualisation des données...")
        # Re-remplir les tableaux
        # Mettre à jour d'abord la table des groupes puis le filtre de groupe
        self.populate_groupe_table()
        self.update_entree_group_filter()
        self.populate_entree_table()
        self.update_counts()
        self.update_status("Données actualisées")

    def update_entree_group_filter(self):
        """Remplit la Combobox de filtre de groupe dans l'onglet Entrées."""
        try:
            # Construire la liste des noms de groupes
            names = [g.nom for g in self.groups if getattr(g, 'nom', None)]
            values = ['Tous'] + sorted(list(dict.fromkeys(names))) if names else ['Tous']
            self.entree_groupe_filter['values'] = values
            # Si la valeur actuelle n'est pas dans la liste, définir 'Tous'
            cur = self.entree_groupe_filter.get()
            if cur not in values:
                self.entree_groupe_filter.set('Tous')
        except Exception:
            pass

    def center_window(self, win: tk.Toplevel, width: int = None, height: int = None):
        """Centre une fenêtre `Toplevel` par rapport à la fenêtre principale.

        Si `width` et `height` sont fournis, les utilise ; sinon prend la taille demandée.
        """
        try:
            win.update_idletasks()
            # essayer de centrer par rapport à la fenêtre racine si possible
            rx = self.root.winfo_rootx()
            ry = self.root.winfo_rooty()
            rwidth = self.root.winfo_width()
            rheight = self.root.winfo_height()
            if width is None or height is None:
                w = win.winfo_reqwidth()
                h = win.winfo_reqheight()
            else:
                w = int(width)
                h = int(height)

            if rwidth > 1 and rheight > 1:
                x = max(0, rx + (rwidth - w) // 2)
                y = max(0, ry + (rheight - h) // 2)
            else:
                sw = win.winfo_screenwidth()
                sh = win.winfo_screenheight()
                x = max(0, (sw - w) // 2)
                y = max(0, (sh - h) // 2)

            win.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            try:
                # fallback minimal
                win.geometry(f"+{50}+{50}")
            except Exception:
                pass

    def update_counts(self):
        """Met à jour les compteurs dans la barre de statut"""
        try:
            nb_entrees = len(self.individuals)
            nb_groupes = len(self.groups)
            self.count_label.config(text=f"Entrées: {nb_entrees} | Groupes: {nb_groupes}")
        except Exception:
            pass

    def populate_entree_table(self):
        """Remplit le tableau des entrées avec self.filtered_individuals"""
        for i in self.entree_tree.get_children():
            self.entree_tree.delete(i)

        for i, ind in enumerate(self.filtered_individuals, start=1):
            data = ind.get_data() if hasattr(ind, 'get_data') else []
            score = f"{(sum(data)/len(data)):.2f}" if data else "-"
            date = getattr(ind, 'date', '')
            statut = getattr(ind, 'status', '')
            self.entree_tree.insert('', 'end', values=(i, ind.nom, ind.prenom, ind.groupe, score, date, statut))

    def populate_groupe_table(self):
        """Remplit le tableau des groupes avec self.filtered_groups"""
        for i in self.groupe_tree.get_children():
            self.groupe_tree.delete(i)

        for i, group in enumerate(self.filtered_groups, start=1):
            data = group.get_data() if hasattr(group, 'get_data') else []
            moyenne = f"{np.mean(data):.2f}" if data else "-"
            nb = len(data)
            mini = f"{min(data):.2f}" if data else "-"
            maxi = f"{max(data):.2f}" if data else "-"
            ecart = f"{np.std(data):.2f}" if data else "-"
            self.groupe_tree.insert('', 'end', values=(i, group.nom, nb, moyenne, mini, maxi, ecart))

    def search_entrees(self):
        term = self.entree_search_var.get().lower()
        if not term:
            self.filtered_individuals = self.individuals.copy()
        else:
            self.filtered_individuals = [ind for ind in self.individuals if term in (ind.nom + ' ' + ind.prenom).lower()]
        self.populate_entree_table()

    def search_groupes(self):
        term = self.groupe_search_var.get().lower()
        if not term:
            self.filtered_groups = self.groups.copy()
        else:
            self.filtered_groups = [g for g in self.groups if term in g.nom.lower()]
        self.populate_groupe_table()

    def apply_entree_filters(self):
        # Exemple simple: filtrer par combobox de groupe
        grp = self.entree_groupe_filter.get()
        if not grp:
            self.filtered_individuals = self.individuals.copy()
        else:
            self.filtered_individuals = [ind for ind in self.individuals if getattr(ind, 'groupe', '') == grp]
        self.populate_entree_table()

    def reset_entree_filters(self):
        self.entree_search_var.set("")
        try:
            self.entree_groupe_filter.set("")
        except Exception:
            pass
        self.entree_periode_filter.current(3)
        self.filtered_individuals = self.individuals.copy()
        self.populate_entree_table()

    def on_entree_select(self, event):
        # Affiche des détails simples dans le panneau droit
        sel = self.entree_tree.selection()
        if not sel:
            return
        item = self.entree_tree.item(sel[0])
        vals = item.get('values', [])
        # Nettoyer et afficher
        for w in self.entree_info_frame.winfo_children():
            w.destroy()
        ttk.Label(self.entree_info_frame, text=f"{vals}").pack(pady=10)

    def on_groupe_select(self, event):
        sel = self.groupe_tree.selection()
        if not sel:
            return
        item = self.groupe_tree.item(sel[0])
        vals = item.get('values', [])
        for w in self.groupe_info_frame.winfo_children():
            w.destroy()
        ttk.Label(self.groupe_info_frame, text=f"{vals}").pack(pady=10)


    def generate_entree_report(self):
        messagebox.showinfo("Info", "Générer rapport entrées - à implémenter")

    def generate_groupe_report(self):
        messagebox.showinfo("Info", "Générer rapport groupes - à implémenter")

    def show_global_stats(self):
        if not self.individuals:
            messagebox.showinfo("Info", "Aucune donnée disponible")
            return
        all_data = []
        for ind in self.individuals:
            all_data.extend(ind.get_data() if hasattr(ind, 'get_data') else [])
        if not all_data:
            messagebox.showinfo("Info", "Aucune note enregistrée")
            return
        stats = f"Moyenne: {np.mean(all_data):.2f} | Médiane: {np.median(all_data):.2f} | Écart-type: {np.std(all_data):.2f}"
        messagebox.showinfo("Statistiques globales", stats)

    def compare_groups(self):
        messagebox.showinfo("Info", "Comparer groupes - à implémenter")

    def show_trends(self):
        messagebox.showinfo("Info", "Tendances - à implémenter")

    def get_national_average(self):
        """Calcule la moyenne de toutes les notes du système"""
        all_data = []
        for ind in self.individuals:
            data = ind.get_data() if hasattr(ind, 'get_data') else []
            all_data.extend(data)
        return np.mean(all_data) if all_data else 0

    def get_national_stats(self):
        """Retourne les statistiques nationales complètes"""
        all_data = []
        for ind in self.individuals:
            data = ind.get_data() if hasattr(ind, 'get_data') else []
            all_data.extend(data)
        
        if not all_data:
            return None
        
        stats = {
            'mean': np.mean(all_data),
            'median': np.median(all_data),
            'std': np.std(all_data),
            'min': min(all_data),
            'max': max(all_data),
            'q1': np.percentile(all_data, 25),
            'q3': np.percentile(all_data, 75),
            'count': len(all_data)
        }

        # Si une moyenne nationale forcée est définie (override), l'utiliser
        if hasattr(self, 'national_override') and self.national_override is not None:
            try:
                stats['mean'] = float(self.national_override)
            except Exception:
                pass

        return stats

    def update_comparison_entities(self, *args):
        """Met à jour la liste des entités à comparer selon le type choisi"""
        entity_type = self.comp_type_var.get()
        self.comp_entity_combo['values'] = []
        
        if entity_type == "Individu":
            names = [f"{ind.prenom} {ind.nom}" for ind in self.individuals]
            self.comp_entity_combo['values'] = names
        else:
            names = [g.nom for g in self.groups]
            self.comp_entity_combo['values'] = names
        
        if names:
            self.comp_entity_combo.current(0)

    # ---- Moyenne nationale (override + stockage) ----
    def load_national_override(self):
        """Charge la moyenne nationale forcée depuis un fichier local si présent."""
        try:
            import json, os
            cfg = 'national.json'
            if os.path.isfile(cfg):
                with open(cfg, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.national_override = data.get('mean', None)
            else:
                self.national_override = None
        except Exception:
            self.national_override = None

    def save_national_override(self):
        """Enregistre la moyenne nationale forcée dans un fichier local."""
        try:
            import json
            cfg = 'national.json'
            with open(cfg, 'w', encoding='utf-8') as f:
                json.dump({'mean': self.national_override}, f)
        except Exception as e:
            messagebox.showerror('Erreur', f"Impossible d'enregistrer la moyenne nationale:\n{e}")

    def set_national_override_dialog(self):
        """Ouvre une boîte de dialogue pour définir/effacer la moyenne nationale."""
        try:
            current = getattr(self, 'national_override', None)
            prompt = f"Valeur actuelle: {current}\nEntrez une nouvelle moyenne nationale (laisser vide pour réinitialiser):"
            val = simpledialog.askstring('Moyenne Nationale', prompt, parent=self.root)
            if val is None:
                return
            val = val.strip()
            if val == '':
                self.national_override = None
            else:
                try:
                    self.national_override = float(val)
                except ValueError:
                    messagebox.showerror('Erreur', 'Valeur invalide, entrez un nombre.')
                    return
            self.save_national_override()
            messagebox.showinfo('Succès', 'Moyenne nationale mise à jour.')
            # mettre à jour l'affichage si présent
            try:
                self.nat_mean_label.config(text=f"Moyenne nationale (override): {self.national_override}")
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror('Erreur', str(e))

    def perform_comparison(self):
        """Effectue la comparaison entre l'entité sélectionnée et la moyenne nationale"""
        entity_type = self.comp_type_var.get()
        entity_name = self.comp_entity_combo.get()
        
        if not entity_name:
            messagebox.showwarning("Attention", "Veuillez sélectionner une entité")
            return
        
        national_stats = self.get_national_stats()
        if not national_stats:
            messagebox.showinfo("Info", "Aucune donnée nationale disponible")
            return
        
        # Récupérer l'entité
        entity = None
        if entity_type == "Individu":
            for ind in self.individuals:
                if f"{ind.prenom} {ind.nom}" == entity_name:
                    entity = ind
                    break
        else:
            for grp in self.groups:
                if grp.nom == entity_name:
                    entity = grp
                    break
        
        if not entity:
            messagebox.showerror("Erreur", "Entité non trouvée")
            return
        
        # Calculer les stats de l'entité
        entity_data = entity.get_data() if hasattr(entity, 'get_data') else []
        if not entity_data:
            messagebox.showinfo("Info", "L'entité sélectionnée n'a pas de données")
            return
        
        entity_stats = {
            'mean': np.mean(entity_data),
            'median': np.median(entity_data),
            'std': np.std(entity_data),
            'min': min(entity_data),
            'max': max(entity_data),
            'q1': np.percentile(entity_data, 25),
            'q3': np.percentile(entity_data, 75),
            'count': len(entity_data)
        }
        # Préparer comparaison avec le groupe si l'entité est un individu
        group_stats = None
        grp_name = None
        if entity_type == "Individu":
            grp_name = getattr(entity, 'groupe', None)
            if grp_name:
                group_obj = None
                for g in self.groups:
                    if getattr(g, 'nom', None) == grp_name:
                        group_obj = g
                        break
                if group_obj:
                    g_data = group_obj.get_data() if hasattr(group_obj, 'get_data') else []
                    if g_data:
                        group_stats = {
                            'mean': np.mean(g_data),
                            'median': np.median(g_data),
                            'std': np.std(g_data),
                            'min': min(g_data),
                            'max': max(g_data),
                            'q1': np.percentile(g_data, 25),
                            'q3': np.percentile(g_data, 75),
                            'count': len(g_data)
                        }
        
        # Afficher les résultats
        self.comp_result_text.config(state='normal')
        self.comp_result_text.delete('1.0', tk.END)

        # Build header with national and optional group comparisons
        header_lines = []
        header_lines.append(f"ENTITÉ COMPARÉE: {entity_name} ({entity_type})")
        header_lines.append('')
        if group_stats is not None:
            header_lines.append(f"{'':<27}{entity_name:<25} │ Groupe ({grp_name}):       │ Moyenne Nationale")
            header_lines.append('-' * 80)
            rows = [
                ('Moyenne', entity_stats['mean'], group_stats['mean'], national_stats['mean']),
                ('Médiane', entity_stats['median'], group_stats['median'], national_stats['median']),
                ('Écart-type', entity_stats['std'], group_stats['std'], national_stats['std']),
                ('Min', entity_stats['min'], group_stats['min'], national_stats['min']),
                ('Max', entity_stats['max'], group_stats['max'], national_stats['max']),
                ('Q1 (25%)', entity_stats['q1'], group_stats['q1'], national_stats['q1']),
                ('Q3 (75%)', entity_stats['q3'], group_stats['q3'], national_stats['q3']),
                ('Nombre de notes', entity_stats['count'], group_stats['count'], national_stats['count'])
            ]
            for label, e, g, n in rows:
                header_lines.append(f"{label:<25} {e:>10.2f}    │ {g:>10.2f}    │ {n:>10.2f}")
        else:
            header_lines.append(f"{'':<27}{entity_name:<30} │ Moyenne Nationale")
            header_lines.append('-' * 80)
            rows = [
                ('Moyenne', entity_stats['mean'], national_stats['mean']),
                ('Médiane', entity_stats['median'], national_stats['median']),
                ('Écart-type', entity_stats['std'], national_stats['std']),
                ('Min', entity_stats['min'], national_stats['min']),
                ('Max', entity_stats['max'], national_stats['max']),
                ('Q1 (25%)', entity_stats['q1'], national_stats['q1']),
                ('Q3 (75%)', entity_stats['q3'], national_stats['q3']),
                ('Nombre de notes', entity_stats['count'], national_stats['count'])
            ]
            for label, e, n in rows:
                header_lines.append(f"{label:<25} {e:>10.2f}    │ {n:>10.2f}")

        result = '\n'.join(header_lines) + '\n\nANALYSE COMPARATIVE:\n' + '\n'

        # Comparaison de la moyenne (avec national)
        diff = entity_stats['mean'] - national_stats['mean']
        pct = (diff / national_stats['mean'] * 100) if national_stats['mean'] != 0 else 0
        symbol = "↑" if diff > 0 else "↓" if diff < 0 else "="
        result += f"\nMoyenne: {entity_name} est {symbol} de {abs(diff):.2f} points ({pct:+.1f}%) par rapport à la moyenne nationale.\n"
        if entity_stats['mean'] > national_stats['mean']:
            result += f"✓ {entity_name} performe MIEUX que la moyenne nationale\n"
        elif entity_stats['mean'] < national_stats['mean']:
            result += f"✗ {entity_name} performe MOINS BIEN que la moyenne nationale\n"
        else:
            result += f"• {entity_name} performe EXACTEMENT COMME la moyenne nationale\n"

        # Comparaison avec le groupe si disponible
        if group_stats is not None:
            diffg = entity_stats['mean'] - group_stats['mean']
            pctg = (diffg / group_stats['mean'] * 100) if group_stats['mean'] != 0 else 0
            symg = "↑" if diffg > 0 else "↓" if diffg < 0 else "="
            result += f"\nComparaison au groupe {grp_name}: {entity_name} est {symg} de {abs(diffg):.2f} points ({pctg:+.1f}%).\n"
            if entity_stats['mean'] > group_stats['mean']:
                result += f"✓ {entity_name} performe MIEUX que son groupe\n"
            elif entity_stats['mean'] < group_stats['mean']:
                result += f"✗ {entity_name} performe MOINS BIEN que son groupe\n"
            else:
                result += f"• {entity_name} performe COMME son groupe\n"

        self.comp_result_text.insert('1.0', result)
        self.comp_result_text.config(state='disabled')

        # Stocker pour le graphique
        self.last_comparison = {
            'entity_name': entity_name,
            'entity_stats': entity_stats,
            'national_stats': national_stats,
            'group_stats': group_stats,
            'entity_type': entity_type
        }

    def show_comparison_chart(self):
        """Affiche un graphique comparatif"""
        if not hasattr(self, 'last_comparison'):
            messagebox.showinfo("Info", "Veuillez d'abord effectuer une comparaison")
            return
        
        try:
            import matplotlib.pyplot as plt
            
            comp = self.last_comparison
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            
            # Graphique 1 : Moyennes et quartiles
            categories = ['Min', 'Q1', 'Médiane', 'Moyenne', 'Q3', 'Max']
            entity_vals = [
                comp['entity_stats']['min'],
                comp['entity_stats']['q1'],
                comp['entity_stats']['median'],
                comp['entity_stats']['mean'],
                comp['entity_stats']['q3'],
                comp['entity_stats']['max']
            ]
            national_vals = [
                comp['national_stats']['min'],
                comp['national_stats']['q1'],
                comp['national_stats']['median'],
                comp['national_stats']['mean'],
                comp['national_stats']['q3'],
                comp['national_stats']['max']
            ]
            
            x = np.arange(len(categories))
            width = 0.35
            
            ax1.bar(x - width/2, entity_vals, width, label=comp['entity_name'], color='skyblue')
            ax1.bar(x + width/2, national_vals, width, label='Moyenne Nationale', color='coral')
            
            ax1.set_xlabel('Statistiques')
            ax1.set_ylabel('Valeur')
            ax1.set_title(f'Comparaison: {comp["entity_name"]} vs Moyenne Nationale')
            ax1.set_xticks(x)
            ax1.set_xticklabels(categories, rotation=45, ha='right')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Graphique 2 : Distribution box plot
            all_data = []
            for ind in self.individuals:
                all_data.extend(ind.get_data() if hasattr(ind, 'get_data') else [])
            
            entity_obj = None
            if comp['entity_type'] == "Individu":
                for ind in self.individuals:
                    if f"{ind.prenom} {ind.nom}" == comp['entity_name']:
                        entity_obj = ind
                        break
            else:
                for grp in self.groups:
                    if grp.nom == comp['entity_name']:
                        entity_obj = grp
                        break
            
            if entity_obj:
                entity_data = entity_obj.get_data() if hasattr(entity_obj, 'get_data') else []
                bp = ax2.boxplot([all_data, entity_data], labels=['Nationale', comp['entity_name']], patch_artist=True)
                
                colors = ['coral', 'skyblue']
                for patch, color in zip(bp['boxes'], colors):
                    patch.set_facecolor(color)
                
                ax2.set_ylabel('Notes')
                ax2.set_title('Distribution des notes')
                ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'afficher le graphique:\n{str(e)}")

    def export_stats(self):
        # Export minimal: CSV des individus si possible
        filename = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
        if not filename:
            return
        try:
            import csv
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                w = csv.writer(f)
                w.writerow(['Nom','Prénom','Groupe','NbNotes','Moyenne'])
                for ind in self.individuals:
                    data = ind.get_data() if hasattr(ind, 'get_data') else []
                    avg = f"{(sum(data)/len(data)):.2f}" if data else ''
                    w.writerow([ind.nom, ind.prenom, getattr(ind,'groupe',''), len(data), avg])
            messagebox.showinfo('Succès', f'Statistiques exportées dans:\n{filename}')
        except Exception as e:
            messagebox.showerror('Erreur', str(e))

    def show_help(self):
        help_text = (
            "Guide d'utilisation:\n\n" 
            "- Onglet Entrées: gestion des entrées\n"
            "- Onglet Groupes: gestion des groupes\n"
            "- Comparaisons: comparer performances\n"
        )
        messagebox.showinfo('Aide', help_text)

    def show_about(self):
        about_text = 'Quantiv - Application d\'analyse - Version 2.0'
        messagebox.showinfo('À propos', about_text)

    def manage_notes(self):
        """Ouvre un dialogue pour gérer la liste des notes (assessments) et leurs valeurs nationales."""
        try:
            notes = DataManager.load_notes() or []
        except Exception:
            notes = []

        # Normalize notes to list of dicts {name, national}
        norm = []
        for n in notes:
            if isinstance(n, dict):
                norm.append({'name': n.get('name', ''), 'national': n.get('national', None)})
            else:
                norm.append({'name': str(n), 'national': None})

        dialog = tk.Toplevel(self.root)
        dialog.resizable(False, False)
        dialog.title('Gérer les notes')
        dialog.geometry('600x360')
        dialog.transient(self.root)
        dialog.grab_set()
        try:
            self.center_window(dialog, 600, 360)
        except Exception:
            pass

        # Left: list of notes
        left = ttk.Frame(dialog, padding=8)
        left.pack(side='left', fill='both', expand=True)

        lb = tk.Listbox(left, height=18)
        lb.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(left, orient='vertical', command=lb.yview)
        scrollbar.pack(side='right', fill='y')
        lb.config(yscrollcommand=scrollbar.set)

        def refresh_listbox():
            lb.delete(0, tk.END)
            for it in norm:
                nm = it.get('name','')
                nat = it.get('national')
                s = f"{nm}"
                if nat is not None:
                    s += f"  (national: {nat})"
                lb.insert(tk.END, s)

        # Right: editor
        right = ttk.Frame(dialog, padding=8)
        right.pack(side='right', fill='y')

        ttk.Label(right, text='Nom de la note:').pack(anchor='w', pady=(4,0))
        name_var = tk.StringVar()
        name_entry = ttk.Entry(right, textvariable=name_var, width=30)
        name_entry.pack(anchor='w', pady=4)

        ttk.Label(right, text='Valeur nationale (optionnelle):').pack(anchor='w', pady=(8,0))
        national_var = tk.StringVar()
        national_entry = ttk.Entry(right, textvariable=national_var, width=20)
        national_entry.pack(anchor='w', pady=4)

        status_lbl = ttk.Label(right, text='')
        status_lbl.pack(anchor='w', pady=(8,0))

        def on_select(evt=None):
            sel = lb.curselection()
            if not sel:
                name_var.set('')
                national_var.set('')
                return
            i = sel[0]
            item = norm[i]
            name_var.set(item.get('name',''))
            nat = item.get('national')
            national_var.set('' if nat is None else str(nat))

        lb.bind('<<ListboxSelect>>', on_select)

        def add_new():
            name_var.set('')
            national_var.set('')
            lb.selection_clear(0, tk.END)
            name_entry.focus()

        def save_note():
            name = name_var.get().strip()
            nat = national_var.get().strip()
            if not name:
                status_lbl.config(text='Le nom est requis', foreground='red')
                return
            nval = None
            if nat != '':
                try:
                    nval = float(nat)
                except ValueError:
                    status_lbl.config(text='Valeur nationale invalide', foreground='red')
                    return

            sel = lb.curselection()
            if sel:
                idx = sel[0]
                norm[idx]['name'] = name
                norm[idx]['national'] = nval
            else:
                norm.append({'name': name, 'national': nval})

            ok = DataManager.save_notes(norm)
            if ok:
                status_lbl.config(text='Enregistré', foreground='green')
                try:
                    # confirmation visuelle et rafraîchissement
                    messagebox.showinfo('Succès', 'Notes enregistrées')
                    self.load_initial_data()
                    self.update_comparison_entities()
                except Exception:
                    pass
            else:
                status_lbl.config(text='Erreur enregistrement', foreground='red')
            refresh_listbox()

        def delete_note():
            sel = lb.curselection()
            if not sel:
                return
            idx = sel[0]
            item = norm[idx]
            if not messagebox.askyesno('Confirmer', f"Supprimer la note '{item.get('name')}' ?"):
                return
            norm.pop(idx)
            ok = DataManager.save_notes(norm)
            if ok:
                status_lbl.config(text='Supprimé', foreground='green')
                try:
                    messagebox.showinfo('Succès', 'Note supprimée')
                    self.load_initial_data()
                    self.update_comparison_entities()
                except Exception:
                    pass
            else:
                status_lbl.config(text='Erreur suppression', foreground='red')
            refresh_listbox()

        btn_frame = ttk.Frame(right)
        btn_frame.pack(anchor='w', pady=12)
        ttk.Button(btn_frame, text='Nouveau', command=add_new).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Enregistrer', command=save_note).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Supprimer', command=delete_note).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Fermer', command=dialog.destroy).pack(side='left', padx=8)

        refresh_listbox()
        name_entry.focus()

    def update_status(self, message):
        try:
            self.status_label.config(text=message)
        except Exception:
            pass
        # update_status is intentionally lightweight; UI layout handled in create_* methods
        return

    def show_snackbar(self, message: str, duration: int = 3000):
        # snackbar feature removed
        raise NotImplementedError('Snackbar feature has been removed')
    def create_groupes_tab(self):
        """Crée l'onglet d'analyse des groupes"""
        groupe_frame = ttk.Frame(self.notebook)
        self.notebook.add(groupe_frame, text="👥 Groupes")
        
        # Frame supérieur - Recherche
        top_frame = ttk.LabelFrame(groupe_frame, text="Recherche", padding="10")
        top_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(top_frame, text="🔍 Rechercher:").pack(side='left', padx=5)
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
        
        columns = ('ID', 'Nom Groupe', 'Nb Membres', 'Total Notes', 'Moyenne', 'Médiane', 'Min', 'Max', 'Écart-type')
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.groupe_tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.config(command=self.groupe_tree.yview)
        hsb.config(command=self.groupe_tree.xview)
        
        column_config = {
            'ID': 50,
            'Nom Groupe': 120,
            'Nb Membres': 90,
            'Total Notes': 90,
            'Moyenne': 80,
            'Médiane': 80,
            'Min': 60,
            'Max': 60,
            'Écart-type': 90
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
        self.groupe_tree.bind('<Double-1>', lambda e: self.show_groupe_details())
        
        # Frame droit - Statistiques groupe
        right_frame = ttk.LabelFrame(content_frame, text="Statistiques du Groupe", padding="10")
        right_frame.pack(side='right', fill='both', padx=(5, 0))
        right_frame.config(width=300)
        
        self.groupe_info_frame = ttk.Frame(right_frame)
        self.groupe_info_frame.pack(fill='both', expand=True)
        
        self.groupe_info_label = ttk.Label(self.groupe_info_frame, 
                                          text="Sélectionnez un groupe", 
                                          font=('Arial', 10, 'italic'))
        self.groupe_info_label.pack(pady=20)
        
        # Frame inférieur - Actions
        action_frame = ttk.Frame(groupe_frame)
        action_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(action_frame, text="📊 Voir Distribution", 
                  command=self.show_groupe_distribution).pack(side='left', padx=5)
        ttk.Button(action_frame, text="👥 Détails Membres", 
                  command=self.show_groupe_details).pack(side='left', padx=5)
        ttk.Button(action_frame, text="📈 Graphique Radar", 
                  command=self.show_groupe_radar).pack(side='left', padx=5)
        ttk.Button(action_frame, text="📄 Générer Rapport", 
                  command=self.generate_groupe_report).pack(side='right', padx=5)
        
    def create_comparison_tab(self):
        comp_frame = ttk.Frame(self.notebook)
        self.notebook.add(comp_frame, text="Comparaisons")

        # Frame supérieur - Sélection
        select_frame = ttk.LabelFrame(comp_frame, text="Sélectionner une entité à comparer", padding="10")
        select_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(select_frame, text="Type:").pack(side='left', padx=5)
        self.comp_type_var = tk.StringVar(value="Individu")
        ttk.Combobox(select_frame, textvariable=self.comp_type_var, values=["Individu", "Groupe"], 
                     state='readonly', width=15).pack(side='left', padx=5)

        ttk.Label(select_frame, text="Entité:").pack(side='left', padx=5)
        self.comp_entity_combo = ttk.Combobox(select_frame, width=30, state='readonly')
        self.comp_entity_combo.pack(side='left', padx=5)
        self.comp_type_var.trace('w', self.update_comparison_entities)

        ttk.Button(select_frame, text="Comparer", command=self.perform_comparison).pack(side='left', padx=5)
        
        # Affichage / modification de la moyenne nationale (override)
        self.load_national_override()
        self.nat_mean_label = ttk.Label(select_frame, text=f"Moyenne nationale (override): {getattr(self, 'national_override', None)}")
        self.nat_mean_label.pack(side='left', padx=10)
        ttk.Button(select_frame, text="Modifier moyenne nationale", command=self.set_national_override_dialog).pack(side='left', padx=5)

        # Frame central - Résultats
        result_frame = ttk.LabelFrame(comp_frame, text="Résultats de la comparaison", padding="10")
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.comp_result_text = tk.Text(result_frame, height=20, width=80, font=('Courier', 10))
        self.comp_result_text.pack(fill='both', expand=True)
        self.comp_result_text.config(state='disabled')

        # Frame inférieur - Bouton graphique
        button_frame = ttk.Frame(comp_frame)
        button_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(button_frame, text="Afficher Graphique", command=self.show_comparison_chart).pack(side='left', padx=5)
    
    # ============================================================================
    # MÉTHODES DE RECHERCHE ET FILTRAGE
    # ============================================================================
    
    def search_entrees(self):
        """Recherche dans les entrées individuelles"""
        search_term = self.entree_search_var.get().lower()
        
        if not search_term:
            self.filtered_individuals = self.individuals.copy()
        else:
            self.filtered_individuals = [
                ind for ind in self.individuals
                if search_term in ind.nom.lower() 
                or search_term in ind.prenom.lower()
                or search_term in ind.groupe.lower()
            ]
        
        self.apply_entree_filters()
        
    def search_groupes(self):
        """Recherche dans les groupes"""
        search_term = self.groupe_search_var.get().lower()
        
        if not search_term:
            self.filtered_groups = self.groups.copy()
        else:
            self.filtered_groups = [
                group for group in self.groups
                if search_term in group.nom.lower()
            ]
        
        self.populate_groupe_table()
        
    def apply_entree_filters(self):
        """Applique les filtres sur les entrées"""
        # Commencer avec les résultats de recherche
        filtered = self.filtered_individuals.copy()
        
        # Appliquer le filtre de groupe
        groupe_filter = self.entree_groupe_filter.get()
        if groupe_filter and groupe_filter != 'Tous':
            filtered = [ind for ind in filtered if ind.groupe == groupe_filter]
        
        self.filtered_individuals = filtered
        self.populate_entree_table()
        
    def reset_entree_filters(self):
        """Réinitialise tous les filtres"""
        self.entree_search_var.set("")
        self.entree_groupe_filter.set('Tous')
        self.filtered_individuals = self.individuals.copy()
        self.populate_entree_table()
        
    def sort_entrees(self, column):
        """Trie les entrées par colonne (à implémenter si nécessaire)"""
        # Implémentation optionnelle du tri
        pass
        
    def sort_groupes(self, column):
        """Trie les groupes par colonne (à implémenter si nécessaire)"""
        pass
    
    # ============================================================================
    # ÉVÉNEMENTS DE SÉLECTION
    # ============================================================================
    
    def on_entree_select(self, event):
        """Gère la sélection d'une entrée dans le tableau"""
        selection = self.entree_tree.selection()
        if not selection:
            return
        
        # Récupérer l'index de la ligne sélectionnée
        item = self.entree_tree.item(selection[0])
        index = int(item['values'][0]) - 1  # ID commence à 1
        
        if 0 <= index < len(self.filtered_individuals):
            individual = self.filtered_individuals[index]
            self.display_entree_info(individual)
    
    def display_entree_info(self, individual):
        """Affiche les informations détaillées d'une entrée"""
        # Effacer l'ancien contenu
        for widget in self.entree_info_frame.winfo_children():
            widget.destroy()
        
        # Frame pour les infos
        info_frame = ttk.Frame(self.entree_info_frame)
        info_frame.pack(fill='both', expand=True)
        
        # Titre
        title = ttk.Label(info_frame, 
                         text=f"{individual.prenom} {individual.nom}",
                         font=('Arial', 12, 'bold'))
        title.pack(pady=5)
        
        # Informations
        ttk.Label(info_frame, text=f"Groupe: {individual.groupe}").pack(anchor='w', padx=10)
        
        data = individual.get_data()
        if data:
            ttk.Separator(info_frame, orient='horizontal').pack(fill='x', pady=10)
            
            ttk.Label(info_frame, text="Statistiques:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10)
            ttk.Label(info_frame, text=f"Nombre de notes: {len(data)}").pack(anchor='w', padx=10)
            ttk.Label(info_frame, text=f"Moyenne: {sum(data)/len(data):.2f}").pack(anchor='w', padx=10)
            ttk.Label(info_frame, text=f"Minimum: {min(data):.2f}").pack(anchor='w', padx=10)
            ttk.Label(info_frame, text=f"Maximum: {max(data):.2f}").pack(anchor='w', padx=10)
            ttk.Label(info_frame, text=f"Écart-type: {np.std(data):.2f}").pack(anchor='w', padx=10)
            
            ttk.Separator(info_frame, orient='horizontal').pack(fill='x', pady=10)
            
            ttk.Label(info_frame, text="Notes:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10)
            notes_text = ", ".join([f"{note:.1f}" for note in data])
            notes_label = ttk.Label(info_frame, text=notes_text, wraplength=250)
            notes_label.pack(anchor='w', padx=10, pady=5)
        else:
            ttk.Label(info_frame, text="Aucune note enregistrée").pack(anchor='w', padx=10, pady=10)
    
    def on_groupe_select(self, event):
        """Gère la sélection d'un groupe dans le tableau"""
        selection = self.groupe_tree.selection()
        if not selection:
            return
        
        item = self.groupe_tree.item(selection[0])
        index = int(item['values'][0]) - 1
        
        if 0 <= index < len(self.filtered_groups):
            group = self.filtered_groups[index]
            self.display_groupe_info(group)
    
    def display_groupe_info(self, group):
        """Affiche les informations détaillées d'un groupe"""
        for widget in self.groupe_info_frame.winfo_children():
            widget.destroy()
        
        info_frame = ttk.Frame(self.groupe_info_frame)
        info_frame.pack(fill='both', expand=True)
        
        # Titre
        title = ttk.Label(info_frame, 
                         text=f"Groupe {group.nom}",
                         font=('Arial', 12, 'bold'))
        title.pack(pady=5)
        
        # Nombre de membres
        ttk.Label(info_frame, text=f"Nombre de membres: {len(group.members)}").pack(anchor='w', padx=10)
        
        # Liste des membres
        ttk.Separator(info_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(info_frame, text="Membres:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10)
        
        members_frame = ttk.Frame(info_frame)
        members_frame.pack(fill='both', expand=True, padx=10)
        
        for member in group.members[:10]:  # Limiter à 10 pour l'affichage
            ttk.Label(members_frame, text=f"• {member.prenom} {member.nom}").pack(anchor='w')
        
        if len(group.members) > 10:
            ttk.Label(members_frame, text=f"... et {len(group.members) - 10} autre(s)").pack(anchor='w')
        
        # Statistiques globales
        data = group.get_data()
        if data:
            ttk.Separator(info_frame, orient='horizontal').pack(fill='x', pady=10)
            ttk.Label(info_frame, text="Statistiques:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10)
            ttk.Label(info_frame, text=f"Total de notes: {len(data)}").pack(anchor='w', padx=10)
            ttk.Label(info_frame, text=f"Moyenne: {group.moyenne():.2f}").pack(anchor='w', padx=10)
            ttk.Label(info_frame, text=f"Médiane: {group.mediane():.2f}").pack(anchor='w', padx=10)
    
    # ============================================================================
    # ACTIONS - CRUD ENTRÉES
    # ============================================================================
    
    def add_entree(self):
        """Ouvre un dialogue pour ajouter une nouvelle entrée en utilisant uniquement
        les notes pré-définies (via `notes.json`)."""
        notes = DataManager.load_notes() or []
        if not notes:
            messagebox.showinfo("Info", "Aucune note définie. Utilisez Analyse → Gérer les notes pour en créer.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.resizable(False, False)
        dialog.title("Nouvelle Entrée")
        dialog.geometry("600x420")
        dialog.transient(self.root)
        dialog.grab_set()
        try:
            self.center_window(dialog, 300, 210)
        except Exception:
            pass

        main_frame = ttk.Frame(dialog, padding=12)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Nom:").grid(row=0, column=0, sticky='e')
        nom_entry = ttk.Entry(main_frame, width=30)
        nom_entry.grid(row=0, column=1, pady=2)

        ttk.Label(main_frame, text="Prénom:").grid(row=1, column=0, sticky='e')
        prenom_entry = ttk.Entry(main_frame, width=30)
        prenom_entry.grid(row=1, column=1, pady=2)

        ttk.Label(main_frame, text="Groupe:").grid(row=2, column=0, sticky='e')
        groupe_entry = ttk.Entry(main_frame, width=30)
        groupe_entry.grid(row=2, column=1, pady=2)

        ttk.Label(main_frame, text="Notes:").grid(row=3, column=0, sticky='ne')
        notes_frame = ttk.Frame(main_frame)
        notes_frame.grid(row=3, column=1, sticky='w')

        score_vars = {}
        for i, n in enumerate(notes):
            name = n.get('name') if isinstance(n, dict) else str(n)
            ttk.Label(notes_frame, text=name).grid(row=i, column=0, sticky='e', padx=(0,8), pady=2)
            ent = ttk.Entry(notes_frame, width=14)
            ent.grid(row=i, column=1, pady=2, padx=(0,6))
            score_vars[name] = ent

        status_lbl = ttk.Label(main_frame, text='', foreground='red')
        status_lbl.grid(row=4, column=0, columnspan=2, pady=8)

        def save_student_dialog():
            nom = nom_entry.get().strip()
            prenom = prenom_entry.get().strip()
            groupe = groupe_entry.get().strip()
            if not nom or not prenom:
                status_lbl.config(text='Nom et prénom requis')
                return

            scores = {}
            for k, e in score_vars.items():
                v = e.get().strip()
                if v != '':
                    try:
                        scores[k] = float(v)
                    except ValueError:
                        status_lbl.config(text=f'Valeur invalide pour {k}')
                        return

            student = {'nom': nom, 'prenom': prenom, 'groupe': groupe, 'scores': scores}
            ok = DataManager.save_student(student)
            if ok:
                messagebox.showinfo('Succès', 'Étudiant enregistré')
                dialog.destroy()
                self.load_initial_data()
            else:
                status_lbl.config(text='Erreur lors de l\'enregistrement')

        btns = ttk.Frame(main_frame)
        btns.grid(row=999, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text='Enregistrer', command=save_student_dialog).pack(side='left', padx=6)
        ttk.Button(btns, text='Annuler', command=dialog.destroy).pack(side='left', padx=6)
        nom_entry.focus()
        
    def edit_entree(self):
        """Modifie une entrée sélectionnée en affichant uniquement les champs de
        notes pré-définies."""
        selection = self.entree_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une entrée à modifier")
            return

        item = self.entree_tree.item(selection[0])
        index = int(item['values'][0]) - 1
        if index < 0 or index >= len(self.filtered_individuals):
            messagebox.showerror("Erreur", "Entrée invalide")
            return

        individual = self.filtered_individuals[index]
        notes = DataManager.load_notes() or []
        if not notes:
            messagebox.showinfo("Info", "Aucune note définie. Utilisez Analyse → Gérer les notes pour en créer.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.resizable(False, False)
        dialog.title("Modifier l'Entrée")
        dialog.transient(self.root)
        dialog.grab_set()
        try:
            self.center_window(dialog)
        except Exception:
            pass

        main_frame = ttk.Frame(dialog, padding=12)
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Nom:").grid(row=0, column=0, sticky='e')
        nom_entry = ttk.Entry(main_frame, width=30)
        nom_entry.insert(0, individual.nom)
        nom_entry.grid(row=0, column=1, pady=2)

        ttk.Label(main_frame, text="Prénom:").grid(row=1, column=0, sticky='e')
        prenom_entry = ttk.Entry(main_frame, width=30)
        prenom_entry.insert(0, individual.prenom)
        prenom_entry.grid(row=1, column=1, pady=2)

        ttk.Label(main_frame, text="Groupe:").grid(row=2, column=0, sticky='e')
        groupe_entry = ttk.Entry(main_frame, width=30)
        groupe_entry.insert(0, getattr(individual, 'groupe', ''))
        groupe_entry.grid(row=2, column=1, pady=2)

        ttk.Label(main_frame, text="Notes:").grid(row=3, column=0, sticky='ne')
        notes_frame = ttk.Frame(main_frame)
        notes_frame.grid(row=3, column=1, sticky='w')

        score_vars = {}
        # Prefill using individual.scores if available, else map data by position
        scores_src = getattr(individual, 'scores', {}) or {}
        data_list = getattr(individual, 'data', []) or []

        for i, n in enumerate(notes):
            name = n.get('name') if isinstance(n, dict) else str(n)
            ttk.Label(notes_frame, text=name).grid(row=i, column=0, sticky='e', padx=(0,8), pady=2)
            ent = ttk.Entry(notes_frame, width=14)
            ent.grid(row=i, column=1, pady=2, padx=(0,6))
            # Prefill
            if name in scores_src:
                ent.insert(0, str(scores_src.get(name)))
            elif i < len(data_list):
                ent.insert(0, str(data_list[i]))
            score_vars[name] = ent

        status_lbl = ttk.Label(main_frame, text='', foreground='red')
        status_lbl.grid(row=4, column=0, columnspan=2, pady=8)

        def save_changes():
            new_nom = nom_entry.get().strip()
            new_prenom = prenom_entry.get().strip()
            new_groupe = groupe_entry.get().strip()
            if not new_nom or not new_prenom:
                status_lbl.config(text='Nom et prénom requis')
                return

            new_scores = {}
            for k, e in score_vars.items():
                v = e.get().strip()
                if v != '':
                    try:
                        new_scores[k] = float(v)
                    except ValueError:
                        status_lbl.config(text=f'Valeur invalide pour {k}')
                        return

            try:
                # Supprimer l'ancienne entrée dans students.json si présente
                try:
                    DataManager.delete_student(individual.nom, individual.prenom)
                except Exception:
                    pass

                student = {'nom': new_nom, 'prenom': new_prenom, 'groupe': new_groupe, 'scores': new_scores}
                ok = DataManager.save_student(student)
                if not ok:
                    status_lbl.config(text='Erreur lors de l\'enregistrement')
                    return

                self.load_initial_data()
                dialog.destroy()
                messagebox.showinfo('Succès', 'Entrée modifiée avec succès!')

            except Exception as e:
                status_lbl.config(text=f'Erreur: {str(e)}')

        btns = ttk.Frame(main_frame)
        btns.grid(row=999, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text='Enregistrer', command=save_changes).pack(side='left', padx=6)
        ttk.Button(btns, text='Annuler', command=dialog.destroy).pack(side='left', padx=6)
        
    def delete_entree(self):
        """Supprime une entrée sélectionnée"""
        selection = self.entree_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une entrée à supprimer")
            return
        
        item = self.entree_tree.item(selection[0])
        index = int(item['values'][0]) - 1
        
        if index < 0 or index >= len(self.filtered_individuals):
            return
        
        individual = self.filtered_individuals[index]
        
        # Confirmation
        response = messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer l'entrée de {individual.prenom} {individual.nom} ?"
        )
        
        if response:
            try:
                # Essayer de supprimer depuis students.json, puis fallback CSV
                try:
                    DataManager.delete_student(individual.nom, individual.prenom)
                except Exception:
                    try:
                        DataManager.delete_individual(individual.nom, individual.prenom)
                    except Exception:
                        pass

                self.refresh_data()
                self.update_status(f"Entrée supprimée: {individual.prenom} {individual.nom}")
                messagebox.showinfo("Succès", "Entrée supprimée avec succès!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de supprimer l'entrée:\n{str(e)}")
    
    # ============================================================================
    # ACTIONS - VISUALISATIONS
    # ============================================================================
    
    def show_entree_charts(self):
        """Affiche le graphique radar pour une entrée sélectionnée"""
        selection = self.entree_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une entrée")
            return
        
        item = self.entree_tree.item(selection[0])
        index = int(item['values'][0]) - 1
        
        if index < 0 or index >= len(self.filtered_individuals):
            return
        
        individual = self.filtered_individuals[index]
        
        if not individual.data:
            messagebox.showinfo("Info", "Aucune donnée à afficher pour cette entrée")
            return
        
        try:
            analysis = Main.StatistiqueAnalysis(individual)
            analysis.plot_radar_chart()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'afficher le graphique:\n{str(e)}")
    
    def show_groupe_distribution(self):
        """Affiche la distribution des notes d'un groupe"""
        selection = self.groupe_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un groupe")
            return
        
        item = self.groupe_tree.item(selection[0])
        index = int(item['values'][0]) - 1
        
        if index < 0 or index >= len(self.filtered_groups):
            return
        
        group = self.filtered_groups[index]
        data = group.get_data()
        
        if not data:
            messagebox.showinfo("Info", "Aucune donnée pour ce groupe")
            return
        
        try:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Histogramme
            ax1.hist(data, bins=20, color='skyblue', edgecolor='black')
            ax1.set_title(f'Distribution des notes - Groupe {group.nom}')
            ax1.set_xlabel('Notes')
            ax1.set_ylabel('Fréquence')
            ax1.grid(True, alpha=0.3)
            
            # Boîte à moustaches
            ax2.boxplot(data, vert=True)
            ax2.set_title(f'Boîte à moustaches - Groupe {group.nom}')
            ax2.set_ylabel('Notes')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'afficher la distribution:\n{str(e)}")
    
    def show_groupe_radar(self):
        """Affiche le graphique radar pour un groupe"""
        selection = self.groupe_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un groupe")
            return
        
        item = self.groupe_tree.item(selection[0])
        index = int(item['values'][0]) - 1
        
        if index < 0 or index >= len(self.filtered_groups):
            return
        
        group = self.filtered_groups[index]
        
        if not group.get_data():
            messagebox.showinfo("Info", "Aucune donnée pour ce groupe")
            return
        
        try:
            analysis = Main.StatistiqueAnalysis(group)
            analysis.plot_radar_chart()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'afficher le graphique:\n{str(e)}")
    
    def show_groupe_details(self):
        """Affiche les détails complets d'un groupe dans une nouvelle fenêtre"""
        selection = self.groupe_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un groupe")
            return
        
        item = self.groupe_tree.item(selection[0])
        index = int(item['values'][0]) - 1
        
        if index < 0 or index >= len(self.filtered_groups):
            return
        
        group = self.filtered_groups[index]
        
        # Créer une fenêtre de détails
        detail_window = tk.Toplevel(self.root)
        detail_window.resizable(False, False)
        detail_window.title(f"Détails du Groupe {group.nom}")
        detail_window.geometry("600x400")
        try:
            self.center_window(detail_window, 600, 400)
        except Exception:
            pass
        
        main_frame = ttk.Frame(detail_window, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Titre
        title = ttk.Label(main_frame, text=f"Groupe {group.nom}", font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Tableau des membres
        columns = ('Nom', 'Prénom', 'Nb Notes', 'Moyenne')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=140, anchor='center')
        
        for member in group.members:
            data = member.get_data()
            nb_notes = len(data)
            moyenne = sum(data) / nb_notes if nb_notes > 0 else 0
            
            tree.insert('', 'end', values=(
                member.nom,
                member.prenom,
                nb_notes,
                f"{moyenne:.2f}"
            ))
        
        tree.pack(fill='both', expand=True, pady=10)
        
        # Statistiques du groupe
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill='x', pady=10)
        
        data = group.get_data()
        if data:
            stats_text = f"Statistiques globales: Moyenne={group.moyenne():.2f} | Médiane={group.mediane():.2f} | Écart-type={np.std(data):.2f}"
        else:
            stats_text = "Aucune donnée disponible"
        
        ttk.Label(stats_frame, text=stats_text, font=('Arial', 10)).pack()
        
        ttk.Button(main_frame, text="Fermer", command=detail_window.destroy).pack(pady=10)
    
    # ============================================================================
    # ACTIONS - RAPPORTS ET ANALYSES
    # ============================================================================
    
    def generate_entree_report(self):
        """Génère un rapport pour les entrées"""
        if not self.individuals:
            messagebox.showinfo("Info", "Aucune donnée à exporter")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
            title="Enregistrer le rapport"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("RAPPORT DES ENTRÉES INDIVIDUELLES - QUANTIV\n")
                f.write(f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Nombre total d'entrées: {len(self.individuals)}\n\n")
                
                for ind in self.individuals:
                    f.write(f"\n{'-' * 60}\n")
                    f.write(f"NOM: {ind.nom} {ind.prenom}\n")
                    f.write(f"GROUPE: {ind.groupe}\n")
                    
                    data = ind.get_data()
                    if data:
                        f.write(f"Nombre de notes: {len(data)}\n")
                        f.write(f"Moyenne: {sum(data)/len(data):.2f}\n")
                        f.write(f"Min: {min(data):.2f} | Max: {max(data):.2f}\n")
                        f.write(f"Notes: {', '.join([str(n) for n in data])}\n")
                    else:
                        f.write("Aucune note enregistrée\n")
            
            messagebox.showinfo("Succès", f"Rapport enregistré dans:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de générer le rapport:\n{str(e)}")
    
    def generate_groupe_report(self):
        """Génère un rapport pour les groupes"""
        if not self.groups:
            messagebox.showinfo("Info", "Aucun groupe à exporter")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
            title="Enregistrer le rapport"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("RAPPORT DES GROUPES - QUANTIV\n")
                f.write(f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Nombre total de groupes: {len(self.groups)}\n\n")
                
                for group in self.groups:
                    f.write(f"\n{'-' * 60}\n")
                    f.write(f"GROUPE: {group.nom}\n")
                    f.write(f"Nombre de membres: {len(group.members)}\n")
                    
                    data = group.get_data()
                    if data:
                        f.write(f"Total de notes: {len(data)}\n")
                        f.write(f"Moyenne: {group.moyenne():.2f}\n")
                        f.write(f"Médiane: {group.mediane():.2f}\n")
                        f.write(f"Min: {min(data):.2f} | Max: {max(data):.2f}\n")
                        f.write(f"Écart-type: {np.std(data):.2f}\n")
                    
                    f.write("\nMembres:\n")
                    for member in group.members:
                        f.write(f"  - {member.prenom} {member.nom}\n")
            
            messagebox.showinfo("Succès", f"Rapport enregistré dans:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de générer le rapport:\n{str(e)}")
    
    def show_global_stats(self):
        """Affiche les statistiques globales de toutes les données"""
        if not self.individuals:
            messagebox.showinfo("Info", "Aucune donnée disponible")
            return
        
        # Collecter toutes les données
        all_data = []
        for ind in self.individuals:
            all_data.extend(ind.get_data())
        
        if not all_data:
            messagebox.showinfo("Info", "Aucune note enregistrée")
            return
        
        # Créer une fenêtre de statistiques
        stats_window = tk.Toplevel(self.root)
        stats_window.resizable(False, False)
        stats_window.title("Statistiques Globales")
        stats_window.geometry("500x400")
        try:
            self.center_window(stats_window, 500, 400)
        except Exception:
            pass
        
        main_frame = ttk.Frame(stats_window, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Statistiques Globales", font=('Arial', 14, 'bold')).pack(pady=10)
        
        stats_text = f"""
Nombre total d'entrées: {len(self.individuals)}
Nombre total de groupes: {len(self.groups)}
Nombre total de notes: {len(all_data)}

STATISTIQUES DES NOTES:
Moyenne générale: {np.mean(all_data):.2f}
Médiane: {np.median(all_data):.2f}
Écart-type: {np.std(all_data):.2f}
Minimum: {min(all_data):.2f}
Maximum: {max(all_data):.2f}

Quartiles:
  Q1 (25%): {np.percentile(all_data, 25):.2f}
  Q2 (50%): {np.percentile(all_data, 50):.2f}
  Q3 (75%): {np.percentile(all_data, 75):.2f}
        """
        
        text_widget = tk.Text(main_frame, height=15, width=50, font=('Courier', 10))
        text_widget.insert('1.0', stats_text)
        text_widget.config(state='disabled')
        text_widget.pack(pady=10)
        
        ttk.Button(main_frame, text="Fermer", command=stats_window.destroy).pack(pady=10)
    
    def compare_groups(self):
        """Compare les performances entre les groupes"""
        if len(self.groups) < 2:
            messagebox.showinfo("Info", "Au moins 2 groupes nécessaires pour la comparaison")
            return
        
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            group_names = []
            group_means = []
            
            for group in self.groups:
                data = group.get_data()
                if data:
                    group_names.append(group.nom)
                    group_means.append(group.moyenne())
            
            if not group_names:
                messagebox.showinfo("Info", "Aucune donnée à comparer")
                return
            
            bars = ax.bar(group_names, group_means, color='skyblue', edgecolor='black')
            ax.set_title('Comparaison des Moyennes par Groupe', fontsize=14, fontweight='bold')
            ax.set_xlabel('Groupes', fontsize=12)
            ax.set_ylabel('Moyenne', fontsize=12)
            ax.grid(True, axis='y', alpha=0.3)
            
            # Ajouter les valeurs au-dessus des barres
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}',
                       ha='center', va='bottom')
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de comparer les groupes:\n{str(e)}")
    
    def launch_comparison(self):
        """Lance une comparaison personnalisée"""
        comp_type = self.comparison_type.get()
        
        if comp_type == "Comparer des individus":
            self.compare_individuals()
        else:
            self.compare_groups_detailed()
    
    def compare_individuals(self):
        """Compare plusieurs individus sélectionnés"""
        # Sélection multiple d'individus (simplifié pour l'exemple)
        messagebox.showinfo("Info", "Fonctionnalité de comparaison d'individus à implémenter")
    
    def compare_groups_detailed(self):
        """Comparaison détaillée des groupes"""
        self.compare_groups()
    
    def show_trends(self):
        """Affiche les tendances temporelles (si dates disponibles)"""
        messagebox.showinfo("Info", "Fonctionnalité de tendances à implémenter avec des dates")
    
    def export_stats(self):
        """Exporte les statistiques vers un fichier CSV"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")],
            title="Exporter les statistiques"
        )
        
        if not filename:
            return
        
        try:
            import csv
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Nom', 'Prénom', 'Groupe', 'Nb Notes', 'Moyenne', 'Min', 'Max', 'Écart-type'])
                
                for ind in self.individuals:
                    data = ind.get_data()
                    if data:
                        writer.writerow([
                            ind.nom,
                            ind.prenom,
                            ind.groupe,
                            len(data),
                            f"{sum(data)/len(data):.2f}",
                            f"{min(data):.2f}",
                            f"{max(data):.2f}",
                            f"{np.std(data):.2f}"
                        ])
            
            messagebox.showinfo("Succès", f"Statistiques exportées dans:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'exporter:\n{str(e)}")
    
    # ============================================================================
    # MÉTHODES UTILITAIRES
    # ============================================================================
    
    def show_help(self):
        """Affiche l'aide"""
        help_text = """
GUIDE D'UTILISATION - QUANTIV

ONGLET ENTRÉES INDIVIDUELLES:
- Ajouter: Créer une nouvelle entrée avec nom, prénom, groupe et notes
- Modifier: Double-cliquer ou utiliser le bouton pour éditer
- Supprimer: Supprimer l'entrée sélectionnée
- Graphiques: Affiche un graphique radar des notes

ONGLET GROUPES:
- Visualiser les statistiques par groupe
- Comparer les performances
- Voir la distribution des notes

ONGLET COMPARAISONS:
- Comparer plusieurs entrées ou groupes entre eux

FILTRES:
- Utiliser la barre de recherche pour trouver rapidement
- Filtrer par groupe dans l'onglet Entrées
        """
        
        messagebox.showinfo("Guide d'utilisation", help_text)
    
    def show_about(self):
        """Affiche les informations À propos"""
        about_text = """
QUANTIV - Analyse Statistique
Version 2.0

Application d'analyse de données pour 
entrées individuelles et groupes.

Développé avec Python, Tkinter et Matplotlib.

© 2024 - Tous droits réservés
        """
        messagebox.showinfo("À propos", about_text)
    
    def update_status(self, message):
        """Met à jour la barre de statut"""
        self.status_label.config(text=message)


def main():
    """Fonction principale pour lancer l'application"""
    try:
        import Stockcsv
        Stockcsv.CreateCsv()
    except Exception as e:
        print(f"Erreur lors de la création du CSV: {e}")
    
    root = tk.Tk()
    app = StatisticsWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()