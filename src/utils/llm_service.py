import requests
import json
from typing import Dict
# from transformers import AutoTokenizer
from config.config import API_KEY, LLM_MODEL, API_BASE_URL, TOKEN_MODEL

class LLMService:
    def __init__(self):
        self.headers = {
            # "Authorization": f'Bearer {API_KEY}',
            "Content-Type": "application/json",
        }
        self.total_tokens = 0
    #     self.enc = AutoTokenizer.from_pretrained(TOKEN_MODEL) # 使用适合的编码器

    # def count_tokens(self, text: str) -> int:
    #     """Count tokens in text using tiktoken"""
    #     return len(self.enc.encode(text))
    
    def count_word(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
        
    def get_response(self, prompt: str) -> str:
        
        prompt_tokens = self.count_word(prompt)
        
        data = {
            "model": LLM_MODEL,  # 替换为你的模型名称（如 mistral、codellama 等）
            "prompt": prompt,
            "stream": False,     # 是否启用流式响应
            # "temperature": 0.7   # 控制生成随机性（0-1）
        }
        
        response = requests.post(
            API_BASE_URL,
            headers=self.headers,
            data=json.dumps(data)
        )
        
        res = response.json()
        # print(res)
        
        if 'response' in res and len(res['response']) > 0:
            # Count response tokens
            response_tokens = self.count_word(res['response'])
            # Update total tokens
            self.total_tokens += prompt_tokens + response_tokens
            return res['response'].strip()
        else:
            raise ValueError("Failed to get a valid response from the API.")
    
    def get_total_tokens(self) -> int:
        """Get total tokens used"""
        return self.total_tokens
        
    def reset_token_count(self):
        """Reset token counter"""
        self.total_tokens = 0