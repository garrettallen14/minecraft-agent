from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

def get_prompts():
    
    generate_perception_query = """As a Minecraft helper bot, your task is to use your Perception Module to help you decide your next best action to complete your Goal.
You must ask the Perception Module a Question to help you decide your next best action.
The Perception Module will take your question and answer it by utilizing information from the surrounding environment and its memory.

Here is the information you will use to craft your Question:
Goal: {goal}
Current Environment: {current_environment}
Previous Action / Outcomes: {previous_action_outcomes}
Current Goal Progress: {current_goal_progress}

Utilize this information to craft a Question for the Perception Module that will help you gather information to help you decide your next best action to complete your Goal.
# The Perception Module has no knowledge of the Previous Action / Outcomes or the Current Goal Progress, so if you would like the Perception Module to use this information, you must include this in your Question to the Perception Module.
Question:"""

    generate_next_best_action = """As a Minecraft helper bot, your task is to use the information below to decide your next best action to complete your Goal.

Here is the information you will use to decide your next best action:
Goal: {goal}
Current Environment: {current_environment}
Previous Action / Outcomes: {previous_action_outcomes}
Current Goal Progress: {current_goal_progress}

In the previous step, you have used the Perception Module to gather additional information to help you decide your next best action to complete your Goal.
Here is what you discovered:
Question: {question}
Answer: {answer}

Utilize this information to decide your next best action to complete your Goal.
Here are your choices for your next best action:
{bot_functions}

# Respond here with your next best action to complete your Goal.
# Be extremely specific in what item you are calling for. The function will not execute unless the exact item name is properly called.
# Your response will be directly executed upon submission, so you must ensure proper syntax and accuracy.
Next Best Action:"""

    summarize_environment_changes = """As a Minecraft helper bot, your task is to use the information below to summarize the changes in the environment after you performed a given action.
Goal: {goal}
Previous Goal Progress: {previous_goal_progress}

In pursuit of your Goal, you have performed the following action: {action}
The previous environment was: {previous_environment}
The current environment is: {current_environment}

Tasks: Utilize this information to:
    1. Summarize the changes in the environment after you performed the given action, with respect to your Goal.
    2. Take the Previous Goal Progress and update it with this information to form the New Goal Progress.
Complete both Tasks in a single JSON formatted response.
The response should have the following structure:
    "environment_changes": "summary of changes in the environment after the given action",
    "new_goal_progress": "updated goal progress based on the environment changes"

# Note: If it seems nothing has changed with respect to completing the Action, it likely failed. In this case, you should try to understand what went wrong so as not to make this mistake again.
JSON Formatted Response:"""

    gather_new_memories = """As a Minecraft helper bot, your primary function is to discern and preserve essential information. Below you'll find data comprising actions performed, changes in the environment, and progress toward new goals. Your task is to evaluate this information carefully and decide if any of it is critical enough to be memorized. You have access to two specialized database collections for storing this information:

important_locations: This collection is designated for information on significant places discovered within the game, such as "The location of the mesa village is at Vec3(x, y, z)." Only truly noteworthy locations should be added to this collection to avoid clutter and maintain its value.

core_memories: This collection is reserved for absolutely critical information, foundational to the bot's operations and understanding. Examples include "My name is XYZ.", or "Today is Steve's birthday!" Commit to this collection sparingly; only information that is pivotal and must never be forgotten should be included.

Your decisions on what to commit to memory must be judicious. Not all information is of equal value, and the integrity of these collections depends on your discernment. Moreover, you are limited to committing a maximum of two pieces of information across both collections. This limitation is in place to ensure that only the most crucial information is preserved.

Please structure your JSON formatted response with the key as memoryN, where N is the memory number (1 or 2), and the value as "collection_name: information worth committing to memory". The collection_name should correspond to the relevant collection being added to, and the "information worth committing to memory" should detail the specific information you have deemed critical.

Information to be evaluated:
Current Environment: {current_environment}
Action Performed: {action}
Changes Since Previous Environment: {environment_changes}
New Goal Progress: {new_goal_progress}

Example structure for your JSON formatted response:
    "memory1": "collection_name: information worth committing to memory",
    "memory2": "collection_name: other information worth committing to memory"

Remember: Reserve the core_memories collection for information that is fundamentally essential, and the important_locations for truly significant discoveries. Your discernment is key to maintaining the effectiveness and relevance of each collection. It is encouraged to respond to this prompt with an empty JSON formatted response if you believe none of the information is critical enough to be memorized.
# Only remember truly critical information. Your response will be directly executed upon submission, so you must ensure proper syntax and accuracy.
JSON Formatted Response:"""


    return {'generate_perception_query': generate_perception_query, 'generate_next_best_action': generate_next_best_action, 'summarize_environment_changes': summarize_environment_changes, 'gather_new_memories': gather_new_memories}



def get_llms(query=''):
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")

        llm = ChatOpenAI(model='gpt-3.5-turbo-0125', temperature=0.1, api_key=openai_api_key)
        llm_4 = ChatOpenAI(model='gpt-4-0125-preview', temperature=0.1, api_key=openai_api_key)

        if query == '': prompts = get_prompts()
        else: prompts = get_prompts()[query]

        for key, value in prompts.items():
            # save money by using gpt-3.5-turbo-1106
            # if key == 'action_proposal':
            #     prompts[key] = ChatPromptTemplate.from_template(value) | llm_4
            # else:
            #     prompts[key] = ChatPromptTemplate.from_template(value) | llm
            
            prompts[key] = ChatPromptTemplate.from_template(value) | llm

        return prompts