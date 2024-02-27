from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

def get_prompts():
    
    select_module = """You are playing the game Minecraft. You have been tasked with selecting the best module for a given situation.
    
The current environment is: {current_environment}.
The current goal is: {goal}.
The plan is: {plan}.
The current goal progress is: {goal_progress}.
The previous action and outcomes in attempting to accomplish the goal were: {previous_action_outcomes}.


Here are the modules you can choose from:
{modules}

In the previous timestep, you performed the following Module request: {previous_module_outcome}.

Please think about the current environment, goal, and previous module and then choose the best module for the current situation.
You must respond in the following JSON format:
    "reasoning": "detailed reasoning behind your decision to choose the next module",
    "exact syntax of the module name": "the input to the module you have chosen"
Note: The key for "exact syntax of the module name" must be in the exact syntax of one of the modules listed above, and the value of this key must be a string which is the input to the module you have chosen.

******************
Example:
    "reasoning": "...",
    "update_goal": "description of the proposed new goal you are inputting to the update_goal module. keep goals reasonable and easily achievable"
Example:
    "reasoning": "...",
    "ask_memories": "the exact question you are inputting to the ask_memories module"
Example:
    "reasoning": "...",
    "perform_action": "a description of the simple action you would like perform_action module to perform"
******************

# Configuration: When stuck in a loop, the Agent will opt for the "update_goal" module to change the goal. This will allow the Agent to break out of the loop and continue with the game.
JSON Formatted Response:"""


    return {'select_module': select_module}



def get_llms(query=''):
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")

        llm = ChatOpenAI(model='gpt-3.5-turbo-0125', temperature=0.1, api_key=openai_api_key)
        llm_4 = ChatOpenAI(model='gpt-4-0125-preview', temperature=0.1, api_key=openai_api_key)

        if query == '': prompts = get_prompts()
        else: prompts = get_prompts()[query]

        for key, value in prompts.items():
            # save money by using gpt-3.5-turbo-1106
            if key == 'generate_next_best_action' or key == 'key_lessons':
                prompts[key] = ChatPromptTemplate.from_template(value) | llm_4
            else:
                prompts[key] = ChatPromptTemplate.from_template(value) | llm
            
            # prompts[key] = ChatPromptTemplate.from_template(value) | llm

        return prompts