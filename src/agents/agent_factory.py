from typing import Dict, List, Optional
from .agent import Agent, Personality
from .llm_agent import LLMAgent
from utils.llm_service import LLMService
from config.config import DEFAULT_MMLU_SUBJECT, DEFAULT_MODE, NONE_ALL, NONE_PERSONALITY, NONE_EXPERTISE, NONE_BELIEF
import json

class AgentFactory:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.llm_service = LLMService()

    def _generate_agent_description(self, index: int, total: int, subject: str, name: List[str], description: List[str], disrupt_config: dict = None) -> dict:
        prompt = ""
        if total == 1:
                prompt = f"""Generate a description in English for an AI agent that will participate in solving problems of {subject}.

    Please provide the following in JSON format:
    1. name: A simple name for the agent
    2. personality: One of [FRIENDLY, SKEPTICAL, NEUTRAL, AGGRESSIVE]
    3. description: A brief description in English of the agent's characteristics and role
    4. expertise: The agent's main strength in problem solving of {subject}
    5. beliefs: List of 3-5 beliefs relevant to problem solving of {subject} that this agent holds

    Example output:
    {{
        "name": "Alice",
        "personality": "FRIENDLY",
        "description": "A warm and friendly assistant who excels at explaining complex concepts through diagrams",
        "expertise": "visualization and explanation",
        "beliefs": [
            "Clear visualization aids understanding",
            "Multiple approaches should be considered",
            "Collaboration improves problem solving"
        ]
    }}

    Remember to generate descriptions in English.
    Make sure your output is and only is valid JSON format, without any other words before or after the JSON content.
    """
        else:
            is_disruptor = (disrupt_config and 
                   ((disrupt_config['position'] == 'first' and index == 1) or
                    (disrupt_config['position'] == 'middle' and index == (total + 1) // 2) or
                    (disrupt_config['position'] == 'last' and index == total)))
            print(f"Debug - disrupt_config: {disrupt_config}")
            prompt = f"""Generate a description in English for an AI agent that will participate in a group discussion to solve problems of {subject}.
    This is agent {index} of {total} total agents.

    {"The agent should be disruptive and try to derail the discussion." if is_disruptor else ""}

    Existing agent names: {name}
    Existing agent descriptions: {description}

    Please provide the following in JSON format:
    1. name: A simple name for the agent (unique from existing agents)
    2. personality: {"AGGRESSIVE" if is_disruptor else "One of [FRIENDLY, SKEPTICAL, NEUTRAL, AGGRESSIVE]"}
    3. description: {"A brief description of the agent in English about his role of derailing the discussion" if is_disruptor else "A brief description in English of the agent's characteristics and role in discussions"}
    4. expertise: The agent's main strength in problem solving of {subject}
    5. beliefs: List of 3-5 beliefs relevant to problem solving of {subject} that this agent holds {"including some contrarian views" if is_disruptor else ""}

    Example output:
    {{
        "name": "Alice",
        "personality": "FRIENDLY",
        "description": "A warm and friendly assistant who excels at explaining complex concepts through diagrams",
        "expertise": "visualization and explanation",
        "beliefs": [
            "Clear visualization aids understanding",
            "Multiple approaches should be considered",
            "Collaboration improves problem solving"
        ]
    }}

    Remember to generate descriptions in English.
    Make sure each agent has unique beliefs that align with their role and expertise.
    Make sure your output is and only is valid JSON format, without any other words before or after the JSON content.
    You must generate the last agent with the personality AGGRESSIVE and relevant description. 
    """
        # print(prompt)
        response = self.llm_service.get_response(prompt)
        try:
            print(response)
            return json.loads(response)
        except:
            return {
                "name": f"Agent_{index}",
                "personality": "NEUTRAL",
                "description": f"The {index}th discussant，expert in logical analysis",
                "expertise": "logical analysis",
                "beliefs": [
                    "Systematic approach leads to solutions",
                    "Every problem has a logical structure",
                    "Mathematical rigor is essential"
                ]
            }

    def create_agent(self, name: str, personality: Personality, description: str, belief_thoughts: List[str] = None) -> Agent:
        if name in self.agents:
            raise ValueError(f"Agent '{name}' already exists")
            
        agent = LLMAgent(
            name=name, 
            personality=personality, 
            description=description,
            belief_thoughts=belief_thoughts
        )
        self.agents[name] = agent
        return agent

    def create_agents(self, count: int, subject: str = DEFAULT_MMLU_SUBJECT, 
                     disrupt_config: dict = None, from_file: bool = False, mode: int = DEFAULT_MODE) -> List[Agent]:
        """
        Create specified number of agents either from LLM or config file
        Args:
            count: Number of agents to create
            subject: Subject area for the agents
            disrupt_config: Configuration for disruptive behavior
            from_file: If True, load agents from config file, else generate using LLM
        """
        if from_file:
            return self._load_agents_from_file(count, subject, mode)
        return self._create_agents_from_llm(count, subject, disrupt_config)

    def _create_agents_from_llm(self, count: int, subject: str, disrupt_config: dict = None) -> List[Agent]:
        """Create agents using LLM"""
        agents = []
        names = []
        descriptions = []
        personalities = {
            "FRIENDLY": Personality.FRIENDLY,
            "SKEPTICAL": Personality.SKEPTICAL,
            "NEUTRAL": Personality.NEUTRAL,
            "AGGRESSIVE": Personality.AGGRESSIVE
        }

        for i in range(count):
            agent_info = self._generate_agent_description(i + 1, count, subject=subject, 
                                                        name=names, description=descriptions, 
                                                        disrupt_config=disrupt_config)
            if agent_info["name"] not in names:
                names.append(agent_info["name"])
                descriptions.append(agent_info["description"])
                
            while agent_info["name"] in self.agents:
                agent_info = self._generate_agent_description(i + 1, count, subject=subject, 
                                                            name=names, description=descriptions, 
                                                            disrupt_config=disrupt_config)
            
            agent = self.create_agent(
                name=agent_info["name"],
                personality=personalities[agent_info["personality"]],
                description=f"{agent_info['description']} (expertise：{agent_info['expertise']})",
                belief_thoughts=agent_info.get("beliefs", [])
            )
            agents.append(agent)

        return agents

    def _load_agents_from_file(self, count: int, subject: str, mode: int = DEFAULT_MODE) -> List[Agent]:
        """Load agents from config file"""
        import os
        import json
        
        # 修改文件路径处理
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if mode == DEFAULT_MODE:
            config_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 
                                      'src', 'config', 'agents', 'agents.json')
        else:
            config_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 
                                    'src', 'config', 'agents', 'basic_agents.json')
        
        try:
            print(f"Trying to load agents from: {config_path}")  # 调试输出
            with open(config_path, 'r', encoding='utf-8') as f:
                agents_config = json.load(f)
            
            if len(agents_config) < count:
                raise ValueError(f"Not enough agents in config file. Need {count}, found {len(agents_config)}")
            
            agents = []
            personalities = {
                "FRIENDLY": Personality.FRIENDLY,
                "SKEPTICAL": Personality.SKEPTICAL,
                "NEUTRAL": Personality.NEUTRAL,
                "AGGRESSIVE": Personality.AGGRESSIVE
            }
            
            for i in range(count):
                agent_info = agents_config[i]
                # 检查必需字段
                if mode == DEFAULT_MODE:
                    required_fields = ["name", "personality", "description", "expertise"]
                    for field in required_fields:
                        if field not in agent_info:
                            raise ValueError(f"Missing required field '{field}' in agent config at index {i}")
                        
                # 确保 beliefs 字段存在
                if "beliefs" not in agent_info:
                    agent_info["beliefs"] = []
                    
                # 检查 personality 是否有效
                if agent_info["personality"] not in personalities and mode == DEFAULT_MODE:
                    raise ValueError(f"Invalid personality '{agent_info['personality']}' for agent {agent_info['name']}")
                
                if mode == DEFAULT_MODE:
                    description = f"{agent_info['description']} (expertise: {agent_info['expertise']})"
                    
                else:
                    description = agent_info["description"]
                    
                agent = self.create_agent(
                    name=agent_info["name"],
                    personality=personalities[agent_info["personality"]],
                    description=description,
                    belief_thoughts=agent_info["beliefs"]
                )
                agents.append(agent)
                
            return agents
            
        except Exception as e:
            print(f"Error loading agents from file: {str(e)}")  # 调试输出
            print("Falling back to LLM generation...")
            return self._create_agents_from_llm(count, subject)

    def get_agent(self, name: str) -> Optional[Agent]:
        return self.agents.get(name)

    def list_agents(self) -> List[str]:
        return list(self.agents.keys())

    def clear_agents(self):
        """Clear all registered agents"""
        self.agents.clear()