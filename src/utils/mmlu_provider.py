from typing import List, Optional
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
from datasets import load_dataset
import datasets
import pandas as pd
from .problem_base import Problem, ProblemProvider

class MMLUProblemProvider(ProblemProvider):
    def __init__(self, subject: str = 'abstract_algebra', total_problems: int = 10):
        """
        Initialize MMLU problem provider
        Args:
            subject: The MMLU subject to load (e.g. 'abstract_algebra')
            total_problems: Total number of problems to load
        """
        self.problems: List[Problem] = []
        self.used_problems: List[Problem] = []
        self.correct_answers = 0
        self.total_answered = 0
        self._load_mmlu_problems(subject, total_problems)
        
    def _load_mmlu_problems(self, subject: str, n_problems: int):
        try:
            # Load MMLU dataset using datasets library
            config = datasets.DownloadConfig(resume_download=True, max_retries=100) 
            dataset = load_dataset("cais/mmlu", subject, download_config=config)
            
            # Convert test split to dataframe and take first n_problems
            df = pd.DataFrame(dataset['test'][:n_problems])
            
            for _, row in df.iterrows():
                # Format question with options
                question = (
                    f"{row['question']}\n"
                    f"A) {row['choices'][0]}\n"
                    f"B) {row['choices'][1]}\n"
                    f"C) {row['choices'][2]}\n"
                    f"D) {row['choices'][3]}"
                )
                
                # Convert numeric answer to letter (0->A, 1->B, etc)
                answer = chr(65 + row['answer'])  # Convert 0->A, 1->B, etc
                
                self.problems.append(Problem(
                    question=question,
                    answer=answer,
                    metadata={
                        "type": "multiple_choice",
                        "subject": subject
                    }
                ))
                
        except Exception as e:
            print(f"Error loading MMLU dataset: {e}")
            self._generate_sample_problem()
    
    def _generate_sample_problem(self):
        """Generate a sample problem if dataset loading fails"""
        self.problems = [
            Problem(
                question="What is the capital of France?\nA) London\nB) Paris\nC) Berlin\nD) Madrid",
                answer="B",
                metadata={"type": "multiple_choice", "subject": "geography"}
            )
        ]
    
    def get_next_problem(self) -> Optional[Problem]:
        """Get next problem and move it to used problems list"""
        if not self.problems:
            return None
        problem = self.problems.pop(0)
        self.used_problems.append(problem)
        return problem

    def record_answer(self, problem: Problem, answer: str) -> bool:
        """Record an answer and return whether it was correct"""
        is_correct = self.evaluate_answer(problem, answer)
        self.total_answered += 1
        if is_correct:
            self.correct_answers += 1
        return is_correct
    
    def get_accuracy(self) -> float:
        """Get current accuracy rate"""
        if self.total_answered == 0:
            return 0.0
        return self.correct_answers / self.total_answered

    def evaluate_answer(self, problem: Problem, answer: str) -> bool:
        try:
            import re
            # First try to find the most specific answer format
            patterns = [
                # Match complete answer format "D) content" or "D. content"
                r'^([A-D])[）).\s].*$',
                
                # Match simple option format
                r'^([A-D])$',
                
                # Match letter in parentheses
                r'^\(?([A-D])\)$',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, answer.strip(), re.IGNORECASE)
                if match:
                    student_answer = match.group(1).upper()
                    print(f"Pattern matched: {pattern}")
                    print(f"Answer text: {answer}")
                    print(f"Student answer: {student_answer}")
                    print(f"Correct answer: {problem.answer.upper()}")
                    return student_answer == problem.answer.upper()
                    
            print(f"No valid answer format found in: {answer}")
            return False
                
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return False

    def get_remaining_count(self) -> int:
        """Get number of remaining unused problems"""
        return len(self.problems)
        
    def reset(self):
        """Reset problems - move all used problems back to available"""
        self.problems.extend(self.used_problems)
        self.used_problems.clear()