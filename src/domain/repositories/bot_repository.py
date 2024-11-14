from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from ..entities.bot import Bot
from datetime import datetime

class BotRepository(ABC):
    """
    Interfaz abstracta que define las operaciones básicas para un repositorio de bots.
    Sigue los principios SOLID y permite diferentes implementaciones (JSON, SQL, etc.).
    """

    @abstractmethod
    def save(self, bot: Bot) -> bool:
        """
        Guarda un bot en el repositorio.
        
        Args:
            bot: Bot a guardar
            
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        pass

    @abstractmethod
    def update(self, bot: Bot) -> bool:
        """
        Actualiza un bot existente.
        
        Args:
            bot: Bot con los datos actualizados
            
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        pass

    @abstractmethod
    def delete(self, name: str) -> bool:
        """
        Elimina un bot del repositorio.
        
        Args:
            name: Nombre del bot a eliminar
            
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        pass

    @abstractmethod
    def get(self, name: str) -> Optional[Bot]:
        """
        Obtiene un bot por su nombre.
        
        Args:
            name: Nombre del bot a buscar
            
        Returns:
            Optional[Bot]: El bot si existe, None en caso contrario
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Bot]:
        """
        Obtiene todos los bots en el repositorio.
        
        Returns:
            List[Bot]: Lista de todos los bots
        """
        pass

    @abstractmethod
    def exists(self, name: str) -> bool:
        """
        Verifica si existe un bot con el nombre dado.
        
        Args:
            name: Nombre del bot a verificar
            
        Returns:
            bool: True si existe, False en caso contrario
        """
        pass

    @abstractmethod
    def clear(self) -> bool:
        """
        Elimina todos los bots del repositorio.
        
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        pass

    def get_by_trait(self, trait_code: str, min_value: float = 0.0) -> List[Bot]:
        """
        Obtiene bots que tienen un valor mínimo en un rasgo específico.
        
        Args:
            trait_code: Código del rasgo de personalidad
            min_value: Valor mínimo del rasgo (default: 0.0)
            
        Returns:
            List[Bot]: Lista de bots que cumplen el criterio
        """
        return [
            bot for bot in self.get_all()
            if bot.personality.factors.get(trait_code, 0.0) >= min_value
        ]

    def get_by_traits(self, traits: Dict[str, float]) -> List[Bot]:
        """
        Obtiene bots que coinciden con múltiples criterios de rasgos.
        
        Args:
            traits: Diccionario de códigos de rasgos y sus valores mínimos
            
        Returns:
            List[Bot]: Lista de bots que cumplen todos los criterios
        """
        all_bots = self.get_all()
        return [
            bot for bot in all_bots
            if all(
                bot.personality.factors.get(code, 0.0) >= value
                for code, value in traits.items()
            )
        ]

    def get_similar_bots(self, reference_bot: Bot, 
                        threshold: float = 0.8) -> List[Bot]:
        """
        Encuentra bots con personalidades similares al bot de referencia.
        
        Args:
            reference_bot: Bot de referencia
            threshold: Umbral de similitud (0.0 a 1.0)
            
        Returns:
            List[Bot]: Lista de bots similares
        """
        similar_bots = []
        ref_factors = reference_bot.personality.factors
        
        for bot in self.get_all():
            if bot.name == reference_bot.name:
                continue
                
            similarity = self._calculate_similarity(
                ref_factors,
                bot.personality.factors
            )
            
            if similarity >= threshold:
                similar_bots.append(bot)
                
        return similar_bots

    def _calculate_similarity(self, factors1: Dict, factors2: Dict) -> float:
        """
        Calcula la similitud entre dos conjuntos de factores de personalidad.
        
        Args:
            factors1: Primer conjunto de factores
            factors2: Segundo conjunto de factores
            
        Returns:
            float: Valor de similitud entre 0.0 y 1.0
        """
        if not factors1 or not factors2:
            return 0.0
            
        differences = []
        for code in factors1.keys():
            value1 = factors1[code].value
            value2 = factors2[code].value if code in factors2 else 0.0
            differences.append(abs(value1 - value2))
            
        avg_difference = sum(differences) / len(differences)
        return 1.0 - (avg_difference / 2.0)  # Normalizado a [0,1]

    def get_metadata(self) -> Dict:
        """
        Obtiene metadatos sobre el repositorio.
        
        Returns:
            Dict: Diccionario con metadatos del repositorio
        """
        all_bots = self.get_all()
        
        return {
            'total_bots': len(all_bots),
            'last_updated': datetime.now().isoformat(),
            'trait_statistics': self._calculate_trait_statistics(all_bots),
            'personality_types': self._analyze_personality_types(all_bots)
        }

    def _calculate_trait_statistics(self, bots: List[Bot]) -> Dict:
        """
        Calcula estadísticas sobre los rasgos de personalidad.
        
        Args:
            bots: Lista de bots para analizar
            
        Returns:
            Dict: Estadísticas de los rasgos
        """
        if not bots:
            return {}
            
        stats = {}
        for code in bots[0].personality.factors.keys():
            values = [bot.personality.factors[code].value for bot in bots]
            stats[code] = {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values)
            }
            
        return stats

    def _analyze_personality_types(self, bots: List[Bot]) -> Dict:
        """
        Analiza los tipos de personalidad presentes.
        
        Args:
            bots: Lista de bots para analizar
            
        Returns:
            Dict: Distribución de tipos de personalidad
        """
        type_counts = {
            'balanced': 0,
            'extreme': 0,
            'specialized': 0
        }
        
        for bot in bots:
            extreme_traits = sum(
                1 for factor in bot.personality.factors.values()
                if abs(factor.value) > 0.7
            )
            
            if extreme_traits == 0:
                type_counts['balanced'] += 1
            elif extreme_traits > 3:
                type_counts['extreme'] += 1
            else:
                type_counts['specialized'] += 1
                
        return type_counts

    @abstractmethod
    def create_backup(self) -> bool:
        """
        Crea una copia de seguridad del repositorio.
        
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        pass

    @abstractmethod
    def restore_from_backup(self, backup_date: datetime) -> bool:
        """
        Restaura el repositorio desde una copia de seguridad.
        
        Args:
            backup_date: Fecha de la copia de seguridad a restaurar
            
        Returns:
            bool: True si la operación fue exitosa, False en caso contrario
        """
        pass
