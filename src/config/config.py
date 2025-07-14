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

DEFAULT_MODE = 0
NONE_ALL = 1
NONE_PERSONALITY = 2
NONE_EXPERTISE = 3
NONE_BELIEF = 4

API_KEY = 'sk-ZUEYf2Wo10e210991399T3BLbkFJf7172fB2f5Fd438CA0c3'
# LLM_MODEL = 'TA/deepseek-ai/DeepSeek-V3'
# LLM_MODEL = 'TA/Qwen/Qwen2.5-72B-Instruct-Turbo'
# LLM_MODEL = 'TA/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'
# LLM_MODEL = 'llama3.1'
LLM_MODEL = 'llama3.1:70b'
# LLM_MODEL = 'qwen2.5:7b-instruct-q8_0'
# LLM_MODEL = 'TA/Qwen/Qwen2.5-7B-Instruct-Turbo'
# LLM_MODEL = 'TA/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo'

TOKEN_MODEL = 'meta-llama/Llama-3.1-70B'
TOKEN_COUNTING = {
    'enabled': True,
    'encoding_name': 'meta-llama/Meta-Llama-3.1-70B',  # 或其他适合的编码器名称
}

AGENT_GENERATOR = 'TA/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'
# API_BASE_URL = "https://aigptx.top/v1/chat/completions"
API_BASE_URL = "http://localhost:11434/api/generate"

# MMLU Dataset Configuration
MMLU_DATA_PATH = 'data/mmlu'
DEFAULT_MMLU_SUBJECT = 'college_computer_science'  # Default subject for MMLU dataset
TOTAL_PROBLEMS_TO_LOAD = 10  # Total number of problems to load from dataset
PROBLEMS_PER_CHAT = 1  # Number of problems to solve in each chat session