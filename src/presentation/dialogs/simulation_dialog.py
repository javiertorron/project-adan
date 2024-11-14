import tkinter as tk
from tkinter import ttk
from typing import Callable

from ...domain.models.need_type import NeedType
from ...domain.entities.bot import Bot
from enum import Enum, auto
import json
import threading
import time
from datetime import datetime, timedelta

class SimulationDialog(tk.Toplevel):
    """
    Ventana principal de simulación.
    Permite:
    - Configuración y envío de estímulos
    - (Futuro) Monitoreo de estado del bot
    - (Futuro) Visualización de reacciones
    - (Futuro) Gestión de eventos
    - (Futuro) Análisis de comportamiento
    """
    
    def __init__(self, parent: tk.Widget, bot: Bot):
        super().__init__(parent)
        self.bot = bot
        self.simulation_time = 0  # Tiempo en segundos
        self.is_running = False
        self.simulation_thread = None
        self.update_interval = 1.0  # Actualización cada segundo
        self.is_destroyed = False
        self.time_scale = 60
        
        self.title(f"Simulador - {bot.name}")
        self.setup_window()
        self.create_widgets()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Iniciar simulación
        self.start_simulation()
        
    def setup_window(self):
        """Configura la ventana"""
        # Hacer la ventana modal
        self.transient(self.master)
        self.grab_set()
        
        # Configurar tamaño y posición
        width = 1024
        height = 768
        
        # Obtener posición de la ventana padre
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        # Calcular posición centrada
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(800, 600)
        
    def create_widgets(self):
        """Crea los widgets de la interfaz"""
        self.create_toolbar()
        self.create_main_content()
        self.create_status_bar()
        
    def create_toolbar(self):
        """Crea la barra de herramientas"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Botones principales
        ttk.Button(
            toolbar,
            text="Nuevo Estímulo",
            command=self.new_stimulus
        ).pack(side=tk.LEFT, padx=2)
        
        # Añadir indicador de tiempo
        self.time_label = ttk.Label(toolbar, text="Tiempo: 00:00:00")
        self.time_label.pack(side=tk.LEFT, padx=20)
        
        self.pause_button = ttk.Button(
            toolbar,
            text="Pausar",
            command=self.toggle_simulation
        )
        self.pause_button.pack(side=tk.LEFT, padx=2)
        
    def create_main_content(self):
        """Crea el contenido principal"""
        # Panel principal dividido
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel izquierdo: Controles y Estado
        left_frame = ttk.Frame(self.paned)
        self.paned.add(left_frame, weight=1)
        
        # Información del Bot
        info_frame = ttk.LabelFrame(left_frame, text="Información del Bot")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text=f"Nombre: {self.bot.name}").pack(anchor=tk.W, padx=5, pady=2)
        # Añadir más información relevante del bot
        
        # Estado Actual
        state_frame = ttk.LabelFrame(left_frame, text="Estado Actual")
        state_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_state_indicators(state_frame)
        
        # Panel derecho: Visualización y Registro
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame, weight=2)
        
        # Notebook para diferentes vistas
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de Eventos
        events_frame = ttk.Frame(self.notebook)
        self.notebook.add(events_frame, text="Eventos")
        self.create_events_view(events_frame)
        
        # Pestaña de Gráficos
        graphs_frame = ttk.Frame(self.notebook)
        self.notebook.add(graphs_frame, text="Gráficos")
        self.create_graphs_view(graphs_frame)
        
    def create_state_indicators(self, parent):
        """Crea los indicadores de estado del bot"""
        # Estado Emocional
        ttk.Label(parent, text="Estado Emocional:").pack(anchor=tk.W, padx=5, pady=2)
        self.emotional_state = ttk.Label(parent, text="Neutral")
        self.emotional_state.pack(anchor=tk.W, padx=20, pady=2)
        
        # Nivel de Estrés
        ttk.Label(parent, text="Nivel de Estrés:").pack(anchor=tk.W, padx=5, pady=2)
        self.stress_bar = ttk.Progressbar(parent, length=200, mode='determinate')
        self.stress_bar.pack(anchor=tk.W, padx=20, pady=2)
        
        # Necesidades Activas
        ttk.Label(parent, text="Necesidades Activas:").pack(anchor=tk.W, padx=5, pady=2)
        self.needs_list = tk.Listbox(parent, height=4)
        self.needs_list.pack(fill=tk.X, padx=20, pady=2)
        
    def create_events_view(self, parent):
        """Crea la vista de eventos"""
        # Crear Treeview para eventos, añadimos la columna 'reaction'
        columns = ('timestamp', 'type', 'description', 'impact', 'reaction')
        self.events_tree = ttk.Treeview(
            parent,
            columns=columns,
            show='headings',
            selectmode='browse'
        )
        
        # Configurar columnas
        self.events_tree.heading('timestamp', text='Tiempo')
        self.events_tree.heading('type', text='Tipo')
        self.events_tree.heading('description', text='Descripción')
        self.events_tree.heading('impact', text='Impacto')
        self.events_tree.heading('reaction', text='Reacción')
        
        self.events_tree.column('timestamp', width=100)
        self.events_tree.column('type', width=100)
        self.events_tree.column('description', width=300)
        self.events_tree.column('impact', width=100)
        self.events_tree.column('reaction', width=100)
        
        # Configurar etiquetas para colores
        self.events_tree.tag_configure('reaction', foreground='green')
        self.events_tree.tag_configure('ignored', foreground='red')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.events_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_graphs_view(self, parent):
        """Crea la vista de gráficos"""
        # Por implementar: Gráficos de estado emocional, necesidades, etc.
        ttk.Label(
            parent,
            text="Visualización de gráficos en desarrollo..."
        ).pack(expand=True)
        
    def create_status_bar(self):
        """Crea la barra de estado"""
        self.status_bar = ttk.Label(
            self,
            text="Listo",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
        
    def new_stimulus(self):
        """Abre el diálogo de nuevo estímulo"""
        from .stimulus_dialog import StimulusDialog
        def on_stimulus_created(event_type, description, impact, should_react):
            self.add_event(event_type, description, impact, should_react)
            
        dialog = StimulusDialog(self, self.bot, on_stimulus_created)
    
    def _update_state_indicators(self, stimulus_data):
        """Actualiza los indicadores de estado basados en el estímulo"""
        # Actualizar estado emocional
        impact = stimulus_data['emotional_impact']
        if impact.impact_intensity > 0.7:
            self.emotional_state.config(text="Estresado")
        elif impact.impact_intensity > 0.3:
            self.emotional_state.config(text="Alerta")
        elif impact.impact_intensity < -0.3:
            self.emotional_state.config(text="Calma")
        else:
            self.emotional_state.config(text="Neutral")
            
        # Actualizar barra de estrés
        stress_level = min(100, max(0, (1 - impact.current_stability) * 100))
        self.stress_bar['value'] = stress_level
        
        # Actualizar lista de necesidades
        self.needs_list.delete(0, tk.END)
        for need_impact in stimulus_data['need_impacts']:
            if need_impact.urgency > 0.5:  # Solo mostrar necesidades urgentes
                self.needs_list.insert(
                    tk.END,
                    f"{need_impact.need_type.name}: {need_impact.intensity:.2f}"
                )
        
    def pause_simulation(self):
        """Pausa la simulación"""
        self.update_status("Simulación pausada")
        
    def resume_simulation(self):
        """Reanuda la simulación"""
        self.update_status("Simulación en curso")
        
    def show_bot_state(self):
        """Muestra una ventana con el estado detallado del bot"""
        # Por implementar
        self.update_status("Visualización de estado en desarrollo")
        
    def show_history(self):
        """Muestra el historial de la simulación"""
        # Por implementar
        self.update_status("Visualización de historial en desarrollo")
        
    def update_status(self, message: str):
        """Actualiza el mensaje de la barra de estado"""
        self.status_bar['text'] = message
        
    def add_event(self, event_type: str, description: str, impact: str, should_react: bool):
        """Añade un evento al registro"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        reaction_text = "Reacción" if should_react else "Ignorado"
        tag = 'reaction' if should_react else 'ignored'
        
        item = self.events_tree.insert(
            '',
            'end',
            values=(timestamp, event_type, description, impact, reaction_text),
            tags=(tag,)
        )
        
        # Auto-scroll al último evento
        self.events_tree.see(item)

    def update_ui(self):
        """Actualiza la interfaz de usuario con el estado actual"""
        if self.is_destroyed:  # No actualizar si la ventana está destruida
            return
            
        try:
            if not self.is_running:
                return
                
            # Actualizar tiempo
            sim_time = self.simulation_time * self.time_scale
            time_str = str(timedelta(seconds=int(sim_time)))
            self.time_label.configure(text=f"Tiempo simulado: {time_str}")
            
            # Actualizar estado emocional
            self.emotional_state.configure(
                text=self.bot.emotional_manager.current_state.name
            )
            
            # Actualizar barra de estrés
            stress_level = self.bot.emotional_manager.stress_level * 100
            self.stress_bar['value'] = stress_level
            
            # Actualizar barras de necesidades
            for need_type, need_bar in self.need_bars.items():
                value = self.bot.needs_manager.needs[need_type] * 100
                need_bar['bar']['value'] = value
                need_bar['label'].configure(text=f"{value:.1f}%")
                
                # Cambiar color según nivel
                if value < 30:
                    need_bar['bar'].configure(style='Critical.Horizontal.TProgressbar')
                elif value < 60:
                    need_bar['bar'].configure(style='Warning.Horizontal.TProgressbar')
                else:
                    need_bar['bar'].configure(style='Normal.Horizontal.TProgressbar')
        except tk.TclError:
            self.is_destroyed = True  # Marcar la ventana como destruida si hay un error

    def update_bot_state(self, delta_time: float):
        """Actualiza el estado del bot basado en el tiempo transcurrido"""
        # Actualizar necesidades
        self.bot.needs_manager.update_needs(delta_time)
        
        # Recuperación natural del estrés (si no hay estímulos negativos)
        self.bot.emotional_manager.update_emotional_state(-0.01 * delta_time)

    def create_state_indicators(self, parent):
        """Crea los indicadores de estado del bot"""
        # Estado Emocional
        ttk.Label(parent, text="Estado Emocional:").pack(anchor=tk.W, padx=5, pady=2)
        self.emotional_state = ttk.Label(parent, text="Neutral")
        self.emotional_state.pack(anchor=tk.W, padx=20, pady=2)
        
        # Nivel de Estrés
        ttk.Label(parent, text="Nivel de Estrés:").pack(anchor=tk.W, padx=5, pady=2)
        self.stress_bar = ttk.Progressbar(parent, length=200, mode='determinate')
        self.stress_bar.pack(anchor=tk.W, padx=20, pady=2)
        
        # Frame para necesidades
        needs_frame = ttk.LabelFrame(parent, text="Necesidades")
        needs_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Crear barras de progreso para cada necesidad
        self.need_bars = {}
        for need_type in NeedType:
            frame = ttk.Frame(needs_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=f"{need_type.name}:").pack(side=tk.LEFT, padx=5)
            progress = ttk.Progressbar(frame, length=150, mode='determinate')
            progress.pack(side=tk.LEFT, padx=5)
            value_label = ttk.Label(frame, text="100%")
            value_label.pack(side=tk.LEFT, padx=5)
            
            self.need_bars[need_type] = {
                'bar': progress,
                'label': value_label
            }

    def start_simulation(self):
        """Inicia la simulación"""
        self.is_running = True
        self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.simulation_thread.start()

    def toggle_simulation(self):
        """Alterna entre pausar y reanudar la simulación"""
        self.is_running = not self.is_running
        if self.is_running:
            self.pause_button.configure(text="Pausar")
            self.start_simulation()
        else:
            self.pause_button.configure(text="Reanudar")

    def _simulation_loop(self):
        """Bucle principal de la simulación"""
        last_update = time.time()
        
        while self.is_running and not self.is_destroyed:  # Comprobar si la ventana está destruida
            current_time = time.time()
            delta_time = current_time - last_update
            last_update = current_time
            
            # Actualizar tiempo de simulación
            self.simulation_time += delta_time
            
            # Actualizar estado del bot
            self.update_bot_state(delta_time)
            
            # Actualizar UI solo si la ventana sigue existiendo
            if not self.is_destroyed:
                try:
                    self.after(int(self.update_interval * 1000), self.update_ui)
                except tk.TclError:
                    break  # Salir si la ventana fue destruida
            
            # Esperar hasta la siguiente actualización
            time.sleep(self.update_interval)
    
    def on_closing(self):
        """Maneja el cierre de la ventana"""
        self.is_running = False
        self.is_destroyed = True  # Marcar la ventana como destruida
        
        # Esperar a que el thread de simulación termine
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=1.0)
            
        # Destruir la ventana
        self.destroy()

    def destroy(self):
        """Sobrescribir el método destroy para asegurar la limpieza correcta"""
        self.is_running = False
        self.is_destroyed = True
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=1.0)
        super().destroy()