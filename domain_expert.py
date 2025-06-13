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


def generate_question(
    topic: str, 
    previous_questions: List[str] = None,
    difficulty: str = "medium",
    question_type: str = "conceptual"
) -> str:
    """
    Generate a question based on source documents.
    
    Args:
        topic: The topic for the question
        previous_questions: List of previously asked questions to avoid repetition
        difficulty: "easy", "medium", or "hard"
        question_type: "conceptual", "analytical", "application", or "synthesis"
    """
    if previous_questions is None:
        previous_questions = []
    
    context, citations = retrieve_context_with_citations(topic)
    
    if not context:
        # Fallback to general question if no context available
        return f"What do you know about {topic}? (Note: No source documents available for this topic)"
    
    # Build prompt based on question type and difficulty
    type_instructions = {
        "conceptual": "that tests understanding of key concepts",
        "analytical": "that requires analysis and critical thinking",
        "application": "that applies the concept to a practical scenario",
        "synthesis": "that combines multiple aspects or relates to other concepts"
    }
    
    difficulty_instructions = {
        "easy": "Make it straightforward and direct",
        "medium": "Make it moderately challenging",
        "hard": "Make it challenging and thought-provoking"
    }
    
    base_prompt = (
        f"Create a {question_type} question about '{topic}' {type_instructions[question_type]}. "
        f"{difficulty_instructions[difficulty]}. Base the question on the provided context."
    )
    
    if previous_questions:
        previous_q_text = "\n".join([f"- {q}" for q in previous_questions[-5:]])  # Last 5 questions
        prompt = (
            f"{base_prompt}\n\n"
            f"Avoid repeating these previously asked questions:\n{previous_q_text}\n\n"
            f"Generate a different question that covers a different aspect."
        )
    else:
        prompt = base_prompt
    
    return query_domain_expert(prompt, context, citations)


def check_answer(question: str, answer: str, provide_hints: bool = True) -> Tuple[bool, str]:
    """
    Check answer against source documents with detailed feedback.
    
    Args:
        question: The question that was asked
        answer: The user's answer
        provide_hints: Whether to provide hints for incorrect answers
    
    Returns:
        Tuple of (is_correct, feedback)
    """
    # Get context relevant to both question and answer
    combined_query = f"{question} {answer}"
    context, citations = retrieve_context_with_citations(combined_query)
    
    prompt = (
        f"Question: {question}\n"
        f"User answer: {answer}\n\n"
        f"Based on the provided context, evaluate the answer:\n"
        f"1. Is it correct according to the source materials?\n"
        f"2. What aspects are correct or incorrect?\n"
        f"3. What key points might be missing?\n"
    )
    
    if provide_hints and answer.lower() in ['i dont know', 'idk', '?', 'no idea']:
        prompt += "\n4. Provide a helpful hint to guide the learner."
    
    feedback = query_domain_expert(prompt, context, citations)
    
    # Determine correctness based on feedback
    feedback_lower = feedback.lower()
    correct = any(word in feedback_lower for word in ['correct', 'right', 'accurate', 'excellent', 'perfect'])
    partially_correct = any(word in feedback_lower for word in ['partially', 'somewhat', 'mostly'])
    
    if partially_correct and not correct:
        correct = False  # Partial credit could be implemented later
    
    return correct, feedback


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



