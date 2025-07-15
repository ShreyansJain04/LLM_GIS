"""Flashcard system with spaced repetition."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import json
from pathlib import Path

class FlashcardDeck:
    """Manages a deck of flashcards with spaced repetition."""
    
    def __init__(self, username: str, topic: str):
        self.username = username
        self.topic = topic
        self.deck_file = Path(f'flashcards_{username}.json')
        self.deck = self._load_or_create_deck()
        
    def _load_or_create_deck(self) -> Dict:
        """Load existing deck or create new one."""
        if self.deck_file.exists():
            with self.deck_file.open('r') as f:
                return json.load(f)
        return {
            'decks': {},
            'stats': {
                'cards_studied': 0,
                'correct_answers': 0,
                'study_sessions': 0
            }
        }
    
    def save_deck(self):
        """Save deck to file."""
        with self.deck_file.open('w') as f:
            json.dump(self.deck, f, indent=2)
    
    def add_card(self, front: str, back: str, subtopic: Optional[str] = None) -> Dict:
        """Add a new flashcard to the deck."""
        if self.topic not in self.deck['decks']:
            self.deck['decks'][self.topic] = []
            
        # Check for duplicates
        for existing_card in self.deck['decks'][self.topic]:
            if existing_card['front'].lower().strip() == front.lower().strip():
                return existing_card  # Don't add duplicate
            
        card = {
            'front': front,
            'back': back,
            'subtopic': subtopic or self.topic,
            'created_at': datetime.now().isoformat(),
            'last_reviewed': None,
            'next_review': datetime.now().isoformat(),
            'interval': 0,  # Days until next review
            'ease_factor': 2.5,  # SuperMemo-2 algorithm factor
            'repetitions': 0,  # Number of successful reviews
            'difficulty_level': 'medium',  # Track original difficulty
        }
        
        self.deck['decks'][self.topic].append(card)
        self.save_deck()
        return card
    
    def get_due_cards(self, limit: Optional[int] = None) -> List[Dict]:
        """Get cards due for review."""
        if self.topic not in self.deck['decks']:
            return []
            
        now = datetime.now()
        due_cards = []
        
        for card in self.deck['decks'][self.topic]:
            next_review = datetime.fromisoformat(card['next_review'])
            if next_review <= now:
                due_cards.append(card)
        
        # Sort by most overdue first
        due_cards.sort(key=lambda x: datetime.fromisoformat(x['next_review']))
        
        if limit:
            return due_cards[:limit]
        return due_cards
    
    def get_cards_due_within_days(self, days: int = 7) -> List[Dict]:
        """Get cards due within specified number of days."""
        if self.topic not in self.deck['decks']:
            return []
            
        now = datetime.now()
        cutoff = now + timedelta(days=days)
        upcoming_cards = []
        
        for card in self.deck['decks'][self.topic]:
            next_review = datetime.fromisoformat(card['next_review'])
            if next_review <= cutoff:
                days_until = (next_review - now).days
                card_info = card.copy()
                card_info['days_until_review'] = max(0, days_until)
                upcoming_cards.append(card_info)
        
        # Sort by review date
        upcoming_cards.sort(key=lambda x: x['days_until_review'])
        return upcoming_cards
    
    def update_card_schedule(self, card: Dict, quality: int):
        """Update card scheduling using SuperMemo-2 algorithm.
        
        Args:
            card: The flashcard to update
            quality: Rating of answer quality (0-5)
                0 - Complete blackout
                1 - Incorrect, but remembered
                2 - Incorrect, but seemed easy
                3 - Correct, but difficult
                4 - Correct
                5 - Correct and easy
        """
        if quality < 3:
            # Reset card on failure
            card['interval'] = 0
            card['repetitions'] = 0
        else:
            # Update ease factor
            card['ease_factor'] = max(1.3, card['ease_factor'] + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
            
            # Calculate next interval
            if card['repetitions'] == 0:
                card['interval'] = 1
            elif card['repetitions'] == 1:
                card['interval'] = 6
            else:
                card['interval'] = round(card['interval'] * card['ease_factor'])
            
            card['repetitions'] += 1
        
        # Update review dates
        card['last_reviewed'] = datetime.now().isoformat()
        next_review = datetime.now() + timedelta(days=card['interval'])
        card['next_review'] = next_review.isoformat()
        
        self.save_deck()
    
    def get_stats(self) -> Dict:
        """Get study statistics for this deck."""
        return {
            'total_cards': len(self.deck['decks'].get(self.topic, [])),
            'cards_due': len(self.get_due_cards()),
            **self.deck['stats']
        }
    
    def update_stats(self, correct: bool):
        """Update deck statistics."""
        self.deck['stats']['cards_studied'] += 1
        if correct:
            self.deck['stats']['correct_answers'] += 1
        self.save_deck()

def create_flashcards_from_qa(username: str, topic: str, qa_pairs: List[Dict]) -> FlashcardDeck:
    """Create flashcards from question-answer pairs."""
    deck = FlashcardDeck(username, topic)
    
    for qa in qa_pairs:
        deck.add_card(
            front=qa['question'],
            back=qa['answer'],
            subtopic=qa.get('subtopic') or None
        )
    
    return deck

def auto_create_flashcard_from_review(username: str, topic: str, question: str, 
                                    correct_answer: str, difficulty: str = "medium") -> bool:
    """Automatically create a flashcard from a review session question."""
    deck = FlashcardDeck(username, topic)
    
    # Only create flashcard if answer was correct and at medium+ difficulty
    # This ensures we're reinforcing successful understanding
    if difficulty in ["medium", "hard"]:
        card = deck.add_card(
            front=str(question),
            back=correct_answer,
            subtopic=topic
        )
        if 'difficulty_level' in card:
            card['difficulty_level'] = difficulty
            deck.save_deck()
        return True
    return False

def get_all_due_cards_for_user(username: str) -> List[Dict]:
    """Get all due cards across all topics for a user."""
    flashcards_file = Path(f'flashcards_{username}.json')
    if not flashcards_file.exists():
        return []
    
    with flashcards_file.open('r') as f:
        data = json.load(f)
    
    all_due_cards = []
    now = datetime.now()
    
    for topic, cards in data.get('decks', {}).items():
        for card in cards:
            next_review = datetime.fromisoformat(card['next_review'])
            if next_review <= now:
                card_info = card.copy()
                card_info['topic'] = topic
                card_info['days_overdue'] = (now - next_review).days
                all_due_cards.append(card_info)
    
    # Sort by most overdue first
    all_due_cards.sort(key=lambda x: x['days_overdue'], reverse=True)
    return all_due_cards

def get_spaced_repetition_schedule_for_user(username: str, days_ahead: int = 7) -> List[Dict]:
    """Get upcoming spaced repetition schedule for a user across all topics."""
    flashcards_file = Path(f'flashcards_{username}.json')
    if not flashcards_file.exists():
        return []
    
    with flashcards_file.open('r') as f:
        data = json.load(f)
    
    schedule = []
    now = datetime.now()
    cutoff = now + timedelta(days=days_ahead)
    
    for topic, cards in data.get('decks', {}).items():
        for card in cards:
            next_review = datetime.fromisoformat(card['next_review'])
            if next_review <= cutoff:
                days_until = (next_review - now).days
                schedule.append({
                    'topic': topic,
                    'subtopic': card.get('subtopic', topic),
                    'front': card['front'],
                    'days_until_review': max(0, days_until),
                    'review_date': next_review.strftime('%Y-%m-%d'),
                    'priority': 'high' if days_until <= 0 else 'medium' if days_until <= 2 else 'low',
                    'ease_factor': card.get('ease_factor', 2.5),
                    'repetitions': card.get('repetitions', 0)
                })
    
    # Sort by review date (overdue first)
    schedule.sort(key=lambda x: x['days_until_review'])
    return schedule 