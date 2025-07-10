"""Interactive Session Manager for dynamic tutoring experience."""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum

from memory import load_user, save_user, record_learning_session
from domain_expert import explain_concept, generate_example, generate_question, check_answer, query_domain_expert, _retrieve_context
from planner import PlannerAgent
from enhanced_memory import EnhancedMemorySystem


class InteractionMode(Enum):
    """Modes of interaction during a session."""
    LEARNING = "learning"
    QUESTIONING = "questioning"
    EXPLAINING = "explaining"
    TESTING = "testing"
    PAUSED = "paused"


class Command(Enum):
    """Interactive commands available during sessions."""
    HELP = "!help"
    EXPLAIN_MORE = "!explain"
    EXAMPLE = "!example"
    HINT = "!hint"
    SKIP = "!skip"
    PAUSE = "!pause"
    RESUME = "!resume"
    ASK = "!ask"
    DIFFICULTY = "!difficulty"
    PROGRESS = "!progress"
    QUIT = "!quit"


class InteractiveSession:
    """Manages interactive tutoring sessions with dynamic user interaction."""
    
    def __init__(self, username: str, topic: str):
        self.username = username
        self.topic = topic
        self.mode = InteractionMode.LEARNING
        self.session_id = datetime.now().isoformat()
        self.session_state = self._load_or_create_session()
        self.planner = PlannerAgent(username)
        self.commands_help = {
            Command.HELP: "Show available commands",
            Command.EXPLAIN_MORE: "Get more detailed explanation of current topic",
            Command.EXAMPLE: "See another example",
            Command.HINT: "Get a hint for the current question",
            Command.SKIP: "Skip current topic/question",
            Command.PAUSE: "Pause session (save progress)",
            Command.RESUME: "Resume from saved session",
            Command.ASK: "Ask a specific question",
            Command.DIFFICULTY: "Adjust difficulty level",
            Command.PROGRESS: "View learning progress",
            Command.QUIT: "End session"
        }
    
    def _load_or_create_session(self) -> Dict:
        """Load existing session or create new one."""
        sessions_file = Path(f'sessions_{self.username}.json')
        
        if sessions_file.exists():
            with sessions_file.open('r') as f:
                sessions = json.load(f)
                # Check for incomplete session
                for session in sessions.get('active_sessions', []):
                    if session['topic'] == self.topic and session['status'] == 'paused':
                        print(f"Found paused session from {session['paused_at']}")
                        resume = input("Would you like to resume? (y/n): ").lower().strip()
                        if resume == 'y':
                            return session
        
        # Create new session
        return {
            'session_id': self.session_id,
            'topic': self.topic,
            'status': 'active',
            'started_at': datetime.now().isoformat(),
            'current_subtopic_index': 0,
            'subtopics_completed': [],
            'questions_asked': [],
            'performance': [],
            'total_score': 0,
            'total_questions': 0,
            'user_questions': [],
            'difficulty_adjustments': []
        }
    
    def save_session_state(self, status: str = 'paused'):
        """Save current session state."""
        sessions_file = Path(f'sessions_{self.username}.json')
        
        sessions = {'active_sessions': []}
        if sessions_file.exists():
            with sessions_file.open('r') as f:
                sessions = json.load(f)
        
        # Update session status
        self.session_state['status'] = status
        if status == 'paused':
            self.session_state['paused_at'] = datetime.now().isoformat()
        elif status == 'completed':
            self.session_state['completed_at'] = datetime.now().isoformat()
        
        # Remove old session if exists and add updated one
        sessions['active_sessions'] = [
            s for s in sessions.get('active_sessions', []) 
            if s['session_id'] != self.session_id
        ]
        sessions['active_sessions'].append(self.session_state)
        
        with sessions_file.open('w') as f:
            json.dump(sessions, f, indent=2)
    
    def parse_command(self, user_input: str) -> Tuple[Optional[Command], str]:
        """Parse user input for commands."""
        input_lower = user_input.strip().lower()
        
        for command in Command:
            if input_lower.startswith(command.value):
                remainder = user_input[len(command.value):].strip()
                return command, remainder
        
        return None, user_input
    
    def handle_command(self, command: Command, args: str = "") -> bool:
        """Handle interactive commands. Returns True to continue, False to end."""
        if command == Command.HELP:
            self.show_help()
        
        elif command == Command.EXPLAIN_MORE:
            current_topic = self._get_current_topic()
            explanation = explain_concept(current_topic)
            print(f"\n📚 Detailed Explanation:\n{explanation}")
        
        elif command == Command.EXAMPLE:
            current_topic = self._get_current_topic()
            example = generate_example(current_topic)
            print(f"\n💡 Example:\n{example}")
        
        elif command == Command.HINT:
            if self.mode == InteractionMode.QUESTIONING:
                print("\n💭 Hint: Think about the key concepts we just covered...")
                # Could be enhanced with actual hint generation
        
        elif command == Command.SKIP:
            print("⏭️ Skipping current topic...")
            return self._move_to_next_subtopic()
        
        elif command == Command.PAUSE:
            self.save_session_state('paused')
            print("⏸️ Session paused. Your progress has been saved.")
            return False
        
        elif command == Command.ASK:
            if args:
                self._handle_user_question(args)
            else:
                question = input("What would you like to know? ")
                self._handle_user_question(question)
        
        elif command == Command.DIFFICULTY:
            self._adjust_difficulty(args)
        
        elif command == Command.PROGRESS:
            self._show_progress()
        
        elif command == Command.QUIT:
            self.save_session_state('ended')
            print("👋 Ending session. Your progress has been saved.")
            return False
        
        return True
    
    def show_help(self):
        """Display available commands."""
        print("\n📋 Available Commands:")
        for cmd, description in self.commands_help.items():
            print(f"  {cmd.value:<15} - {description}")
        print("\nYou can use these commands at any time during the session.")
    
    def _get_current_topic(self) -> str:
        """Get the current subtopic being studied."""
        if hasattr(self, 'current_subtopic'):
            return self.current_subtopic.get('name', self.topic)
        return self.topic
    
    def _handle_user_question(self, question: str):
        """Handle user's custom question."""
        print(f"\n🤔 Your question: {question}")
        
        # Get context and generate answer
        context, citations = _retrieve_context(question), []
        response = query_domain_expert(
            f"Answer this question about {self.topic}: {question}",
            context
        )
        
        print(f"📖 Answer: {response}")
        
        # Record the question
        self.session_state['user_questions'].append({
            'question': question,
            'asked_at': datetime.now().isoformat(),
            'context': self._get_current_topic()
        })
    
    def _adjust_difficulty(self, level: str):
        """Adjust session difficulty."""
        valid_levels = ['easy', 'medium', 'hard']
        if level.lower() in valid_levels:
            self.session_state['difficulty_adjustments'].append({
                'level': level,
                'adjusted_at': datetime.now().isoformat()
            })
            print(f"📊 Difficulty adjusted to: {level}")
        else:
            print(f"Please specify difficulty: {', '.join(valid_levels)}")
    
    def _show_progress(self):
        """Show current learning progress."""
        total_q = self.session_state['total_questions']
        if total_q > 0:
            score = self.session_state['total_score'] / total_q * 100
            print(f"\n📈 Progress Report:")
            print(f"  Topic: {self.topic}")
            print(f"  Questions answered: {total_q}")
            print(f"  Current score: {score:.1f}%")
            print(f"  Subtopics completed: {len(self.session_state['subtopics_completed'])}")
        else:
            print("\n📈 No questions answered yet.")
    
    def _move_to_next_subtopic(self) -> bool:
        """Move to next subtopic in the plan."""
        self.session_state['current_subtopic_index'] += 1
        return True
    
    def run_interactive_learning(self):
        """Run the main interactive learning loop."""
        print(f"\n🎓 Starting Interactive Learning Session: {self.topic}")
        print("Type !help at any time to see available commands.\n")
        
        # Build learning plan
        plan = self.planner.build_learning_plan(self.topic)
        subtopics = plan.get('subtopics', [])
        
        # Resume from saved position if applicable
        start_index = self.session_state.get('current_subtopic_index', 0)
        
        # Initialize session state if needed
        if 'difficulty' not in self.session_state:
            self.session_state['difficulty'] = 'medium'
        if 'question_types' not in self.session_state:
            self.session_state['question_types'] = ['objective', 'subjective']
        
        for i in range(start_index, len(subtopics)):
            self.session_state['current_subtopic_index'] = i
            self.current_subtopic = subtopics[i]
            subtopic_name = self.current_subtopic['name']
            
            print(f"\n{'='*50}")
            print(f"📚 Subtopic {i+1}/{len(subtopics)}: {subtopic_name}")
            print(f"{'='*50}")
            
            # Explanation phase
            self.mode = InteractionMode.EXPLAINING
            print("\n📖 Let me explain this concept...")
            explanation = explain_concept(subtopic_name)
            print(explanation)
            
            # Check for user input/commands
            user_input = input("\n[Press Enter to continue, or type a command] ")
            if user_input:
                cmd, args = self.parse_command(user_input)
                if cmd:
                    if not self.handle_command(cmd, args):
                        return
            
            # Example phase
            print("\n💡 Here's an example:")
            example = generate_example(subtopic_name)
            print(example)
            
            # Interactive Q&A phase
            self.mode = InteractionMode.QUESTIONING
            ready = False
            while not ready:
                user_input = input("\n[Ready for a question? Press Enter, or type a command] ")
                if not user_input:
                    ready = True
                else:
                    cmd, args = self.parse_command(user_input)
                    if cmd:
                        if not self.handle_command(cmd, args):
                            return
                    else:
                        ready = True
            
            # Generate and ask objective question for learning
            previous_questions = [q['text'] for q in self.session_state['questions_asked']] if self.session_state['questions_asked'] else []
            question = generate_question(
                subtopic_name,
                previous_questions,
                difficulty=self.session_state['difficulty'],
                question_type='objective'  # Always use objective questions during learning
            )
            self.session_state['questions_asked'].append(question)
            
            print(f"\n❓ Question: {question['text']}")
            print("\nOptions:")
            for i, option in enumerate(question["options"]):
                print(f"{i}. {option}")
            
            answered = False
            while not answered:
                answer = input("Enter option number (0-3): ")
                
                # Check for commands in answer
                cmd, args = self.parse_command(answer)
                if cmd:
                    if not self.handle_command(cmd, args):
                        return
                else:
                    # Process the answer
                    correct, feedback = check_answer(question, answer)
                    print(f"\n{feedback}")
                    
                    # Update session state
                    self.session_state['total_questions'] += 1
                    if correct:
                        self.session_state['total_score'] += 1
                    
                    # Record detailed performance data
                    performance_entry = {
                        'subtopic': subtopic_name,
                        'question': question["text"],
                        'answer': answer,
                        'correct': correct,
                        'question_type': question["type"],
                        'difficulty': question["difficulty"],
                        'timestamp': datetime.now().isoformat(),
                        'options': question["options"],
                        'correct_option': question["correct_option"],
                        'selected_option': int(answer) if answer.isdigit() else None,
                        'explanation': question.get("explanation", "")
                    }
                    
                    self.session_state['performance'].append(performance_entry)
                    answered = True
            
            # Add to completed subtopics
            if subtopic_name not in self.session_state['subtopics_completed']:
                self.session_state['subtopics_completed'].append(subtopic_name)
            
            # Save progress
            save_user(self.username, self.user_profile)
            
            # Show progress
            self._show_progress()
            
            # Ask if ready to continue
            if i < len(subtopics) - 1:  # Not the last subtopic
                ready = False
                while not ready:
                    user_input = input("\n[Press Enter to continue to next subtopic, or type a command] ")
                    if not user_input:
                        ready = True
                    else:
                        cmd, args = self.parse_command(user_input)
                        if cmd:
                            if not self.handle_command(cmd, args):
                                return
                        else:
                            ready = True
            elif i == len(subtopics) - 1:  # Last subtopic
                print("\n🎉 Congratulations! You've completed all subtopics!")
                
                # Optional subjective question at the end
                print("\nWould you like to answer a reflective question about what you've learned? (This won't affect your grade)")
                if input("Type 'y' for yes, any other key to skip: ").lower().strip() == 'y':
                    reflection_q = generate_question(
                        self.topic,
                        previous_questions,
                        difficulty='medium',
                        question_type='subjective'
                    )
                    print(f"\n💭 Reflection Question: {reflection_q['text']}")
                    reflection_ans = input("Your thoughts: ")
                    _, feedback = check_answer(reflection_q, reflection_ans)
                    print(f"\nThank you for sharing! {feedback}")
        
        # Session completed
        self._complete_session()
    
    def _complete_session(self):
        """Complete the learning session and save results."""
        print("\n🎉 Congratulations! You've completed the learning session!")
        
        # Calculate final score
        if self.session_state['total_questions'] > 0:
            final_score = self.session_state['total_score'] / self.session_state['total_questions']
            mastery_level = 'mastered' if final_score >= 0.8 else 'intermediate' if final_score >= 0.6 else 'beginner'
            
            print(f"\n📊 Final Results:")
            print(f"  Score: {self.session_state['total_score']}/{self.session_state['total_questions']} ({final_score:.1%})")
            print(f"  Mastery Level: {mastery_level}")
            
            # Update session state with final score
            self.session_state['final_score'] = final_score
            
            # Use enhanced memory system
            enhanced_memory = EnhancedMemorySystem(self.username)
            enhanced_memory.record_interactive_session(self.session_state)
            
            # Get and show insights
            insights = enhanced_memory.get_insights()
            
            print("\n🧠 Learning Insights:")
            print(f"  Study streak: {insights['performance_summary']['study_streak']} days")
            print(f"  Average mastery: {insights['performance_summary']['average_mastery']:.1%}")
            print(f"  {insights['learning_trajectory']}")
            
            # Show personalized recommendations
            recommendations = insights['personalized_recommendations']
            if recommendations['learning_style_adjustments']:
                print("\n💡 Personalized Tips:")
                for tip in recommendations['learning_style_adjustments'][:2]:
                    print(f"  • {tip}")
            
            if recommendations['focus_areas']:
                print("\n🎯 Priority Focus Areas:")
                for area in recommendations['focus_areas'][:3]:
                    print(f"  • {area['topic']} - {area['subtopic']}")
            
            # Show spaced repetition schedule
            if recommendations['spaced_repetition_schedule']:
                print("\n📅 Upcoming Reviews:")
                for review in recommendations['spaced_repetition_schedule'][:3]:
                    print(f"  • {review['topic']} ({review['days_until_review']} days)")
        
        # Save session as completed
        self.save_session_state('completed') 