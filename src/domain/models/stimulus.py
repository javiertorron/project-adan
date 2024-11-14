from dataclasses import dataclass
from typing import List, Optional
from .need_type import NeedType
from .need_impact import NeedImpact
from .emotional_impact import EmotionalImpact

@dataclass
class Stimulus:
    """Representa un estímulo con sus características e impactos"""
    type: str
    source: str  # Origen del estímulo (ambiente, otro NPC, objeto, etc.)
    
    # Impacto en necesidades
    need_impacts: List[NeedImpact]
    
    # Impacto emocional
    emotional_impact: EmotionalImpact
    
    # Características generales
    threat_level: float  # 0.0 a 1.0
    immediacy: float  # 0.0 a 1.0
    duration: float  # Duración del estímulo 0.0 a 1.0
    
    def get_need_impact(self, need_type: NeedType) -> Optional[NeedImpact]:
        """Obtiene el impacto para una necesidad específica"""
        for impact in self.need_impacts:
            if impact.need_type == need_type:
                return impact
        return None

    def get_highest_urgency_need(self) -> Optional[NeedImpact]:
        """Obtiene la necesidad con la mayor urgencia"""
        if not self.need_impacts:
            return None
        return max(self.need_impacts, key=lambda x: x.urgency)

    def is_emotionally_destabilizing(self, stability_threshold: float = 0.5) -> bool:
        """Determina si el estímulo es emocionalmente desestabilizante"""
        return (abs(self.emotional_impact.impact_intensity) * 
                (1 - self.emotional_impact.current_stability) > stability_threshold)

    def get_total_impact_score(self) -> float:
        """Calcula el impacto total del estímulo"""
        need_score = sum(impact.intensity * impact.urgency for impact in self.need_impacts)
        emotional_score = abs(self.emotional_impact.impact_intensity) * (1 - self.emotional_impact.current_stability)
        threat_score = self.threat_level * self.immediacy
        
        return (need_score + emotional_score + threat_score) / 3