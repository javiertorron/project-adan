import json
from pathlib import Path
from typing import Dict, List, Optional
from ...domain.entities.bot import Bot
from ...domain.repositories.bot_repository import BotRepository
from ...domain.entities.personality import Personality
import threading
import logging
from datetime import datetime

class JsonBotRepository(BotRepository):
    """
    Implementación de BotRepository que almacena bots en un archivo JSON.
    Incluye características de:
    - Auto-guardado
    - Backup automático
    - Manejo de concurrencia
    - Validación de datos
    - Logging
    """
    
    def __init__(self, file_path: str = "bots.json", backup_dir: str = "backups"):
        self.file_path = Path(file_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Lock para manejo de concurrencia
        self._lock = threading.Lock()
        
        # Caché en memoria
        self._bots: Dict[str, Bot] = {}
        
        # Configurar logging
        self._setup_logging()
        
        # Cargar datos iniciales
        self._load_data()
        
    def _setup_logging(self):
        """Configura el sistema de logging"""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.FileHandler('bot_repository.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            
    def _load_data(self):
        """Carga los datos del archivo JSON"""
        try:
            if self.file_path.exists():
                with self._lock:
                    data = json.loads(self.file_path.read_text(encoding='utf-8'))
                    self._validate_data(data)
                    self._bots = {
                        name: Bot.from_dict(bot_data)
                        for name, bot_data in data.items()
                    }
                self.logger.info(f"Datos cargados: {len(self._bots)} bots")
            else:
                self._bots = {}
                self._save_data()  # Crear archivo inicial
                self.logger.info("Archivo de datos creado")
        except Exception as e:
            self.logger.error(f"Error al cargar datos: {str(e)}")
            self._handle_data_corruption()
            
    def _save_data(self):
        """Guarda los datos en el archivo JSON"""
        try:
            with self._lock:
                data = {
                    name: bot.to_dict()
                    for name, bot in self._bots.items()
                }
                self.file_path.write_text(
                    json.dumps(data, indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
            self.logger.info(f"Datos guardados: {len(self._bots)} bots")
        except Exception as e:
            self.logger.error(f"Error al guardar datos: {str(e)}")
            raise
            
    def _create_backup(self):
        """Crea una copia de seguridad del archivo de datos"""
        try:
            if self.file_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.backup_dir / f"bots_backup_{timestamp}.json"
                with self._lock:
                    data = json.loads(self.file_path.read_text(encoding='utf-8'))
                    backup_path.write_text(
                        json.dumps(data, indent=2, ensure_ascii=False),
                        encoding='utf-8'
                    )
                self.logger.info(f"Backup creado: {backup_path}")
                
                # Mantener solo los últimos 5 backups
                self._cleanup_old_backups()
        except Exception as e:
            self.logger.error(f"Error al crear backup: {str(e)}")
            
    def _cleanup_old_backups(self):
        """Elimina backups antiguos manteniendo solo los más recientes"""
        try:
            backups = sorted(
                self.backup_dir.glob("bots_backup_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            for backup in backups[5:]:  # Mantener solo los últimos 5
                backup.unlink()
                self.logger.info(f"Backup antiguo eliminado: {backup}")
        except Exception as e:
            self.logger.error(f"Error al limpiar backups: {str(e)}")
            
    def _validate_data(self, data: dict):
        """Valida la estructura de los datos cargados"""
        if not isinstance(data, dict):
            raise ValueError("Los datos deben ser un diccionario")
            
        for name, bot_data in data.items():
            if not isinstance(name, str):
                raise ValueError(f"Nombre de bot inválido: {name}")
            if not isinstance(bot_data, dict):
                raise ValueError(f"Datos de bot inválidos para {name}")
            if 'personality' not in bot_data:
                raise ValueError(f"Faltan datos de personalidad para {name}")
                
    def _handle_data_corruption(self):
        """Maneja casos de corrupción de datos"""
        self.logger.warning("Intentando recuperar de backup...")
        
        # Buscar el backup más reciente
        backups = sorted(
            self.backup_dir.glob("bots_backup_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if backups:
            try:
                # Intentar cargar el backup más reciente
                data = json.loads(backups[0].read_text(encoding='utf-8'))
                self._validate_data(data)
                self._bots = {
                    name: Bot.from_dict(bot_data)
                    for name, bot_data in data.items()
                }
                self._save_data()  # Restaurar archivo principal
                self.logger.info(f"Recuperación exitosa desde {backups[0]}")
            except Exception as e:
                self.logger.error(f"Error en recuperación: {str(e)}")
                self._bots = {}  # Iniciar con datos limpios
        else:
            self.logger.warning("No hay backups disponibles")
            self._bots = {}
            
    # Implementación de la interfaz BotRepository
    
    def save(self, bot: Bot) -> bool:
        """Guarda un bot en el repositorio"""
        try:
            with self._lock:
                self._bots[bot.name] = bot
                self._save_data()
                self._create_backup()
            self.logger.info(f"Bot guardado: {bot.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error al guardar bot {bot.name}: {str(e)}")
            return False
            
    def delete(self, name: str) -> bool:
        """Elimina un bot del repositorio"""
        try:
            with self._lock:
                if name in self._bots:
                    del self._bots[name]
                    self._save_data()
                    self._create_backup()
                    self.logger.info(f"Bot eliminado: {name}")
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Error al eliminar bot {name}: {str(e)}")
            return False
            
    def get(self, name: str) -> Optional[Bot]:
        """Obtiene un bot por su nombre"""
        return self._bots.get(name)
        
    def get_all(self) -> List[Bot]:
        """Obtiene todos los bots"""
        return list(self._bots.values())
        
    def exists(self, name: str) -> bool:
        """Verifica si existe un bot con el nombre dado"""
        return name in self._bots
        
    def update(self, bot: Bot) -> bool:
        """Actualiza un bot existente"""
        try:
            with self._lock:
                if bot.name in self._bots:
                    self._bots[bot.name] = bot
                    self._save_data()
                    self._create_backup()
                    self.logger.info(f"Bot actualizado: {bot.name}")
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Error al actualizar bot {bot.name}: {str(e)}")
            return False
            
    def clear(self) -> bool:
        """Elimina todos los bots"""
        try:
            with self._lock:
                self._create_backup()  # Crear backup antes de limpiar
                self._bots.clear()
                self._save_data()
            self.logger.info("Repositorio limpiado")
            return True
        except Exception as e:
            self.logger.error(f"Error al limpiar repositorio: {str(e)}")
            return False

if __name__ == "__main__":
    # Código de prueba
    repo = JsonBotRepository()
    
    # Crear un bot de prueba
    personality = Personality()
    personality.randomize()
    test_bot = Bot("TestBot", personality)
    
    # Probar operaciones
    repo.save(test_bot)
    loaded_bot = repo.get("TestBot")
    if loaded_bot:
        print(f"Bot cargado: {loaded_bot.name}")
        print("Factores de personalidad:")
        for code, factor in loaded_bot.personality.factors.items():
            print(f"{code}: {factor.value:.2f}")
