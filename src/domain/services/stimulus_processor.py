from typing import Dict
from ..models.need_type import NeedType
from ..models.emotional_state import EmotionalState
from ..models.stimulus import Stimulus

class StimulusProcessor:
    """Evalúa estímulos y determina respuestas basadas en necesidades y estado"""
    
    def __init__(self, needs_manager, emotional_manager, personality):
        self.needs_manager = needs_manager
        self.emotional_manager = emotional_manager
        self.personality = personality
        self.stability_threshold = 0.5

    def evaluate_stimulus(self, stimulus: Stimulus) -> dict:
        # Modificar umbrales según personalidad
        threat_threshold = self._adjust_threat_threshold()
        stability_threshold = self._adjust_stability_threshold()
        urgency_threshold = self._adjust_urgency_threshold()

        # 1. Evaluación de supervivencia
        survival_impact = stimulus.get_need_impact(NeedType.SURVIVAL)
        if survival_impact and survival_impact.intensity > threat_threshold:
            return {
                'should_react': True,
                'reason': 'Amenaza crítica a la supervivencia',
                'priority': 1,
                'need_type': NeedType.SURVIVAL,
                'emotional_state': EmotionalState.PANICKED,
                'personality_influence': f"Umbral de amenaza ajustado por personalidad: {threat_threshold:.2f}"
            }

        # 2. Evaluación de estabilidad emocional
        if stimulus.is_emotionally_destabilizing(stability_threshold):
            current_emotional_state = self.emotional_manager.evaluate_threat(
                self._adjust_perceived_threat(stimulus.threat_level),
                stimulus.immediacy
            )
            if current_emotional_state in [EmotionalState.STRESSED, EmotionalState.PANICKED]:
                return {
                    'should_react': True,
                    'reason': 'Inestabilidad emocional crítica',
                    'priority': 2,
                    'emotional_state': current_emotional_state,
                    'personality_influence': f"Umbral de estabilidad ajustado por personalidad: {stability_threshold:.2f}"
                }

        # 3. Evaluación de necesidades críticas
        highest_urgency = stimulus.get_highest_urgency_need()
        if highest_urgency and highest_urgency.urgency > urgency_threshold:
            current_need_level = self.needs_manager.needs[highest_urgency.need_type]
            if current_need_level < self.needs_manager.critical_thresholds[highest_urgency.need_type]:
                return {
                    'should_react': True,
                    'reason': f'Necesidad crítica: {highest_urgency.need_type.name}',
                    'priority': self._get_need_priority(highest_urgency.need_type),
                    'need_type': highest_urgency.need_type,
                    'emotional_state': self.emotional_manager.current_state,
                    'personality_influence': f"Umbral de urgencia ajustado por personalidad: {urgency_threshold:.2f}"
                }

        # 4. Evaluación de beneficios vs estabilidad con ajuste de personalidad
        total_impact = self._adjust_perceived_impact(stimulus.get_total_impact_score())
        emotional_stability = stimulus.emotional_impact.current_stability

        if total_impact > 0.7 and emotional_stability > 0.3:
            return {
                'should_react': True,
                'reason': 'Beneficio significativo con estabilidad emocional adecuada',
                'priority': 3,
                'impact_score': total_impact,
                'emotional_stability': emotional_stability,
                'personality_influence': f"Impacto percibido ajustado por personalidad: {total_impact:.2f}"
            }

        return {
            'should_react': False,
            'reason': 'Impacto insuficiente para justificar reacción',
            'priority': 0,
            'impact_score': total_impact,
            'emotional_stability': emotional_stability
        }
    
    def _get_need_priority(self, need: NeedType) -> int:
        """Retorna la prioridad numérica de una necesidad"""
        return need.value
    
    def _adjust_threat_threshold(self) -> float:
        """Ajusta el umbral de amenaza según la personalidad"""
        base_threshold = 0.7
        # Factor C (Estabilidad) reduce el umbral
        stability_mod = -0.2 * self.personality.factors['C'].value
        # Factor H (Atrevimiento) reduce el umbral
        boldness_mod = -0.2 * self.personality.factors['H'].value
        # Factor O (Aprensión) aumenta el umbral
        apprehension_mod = 0.1 * self.personality.factors['O'].value
        
        return max(0.3, min(0.9, base_threshold + stability_mod + boldness_mod + apprehension_mod))

    def _adjust_stability_threshold(self) -> float:
        """Ajusta el umbral de estabilidad emocional según la personalidad"""
        base_threshold = 0.5
        # Factor C (Estabilidad) aumenta el umbral
        stability_mod = 0.2 * self.personality.factors['C'].value
        # Factor Q4 (Tensión) reduce el umbral
        tension_mod = -0.1 * self.personality.factors['Q4'].value
        
        return max(0.2, min(0.8, base_threshold + stability_mod + tension_mod))

    def _adjust_urgency_threshold(self) -> float:
        """Ajusta el umbral de urgencia según la personalidad"""
        base_threshold = 0.8
        # Factor F (Animación) reduce el umbral
        liveliness_mod = -0.1 * self.personality.factors['F'].value
        # Factor Q4 (Tensión) reduce el umbral
        tension_mod = -0.1 * self.personality.factors['Q4'].value
        
        return max(0.6, min(0.9, base_threshold + liveliness_mod + tension_mod))

    def _adjust_perceived_threat(self, threat_level: float) -> float:
        """Ajusta la percepción de amenaza según la personalidad"""
        # Factor O (Aprensión) aumenta la amenaza percibida
        apprehension_mod = 0.2 * self.personality.factors['O'].value
        # Factor C (Estabilidad) reduce la amenaza percibida
        stability_mod = -0.1 * self.personality.factors['C'].value
        
        return max(0.0, min(1.0, threat_level + apprehension_mod + stability_mod))

    def _adjust_perceived_impact(self, impact: float) -> float:
        """Ajusta la percepción del impacto según la personalidad"""
        # Factor F (Animación) aumenta el impacto percibido
        liveliness_mod = 0.1 * self.personality.factors['F'].value
        # Factor O (Aprensión) aumenta el impacto percibido
        apprehension_mod = 0.1 * self.personality.factors['O'].value
        
        return max(0.0, min(1.0, impact + liveliness_mod + apprehension_mod))