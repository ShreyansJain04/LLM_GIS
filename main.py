"""CLI entry point for tutoring assistant."""
from dotenv import load_dotenv
load_dotenv()

from memory import load_user, save_user, get_weak_areas, get_recommended_review_topics, get_performance_summary, record_learning_session
from planner import PlannerAgent
from utils import choose_option
from domain_expert import generate_question, check_answer, show_available_sources, get_llm_info, set_llm_provider
from interactive_session import InteractiveSession
from enhanced_memory import EnhancedMemorySystem
from llm_providers import llm_manager


def show_sources():
    """Show available document sources to the user."""
    print("\n=== Available Document Sources ===")
    sources_info = show_available_sources()
    print(sources_info)
    print("\nTo add more documents:")
    print("1. Place PDF or .txt files in the 'docs' folder")
    print("2. Restart the application to load new documents")
    print("3. The system will automatically extract and index content with citations")


def review_mode(agent: PlannerAgent):
    """Enhanced review mode that focuses on user's actual weak areas"""
    print("\n=== Review Mode ===")
    
    # Get performance summary
    summary = get_performance_summary(agent.username)
    print(f"Topics studied: {summary['total_topics_studied']}")
    print(f"Topics mastered: {summary['topics_mastered']}")
    print(f"Weak areas: {summary['weak_areas_count']}")
    
    # Get recommended topics for review
    recommended_topics = get_recommended_review_topics(agent.username, limit=5)
    
    if not recommended_topics:
        print("Great! No weak areas found. You're doing well!")
        return
    
    print(f"\nRecommended topics to review: {', '.join(recommended_topics)}")
    
    # Let user choose what to review
    print("\nWhat would you like to review?")
    print("1. Focus on weakest topics")
    print("2. Choose specific topic")
    print("3. Quick review of all weak areas")
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == "1":
        # Focus on the weakest topic
        focus_topic = recommended_topics[0]
        print(f"\nFocusing on: {focus_topic}")
        _review_topic_intensively(agent, focus_topic)
        
    elif choice == "2":
        # Let user choose specific topic
        print("\nWeak areas:")
        for i, topic in enumerate(recommended_topics, 1):
            print(f"{i}. {topic}")
        
        try:
            topic_choice = int(input("Choose topic number: ")) - 1
            if 0 <= topic_choice < len(recommended_topics):
                selected_topic = recommended_topics[topic_choice]
                _review_topic_intensively(agent, selected_topic)
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")
            
    elif choice == "3":
        # Quick review of all weak areas
        _quick_review_all(agent, recommended_topics)
    else:
        print("Invalid choice.")


def _review_topic_intensively(agent: PlannerAgent, topic: str):
    """Intensive review of a specific topic"""
    print(f"\n=== Intensive Review: {topic} ===")
    
    # Generate multiple questions for this topic
    questions_asked = 0
    correct_answers = 0
    max_questions = 3
    asked_questions = []  # Track previously asked questions to avoid repetition
    subtopics_performance = []  # Track performance for memory system
    
    while questions_asked < max_questions:
        question = generate_question(topic, asked_questions)
        asked_questions.append(question)  # Add to the list to avoid repetition
        answer = input(f"\nQuestion {questions_asked + 1}: {question}\nYour answer: ")
        
        correct, feedback = check_answer(question, answer)
        print(feedback)
        
        # Record performance for this question
        subtopics_performance.append({
            'subtopic': f"Review Question {questions_asked + 1}",
            'question': question,
            'user_answer': answer,
            'correct': correct,
            'score': 1 if correct else 0,
            'feedback': feedback
        })
        
        if correct:
            correct_answers += 1
            
        questions_asked += 1
        
        if questions_asked < max_questions:
            continue_review = input("\nContinue with another question? (y/n): ").lower().strip()
            if continue_review != 'y':
                break
    
    # Show results
    score = correct_answers / questions_asked if questions_asked > 0 else 0
    print(f"\nReview Results: {correct_answers}/{questions_asked} ({score:.1%})")
    
    # Determine mastery level
    if score >= 0.8:
        mastery_level = 'mastered'
        print(f"Excellent! You've improved in {topic}")
        # Update the topic as no longer weak
        profile = agent.profile
        weak_areas = set(profile.get('weak_areas', []))
        weak_areas.discard(topic)
        profile['weak_areas'] = list(weak_areas)
        agent.save_profile(profile)
    elif score >= 0.6:
        mastery_level = 'intermediate'
        print(f"Good progress in {topic}. Keep practicing!")
    else:
        mastery_level = 'beginner'
        print(f"Keep working on {topic}. Consider studying it again.")
    
    # Record the review session in memory
    record_learning_session(
        username=agent.username,
        topic=topic,
        subtopics_performance=subtopics_performance,
        final_score=score,
        mastery_level=mastery_level
    )


def _quick_review_all(agent: PlannerAgent, weak_topics: list):
    """Quick review covering all weak areas"""
    print(f"\n=== Quick Review of All Weak Areas ===")
    
    total_correct = 0
    total_questions = 0
    asked_questions = []  # Track all questions asked in this session
    
    for topic in weak_topics[:5]:  # Limit to top 5 weak areas
        print(f"\n--- {topic} ---")
        # Generate question for this topic, avoiding previously asked questions
        question = generate_question(topic, asked_questions)
        asked_questions.append(question)  # Add to the list to avoid repetition
        answer = input(question + "\nYour answer: ")
        
        correct, feedback = check_answer(question, answer)
        print(feedback)
        
        if correct:
            total_correct += 1
        total_questions += 1
    
    # Show overall results
    overall_score = total_correct / total_questions if total_questions > 0 else 0
    print(f"\n=== Overall Review Results ===")
    print(f"Score: {total_correct}/{total_questions} ({overall_score:.1%})")
    
    if overall_score >= 0.8:
        print("Excellent improvement across your weak areas!")
    elif overall_score >= 0.6:
        print("Good progress! Keep reviewing these topics.")
    else:
        print("These topics need more study. Consider focused learning sessions.")


def learn_mode(agent: PlannerAgent):
    topic = input("Enter topic to learn: ")
    
    # Check if user wants interactive mode
    print("\nLearning mode options:")
    print("1. Interactive mode (recommended) - Ask questions anytime, pause/resume")
    print("2. Traditional mode - Sequential learning")
    
    mode_choice = input("Select mode (1 or 2): ").strip()
    
    if mode_choice == "1":
        # Use new interactive session
        session = InteractiveSession(agent.username, topic)
        session.run_interactive_learning()
    else:
        # Use traditional mode
        agent.run_learning_loop(topic)


def test_mode(agent: PlannerAgent):
    topic = input("Topic to test: ")
    num_q = 3
    correct = 0
    asked_questions = []  # Track previously asked questions
    subtopics_performance = []  # Track performance for memory system
    
    for i in range(num_q):
        # Generate a unique question by passing previously asked questions
        q = generate_question(topic, asked_questions)
        asked_questions.append(q)  # Add to the list to avoid repetition
        
        ans = input(f"\nQuestion {i+1}: {q}\nYour answer: ")
        ok, feedback = check_answer(q, ans)
        
        # Record performance for this question
        subtopics_performance.append({
            'subtopic': f"Test Question {i+1}",
            'question': q,
            'user_answer': ans,
            'correct': ok,
            'score': 1 if ok else 0,
            'feedback': feedback
        })
        
        if ok:
            correct += 1
        print(feedback)
        
    final_score = correct / num_q
    print(f"\nTest completed! You scored {correct}/{num_q} ({final_score:.1%})")
    
    # Determine mastery level
    if final_score >= 0.8:
        mastery_level = 'mastered'
    elif final_score >= 0.6:
        mastery_level = 'intermediate'
    else:
        mastery_level = 'beginner'
    
    # Record the test session in memory
    record_learning_session(
        username=agent.username,
        topic=topic,
        subtopics_performance=subtopics_performance,
        final_score=final_score,
        mastery_level=mastery_level
    )
    
    print(f"Progress saved! Mastery level: {mastery_level}")


def insights_mode(username: str):
    """Show detailed learning insights and analytics."""
    print("\n=== Learning Insights & Analytics ===")
    
    enhanced_memory = EnhancedMemorySystem(username)
    insights = enhanced_memory.get_insights()
    
    # Performance Summary
    perf = insights['performance_summary']
    print(f"\n📊 Performance Summary:")
    print(f"  Topics studied: {perf['topics_studied']}")
    print(f"  Average mastery: {perf['average_mastery']:.1%}")
    print(f"  Weak areas: {perf['weak_areas_count']}")
    print(f"  Study streak: {perf['study_streak']} days")
    
    # Learning Trajectory
    print(f"\n📈 Learning Trajectory:")
    print(f"  {insights['learning_trajectory']}")
    
    # Personalized Recommendations
    recommendations = insights['personalized_recommendations']
    
    print(f"\n⏰ Optimal Study Time: {recommendations['optimal_study_time']}")
    print(f"📏 Suggested Session Length: {recommendations['suggested_session_length']} minutes")
    
    # Learning Style Adjustments
    if recommendations['learning_style_adjustments']:
        print("\n💡 Personalized Learning Tips:")
        for i, tip in enumerate(recommendations['learning_style_adjustments'], 1):
            print(f"  {i}. {tip}")
    
    # Focus Areas
    if recommendations['focus_areas']:
        print("\n🎯 Priority Focus Areas:")
        for area in recommendations['focus_areas']:
            print(f"  • {area['topic']} - {area['subtopic']}")
            print(f"    Error type: {area['main_error_type']}, Repetitions needed: {area['repetitions_needed']}")
    
    # Spaced Repetition Schedule
    if recommendations['spaced_repetition_schedule']:
        print("\n📅 Spaced Repetition Schedule:")
        for review in recommendations['spaced_repetition_schedule']:
            priority_emoji = "🔴" if review['priority'] == 'high' else "🟡"
            print(f"  {priority_emoji} {review['topic']} - {review['subtopic']}")
            print(f"     Review date: {review['review_date']} ({review['days_until_review']} days)")
    
    # Action prompt
    print("\n💭 What would you like to do?")
    print("1. Start a focused review session")
    print("2. View detailed weakness analysis")
    print("3. Export learning data")
    print("4. Return to main menu")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        # Start focused review based on recommendations
        if recommendations['focus_areas']:
            topic = recommendations['focus_areas'][0]['topic']
            print(f"\nStarting focused review on: {topic}")
            session = InteractiveSession(username, topic)
            session.run_interactive_learning()
    elif choice == "2":
        # Show detailed weakness analysis
        print("\n=== Detailed Weakness Analysis ===")
        for area in recommendations['focus_areas']:
            print(f"\n📌 {area['topic']} - {area['subtopic']}")
            print(f"  Main error type: {area['main_error_type']}")
            print(f"  Times reviewed: {area['repetitions_needed']}")
            if area['last_reviewed']:
                print(f"  Last reviewed: {area['last_reviewed']}")
    elif choice == "3":
        # Export data (placeholder)
        print("\n📤 Learning data export coming soon!")
    
    # Return to main menu


def llm_mode():
    """Manage LLM providers and settings."""
    print("\n=== LLM Provider Management ===")
    
    # Show current providers
    providers = get_llm_info()
    
    print("\n📡 Available LLM Providers:")
    for name, info in providers.items():
        status = "✅" if info['available'] else "❌"
        active = "🎯" if info.get('active') else "  "
        print(f"{active} {status} {name}: {info['model']}")
        if not info['available'] and info.get('requires_api_key'):
            print(f"     → Requires API key")
    
    print("\n🔧 Options:")
    print("1. Switch active provider")
    print("2. Add/Update API key")
    print("3. Test provider")
    print("4. View provider details")
    print("5. Return to main menu")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        # Switch provider
        available = [name for name, info in providers.items() if info['available']]
        if not available:
            print("\n❌ No providers available. Please add API keys first.")
            return
        
        print("\nAvailable providers:")
        for i, name in enumerate(available, 1):
            print(f"{i}. {name}")
        
        try:
            provider_choice = int(input("Select provider: ")) - 1
            if 0 <= provider_choice < len(available):
                selected = available[provider_choice]
                if set_llm_provider(selected):
                    print(f"\n✅ Switched to {selected}")
                else:
                    print(f"\n❌ Failed to switch to {selected}")
        except ValueError:
            print("\n❌ Invalid selection")
    
    elif choice == "2":
        # Add API key
        print("\nProviders requiring API keys:")
        print("1. OpenAI")
        print("2. DeepSeek")
        print("3. Anthropic")
        print("4. Google Gemini")
        
        provider_map = {
            "1": "openai",
            "2": "deepseek",
            "3": "anthropic",
            "4": "gemini"
        }
        
        provider_choice = input("Select provider: ").strip()
        if provider_choice in provider_map:
            provider = provider_map[provider_choice]
            api_key = input(f"Enter API key for {provider}: ").strip()
            if api_key:
                llm_manager.add_api_key(provider, api_key)
                print(f"\n✅ API key added for {provider}")
        else:
            print("\n❌ Invalid selection")
    
    elif choice == "3":
        # Test provider
        available = [name for name, info in providers.items() if info['available']]
        if not available:
            print("\n❌ No providers available to test")
            return
        
        print("\nTest which provider?")
        for i, name in enumerate(available, 1):
            print(f"{i}. {name}")
        
        try:
            provider_choice = int(input("Select provider: ")) - 1
            if 0 <= provider_choice < len(available):
                selected = available[provider_choice]
                print(f"\nTesting {selected}...")
                if llm_manager.test_provider(selected):
                    print(f"✅ {selected} is working correctly!")
                else:
                    print(f"❌ {selected} test failed")
        except ValueError:
            print("\n❌ Invalid selection")
    
    elif choice == "4":
        # View details
        print("\n=== Provider Details ===")
        for name, info in providers.items():
            print(f"\n{name}:")
            for key, value in info.items():
                if key != "active":
                    print(f"  {key}: {value}")
    
    # Recurse to show menu again unless returning to main
    if choice != "5":
        input("\nPress Enter to continue...")
        llm_mode()


def main():
    username = input("Username: ")
    agent = PlannerAgent(username)
    profile = load_user(username)
    mode = agent.suggest_mode()
    
    print("\n=== Welcome to the AI Tutoring System ===")
    print("📚 This system uses your documents for accurate, cited answers")
    print("💡 Add PDF or text files to the 'docs' folder for better results")
    
    choice = choose_option(
        f"Select mode (suggested: {mode}): ",
        ["review", "learn", "test", "insights", "sources", "llm"]
    )
    
    if choice == "review":
        review_mode(agent)
    elif choice == "learn":
        learn_mode(agent)
    elif choice == "test":
        test_mode(agent)
    elif choice == "insights":
        insights_mode(username)
    elif choice == "sources":
        show_sources()
    elif choice == "llm":
        llm_mode()
    
    save_user(username, load_user(username))


if __name__ == "__main__":
    main()

