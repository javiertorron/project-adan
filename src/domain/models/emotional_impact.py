from dataclasses import dataclass

@dataclass
class EmotionalImpact:
    """Representa el impacto emocional del estímulo"""
    current_stability: float  # 0.0 a 1.0
    impact_intensity: float  # -1.0 a 1.0
    duration: float  # 0.0 a 1.0