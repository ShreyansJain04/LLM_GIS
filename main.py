"""CLI entry point for tutoring assistant."""
from memory import load_user, save_user, get_weak_areas
from planner import PlannerAgent
from utils import choose_option
from domain_expert import generate_question, check_answer


def review_mode(agent: PlannerAgent):
    weak_topics = get_weak_areas(agent.username)
    if not weak_topics:
        print("No weak areas to review.")
        return
    for topic in weak_topics:
        question = generate_question(topic)
        answer = input(question + "\nYour answer: ")
        _, feedback = check_answer(question, answer)
        print(feedback)


def learn_mode(agent: PlannerAgent):
    topic = input("Enter topic to learn: ")
    agent.run_learning_loop(topic)


def test_mode(agent: PlannerAgent):
    topic = input("Topic to test: ")
    num_q = 3
    correct = 0
    for _ in range(num_q):
        q = generate_question(topic)
        ans = input(q + "\nYour answer: ")
        ok, feedback = check_answer(q, ans)
        if ok:
            correct += 1
        print(feedback)
    print(f"You scored {correct}/{num_q}")


def main():
    username = input("Username: ")
    agent = PlannerAgent(username)
    profile = load_user(username)
    mode = agent.suggest_mode()
    choice = choose_option(
        f"Select mode (suggested: {mode}): ",
        ["review", "learn", "test"]
    )
    if choice == "review":
        review_mode(agent)
    elif choice == "learn":
        learn_mode(agent)
    else:
        test_mode(agent)
    save_user(username, load_user(username))


if __name__ == "__main__":
    main()

