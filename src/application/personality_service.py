from typing import Dict, List, Tuple, Optional
from ..domain.entities.personality import Personality
from ..domain.value_objects.personality_factor import PersonalityFactor
from ..infrastructure.config.settings import get_settings
import random
import math
import logging
import numpy as np
from dataclasses import dataclass
from enum import Enum

class PersonalityTemplate(Enum):
    """Templates predefinidos de personalidad"""
    NEUTRAL = "neutral"
    LEADER = "leader"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    SOCIAL = "social"
    RESERVED = "reserved"
    ADVENTUROUS = "adventurous"
    CAUTIOUS = "cautious"

@dataclass
class PersonalityAnalysis:
    """Resultado del análisis de personalidad"""
    dominant_traits: List[Tuple[str, float]]
    trait_distribution: Dict[str, int]
    personality_type: str
    compatibility_scores: Dict[str, float]
    behavioral_tendencies: Dict[str, float]
    decision_making_style: str
    social_orientation: str
    emotional_stability: float
    adaptability_score: float

class PersonalityService:
    """
    Servicio que gestiona las operaciones relacionadas con personalidades.
    Proporciona funcionalidades para crear, analizar y modificar personalidades.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self._setup_logging()
        self._load_templates()
        
    def _setup_logging(self):
        """Configura el sistema de logging"""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler = logging.FileHandler('personality_service.log')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            
    def _load_templates(self):
        """Carga las plantillas predefinidas de personalidad"""
        self.templates = {
            PersonalityTemplate.NEUTRAL: self._create_neutral_template(),
            PersonalityTemplate.LEADER: self._create_leader_template(),
            PersonalityTemplate.CREATIVE: self._create_creative_template(),
            PersonalityTemplate.ANALYTICAL: self._create_analytical_template(),
            PersonalityTemplate.SOCIAL: self._create_social_template(),
            PersonalityTemplate.RESERVED: self._create_reserved_template(),
            PersonalityTemplate.ADVENTUROUS: self._create_adventurous_template(),
            PersonalityTemplate.CAUTIOUS: self._create_cautious_template()
        }
        
    def create_personality(self, template: Optional[PersonalityTemplate] = None) -> Personality:
        """Crea una nueva personalidad, opcionalmente basada en una plantilla"""
        personality = Personality()
        
        if template and template in self.templates:
            base_template = self.templates[template]
            for code, factor in personality.factors.items():
                factor.value = base_template[code]
                # Añadir variación aleatoria para mayor naturalidad
                variation = random.uniform(-0.1, 0.1)
                factor.value = max(-1, min(1, factor.value + variation))
        else:
            self.randomize_personality(personality)
            
        self.logger.info(f"Personalidad creada con template: {template}")
        return personality
        
    def randomize_personality(self, personality: Personality, 
                            intensity: float = 1.0) -> None:
        """
        Randomiza los valores de una personalidad.
        intensity: controla la intensidad de los valores (0.0 a 1.0)
        """
        for factor in personality.factors.values():
            factor.value = random.uniform(-1, 1) * intensity
            
    def analyze_personality(self, personality: Personality) -> PersonalityAnalysis:
        """Realiza un análisis completo de la personalidad"""
        return PersonalityAnalysis(
            dominant_traits=self._get_dominant_traits(personality),
            trait_distribution=self._calculate_trait_distribution(personality),
            personality_type=self._determine_personality_type(personality),
            compatibility_scores=self._calculate_compatibility_scores(personality),
            behavioral_tendencies=self._analyze_behavioral_tendencies(personality),
            decision_making_style=self._determine_decision_style(personality),
            social_orientation=self._determine_social_orientation(personality),
            emotional_stability=self._calculate_emotional_stability(personality),
            adaptability_score=self._calculate_adaptability(personality)
        )
        
    def calculate_compatibility(self, personality1: Personality, 
                              personality2: Personality) -> float:
        """Calcula la compatibilidad entre dos personalidades"""
        compatibility_score = 0.0
        factor_weights = self._get_compatibility_weights()
        
        for code in personality1.factors.keys():
            factor_diff = abs(personality1.factors[code].value - 
                            personality2.factors[code].value)
            weighted_diff = factor_diff * factor_weights.get(code, 1.0)
            compatibility_score += weighted_diff
            
        # Normalizar score (0 = idénticos, 1 = opuestos)
        max_possible_diff = sum(factor_weights.values()) * 2
        normalized_score = 1 - (compatibility_score / max_possible_diff)
        
        return normalized_score
        
    def merge_personalities(self, personality1: Personality, personality2: Personality, 
                          weight1: float = 0.5) -> Personality:
        """
        Combina dos personalidades con el peso especificado.
        weight1: peso para personality1 (0.0 a 1.0), el resto para personality2
        """
        weight2 = 1 - weight1
        result = Personality()
        
        for code in personality1.factors.keys():
            value1 = personality1.factors[code].value
            value2 = personality2.factors[code].value
            result.factors[code].value = value1 * weight1 + value2 * weight2
            
        return result
        
    def evolve_personality(self, personality: Personality, 
                          experiences: List[Dict[str, float]]) -> None:
        """
        Evoluciona una personalidad basada en experiencias.
        experiences: lista de diccionarios con impactos en factores
        """
        learning_rate = self.settings.get().personality.learning_rate
        
        for experience in experiences:
            for code, impact in experience.items():
                if code in personality.factors:
                    current = personality.factors[code].value
                    change = impact * learning_rate
                    personality.factors[code].value = max(-1, min(1, current + change))
                    
    def _get_dominant_traits(self, personality: Personality, 
                           threshold: float = 0.7) -> List[Tuple[str, float]]:
        """Identifica los rasgos dominantes de la personalidad"""
        dominant = []
        for code, factor in personality.factors.items():
            if abs(factor.value) > threshold:
                dominant.append((code, factor.value))
        return sorted(dominant, key=lambda x: abs(x[1]), reverse=True)
        
    def _calculate_trait_distribution(self, personality: Personality) -> Dict[str, int]:
        """Calcula la distribución de rasgos por intensidad"""
        distribution = {
            'very_low': 0,   # < -0.7
            'low': 0,        # -0.7 to -0.3
            'neutral': 0,    # -0.3 to 0.3
            'high': 0,       # 0.3 to 0.7
            'very_high': 0   # > 0.7
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
        
    def _determine_personality_type(self, personality: Personality) -> str:
        """Determina el tipo de personalidad basado en rasgos dominantes"""
        # Implementar lógica de clasificación según los requisitos específicos
        return "Balanced"  # Placeholder
        
    def _calculate_compatibility_scores(self, personality: Personality) -> Dict[str, float]:
        """Calcula compatibilidad con diferentes templates"""
        scores = {}
        for template_name, template_values in self.templates.items():
            score = 0.0
            for code, value in template_values.items():
                factor_diff = abs(personality.factors[code].value - value)
                score += factor_diff
            scores[template_name.value] = 1 - (score / len(template_values))
        return scores
        
    def _analyze_behavioral_tendencies(self, personality: Personality) -> Dict[str, float]:
        """Analiza tendencias de comportamiento basadas en la personalidad"""
        return {
            'risk_taking': self._calculate_risk_taking(personality),
            'sociability': self._calculate_sociability(personality),
            'leadership': self._calculate_leadership(personality),
            'creativity': self._calculate_creativity(personality),
            'analytical': self._calculate_analytical_tendency(personality)
        }
        
    def _determine_decision_style(self, personality: Personality) -> str:
        """Determina el estilo de toma de decisiones"""
        analytical = self._calculate_analytical_tendency(personality)
        emotional = self._calculate_emotional_dependency(personality)
        
        if analytical > 0.7:
            return "Logical"
        elif emotional > 0.7:
            return "Emotional"
        else:
            return "Balanced"
            
    def _determine_social_orientation(self, personality: Personality) -> str:
        """Determina la orientación social"""
        sociability = self._calculate_sociability(personality)
        
        if sociability > 0.7:
            return "Extroverted"
        elif sociability < -0.3:
            return "Introverted"
        else:
            return "Ambivert"
            
    def _calculate_emotional_stability(self, personality: Personality) -> float:
        """Calcula la estabilidad emocional"""
        relevant_factors = ['C', 'O', 'Q4']  # Factores relevantes de Cattell
        weights = {'C': 0.5, 'O': 0.3, 'Q4': 0.2}
        
        stability = 0.0
        for factor, weight in weights.items():
            if factor in personality.factors:
                stability += personality.factors[factor].value * weight
                
        return max(-1, min(1, stability))
        
    def _calculate_adaptability(self, personality: Personality) -> float:
        """Calcula la capacidad de adaptación"""
        relevant_factors = ['Q1', 'F', 'E']
        weights = {'Q1': 0.4, 'F': 0.3, 'E': 0.3}
        
        adaptability = 0.0
        for factor, weight in weights.items():
            if factor in personality.factors:
                adaptability += personality.factors[factor].value * weight
                
        return max(-1, min(1, adaptability))
        
    # Templates predefinidos
    def _create_neutral_template(self) -> Dict[str, float]:
        return {code: 0.0 for code in Personality.FACTORS.keys()}
        
    def _create_leader_template(self) -> Dict[str, float]:
        return {
            'A': 0.7,  # Cálido
            'E': 0.8,  # Dominante
            'H': 0.7,  # Atrevido
            'L': 0.3,  # Vigilante
            'O': -0.5, # Seguro
            'Q2': 0.6, # Autosuficiente
            'Q3': 0.7, # Perfeccionista
            # ... otros factores en valores neutrales
            **{code: 0.0 for code in Personality.FACTORS.keys() 
               if code not in ['A', 'E', 'H', 'L', 'O', 'Q2', 'Q3']}
        }
        
    def _create_creative_template(self) -> Dict[str, float]:
        return {
            'B': 0.7,  # Abstracto
            'M': 0.8,  # Imaginativo
            'Q1': 0.8, # Abierto al cambio
            'F': 0.6,  # Entusiasta
            # ... otros factores
            **{code: 0.0 for code in Personality.FACTORS.keys() 
               if code not in ['B', 'M', 'Q1', 'F']}
        }
        
    def _create_analytical_template(self) -> Dict[str, float]:
        return {
            'B': 0.8,  # Abstracto
            'G': 0.7,  # Cumplidor
            'Q3': 0.7, # Perfeccionista
            'M': 0.5,  # Imaginativo
            # ... otros factores
            **{code: 0.0 for code in Personality.FACTORS.keys() 
               if code not in ['B', 'G', 'Q3', 'M']}
        }
        
    def _create_social_template(self) -> Dict[str, float]:
        return {
            'A': 0.8,  # Cálido
            'F': 0.7,  # Entusiasta
            'H': 0.7,  # Atrevido
            'Q2': -0.6,# Orientado al grupo
            # ... otros factores
            **{code: 0.0 for code in Personality.FACTORS.keys() 
               if code not in ['A', 'F', 'H', 'Q2']}
        }
        
    def _create_reserved_template(self) -> Dict[str, float]:
        return {
            'A': -0.5, # Reservado
            'F': -0.4, # Serio
            'H': -0.5, # Tímido
            'N': 0.6,  # Discreto
            # ... otros factores
            **{code: 0.0 for code in Personality.FACTORS.keys() 
               if code not in ['A', 'F', 'H', 'N']}
        }
        
    def _create_adventurous_template(self) -> Dict[str, float]:
        return {
            'H': 0.8,  # Atrevido
            'F': 0.7,  # Entusiasta
            'Q1': 0.7, # Abierto al cambio
            'E': 0.6,  # Dominante
            # ... otros factores
            **{code: 0.0 for code in Personality.FACTORS.keys() 
               if code not in ['H', 'F', 'Q1', 'E']}
        }
        
    def _create_cautious_template(self) -> Dict[str, float]:
        return {
            'H': -0.6, # Tímido
            'L': 0.6,  # Vigilante
            'O': 0.5,  # Aprensivo
            'F': -0.4, # Serio
            'G': 0.7,  # Cumplidor
            # ... otros factores
            **{code: 0.0 for code in Personality.FACTORS.keys() 
               if code not in ['H', 'L', 'O', 'F', 'G']}
        }
        
    # Métodos de cálculo de tendencias
    def _calculate_risk_taking(self, personality: Personality) -> float:
        """Calcula la tendencia a tomar riesgos"""
        weights = {
            'H': 0.3,  # Atrevimiento
            'F': 0.2,  # Animación
            'L': -0.1, # Vigilancia
            'O': -0.2, # Aprensión
            'Q1': 0.2  # Apertura al cambio
        }
        
        score = 0.0
        for factor, weight in weights.items():
            if factor in personality.factors:
                score += personality.factors[factor].value * weight
                
        return max(-1, min(1, score))
        
    def _calculate_sociability(self, personality: Personality) -> float:
        """Calcula el nivel de sociabilidad"""
        weights = {
            'A': 0.3,  # Afabilidad
            'F': 0.2,  # Animación
            'H': 0.2,  # Atrevimiento
            'Q2': -0.2,# Autosuficiencia
            'N': -0.1  # Privacidad
        }
        
        score = 0.0
        for factor, weight in weights.items():
            if factor in personality.factors:
                score += personality.factors[factor].value * weight
                
        return max(-1, min(1, score))
        
    def _calculate_leadership(self, personality: Personality) -> float:
        """Calcula la tendencia al liderazgo"""
        weights = {
            'E': 0.3,  # Dominancia
            'L': 0.1,  # Vigilancia
            'Q2': 0.2, # Autosuficiencia
            'O': -0.2, # Aprensión
            'H': 0.2   # Atrevimiento
        }
        
        score = 0.0
        for factor, weight in weights.items():
            if factor in personality.factors:
                score += personality.factors[factor].value * weight
                
        return max(-1, min(1, score))
        
    def _calculate_creativity(self, personality: Personality) -> float:
        """Calcula el nivel de creatividad"""
        weights = {
            'M': 0.3,  # Abstracción
            'Q1': 0.3, # Apertura al cambio
            'B': 0.2,  # Razonamiento
            'F': 0.1,  # Animación
            'A': 0.1   # Afabilidad
        }
        
        score = 0.0
        for factor, weight in weights.items():
            if factor in personality.factors:
                score += personality.factors[factor].value * weight
                
        return max(-1, min(1, score))
        
    def _calculate_analytical_tendency(self, personality: Personality) -> float:
        """Calcula la tendencia analítica"""
        weights = {
            'B': 0.3,  # Razonamiento
            'G': 0.2,  # Atención a normas
            'Q3': 0.2, # Perfeccionismo
            'M': -0.1, # Abstracción
            'C': 0.2   # Estabilidad
        }
        
        score = 0.0
        for factor, weight in weights.items():
            if factor in personality.factors:
                score += personality.factors[factor].value * weight
                
        return max(-1, min(1, score))
        
    def _calculate_emotional_dependency(self, personality: Personality) -> float:
        """Calcula la dependencia emocional"""
        weights = {
            'C': -0.3, # Estabilidad
            'O': 0.3,  # Aprensión
            'Q4': 0.2, # Tensión
            'I': 0.2,  # Sensibilidad
        }
        
        score = 0.0
        for factor, weight in weights.items():
            if factor in personality.factors:
                score += personality.factors[factor].value * weight
                
        return max(-1, min(1, score))
        
    def _get_compatibility_weights(self) -> Dict[str, float]:
        """Retorna los pesos para el cálculo de compatibilidad"""
        return {
            'A': 1.0,  # Afabilidad
            'E': 0.8,  # Dominancia
            'F': 0.7,  # Animación
            'H': 0.9,  # Atrevimiento
            'I': 0.6,  # Sensibilidad
            'L': 0.8,  # Vigilancia
            'N': 0.7,  # Privacidad
            'Q2': 0.9, # Autosuficiencia
            # Valores por defecto para otros factores
            **{code: 0.5 for code in Personality.FACTORS.keys() 
               if code not in ['A', 'E', 'F', 'H', 'I', 'L', 'N', 'Q2']}
        }
        
    def generate_personality_description(self, personality: Personality) -> str:
        """Genera una descripción en lenguaje natural de la personalidad"""
        analysis = self.analyze_personality(personality)
        
        description_parts = []
        
        # Descripción general
        description_parts.append(
            f"Esta personalidad es principalmente {analysis.personality_type.lower()}, "
            f"con una orientación {analysis.social_orientation.lower()}."
        )
        
        # Rasgos dominantes
        if analysis.dominant_traits:
            traits_desc = ", ".join(
                f"{Personality.FACTORS[code][0]}: {value:+.2f}"
                for code, value in analysis.dominant_traits[:3]
            )
            description_parts.append(f"Los rasgos más destacados son: {traits_desc}.")
            
        # Estilo de decisión
        description_parts.append(
            f"Muestra un estilo de toma de decisiones {analysis.decision_making_style.lower()}, "
            f"con una estabilidad emocional de {analysis.emotional_stability:+.2f} "
            f"y una adaptabilidad de {analysis.adaptability_score:+.2f}."
        )
        
        # Tendencias conductuales
        tendencies = analysis.behavioral_tendencies
        high_tendencies = [
            (k, v) for k, v in tendencies.items() 
            if abs(v) > 0.5
        ]
        if high_tendencies:
            tendencies_desc = ", ".join(
                f"{k} ({v:+.2f})"
                for k, v in sorted(high_tendencies, key=lambda x: abs(x[1]), reverse=True)
            )
            description_parts.append(
                f"Las tendencias conductuales más marcadas son: {tendencies_desc}."
            )
            
        return " ".join(description_parts)
        
    def suggest_personality_adjustments(
        self, 
        personality: Personality,
        target_template: PersonalityTemplate
    ) -> Dict[str, float]:
        """Sugiere ajustes para acercar la personalidad a un template objetivo"""
        target_values = self.templates[target_template]
        adjustments = {}
        
        for code, target in target_values.items():
            current = personality.factors[code].value
            if abs(current - target) > 0.2:  # Umbral de diferencia significativa
                adjustments[code] = target - current
                
        return adjustments

if __name__ == "__main__":
    # Código de prueba
    service = PersonalityService()
    
    # Crear algunas personalidades de prueba
    neutral_personality = service.create_personality(PersonalityTemplate.NEUTRAL)
    leader_personality = service.create_personality(PersonalityTemplate.LEADER)
    creative_personality = service.create_personality(PersonalityTemplate.CREATIVE)
    
    # Analizar personalidades
    for personality, name in [
        (neutral_personality, "Neutral"),
        (leader_personality, "Líder"),
        (creative_personality, "Creativo")
    ]:
        print(f"\nAnálisis de personalidad {name}:")
        print(service.generate_personality_description(personality))
        
        # Calcular compatibilidades
        compatibility = service.calculate_compatibility(
            personality,
            service.create_personality(PersonalityTemplate.SOCIAL)
        )
        print(f"Compatibilidad con template social: {compatibility:.2f}")
        
        # Sugerir ajustes
        adjustments = service.suggest_personality_adjustments(
            personality,
            PersonalityTemplate.LEADER
        )
        if adjustments:
            print("\nAjustes sugeridos para perfil de líder:")
            for code, adjustment in adjustments.items():
                print(f"{Personality.FACTORS[code][0]}: {adjustment:+.2f}")
