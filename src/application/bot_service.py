from typing import List, Optional, Dict, Tuple
from ..domain.entities.bot import Bot
from ..domain.entities.personality import Personality
from ..domain.repositories.bot_repository import BotRepository
from ..infrastructure.config.settings import get_settings
import logging
from datetime import datetime
from pathlib import Path
import json
import csv

class BotService:
    """
    Servicio que gestiona las operaciones relacionadas con los bots.
    Implementa la lógica de negocio y coordina las operaciones entre la UI y el repositorio.
    """
    
    def __init__(self, repository: BotRepository):
        self.repository = repository
        self.settings = get_settings()
        self._setup_logging()
        
    def _setup_logging(self):
        """Configura el logging para el servicio"""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler = logging.FileHandler('bot_service.log')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def create_bot(self, name: str, personality: Optional[Personality] = None) -> Tuple[bool, str]:
        """
        Crea un nuevo bot.
        Retorna una tupla (éxito, mensaje).
        """
        try:
            # Validar nombre
            if not self._validate_bot_name(name):
                return False, "Nombre de bot inválido"
            
            # Verificar si ya existe
            if self.repository.exists(name):
                return False, "Ya existe un bot con ese nombre"
            
            # Crear bot
            bot = Bot(
                name=name,
                personality=personality if personality else Personality()
            )
            
            # Guardar
            if self.repository.save(bot):
                self.logger.info(f"Bot creado exitosamente: {name}")
                return True, "Bot creado exitosamente"
            else:
                return False, "Error al guardar el bot"
                
        except Exception as e:
            self.logger.error(f"Error al crear bot: {str(e)}")
            return False, f"Error al crear bot: {str(e)}"
            
    def update_bot(self, bot: Bot) -> Tuple[bool, str]:
        """
        Actualiza un bot existente.
        Retorna una tupla (éxito, mensaje).
        """
        try:
            if not self.repository.exists(bot.name):
                return False, "Bot no encontrado"
                
            if self.repository.update(bot):
                self.logger.info(f"Bot actualizado: {bot.name}")
                return True, "Bot actualizado exitosamente"
            else:
                return False, "Error al actualizar el bot"
                
        except Exception as e:
            self.logger.error(f"Error al actualizar bot: {str(e)}")
            return False, f"Error al actualizar bot: {str(e)}"
            
    def delete_bot(self, name: str) -> Tuple[bool, str]:
        """
        Elimina un bot.
        Retorna una tupla (éxito, mensaje).
        """
        try:
            if not self.repository.exists(name):
                return False, "Bot no encontrado"
                
            if self.repository.delete(name):
                self.logger.info(f"Bot eliminado: {name}")
                return True, "Bot eliminado exitosamente"
            else:
                return False, "Error al eliminar el bot"
                
        except Exception as e:
            self.logger.error(f"Error al eliminar bot: {str(e)}")
            return False, f"Error al eliminar bot: {str(e)}"
            
    def get_bot(self, name: str) -> Optional[Bot]:
        """Obtiene un bot por su nombre"""
        return self.repository.get(name)
        
    def get_all_bots(self) -> List[Bot]:
        """Obtiene todos los bots"""
        return self.repository.get_all()
        
    def get_bot_statistics(self, bot: Bot) -> Dict:
        """Calcula estadísticas para un bot específico"""
        stats = {
            'name': bot.name,
            'creation_date': self._get_bot_creation_date(bot),
            'personality_stats': self._calculate_personality_stats(bot.personality),
            'dominant_traits': self._get_dominant_traits(bot.personality),
            'trait_distribution': self._calculate_trait_distribution(bot.personality)
        }
        return stats
        
    def get_global_statistics(self) -> Dict:
        """Calcula estadísticas globales para todos los bots"""
        bots = self.get_all_bots()
        return {
            'total_bots': len(bots),
            'average_traits': self._calculate_average_traits(bots),
            'trait_correlations': self._calculate_trait_correlations(bots),
            'personality_clusters': self._identify_personality_clusters(bots)
        }
        
    def export_bots(self, format: str, file_path: str) -> Tuple[bool, str]:
        """
        Exporta los bots en el formato especificado.
        Soporta JSON y CSV.
        """
        try:
            bots = self.get_all_bots()
            
            if format.lower() == 'json':
                return self._export_to_json(bots, file_path)
            elif format.lower() == 'csv':
                return self._export_to_csv(bots, file_path)
            else:
                return False, f"Formato no soportado: {format}"
                
        except Exception as e:
            self.logger.error(f"Error al exportar bots: {str(e)}")
            return False, f"Error al exportar: {str(e)}"
            
    def import_bots(self, format: str, file_path: str) -> Tuple[bool, str]:
        """
        Importa bots desde un archivo.
        Soporta JSON y CSV.
        """
        try:
            if format.lower() == 'json':
                return self._import_from_json(file_path)
            elif format.lower() == 'csv':
                return self._import_from_csv(file_path)
            else:
                return False, f"Formato no soportado: {format}"
                
        except Exception as e:
            self.logger.error(f"Error al importar bots: {str(e)}")
            return False, f"Error al importar: {str(e)}"
            
    def _validate_bot_name(self, name: str) -> bool:
        """Valida el nombre del bot"""
        if not name or len(name) < 3:
            return False
        # Añadir más validaciones según necesidades
        return True
        
    def _get_bot_creation_date(self, bot: Bot) -> str:
        """Obtiene la fecha de creación del bot"""
        # Implementar según el sistema de metadatos
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def _calculate_personality_stats(self, personality: Personality) -> Dict:
        """Calcula estadísticas de personalidad"""
        values = [f.value for f in personality.factors.values()]
        return {
            'mean': sum(values) / len(values),
            'max': max(values),
            'min': min(values),
            'extreme_traits_count': len([v for v in values if abs(v) > 0.7])
        }
        
    def _get_dominant_traits(self, personality: Personality, threshold: float = 0.7) -> List[Tuple[str, float]]:
        """Identifica los rasgos dominantes de la personalidad"""
        dominant = []
        for code, factor in personality.factors.items():
            if abs(factor.value) > threshold:
                dominant.append((code, factor.value))
        return sorted(dominant, key=lambda x: abs(x[1]), reverse=True)
        
    def _calculate_trait_distribution(self, personality: Personality) -> Dict:
        """Calcula la distribución de rasgos"""
        distribution = {
            'very_low': 0,  # < -0.7
            'low': 0,      # -0.7 to -0.3
            'neutral': 0,  # -0.3 to 0.3
            'high': 0,     # 0.3 to 0.7
            'very_high': 0 # > 0.7
        }
        
        for factor in personality.factors.values():
            value = factor.value
            if value < -0.7:
                distribution['very_low'] += 1
            elif value < -0.3:
                distribution['low'] += 1
            elif value < 0.3:
                distribution['neutral'] += 1
            elif value < 0.7:
                distribution['high'] += 1
            else:
                distribution['very_high'] += 1
                
        return distribution
        
    def _calculate_average_traits(self, bots: List[Bot]) -> Dict:
        """Calcula el promedio de cada rasgo entre todos los bots"""
        trait_sums = {code: 0.0 for code in Personality.FACTORS.keys()}
        for bot in bots:
            for code, factor in bot.personality.factors.items():
                trait_sums[code] += factor.value
                
        return {code: value/len(bots) for code, value in trait_sums.items()}
        
    def _calculate_trait_correlations(self, bots: List[Bot]) -> List[Tuple[str, str, float]]:
        """Calcula correlaciones entre rasgos"""
        # Implementar cálculo de correlaciones según necesidades
        return []
        
    def _identify_personality_clusters(self, bots: List[Bot]) -> List[Dict]:
        """Identifica grupos de personalidades similares"""
        # Implementar clustering según necesidades
        return []
        
    def _export_to_json(self, bots: List[Bot], file_path: str) -> Tuple[bool, str]:
        """Exporta bots a formato JSON"""
        try:
            data = {bot.name: bot.to_dict() for bot in bots}
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True, "Exportación JSON exitosa"
        except Exception as e:
            return False, f"Error en exportación JSON: {str(e)}"
            
    def _export_to_csv(self, bots: List[Bot], file_path: str) -> Tuple[bool, str]:
        """Exporta bots a formato CSV"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Escribir encabezados
                headers = ['name'] + list(Personality.FACTORS.keys())
                writer.writerow(headers)
                
                # Escribir datos
                for bot in bots:
                    row = [bot.name] + [
                        bot.personality.factors[code].value 
                        for code in Personality.FACTORS.keys()
                    ]
                    writer.writerow(row)
                    
            return True, "Exportación CSV exitosa"
        except Exception as e:
            return False, f"Error en exportación CSV: {str(e)}"
            
    def _import_from_json(self, file_path: str) -> Tuple[bool, str]:
        """Importa bots desde formato JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for name, bot_data in data.items():
                bot = Bot.from_dict({'name': name, **bot_data})
                self.repository.save(bot)
                
            return True, f"Importados {len(data)} bots desde JSON"
        except Exception as e:
            return False, f"Error en importación JSON: {str(e)}"
            
    def _import_from_csv(self, file_path: str) -> Tuple[bool, str]:
        """Importa bots desde formato CSV"""
        try:
            imported = 0
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)  # Leer encabezados
                
                for row in reader:
                    name = row[0]
                    personality = Personality()
                    
                    # Asignar valores de personalidad
                    for i, code in enumerate(Personality.FACTORS.keys(), 1):
                        if i < len(row):
                            personality.factors[code].value = float(row[i])
                            
                    bot = Bot(name, personality)
                    self.repository.save(bot)
                    imported += 1
                    
            return True, f"Importados {imported} bots desde CSV"
        except Exception as e:
            return False, f"Error en importación CSV: {str(e)}"

if __name__ == "__main__":
    # Código de prueba
    from ..infrastructure.persistence.json_bot_repository import JsonBotRepository
    
    # Crear instancias
    repo = JsonBotRepository()
    service = BotService(repo)
    
    # Probar creación
    success, message = service.create_bot("TestBot")
    print(f"Creación de bot: {message}")
    
    # Probar estadísticas
    if bot := service.get_bot("TestBot"):
        stats = service.get_bot_statistics(bot)
        print("\nEstadísticas del bot:")
        print(json.dumps(stats, indent=2))
        
    # Probar exportación
    success, message = service.export_bots('json', 'bots_export.json')
    print(f"\nExportación: {message}")
