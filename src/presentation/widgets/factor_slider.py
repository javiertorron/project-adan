# src/presentation/widgets/factor_slider.py

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

class FactorSlider(ttk.Frame):
    def __init__(self, 
                 master,
                 command: Optional[Callable[[float], None]] = None,
                 **kwargs):
        super().__init__(master)
        self.command = command
        self.value = tk.DoubleVar(value=0.0)
        self.setup_ui()
        
    def setup_ui(self):
        self.slider = ttk.Scale(
            self,
            from_=-1.0,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.value
        )
        self.slider.pack(fill=tk.X, expand=True)
        
        if self.command:
            self.value.trace_add('write', self._on_value_change)
            
    def _on_value_change(self, *args):
        if self.command:
            self.command(self.value.get())
            
    def get(self) -> float:
        return self.value.get()
        
    def set(self, value: float):
        self.value.set(value)