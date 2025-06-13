"""Enhanced Memory System with detailed pattern tracking and analytics."""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import statistics

from memory import load_user, save_user


class LearningPatternAnalyzer:
    """Analyzes learning patterns and provides insights."""
    
    def __init__(self, username: str):
        self.username = username
        self.profile = load_user(username)
        self.analytics_file = Path(f'analytics_{username}.json')
        self.patterns = self._load_or_create_analytics()
    
    def _load_or_create_analytics(self) -> Dict:
        """Load existing analytics or create new ones."""
        if self.analytics_file.exists():
            with self.analytics_file.open('r') as f:
                return json.load(f)
        
        return {
            'learning_patterns': {
                'time_of_day_performance': defaultdict(list),
                'session_duration_patterns': [],
                'mistake_patterns': defaultdict(list),
                'improvement_velocity': defaultdict(list),
                'concept_relationships': defaultdict(set)
            },
            'personalization': {
                'preferred_learning_style': 'unknown',
                'optimal_session_length': 20,
                'best_time_of_day': 'unknown',
                'difficulty_preference': 'medium'
            },
            'detailed_weaknesses': defaultdict(lambda: {
                'error_types': defaultdict(int),
                'confusion_indicators': [],
                'required_repetitions': 0,
                'last_reviewed': None
            })
        }
    
    def save_analytics(self):
        """Save analytics to file."""
        # Convert defaultdicts to regular dicts for JSON serialization
        patterns_copy = {
            'learning_patterns': {
                'time_of_day_performance': dict(self.patterns['learning_patterns']['time_of_day_performance']),
                'session_duration_patterns': self.patterns['learning_patterns']['session_duration_patterns'],
                'mistake_patterns': dict(self.patterns['learning_patterns']['mistake_patterns']),
                'improvement_velocity': dict(self.patterns['learning_patterns']['improvement_velocity']),
                'concept_relationships': {k: list(v) for k, v in self.patterns['learning_patterns']['concept_relationships'].items()}
            },
            'personalization': self.patterns['personalization'],
            'detailed_weaknesses': dict(self.patterns['detailed_weaknesses'])
        }
        
        with self.analytics_file.open('w') as f:
            json.dump(patterns_copy, f, indent=2)
    
    def analyze_session(self, session_data: Dict):
        """Analyze a learning session for patterns."""
        start_time = datetime.fromisoformat(session_data['started_at'])
        hour_of_day = start_time.hour
        
        # Track time of day performance
        if 'final_score' in session_data:
            self.patterns['learning_patterns']['time_of_day_performance'][hour_of_day].append(
                session_data['final_score']
            )
        
        # Track session duration
        if 'completed_at' in session_data:
            end_time = datetime.fromisoformat(session_data['completed_at'])
            duration_minutes = (end_time - start_time).total_seconds() / 60
            self.patterns['learning_patterns']['session_duration_patterns'].append({
                'duration': duration_minutes,
                'performance': session_data.get('final_score', 0),
                'topic': session_data['topic']
            })
        
        # Analyze mistakes
        for perf in session_data.get('performance', []):
            if not perf['correct']:
                self._analyze_mistake(
                    topic=session_data['topic'],
                    subtopic=perf['subtopic'],
                    question=perf['question'],
                    wrong_answer=perf['answer']
                )
    
    def _analyze_mistake(self, topic: str, subtopic: str, question: str, wrong_answer: str):
        """Analyze a specific mistake for patterns."""
        mistake_key = f"{topic}::{subtopic}"
        
        # Classify error type
        error_type = self._classify_error(question, wrong_answer)
        self.patterns['detailed_weaknesses'][mistake_key]['error_types'][error_type] += 1
        
        # Track confusion indicators
        confusion_indicators = self._detect_confusion(wrong_answer)
        self.patterns['detailed_weaknesses'][mistake_key]['confusion_indicators'].extend(confusion_indicators)
        
        # Update required repetitions
        self.patterns['detailed_weaknesses'][mistake_key]['required_repetitions'] += 1
        self.patterns['detailed_weaknesses'][mistake_key]['last_reviewed'] = datetime.now().isoformat()
    
    def _classify_error(self, question: str, answer: str) -> str:
        """Classify the type of error made."""
        answer_lower = answer.lower().strip()
        
        # Simple classification heuristics
        if len(answer_lower) < 5:
            return 'incomplete_answer'
        elif answer_lower in ['i dont know', 'idk', 'no idea', '?', 'n', 'j', 'h']:
            return 'no_attempt'
        elif any(word in answer_lower for word in ['maybe', 'think', 'guess', 'probably']):
            return 'uncertain'
        elif len(answer.split()) < 3:
            return 'too_brief'
        else:
            return 'conceptual_error'
    
    def _detect_confusion(self, answer: str) -> List[str]:
        """Detect confusion indicators in answers."""
        indicators = []
        answer_lower = answer.lower()
        
        confusion_phrases = {
            'uncertainty': ['i think', 'maybe', 'not sure', 'possibly', 'might be'],
            'lack_of_knowledge': ['dont know', 'no idea', 'idk', 'forgotten'],
            'partial_understanding': ['sort of', 'kind of', 'partially', 'somewhat']
        }
        
        for category, phrases in confusion_phrases.items():
            if any(phrase in answer_lower for phrase in phrases):
                indicators.append(category)
        
        return indicators
    
    def get_personalized_recommendations(self) -> Dict:
        """Get personalized learning recommendations."""
        recommendations = {
            'optimal_study_time': self._calculate_optimal_time(),
            'suggested_session_length': self._calculate_optimal_session_length(),
            'focus_areas': self._identify_focus_areas(),
            'learning_style_adjustments': self._suggest_style_adjustments(),
            'spaced_repetition_schedule': self._generate_repetition_schedule()
        }
        
        return recommendations
    
    def _calculate_optimal_time(self) -> str:
        """Calculate the best time of day for learning."""
        time_performance = self.patterns['learning_patterns']['time_of_day_performance']
        
        if not time_performance:
            return "No data yet - try different times to find your optimal learning window"
        
        # Calculate average performance by hour
        hour_averages = {}
        for hour, scores in time_performance.items():
            if scores:
                hour_averages[hour] = statistics.mean(scores)
        
        if hour_averages:
            best_hour = max(hour_averages, key=hour_averages.get)
            
            # Convert to time range
            if best_hour < 12:
                period = "morning"
            elif best_hour < 17:
                period = "afternoon"
            else:
                period = "evening"
            
            return f"{best_hour}:00-{(best_hour+1)%24}:00 ({period})"
        
        return "Insufficient data"
    
    def _calculate_optimal_session_length(self) -> int:
        """Calculate optimal session length based on performance."""
        duration_data = self.patterns['learning_patterns']['session_duration_patterns']
        
        if len(duration_data) < 3:
            return 20  # Default
        
        # Group by duration ranges and calculate average performance
        duration_performance = defaultdict(list)
        for session in duration_data:
            duration_range = int(session['duration'] // 10) * 10  # Round to nearest 10
            duration_performance[duration_range].append(session['performance'])
        
        # Find duration with best average performance
        best_duration = 20
        best_performance = 0
        
        for duration, performances in duration_performance.items():
            avg_performance = statistics.mean(performances)
            if avg_performance > best_performance:
                best_performance = avg_performance
                best_duration = duration
        
        return best_duration
    
    def _identify_focus_areas(self) -> List[Dict]:
        """Identify areas that need focus based on detailed analysis."""
        focus_areas = []
        
        for topic_subtopic, data in self.patterns['detailed_weaknesses'].items():
            if data['required_repetitions'] > 0:
                topic, subtopic = topic_subtopic.split('::', 1)
                
                # Calculate priority score
                priority_score = (
                    data['required_repetitions'] * 2 +
                    sum(data['error_types'].values()) +
                    len(data['confusion_indicators'])
                )
                
                focus_areas.append({
                    'topic': topic,
                    'subtopic': subtopic,
                    'priority_score': priority_score,
                    'main_error_type': max(data['error_types'], key=data['error_types'].get) if data['error_types'] else 'unknown',
                    'repetitions_needed': data['required_repetitions'],
                    'last_reviewed': data['last_reviewed']
                })
        
        # Sort by priority score
        focus_areas.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return focus_areas[:5]  # Top 5 focus areas
    
    def _suggest_style_adjustments(self) -> List[str]:
        """Suggest learning style adjustments based on patterns."""
        suggestions = []
        
        # Analyze error patterns
        all_errors = defaultdict(int)
        for data in self.patterns['detailed_weaknesses'].values():
            for error_type, count in data['error_types'].items():
                all_errors[error_type] += count
        
        if all_errors:
            most_common_error = max(all_errors, key=all_errors.get)
            
            if most_common_error == 'incomplete_answer':
                suggestions.append("Try to provide more detailed answers - break down your thoughts step by step")
            elif most_common_error == 'no_attempt':
                suggestions.append("Don't give up! Use the !hint command when stuck")
            elif most_common_error == 'uncertain':
                suggestions.append("Build confidence by reviewing fundamentals - use !explain for clarification")
            elif most_common_error == 'too_brief':
                suggestions.append("Expand your answers with examples and explanations")
            elif most_common_error == 'conceptual_error':
                suggestions.append("Focus on understanding core concepts before moving to applications")
        
        # Analyze session patterns
        if self.patterns['learning_patterns']['session_duration_patterns']:
            avg_duration = statistics.mean([s['duration'] for s in self.patterns['learning_patterns']['session_duration_patterns']])
            if avg_duration < 10:
                suggestions.append("Your sessions are very short - try longer, focused study periods")
            elif avg_duration > 60:
                suggestions.append("Consider shorter, more frequent sessions to maintain focus")
        
        return suggestions
    
    def _generate_repetition_schedule(self) -> List[Dict]:
        """Generate a spaced repetition schedule for weak areas."""
        schedule = []
        today = datetime.now()
        
        # Spaced repetition intervals (in days)
        intervals = [1, 3, 7, 14, 30]
        
        for topic_subtopic, data in self.patterns['detailed_weaknesses'].items():
            if data['required_repetitions'] > 0:
                topic, subtopic = topic_subtopic.split('::', 1)
                
                # Calculate next review date based on last review
                if data['last_reviewed']:
                    last_review = datetime.fromisoformat(data['last_reviewed'])
                    days_since_review = (today - last_review).days
                    
                    # Find appropriate interval
                    next_interval = 1
                    for interval in intervals:
                        if days_since_review < interval:
                            next_interval = interval
                            break
                    
                    next_review_date = last_review + timedelta(days=next_interval)
                else:
                    next_review_date = today + timedelta(days=1)
                
                # Only include if review is due soon
                if (next_review_date - today).days <= 7:
                    schedule.append({
                        'topic': topic,
                        'subtopic': subtopic,
                        'review_date': next_review_date.strftime('%Y-%m-%d'),
                        'days_until_review': (next_review_date - today).days,
                        'priority': 'high' if (next_review_date - today).days <= 1 else 'medium'
                    })
        
        # Sort by review date
        schedule.sort(key=lambda x: x['days_until_review'])
        
        return schedule[:7]  # Next 7 reviews


class EnhancedMemorySystem:
    """Enhanced memory system with detailed tracking and analytics."""
    
    def __init__(self, username: str):
        self.username = username
        self.analyzer = LearningPatternAnalyzer(username)
    
    def record_interactive_session(self, session_data: Dict):
        """Record an interactive session with detailed analytics."""
        # Analyze the session
        self.analyzer.analyze_session(session_data)
        self.analyzer.save_analytics()
        
        # Also update the regular memory system
        if 'performance' in session_data and session_data['performance']:
            from memory import record_learning_session
            
            subtopics_performance = [
                {
                    'subtopic': perf['subtopic'],
                    'question': perf['question'],
                    'user_answer': perf['answer'],
                    'correct': perf['correct'],
                    'score': 1 if perf['correct'] else 0,
                    'feedback': ''
                }
                for perf in session_data['performance']
            ]
            
            final_score = session_data.get('final_score', 0)
            mastery_level = 'mastered' if final_score >= 0.8 else 'intermediate' if final_score >= 0.6 else 'beginner'
            
            record_learning_session(
                username=self.username,
                topic=session_data['topic'],
                subtopics_performance=subtopics_performance,
                final_score=final_score,
                mastery_level=mastery_level
            )
    
    def get_insights(self) -> Dict:
        """Get comprehensive learning insights."""
        recommendations = self.analyzer.get_personalized_recommendations()
        profile = load_user(self.username)
        
        insights = {
            'performance_summary': {
                'topics_studied': len(profile.get('topic_mastery', {})),
                'average_mastery': self._calculate_average_mastery(profile),
                'weak_areas_count': len(profile.get('weak_areas', [])),
                'study_streak': self._calculate_study_streak(profile)
            },
            'personalized_recommendations': recommendations,
            'learning_trajectory': self._analyze_trajectory(profile)
        }
        
        return insights
    
    def _calculate_average_mastery(self, profile: Dict) -> float:
        """Calculate average mastery level."""
        mastery_scores = {
            'mastered': 1.0,
            'intermediate': 0.6,
            'beginner': 0.3
        }
        
        masteries = profile.get('topic_mastery', {}).values()
        if not masteries:
            return 0.0
        
        total_score = sum(mastery_scores.get(m, 0) for m in masteries)
        return total_score / len(masteries)
    
    def _calculate_study_streak(self, profile: Dict) -> int:
        """Calculate current study streak in days."""
        history = profile.get('history', [])
        if not history:
            return 0
        
        # Sort by date
        sorted_history = sorted(history, key=lambda x: x['date'], reverse=True)
        
        streak = 0
        last_date = None
        today = datetime.now().date()
        
        for session in sorted_history:
            session_date = datetime.fromisoformat(session['date']).date()
            
            if last_date is None:
                # First session
                if (today - session_date).days <= 1:
                    streak = 1
                    last_date = session_date
                else:
                    break
            else:
                # Check if consecutive
                if (last_date - session_date).days == 1:
                    streak += 1
                    last_date = session_date
                else:
                    break
        
        return streak
    
    def _analyze_trajectory(self, profile: Dict) -> str:
        """Analyze learning trajectory."""
        history = profile.get('history', [])
        if len(history) < 3:
            return "Not enough data to determine trajectory"
        
        # Get recent scores
        recent_scores = [h.get('final_score', 0) for h in history[-5:]]
        
        if len(recent_scores) >= 2:
            # Simple trend analysis
            first_half = statistics.mean(recent_scores[:len(recent_scores)//2])
            second_half = statistics.mean(recent_scores[len(recent_scores)//2:])
            
            if second_half > first_half + 0.1:
                return "Improving! Your recent performance shows upward trend"
            elif second_half < first_half - 0.1:
                return "Declining - consider reviewing fundamentals"
            else:
                return "Stable performance - challenge yourself with harder topics"
        
        return "Continue learning to establish trajectory" 