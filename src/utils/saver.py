import os
from datetime import datetime
from typing import Optional
from utils.mmlu_provider import MMLUProblemProvider
from config.config import DEFAULT_MODE, NONE_ALL, NONE_PERSONALITY, NONE_EXPERTISE, NONE_BELIEF

def save_evaluation_result(
    subject: str, 
    agent_count: int, 
    max_rounds: int, 
    problem_provider: Optional[MMLUProblemProvider], 
    model: str, 
    disrupt_config: dict = None,
    agent_mode: int = DEFAULT_MODE,
    metadata: dict = None
):
    """
    Save evaluation results with support for multiple experiments
    Args:
        metadata: Optional dict containing:
            - experiment_count: number of experiments run
            - individual_accuracies: list of accuracies from each experiment
            - average_accuracy: mean accuracy across all experiments
            - std_deviation: standard deviation of accuracies
    """
    # Create evaluate_result directory if it doesn't exist
    result_dir = f"/home/guzhouhong/ljl/multi-agent-chat/evaluate_result/{subject}"
    os.makedirs(result_dir, exist_ok=True)
    
    # Get current date and find next available index
    now = datetime.now()
    base_filename = f"result_{now.month}_{now.day}"
    index = 1
    while os.path.exists(os.path.join(result_dir, f"{base_filename}({index}).txt")):
        index += 1
    
    # Create result file
    filepath = os.path.join(result_dir, f"{base_filename}({index}).txt")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Model: {model}\n")
        f.write(f"Subject: {subject}\n")
        f.write(f"Agent Count: {agent_count} | Rounds: {max_rounds}\n")
        f.write(f"Agent Mode: {agent_mode}\n")
        f.write(f"Derailment: {disrupt_config}\n\n")
        
        if metadata:
            f.write(f"=== Experiment Summary ({metadata['experiment_count']} runs) ===\n")
            f.write(f"Total problems: {metadata['problem_count']}\n")
            f.write("Individual Accuracies:\n")
            for i, acc in enumerate(metadata['individual_accuracies'], 1):
                f.write(f"Experiment {i}: {acc:.2%}\n")
            f.write(f"\nAverage Accuracy: {metadata['average_accuracy']:.2%}\n")
            f.write(f"Standard Deviation: {metadata['std_deviation']:.2%}\n")

            # Add token usage information
            f.write("\nToken Usage:\n")
            for i, tokens in enumerate(metadata['token_usages'], 1):
                f.write(f"Experiment {i}: {tokens:,} tokens\n")
            f.write(f"Total Tokens: {metadata['total_tokens']:,}\n")
            f.write(f"Average Tokens per Experiment: {metadata['avg_tokens_per_experiment']:,.0f}\n")
        else:
            f.write("\nFinal Results:\n")
            f.write(f"Total Problems: {problem_provider.total_answered}\n")
            f.write(f"Correct Answers: {problem_provider.correct_answers}\n")
            accuracy = problem_provider.get_accuracy()
            f.write(f"Accuracy: {accuracy:.2%}\n")
        
        f.write("\n\n")
    
    print(f"\nEvaluation results saved to: {filepath}")