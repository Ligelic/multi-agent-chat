from agents.agent_factory import AgentFactory
from chat.chat_manager import ChatManager
from utils.mmlu_provider import MMLUProblemProvider
from utils.ekar_provider import EKARProblemProvider
from utils.saver import save_evaluation_result
from statistics import mean
import copy
from config.config import (
    DEFAULT_MMLU_SUBJECT, 
    TOTAL_PROBLEMS_TO_LOAD,
    LLM_MODEL,
    DEFAULT_MODE,
    NONE_ALL,
    NONE_PERSONALITY,
    NONE_EXPERTISE,
    NONE_BELIEF
)

def run_chat_session(
    chat_manager: ChatManager,
    agents: list,
    problem_provider: MMLUProblemProvider,
    max_rounds: int,
    session_num: int,
    disrupt_config: dict = None
) -> bool:
    """Run a single chat session with optional disruption"""
    
    # Get next problem
    problem = problem_provider.get_next_problem()
    if not problem:
        return False
        
    print(f"\n=== Starting Chat Session {session_num} ===")
    print(f"Remaining problems: {problem_provider.get_remaining_count()}")
    
    # Create new chat room for this session
    chat_room = chat_manager.create_chat_room(f"Session_{session_num}", max_round=max_rounds)
    # chat_room.max_rounds = max_rounds
    
    # Add agents to room
    for agent in agents:
        chat_room.add_agent(agent)

    # Store problem for evaluation
    chat_room.metadata['current_problem'] = problem
    chat_room.metadata['problem_provider'] = problem_provider
    print(f"{problem.question}")
    # Start discussion with problem
    if disrupt_config and disrupt_config.get('position') == 'first':
        # Send disruptive message first
        chat_manager.send_message(
            room_name=chat_room.name,
            sender=agents[0],
            content=f"I don't think we should solve this problem. Let's talk about something else instead!\n\n{problem.question}"
        )
    else:
        # Normal first message
        chat_manager.send_message(
            room_name=chat_room.name,
            sender=agents[0],
            content=f"Hello everyone! Let's discuss the following problem:\n\n{problem.question}"
        )
    
    return True

def run_experiment(max_rounds: int, agent_count: int, subject: str, 
                  problem_count: int, disrupt_config: dict = None, agent_mode: int = DEFAULT_MODE) -> float:
    """Run a single experiment and return accuracy"""
    # Create managers
    chat_manager = ChatManager()
    agent_factory = AgentFactory()
    
    # Initialize MMLU problem provider with total problems to load
    problem_provider = MMLUProblemProvider(
        subject=subject,
        total_problems=problem_count
    )

    # problem_provider = EKARProblemProvider(
    #     total_problems=problem_count
    # )
    
    # Generate agents with disruption configuration
    if agent_mode == DEFAULT_MODE:
        agents = agent_factory.create_agents(
            agent_count, 
            subject=subject,
            disrupt_config=disrupt_config,
            from_file=False
        )
    else:
        agents = agent_factory.create_agents(
            agent_count, 
            subject=subject,
            disrupt_config=disrupt_config,
            from_file=True,
            mode=agent_mode
        )
        for agent in agents:
            agent.mode = agent_mode
    print("\n=== Generated Agents ===")
    for agent in agents:
        print(f"{agent.name}: {agent.description}")
    
    total_tokens = 0
    for agent in agents:
        agent.llm_service.reset_token_count()
    # Run chat sessions until we run out of problems
    session_num = 1
    while True:
        try:
            success = run_chat_session(
                chat_manager=chat_manager,
                agents=agents,
                problem_provider=problem_provider,
                max_rounds=max_rounds,
                session_num=session_num,
                disrupt_config=disrupt_config
            )
            
            if not success:
                for agent in agents:
                    total_tokens += agent.llm_service.get_total_tokens()
                return problem_provider.get_accuracy(), total_tokens
                
            session_num += 1
            # Optional: wait for user input before starting next session
            print(f"\nCurrent Accuracy: {problem_provider.get_accuracy():.2%}")
            # input("\nPress Enter to start next problem discussion...")
        except Exception as e:
            print(f"Error during chat session: {e}")
            session_num += 1
            continue

def main(max_rounds: int = 3, agent_count: int = 3, subject: str = DEFAULT_MMLU_SUBJECT, 
         problem_count: int = TOTAL_PROBLEMS_TO_LOAD, disrupt_config: dict = None, agent_mode: int = DEFAULT_MODE,
         experiment_count: int = 3):
    print(f"Starting {experiment_count} experiments with {agent_count} agents...")
    print(f"Mode: {agent_mode}")
    
    accuracies = []
    token_usages = []
    for i in range(experiment_count):
        print(f"\n=== Experiment {i+1}/{experiment_count} ===")
        accuracy, tokens = run_experiment(
            max_rounds=max_rounds,
            agent_count=agent_count,
            subject=subject,
            problem_count=problem_count,
            disrupt_config=copy.deepcopy(disrupt_config),
            agent_mode=agent_mode
        )
        accuracies.append(accuracy)
        token_usages.append(tokens)
        print(f"Experiment {i+1} Accuracy: {accuracy:.2%}")
        print(f"Experiment {i+1} Token Usage: {tokens:,}")
    
    avg_accuracy = mean(accuracies)
    avg_tokens = mean(token_usages)
    std_dev = (sum((x - avg_accuracy) ** 2 for x in accuracies) / len(accuracies)) ** 0.5
    
    print("\n=== Final Results ===")
    print(f"Model: {LLM_MODEL}")
    print(f"Subject: {subject}")
    print(f"Agent Count: {agent_count} | Rounds: {max_rounds}")
    print(f"Agent Mode: {agent_mode}")
    print(f"Derailment: {disrupt_config}")
    print(f"Total problems: {problem_count}")
    print(f"Individual Accuracies: {[f'{acc:.2%}' for acc in accuracies]}")
    print(f"Average Accuracy: {avg_accuracy:.2%}")
    print(f"Standard Deviation: {std_dev:.2%}")
    print(f"Total Token Usage: {sum(token_usages):,}")
    print(f"Average Token Usage per Experiment: {avg_tokens:,.0f}")
    
    # Save results with average accuracy
    save_evaluation_result(
        subject=subject,
        agent_count=agent_count,
        max_rounds=max_rounds,
        problem_provider=None,  # Not using specific provider for average results
        model=LLM_MODEL,
        disrupt_config=disrupt_config,
        agent_mode=agent_mode,
        metadata={
            "experiment_count": experiment_count,
            "individual_accuracies": accuracies,
            "average_accuracy": avg_accuracy,
            "std_deviation": std_dev,
            "problem_count": problem_count,
            "token_usages": token_usages,
            "total_tokens": sum(token_usages),
            "avg_tokens_per_experiment": avg_tokens
        }
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Multi-Agent Math Discussion System')
    parser.add_argument('--agents', type=int, default=3, help='Number of agents to participate')
    parser.add_argument('--rounds', type=int, default=3, help='Number of rounds per problem')
    parser.add_argument('--subject', type=str, default=DEFAULT_MMLU_SUBJECT, help='MMLU subject')
    parser.add_argument('--problem_count', type=int, default=TOTAL_PROBLEMS_TO_LOAD, help='Number of problems to load')
    parser.add_argument('--experiments', type=int, default=3, help='Number of experiments to run')
    args = parser.parse_args()
    # main(max_rounds=args.rounds, agent_count=args.agents, subject=args.subject)
    disrupt_config = {
    'position': 'middle',
    'type': 'contrarian'
    }
    main(max_rounds=3, agent_count=2, subject=args.subject, problem_count=17, disrupt_config=None, agent_mode=NONE_ALL, experiment_count=args.experiments)