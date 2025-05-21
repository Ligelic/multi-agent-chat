# File: /multi-agent-chat/multi-agent-chat/src/config/config.py

DEFAULT_AGENT_SETTINGS = {
    'name': 'DefaultAgent',
    'max_messages': 100,
    'response_time': 1.0,  # seconds
}

CHAT_ROOM_PARAMETERS = {
    'max_agents': 10,
    'max_message_length': 256,
    'timeout': 300,  # seconds
}

API_KEY = 'sk-ZUEYf2Wo10e210991399T3BLbkFJf7172fB2f5Fd438CA0c3'
# LLM_MODEL = 'TA/deepseek-ai/DeepSeek-V3'
# LLM_MODEL = 'TA/Qwen/Qwen2.5-72B-Instruct-Turbo'
LLM_MODEL = 'TA/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'
# LLM_MODEL = 'TA/Qwen/Qwen2.5-7B-Instruct-Turbo'
# LLM_MODEL = 'TA/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo'
AGENT_GENERATOR = 'TA/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'
API_BASE_URL = "https://aigptx.top/v1/chat/completions"

# MMLU Dataset Configuration
MMLU_DATA_PATH = 'data/mmlu'
DEFAULT_MMLU_SUBJECT = 'formal_logic'  # Default subject for MMLU dataset
TOTAL_PROBLEMS_TO_LOAD = 10  # Total number of problems to load from dataset
PROBLEMS_PER_CHAT = 1  # Number of problems to solve in each chat session