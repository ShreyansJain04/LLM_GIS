import json
from pathlib import Path

DATA_FILE = Path('users.json')


def load_user(username: str) -> dict:
    data = {}
    if DATA_FILE.exists():
        with DATA_FILE.open('r') as f:
            data = json.load(f)
    return data.get(username, {
        'weak_areas': [],
        'topic_mastery': {},
        'history': [],
        'learning_plan': {}
    })


def save_user(username: str, profile: dict) -> None:
    if DATA_FILE.exists():
        with DATA_FILE.open('r') as f:
            data = json.load(f)
    else:
        data = {}
    data[username] = profile
    with DATA_FILE.open('w') as f:
        json.dump(data, f, indent=2)


def update_progress(username: str, topic: str, mastery: str) -> None:
    profile = load_user(username)
    profile['topic_mastery'][topic] = mastery
    if topic in profile.get('weak_areas', []) and mastery != 'weak':
        profile['weak_areas'].remove(topic)
    save_user(username, profile)


def get_weak_areas(username: str):
    profile = load_user(username)
    return profile.get('weak_areas', [])
