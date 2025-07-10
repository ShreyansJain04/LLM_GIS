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
from typing import List, Dict


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
    """Enhanced review mode with integrated spaced repetition and adaptive difficulty"""
    print("\n=== Review Mode ===")
    
    # Get enhanced memory insights 
    enhanced_memory = EnhancedMemorySystem(agent.username)
    insights = enhanced_memory.get_insights()
    recommendations = insights['personalized_recommendations']
    
    # Get performance summary
    summary = get_performance_summary(agent.username)
    print(f"Topics studied: {summary['total_topics_studied']}")
    print(f"Topics mastered: {summary['topics_mastered']}")
    print(f"Weak areas: {summary['weak_areas_count']}")
    
    # Check for due spaced repetition items first
    spaced_schedule = recommendations.get('spaced_repetition_schedule', [])
    due_items = [item for item in spaced_schedule if item['days_until_review'] <= 0]
    
    if due_items:
        print(f"\n🔔 You have {len(due_items)} items due for spaced repetition review!")
        for item in due_items[:3]:  # Show top 3
            priority_emoji = "🔴" if item['priority'] == 'high' else "🟡"
            print(f"  {priority_emoji} {item['topic']} - {item['subtopic']}")
        
        use_spaced = input("\nStart with spaced repetition items? (y/n): ").strip().lower()
        if use_spaced == 'y':
            _spaced_repetition_review(agent, due_items)
            return
    
    # Get focus areas from enhanced memory
    focus_areas = recommendations.get('focus_areas', [])
    if not focus_areas:
        print("Great! No weak areas found. You're doing well!")
        return
    
    print(f"\n🎯 Priority Focus Areas:")
    for i, area in enumerate(focus_areas[:5], 1):
        print(f"{i}. {area['topic']} - {area['subtopic']} (Priority: {area['priority_score']})")
    
    # Enhanced review options
    print("\nWhat would you like to review?")
    print("1. Adaptive review (recommended) - AI adjusts difficulty based on performance")
    print("2. Focus on highest priority weakness")
    print("3. Choose specific topic")
    print("4. Quick review of all weak areas")
    print("5. Flashcard review mode")
    
    choice = input("Select option (1-5): ").strip()
    
    if choice == "1":
        _adaptive_review_session(agent, focus_areas)
    elif choice == "2":
        if focus_areas:
            highest_priority = focus_areas[0]
            print(f"\nFocusing on: {highest_priority['topic']} - {highest_priority['subtopic']}")
            _review_topic_intensively(agent, highest_priority['topic'], adaptive=True)
    elif choice == "3":
        # Let user choose specific topic
        print("\nWeak areas:")
        for i, area in enumerate(focus_areas, 1):
            print(f"{i}. {area['topic']} - {area['subtopic']}")
        
        try:
            topic_choice = int(input("Choose topic number: ")) - 1
            if 0 <= topic_choice < len(focus_areas):
                selected_area = focus_areas[topic_choice]
                _review_topic_intensively(agent, selected_area['topic'], adaptive=True)
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")
    elif choice == "4":
        _quick_review_all(agent, [area['topic'] for area in focus_areas])
    elif choice == "5":
        _flashcard_review(agent, [area['topic'] for area in focus_areas])
    else:
        print("Invalid choice.")


def _spaced_repetition_review(agent: PlannerAgent, due_items: List[Dict]):
    """Review items due for spaced repetition"""
    from flashcards import FlashcardDeck
    
    print(f"\n=== Spaced Repetition Review ===")
    print(f"Reviewing {len(due_items)} due items...")
    
    total_reviewed = 0
    total_correct = 0
    
    for item in due_items:
        topic = item['topic']
        print(f"\n--- {topic} - {item['subtopic']} ---")
        print(f"Last reviewed: {item.get('days_until_review', 0)} days ago")
        
        # Check if we have flashcards for this topic
        deck = FlashcardDeck(agent.username, topic)
        due_cards = deck.get_due_cards(limit=2)  # Limit to 2 cards per topic
        
        if due_cards:
            # Use flashcard system
            for card in due_cards:
                print(f"\nFlashcard: {card['front']}")
                input("Press Enter to see answer...")
                print(f"Answer: {card['back']}")
                
                while True:
                    try:
                        quality = int(input(
                            "\nRate your recall (0-5):\n"
                            "0 - Couldn't remember at all\n"
                            "1 - Wrong, but had some memory\n" 
                            "2 - Wrong, but felt familiar\n"
                            "3 - Correct after some effort\n"
                            "4 - Correct with slight hesitation\n"
                            "5 - Perfect recall\n"
                            "Choice: "
                        ))
                        if 0 <= quality <= 5:
                            break
                        print("Please enter a number between 0 and 5")
                    except ValueError:
                        print("Please enter a valid number")
                
                # Update card with spaced repetition algorithm
                deck.update_card_schedule(card, quality)
                deck.update_stats(quality >= 3)
                
                if quality >= 3:
                    total_correct += 1
                total_reviewed += 1
        else:
            # Generate a question for this topic
            question = generate_question(topic, [], difficulty="medium")
            answer = input(f"\nQuestion: {question}\nYour answer: ")
            
            correct, feedback = check_answer(question, answer)
            print(feedback)
            
            if correct:
                total_correct += 1
            total_reviewed += 1
            
            # Create a flashcard from this Q&A for future spaced repetition
            if not deck.get_stats()['total_cards']:
                deck.add_card(question, feedback.split('\n')[0], item['subtopic'])
    
    # Show results
    accuracy = total_correct / total_reviewed if total_reviewed > 0 else 0
    print(f"\n=== Spaced Repetition Results ===")
    print(f"Items reviewed: {total_reviewed}")
    print(f"Accuracy: {total_correct}/{total_reviewed} ({accuracy:.1%})")
    
    if accuracy >= 0.8:
        print("🎉 Excellent retention! Your spaced repetition is working well.")
    elif accuracy >= 0.6:
        print("👍 Good progress. Keep up the regular reviews.")
    else:
        print("📚 These topics need more frequent review. Consider studying them again.")


def _adaptive_review_session(agent: PlannerAgent, focus_areas: List[Dict]):
    """Adaptive review that adjusts difficulty based on performance"""
    print(f"\n=== Adaptive Review Session ===")
    print("AI will adjust question difficulty based on your performance...")
    
    # Start with mixed topics and adaptive difficulty
    total_questions = 0
    total_correct = 0
    difficulty_level = "medium"  # Start with medium
    consecutive_correct = 0
    consecutive_wrong = 0
    
    subtopics_performance = []
    asked_questions = []
    
    for round_num in range(1, 8):  # Up to 7 questions 
        # Select topic based on priority and recent performance
        if round_num <= 3:
            # First 3 questions: highest priority areas
            current_area = focus_areas[min(round_num-1, len(focus_areas)-1)]
        else:
            # Later questions: rotate through areas
            current_area = focus_areas[(round_num-1) % len(focus_areas)]
        
        topic = current_area['topic']
        print(f"\n--- Round {round_num}: {topic} ---")
        print(f"Difficulty: {difficulty_level.upper()}")
        
        # Generate adaptive question
        question = generate_question(
            topic, 
            asked_questions, 
            difficulty=difficulty_level,
            question_type="objective"
        )
        asked_questions.append(question)
        
        # Handle different question types
        if isinstance(question, dict) and 'options' in question:
            # Multiple choice question
            print(f"\nQuestion: {question['text']}")
            for i, option in enumerate(question['options']):
                print(f"{i}. {option}")
            
            user_answer = input("Enter option number (0-3): ")
        else:
            # Text question
            user_answer = input(f"\nQuestion: {question}\nYour answer: ")
        
        correct, feedback = check_answer(question, user_answer)
        print(feedback)
        
        # Update counters
        total_questions += 1
        if correct:
            total_correct += 1
            consecutive_correct += 1
            consecutive_wrong = 0
        else:
            consecutive_correct = 0
            consecutive_wrong += 1
        
        # Record performance
        subtopics_performance.append({
            'subtopic': f"{topic} - Round {round_num}",
            'question': question,
            'user_answer': user_answer,
            'correct': correct,
            'score': 1 if correct else 0,
            'feedback': feedback,
            'difficulty': difficulty_level
        })
        
        # Auto-create flashcard for correct answers at medium+ difficulty
        if correct and difficulty_level in ["medium", "hard"]:
            from flashcards import auto_create_flashcard_from_review
            auto_create_flashcard_from_review(
                agent.username, 
                topic, 
                str(question),
                feedback.split('\n')[0] if '\n' in feedback else feedback,
                difficulty_level
            )
        
        # Adapt difficulty based on performance
        if consecutive_correct >= 2 and difficulty_level != "hard":
            if difficulty_level == "easy":
                difficulty_level = "medium"
            elif difficulty_level == "medium":
                difficulty_level = "hard"
            print(f"📈 Performance good! Increasing difficulty to {difficulty_level.upper()}")
            consecutive_correct = 0
        elif consecutive_wrong >= 2 and difficulty_level != "easy":
            if difficulty_level == "hard":
                difficulty_level = "medium"
            elif difficulty_level == "medium":
                difficulty_level = "easy"
            print(f"📉 Adjusting difficulty to {difficulty_level.upper()} for better learning")
            consecutive_wrong = 0
        
        # Ask if user wants to continue (after round 3)
        if round_num >= 3 and round_num < 7:
            continue_review = input(f"\nContinue review? ({7-round_num} questions remaining) (y/n): ").lower().strip()
            if continue_review != 'y':
                break
    
    # Final results with adaptive insights
    final_score = total_correct / total_questions if total_questions > 0 else 0
    print(f"\n=== Adaptive Review Results ===")
    print(f"Questions answered: {total_questions}")
    print(f"Final accuracy: {total_correct}/{total_questions} ({final_score:.1%})")
    print(f"Final difficulty level: {difficulty_level.upper()}")
    
    # Determine mastery improvements
    improved_topics = set()
    for perf in subtopics_performance:
        if perf['correct'] and perf['difficulty'] in ["medium", "hard"]:
            improved_topics.add(perf['subtopic'].split(' - ')[0])
    
    if final_score >= 0.8:
        mastery_level = 'mastered'
        print(f"🎉 Excellent! You've shown strong understanding.")
        # Update mastery for topics that were answered correctly at medium/hard difficulty
        profile = agent.profile
        for topic in improved_topics:
            if topic in profile.get('weak_areas', []):
                weak_areas = set(profile.get('weak_areas', []))
                weak_areas.discard(topic)
                profile['weak_areas'] = list(weak_areas)
        agent.save_profile(profile)
    elif final_score >= 0.6:
        mastery_level = 'intermediate'
        print(f"👍 Good progress! Keep practicing these topics.")
    else:
        mastery_level = 'beginner'
        print(f"📚 These topics need more study. Try learning mode for deeper understanding.")
    
    # Record the adaptive session
    record_learning_session(
        username=agent.username,
        topic="Adaptive Review Session",
        subtopics_performance=subtopics_performance,
        final_score=final_score,
        mastery_level=mastery_level
    )


def _review_topic_intensively(agent: PlannerAgent, topic: str, adaptive: bool = False):
    """Enhanced intensive review with optional adaptive difficulty"""
    print(f"\n=== Intensive Review: {topic} ===")
    
    # Start with user's current level for this topic
    profile = agent.profile
    topic_mastery = profile.get('performance_data', {}).get(topic, {})
    avg_score = topic_mastery.get('average_score', 0.5)
    
    # Set initial difficulty based on past performance
    if avg_score >= 0.8:
        difficulty = "hard"
    elif avg_score >= 0.6:
        difficulty = "medium"
    else:
        difficulty = "easy"
    
    print(f"Starting difficulty: {difficulty.upper()} (based on your past performance)")
    
    questions_asked = 0
    correct_answers = 0
    max_questions = 5 if adaptive else 3
    asked_questions = []
    subtopics_performance = []
    consecutive_correct = 0
    consecutive_wrong = 0
    
    while questions_asked < max_questions:
        print(f"\n--- Question {questions_asked + 1}/{max_questions} ---")
        
        # Generate question with current difficulty
        question = generate_question(topic, asked_questions, difficulty=difficulty)
        asked_questions.append(question)
        
        # Handle different question formats
        if isinstance(question, dict) and 'options' in question:
            print(f"\nQuestion: {question['text']}")
            for i, option in enumerate(question['options']):
                print(f"{i}. {option}")
            user_answer = input("Enter option number (0-3): ")
        else:
            user_answer = input(f"\nQuestion: {question}\nYour answer: ")
        
        correct, feedback = check_answer(question, user_answer)
        print(feedback)
        
        # Update performance tracking
        if correct:
            correct_answers += 1
            consecutive_correct += 1
            consecutive_wrong = 0
        else:
            consecutive_correct = 0
            consecutive_wrong += 1
            
        # Record performance with difficulty level
        subtopics_performance.append({
            'subtopic': f"{topic} - Question {questions_asked + 1}",
            'question': question,
            'user_answer': user_answer,
            'correct': correct,
            'score': 1 if correct else 0,
            'feedback': feedback,
            'difficulty': difficulty
        })
        
        # Auto-create flashcard for correct answers at medium+ difficulty
        if correct and difficulty in ["medium", "hard"]:
            from flashcards import auto_create_flashcard_from_review
            auto_create_flashcard_from_review(
                agent.username, 
                topic, 
                str(question),
                feedback.split('\n')[0] if '\n' in feedback else feedback,
                difficulty
            )
        
        questions_asked += 1
        
        # Adaptive difficulty adjustment
        if adaptive and questions_asked < max_questions:
            if consecutive_correct >= 2 and difficulty != "hard":
                old_difficulty = difficulty
                if difficulty == "easy":
                    difficulty = "medium"
                elif difficulty == "medium":
                    difficulty = "hard"
                print(f"\n📈 Great! Increasing difficulty from {old_difficulty.upper()} to {difficulty.upper()}")
                consecutive_correct = 0
            elif consecutive_wrong >= 2 and difficulty != "easy":
                old_difficulty = difficulty
                if difficulty == "hard":
                    difficulty = "medium"
                elif difficulty == "medium":
                    difficulty = "easy"
                print(f"\n📉 Let's adjust difficulty from {old_difficulty.upper()} to {difficulty.upper()}")
                consecutive_wrong = 0
        
        # Ask to continue (except for last question)
        if questions_asked < max_questions:
            continue_review = input("\nContinue with another question? (y/n): ").lower().strip()
            if continue_review != 'y':
                break
    
    # Enhanced results analysis
    score = correct_answers / questions_asked if questions_asked > 0 else 0
    print(f"\n=== Review Results ===")
    print(f"Questions answered: {questions_asked}")
    print(f"Accuracy: {correct_answers}/{questions_asked} ({score:.1%})")
    print(f"Final difficulty level: {difficulty.upper()}")
    
    # Improved mastery determination - considers difficulty and consistency
    high_difficulty_correct = sum(1 for perf in subtopics_performance 
                                 if perf['correct'] and perf['difficulty'] in ['medium', 'hard'])
    
    if score >= 0.8 and high_difficulty_correct >= 2:
        mastery_level = 'mastered'
        print(f"🎉 Excellent! You've mastered {topic}")
        # Remove from weak areas only if consistently good at medium+ difficulty
        profile = agent.profile
        weak_areas = set(profile.get('weak_areas', []))
        weak_areas.discard(topic)
        profile['weak_areas'] = list(weak_areas)
        agent.save_profile(profile)
        
        # Create flashcards for future spaced repetition
        from flashcards import FlashcardDeck
        deck = FlashcardDeck(agent.username, topic)
        if deck.get_stats()['total_cards'] < 3:  # Add some cards for retention
            for perf in subtopics_performance[:2]:  # Use best 2 questions
                if perf['correct']:
                    deck.add_card(
                        str(perf['question']),
                        perf['feedback'].split('\n')[0],
                        topic
                    )
                    
    elif score >= 0.6:
        mastery_level = 'intermediate'
        print(f"👍 Good progress in {topic}. A few more practice sessions should help!")
    else:
        mastery_level = 'beginner'
        print(f"📚 {topic} needs more study. Consider using learning mode first.")
    
    # Record the intensive review session
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


def _flashcard_review(agent: PlannerAgent, topics: List[str]):
    """Review topics using flashcards with spaced repetition."""
    from flashcards import FlashcardDeck, create_flashcards_from_qa
    
    print("\n=== Flashcard Review ===")
    
    # Let user choose topic
    print("\nAvailable topics:")
    for i, topic in enumerate(topics, 1):
        deck = FlashcardDeck(agent.username, topic)
        stats = deck.get_stats()
        due_cards = stats['cards_due']
        print(f"{i}. {topic} ({due_cards} cards due)")
    
    try:
        topic_choice = int(input("\nChoose topic number (or 0 for all): ")) - 1
        
        if topic_choice == -1:
            # Review all due cards across topics
            selected_topics = topics
        elif 0 <= topic_choice < len(topics):
            selected_topics = [topics[topic_choice]]
        else:
            print("Invalid choice.")
            return
            
        total_reviewed = 0
        for topic in selected_topics:
            deck = FlashcardDeck(agent.username, topic)
            
            # Check if we need to generate cards
            if deck.get_stats()['total_cards'] == 0:
                print(f"\nGenerating flashcards for {topic}...")
                # Generate QA pairs for the topic
                qa_pairs = []
                for _ in range(5):  # Generate 5 cards per topic
                    question = generate_question(topic, [])
                    correct_answer, _ = check_answer(question, "GENERATE_ANSWER")
                    qa_pairs.append({
                        'question': question,
                        'answer': correct_answer,
                        'subtopic': topic
                    })
                deck = create_flashcards_from_qa(agent.username, topic, qa_pairs)
            
            # Get due cards
            due_cards = deck.get_due_cards()
            if not due_cards:
                print(f"\nNo cards due for review in {topic}")
                continue
            
            print(f"\nReviewing {topic}...")
            for card in due_cards:
                print(f"\nCard front: {card['front']}")
                input("Press Enter to see answer...")
                print(f"Answer: {card['back']}")
                
                while True:
                    try:
                        quality = int(input(
                            "\nRate your answer (0-5):\n"
                            "0 - Complete blackout\n"
                            "1 - Incorrect, but remembered\n"
                            "2 - Incorrect, but seemed easy\n"
                            "3 - Correct, but difficult\n"
                            "4 - Correct\n"
                            "5 - Correct and easy\n"
                            "Choice: "
                        ))
                        if 0 <= quality <= 5:
                            break
                        print("Please enter a number between 0 and 5")
                    except ValueError:
                        print("Please enter a valid number")
                
                # Update card scheduling
                deck.update_card_schedule(card, quality)
                deck.update_stats(quality >= 3)
                total_reviewed += 1
                
                if total_reviewed % 5 == 0:
                    continue_review = input("\nContinue reviewing? (y/n): ").lower().strip()
                    if continue_review != 'y':
                        break
            
            # Show progress
            stats = deck.get_stats()
            print(f"\nProgress for {topic}:")
            print(f"Cards studied: {stats['cards_studied']}")
            print(f"Correct answers: {stats['correct_answers']}")
            accuracy = stats['correct_answers'] / stats['cards_studied'] if stats['cards_studied'] > 0 else 0
            print(f"Accuracy: {accuracy:.1%}")
            
    except ValueError:
        print("Invalid input.")
        return


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

