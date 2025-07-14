"""Enhanced Domain Expert with Advanced RAG and Multi-LLM Support."""
import os
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any

from advanced_rag import AdvancedRAGSystem
from llm_providers import llm_manager


# Initialize the advanced RAG system
rag_system = AdvancedRAGSystem(
    docs_path=Path('docs'),
    embedding_model='all-MiniLM-L6-v2',
    rerank_model='cross-encoder/ms-marco-MiniLM-L-6-v2',
    chunk_size=512,
    chunk_overlap=128
)


def query_domain_expert(
    prompt: str, 
    context: str = "", 
    citations: List[str] = None,
    provider: Optional[str] = None,
    temperature: float = 0.7
) -> str:
    """
    Query the domain expert LLM with advanced RAG context.
    
    Args:
        prompt: The question or request
        context: Optional pre-retrieved context
        citations: Optional citations for the context
        provider: Specific LLM provider to use (None = use default)
        temperature: LLM temperature setting
    
    Returns:
        Generated response from the domain expert
    """
    # Enhance prompt with context and citations
    if context:
        if citations:
            citations_text = "\n".join([f"Source: {cite}" for cite in citations])
            enhanced_prompt = (
                f"You are a domain expert tutor. Use the following context to answer accurately. "
                f"Base your answer ONLY on the provided context. If the context doesn't contain "
                f"enough information, say so clearly. Include citations from the sources listed.\n\n"
                f"Context:\n{context}\n\n"
                f"Sources:\n{citations_text}\n\n"
                f"Question: {prompt}\n\n"
                f"Answer (include citations where relevant):"
            )
        else:
            enhanced_prompt = (
                f"You are a domain expert tutor. Use the following context to answer:\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {prompt}"
            )
    else:
        enhanced_prompt = f"You are a domain expert tutor. {prompt}"
    
    # Generate response using LLM manager
    try:
        response = llm_manager.generate(
            enhanced_prompt, 
            provider=provider,
            temperature=temperature
        )
        return response
    except Exception as e:
        # Fallback response if LLM fails
        return f"[Error: {str(e)}] Unable to generate response. Please check LLM configuration."


def retrieve_context_with_citations(topic: str, k: int = 5) -> Tuple[str, List[str]]:
    """
    Retrieve context using advanced RAG system.
    
    Returns:
        Tuple of (context, citations)
    """
    context, citations, _ = rag_system.retrieve(
        query=topic,
        k=k,
        use_reranking=True,
        alpha=0.7  # Favor semantic search
    )
    return context, citations


def explain_concept(topic: str, detail_level: str = "standard") -> str:
    """
    Explain a concept with appropriate detail level.
    
    Args:
        topic: The concept to explain
        detail_level: "simple", "standard", or "advanced"
    """
    # Retrieve relevant context
    context, citations = retrieve_context_with_citations(topic)
    
    if not context:
        # Check available sources
        stats = rag_system.get_statistics()
        if stats['total_documents'] == 0:
            return (
                f"No documents found in the docs folder. Please add relevant PDF or text files "
                f"to get accurate, source-based explanations about '{topic}'."
            )
        else:
            sources = list(stats['source_breakdown'].keys())
            return (
                f"I don't have specific information about '{topic}' in the available documents. "
                f"Available sources: {', '.join(sources)}. Please ensure your query matches "
                f"content in these documents or add relevant documents to the docs folder."
            )
    
    # Adjust prompt based on detail level
    prompts = {
        "simple": f"Explain '{topic}' in simple terms that a beginner can understand. Use analogies if helpful.",
        "standard": f"Explain the concept of '{topic}' clearly and comprehensively.",
        "advanced": f"Provide an in-depth explanation of '{topic}' including technical details and nuances."
    }
    
    prompt = prompts.get(detail_level, prompts["standard"])
    return query_domain_expert(prompt, context, citations)


def generate_example(topic: str, difficulty: str = "medium") -> str:
    """
    Generate an example for a topic with specified difficulty.
    
    Args:
        topic: The topic for the example
        difficulty: "easy", "medium", or "hard"
    """
    context, citations = retrieve_context_with_citations(topic)
    
    if not context:
        stats = rag_system.get_statistics()
        if stats['total_documents'] == 0:
            return (
                f"No documents found. Please add relevant documents to get examples based on "
                f"your specific materials."
            )
        else:
            sources = list(stats['source_breakdown'].keys())
            return (
                f"I don't have specific examples for '{topic}' in the available documents. "
                f"Available sources: {', '.join(sources)}."
            )
    
    difficulty_prompts = {
        "easy": f"Provide a simple, straightforward example for '{topic}' that clearly illustrates the basic concept.",
        "medium": f"Provide a practical worked example for '{topic}' that demonstrates typical usage.",
        "hard": f"Provide a challenging example for '{topic}' that explores edge cases or advanced applications."
    }
    
    prompt = difficulty_prompts.get(difficulty, difficulty_prompts["medium"])
    return query_domain_expert(prompt, context, citations)


def generate_question(topic: str, previous_questions: List[str] = None, difficulty: str = "medium", question_type: str = "objective") -> Dict:
    """Generate a question for a given topic.
    
    Args:
        topic: The topic to generate a question for
        previous_questions: List of previously asked questions to avoid repetition
        difficulty: Difficulty level ("easy", "medium", "hard")
        question_type: Type of question ("objective", "analytical", "synthesis")
        
    Returns:
        Dict containing question text and options if objective
    """
    if previous_questions is None:
        previous_questions = []
    
    # Get context for the topic
    context = _retrieve_context(topic)
    
    if question_type == "objective":
        # Build prompt for multiple choice question
        prompt = (
            f"Create a multiple choice question about '{topic}' based on the provided context.\n"
            f"Difficulty level: {difficulty}\n"
            "Requirements:\n"
            "1. Question should test understanding, not just recall\n"
            "2. All options should be plausible and related to the topic\n"
            "3. Only one option should be correct\n"
            "4. Options should be clear and concise\n"
            "Format:\n"
            "QUESTION: <question text>\n"
            "CORRECT: <correct answer>\n"
            "WRONG1: <plausible wrong answer 1>\n"
            "WRONG2: <plausible wrong answer 2>\n"
            "WRONG3: <plausible wrong answer 3>\n"
            "EXPLANATION: <brief explanation of why the correct answer is right>"
        )
        
        if previous_questions:
            prompt += "\nAvoid these previous questions:\n" + "\n".join(previous_questions)
        
        # Get response from LLM
        response = query_domain_expert(prompt, context)
        
        # Parse response
        try:
            lines = response.split('\n')
            question_text = next(line.replace('QUESTION: ', '') for line in lines if line.startswith('QUESTION:'))
            correct_ans = next(line.replace('CORRECT: ', '') for line in lines if line.startswith('CORRECT:'))
            wrong1 = next(line.replace('WRONG1: ', '') for line in lines if line.startswith('WRONG1:'))
            wrong2 = next(line.replace('WRONG2: ', '') for line in lines if line.startswith('WRONG2:'))
            wrong3 = next(line.replace('WRONG3: ', '') for line in lines if line.startswith('WRONG3:'))
            explanation = next(line.replace('EXPLANATION: ', '') for line in lines if line.startswith('EXPLANATION:'))
            
            # Randomize option order
            options = [correct_ans, wrong1, wrong2, wrong3]
            correct_idx = 0  # Index of correct answer before shuffling
            import random
            random.shuffle(options)
            correct_idx = options.index(correct_ans)  # New index after shuffling
            
            return {
                "text": question_text,
                "options": options,
                "correct_option": correct_idx,
                "explanation": explanation,
                "type": "objective",
                "difficulty": difficulty
            }
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            # Fallback to basic question if parsing fails
            return {
                "text": f"Which of the following best describes {topic}?",
                "options": [
                    "The correct description",
                    "An incorrect description",
                    "Another incorrect description",
                    "Yet another incorrect description"
                ],
                "correct_option": 0,
                "explanation": "Please refer to the course materials.",
                "type": "objective",
                "difficulty": difficulty
            }
    else:
        # Generate subjective/analytical question
        prompt = (
            f"Create a {question_type} question about '{topic}' that requires {difficulty} level understanding.\n"
            "The question should encourage critical thinking and detailed explanation."
        )
        if previous_questions:
            prompt += "\nAvoid these previous questions:\n" + "\n".join(previous_questions)
        
        question_text = query_domain_expert(prompt, context)
        return {
            "text": question_text,
            "type": "subjective",
            "difficulty": difficulty
        }


def check_answer(question: Dict, answer: str) -> Tuple[bool, str]:
    """Check if the answer is correct.
    
    Args:
        question: Question dict containing text and options if objective
        answer: User's answer
        
    Returns:
        Tuple of (is_correct, feedback)
    """
    
    print(f"check_answer received question: {question}")
    print(f"check_answer received answer: {answer}")
    print(f"Question type: {question.get('type')}")
    print(f"Question options: {question.get('options', [])}")
    print(f"Question correct_option: {question.get('correct_option')}")
    
    if question.get("type") == "objective":
        try:
            selected_option = int(answer)
            is_correct = selected_option == question["correct_option"]
            
            feedback = question.get("explanation", "")
            if is_correct:
                feedback = "✅ Correct! " + feedback
            else:
                correct_text = question["options"][question["correct_option"]]
                feedback = f"❌ Incorrect. The correct answer was: {correct_text}\n\nExplanation: {feedback}"
            
            return is_correct, feedback
        except ValueError:
            return False, "Please enter a valid option number (0-3)"
    else:
        # For subjective questions, use semantic similarity
        context = _retrieve_context(question["text"])
        
        # Build evaluation prompt
        prompt = (
            f"Question: {question['text']}\n"
            f"Student's answer: {answer}\n\n"
            "Evaluate the answer based on:\n"
            "1. Accuracy of information\n"
            "2. Completeness of explanation\n"
            "3. Understanding of concepts\n\n"
            "Provide:\n"
            "SCORE: (number between 0 and 1)\n"
            "FEEDBACK: (constructive feedback explaining the score)"
        )
        
        response = query_domain_expert(prompt, context)
        
        try:
            # Parse score and feedback
            score_line = next(line for line in response.split('\n') if line.startswith('SCORE:'))
            score = float(score_line.replace('SCORE:', '').strip())
            
            feedback_line = next(line for line in response.split('\n') if line.startswith('FEEDBACK:'))
            feedback = feedback_line.replace('FEEDBACK:', '').strip()
            
            # Consider score >= 0.8 as correct for subjective questions
            is_correct = score >= 0.8
            
            return is_correct, feedback
        except Exception as e:
            print(f"Error parsing evaluation response: {e}")
            # Fallback scoring
            return False, "Unable to evaluate answer. Please try again."


def generate_hint(question: str, difficulty_level: int = 1) -> str:
    """
    Generate a hint for a question with varying levels of help.
    
    Args:
        question: The question to provide a hint for
        difficulty_level: 1 (subtle hint) to 3 (explicit guidance)
    """
    context, citations = retrieve_context_with_citations(question)
    
    hint_prompts = {
        1: f"Provide a subtle hint for this question without giving away the answer: {question}",
        2: f"Provide a helpful hint that guides toward the answer for: {question}",
        3: f"Provide clear guidance toward answering this question: {question}"
    }
    
    prompt = hint_prompts.get(difficulty_level, hint_prompts[1])
    return query_domain_expert(prompt, context, citations)


def generate_summary(topic: str, length: str = "medium") -> str:
    """
    Generate a summary of a topic.
    
    Args:
        topic: The topic to summarize
        length: "short", "medium", or "long"
    """
    context, citations = retrieve_context_with_citations(topic)
    
    if not context:
        stats = rag_system.get_statistics()
        sources = list(stats['source_breakdown'].keys()) if stats['total_documents'] > 0 else []
        if sources:
            return (
                f"I don't have specific information about '{topic}' to summarize. "
                f"Available sources: {', '.join(sources)}."
            )
        else:
            return "No documents available to create a summary. Please add relevant documents to the docs folder."
    
    length_instructions = {
        "short": "Give a brief 2-3 sentence summary",
        "medium": "Give a concise paragraph summary",
        "long": "Give a comprehensive summary with key points"
    }
    
    prompt = f"{length_instructions[length]} of '{topic}' based on the provided context."
    return query_domain_expert(prompt, context, citations)


def generate_quiz(topic: str, num_questions: int = 5, mix_types: bool = True) -> List[Dict[str, Any]]:
    """
    Generate a complete quiz on a topic.
    
    Args:
        topic: The topic for the quiz
        num_questions: Number of questions to generate
        mix_types: Whether to mix different question types
    
    Returns:
        List of quiz questions with structure
    """
    context, citations = retrieve_context_with_citations(topic, k=10)  # Get more context for quiz
    
    if not context:
        return [{
            "question": f"No source materials available for {topic}",
            "type": "error",
            "difficulty": "n/a"
        }]
    
    quiz_questions = []
    question_types = ["conceptual", "analytical", "application"] if mix_types else ["conceptual"]
    difficulties = ["easy", "medium", "hard"]
    
    for i in range(num_questions):
        q_type = question_types[i % len(question_types)]
        q_difficulty = difficulties[min(i // len(question_types), 2)]  # Gradually increase difficulty
        
        # Generate unique question
        previous = [q["question"] for q in quiz_questions]
        question = generate_question(topic, previous, q_difficulty, q_type)
        
        quiz_questions.append({
            "question": question,
            "type": q_type,
            "difficulty": q_difficulty,
            "topic": topic
        })
    
    return quiz_questions


def get_available_sources() -> List[str]:
    """Get list of available document sources."""
    stats = rag_system.get_statistics()
    return list(stats['source_breakdown'].keys())


def show_available_sources() -> str:
    """Show what document sources are available with statistics."""
    stats = rag_system.get_statistics()
    
    if stats['total_documents'] == 0:
        return "No documents found in the docs folder. Please add PDF or text files."
    
    lines = [
        f"Total documents: {stats['total_documents']}",
        f"Total sources: {stats['total_sources']}",
        f"Index type: {stats['index_type']}",
        f"Hybrid search: {'Enabled' if stats['has_sparse_index'] else 'Semantic only'}",
        f"Reranking: {'Enabled' if stats['has_reranker'] else 'Disabled'}",
        "",
        "Document sources:"
    ]
    
    for source, count in stats['source_breakdown'].items():
        lines.append(f"  - {source}: {count} chunks")
    
    return "\n".join(lines)


def search_specific_source(source_name: str, query: str) -> str:
    """Search within a specific document source."""
    # Filter search to specific source
    context, citations, docs = rag_system.retrieve(
        query=query,
        filters={"source": source_name},
        k=5
    )
    
    if not context:
        return f"No relevant content found for '{query}' in source '{source_name}'."
    
    prompt = f"Answer the following question based on the specific source: {query}"
    return query_domain_expert(prompt, context, citations)


def get_llm_info() -> Dict[str, Any]:
    """Get information about available LLM providers."""
    return llm_manager.list_providers()


def set_llm_provider(provider: str) -> bool:
    """Set the active LLM provider."""
    try:
        llm_manager.set_active_provider(provider)
        return True
    except ValueError:
        return False


# Legacy functions for backward compatibility
def _retrieve_context(topic: str) -> str:
    """Legacy retrieval helper - kept for backward compatibility."""
    context, _ = retrieve_context_with_citations(topic)
    return context



