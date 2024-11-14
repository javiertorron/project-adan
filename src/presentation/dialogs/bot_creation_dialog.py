import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from ...domain.entities.bot import Bot
from ...domain.entities.personality import Personality
from ...presentation.widgets.factor_slider import FactorSlider

class BotCreationDialog(tk.Toplevel):
    def __init__(self, parent, on_create: Callable[[Bot], None]):
        super().__init__(parent)
        self.on_create = on_create
        self.personality = Personality()
        
        self.title("Crear Nuevo Bot")
        self.resizable(False, False)
        self.setup_window()
        self.create_widgets()
        
        # Hacer la ventana modal
        self.transient(parent)
        self.grab_set()
        
    def setup_window(self):
        """Configura la geometría y posición de la ventana"""
        # Dimensiones de la ventana
        width = 800
        height = 700
        
        # Obtener dimensiones de la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calcular posición
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Configurar geometría
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Crea todos los widgets del diálogo"""
        self.create_name_section()
        self.create_personality_section()
        self.create_button_section()
        
    def create_name_section(self):
        """Crea la sección para el nombre del bot"""
        name_frame = ttk.LabelFrame(self, text="Identificación", padding="10")
        name_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(name_frame, text="Nombre del Bot:").pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(name_frame, width=30)
        self.name_entry.pack(side=tk.LEFT, padx=5)
        
    def create_personality_section(self):
        """Crea la sección de personalidad con los sliders y valores numéricos"""
        personality_frame = ttk.LabelFrame(self, text="Personalidad", padding="10")
        personality_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Crear un canvas con scrollbar
        canvas = tk.Canvas(personality_frame)
        scrollbar = ttk.Scrollbar(personality_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar los widgets
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Crear controles para cada factor
        self.factor_controls = {}
        factors_list = list(self.personality.FACTORS.items())
        mid_point = len(factors_list) // 2
        
        # Crear frames para dos columnas
        left_frame = ttk.Frame(self.scrollable_frame)
        right_frame = ttk.Frame(self.scrollable_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Distribuir factores en las columnas
        for i, (code, (name, low, high)) in enumerate(factors_list):
            frame = left_frame if i < mid_point else right_frame
            self.create_factor_control(frame, code, name, low, high)
        
        # Configurar el scroll con el mouse
        self.scrollable_frame.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollable_frame.bind('<Leave>', self._unbound_to_mousewheel)
        
    def create_factor_control(self, parent, code: str, name: str, low: str, high: str):
        """Crea un control completo para un factor de personalidad"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        
        # Label Frame para el factor
        factor_frame = ttk.LabelFrame(frame, text=name)
        factor_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Frame para los controles
        controls_frame = ttk.Frame(factor_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Slider personalizado
        slider = FactorSlider(
            controls_frame,
            command=lambda value: self._on_slider_change(code, value)
        )
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Entry para valor numérico
        vcmd = (self.register(self._validate_numeric), '%P')
        entry = ttk.Entry(controls_frame, width=6, validate='key', validatecommand=vcmd)
        entry.insert(0, "0.00")
        entry.pack(side=tk.LEFT, padx=5)
        
        # Label descriptor
        description = ttk.Label(controls_frame, text="Neutral", width=15)
        description.pack(side=tk.LEFT, padx=5)
        
        # Almacenar controles
        self.factor_controls[code] = {
            'slider': slider,
            'entry': entry,
            'description': description,
            'low': low,
            'high': high
        }
        
        # Configurar callbacks
        entry.bind('<FocusOut>', lambda e, code=code: self._on_entry_change(code))
        entry.bind('<Return>', lambda e, code=code: self._on_entry_change(code))
        
    def create_button_section(self):
        """Crea la sección de botones de acción"""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="Randomizar",
            command=self._randomize
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Crear",
            command=self._create_bot
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
    def _validate_numeric(self, value: str) -> bool:
        """Valida la entrada numérica"""
        if value == "" or value == "-":
            return True
        try:
            float_val = float(value)
            return -1 <= float_val <= 1
        except ValueError:
            return False
            
    def _on_slider_change(self, code: str, value: float):
        """Maneja el cambio en el slider"""
        controls = self.factor_controls[code]
        
        # Actualizar entry
        controls['entry'].delete(0, tk.END)
        controls['entry'].insert(0, f"{value:.2f}")
        
        # Actualizar descripción
        self._update_description(code, value)
            
    def _on_entry_change(self, code: str):
        """Maneja el cambio en el entry"""
        controls = self.factor_controls[code]
        try:
            value = float(controls['entry'].get())
            value = max(-1, min(1, value))  # Clamp value
            
            # Actualizar slider
            controls['slider'].set(value)
            
            # Actualizar entry con el valor formateado
            controls['entry'].delete(0, tk.END)
            controls['entry'].insert(0, f"{value:.2f}")
            
            # Actualizar descripción
            self._update_description(code, value)
            
        except ValueError:
            # Restaurar valor anterior
            controls['entry'].delete(0, tk.END)
            controls['entry'].insert(0, "0.00")
            
    def _update_description(self, code: str, value: float):
        """Actualiza la descripción del factor basada en el valor"""
        controls = self.factor_controls[code]
        description = ""
        
        if value > 0.75:
            description = f"Muy {controls['high']}"
        elif value > 0.25:
            description = controls['high']
        elif value > -0.25:
            description = "Neutral"
        elif value > -0.75:
            description = controls['low']
        else:
            description = f"Muy {controls['low']}"
            
        controls['description'].configure(text=description)
        
    def _randomize(self):
        """Randomiza todos los valores de personalidad"""
        self.personality.randomize()
        for code, factor_value in self.personality.to_dict().items():
            controls = self.factor_controls[code]
            controls['slider'].set(factor_value)
            controls['entry'].delete(0, tk.END)
            controls['entry'].insert(0, f"{factor_value:.2f}")
            self._update_description(code, factor_value)
            
    def _create_bot(self):
        """Crea el bot con los valores actuales"""
        name = self.name_entry.get().strip()
        if not name:
            tk.messagebox.showerror("Error", "Por favor, introduce un nombre para el bot")
            return
            
        # Actualizar personalidad con valores actuales
        personality_values = {}
        for code, controls in self.factor_controls.items():
            try:
                value = float(controls['entry'].get())
                personality_values[code] = max(-1, min(1, value))
            except ValueError:
                personality_values[code] = 0.0
                
        self.personality.from_dict(personality_values)
        bot = Bot(name, self.personality)
        
        self.on_create(bot)
        self.destroy()
        
    def _bound_to_mousewheel(self, event):
        """Vincula el scroll del mouse"""
        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _unbound_to_mousewheel(self, event):
        """Desvincula el scroll del mouse"""
        self.scrollable_frame.unbind_all("<MouseWheel>")
        
    def _on_mousewheel(self, event):
        """Maneja el evento de scroll del mouse"""
        canvas = event.widget.master.master
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
