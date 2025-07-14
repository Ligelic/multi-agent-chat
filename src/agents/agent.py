from typing import Dict, List
from dataclasses import dataclass, field
from enum import Enum

class Personality(Enum):
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    SKEPTICAL = "skeptical"
    AGGRESSIVE = "aggressive"

@dataclass
class Belief:
    thought: str
    confidence: float = 0.0  # Range 0-1

@dataclass
class Relationship:
    target_name: str
    score: float = 0.0  # Range -1 to 1
    history: List[str] = field(default_factory=list)

class Agent:
    def __init__(self, name: str, personality: Personality, description: str, mode: int = 0):
        self.name = name
        self.personality = personality
        self.description = description
        self.messages = []
        self.beliefs: Dict[str, Belief] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.action_history: List[str] = []
        self.mode = mode

    def send_message(self, message, chat_room):
        self.action_history.append(f"Sent message: {message}")
        chat_room.broadcast_message(self, message)

    def receive_message(self, message):
        self.messages.append(message)
        
        # Only update relationship if message has a sender
        if message.sender:
            self.update_relationship(message.sender.name, 0.05)  # Small positive bump for interaction
            
            # Personality-based response
            # if self.personality == Personality.FRIENDLY:
            #     print(f"{self.name} warmly received message from {message.sender.name}: {message.content}")
            # elif self.personality == Personality.SKEPTICAL:
            #     print(f"{self.name} cautiously considers message from {message.sender.name}: {message.content}")
            # else:
            #     print(f"{self.name} received message from {message.sender.name}: {message.content}")
        # else:
        #     # Handle system messages
        #     if message.content.startswith(".* joined the chat room"):
        #         return  # Ignore join messages
        #     else:
        #         print(f"System message received by {self.name}: {message.content}")

    def update_belief(self, thought: str, confidence_change: float):
        if thought not in self.beliefs:
            self.beliefs[thought] = Belief(thought)
        new_confidence = max(0.0, min(1.0, self.beliefs[thought].confidence + confidence_change))
        self.beliefs[thought].confidence = new_confidence

    def update_relationship(self, target_name: str, score_change: float, reason: str = ""):
        """Update relationship with another agent with justification."""
        if target_name not in self.relationships:
            self.relationships[target_name] = Relationship(target_name)
            
        # Calculate weighted score change based on personality
        personality_multiplier = {
            Personality.FRIENDLY: 1.2,    # More likely to form positive relationships
            Personality.SKEPTICAL: 0.8,   # More reserved in relationship building
            Personality.NEUTRAL: 1.0,     # Standard relationship building
            Personality.AGGRESSIVE: 0.6   # More difficult to build relationships with
        }.get(self.personality, 1.0)
        
        adjusted_change = score_change * personality_multiplier
        new_score = max(-1.0, min(1.0, self.relationships[target_name].score + adjusted_change))
        
        # Record the reason for relationship change if provided
        if reason:
            self.relationships[target_name].history.append(
                f"Score changed by {adjusted_change:.2f} - Reason: {reason}"
            )
            
        self.relationships[target_name].score = new_score

    def reflect(self) -> str:
        """Reflect on recent actions and relationships"""
        return f"{self.name} has interacted with {len(self.relationships)} agents and holds {len(self.beliefs)} beliefs"

    def __str__(self):
        return f"{self.name} ({self.personality.value})"