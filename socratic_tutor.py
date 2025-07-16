"""Socratic Tutoring Module - Implements guided discovery learning through Socratic questioning."""

from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import random
from datetime import datetime

from domain_expert import query_domain_expert, retrieve_context_with_citations
from enhanced_memory import LearningPatternAnalyzer


class SocraticStrategy(Enum):
    """Types of Socratic questioning strategies."""
    CLARIFICATION = "clarification"
    ASSUMPTION_PROBE = "assumption_probe"
    EVIDENCE_REQUEST = "evidence_request"
    PERSPECTIVE_SHIFT = "perspective_shift"
    IMPLICATION_EXPLORE = "implication_explore"
    QUESTION_THE_QUESTION = "question_the_question"
    EXAMPLE_REQUEST = "example_request"
    ANALOGY_EXPLORE = "analogy_explore"


class StudentUnderstandingLevel(Enum):
    """Levels of student understanding."""
    NOVICE = 0
    BASIC = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4


class SocraticDialogueManager:
    """Manages Socratic teaching interactions and dialogue flow."""
    
    def __init__(self, username: str):
        self.username = username
        self.dialogue_history: List[Dict] = []
        self.current_topic = None
        self.learning_objective = None
        self.pattern_analyzer = LearningPatternAnalyzer(username)
        
        # Strategy templates for different questioning approaches
        self.strategy_templates = {
            SocraticStrategy.CLARIFICATION: [
                "What do you mean when you say '{concept}'?",
                "Can you give me an example of {concept}?",
                "How does {concept} relate to what we discussed earlier?",
                "What is the main point you're trying to make about {concept}?"
            ],
            SocraticStrategy.ASSUMPTION_PROBE: [
                "What assumptions are you making when you say that?",
                "What could we assume instead?",
                "Do you think that assumption always holds true?",
                "How can you verify or disprove that assumption?"
            ],
            SocraticStrategy.EVIDENCE_REQUEST: [
                "What evidence supports your answer?",
                "How might we test if that's true?",
                "Can you think of a case where that wouldn't apply?",
                "What observations led you to that conclusion?"
            ],
            SocraticStrategy.PERSPECTIVE_SHIFT: [
                "How might someone else view this differently?",
                "What if we looked at this from the perspective of {alternative}?",
                "Is there another way to approach this problem?",
                "What are the strengths and weaknesses of that viewpoint?"
            ],
            SocraticStrategy.IMPLICATION_EXPLORE: [
                "What follows from what you just said?",
                "What are the implications of that approach?",
                "How does this affect our understanding of {related_concept}?",
                "What would happen if we extended this idea further?"
            ],
            SocraticStrategy.QUESTION_THE_QUESTION: [
                "Why do you think this question is important?",
                "What does this question assume?",
                "Is there a better question we should be asking?",
                "How does this question relate to our learning goal?"
            ],
            SocraticStrategy.EXAMPLE_REQUEST: [
                "Can you think of a real-world example where this applies?",
                "How would you use this concept in practice?",
                "Can you create a simple scenario that demonstrates this?",
                "What's the simplest example that shows this principle?"
            ],
            SocraticStrategy.ANALOGY_EXPLORE: [
                "What is this similar to that you already understand?",
                "Can you think of an analogy from everyday life?",
                "How is this like {familiar_concept}? How is it different?",
                "If you had to explain this to a child, what comparison would you use?"
            ]
        }
    
    def analyze_student_response(self, response: str) -> Dict[str, Any]:
        """Analyze student response for understanding level and misconceptions."""
        # This would integrate with a more sophisticated NLP model in production
        analysis = {
            'understanding_level': self._estimate_understanding_level(response),
            'key_concepts_mentioned': self._extract_concepts(response),
            'potential_misconceptions': self._detect_misconceptions(response),
            'confidence_indicators': self._analyze_confidence(response),
            'reasoning_quality': self._assess_reasoning(response)
        }
        return analysis
    
    def _estimate_understanding_level(self, response: str) -> StudentUnderstandingLevel:
        """Estimate student's understanding level from their response."""
        # Simplified heuristic - in production, use ML model
        response_lower = response.lower()
        
        # Indicators of different levels
        expert_indicators = ['because', 'therefore', 'implies', 'demonstrates', 'proves']
        advanced_indicators = ['relates to', 'similar to', 'differs from', 'depends on']
        intermediate_indicators = ['think', 'maybe', 'probably', 'seems like']
        basic_indicators = ['don\'t know', 'confused', 'not sure', 'guess']
        
        if any(ind in response_lower for ind in expert_indicators) and len(response) > 100:
            return StudentUnderstandingLevel.EXPERT
        elif any(ind in response_lower for ind in advanced_indicators) and len(response) > 50:
            return StudentUnderstandingLevel.ADVANCED
        elif any(ind in response_lower for ind in intermediate_indicators):
            return StudentUnderstandingLevel.INTERMEDIATE
        elif any(ind in response_lower for ind in basic_indicators):
            return StudentUnderstandingLevel.BASIC
        else:
            return StudentUnderstandingLevel.NOVICE
    
    def _extract_concepts(self, response: str) -> List[str]:
        """Extract key concepts mentioned in the response."""
        # Simplified extraction - in production, use NER
        # For now, extract capitalized words and technical terms
        words = response.split()
        concepts = []
        for word in words:
            if word[0].isupper() and len(word) > 3:
                concepts.append(word.strip('.,!?'))
        return list(set(concepts))
    
    def _detect_misconceptions(self, response: str) -> List[str]:
        """Detect potential misconceptions in student response."""
        misconceptions = []
        response_lower = response.lower()
        
        # Common misconception patterns (domain-specific in production)
        misconception_patterns = {
            'recursion is just a loop': 'recursion.*loop|loop.*recursion',
            'arrays and lists are the same': 'array.*same.*list|list.*same.*array',
            'correlation implies causation': 'correlation.*caus|correlat.*means'
        }
        
        import re
        for misconception, pattern in misconception_patterns.items():
            if re.search(pattern, response_lower):
                misconceptions.append(misconception)
        
        return misconceptions
    
    def _analyze_confidence(self, response: str) -> Dict[str, float]:
        """Analyze confidence indicators in response."""
        response_lower = response.lower()
        
        high_confidence_words = ['definitely', 'certainly', 'obviously', 'clearly']
        medium_confidence_words = ['think', 'believe', 'seems', 'probably']
        low_confidence_words = ['maybe', 'possibly', 'might', 'could be', 'not sure']
        
        confidence_score = 0.5  # neutral
        
        for word in high_confidence_words:
            if word in response_lower:
                confidence_score += 0.1
        
        for word in low_confidence_words:
            if word in response_lower:
                confidence_score -= 0.1
        
        return {
            'confidence_score': max(0, min(1, confidence_score)),
            'uses_hedging': any(word in response_lower for word in low_confidence_words)
        }
    
    def _assess_reasoning(self, response: str) -> float:
        """Assess quality of reasoning in response."""
        reasoning_indicators = [
            'because', 'therefore', 'since', 'as a result',
            'this means', 'which shows', 'demonstrates', 'implies'
        ]
        
        response_lower = response.lower()
        reasoning_score = 0.0
        
        for indicator in reasoning_indicators:
            if indicator in response_lower:
                reasoning_score += 0.2
        
        # Check for structured thinking
        if any(marker in response for marker in ['First,', 'Second,', 'Finally,']):
            reasoning_score += 0.3
        
        # Length bonus for detailed responses
        if len(response) > 100:
            reasoning_score += 0.2
        
        return min(1.0, reasoning_score)
    
    def select_strategy(self, 
                       student_response: str,
                       analysis: Dict[str, Any],
                       dialogue_context: List[Dict]) -> SocraticStrategy:
        """Select appropriate Socratic strategy based on student response and context."""
        
        understanding_level = analysis['understanding_level']
        misconceptions = analysis['potential_misconceptions']
        confidence = analysis['confidence_indicators']['confidence_score']
        
        # Strategy selection logic
        if misconceptions:
            # Address misconceptions first
            return SocraticStrategy.ASSUMPTION_PROBE
        
        elif understanding_level == StudentUnderstandingLevel.NOVICE:
            # Start with concrete examples
            return SocraticStrategy.EXAMPLE_REQUEST
        
        elif understanding_level == StudentUnderstandingLevel.BASIC:
            # Build connections to known concepts
            return SocraticStrategy.ANALOGY_EXPLORE
        
        elif confidence > 0.8 and understanding_level.value < 3:
            # High confidence but limited understanding - probe assumptions
            return SocraticStrategy.EVIDENCE_REQUEST
        
        elif understanding_level == StudentUnderstandingLevel.ADVANCED:
            # Explore deeper implications
            return SocraticStrategy.IMPLICATION_EXPLORE
        
        else:
            # Default to clarification
            return SocraticStrategy.CLARIFICATION
    
    def generate_socratic_question(self,
                                 strategy: SocraticStrategy,
                                 context: Dict[str, Any]) -> str:
        """Generate a Socratic question based on selected strategy."""
        
        # Get template questions for the strategy
        templates = self.strategy_templates[strategy]
        template = random.choice(templates)
        
        # Fill in template with context
        question = template.format(
            concept=context.get('current_concept', 'this'),
            related_concept=context.get('related_concept', 'what we learned'),
            alternative=context.get('alternative_view', 'another perspective'),
            familiar_concept=context.get('familiar_concept', 'something familiar')
        )
        
        return question
    
    def generate_socratic_response(self,
                                 student_input: str,
                                 learning_objective: str,
                                 current_topic: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a complete Socratic response to student input."""
        
        # Analyze student response
        analysis = self.analyze_student_response(student_input)
        
        # Add to dialogue history
        self.dialogue_history.append({
            'timestamp': datetime.now().isoformat(),
            'student': student_input,
            'analysis': analysis
        })
        
        # Select strategy
        strategy = self.select_strategy(student_input, analysis, self.dialogue_history)
        
        # Prepare context for question generation
        context, citations = retrieve_context_with_citations(current_topic)
        
        question_context = {
            'current_concept': current_topic,
            'related_concept': self._find_related_concept(current_topic),
            'familiar_concept': self._find_familiar_analogy(current_topic),
            'alternative_view': 'a different approach'
        }
        
        # Generate Socratic question
        socratic_question = self.generate_socratic_question(strategy, question_context)
        
        # Use LLM to enhance and personalize the question
        enhanced_prompt = f"""
        You are a Socratic tutor guiding a student to understand: {learning_objective}
        
        Current topic: {current_topic}
        Student said: "{student_input}"
        Student understanding level: {analysis['understanding_level'].name}
        Detected misconceptions: {analysis['potential_misconceptions']}
        
        Base Socratic question: {socratic_question}
        
        Enhance this Socratic question to:
        1. Be more specific to the student's response
        2. Guide them toward discovering the key insight
        3. Build on what they already seem to understand
        4. Address any misconceptions indirectly
        
        Keep the question open-ended and thought-provoking.
        Do not give away the answer.
        """
        
        enhanced_question = query_domain_expert(enhanced_prompt, context, citations)
        
        # Record the tutor's response
        self.dialogue_history.append({
            'timestamp': datetime.now().isoformat(),
            'tutor': enhanced_question,
            'strategy': strategy.value,
            'analysis_summary': {
                'understanding': analysis['understanding_level'].name,
                'misconceptions': analysis['potential_misconceptions']
            }
        })
        
        return enhanced_question, {
            'strategy_used': strategy.value,
            'student_analysis': analysis,
            'dialogue_length': len(self.dialogue_history)
        }
    
    def _find_related_concept(self, topic: str) -> str:
        """Find a related concept from the learning history."""
        # In production, use knowledge graph or curriculum mapping
        related_concepts = {
            'recursion': 'iteration',
            'arrays': 'lists',
            'functions': 'procedures',
            'variables': 'memory'
        }
        return related_concepts.get(topic.lower(), 'previous concepts')
    
    def _find_familiar_analogy(self, topic: str) -> str:
        """Find familiar real-world analogy for the concept."""
        analogies = {
            'recursion': 'Russian dolls',
            'arrays': 'parking spaces',
            'functions': 'recipes',
            'variables': 'labeled boxes'
        }
        return analogies.get(topic.lower(), 'everyday objects')
    
    def should_provide_direct_answer(self) -> bool:
        """Determine if it's time to provide a direct answer."""
        # Provide direct answer if:
        # 1. Student has been stuck for too long (>5 exchanges)
        # 2. Student explicitly asks for the answer
        # 3. Understanding level hasn't improved after multiple attempts
        
        if len(self.dialogue_history) > 10:
            return True
        
        # Check if understanding is improving
        if len(self.dialogue_history) >= 4:
            recent_levels = [
                exchange.get('analysis', {}).get('understanding_level', StudentUnderstandingLevel.NOVICE)
                for exchange in self.dialogue_history[-4:]
                if 'analysis' in exchange
            ]
            if all(level.value <= StudentUnderstandingLevel.BASIC.value for level in recent_levels):
                return True
        
        return False
    
    def generate_summary_and_reinforcement(self) -> str:
        """Generate a summary of the Socratic dialogue and reinforce learning."""
        topic = self.current_topic or "the concept"
        
        prompt = f"""
        Based on this Socratic dialogue about {topic}, create a brief summary that:
        1. Highlights the key insights the student discovered
        2. Reinforces correct understanding
        3. Gently corrects any remaining misconceptions
        4. Provides a clear, concise explanation of the concept
        5. Suggests next steps for deeper learning
        
        Dialogue history:
        {self._format_dialogue_history()}
        
        Make the summary encouraging and focused on what the student learned through discovery.
        """
        
        context, citations = retrieve_context_with_citations(topic)
        return query_domain_expert(prompt, context, citations)
    
    def _format_dialogue_history(self) -> str:
        """Format dialogue history for prompt."""
        formatted = []
        for exchange in self.dialogue_history[-10:]:  # Last 10 exchanges
            if 'student' in exchange:
                formatted.append(f"Student: {exchange['student']}")
            elif 'tutor' in exchange:
                formatted.append(f"Tutor: {exchange['tutor']}")
        return "\n".join(formatted)


class SocraticTutor:
    """Main interface for Socratic tutoring functionality."""
    
    def __init__(self, username: str):
        self.username = username
        self.dialogue_manager = SocraticDialogueManager(username)
        self.session_active = False
        self.current_topic = None
        self.learning_objective = None
    
    def start_socratic_session(self, topic: str, learning_objective: str):
        """Start a new Socratic tutoring session."""
        self.session_active = True
        self.current_topic = topic
        self.learning_objective = learning_objective
        self.dialogue_manager.current_topic = topic
        self.dialogue_manager.learning_objective = learning_objective
        
        # Generate opening question
        opening_prompt = f"""
        Create an engaging opening question to start a Socratic dialogue about: {topic}
        
        The question should:
        1. Be open-ended and thought-provoking
        2. Connect to something familiar or concrete
        3. Encourage the student to think about what they already know
        4. Set up the path toward understanding: {learning_objective}
        
        Do not explain the concept. Just ask a question that starts the discovery process.
        """
        
        context, citations = retrieve_context_with_citations(topic)
        opening_question = query_domain_expert(opening_prompt, context, citations)
        
        return opening_question
    
    def respond_to_student(self, student_input: str) -> Dict[str, Any]:
        """Process student input and generate Socratic response."""
        if not self.session_active:
            return {
                'response': "Please start a Socratic session first.",
                'session_active': False
            }
        
        # Check if we should switch to direct teaching
        if self.dialogue_manager.should_provide_direct_answer():
            summary = self.dialogue_manager.generate_summary_and_reinforcement()
            return {
                'response': summary,
                'mode': 'direct_teaching',
                'session_complete': True,
                'metadata': {
                    'total_exchanges': len(self.dialogue_manager.dialogue_history)
                }
            }
        
        # Generate Socratic response
        response, metadata = self.dialogue_manager.generate_socratic_response(
            student_input,
            self.learning_objective,
            self.current_topic
        )
        
        return {
            'response': response,
            'mode': 'socratic',
            'session_active': True,
            'metadata': metadata
        }
    
    def end_session(self) -> Dict[str, Any]:
        """End the current Socratic session and provide summary."""
        if not self.session_active:
            return {'status': 'No active session'}
        
        summary = self.dialogue_manager.generate_summary_and_reinforcement()
        
        # Save session data for analysis
        session_data = {
            'topic': self.current_topic,
            'objective': self.learning_objective,
            'dialogue_history': self.dialogue_manager.dialogue_history,
            'total_exchanges': len(self.dialogue_manager.dialogue_history),
            'timestamp': datetime.now().isoformat()
        }
        
        # Reset session
        self.session_active = False
        self.dialogue_manager.dialogue_history = []
        
        return {
            'summary': summary,
            'session_data': session_data
        }


# Example usage and integration functions
def integrate_socratic_mode(username: str, topic: str, objective: str):
    """Example of how to integrate Socratic mode into existing system."""
    tutor = SocraticTutor(username)
    
    # Start session
    opening = tutor.start_socratic_session(topic, objective)
    print(f"Tutor: {opening}")
    
    # Interaction loop
    while tutor.session_active:
        student_response = input("You: ")
        
        if student_response.lower() in ['quit', 'exit', 'stop']:
            break
        
        result = tutor.respond_to_student(student_response)
        print(f"\nTutor: {result['response']}")
        
        if result.get('session_complete'):
            break
    
    # End session
    summary = tutor.end_session()
    print(f"\n=== Session Summary ===\n{summary['summary']}")


if __name__ == "__main__":
    # Demo the Socratic tutor
    print("=== Socratic Tutor Demo ===")
    integrate_socratic_mode(
        username="demo_user",
        topic="recursion",
        objective="understand how recursive functions work and when to use them"
    )