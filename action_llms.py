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

    generate_next_best_action = """You are an extremely helpful advanced Minecraft helper, providing guidance to a bot to help it complete its Goal.
As a Minecraft helper, your task is to use the provided image and information below to think through the situation, then decide the next best action to complete the Goal.

Here is the information you will use to decide the next best action:
Goal: {goal}
Current Environment: {current_environment}
Previous Action / Outcomes: {previous_action_outcomes}
Current Goal Progress: {current_goal_progress}

You may have proposed an action to the bot in the previous step.
If the Rejected Proposal Actions field is filled, you must explain in detail exactly why the proposed action was rejected and what the bot should do instead.
Rejected Proposed Actions: {proposed_action}

Utilize all of this information to decide your next best action to complete your Goal.
Here are your choices for your next best action:
{bot_functions}

Respond in JSON format in the following structure:
    "reasoning": "detailed and thought through reasoning for your choice of action. ensure you decide on what the absolute best action is to complete your goal.",
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
You must ensure that the variable names are proper item names which exist in Minecraft. For example, if the bot is proposing to craft 'planks', you must reject this action as the correct variable name is 'oak_planks', or 'spruce_planks', etc.

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

    summarize_environment_changes = """As a Minecraft assistant, your task is to analyze the impact of a specific action towards achieving your goal. Provide a summary of the action's outcome and update the goal progress based on this impact.

Input details:
- Goal: The objective you're aiming to achieve.
- Previous Goal Progress: The progress made towards the goal before this action.
- Action: The action you've taken to advance towards the goal.
- Previous Environment: The state of the environment before the action.
- Current Environment: The state of the environment after the action.

Goal: {goal}
Previous Goal Progress: {previous_goal_progress}
Action: {action}
Previous Environment: {previous_environment}
Current Environment: {current_environment}

Output Requirements:
1. Summarize the outcome of the action, assessing its impact on reaching the goal and identifying any shortcomings in achieving the desired results.
2. Update the goal progress, incorporating the impact of the action.

Provide your analysis in a JSON format with two keys: "action_outcome" and "new_goal_progress", each containing concise, detailed explanations. Limit your total response to 200 tokens.

Example JSON Response Structure:
  "action_outcome": "Explanation of the action's effectiveness and any areas where it fell short.",
  "new_goal_progress": "Updated progress towards the goal, including next steps."
"""

    gather_new_memories = """As a Minecraft helper bot, your primary function is to discern and preserve essential information. Below you'll find data comprising actions performed, changes in the environment, and progress toward new goals. Your task is to evaluate this information carefully and decide if any of it is critical enough to be memorized. You have access to two specialized database collections for storing this information:

important_locations: This collection is designated for information on significant places discovered within the game, such as "The location of the mesa village is at Vec3(x, y, z)." Only truly noteworthy locations should be added to this collection to avoid clutter and maintain its value. Locations of crafting tables and chests are particularly important.

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

    key_lessons = """The Minecraft Bot has finished trying to accomplish a goal.
Your task is to look at how the Bot attempted to accomplish the goal at every single timestep and determine what key lessons were learned from the bot's actions and the environment.
These lessons will inform future planning and strategies for the bot to accomplish its goals.
Be critical and thoughtful in your analysis, and ensure that the lessons are actionable and can be used to improve the bot's future performance.
Goal: {goal}
Previous Goal Progress: {previous_goal_progress}
Previous Action / Outcomes: {previous_action_outcomes}
RESPOND IN JSON FORMAT:
    "reasoning": "detailed and thought through reasoning for your key lessons learned",
    "key_lessons": "key lessons learned from the bot's actions and the environment"

Respond here in the JSON format, using "reasoning" then "key_lessons" as your keys.
JSON Formatted Response:"""


    return {'generate_perception_query': generate_perception_query, 'generate_next_best_action': generate_next_best_action, 'gate_action': gate_action, 'summarize_environment_changes': summarize_environment_changes, 'gather_new_memories': gather_new_memories, 'key_lessons': key_lessons}



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