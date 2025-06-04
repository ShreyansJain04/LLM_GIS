import json
from pathlib import Path
from typing import List, Dict

from memory import load_user, save_user
from domain_expert import (
    explain_concept,
    generate_example,
    generate_question,
    check_answer,
    generate_summary,
    query_domain_expert,
)

TOPICS_FILE = Path('topics.json')


def load_topics() -> dict:
    if TOPICS_FILE.exists():
        with TOPICS_FILE.open('r') as f:
            return json.load(f)
    return {}


class PlannerAgent:
    """Agent that builds plans and drives learning loops."""

    def __init__(self, username: str):
        self.username = username

    # ---- Memory helpers ----
    @property
    def profile(self) -> dict:
        return load_user(self.username)

    def save_profile(self, profile: dict) -> None:
        save_user(self.username, profile)

    # ---- Agent functions ----
    def suggest_mode(self) -> str:
        profile = self.profile
        if profile.get('weak_areas'):
            return 'review'
        return 'learn'

    def build_learning_plan(self, topic: str) -> Dict:
        topics = load_topics()

        prereqs: List[str] = []
        difficulty = "beginner"
        est_time = 20
        num_q = 5

        for _parent, children in topics.items():
            if topic in children:
                info = children[topic]
                prereqs = info.get("prerequisites", [])
                difficulty = info.get("difficulty", "beginner")
                est_time = info.get("estimated_time", 20)
                num_q = info.get("num_questions", 5)
                break

        prompt = (
            "Create a JSON learning plan for the topic '{t}'. Include fields: "
            "topic, prerequisites, estimated_time, num_questions, difficulty. "
            "Use prerequisites {p}. Difficulty hint: {d}.".format(
                t=topic, p=prereqs or [], d=difficulty
            )
        )

        plan = {
            "topic": topic,
            "prerequisites": prereqs,
            "estimated_time": est_time,
            "num_questions": num_q,
            "difficulty": difficulty,
        }

        try:
            response = query_domain_expert(prompt)
            plan.update(json.loads(response))
        except Exception:
            pass  # fall back to default plan

        return plan

    def run_learning_loop(self, topic: str) -> None:
        profile = self.profile
        plan = self.build_learning_plan(topic)
        # Ensure prerequisites mastered
        for prereq in plan['prerequisites']:
            if profile['topic_mastery'].get(prereq) != 'mastered':
                self.run_learning_loop(prereq)
                profile = self.profile
        # Teach concept
        print(explain_concept(topic))
        print(generate_example(topic))
        question = generate_question(topic)
        user_answer = input(question + "\nYour answer: ")
        correct, feedback = check_answer(question, user_answer)
        print(feedback)
        print(generate_summary(topic))
        profile['topic_mastery'][topic] = 'mastered' if correct else 'intermediate'
        self.save_profile(profile)



