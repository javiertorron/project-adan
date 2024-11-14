from .personality import Personality
from ..services.needs_manager import NeedsManager
from ..services.emotional_manager import EmotionalManager
from ..services.stimulus_processor import StimulusProcessor

class Bot:
    def __init__(self, name: str, personality: Personality):
        self.name = name
        self.personality = personality
        self.needs_manager = NeedsManager()
        self.emotional_manager = EmotionalManager()
        self.stimulus_processor = StimulusProcessor(
            self.needs_manager,
            self.emotional_manager,
            self.personality  # Añadimos la personalidad aquí
        )
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'personality': self.personality.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Bot':
        personality = Personality()
        personality.from_dict(data['personality'])
        return cls(data['name'], personality)
