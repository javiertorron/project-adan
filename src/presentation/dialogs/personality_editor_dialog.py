import tkinter as tk
from tkinter import ttk
from typing import Callable
from ...domain.entities.personality import Personality

class PersonalityEditorDialog(tk.Toplevel):
    def __init__(self, parent, personality: Personality, on_save: Callable):
        super().__init__(parent)
        self.personality = personality
        self.on_save = on_save
        
        self.title("Editor de Personalidad")
        self._center_window()
        self._create_widgets()
        
    def _center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = 800
        height = 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _create_widgets(self):
        # Frame principal con scroll
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frames para organizar los factores
        left_frame = ttk.Frame(main_frame)
        right_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Crear controles para cada factor
        self.factor_controls = {}
        factors = list(self.personality.factors.items())
        mid_point = len(factors) // 2
        
        for i, (code, factor) in enumerate(factors):
            frame = left_frame if i < mid_point else right_frame
            self._create_factor_control(frame, factor)
        
        # Botones de acción
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Randomizar", 
                  command=self._randomize).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Guardar",
                  command=self._save).pack(side=tk.LEFT, padx=5)
    
    def _create_factor_control(self, parent, factor):
        frame = ttk.LabelFrame(parent, text=factor.name)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Slider
        slider = ttk.Scale(frame, from_=-1, to=1, orient=tk.HORIZONTAL,
                         length=200, value=factor.value)
        slider.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Entry numérico
        vcmd = (self.register(self._validate_numeric), '%P')
        entry = ttk.Entry(frame, width=6, validate='key', validatecommand=vcmd)
        entry.insert(0, f"{factor.value:.2f}")
        entry.pack(side=tk.LEFT, padx=5)
        
        # Label descriptor
        descriptor = ttk.Label(frame, text=factor.get_descriptor(), width=15)
        descriptor.pack(side=tk.LEFT, padx=5)
        
        # Almacenar controles y configurar callbacks
        self.factor_controls[factor.code] = {
            'slider': slider,
            'entry': entry,
            'descriptor': descriptor,
            'factor': factor
        }
        
        # Configurar callbacks
        slider.configure(command=lambda value, code=factor.code: 
                       self._on_slider_change(code, float(value)))
        entry.bind('<FocusOut>', lambda e, code=factor.code: 
                  self._on_entry_change(code))
        entry.bind('<Return>', lambda e, code=factor.code: 
                  self._on_entry_change(code))
    
    def _validate_numeric(self, value):
        if value == "" or value == "-":
            return True
        try:
            float_val = float(value)
            return -1 <= float_val <= 1
        except ValueError:
            return False
    
    def _on_slider_change(self, code: str, value: float):
        controls = self.factor_controls[code]
        factor = controls['factor']
        factor.value = value
        
        controls['entry'].delete(0, tk.END)
        controls['entry'].insert(0, f"{value:.2f}")
        controls['descriptor'].config(text=factor.get_descriptor())
    
    def _on_entry_change(self, code: str):
        controls = self.factor_controls[code]
        try:
            value = float(controls['entry'].get())
            value = max(-1, min(1, value))  # Clamp value
            
            controls['slider'].set(value)
            controls['factor'].value = value
            controls['descriptor'].config(text=controls['factor'].get_descriptor())
            
            controls['entry'].delete(0, tk.END)
            controls['entry'].insert(0, f"{value:.2f}")
        except ValueError:
            # Restaurar valor anterior
            controls['entry'].delete(0, tk.END)
            controls['entry'].insert(0, f"{controls['factor'].value:.2f}")
    
    def _randomize(self):
        self.personality.randomize()
        for code, controls in self.factor_controls.items():
            value = self.personality.factors[code].value
            controls['slider'].set(value)
            controls['entry'].delete(0, tk.END)
            controls['entry'].insert(0, f"{value:.2f}")
            controls['descriptor'].config(
                text=self.personality.factors[code].get_descriptor()
            )
    
    def _save(self):
        # Actualizar todos los valores antes de guardar
        for code, controls in self.factor_controls.items():
            try:
                value = float(controls['entry'].get())
                self.personality.factors[code].value = max(-1, min(1, value))
            except ValueError:
                continue
        
        self.on_save()
        self.destroy()