import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import re

class NumericEntry(ttk.Frame):
    """
    Widget de entrada numérica especializado para factores de personalidad.
    Características:
    - Validación en tiempo real
    - Formateo automático
    - Soporte para teclas arriba/abajo
    - Límites configurables
    - Incremento/decremento configurable
    - Tooltip con rango válido
    """
    
    def __init__(
        self,
        master,
        min_value: float = -1.0,
        max_value: float = 1.0,
        increment: float = 0.1,
        initial_value: float = 0.0,
        command: Optional[Callable[[float], None]] = None,
        width: int = 8,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.min_value = min_value
        self.max_value = max_value
        self.increment = increment
        self.command = command
        self._current_value = initial_value
        
        self._create_widgets(width)
        self._setup_validation()
        self._create_tooltip()
        self.set_value(initial_value)
        
    def _create_widgets(self, width: int):
        """Crea los widgets del control numérico"""
        # Frame para el entry y los botones
        self.entry_frame = ttk.Frame(self)
        self.entry_frame.pack(fill=tk.X, expand=True)
        
        # Entry principal
        self.entry = ttk.Entry(
            self.entry_frame,
            width=width,
            justify=tk.RIGHT
        )
        self.entry.pack(side=tk.LEFT, padx=(0, 2))
        
        # Frame para botones arriba/abajo
        self.button_frame = ttk.Frame(self.entry_frame)
        self.button_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Botones
        self.up_button = ttk.Button(
            self.button_frame,
            text="▲",
            width=2,
            command=self._increment
        )
        self.up_button.pack(fill=tk.X)
        
        self.down_button = ttk.Button(
            self.button_frame,
            text="▼",
            width=2,
            command=self._decrement
        )
        self.down_button.pack(fill=tk.X)
        
        # Configurar eventos
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.entry.bind('<Return>', self._on_return)
        self.entry.bind('<Up>', lambda e: self._increment())
        self.entry.bind('<Down>', lambda e: self._decrement())
        self.entry.bind('<MouseWheel>', self._on_mousewheel)
        
    def _setup_validation(self):
        """Configura la validación de entrada"""
        self.validate_cmd = self.register(self._validate_input)
        self.format_cmd = self.register(self._format_input)
        
        self.entry.configure(
            validate='key',
            validatecommand=(self.validate_cmd, '%P', '%s', '%d'),
            invalidcommand=(self.format_cmd, '%P', '%s')
        )
        
    def _create_tooltip(self):
        """Crea el tooltip con información del rango válido"""
        self.tooltip = None
        self.entry.bind('<Enter>', self._show_tooltip)
        self.entry.bind('<Leave>', self._hide_tooltip)
        
    def _show_tooltip(self, event=None):
        """Muestra el tooltip"""
        x, y, _, height = self.entry.bbox("insert")
        x = x + self.entry.winfo_rootx() + 25
        y = y + height + self.entry.winfo_rooty() + 20
        
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(
            self.tooltip,
            text=f"Rango válido: [{self.min_value}, {self.max_value}]",
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1
        )
        label.pack()
        
    def _hide_tooltip(self, event=None):
        """Oculta el tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
            
    def _validate_input(self, new_value: str, old_value: str, action: str) -> bool:
        """Valida la entrada mientras el usuario escribe"""
        # Permitir campo vacío o solo signo menos
        if new_value == "" or new_value == "-":
            return True
            
        # Validar formato numérico
        try:
            if action == '1':  # Inserción
                # Permitir solo un punto decimal
                if new_value.count('.') > 1:
                    return False
                    
                # Verificar formato válido
                pattern = r'^-?\d*\.?\d*$'
                if not re.match(pattern, new_value):
                    return False
                    
                # Si hay un valor numérico completo, verificar rango
                if re.match(r'^-?\d+\.?\d*$', new_value):
                    value = float(new_value)
                    if value < self.min_value or value > self.max_value:
                        return False
                        
            return True
            
        except ValueError:
            return False
            
    def _format_input(self, new_value: str, old_value: str) -> bool:
        """Formatea el valor cuando la validación falla"""
        self.bell()
        return True
        
    def _on_focus_out(self, event=None):
        """Maneja la pérdida de foco"""
        self._format_value()
        
    def _on_return(self, event=None):
        """Maneja la pulsación de Enter"""
        self._format_value()
        
    def _format_value(self):
        """Formatea el valor actual"""
        try:
            value = float(self.entry.get())
            self.set_value(value)
        except ValueError:
            self.set_value(self._current_value)
            
    def _increment(self, event=None):
        """Incrementa el valor"""
        try:
            current = float(self.entry.get())
        except ValueError:
            current = self._current_value
            
        new_value = min(self.max_value, current + self.increment)
        self.set_value(new_value)
        
    def _decrement(self, event=None):
        """Decrementa el valor"""
        try:
            current = float(self.entry.get())
        except ValueError:
            current = self._current_value
            
        new_value = max(self.min_value, current - self.increment)
        self.set_value(new_value)
        
    def _on_mousewheel(self, event):
        """Maneja el scroll del ratón"""
        if event.delta > 0:
            self._increment()
        else:
            self._decrement()
            
    def set_value(self, value: float):
        """Establece el valor del control"""
        value = max(self.min_value, min(self.max_value, value))
        self._current_value = value
        
        # Actualizar entry
        self.entry.delete(0, tk.END)
        self.entry.insert(0, f"{value:.2f}")
        
        # Notificar cambio
        if self.command:
            self.command(value)
            
    def get_value(self) -> float:
        """Obtiene el valor actual"""
        try:
            return float(self.entry.get())
        except ValueError:
            return self._current_value
            
    def configure(self, **kwargs):
        """Configura el widget"""
        if 'command' in kwargs:
            self.command = kwargs.pop('command')
        if 'min_value' in kwargs:
            self.min_value = kwargs.pop('min_value')
        if 'max_value' in kwargs:
            self.max_value = kwargs.pop('max_value')
        if 'increment' in kwargs:
            self.increment = kwargs.pop('increment')
            
        super().configure(**kwargs)
        
    def config(self, **kwargs):
        """Alias para configure"""
        self.configure(**kwargs)

if __name__ == "__main__":
    # Código de prueba
    root = tk.Tk()
    root.title("Numeric Entry Demo")
    
    def on_value_change(value):
        print(f"Valor cambiado a: {value}")
    
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Crear varios ejemplos
    ttk.Label(frame, text="Valor estándar (-1 a 1):").pack()
    entry1 = NumericEntry(frame, command=on_value_change)
    entry1.pack(pady=5)
    
    ttk.Label(frame, text="Valor personalizado (0 a 100):").pack()
    entry2 = NumericEntry(
        frame,
        min_value=0,
        max_value=100,
        increment=5,
        initial_value=50,
        command=on_value_change
    )
    entry2.pack(pady=5)
    
    ttk.Label(frame, text="Valor de precisión (0 a 1):").pack()
    entry3 = NumericEntry(
        frame,
        min_value=0,
        max_value=1,
        increment=0.01,
        initial_value=0.5,
        command=on_value_change
    )
    entry3.pack(pady=5)
    
    root.mainloop()