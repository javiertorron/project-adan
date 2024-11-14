from typing import Dict
from ..models.need_type import NeedType

class NeedsManager:
    """Gestiona las necesidades del bot y sus niveles"""
    
    def __init__(self):
        # Inicializar necesidades con valores por defecto
        self.needs = {need_type: 1.0 for need_type in NeedType}
        
        # Umbrales críticos para cada necesidad
        self.critical_thresholds = {
            NeedType.SURVIVAL: 0.2,      # Muy crítico
            NeedType.PHYSIOLOGICAL: 0.3,
            NeedType.SAFETY: 0.3,
            NeedType.SOCIAL: 0.4,
            NeedType.ESTEEM: 0.4,
            NeedType.GROWTH: 0.5         # Menos crítico
        }
        
        # Tasas de decaimiento por necesidad por segundo
        # Considerando que 1.0 representa el máximo y queremos que tarden:
        # SURVIVAL: ~8 horas (28800 segundos) para llegar a crítico
        # PHYSIOLOGICAL: ~4 horas (14400 segundos) para llegar a crítico
        # SAFETY: ~12 horas (43200 segundos) para llegar a crítico
        # SOCIAL: ~24 horas (86400 segundos) para llegar a crítico
        # ESTEEM: ~48 horas (172800 segundos) para llegar a crítico
        # GROWTH: ~72 horas (259200 segundos) para llegar a crítico
        
        self.decay_rates = {
            NeedType.SURVIVAL: 0.00003,      # ~8 horas hasta crítico
            NeedType.PHYSIOLOGICAL: 0.00005, # ~4 horas hasta crítico
            NeedType.SAFETY: 0.00002,        # ~12 horas hasta crítico
            NeedType.SOCIAL: 0.00001,        # ~24 horas hasta crítico
            NeedType.ESTEEM: 0.000005,       # ~48 horas hasta crítico
            NeedType.GROWTH: 0.000003        # ~72 horas hasta crítico
        }
    
    def update_needs(self, delta_time: float):
        """Actualiza los niveles de necesidad basado en el tiempo transcurrido"""
        for need_type in NeedType:
            decay = self.decay_rates[need_type] * delta_time
            self.needs[need_type] = max(0.0, self.needs[need_type] - decay)
    
    def apply_impact(self, need_type: NeedType, impact: float):
        """Aplica un impacto a una necesidad específica"""
        # Asegurarse de que need_type es una instancia de NeedType
        if isinstance(need_type, str):
            need_type = NeedType[need_type]
            
        if need_type in self.needs:
            self.needs[need_type] = max(0.0, min(1.0, self.needs[need_type] + impact))
    
    def get_critical_needs(self) -> Dict[NeedType, float]:
        """Retorna las necesidades que están por debajo de su umbral crítico"""
        return {
            need_type: level 
            for need_type, level in self.needs.items() 
            if level < self.critical_thresholds[need_type]
        }
    
    def get_satisfaction_level(self) -> float:
        """Retorna el nivel general de satisfacción de necesidades"""
        weighted_sum = sum(
            level * (1.0 / need_type.value)  # Necesidades básicas tienen más peso
            for need_type, level in self.needs.items()
        )
        total_weights = sum(1.0 / need_type.value for need_type in NeedType)
        return weighted_sum / total_weights