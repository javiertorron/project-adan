import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Dict
from ..domain.entities.bot import Bot
from ..domain.entities.personality import Personality
from .dialogs.bot_creation_dialog import BotCreationDialog
from .dialogs.personality_editor_dialog import PersonalityEditorDialog
import json
from pathlib import Path

class BotListWindow(ttk.Frame):
    """
    Ventana principal que muestra la lista de bots y permite gestionarlos.
    Incluye funcionalidades de ordenamiento, filtrado y visualización detallada.
    """
    
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.bots: Dict[str, Bot] = {}
        self.selected_bot: Optional[Bot] = None
        
        self.setup_ui()
        self.load_bots()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.create_toolbar()
        self.create_main_content()
        self.create_status_bar()
        
    def create_toolbar(self):
        """Crea la barra de herramientas"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Botones principales
        self.create_button = ttk.Button(
            toolbar,
            text="Crear Bot",
            command=self.create_bot,
            width=15
        )
        self.create_button.pack(side=tk.LEFT, padx=2)
        
        self.edit_button = ttk.Button(
            toolbar,
            text="Editar Bot",
            command=self.edit_bot,
            width=15,
            state=tk.DISABLED
        )
        self.edit_button.pack(side=tk.LEFT, padx=2)
        
        self.delete_button = ttk.Button(
            toolbar,
            text="Eliminar Bot",
            command=self.delete_bot,
            width=15,
            state=tk.DISABLED
        )
        self.delete_button.pack(side=tk.LEFT, padx=2)
        
        self.simulate_button = ttk.Button(
            toolbar,
            text="Simular",
            command=self.simulate_bot,
            width=15
        )
        self.simulate_button.pack(side=tk.LEFT, padx=2)
        
        # Separador
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Búsqueda
        ttk.Label(toolbar, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_bots)
        self.search_entry = ttk.Entry(toolbar, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
    def create_main_content(self):
        """Crea el contenido principal con la lista y detalles"""
        main_frame = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel izquierdo: Lista de bots
        left_frame = ttk.Frame(main_frame)
        main_frame.add(left_frame, weight=1)
        
        # Crear Treeview con scrollbar
        columns = ('name', 'dominant_trait')
        self.bot_tree = ttk.Treeview(
            left_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )
        
        # Configurar columnas
        self.bot_tree.heading('name', text='Nombre', command=lambda: self.sort_bots('name'))
        self.bot_tree.heading('dominant_trait', text='Rasgo Dominante', 
                            command=lambda: self.sort_bots('dominant_trait'))
        
        self.bot_tree.column('name', width=150)
        self.bot_tree.column('dominant_trait', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, 
                                command=self.bot_tree.yview)
        self.bot_tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar Treeview y scrollbar
        self.bot_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Panel derecho: Detalles del bot
        right_frame = ttk.Frame(main_frame)
        main_frame.add(right_frame, weight=1)
        
        # Frame para detalles
        self.details_frame = ttk.LabelFrame(right_frame, text="Detalles del Bot")
        self.details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear visualización de factores de personalidad
        self.create_personality_view(self.details_frame)
        
        # Configurar evento de selección
        self.bot_tree.bind('<<TreeviewSelect>>', self.on_bot_selected)
        
    def create_personality_view(self, parent):
        """Crea la vista de factores de personalidad"""
        self.factor_bars = {}
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configurar scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Crear barras de progreso para cada factor
        for code, (name, low, high) in Personality.FACTORS.items():
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=name, width=20).pack(side=tk.LEFT)
            
            progress = ttk.Progressbar(
                frame,
                length=200,
                mode='determinate',
                maximum=200  # -1 a 1 convertido a 0-200
            )
            progress.pack(side=tk.LEFT, padx=5)
            
            value_label = ttk.Label(frame, text="0.00", width=6)
            value_label.pack(side=tk.LEFT)
            
            desc_label = ttk.Label(frame, text="Neutral", width=15)
            desc_label.pack(side=tk.LEFT)
            
            self.factor_bars[code] = {
                'progress': progress,
                'value_label': value_label,
                'desc_label': desc_label
            }
        
        # Empaquetar canvas y scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_status_bar(self):
        """Crea la barra de estado"""
        self.status_bar = ttk.Label(self, text="", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
        
    def load_bots(self):
        """Carga los bots desde el archivo de persistencia"""
        try:
            if Path('bots.json').exists():
                data = json.loads(Path('bots.json').read_text())
                self.bots = {name: Bot.from_dict(bot_data) 
                            for name, bot_data in data.items()}
                self.refresh_bot_list()
                self.update_status(f"Bots cargados: {len(self.bots)}")
        except Exception as e:
            self.update_status(f"Error al cargar bots: {str(e)}")
            
    def save_bots(self):
        """Guarda los bots en el archivo de persistencia"""
        try:
            data = {name: bot.to_dict() for name, bot in self.bots.items()}
            Path('bots.json').write_text(json.dumps(data, indent=2))
            self.update_status("Bots guardados correctamente")
        except Exception as e:
            self.update_status(f"Error al guardar bots: {str(e)}")
            
    def create_bot(self):
        """Abre el diálogo de creación de bot"""
        def on_bot_created(bot: Bot):
            if bot.name not in self.bots:
                self.bots[bot.name] = bot
                self.save_bots()
                self.refresh_bot_list()
                self.update_status(f"Bot '{bot.name}' creado")
            else:
                self.update_status(f"Ya existe un bot llamado '{bot.name}'")
                
        BotCreationDialog(self, on_bot_created)
        
    def edit_bot(self):
        """Abre el diálogo de edición de bot"""
        if not self.selected_bot:
            return
            
        bot = self.bots[self.selected_bot]
        def on_save():
            self.save_bots()
            self.refresh_bot_list()
            self.update_status(f"Bot '{bot.name}' actualizado")
            
        PersonalityEditorDialog(self, bot.personality, on_save)
        
    def delete_bot(self):
        """Elimina el bot seleccionado"""
        if not self.selected_bot:
            return
            
        if tk.messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar el bot '{self.selected_bot}'?"
        ):
            del self.bots[self.selected_bot]
            self.save_bots()
            self.selected_bot = None
            self.refresh_bot_list()
            self.update_status(f"Bot eliminado")

    def simulate_bot(self):
        """Abre la ventana de simulación para el bot seleccionado"""
        if not self.selected_bot:
            return
        
        bot = self.selected_bot
        
        if bot:
            from .dialogs.simulation_dialog import SimulationDialog
            dialog = SimulationDialog(self, bot)
            
    def refresh_bot_list(self):
        """Actualiza la lista de bots"""
        self.bot_tree.delete(*self.bot_tree.get_children())
        
        for name, bot in self.bots.items():
            # Encontrar rasgo dominante
            dominant_trait = self.get_dominant_trait(bot.personality)
            
            self.bot_tree.insert(
                '',
                'end',
                values=(name, dominant_trait)
            )
            
    def get_dominant_trait(self, personality: Personality) -> str:
        """Obtiene el rasgo dominante de una personalidad"""
        max_value = 0
        dominant_trait = "Neutral"
        
        for code, factor in personality.factors.items():
            abs_value = abs(factor.value)
            if abs_value > max_value:
                max_value = abs_value
                if factor.value > 0:
                    dominant_trait = factor.high_label
                else:
                    dominant_trait = factor.low_label
                    
        return dominant_trait
        
    def on_bot_selected(self, event):
        """Maneja la selección de un bot"""
        selection = self.bot_tree.selection()
        if not selection:
            self.selected_bot = None
            self.edit_button.configure(state=tk.DISABLED)
            self.delete_button.configure(state=tk.DISABLED)
            self.simulate_button.configure(state=tk.DISABLED)
            self.clear_personality_view()
            return
            
        # Obtener bot seleccionado
        item = self.bot_tree.item(selection[0])
        selected_name = item['values'][0]
        for bot_name, bot_object in self.bots.items():
            if bot_name == selected_name:
                self.selected_bot = bot_object
        
        # Habilitar botones
        self.edit_button.configure(state=tk.NORMAL)
        self.delete_button.configure(state=tk.NORMAL)
        self.simulate_button.configure(state=tk.NORMAL)
        
        # Actualizar vista de personalidad
        self.update_personality_view(self.bots[selected_name].personality)
        
    def update_personality_view(self, personality: Personality):
        """Actualiza la vista de personalidad con los valores del bot seleccionado"""
        for code, factor in personality.factors.items():
            if code in self.factor_bars:
                controls = self.factor_bars[code]
                
                # Actualizar barra de progreso (-1 a 1 -> 0 a 200)
                progress_value = (factor.value + 1) * 100
                controls['progress']['value'] = progress_value
                
                # Actualizar etiquetas
                controls['value_label']['text'] = f"{factor.value:.2f}"
                controls['desc_label']['text'] = factor.get_descriptor()
                
                # Actualizar color
                if factor.value > 0:
                    controls['progress']['style'] = 'green.Horizontal.TProgressbar'
                elif factor.value < 0:
                    controls['progress']['style'] = 'red.Horizontal.TProgressbar'
                else:
                    controls['progress']['style'] = 'Horizontal.TProgressbar'
                    
    def clear_personality_view(self):
        """Limpia la vista de personalidad"""
        for controls in self.factor_bars.values():
            controls['progress']['value'] = 100  # Valor medio
            controls['value_label']['text'] = "0.00"
            controls['desc_label']['text'] = "Neutral"
            controls['progress']['style'] = 'Horizontal.TProgressbar'
            
    def sort_bots(self, column):
        """Ordena la lista de bots por la columna especificada"""
        items = [(self.bot_tree.set(child, column), child) 
                for child in self.bot_tree.get_children('')]
        
        items.sort()  # Ordenar por el valor de la columna
        
        for idx, (_, child) in enumerate(items):
            self.bot_tree.move(child, '', idx)
            
    def filter_bots(self, *args):
        """Filtra la lista de bots según el texto de búsqueda"""
        search_text = self.search_var.get().lower()
        self.bot_tree.delete(*self.bot_tree.get_children())
        
        for name, bot in self.bots.items():
            if search_text in name.lower():
                dominant_trait = self.get_dominant_trait(bot.personality)
                self.bot_tree.insert('', 'end', values=(name, dominant_trait))
                
    def update_status(self, message: str):
        """Actualiza el mensaje de la barra de estado"""
        self.status_bar['text'] = message

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Bot Manager")
    
    # Configurar estilos
    style = ttk.Style()
    style.configure("green.Horizontal.TProgressbar", background='green')
    style.configure("red.Horizontal.TProgressbar", background='red')
    
    app = BotListWindow(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    # Centrar ventana
    root.update_idletasks()
    width = 800
    height = 600
    x = (root.winfo_screenwidth() // 2)
