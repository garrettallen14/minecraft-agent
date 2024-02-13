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
Respond with your Question in the following JSON format:
    "reasoning": "detailed and thought through reasoning for your question to the Perception Module",
    "question": "Your question to the Perception Module"

# Think through your answer, and enter a Question to the Perception Module in JSON Format.
JSON Formatted Response:"""

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

Ignore this below if both the Proposed Action and Rejection Information are empty:
You may have also recently proposed an action to the bot, and the bot may have rejected it. Here is the information about the proposed action:
Proposed Action: {proposed_action}
Rejection Information: {additional_information}

Utilize all of this information to decide your next best action to complete your Goal.
Here are your choices for your next best action:
{bot_functions}

Respond in JSON format in the following structure:
    "reasoning": "detailed and thought through reasoning for your choice of action",
    "next_best_action": "Exact syntactic Python call to the function your are choosing to perform. This should be a string with the function name and variable inputs to be executed."

# Respond here in the JSON format, using "reasoning" then "next_best_action" as your keys.
JSON Formatted Response:"""

    gate_action = """As a Minecraft assistant, your role is to steer the bot away from actions that don't align with our strategy or the game's logic. When considering the next move, we must ensure it's the right step towards our objective, feasible with our current resources, and a fresh approach if previous attempts haven't worked.

Your mission is to evaluate a suggested action for the bot. Take into account:

The goal we're aiming for,
The current state of the game environment,
The outcomes of what we've tried before,
Our progress towards the objective.
You'll review a proposed action. Here's your task:

Analyze if the suggested action makes sense given our current situation and goals.
Check if we have the necessary tools and if the action is practical in the current game environment.
Ensure the action isn't a repeat of an unsuccessful past attempt that didn't move us closer to our goal.
Imagine the bot plans to mine iron but lacks the basic tools, like a wooden pickaxe. Your advice should guide it to first gather the essentials, like wood, to craft the needed tools before attempting to mine iron.

********* Relevant Informations: *********
Goal: {goal}
Current Environment: {current_environment}
Previous Action / Outcomes: {previous_action_outcomes}
Current Goal Progress: {current_goal_progress}
Proposed Action: {next_best_action}
*********************************

Please reply in JSON format, structured as follows:
"reasoning": Provide a detailed rationale for your verdict on the proposed action.
"gate": Indicate with TRUE or FALSE whether the action should proceed.
"description": If FALSE, explain why the action is not suitable, offering guidance that will be relayed back to the bot to improve its strategy.

Example:
Here's a template for how your response should look, adjusted for a scenario where the bot aims to efficiently collect resources but is about to skip necessary preliminary steps:
    "reasoning": "Considering the bot's current lack of tools, it must first focus on acquiring basic materials like wood to craft the necessary tools. Attempting to mine iron ore without even a wooden pickaxe is premature. The bot should locate nearby oak trees for wood, ensuring it has the means to create a pickaxe, thus aligning its actions with a logical progression in resource gathering.",
    "gate": "FALSE",
    "description": "The proposed action to mine iron ore is rejected because the bot does not possess the required tools for mining. It should first collect wood to craft a wooden pickaxe."

This template ensures the bot takes logical, efficient steps towards its goals without repeating ineffective actions or bypassing essential preparatory stages."""

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
    "reasoning": "detailed and thought through reasoning for your summary of changes in the environment and updated goal progress",
    "environment_changes": "detailed explanation of exactly how the action changed the environment. If no changes occured, explain why you think the function failed to do what it was supposed to.",
    "new_goal_progress": "updated goal progress based on the environment changes"

The bot will use the environment_changes value to see what effects on the inventory or environment he has had to determine the true outcome of his action. The new_goal_progress value will be used to update the goal progress based on the environment changes.
Note: In your reasoning, explore if environment_changes seem unchanged. If so, decide if the function simply failed to do what it was supposed to. If the function failed to have the effect it was supposed to, then in the environment_changes, explain why you think the function failed to do what it was supposed to do, so we can avoid this mistake in the future.

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
    "reasoning": "detailed and thought through reasoning for your decision whether or not to commit any information to memory",
    "memory1": "collection_name: information worth committing to memory",
    "memory2": "collection_name: other information worth committing to memory"

Remember: Reserve the core_memories collection for information that is fundamentally essential, and the important_locations for truly significant discoveries. Your discernment is key to maintaining the effectiveness and relevance of each collection. It is encouraged to respond to this prompt with an empty JSON formatted response if you believe none of the information is critical enough to be memorized.
# Only remember truly critical information. Your response will be directly executed upon submission, so you must ensure proper syntax and accuracy.
JSON Formatted Response:"""


    return {'generate_perception_query': generate_perception_query, 'generate_next_best_action': generate_next_best_action, 'gate_action': gate_action, 'summarize_environment_changes': summarize_environment_changes, 'gather_new_memories': gather_new_memories}



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