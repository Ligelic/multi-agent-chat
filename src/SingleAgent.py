from agents.agent_factory import AgentFactory
from chat.chat_manager import ChatManager
from utils.ekar_provider import EKARProblemProvider
from utils.mmlu_provider import MMLUProblemProvider
from utils.saver import save_evaluation_result
from config.config import (
    DEFAULT_MMLU_SUBJECT, 
    TOTAL_PROBLEMS_TO_LOAD,
    LLM_MODEL
)
from statistics import mean

def run_single_agent_session(
    chat_manager: ChatManager,
    agent,
    problem_provider: MMLUProblemProvider,
    session_num: int
) -> bool:
    """Run a single session with one agent. Returns True if successful."""
    
    # Get next problem
    problem = problem_provider.get_next_problem()
    if not problem:
        return False
        
    print(f"\n=== Starting Session {session_num} ===")
    print(f"Remaining problems: {problem_provider.get_remaining_count()}")
    
    # Create chat room for this session
    chat_room = chat_manager.create_chat_room(f"Session_{session_num}", max_round=1)
    
    # Add single agent
    chat_room.add_agent(agent)
    
    # Store problem for evaluation
    chat_room.metadata['current_problem'] = problem
    chat_room.metadata['problem_provider'] = problem_provider
    print(f"{problem.question}")
    
    # Send problem to agent
    chat_manager.send_message(
        room_name=chat_room.name,
        sender=agent,
        content=f"Please solve this problem:\n\n{problem.question}\n\nProvide your answer in the format: '[Letter]) [Answer]'"
    )
    
    return True

def run_single_agent_experiment(subject: str, problem_count: int) -> float:
    """Run a single experiment with one agent and return accuracy"""
    chat_manager = ChatManager()
    agent_factory = AgentFactory()
    
    # Initialize problem provider
    problem_provider = MMLUProblemProvider(
        subject=subject,
        total_problems=problem_count
    )
    
    # Create single agent
    agent = agent_factory.create_agents(1, subject=subject)[0]
    print(f"\n=== Testing Agent ===")
    print(f"{agent.name}: {agent.description}")
    
    # Run sessions
    session_num = 1
    while True:
        success = run_single_agent_session(
            chat_manager=chat_manager,
            agent=agent,
            problem_provider=problem_provider,
            session_num=session_num
        )
        
        if not success:
            return problem_provider.get_accuracy()
            
        session_num += 1
        print(f"\nCurrent Accuracy: {problem_provider.get_accuracy():.2%}")

def main_single_agent(subject: str = DEFAULT_MMLU_SUBJECT, 
                     problem_count: int = TOTAL_PROBLEMS_TO_LOAD,
                     experiment_count: int = 3):
    print(f"Initializing Single-Agent Testing System...")
    print(f"Running {experiment_count} experiments...")
    
    accuracies = []
    for i in range(experiment_count):
        print(f"\n=== Experiment {i+1}/{experiment_count} ===")
        accuracy = run_single_agent_experiment(
            subject=subject,
            problem_count=problem_count
        )
        accuracies.append(accuracy)
        print(f"Experiment {i+1} Accuracy: {accuracy:.2%}")
    
    # Calculate statistics
    avg_accuracy = mean(accuracies)
    std_dev = (sum((x - avg_accuracy) ** 2 for x in accuracies) / len(accuracies)) ** 0.5
    
    # Print final results
    print("\n=== Final Results ===")
    print(f"Model: {LLM_MODEL}")
    print(f"Subject: {subject}")
    print(f"Mode: Single Agent")
    print(f"Total problems: {problem_count}")
    print(f"Individual Accuracies: {[f'{acc:.2%}' for acc in accuracies]}")
    print(f"Average Accuracy: {avg_accuracy:.2%}")
    print(f"Standard Deviation: {std_dev:.2%}")
    
    # Save results
    save_evaluation_result(
        subject=subject,
        agent_count=1,
        max_rounds=1,
        problem_provider=None,
        model=LLM_MODEL,
        metadata={
            "experiment_count": experiment_count,
            "individual_accuracies": accuracies,
            "average_accuracy": avg_accuracy,
            "std_deviation": std_dev,
            "problem_count": problem_count
        }
    )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Single-Agent Problem Solving System')
    parser.add_argument('--subject', type=str, default=DEFAULT_MMLU_SUBJECT, help='MMLU subject')
    parser.add_argument('--problem_count', type=int, default=17, help='Number of problems to load')
    parser.add_argument('--experiments', type=int, default=3, help='Number of experiments to run')
    args = parser.parse_args()
    
    main_single_agent(
        subject=args.subject, 
        problem_count=args.problem_count,
        experiment_count=args.experiments
    )