"""Generate datasets for fine-tuning LLMs on Socratic teaching methods."""

import json
from typing import List, Dict, Any
from pathlib import Path
import random

from domain_expert import query_domain_expert, retrieve_context_with_citations


class SocraticDatasetGenerator:
    """Generates training data for Socratic tutoring."""
    
    def __init__(self):
        self.topics = self._load_topics()
        self.misconception_templates = self._load_misconception_templates()
        self.dataset = {
            'socratic_dialogues': [],
            'misconception_corrections': [],
            'progressive_hints': [],
            'understanding_assessments': []
        }
    
    def _load_topics(self) -> List[Dict[str, str]]:
        """Load topics for dataset generation."""
        # Example topics - expand based on your domain
        return [
            {
                'topic': 'recursion',
                'objective': 'understand recursive functions and base cases',
                'common_misconceptions': [
                    'recursion is just a loop',
                    'recursion always causes stack overflow',
                    'recursion is always slower than iteration'
                ]
            },
            {
                'topic': 'arrays',
                'objective': 'understand array indexing and memory layout',
                'common_misconceptions': [
                    'arrays can grow dynamically',
                    'array indices start at 1',
                    'arrays and lists are the same'
                ]
            },
            {
                'topic': 'pointers',
                'objective': 'understand memory addresses and pointer arithmetic',
                'common_misconceptions': [
                    'pointers are just variables',
                    'pointer arithmetic works like regular arithmetic',
                    'null pointers are the same as zero'
                ]
            }
        ]
    
    def _load_misconception_templates(self) -> Dict[str, List[str]]:
        """Load templates for addressing misconceptions."""
        return {
            'assumption_probe': [
                "What makes you think that {misconception}?",
                "Is it always true that {misconception}?",
                "Under what conditions might {misconception} not hold?"
            ],
            'counter_example': [
                "Can you think of a case where {misconception} wouldn't be true?",
                "What would happen if we tried {scenario}?",
                "How would you explain {counter_example}?"
            ],
            'definition_clarify': [
                "What exactly do you mean by {term}?",
                "How would you define {concept} in your own words?",
                "What's the difference between {term1} and {term2}?"
            ]
        }
    
    def generate_socratic_dialogue(self, topic_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete Socratic dialogue for a topic."""
        topic = topic_info['topic']
        objective = topic_info['objective']
        
        # Generate student question variations
        student_questions = [
            f"What is {topic}?",
            f"How does {topic} work?",
            f"Can you explain {topic} to me?",
            f"I'm confused about {topic}",
            f"When should I use {topic}?"
        ]
        
        dialogue = {
            'topic': topic,
            'objective': objective,
            'initial_question': random.choice(student_questions),
            'exchanges': []
        }
        
        # Generate opening Socratic response
        opening_strategies = [
            f"Before we dive into {topic}, can you think of any real-world examples where something refers to itself?",
            f"What comes to mind when you hear the term '{topic}'?",
            f"Have you encountered any situations where you needed to repeat a process? How did you handle it?",
            f"If you had to explain {topic} to someone else, where would you start?"
        ]
        
        dialogue['exchanges'].append({
            'role': 'tutor',
            'content': random.choice(opening_strategies),
            'strategy': 'opening_probe',
            'pedagogical_intent': 'activate prior knowledge'
        })
        
        # Simulate student responses and generate follow-ups
        student_responses = [
            {
                'understanding_level': 'novice',
                'response': f"I'm not sure, maybe {topic} is like doing something over and over?",
                'shows_misconception': False
            },
            {
                'understanding_level': 'basic',
                'response': f"I think {topic} is just another way to write a loop",
                'shows_misconception': True,
                'misconception': topic_info['common_misconceptions'][0]
            },
            {
                'understanding_level': 'intermediate',
                'response': f"{topic} seems to involve calling the same function from within itself",
                'shows_misconception': False
            }
        ]
        
        for i, student_resp in enumerate(student_responses[:2]):  # Generate 2 exchanges
            dialogue['exchanges'].append({
                'role': 'student',
                'content': student_resp['response'],
                'understanding_level': student_resp['understanding_level'],
                'shows_misconception': student_resp['shows_misconception']
            })
            
            # Generate appropriate Socratic follow-up
            if student_resp['shows_misconception']:
                follow_up = self._generate_misconception_response(
                    student_resp.get('misconception', ''),
                    topic
                )
            else:
                follow_up = self._generate_progressive_question(
                    student_resp['understanding_level'],
                    topic,
                    objective
                )
            
            dialogue['exchanges'].append({
                'role': 'tutor',
                'content': follow_up['content'],
                'strategy': follow_up['strategy'],
                'pedagogical_intent': follow_up['intent']
            })
        
        return dialogue
    
    def _generate_misconception_response(self, misconception: str, topic: str) -> Dict[str, str]:
        """Generate Socratic response to address a misconception."""
        strategies = [
            {
                'content': f"That's an interesting perspective. What makes you think {topic} and loops are the same?",
                'strategy': 'assumption_probe',
                'intent': 'surface underlying assumptions'
            },
            {
                'content': f"Let's explore that idea. Can you think of something a {topic} can do that a regular loop cannot?",
                'strategy': 'contrast_exploration',
                'intent': 'highlight differences through discovery'
            },
            {
                'content': f"If {topic} were just a loop, how would you explain the call stack behavior?",
                'strategy': 'contradiction_reveal',
                'intent': 'guide to discovering contradiction'
            }
        ]
        return random.choice(strategies)
    
    def _generate_progressive_question(self, level: str, topic: str, objective: str) -> Dict[str, str]:
        """Generate progressive Socratic question based on understanding level."""
        if level == 'novice':
            strategies = [
                {
                    'content': f"Good start! Can you think of a simple example from everyday life that demonstrates {topic}?",
                    'strategy': 'concrete_example_request',
                    'intent': 'build from concrete to abstract'
                },
                {
                    'content': f"You're on the right track. What would happen if the process needed to track where it came from?",
                    'strategy': 'complexity_introduction',
                    'intent': 'introduce key concept gradually'
                }
            ]
        elif level == 'basic':
            strategies = [
                {
                    'content': f"Nice observation! Now, what do you think needs to happen for {topic} to eventually stop?",
                    'strategy': 'base_case_exploration',
                    'intent': 'guide toward essential components'
                },
                {
                    'content': f"Good thinking! How would the computer keep track of multiple calls to the same function?",
                    'strategy': 'mechanism_exploration',
                    'intent': 'explore technical understanding'
                }
            ]
        else:  # intermediate
            strategies = [
                {
                    'content': f"Excellent! Can you identify the advantages and disadvantages of using {topic}?",
                    'strategy': 'tradeoff_analysis',
                    'intent': 'develop critical evaluation skills'
                },
                {
                    'content': f"Great understanding! When would you choose {topic} over an alternative approach?",
                    'strategy': 'application_reasoning',
                    'intent': 'develop decision-making skills'
                }
            ]
        return random.choice(strategies)
    
    def generate_progressive_hints(self, problem: str, solution_steps: List[str]) -> Dict[str, Any]:
        """Generate progressive hints for problem-solving."""
        hints = {
            'problem': problem,
            'solution_steps': solution_steps,
            'hint_sequence': []
        }
        
        # Generate hints from vague to specific
        hint_levels = [
            {
                'level': 1,
                'hint': "What is the simplest case of this problem?",
                'reveals': 0.2
            },
            {
                'level': 2,
                'hint': "How can you break this problem into smaller, similar problems?",
                'reveals': 0.4
            },
            {
                'level': 3,
                'hint': f"Consider what happens when you reach the base case: {solution_steps[0]}",
                'reveals': 0.6
            },
            {
                'level': 4,
                'hint': f"Try this approach: {solution_steps[1]}",
                'reveals': 0.8
            }
        ]
        
        hints['hint_sequence'] = hint_levels
        return hints
    
    def generate_understanding_assessment(self, topic: str) -> Dict[str, Any]:
        """Generate data for assessing depth of understanding."""
        assessment = {
            'topic': topic,
            'assessment_questions': [],
            'rubric': {}
        }
        
        # Different types of assessment questions
        question_types = [
            {
                'type': 'explanation',
                'question': f"Explain {topic} in your own words",
                'evaluation_criteria': [
                    'mentions key concepts',
                    'uses appropriate terminology',
                    'provides examples',
                    'shows connections to other concepts'
                ]
            },
            {
                'type': 'application',
                'question': f"Give an example of when you would use {topic}",
                'evaluation_criteria': [
                    'identifies appropriate use case',
                    'explains why it\'s suitable',
                    'considers alternatives',
                    'discusses tradeoffs'
                ]
            },
            {
                'type': 'analysis',
                'question': f"What are the advantages and limitations of {topic}?",
                'evaluation_criteria': [
                    'identifies multiple advantages',
                    'identifies multiple limitations',
                    'provides balanced view',
                    'supports with reasoning'
                ]
            }
        ]
        
        assessment['assessment_questions'] = question_types
        
        # Rubric for evaluating responses
        assessment['rubric'] = {
            'novice': {
                'score_range': [0, 0.3],
                'indicators': ['vague understanding', 'major misconceptions', 'cannot apply']
            },
            'basic': {
                'score_range': [0.3, 0.5],
                'indicators': ['surface understanding', 'minor misconceptions', 'limited application']
            },
            'intermediate': {
                'score_range': [0.5, 0.7],
                'indicators': ['good understanding', 'mostly correct', 'can apply with guidance']
            },
            'advanced': {
                'score_range': [0.7, 0.9],
                'indicators': ['deep understanding', 'accurate', 'can apply independently']
            },
            'expert': {
                'score_range': [0.9, 1.0],
                'indicators': ['comprehensive understanding', 'teaches others', 'innovative application']
            }
        }
        
        return assessment
    
    def generate_full_dataset(self, num_examples_per_topic: int = 10) -> None:
        """Generate complete dataset for all topics."""
        for topic_info in self.topics:
            # Generate multiple dialogue variations
            for i in range(num_examples_per_topic):
                dialogue = self.generate_socratic_dialogue(topic_info)
                self.dataset['socratic_dialogues'].append(dialogue)
            
            # Generate misconception corrections
            for misconception in topic_info['common_misconceptions']:
                correction = {
                    'topic': topic_info['topic'],
                    'misconception': misconception,
                    'socratic_responses': [
                        self._generate_misconception_response(misconception, topic_info['topic'])
                        for _ in range(3)  # 3 variations
                    ]
                }
                self.dataset['misconception_corrections'].append(correction)
            
            # Generate progressive hints for common problems
            problem = f"Implement a {topic_info['topic']} solution for calculating factorial"
            solution_steps = [
                "Identify base case: factorial(0) = 1",
                "Define recursive case: factorial(n) = n * factorial(n-1)",
                "Ensure termination: n must decrease toward base case"
            ]
            hints = self.generate_progressive_hints(problem, solution_steps)
            self.dataset['progressive_hints'].append(hints)
            
            # Generate understanding assessments
            assessment = self.generate_understanding_assessment(topic_info['topic'])
            self.dataset['understanding_assessments'].append(assessment)
    
    def save_dataset(self, output_path: str = 'socratic_training_data.json'):
        """Save generated dataset to file."""
        output_file = Path(output_path)
        with output_file.open('w') as f:
            json.dump(self.dataset, f, indent=2)
        print(f"Dataset saved to {output_path}")
        print(f"Total dialogues: {len(self.dataset['socratic_dialogues'])}")
        print(f"Total misconception corrections: {len(self.dataset['misconception_corrections'])}")
        print(f"Total progressive hints: {len(self.dataset['progressive_hints'])}")
        print(f"Total assessments: {len(self.dataset['understanding_assessments'])}")
    
    def export_for_fine_tuning(self, format: str = 'jsonl') -> None:
        """Export dataset in format suitable for fine-tuning."""
        if format == 'jsonl':
            # Convert to JSONL format for fine-tuning
            output_file = Path('socratic_fine_tuning.jsonl')
            with output_file.open('w') as f:
                for dialogue in self.dataset['socratic_dialogues']:
                    # Format for instruction fine-tuning
                    for i in range(0, len(dialogue['exchanges']) - 1, 2):
                        if i + 1 < len(dialogue['exchanges']):
                            student_msg = dialogue['exchanges'][i]
                            tutor_msg = dialogue['exchanges'][i + 1]
                            
                            training_example = {
                                'instruction': f"You are a Socratic tutor teaching {dialogue['topic']}. The student says: {student_msg['content']}",
                                'input': f"Learning objective: {dialogue['objective']}",
                                'output': tutor_msg['content'],
                                'metadata': {
                                    'strategy': tutor_msg.get('strategy', ''),
                                    'intent': tutor_msg.get('pedagogical_intent', '')
                                }
                            }
                            f.write(json.dumps(training_example) + '\n')
            
            print(f"Fine-tuning dataset exported to {output_file}")


def generate_dataset_for_domain(domain: str = 'computer_science', 
                               topics: List[str] = None) -> None:
    """Generate Socratic teaching dataset for specific domain."""
    generator = SocraticDatasetGenerator()
    
    if topics:
        # Override default topics
        generator.topics = [
            {'topic': t, 'objective': f'understand {t}', 'common_misconceptions': []}
            for t in topics
        ]
    
    generator.generate_full_dataset(num_examples_per_topic=20)
    generator.save_dataset(f'socratic_{domain}_dataset.json')
    generator.export_for_fine_tuning()


if __name__ == "__main__":
    # Generate dataset
    print("Generating Socratic teaching dataset...")
    generate_dataset_for_domain(
        domain='programming',
        topics=['recursion', 'pointers', 'data structures', 'algorithms', 'memory management']
    )