import json
from pathlib import Path
from typing import List, Dict

from memory import load_user, save_user, record_learning_session, get_recommended_review_topics
from domain_expert import (
    explain_concept,
    generate_example,
    generate_question,
    check_answer,
    generate_summary,
    query_domain_expert,
    _retrieve_context,
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
        
        # Get recommended review topics
        recommended_topics = get_recommended_review_topics(self.username, limit=3)
        
        if recommended_topics:
            print(f"\nRecommended review topics: {', '.join(recommended_topics)}")
            return 'review'
        elif profile.get('weak_areas'):
            return 'review'
        return 'learn'

    def build_learning_plan(self, topic: str) -> Dict:
        """Build a structural learning plan without generating content."""
        topics = load_topics()

        # Get basic info from topics.json if available
        prereqs: List[str] = []
        difficulty = "beginner"
        est_time = 20
        
        for _parent, children in topics.items():
            if topic in children:
                info = children[topic]
                prereqs = info.get("prerequisites", [])
                difficulty = info.get("difficulty", "beginner")
                est_time = info.get("estimated_time", 20)
                break

        # Create a planning prompt for structure only
        prompt = f"""Create a structured learning plan for "{topic}". 
        
        Return a JSON object with this structure:
        {{
            "topic": "{topic}",
            "prerequisites": {prereqs},
            "difficulty": "{difficulty}",
            "estimated_time": {est_time},
            "subtopics": [
                {{
                    "name": "Subtopic 1 Name",
                    "description": "Brief description of what this covers",
                    "key_concepts": ["concept1", "concept2"],
                    "learning_objectives": ["objective1", "objective2"]
                }},
                {{
                    "name": "Subtopic 2 Name", 
                    "description": "Brief description of what this covers",
                    "key_concepts": ["concept3", "concept4"],
                    "learning_objectives": ["objective3", "objective4"]
                }}
            ]
        }}
        
        Focus on creating a logical progression of subtopics. Do not generate actual content."""

        # Default fallback plan structure
        plan = {
            "topic": topic,
            "prerequisites": prereqs,
            "difficulty": difficulty,
            "estimated_time": est_time,
            "subtopics": [
                {
                    "name": f"Introduction to {topic}",
                    "description": f"Basic concepts and overview",
                    "key_concepts": ["fundamentals", "terminology"],
                    "learning_objectives": ["understand basics", "know key terms"]
                }
            ]
        }

        try:
            # Use domain expert to generate plan structure
            response = query_domain_expert(prompt, temperature=0.3)  # Lower temperature for structured output
            ai_plan = json.loads(response)
            plan.update(ai_plan)
        except Exception as e:
            print(f"Warning: Could not generate AI plan structure, using fallback. Error: {e}")

        return plan

    def run_learning_loop(self, topic: str) -> None:
        profile = self.profile
        plan = self.build_learning_plan(topic)
        
        print(f"\n=== Learning Plan for {plan['topic']} ===")
        print(f"Estimated time: {plan['estimated_time']} minutes")
        print(f"Difficulty: {plan['difficulty']}")
        
        # Handle prerequisites intelligently
        prerequisites = plan.get('prerequisites', [])
        if prerequisites:
            print(f"\nThis topic typically requires: {', '.join(prerequisites)}")
            skip_prereqs = input("Do you already have this background? (y/n): ").lower().strip()
            
            if skip_prereqs != 'y':
                print("\nLet's cover the prerequisites first:")
                for prereq in prerequisites:
                    if profile['topic_mastery'].get(prereq) != 'mastered':
                        print(f"\nLearning prerequisite: {prereq}")
                        self.run_learning_loop(prereq)
                        profile = self.profile
            else:
                print("Great! Marking prerequisites as known and proceeding with the main topic.")
                # Mark prerequisites as known to avoid future redundancy
                for prereq in prerequisites:
                    if prereq not in profile['topic_mastery']:
                        profile['topic_mastery'][prereq] = 'mastered'
                self.save_profile(profile)
        
        # Work through each subtopic systematically
        subtopics = plan.get('subtopics', [])
        total_correct = 0
        total_questions = 0
        subtopics_performance = []  # Track performance for each subtopic
        
        for i, subtopic in enumerate(subtopics, 1):
            print(f"\n=== Subtopic {i}/{len(subtopics)}: {subtopic['name']} ===")
            print(f"Learning objectives: {', '.join(subtopic.get('learning_objectives', []))}")
            
            # Use domain expert for all content generation
            print("\n--- Explanation ---")
            explanation = explain_concept(subtopic['name'])
            print(explanation)
            
            # Provide example using domain expert
            print("\n--- Example ---")
            example = generate_example(subtopic['name'])
            print(example)
            
            # Generate question using domain expert
            print("\n--- Check Understanding ---")
            key_concepts = subtopic.get('key_concepts', [])
            # Pass context about what to test
            question = generate_question(
                subtopic['name'], 
                previous_questions=[],
                difficulty="medium",
                question_type="analytical"
            )
            
            user_answer = input(question + "\nYour answer: ")
            correct, feedback = check_answer(question, user_answer)
            print(feedback)
            
            # Record subtopic performance
            subtopic_score = 1 if correct else 0
            subtopics_performance.append({
                'subtopic': subtopic['name'],
                'question': question,
                'user_answer': user_answer,
                'correct': correct,
                'score': subtopic_score,
                'feedback': feedback
            })
            
            if correct:
                total_correct += 1
            total_questions += 1
            
            # Brief summary from domain expert
            summary = generate_summary(subtopic['name'], length="short")
            print(f"\n--- Summary ---\n{summary}")
            
            # Pause between subtopics
            if i < len(subtopics):
                input("\nPress Enter to continue to the next subtopic...")
        
        # Final comprehensive assessment
        print(f"\n=== Final Assessment for {topic} ===")
        # Generate a synthesis question using domain expert
        final_question = generate_question(
            topic,
            previous_questions=[p['question'] for p in subtopics_performance],
            difficulty="hard",
            question_type="synthesis"
        )
        
        user_answer = input(final_question + "\nYour comprehensive answer: ")
        correct, feedback = check_answer(final_question, user_answer)
        print(feedback)
        
        # Record final assessment performance
        final_score = 1 if correct else 0
        subtopics_performance.append({
            'subtopic': 'Final Assessment',
            'question': final_question,
            'user_answer': user_answer,
            'correct': correct,
            'score': final_score,
            'feedback': feedback
        })
        
        if correct:
            total_correct += 1
        total_questions += 1
        
        # Calculate mastery based on performance
        mastery_percentage = total_correct / total_questions if total_questions > 0 else 0
        if mastery_percentage >= 0.8:
            mastery_level = 'mastered'
        elif mastery_percentage >= 0.6:
            mastery_level = 'intermediate'
        else:
            mastery_level = 'beginner'
            
        print(f"\n=== Learning Complete ===")
        print(f"Score: {total_correct}/{total_questions} ({mastery_percentage:.1%})")
        print(f"Mastery level: {mastery_level}")
        
        # Record the complete learning session with detailed performance tracking
        record_learning_session(
            username=self.username,
            topic=topic,
            subtopics_performance=subtopics_performance,
            final_score=mastery_percentage,
            mastery_level=mastery_level
        )
        
        # Show weak areas if any were identified
        profile = self.profile  # Reload to get updated weak areas
        weak_areas = profile.get('weak_areas', [])
        if weak_areas:
            print(f"\nAreas for review: {', '.join(weak_areas[:3])}")  # Show top 3



