from dataclasses import dataclass
from .need_type import NeedType

@dataclass
class NeedImpact:
    """Representa el impacto en una necesidad específica"""
    need_type: NeedType
    intensity: float  # 0.0 a 1.0
    satisfaction_level: float  # 0.0 a 1.0
    urgency: float  # 0.0 a 1.0