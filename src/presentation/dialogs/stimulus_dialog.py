import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, List, Optional
from enum import Enum, auto

from ...domain.models.stimulus import Stimulus
from ...domain.entities.bot import Bot
from dataclasses import dataclass

class NeedType(Enum):
    SURVIVAL = 1
    PHYSIOLOGICAL = 2
    SAFETY = 3
    SOCIAL = 4
    ESTEEM = 5
    GROWTH = 6

class EmotionalState(Enum):
    CALM = auto()
    ALERT = auto()
    STRESSED = auto()
    PANICKED = auto()

@dataclass
class NeedImpact:
    """Representa el impacto en una necesidad específica"""
    need_type: NeedType
    intensity: float  # Qué tan fuerte es la necesidad 0.0 a 1.0
    satisfaction_level: float  # Cuánto satisface el estímulo 0.0 a 1.0
    urgency: float  # Qué tan urgente es atender esta necesidad 0.0 a 1.0

@dataclass
class EmotionalImpact:
    """Representa el impacto emocional del estímulo"""
    current_stability: float  # Estabilidad emocional actual del NPC 0.0 a 1.0
    impact_intensity: float  # Intensidad del impacto emocional -1.0 a 1.0
    duration: float  # Duración esperada del impacto 0.0 a 1.0

class StimulusDialog(tk.Toplevel):
    """Diálogo para configurar y enviar un estímulo al bot"""
    
    def __init__(self, parent: tk.Tk, bot: Bot, on_stimulus_created: Optional[Callable] = None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.on_stimulus_created = on_stimulus_created
        self.need_impacts: List[NeedImpact] = []
        
        self.title("Nuevo Estímulo")
        self.setup_window()
        self.create_widgets()
        self.grab_set()  # Hacer el diálogo modal
        
    def setup_window(self):
        """Configura la ventana"""
        width = 800
        height = 600
        
        # Centrar respecto a la ventana padre
        x = self.master.winfo_x() + (self.master.winfo_width() - width) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
        
    def create_widgets(self):
        """Crea todos los widgets del diálogo"""
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña: Información Básica
        basic_frame = ttk.Frame(notebook, padding=10)
        notebook.add(basic_frame, text="Información Básica")
        self.create_basic_info(basic_frame)
        
        # Pestaña: Impacto en Necesidades
        needs_frame = ttk.Frame(notebook, padding=10)
        notebook.add(needs_frame, text="Necesidades")
        self.create_needs_section(needs_frame)
        
        # Pestaña: Impacto Emocional
        emotional_frame = ttk.Frame(notebook, padding=10)
        notebook.add(emotional_frame, text="Impacto Emocional")
        self.create_emotional_section(emotional_frame)
        
        # Botones de acción
        self.create_action_buttons()
        
    def create_basic_info(self, parent):
        """Crea la sección de información básica"""
        # Tipo de estímulo
        basic_frame = ttk.LabelFrame(parent, text="Información del Estímulo", padding=10)
        basic_frame.pack(fill=tk.X, expand=True)
        
        # Grid para organizar elementos
        ttk.Label(basic_frame, text="Tipo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.type_entry = ttk.Entry(basic_frame, width=40)
        self.type_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(basic_frame, text="Origen:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.source_entry = ttk.Entry(basic_frame, width=40)
        self.source_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Características generales
        chars_frame = ttk.LabelFrame(parent, text="Características", padding=10)
        chars_frame.pack(fill=tk.X, expand=True, pady=10)
        
        # Nivel de amenaza
        ttk.Label(chars_frame, text="Nivel de Amenaza:").grid(row=0, column=0, sticky=tk.W)
        self.threat_scale = ttk.Scale(
            chars_frame, from_=0, to=1, orient=tk.HORIZONTAL
        )
        self.threat_scale.grid(row=0, column=1, sticky=tk.EW, pady=5)
        self.threat_value = ttk.Label(chars_frame, text="0.0")
        self.threat_value.grid(row=0, column=2, padx=5)
        self.threat_scale.configure(
            command=lambda v: self.threat_value.configure(text=f"{float(v):.1f}")
        )
        
        # Inmediatez
        ttk.Label(chars_frame, text="Inmediatez:").grid(row=1, column=0, sticky=tk.W)
        self.immediacy_scale = ttk.Scale(
            chars_frame, from_=0, to=1, orient=tk.HORIZONTAL
        )
        self.immediacy_scale.grid(row=1, column=1, sticky=tk.EW, pady=5)
        self.immediacy_value = ttk.Label(chars_frame, text="0.0")
        self.immediacy_value.grid(row=1, column=2, padx=5)
        self.immediacy_scale.configure(
            command=lambda v: self.immediacy_value.configure(text=f"{float(v):.1f}")
        )
        
        # Duración
        ttk.Label(chars_frame, text="Duración:").grid(row=2, column=0, sticky=tk.W)
        self.duration_scale = ttk.Scale(
            chars_frame, from_=0, to=1, orient=tk.HORIZONTAL
        )
        self.duration_scale.grid(row=2, column=1, sticky=tk.EW, pady=5)
        self.duration_value = ttk.Label(chars_frame, text="0.0")
        self.duration_value.grid(row=2, column=2, padx=5)
        self.duration_scale.configure(
            command=lambda v: self.duration_value.configure(text=f"{float(v):.1f}")
        )
        
        chars_frame.columnconfigure(1, weight=1)
        
    def create_needs_section(self, parent):
        """Crea la sección de impacto en necesidades"""
        # Panel superior para añadir impactos
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(control_frame, text="Necesidad:").pack(side=tk.LEFT, padx=5)
        self.need_type_cb = ttk.Combobox(
            control_frame,
            values=[need.name for need in NeedType],
            state="readonly",
            width=15
        )
        self.need_type_cb.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="Añadir Impacto",
            command=self.add_need_impact
        ).pack(side=tk.LEFT, padx=5)
        
        # Lista de impactos
        list_frame = ttk.LabelFrame(parent, text="Impactos Configurados")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview para impactos
        columns = ('need', 'intensity', 'satisfaction', 'urgency')
        self.impacts_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            selectmode='browse',
            height=10
        )
        
        self.impacts_tree.heading('need', text='Necesidad')
        self.impacts_tree.heading('intensity', text='Intensidad')
        self.impacts_tree.heading('satisfaction', text='Satisfacción')
        self.impacts_tree.heading('urgency', text='Urgencia')
        
        for col in columns:
            self.impacts_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.impacts_tree.yview)
        self.impacts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.impacts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón eliminar
        ttk.Button(
            list_frame,
            text="Eliminar Seleccionado",
            command=self.remove_need_impact
        ).pack(pady=5)
        
    def create_emotional_section(self, parent):
        """Crea la sección de impacto emocional"""
        frame = ttk.LabelFrame(parent, text="Configuración de Impacto Emocional", padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Estabilidad actual
        ttk.Label(frame, text="Estabilidad Emocional Actual:").grid(row=0, column=0, sticky=tk.W)
        self.stability_scale = ttk.Scale(frame, from_=0, to=1, orient=tk.HORIZONTAL)
        self.stability_scale.grid(row=0, column=1, sticky=tk.EW, pady=5)
        self.stability_value = ttk.Label(frame, text="0.0")
        self.stability_value.grid(row=0, column=2, padx=5)
        self.stability_scale.configure(
            command=lambda v: self.stability_value.configure(text=f"{float(v):.1f}")
        )
        
        # Intensidad del impacto
        ttk.Label(frame, text="Intensidad del Impacto:").grid(row=1, column=0, sticky=tk.W)
        self.impact_scale = ttk.Scale(frame, from_=-1, to=1, orient=tk.HORIZONTAL)
        self.impact_scale.grid(row=1, column=1, sticky=tk.EW, pady=5)
        self.impact_value = ttk.Label(frame, text="0.0")
        self.impact_value.grid(row=1, column=2, padx=5)
        self.impact_scale.configure(
            command=lambda v: self.impact_value.configure(text=f"{float(v):.1f}")
        )
        
        # Duración del impacto emocional
        ttk.Label(frame, text="Duración del Impacto:").grid(row=2, column=0, sticky=tk.W)
        self.emotional_duration_scale = ttk.Scale(frame, from_=0, to=1, orient=tk.HORIZONTAL)
        self.emotional_duration_scale.grid(row=2, column=1, sticky=tk.EW, pady=5)
        self.emotional_duration_value = ttk.Label(frame, text="0.0")
        self.emotional_duration_value.grid(row=2, column=2, padx=5)
        self.emotional_duration_scale.configure(
            command=lambda v: self.emotional_duration_value.configure(text=f"{float(v):.1f}")
        )
        
        frame.columnconfigure(1, weight=1)
        
    def create_action_buttons(self):
        """Crea los botones de acción"""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Crear Estímulo",
            command=self.create_stimulus
        ).pack(side=tk.RIGHT, padx=5)
        
    def add_need_impact(self):
        """Abre el diálogo para añadir un impacto en necesidad"""
        if not self.need_type_cb.get():
            messagebox.showwarning("Advertencia", "Selecciona un tipo de necesidad")
            return
            
        dialog = NeedImpactDialog(self, self.need_type_cb.get())
        self.wait_window(dialog)
        
        if dialog.result is not None:
            self.impacts_tree.insert(
                '',
                'end',
                values=(
                    dialog.result.need_type.name,
                    f"{dialog.result.intensity:.2f}",
                    f"{dialog.result.satisfaction_level:.2f}",
                    f"{dialog.result.urgency:.2f}"
                )
            )
            self.need_impacts.append(dialog.result)
            
    def remove_need_impact(self):
        """Elimina el impacto seleccionado"""
        selected = self.impacts_tree.selection()
        if not selected:
            return
            
        index = self.impacts_tree.index(selected[0])
        self.impacts_tree.delete(selected[0])
        del self.need_impacts[index]
        
    def create_stimulus(self):
        if not self.validate_stimulus():
            return
            
        # Crear objeto Stimulus
        stimulus = Stimulus(
            type=self.type_entry.get(),
            source=self.source_entry.get(),
            need_impacts=self.need_impacts,
            emotional_impact=EmotionalImpact(
                current_stability=self.stability_scale.get(),
                impact_intensity=self.impact_scale.get(),
                duration=self.emotional_duration_scale.get()
            ),
            threat_level=self.threat_scale.get(),
            immediacy=self.immediacy_scale.get(),
            duration=self.duration_scale.get()
        )
        
        # Procesar el estímulo
        result = self.bot.stimulus_processor.evaluate_stimulus(stimulus)
        
        # Actualizar estado del bot
        self.bot.emotional_manager.update_emotional_state(
            stimulus.emotional_impact.impact_intensity * stimulus.immediacy
        )
        
        for impact in stimulus.need_impacts:
            self.bot.needs_manager.apply_impact(
                impact.need_type,
                impact.intensity * impact.satisfaction_level
            )
        
        # Añadir al historial de eventos
        if self.on_stimulus_created:
            description = f"Tipo: {stimulus.type} - Origen: {stimulus.source}"
            impact = f"Amenaza: {stimulus.threat_level:.2f}"
            self.on_stimulus_created(
                "Estímulo",
                description,
                impact,
                result['should_react']
            )
        
        self.destroy()
        
    def validate_stimulus(self) -> bool:
        """Valida que todos los datos necesarios estén presentes"""
        if not self.type_entry.get().strip():
            messagebox.showwarning("Validación", "Debe especificar el tipo de estímulo")
            return False
            
        if not self.source_entry.get().strip():
            messagebox.showwarning("Validación", "Debe especificar el origen del estímulo")
            return False
            
        if not self.need_impacts:
            if not messagebox.askyesno(
                "Confirmar",
                "No ha configurado ningún impacto en necesidades. ¿Desea continuar?"
            ):
                return False
                
        return True
    
    def show_result_dialog(self, result: Dict):
        """Muestra el diálogo con el resultado del estímulo"""
        from .stimulus_result_dialog import StimulusResultDialog
        dialog = StimulusResultDialog(self, result)
        dialog.grab_set()  # Hacer el diálogo modal
        self.wait_window(dialog)  # Esperar a que se cierre el diálogo antes de continuar

class NeedImpactDialog(tk.Toplevel):
    """Diálogo para configurar el impacto en una necesidad específica"""
    
    def __init__(self, parent: tk.Tk, need_type: str):
        super().__init__(parent)
        self.need_type = NeedType[need_type]
        self.result = None
        
        self.title(f"Configurar Impacto - {need_type}")
        self.setup_window()
        self.create_widgets()
        self.grab_set()
        
    def setup_window(self):
        """Configura la ventana"""
        width = 400
        height = 300
        
        # Centrar respecto a la ventana padre
        x = self.master.winfo_x() + (self.master.winfo_width() - width) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
        
    def create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Intensidad
        intensity_frame = ttk.LabelFrame(main_frame, text="Intensidad", padding=5)
        intensity_frame.pack(fill=tk.X, pady=5)
        
        self.intensity_scale = ttk.Scale(
            intensity_frame,
            from_=0, to=1,
            orient=tk.HORIZONTAL
        )
        self.intensity_scale.pack(fill=tk.X)
        self.intensity_value = ttk.Label(intensity_frame, text="0.0")
        self.intensity_value.pack()
        self.intensity_scale.configure(
            command=lambda v: self.intensity_value.configure(text=f"{float(v):.2f}")
        )
        
        # Nivel de Satisfacción
        satisfaction_frame = ttk.LabelFrame(main_frame, text="Nivel de Satisfacción", padding=5)
        satisfaction_frame.pack(fill=tk.X, pady=5)
        
        self.satisfaction_scale = ttk.Scale(
            satisfaction_frame,
            from_=0, to=1,
            orient=tk.HORIZONTAL
        )
        self.satisfaction_scale.pack(fill=tk.X)
        self.satisfaction_value = ttk.Label(satisfaction_frame, text="0.0")
        self.satisfaction_value.pack()
        self.satisfaction_scale.configure(
            command=lambda v: self.satisfaction_value.configure(text=f"{float(v):.2f}")
        )
        
        # Urgencia
        urgency_frame = ttk.LabelFrame(main_frame, text="Urgencia", padding=5)
        urgency_frame.pack(fill=tk.X, pady=5)
        
        self.urgency_scale = ttk.Scale(
            urgency_frame,
            from_=0, to=1,
            orient=tk.HORIZONTAL
        )
        self.urgency_scale.pack(fill=tk.X)
        self.urgency_value = ttk.Label(urgency_frame, text="0.0")
        self.urgency_value.pack()
        self.urgency_scale.configure(
            command=lambda v: self.urgency_value.configure(text=f"{float(v):.2f}")
        )
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Aceptar",
            command=self.accept
        ).pack(side=tk.RIGHT, padx=5)
        
    def accept(self):
        """Acepta los valores y cierra el diálogo"""
        try:
            # Asegurarse de que need_type es una instancia de NeedType
            need_type = NeedType[self.need_type] if isinstance(self.need_type, str) else self.need_type
            
            self.result = NeedImpact(
                need_type=need_type,
                intensity=self.intensity_scale.get(),
                satisfaction_level=self.satisfaction_scale.get(),
                urgency=self.urgency_scale.get()
            )
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear el impacto: {str(e)}")