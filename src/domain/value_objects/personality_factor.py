from dataclasses import dataclass

@dataclass
class PersonalityFactor:
    code: str
    name: str
    low_label: str
    high_label: str
    value: float = 0.0
    
    def get_descriptor(self) -> str:
        """Retorna un descriptor basado en el valor actual"""
        if self.value > 0.75:
            return f"Muy {self.high_label}"
        elif self.value > 0.25:
            return self.high_label
        elif self.value > -0.25:
            return "Neutral"
        elif self.value > -0.75:
            return self.low_label
        else:
            return f"Muy {self.low_label}"