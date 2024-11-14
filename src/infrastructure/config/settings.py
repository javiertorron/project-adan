from pathlib import Path
import json
from typing import Any, Dict, Optional
import logging
from dataclasses import dataclass, asdict
import os
import yaml
from threading import Lock
import sys

@dataclass
class UISettings:
    """Configuraciones de la interfaz de usuario"""
    window_width: int = 1024
    window_height: int = 768
    theme: str = "default"
    font_size: int = 10
    show_status_bar: bool = True
    show_tooltips: bool = True
    compact_mode: bool = False
    auto_save: bool = True

@dataclass
class StorageSettings:
    """Configuraciones de almacenamiento"""
    data_directory: str = "data"
    backup_directory: str = "backups"
    max_backups: int = 5
    auto_backup: bool = True
    backup_interval: int = 3600  # segundos
    compression_enabled: bool = False

@dataclass
class PersonalitySettings:
    """Configuraciones relacionadas con la personalidad"""
    default_randomization_range: float = 0.5
    trait_precision: int = 2
    default_neutral_zone: float = 0.25
    show_numerical_values: bool = True
    show_trait_descriptions: bool = True

@dataclass
class LogSettings:
    """Configuraciones de logging"""
    log_level: str = "INFO"
    log_file: str = "app.log"
    max_log_size: int = 1048576  # 1MB
    backup_count: int = 3
    console_logging: bool = True
    file_logging: bool = True

@dataclass
class AppSettings:
    """Configuración principal de la aplicación"""
    ui: UISettings = UISettings()
    storage: StorageSettings = StorageSettings()
    personality: PersonalitySettings = PersonalitySettings()
    log: LogSettings = LogSettings()

class Settings:
    """
    Gestor de configuraciones de la aplicación.
    Implementa el patrón Singleton para asegurar una única instancia.
    """
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Settings, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._settings = AppSettings()
        self._config_file = self._get_config_path()
        self._setup_logging()
        self.load()
        
    def _get_config_path(self) -> Path:
        """Determina la ruta del archivo de configuración según el sistema"""
        if sys.platform == "win32":
            config_dir = Path(os.getenv('APPDATA')) / "BotManager"
        else:
            config_dir = Path.home() / ".config" / "BotManager"
            
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "settings.yaml"
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            if self._settings.log.file_logging:
                file_handler = logging.FileHandler(self._settings.log.log_file)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
                
            if self._settings.log.console_logging:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
                
            self.logger.setLevel(getattr(logging, self._settings.log.log_level))
    
    def load(self) -> bool:
        """Carga las configuraciones desde el archivo"""
        try:
            if self._config_file.exists():
                with self._config_file.open('r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    
                if data:
                    # Cargar configuraciones por sección
                    if 'ui' in data:
                        self._settings.ui = UISettings(**data['ui'])
                    if 'storage' in data:
                        self._settings.storage = StorageSettings(**data['storage'])
                    if 'personality' in data:
                        self._settings.personality = PersonalitySettings(**data['personality'])
                    if 'log' in data:
                        self._settings.log = LogSettings(**data['log'])
                        
                self.logger.info("Configuraciones cargadas correctamente")
                return True
        except Exception as e:
            self.logger.error(f"Error al cargar configuraciones: {str(e)}")
            self._create_default_config()
        return False
    
    def save(self) -> bool:
        """Guarda las configuraciones actuales en el archivo"""
        try:
            # Convertir configuraciones a diccionario
            settings_dict = {
                'ui': asdict(self._settings.ui),
                'storage': asdict(self._settings.storage),
                'personality': asdict(self._settings.personality),
                'log': asdict(self._settings.log)
            }
            
            # Guardar en formato YAML
            with self._config_file.open('w', encoding='utf-8') as f:
                yaml.dump(settings_dict, f, default_flow_style=False)
                
            self.logger.info("Configuraciones guardadas correctamente")
            return True
        except Exception as e:
            self.logger.error(f"Error al guardar configuraciones: {str(e)}")
            return False
    
    def _create_default_config(self):
        """Crea un archivo de configuración con valores por defecto"""
        self._settings = AppSettings()
        self.save()
        self.logger.info("Archivo de configuración por defecto creado")
    
    def get(self) -> AppSettings:
        """Retorna las configuraciones actuales"""
        return self._settings
    
    def update_ui(self, **kwargs):
        """Actualiza configuraciones de UI"""
        for key, value in kwargs.items():
            if hasattr(self._settings.ui, key):
                setattr(self._settings.ui, key, value)
        self.save()
        
    def update_storage(self, **kwargs):
        """Actualiza configuraciones de almacenamiento"""
        for key, value in kwargs.items():
            if hasattr(self._settings.storage, key):
                setattr(self._settings.storage, key, value)
        self.save()
        
    def update_personality(self, **kwargs):
        """Actualiza configuraciones de personalidad"""
        for key, value in kwargs.items():
            if hasattr(self._settings.personality, key):
                setattr(self._settings.personality, key, value)
        self.save()
        
    def update_log(self, **kwargs):
        """Actualiza configuraciones de logging"""
        for key, value in kwargs.items():
            if hasattr(self._settings.log, key):
                setattr(self._settings.log, key, value)
        self.save()
        self._setup_logging()  # Reconfigurar logging con nuevos valores
    
    def reset_to_defaults(self):
        """Restablece todas las configuraciones a sus valores por defecto"""
        self._settings = AppSettings()
        self.save()
        self.logger.info("Configuraciones restablecidas a valores por defecto")

def get_settings() -> Settings:
    """Función de utilidad para obtener la instancia de Settings"""
    return Settings()

if __name__ == "__main__":
    # Código de prueba
    settings = get_settings()
    
    # Mostrar configuraciones actuales
    print("Configuraciones UI:")
    print(asdict(settings.get().ui))
    
    print("\nConfiguraciones de Almacenamiento:")
    print(asdict(settings.get().storage))
    
    print("\nConfiguraciones de Personalidad:")
    print(asdict(settings.get().personality))
    
    print("\nConfiguraciones de Logging:")
    print(asdict(settings.get().log))
    
    # Ejemplo de actualización
    settings.update_ui(theme="dark", font_size=12)
    
    # Verificar cambios
    print("\nConfiguraciones UI actualizadas:")
    print(asdict(settings.get().ui))

