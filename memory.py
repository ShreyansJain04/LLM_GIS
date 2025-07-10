import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util
import fcntl
import os

# Create user data directory if it doesn't exist
USER_DATA_DIR = Path('user_data')
USER_DATA_DIR.mkdir(exist_ok=True)

def get_user_file(username: str) -> Path:
    """Get path to user's data file."""
    return USER_DATA_DIR / f"{username}.json"

def load_user(username: str) -> dict:
    """Load user data with file locking for concurrency safety."""
    user_file = get_user_file(username)
    
    # Create empty profile if file doesn't exist
    if not user_file.exists():
        return {
            'weak_areas': [],
            'topic_mastery': {},
            'history': [],
            'learning_plan': {},
            'performance_data': {},
            'last_active': datetime.now().isoformat()
        }
    
    try:
        with open(user_file, 'r') as f:
            # Get exclusive lock
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return {
                        'weak_areas': [],
                        'topic_mastery': {},
                        'history': [],
                        'learning_plan': {},
                        'performance_data': {},
                        'last_active': datetime.now().isoformat()
                    }
            finally:
                # Release lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        print(f"Error loading user data: {e}")
        return {
            'weak_areas': [],
            'topic_mastery': {},
            'history': [],
            'learning_plan': {},
            'performance_data': {},
            'last_active': datetime.now().isoformat()
        }

def save_user(username: str, profile: dict) -> None:
    """Save user data with atomic write and file locking."""
    user_file = get_user_file(username)
    temp_file = user_file.with_suffix('.tmp')
    
    # Update last active timestamp
    profile['last_active'] = datetime.now().isoformat()
    
    try:
        # Write to temporary file first
        with open(temp_file, 'w') as f:
            # Get exclusive lock
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(profile, f, indent=2)
                f.flush()
                os.fsync(f.fileno())  # Ensure data is written to disk
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # Atomic rename
        temp_file.replace(user_file)
    except Exception as e:
        print(f"Error saving user data: {e}")
        # Try to save backup
        backup_file = user_file.with_suffix('.backup')
        try:
            with open(backup_file, 'w') as f:
                json.dump(profile, f, indent=2)
            print(f"User data saved to backup file: {backup_file}")
        except Exception as backup_error:
            print(f"Failed to save backup: {backup_error}")

def record_learning_session(username: str, topic: str, subtopics_performance: List[Dict], final_score: float, mastery_level: str) -> None:
    """Record a complete learning session with detailed performance data"""
    profile = load_user(username)
    
    # Record session in history with enhanced data
    session_data = {
        'date': datetime.now().isoformat(),
        'topic': topic,
        'subtopics_performance': subtopics_performance,
        'final_score': final_score,
        'mastery_level': mastery_level,
        'session_stats': {
            'objective_questions': 0,
            'objective_correct': 0,
            'subjective_questions': 0,
            'subjective_correct': 0,
            'average_objective_score': 0,
            'average_subjective_score': 0,
            'questions_by_difficulty': {
                'easy': {'total': 0, 'correct': 0},
                'medium': {'total': 0, 'correct': 0},
                'hard': {'total': 0, 'correct': 0}
            }
        }
    }
    
    # Calculate detailed statistics
    for perf in subtopics_performance:
        question_type = perf.get('question_type', 'subjective')  # Default to subjective for backward compatibility
        difficulty = perf.get('difficulty', 'medium')  # Default to medium
        
        if question_type == 'objective':
            session_data['session_stats']['objective_questions'] += 1
            if perf['correct']:
                session_data['session_stats']['objective_correct'] += 1
        else:
            session_data['session_stats']['subjective_questions'] += 1
            if perf['correct']:
                session_data['session_stats']['subjective_correct'] += 1
        
        # Track by difficulty
        session_data['session_stats']['questions_by_difficulty'][difficulty]['total'] += 1
        if perf['correct']:
            session_data['session_stats']['questions_by_difficulty'][difficulty]['correct'] += 1
    
    # Calculate averages
    if session_data['session_stats']['objective_questions'] > 0:
        session_data['session_stats']['average_objective_score'] = (
            session_data['session_stats']['objective_correct'] / 
            session_data['session_stats']['objective_questions']
        )
    if session_data['session_stats']['subjective_questions'] > 0:
        session_data['session_stats']['average_subjective_score'] = (
            session_data['session_stats']['subjective_correct'] / 
            session_data['session_stats']['subjective_questions']
        )
    
    profile['history'].append(session_data)
    
    # Update topic mastery
    profile['topic_mastery'][topic] = mastery_level
    
    # Update detailed performance data
    if topic not in profile['performance_data']:
        profile['performance_data'][topic] = {
            'attempts': 0,
            'average_score': 0,
            'subtopic_scores': {},
            'question_type_performance': {
                'objective': {'total': 0, 'correct': 0, 'trend': []},
                'subjective': {'total': 0, 'correct': 0, 'trend': []}
            },
            'difficulty_performance': {
                'easy': {'total': 0, 'correct': 0},
                'medium': {'total': 0, 'correct': 0},
                'hard': {'total': 0, 'correct': 0}
            },
            'common_mistakes': [],
            'last_attempt': None,
            'improvement_rate': 0
        }
    
    perf_data = profile['performance_data'][topic]
    perf_data['attempts'] += 1
    perf_data['last_attempt'] = datetime.now().isoformat()
    
    # Update average score with weighted recent performance
    if perf_data['attempts'] == 1:
        perf_data['average_score'] = final_score
        perf_data['improvement_rate'] = 0
    else:
        old_avg = perf_data['average_score']
        perf_data['average_score'] = (old_avg * 0.7) + (final_score * 0.3)
        perf_data['improvement_rate'] = final_score - old_avg
    
    # Track question type performance
    for q_type in ['objective', 'subjective']:
        total = session_data['session_stats'][f'{q_type}_questions']
        correct = session_data['session_stats'][f'{q_type}_correct']
        if total > 0:
            perf_data['question_type_performance'][q_type]['total'] += total
            perf_data['question_type_performance'][q_type]['correct'] += correct
            perf_data['question_type_performance'][q_type]['trend'].append(correct / total)
            # Keep only last 10 trend points
            if len(perf_data['question_type_performance'][q_type]['trend']) > 10:
                perf_data['question_type_performance'][q_type]['trend'].pop(0)
    
    # Track difficulty performance
    for difficulty in ['easy', 'medium', 'hard']:
        stats = session_data['session_stats']['questions_by_difficulty'][difficulty]
        perf_data['difficulty_performance'][difficulty]['total'] += stats['total']
        perf_data['difficulty_performance'][difficulty]['correct'] += stats['correct']
    
    # Track subtopic performance
    for subtopic_perf in subtopics_performance:
        subtopic = subtopic_perf['subtopic']
        if subtopic not in perf_data['subtopic_scores']:
            perf_data['subtopic_scores'][subtopic] = []
        perf_data['subtopic_scores'][subtopic].append(1 if subtopic_perf['correct'] else 0)
    
    # Analyze and update weak areas
    _update_weak_areas(profile, topic, final_score, subtopics_performance)
    
    save_user(username, profile)

def _update_weak_areas(profile: dict, topic: str, final_score: float, subtopics_performance: List[Dict]) -> None:
    """Update weak areas based on performance."""
    weak_areas = set(profile.get('weak_areas', []))
    
    # Check overall topic performance
    if final_score < 0.6:  # Below intermediate level
        weak_areas.add(topic)
    elif final_score >= 0.8:  # Mastered
        weak_areas.discard(topic)
    
    # Check individual subtopics
    for perf in subtopics_performance:
        subtopic = perf['subtopic']
        if not perf['correct']:
            weak_areas.add(f"{topic} - {subtopic}")
        elif perf['correct'] and f"{topic} - {subtopic}" in weak_areas:
            weak_areas.discard(f"{topic} - {subtopic}")
    
    profile['weak_areas'] = list(weak_areas)

def get_weak_areas(username: str) -> List[str]:
    """Get list of topics/subtopics the user struggles with"""
    profile = load_user(username)
    return profile.get('weak_areas', [])

def get_performance_summary(username: str) -> Dict:
    """Get a summary of user's learning performance"""
    profile = load_user(username)
    perf_data = profile.get('performance_data', {})
    
    summary = {
        'total_topics_studied': len(perf_data),
        'weak_areas_count': len(profile.get('weak_areas', [])),
        'average_scores': {},
        'topics_mastered': 0,
        'topics_intermediate': 0,
        'topics_beginner': 0,
        'recent_improvement': 0,
        'question_type_stats': {
            'objective': {
                'total_answered': 0,
                'total_correct': 0,
                'average_score': 0
            },
            'subjective': {
                'total_answered': 0,
                'total_correct': 0,
                'average_score': 0
            }
        },
        'difficulty_stats': {
            'easy': {'total': 0, 'correct': 0, 'success_rate': 0},
            'medium': {'total': 0, 'correct': 0, 'success_rate': 0},
            'hard': {'total': 0, 'correct': 0, 'success_rate': 0}
        }
    }
    
    # Calculate recent improvement rate and collect stats
    total_improvement = 0
    topics_with_improvement = 0
    
    for topic, data in perf_data.items():
        summary['average_scores'][topic] = data['average_score']
        if data.get('improvement_rate'):
            total_improvement += data['improvement_rate']
            topics_with_improvement += 1
        
        # Aggregate question type stats
        for q_type in ['objective', 'subjective']:
            type_data = data.get('question_type_performance', {}).get(q_type, {})
            summary['question_type_stats'][q_type]['total_answered'] += type_data.get('total', 0)
            summary['question_type_stats'][q_type]['total_correct'] += type_data.get('correct', 0)
        
        # Aggregate difficulty stats
        for difficulty in ['easy', 'medium', 'hard']:
            diff_data = data.get('difficulty_performance', {}).get(difficulty, {})
            summary['difficulty_stats'][difficulty]['total'] += diff_data.get('total', 0)
            summary['difficulty_stats'][difficulty]['correct'] += diff_data.get('correct', 0)
    
    # Calculate averages and rates
    if topics_with_improvement > 0:
        summary['recent_improvement'] = total_improvement / topics_with_improvement
    
    for q_type in ['objective', 'subjective']:
        total = summary['question_type_stats'][q_type]['total_answered']
        correct = summary['question_type_stats'][q_type]['total_correct']
        if total > 0:
            summary['question_type_stats'][q_type]['average_score'] = correct / total
    
    for difficulty in ['easy', 'medium', 'hard']:
        total = summary['difficulty_stats'][difficulty]['total']
        correct = summary['difficulty_stats'][difficulty]['correct']
        if total > 0:
            summary['difficulty_stats'][difficulty]['success_rate'] = correct / total
    
    # Count mastery levels
    for topic, mastery in profile.get('topic_mastery', {}).items():
        if mastery == 'mastered':
            summary['topics_mastered'] += 1
        elif mastery == 'intermediate':
            summary['topics_intermediate'] += 1
        else:
            summary['topics_beginner'] += 1
    
    return summary

def get_recommended_review_topics(username: str, limit: int = 3) -> List[str]:
    """Get topics that need review based on performance"""
    profile = load_user(username)
    weak_areas = profile.get('weak_areas', [])
    perf_data = profile.get('performance_data', {})
    
    # Sort weak areas by performance (worst first)
    scored_weak_areas = []
    for area in weak_areas:
        # For main topics, use average score
        if area in perf_data:
            score = perf_data[area]['average_score']
            scored_weak_areas.append((area, score))
        else:
            # For subtopics, assign low score
            scored_weak_areas.append((area, 0.0))
    
    # Sort by score (ascending - worst first)
    scored_weak_areas.sort(key=lambda x: x[1])
    
    return [area for area, _ in scored_weak_areas[:limit]]

def update_progress(username: str, topic: str, mastery: str) -> None:
    """Legacy function - kept for compatibility"""
    profile = load_user(username)
    profile['topic_mastery'][topic] = mastery
    if topic in profile.get('weak_areas', []) and mastery == 'mastered':
        profile['weak_areas'].remove(topic)
    save_user(username, profile)

class DocumentProcessor:
    def __init__(self):
        self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self._emb_matrix = None
        self._all_chunks = []

    def _vector_retrieval(self, query, top_k=5):
        q_vec = self._embedder.encode(query, convert_to_tensor=True)
        sims = util.cos_sim(q_vec, self._emb_matrix)[0]
        top_idx = sims.topk(top_k).indices
        return [(self._all_chunks[i], float(sims[i])) for i in top_idx]
