from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import requests

def get_prompts():
    
    planning_prompt = """SYSTEM DESCRIPTION: You are controlling a Minecraft Bot.
    RESTRICTIONS: You cannot build structures very well.
    TASK: Your task is to set a CURRENT GOAL for the Minecraft Bot. Keep it simple and based off of what we have in the inventory currently. Set the CURRENT GOAL, then give a step by step detailed description of how to accomplish this GOAL.
    CURRENT ENVIRONMENT: {current_environment}
    ### PREVIOUS ACTIONS ###
    {previous_actions}
    #######################
    ### BOT ACTIONS ###
    {bot_actions}
    #######################
    // Here you will complete the TASK by setting a simple CURRENT GOAL for the Minecraft Bot, while keeping the RESTRICTIONS in mind. Motivate this CURRENT GOAL with some of the possible BOT ACTIONS to accomplish this.
    CURRENT GOAL:"""

    return {'planning_prompt': planning_prompt}



def get_llms(query=''):
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")

        llm = ChatOpenAI(model='gpt-3.5-turbo-1106', temperature=0.3, api_key=openai_api_key)
        llm_4 = ChatOpenAI(model='gpt-4-1106-preview', temperature=0.3, api_key=openai_api_key)

        if query == '': prompts = get_prompts()
        else: prompts = get_prompts()[query]

        for key, value in prompts.items():
            # # save money by using gpt-3.5-turbo-1106
            # if key == 'decide_on_task' or key == 'synthesize_timestep' or key == 'reflect_on_action_outcome':
            #     prompts[key] = ChatPromptTemplate.from_template(value) | llm_4
            # else:
            #     prompts[key] = ChatPromptTemplate.from_template(value) | llm
            prompts[key] = ChatPromptTemplate.from_template(value) | llm_4

        return prompts