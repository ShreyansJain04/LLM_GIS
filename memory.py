import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util

DATA_FILE = Path('users.json')


def load_user(username: str) -> dict:
    data = {}
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open('r') as f:
                content = f.read().strip()
                if content:  # Check if file has content
                    data = json.loads(content)
                else:
                    # File is empty, initialize with empty dict
                    data = {}
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: users.json file is corrupted. Creating new file. Error: {e}")
            data = {}
        except Exception as e:
            print(f"Warning: Error reading users.json. Creating new file. Error: {e}")
            data = {}
    
    return data.get(username, {
        'weak_areas': [],
        'topic_mastery': {},
        'history': [],
        'learning_plan': {},
        'performance_data': {}  # New: detailed performance tracking
    })


def save_user(username: str, profile: dict) -> None:
    try:
        # Load existing data
        if DATA_FILE.exists():
            try:
                with DATA_FILE.open('r') as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                    else:
                        data = {}
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Warning: Existing users.json corrupted. Starting fresh. Error: {e}")
                data = {}
        else:
            data = {}
        
        # Update user data
        data[username] = profile
        
        # Write to temporary file first, then rename (atomic operation)
        temp_file = DATA_FILE.with_suffix('.tmp')
        with temp_file.open('w') as f:
            json.dump(data, f, indent=2)
        
        # Atomic rename (on most systems)
        temp_file.replace(DATA_FILE)
        
    except Exception as e:
        print(f"Error saving user data: {e}")
        # Try to save just this user's data as backup
        backup_file = Path(f'user_backup_{username}.json')
        try:
            with backup_file.open('w') as f:
                json.dump({username: profile}, f, indent=2)
            print(f"User data saved to backup file: {backup_file}")
        except Exception as backup_error:
            print(f"Failed to save backup: {backup_error}")


def record_learning_session(username: str, topic: str, subtopics_performance: List[Dict], final_score: float, mastery_level: str) -> None:
    """Record a complete learning session with detailed performance data"""
    profile = load_user(username)
    
    # Record session in history
    session_data = {
        'date': datetime.now().isoformat(),
        'topic': topic,
        'subtopics_performance': subtopics_performance,
        'final_score': final_score,
        'mastery_level': mastery_level
    }
    profile['history'].append(session_data)
    
    # Update topic mastery
    profile['topic_mastery'][topic] = mastery_level
    
    # Update detailed performance data
    if topic not in profile['performance_data']:
        profile['performance_data'][topic] = {
            'attempts': 0,
            'average_score': 0,
            'subtopic_scores': {},
            'common_mistakes': []
        }
    
    perf_data = profile['performance_data'][topic]
    perf_data['attempts'] += 1
    
    # Update average score
    if perf_data['attempts'] == 1:
        perf_data['average_score'] = final_score
    else:
        perf_data['average_score'] = (perf_data['average_score'] * (perf_data['attempts'] - 1) + final_score) / perf_data['attempts']
    
    # Track subtopic performance
    for subtopic_perf in subtopics_performance:
        subtopic = subtopic_perf['subtopic']
        score = subtopic_perf['score']
        if subtopic not in perf_data['subtopic_scores']:
            perf_data['subtopic_scores'][subtopic] = []
        perf_data['subtopic_scores'][subtopic].append(score)
    
    # Analyze and update weak areas
    _update_weak_areas(profile, topic, final_score, subtopics_performance)
    
    save_user(username, profile)


def _update_weak_areas(profile: dict, topic: str, final_score: float, subtopics_performance: List[Dict]) -> None:
    """Analyze performance and update weak areas"""
    weak_areas = set(profile.get('weak_areas', []))
    
    # Consider topic weak if final score < 60%
    if final_score < 0.6:
        weak_areas.add(topic)
        print(f"Added '{topic}' to weak areas (score: {final_score:.1%})")
    else:
        # Remove from weak areas if performance improved
        if topic in weak_areas:
            weak_areas.discard(topic)
            print(f"Removed '{topic}' from weak areas (improved to: {final_score:.1%})")
    
    # Check individual subtopics for weaknesses
    for subtopic_perf in subtopics_performance:
        if subtopic_perf['score'] == 0:  # Got subtopic question wrong
            subtopic = subtopic_perf['subtopic']
            weak_areas.add(f"{topic} - {subtopic}")
            print(f"Added '{topic} - {subtopic}' to weak areas (incorrect answer)")
    
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
        'topics_beginner': 0
    }
    
    for topic, data in perf_data.items():
        summary['average_scores'][topic] = data['average_score']
    
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
