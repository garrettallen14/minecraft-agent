from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

def get_prompts():

    create_goal_and_plan = """The Minecraft Bot proposed a new goal.
Your task is to ensure that it is reasonable and achievable, then generate a heuristic plan to achieve the goal.
The plan must be based on the current environment and inventory to ensure that it is feasible.

The proposed goal is: {goal}.
The current environment is: {current_environment}.

The previous goal was: {previous_goal}.
The key lessons learned from the previous goal were: {previous_goal_lessons_learned}.

Utilize this information to update the proposed goal and generate a tentative plan.
Respond in the following JSON format:
    "reasoning": "Your thought process for how you will go about updating the goal and creating the plan.",
    "new_goal": "The updated goal."
    "plan": "The plan to achieve the updated goal."

JSON Formatted Response:"""

    create_goal = """The Minecraft Bot proposed a new goal. 
Your task is to ensure that it is reasonable and achievable.
If it is unreasonable given the current situation, update the proposed goal based on the gathered information.

The proposed goal is: {goal}.

The current environment is: {current_environment}.

The previous goal was: {previous_goal}.
The key lessons learned from the previous goal were: {previous_goal_lessons_learned}.

Utilize this information to update the proposed goal.s
Respond in the following JSON format:
    "reasoning": "Your thought process for how you will go about updating the goal and creating the plan.",
    "new_goal": "The updated goal."

JSON Formatted Response:"""

    update_goal = """The Minecraft Bot proposed a new goal.
You have used the perception and memory modules to gather information about the new goal and the environment.
You are to update the proposed goal based on the gathered information and generate a plan to achieve the updated goal.

The proposed goal is: {proposed_goal}.
Perception Module's input: {perception_response}.
Memory Module's input: {memory_response}.

Utilize this information to update the proposed goal and generate a tentative plan.
Respond in the following JSON format:
    "reasoning": "Your thought process for how you will go about updating the goal and creating the plan.",
    "new_goal": "The updated goal."
    "plan": "The plan to achieve the updated goal."

JSON Formatted Response:"""

    update_plan = """The Minecraft Bot has proposed a new plan to achieve a goal.
You have used the perception and memory modules to gather information about the new plan and the environment.
You are to improve the proposed plan based on the gathered information.

The current environment is: {current_environment}.

The goal is: {goal}.
The proposed plan is: {proposed_plan}.
Perception Module's input: {perception_response}.
Memory Module's input: {memory_response}.

Utilize this information to update the proposed plan.
Respond in the following JSON format:
    "reasoning": "Your thought process for how you will go about updating the plan.",
    "plan": "The improved plan."

JSON Formatted Response:"""


    return {'create_goal': create_goal, 'update_goal': update_goal, 'update_plan': update_plan}



def get_llms(query=''):
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")

        llm = ChatOpenAI(model='gpt-3.5-turbo-0125', temperature=0.1, api_key=openai_api_key)
        llm_4 = ChatOpenAI(model='gpt-4-0125-preview', temperature=0.1, api_key=openai_api_key)

        if query == '': prompts = get_prompts()
        else: prompts = get_prompts()[query]

        for key, value in prompts.items():
            # save money by using gpt-3.5-turbo-1106
            if key == 'generate_next_best_action':
                prompts[key] = ChatPromptTemplate.from_template(value) | llm_4
            else:
                prompts[key] = ChatPromptTemplate.from_template(value) | llm
            
            # prompts[key] = ChatPromptTemplate.from_template(value) | llm

        return prompts