# TODO: Implement Personality Entity
from typing import Dict, List
from ..value_objects.personality_factor import PersonalityFactor
import random

class Personality:
    FACTORS = {
        'A': ('Afabilidad', 'Reservado', 'Cálido'),
        'B': ('Razonamiento', 'Concreto', 'Abstracto'),
        'C': ('Estabilidad', 'Reactivo', 'Estable'),
        'E': ('Dominancia', 'Deferente', 'Dominante'),
        'F': ('Animación', 'Serio', 'Entusiasta'),
        'G': ('Atención a normas', 'Inconformista', 'Cumplidor'),
        'H': ('Atrevimiento', 'Tímido', 'Atrevido'),
        'I': ('Sensibilidad', 'Utilitario', 'Sensible'),
        'L': ('Vigilancia', 'Confiado', 'Suspicaz'),
        'M': ('Abstracción', 'Práctico', 'Imaginativo'),
        'N': ('Privacidad', 'Abierto', 'Discreto'),
        'O': ('Aprensión', 'Seguro', 'Aprensivo'),
        'Q1': ('Apertura al cambio', 'Tradicional', 'Abierto al cambio'),
        'Q2': ('Autosuficiencia', 'Orientado al grupo', 'Autosuficiente'),
        'Q3': ('Perfeccionismo', 'Flexible', 'Perfeccionista'),
        'Q4': ('Tensión', 'Relajado', 'Tenso')
    }

    def __init__(self):
        self.factors: Dict[str, PersonalityFactor] = {}
        self._initialize_factors()
    
    def _initialize_factors(self):
        for code, (name, low, high) in self.FACTORS.items():
            self.factors[code] = PersonalityFactor(code, name, low, high)
    
    def randomize(self):
        for factor in self.factors.values():
            factor.value = round(random.uniform(-1, 1), 2)
    
    def to_dict(self) -> dict:
        return {code: factor.value for code, factor in self.factors.items()}
    
    def from_dict(self, data: dict):
        for code, value in data.items():
            if code in self.factors:
                self.factors[code].value = value