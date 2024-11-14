from ..models.emotional_state import EmotionalState

class EmotionalManager:
    """Gestiona el estado emocional del bot"""
    
    def __init__(self):
        self.current_state = EmotionalState.CALM
        self.stability = 1.0  # 0.0 = inestable, 1.0 = completamente estable
        self.stress_level = 0.0  # 0.0 = sin estrés, 1.0 = estrés máximo
        
        # Umbrales para cambios de estado
        self.stress_thresholds = {
            EmotionalState.CALM: 0.3,
            EmotionalState.ALERT: 0.5,
            EmotionalState.STRESSED: 0.7,
            EmotionalState.PANICKED: 0.9
        }
    
    def update_emotional_state(self, stress_delta: float, recovery_rate: float = 0.1):
        """Actualiza el estado emocional basado en cambios de estrés"""
        # Actualizar nivel de estrés
        self.stress_level = max(0.0, min(1.0, self.stress_level + stress_delta))
        
        # Actualizar estabilidad
        if stress_delta > 0:
            self.stability = max(0.0, self.stability - (stress_delta * 0.5))
        else:
            self.stability = min(1.0, self.stability + (recovery_rate * abs(stress_delta)))
        
        # Determinar nuevo estado emocional
        self._update_state()
    
    def _update_state(self):
        """Actualiza el estado basado en el nivel de estrés actual"""
        if self.stress_level >= self.stress_thresholds[EmotionalState.PANICKED]:
            self.current_state = EmotionalState.PANICKED
        elif self.stress_level >= self.stress_thresholds[EmotionalState.STRESSED]:
            self.current_state = EmotionalState.STRESSED
        elif self.stress_level >= self.stress_thresholds[EmotionalState.ALERT]:
            self.current_state = EmotionalState.ALERT
        else:
            self.current_state = EmotionalState.CALM
    
    def evaluate_threat(self, threat_level: float, immediacy: float) -> EmotionalState:
        """Evalúa una amenaza y determina el estado emocional resultante"""
        stress_impact = threat_level * immediacy
        
        if stress_impact >= 0.8:
            return EmotionalState.PANICKED
        elif stress_impact >= 0.6:
            return EmotionalState.STRESSED
        elif stress_impact >= 0.3:
            return EmotionalState.ALERT
        else:
            return EmotionalState.CALM
    
    def can_handle_stimulus(self, stimulus_intensity: float) -> bool:
        """Determina si el bot puede manejar un estímulo dado su estado actual"""
        return self.stability > (stimulus_intensity * 0.7)
