from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Set, Any
import numpy as np
from datetime import datetime, timedelta
import json
import os
from collections import deque, defaultdict
from dataclasses import dataclass, field
import logging
import asyncio
from contextlib import contextmanager
from scipy.stats import norm
from utils.vtuber_integration import VTuberIntegration
from utils.error_boundary import ErrorBoundary

class PersonalityDimension(Enum):
    EXTRAVERSION = auto()
    AGREEABLENESS = auto()
    CONSCIENTIOUSNESS = auto()
    OPENNESS = auto()          # New: Openness to experience
    NEUROTICISM = auto()       # New: Emotional stability
    CREATIVITY = auto()        # New: Creative expression
    EMPATHY = auto()          # New: Emotional intelligence
    ASSERTIVENESS = auto()    # New: Communication style

@dataclass
class PersonalityProfile:
    base_weights: Dict[PersonalityDimension, float] = field(default_factory=dict)
    context_modifiers: Dict[str, Dict[PersonalityDimension, float]] = field(default_factory=dict)
    interaction_patterns: Dict[str, List[float]] = field(default_factory=dict)
    adaptation_rate: float = 0.01
    
    def __post_init__(self):
        for dim in PersonalityDimension:
            if dim not in self.base_weights:
                self.base_weights[dim] = 0.0

@dataclass
class InteractionEvent:
    timestamp: datetime
    message: str
    emotion: str
    response_time: float
    word_count: int
    sentiment_score: float
    context_tags: Set[str] = field(default_factory=set)
    user_feedback: Optional[float] = None
    conversation_depth: int = 0
    topic_coherence: float = 0.0
    creativity_score: float = 0.0
    empathy_score: float = 0.0

@ErrorBoundary.system()
class PersonalityMetricsManager:
    def __init__(self, history_length: int = 1000):
        self.history_length = history_length
        self.interaction_history: deque = deque(maxlen=history_length)
        self.personality_states: deque = deque(maxlen=history_length)
        self.profile = PersonalityProfile()
        self.context_history: Dict[str, List[InteractionEvent]] = defaultdict(list)
        self.topic_memory: Dict[str, float] = defaultdict(float)
        self.emotional_memory: Dict[str, List[Tuple[datetime, str, float]]] = defaultdict(list)
        
        # New: Advanced configuration
        self.config = {
            'adaptation_threshold': 0.3,
            'context_decay_rate': 0.95,
            'emotional_memory_span': timedelta(days=7),
            'minimum_confidence': 0.6,
            'personality_shift_momentum': 0.8
        }
        
        self.metrics = {}
        # Don't call load_state directly in __init__
        self.initialized = False
        
    async def initialize(self):
        """Async initialization method"""
        if not self.initialized:
            await self.load_state()
            self.initialized = True

    async def analyze_interaction_patterns(self) -> Dict[str, Any]:
        """Analyze complex interaction patterns asynchronously"""
        patterns = defaultdict(list)
        
        for event in self.interaction_history:
            # Analyze conversation depth
            depth_score = self._calculate_conversation_depth(event)
            patterns['depth'].append(depth_score)
            
            # Analyze topic coherence
            coherence = self._calculate_topic_coherence(event)
            patterns['coherence'].append(coherence)
            
            # Track emotional resonance
            emotional_score = self._calculate_emotional_resonance(event)
            patterns['emotional_resonance'].append(emotional_score)
        
        return {
            'depth_trend': np.mean(patterns['depth']),
            'coherence_stability': np.std(patterns['coherence']),
            'emotional_connection': np.mean(patterns['emotional_resonance'])
        }

    def _calculate_conversation_depth(self, event: InteractionEvent) -> float:
        """Calculate conversation depth based on context and complexity"""
        factors = [
            len(event.context_tags) * 0.2,
            min(event.word_count / 100.0, 1.0) * 0.3,
            event.topic_coherence * 0.3,
            (event.creativity_score + event.empathy_score) * 0.2
        ]
        return np.mean(factors)

    def _calculate_topic_coherence(self, event: InteractionEvent) -> float:
        """Evaluate topic consistency and development"""
        coherence_score = 0.0
        for tag in event.context_tags:
            if tag in self.topic_memory:
                coherence_score += self.topic_memory[tag]
        return min(coherence_score / max(len(event.context_tags), 1), 1.0)

    def _calculate_emotional_resonance(self, event: InteractionEvent) -> float:
        """Measure emotional connection and response appropriateness"""
        current_emotion = event.emotion
        emotion_history = self.emotional_memory.get(current_emotion, [])
        
        if not emotion_history:
            return 0.5
        
        recent_emotions = [e for t, e, s in emotion_history 
                         if datetime.now() - t < self.config['emotional_memory_span']]
        
        if not recent_emotions:
            return 0.5
            
        emotional_consistency = len([e for e in recent_emotions if e == current_emotion]) / len(recent_emotions)
        return emotional_consistency * event.empathy_score

    @contextmanager
    def personality_adaptation_context(self, context_tags: Set[str]):
        """Context manager for temporary personality adaptations"""
        original_weights = self.profile.base_weights.copy()
        try:
            self._apply_context_modifiers(context_tags)
            yield
        finally:
            self._restore_base_weights(original_weights)

    def _apply_context_modifiers(self, context_tags: Set[str]) -> None:
        """Apply context-specific personality modifications"""
        for tag in context_tags:
            if tag in self.profile.context_modifiers:
                for dim, modifier in self.profile.context_modifiers[tag].items():
                    current = self.profile.base_weights[dim]
                    self.profile.base_weights[dim] = np.clip(
                        current + modifier * self.config['personality_shift_momentum'],
                        -1.0, 1.0
                    )

    def _restore_base_weights(self, original_weights: Dict[PersonalityDimension, float]) -> None:
        """Restore original personality weights with smooth transition"""
        for dim, original in original_weights.items():
            current = self.profile.base_weights[dim]
            self.profile.base_weights[dim] = current * (1 - self.config['context_decay_rate']) + \
                                           original * self.config['context_decay_rate']

    async def update_personality_model(self) -> None:
        """Asynchronously update the personality model based on recent interactions"""
        patterns = await self.analyze_interaction_patterns()
        
        if patterns['depth_trend'] > self.config['adaptation_threshold']:
            self.profile.adaptation_rate *= 1.1  # Increase adaptation rate
        else:
            self.profile.adaptation_rate *= 0.9  # Decrease adaptation rate
            
        self.profile.adaptation_rate = np.clip(self.profile.adaptation_rate, 0.001, 0.1)

    def load_state(self) -> None:
        """Load personality state from disk with error handling"""
        try:
            with open('personality_state.json', 'r') as f:
                state = json.load(f)
                self.profile.base_weights = {
                    PersonalityDimension(k): float(v) 
                    for k, v in state.get('base_weights', {}).items()
                }
        except FileNotFoundError:
            logging.info("No previous personality state found. Starting fresh.")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding personality state: {e}")
            self._initialize_default_weights()
        except Exception as e:
            logging.error(f"Unexpected error loading personality state: {e}")
            self._initialize_default_weights()

    @ErrorBoundary.component()
    def save_state(self) -> None:
        """Save personality state to disk with error handling"""
        try:
            state = {
                'base_weights': {k.value: float(v) for k, v in self.profile.base_weights.items()},
                'timestamp': datetime.now().isoformat()
            }
            with open('personality_state.json', 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save personality state: {e}")

    @ErrorBoundary.component()
    def add_interaction(self, event: InteractionEvent) -> None:
        """Process and store a new interaction event with error handling"""
        try:
            self.interaction_history.append(event)
            self._update_personality_weights(event)
            self.save_state()
        except Exception as e:
            logging.error(f"Error processing interaction: {e}")

    @ErrorBoundary.component()
    def _update_personality_weights(self, event: InteractionEvent) -> None:
        """Update personality weights based on interaction with error handling"""
        try:
            # Calculate interaction features
            response_speed = 1.0 - min(event.response_time / 5.0, 1.0)
            verbosity = min(event.word_count / 50.0, 1.0)
            
            # Update extraversion based on verbosity and emotion
            extraversion_delta = (
                0.1 * verbosity +
                0.2 * (1 if event.emotion in ['joy', 'excitement'] else -0.5)
            )
            
            # Update agreeableness based on sentiment
            agreeableness_delta = 0.15 * event.sentiment_score
            
            # Update conscientiousness based on response speed
            conscientiousness_delta = 0.1 * response_speed
            
            # Apply updates with learning rate and decay
            for dim, delta in [
                (PersonalityDimension.EXTRAVERSION, extraversion_delta),
                (PersonalityDimension.AGREEABLENESS, agreeableness_delta),
                (PersonalityDimension.CONSCIENTIOUSNESS, conscientiousness_delta)
            ]:
                current = self.profile.base_weights[dim]
                updated = current * self.config['context_decay_rate'] + self.profile.adaptation_rate * delta
                self.profile.base_weights[dim] = np.clip(updated, -1.0, 1.0)
        except Exception as e:
            logging.error(f"Error updating personality weights: {e}")
            # Maintain current weights on error

    def get_personality_metrics(self) -> Dict:
        """Get current personality metrics and history"""
        metrics = {
            'timestamps': [e.timestamp.isoformat() for e in self.interaction_history],
            'interaction_score': self._calculate_interaction_score(),
            'dominant_trait': self._get_dominant_trait(),
        }
        
        # Add current weights
        for dim in PersonalityDimension:
            metrics[dim.value] = self.profile.base_weights[dim]
            
        return metrics

    def _calculate_interaction_score(self) -> float:
        """Calculate overall interaction score"""
        if not self.interaction_history:
            return 0.0
            
        recent = list(self.interaction_history)[-10:]
        weights = np.exp(np.linspace(-1, 0, len(recent)))  # Exponential decay
        
        scores = [
            0.4 * (1 - min(e.response_time / 5.0, 1.0)) +  # Response speed
            0.3 * e.sentiment_score +                       # Sentiment
            0.3 * min(e.word_count / 50.0, 1.0)           # Engagement
            for e in recent
        ]
        
        return float(np.average(scores, weights=weights))

    def _get_dominant_trait(self) -> str:
        """Determine the dominant personality trait"""
        traits = list(self.profile.base_weights.items())
        dominant = max(traits, key=lambda x: abs(x[1]))
        magnitude = abs(dominant[1])
        
        if magnitude < 0.2:
            return "Balanced"
        
        trait_name = dominant[0].value.title()
        direction = "High" if dominant[1] > 0 else "Low"
        return f"{direction} {trait_name}"

    def get_interaction_history(self) -> Dict:
        """Get interaction history data"""
        if not self.interaction_history:
            return {'timestamps': [], 'scores': []}
            
        history = list(self.interaction_history)
        return {
            'timestamps': [e.timestamp.isoformat() for e in history],
            'scores': [
                0.4 * (1 - min(e.response_time / 5.0, 1.0)) +
                0.3 * e.sentiment_score +
                0.3 * min(e.word_count / 50.0, 1.0)
                for e in history
            ]
        }

# Global instance
_manager = PersonalityMetricsManager()

# Public API
def get_personality_metrics() -> Dict[str, Any]:
    """Get current personality metrics and history"""
    metrics = {
        'timestamps': [],
        'interaction_score': 0.0,
        'dominant_trait': 'Balanced'
    }
    
    try:
        base_metrics = _manager.get_personality_metrics()
        metrics.update(base_metrics)
        
        # Add historical values for each dimension
        for dim in PersonalityDimension:
            metrics[f'{dim.value}_history'] = [
                state.base_weights.get(dim, 0.0)
                for state in _manager.personality_states
            ]
            
    except Exception as e:
        logging.error(f"Error getting personality metrics: {e}")
        
    return metrics

def get_interaction_history() -> Dict:
    return _manager.get_interaction_history()

def update_personality_weights(weights: Dict[str, float]) -> None:
    """Update personality weights manually"""
    for dim_name, value in weights.items():
        try:
            dim = PersonalityDimension(dim_name)
            _manager.profile.base_weights[dim] = np.clip(float(value), -1.0, 1.0)
        except (ValueError, KeyError):
            logging.warning(f"Invalid personality dimension: {dim_name}")
    _manager.save_state()

async def record_interaction(
    message: str,
    emotion: str,
    response_time: float,
    sentiment_score: float
) -> None:
    """Record a new interaction event and update VTube expression"""
    event = InteractionEvent(
        timestamp=datetime.now(),
        message=message,
        emotion=emotion,
        response_time=response_time,
        word_count=len(message.split()),
        sentiment_score=sentiment_score
    )
    _manager.add_interaction(event)
    
    # Calculate emotion intensity based on sentiment and interaction scores
    intensity = (abs(sentiment_score) + _manager._calculate_interaction_score()) / 2
    
    # Apply emotion to VTube Studio
    vtuber = VTuberIntegration()
    await vtuber.apply_emotion_expression(emotion, intensity)

def get_interaction_patterns() -> Dict[str, Any]:
    """Get current interaction patterns and analysis"""
    patterns = {
        'timestamps': [],
        'interaction_scores': [],
        'emotion_distribution': {},
        'context_tags': [],
        'context_influence': [],
        'topic_coherence': [],
        'depth_trend': 0.0,
        'emotional_connection': 0.0
    }
    
    try:
        # Get patterns from manager
        async_patterns = asyncio.run(_manager.analyze_interaction_patterns())
        
        # Get recent history
        history = _manager.get_interaction_history()
        patterns['timestamps'] = history['timestamps']
        patterns['interaction_scores'] = history['scores']
        
        # Calculate emotion distribution
        emotion_counts = defaultdict(int)
        for event in _manager.interaction_history:
            emotion_counts[event.emotion] += 1
        total = sum(emotion_counts.values()) or 1
        patterns['emotion_distribution'] = {
            k: v/total for k, v in emotion_counts.items()
        }
        
        # Get context influence
        context_tags = set()
        for event in _manager.interaction_history:
            context_tags.update(event.context_tags)
        patterns['context_tags'] = list(context_tags)
        
        # Create context influence matrix
        influence_matrix = []
        for tag in context_tags:
            if tag in _manager.profile.context_modifiers:
                row = [_manager.profile.context_modifiers[tag].get(dim, 0) 
                      for dim in PersonalityDimension]
            else:
                row = [0] * len(PersonalityDimension)
            influence_matrix.append(row)
        patterns['context_influence'] = influence_matrix
        
        # Get topic coherence
        patterns['topic_coherence'] = [
            _manager._calculate_topic_coherence(event)
            for event in _manager.interaction_history
        ]
        
        # Add async analysis results
        patterns.update(async_patterns)
        
    except Exception as e:
        logging.error(f"Error getting interaction patterns: {e}")
        
    return patterns

def update_personality_config(config: Dict[str, Any]) -> None:
    """Update personality configuration settings"""
    try:
        _manager.config.update(config)
    except Exception as e:
        logging.error(f"Error updating personality config: {e}") 