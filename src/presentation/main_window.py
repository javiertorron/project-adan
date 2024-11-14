import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import sys
from pathlib import Path
from .bot_list_window import BotListWindow

class MainWindow:
    """
    Ventana principal de la aplicación.
    Gestiona:
    - Menú principal
    - Barra de estado
    - Contenido principal
    - Configuración global
    - Gestión de ventanas
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_styles()
        self.create_menu()
        self.create_main_content()
        self.create_status_bar()
        
    def setup_window(self):
        """Configura la ventana principal"""
        self.root.title("Bot Personality Manager")
        
        # Configurar tamaño y posición
        width = 1024
        height = 768
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Geometría de la ventana
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(800, 600)
        
        # Configurar el cierre de la ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configurar ícono si existe
        icon_path = Path(__file__).parent / "assets" / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(icon_path)
            
    def create_styles(self):
        """Configura los estilos de la aplicación"""
        style = ttk.Style()
        
        # Configurar estilos para las barras de progreso
        style.configure(
            "green.Horizontal.TProgressbar",
            background='green',
            troughcolor='#f0f0f0'
        )
        style.configure(
            "red.Horizontal.TProgressbar",
            background='red',
            troughcolor='#f0f0f0'
        )
        
        # Configurar otros estilos
        style.configure(
            "Status.TLabel",
            padding=2,
            background='#f0f0f0'
        )
        
        style.configure(
            "Header.TLabel",
            font=('TkDefaultFont', 12, 'bold')
        )
        
    def create_menu(self):
        """Crea la barra de menú principal"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo Bot", command=self.new_bot)
        file_menu.add_command(label="Importar...", command=self.import_bots)
        file_menu.add_command(label="Exportar...", command=self.export_bots)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.on_closing)
        
        # Menú Ver
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Ver", menu=view_menu)
        view_menu.add_command(label="Actualizar", command=self.refresh_view)
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Barra de Estado", command=self.toggle_status_bar)
        
        # Menú Herramientas
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Configuración...", command=self.show_settings)
        tools_menu.add_command(label="Estadísticas", command=self.show_statistics)
        
        # Menú Ayuda
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Manual de Usuario", command=self.show_manual)
        help_menu.add_command(label="Acerca de...", command=self.show_about)
        
    def create_main_content(self):
        """Crea el contenido principal de la aplicación"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            header_frame,
            text="Gestión de Bots",
            style="Header.TLabel"
        ).pack(side=tk.LEFT)
        
        # Contenido
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear y mostrar la lista de bots
        self.bot_list = BotListWindow(self.content_frame)
        self.bot_list.pack(fill=tk.BOTH, expand=True)
        
    def create_status_bar(self):
        """Crea la barra de estado"""
        self.status_bar = ttk.Label(
            self.root,
            text="Listo",
            style="Status.TLabel",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def update_status(self, message: str):
        """Actualiza el mensaje de la barra de estado"""
        self.status_bar['text'] = message
        
    def new_bot(self):
        """Crea un nuevo bot"""
        self.bot_list.create_bot()
        
    def import_bots(self):
        """Importa bots desde un archivo"""
        # TODO: Implementar importación
        self.update_status("Importación no implementada")
        
    def export_bots(self):
        """Exporta bots a un archivo"""
        # TODO: Implementar exportación
        self.update_status("Exportación no implementada")
        
    def refresh_view(self):
        """Actualiza la vista principal"""
        self.bot_list.refresh_bot_list()
        self.update_status("Vista actualizada")
        
    def toggle_status_bar(self):
        """Muestra/oculta la barra de estado"""
        if self.status_bar.winfo_viewable():
            self.status_bar.pack_forget()
        else:
            self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
            
    def show_settings(self):
        """Muestra la ventana de configuración"""
        # TODO: Implementar ventana de configuración
        self.update_status("Configuración no implementada")
        
    def show_statistics(self):
        """Muestra la ventana de estadísticas"""
        # TODO: Implementar ventana de estadísticas
        self.update_status("Estadísticas no implementadas")
        
    def show_manual(self):
        """Muestra el manual de usuario"""
        # TODO: Implementar visualización del manual
        self.update_status("Manual no implementado")
        
    def show_about(self):
        """Muestra la ventana Acerca de"""
        about_window = tk.Toplevel(self.root)
        about_window.title("Acerca de Bot Personality Manager")
        about_window.geometry("400x300")
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Centrar ventana
        about_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Contenido
        ttk.Label(
            about_window,
            text="Bot Personality Manager",
            style="Header.TLabel"
        ).pack(pady=20)
        
        ttk.Label(
            about_window,
            text="Versión 1.0.0",
            justify=tk.CENTER
        ).pack()
        
        ttk.Label(
            about_window,
            text="Una aplicación para gestionar personalidades de bots\n"
                 "basada en el modelo de los 16 factores de Cattell.\n\n"
                 "Author: Javier Torron Diaz\n"
                 "Proyecto: A living world\n"
                 "Licencia: Prohibida su copia o reproduccion",
            justify=tk.CENTER,
            wraplength=350
        ).pack(pady=20)
        
        ttk.Button(
            about_window,
            text="Cerrar",
            command=about_window.destroy
        ).pack(pady=20)
        
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if tk.messagebox.askokcancel("Salir", "¿Deseas salir de la aplicación?"):
            # Guardar configuración si es necesario
            self.root.quit()
            
    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()
        
if __name__ == "__main__":
    app = MainWindow()
    app.run()
