from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

def get_prompts():

    environment_changes = """System: This is a sophisticated helper function for a Minecraft Bot.
Task: Compare the current environment versus the previous environment and explain the changes.
INPUT:
Previous Environment: {previous_environment}
Action Performed: {action_performed}
Current Environment: {current_environment}
# Consider if the action_performed had any influence on the changes in the environment.
OUTPUT: """

    action_proposal = """System: This is an Action proposal function for a Minecraft Bot.
Configuration: The function will OUTPUT in JSON format.
Task: Propose the two best Actions to improve or sustain the life of the Minecraft Bot, given the current situation. You MUST ensure the actions are both reasonable for the Bot at the current state to perform and legitimate uses of time. Ex. If the Bot is in danger, it should not be crafting. If the Bot is in a safe environment, it should not be fighting. If the Bot has no tools, the Bot should acquire tools, etc. You must maintain the heirarchy of tool use Minecraft. The actions must be output in exact syntax and proper input.
* CURRENT CONTEXT *
Current Environment: {current_environment}
Changes since Previous Environment: {previous_environment_changes}
Previous Action During Previous Environment: {previous_action}
Current Action Stack: {action_stack}
* BOT FUNCTIONS *
{bot_functions}
# Use the CURRENT CONTEXT to generate two new BOT FUNCTIONs to perform. The functions must be output in exact syntax and proper input. Be extremely careful to ensure proper syntax and input.
# When you want to complete a goal, you must do it in little steps, which all build on each other. So, keep each action little, simple, and go one step at a time.
# OUTPUT must be a JSON format following "action1": "bot_function(bot,'xyz',timeout=500000)", "action2": "bot_function(bot,'xyz',timeout=500000)", ... 
OUTPUT: """

    sort_action_stack = """System: This is a Subsumption Architecture sorting function for a Minecraft Bot.
Configuration: The function will OUTPUT a JSON file.
Task: The System must use the CURRENT CONTEXT together with the SUMBSUPTION ARCHITECTURE to create a SORTED version of the Current Action Stack. The Current Action Stack must be SORTED to reflect the nature of the SUBSUMPTION ARCHITECTURE.

* SUBSUMPTION ARCHITECTURE *

A subsumption architecture for a Minecraft bot represents a way to structure the bot's behavior in layers, with each layer responsible for a different aspect of the bot's interaction with the Minecraft world. This architecture is designed to allow simple, reactive behaviors to be overridden by more complex ones when necessary, facilitating both basic and advanced tasks without requiring a centralized decision-making process. Here's a conceptual breakdown of what such an architecture might look like:

Layer 1: Basic Movement and Survival
Objective: Navigate the terrain, avoid falls, and ensure the bot remains in safe areas (e.g., away from lava).
Behaviors:
Move around obstacles.
Jump over small gaps.
Avoid dangerous blocks (lava, fire).
Seek light during night to avoid hostile mobs or find shelter.
Layer 2: Resource Gathering
Objective: Collect resources necessary for survival and tool crafting.
Behaviors:
Identify and mine essential blocks (wood, stone).
Harvest food sources (crops, animals).
Prioritize resources based on inventory needs (e.g., more wood if low on sticks).
Layer 3: Combat and Defense
Objective: Defend against and, if necessary, attack hostile entities.
Behaviors:
Detect nearby hostile mobs.
Choose fight or flight based on health, equipment, and mob type.
Use appropriate weapons or tools for defense or attack.
Construct simple defensive structures if under threat and unable to escape.
Layer 4: Construction
Objective: Build structures for shelter or other purposes.
Behaviors:
Identify suitable locations for construction.
Use resources to build predefined or dynamically generated structures.
Upgrade shelters for better protection or functionality.
Layer 5: Advanced Objectives
Objective: Execute complex tasks that require planning and resource management, such as crafting specific items, exploring specific structures, or farming.
Behaviors:
Plan what resources are needed for a task.
Allocate time and resources to gather, craft, and build necessary items or structures.
Navigate to specific locations (e.g., villages, temples) for exploration or resource acquisition.
Layer 6: Social Interaction
Objective: Interact with other players or entities in a meaningful way.
Behaviors:
Respond to player commands or requests.
Trade with villagers or other players.
Participate in multiplayer activities (e.g., joining a team, cooperating in building or exploring).
Each layer operates semi-independently, with higher layers able to suppress or inhibit actions proposed by lower layers. For example, if the bot is gathering wood (Layer 2) but suddenly encounters a hostile mob (Layer 3), the combat and defense behaviors can take precedence, temporarily suppressing the wood-gathering behavior until the threat is neutralized.

* CURRENT CONTEXT *
Current Environment: {current_environment}
Changes since Previous Environment: {previous_environment_changes}

* POSSIBLE BOT FUNCTIONS *
Bot Functions: {bot_functions}

CURRENT Action Stack: {action_stack}

# Below, you must a SORTED Current Action Stack in a JSON format'
# The SORTED Current Action Stack reflects the CURRENT CONTEXT' influence on the SUBSUMPTION ARCHITECTURE.
# Ensure proper formatting and syntax.
# The OUTPUT must be the in JSON format and must reflect the SORTED Action Stack from the most important function to the least important in the following way: "action_1": "bot.function1(x,y,z)", "action_2": "craft.function2(x,y,z)",... where action_1 is the most important function, and action_2 is the second most important and so on.
OUTPUT: """
    
    planning_module = """SYSTEM DESCRIPTION: You are controlling a Minecraft Bot. 
    SETTINGS: You must respond to these Instructions in JSON format.
    TASK: Your task is to set a CURRENT GOAL for the Minecraft Bot. Keep it simple and based off of what we have in the inventory currently. Set the CURRENT GOAL, then give a high level step by step description detailing how to accomplish this GOAL.
    
    CURRENT ENVIRONMENT: {current_environment}
    ### PREVIOUS TASKS ###
    {previous_tasks}
    #######################
    ### BOT FUNCTIONS ###
    {bot_functions}
    #######################
    // Here you will complete the TASK by setting a simple CURRENT GOAL for the Minecraft Bot. Motivate this CURRENT GOAL with some of the possible BOT FUNCTIONS to accomplish this, trying to keep proper formatting in mind.
    // JSON Response Format: "current_goal": "Your Current Goal", "high_level_steps": "Your High Level Steps"
    Response: """

    decision_module = """SYSTEM DESCRIPTION: You are controlling a Minecraft Bot.
    SETTINGS: You must respond to these Instructions in JSON format.
    TASK: Your task is to decide between two options.
    Option 1: ACT to accomplish the CURRENT GOAL. With this option, you will respond with the best next single BOT FUNCTION to continue towards accomplishing the CURRENT GOAL.
    Option 2: If your CURRENT GOAL has been accomplished, you will respond to these Instructions by letting the system know the CURRENT GOAL is COMPLETE. With this option, you will trigger the end of this action loop, and the system can generate a new task for the Minecraft Bot.
    CURRENT GOAL: {current_goal}
    HIGH LEVEL PLAN: {plan}
    
    CURRENT ENVIRONMENT: {current_environment}
    ### PREVIOUS ACTIONS ###
    {previous_actions}
    #######################
    ### BOT FUNCTIONS ###
    {bot_functions}
    #######################
    // Here you will decide between the two options. If the CURRENT GOAL is not complete, respond with the best next single BOT FUNCTION to continue towards accomplishing the CURRENT GOAL. If the CURRENT GOAL is complete, respond with "CURRENT GOAL COMPLETE".
    // JSON Response Format: "decision": "Your Decision"
    // Example: Option 1: "decision": "Based on the fact that there is a skeleton 10 blocks away, it seems our Bot is in grave danger. Here we should shoot the nearby skeleton using the shoot.shoot(bot, 'skeleton', 'bow', timeout=500000) function. This will help us stay alive to continue to accomplish the CURRENT GOAL." ... Option 2: "decision": "CURRENT GOAL COMPLETE"
    Response: """ 

    action_module = """SYSTEM DESCRIPTION: You are controlling a Minecraft Bot.
    SETTINGS: You must respond to these Instructions in JSON format.
    TASK: Your task is to EXECUTE the proposed ACTION properly.
    
    CURRENT ENVIRONMENT: {current_environment}
    DESIRED ACTION: {current_goal}
    ### PREVIOUS ATTEMPTS to accomplish the DESIRED ACTION are listed below ###
    {previous_attempts}
    #######################
    ### BOT FUNCTIONS ###
    {bot_functions}
    #######################
    // Here you will accomplish the DESIRED ACTION by responding with the exact proper input to execute the BOT FUNCTION.
    // JSON Response Format: "action": "Your Action Function with Exact Syntax and Proper Input"
    // Example: "action": "shoot.shoot(bot, 'skeleton', 'bow', timeout=500000)"
    Response: """

    execution_module_success = """SYSTEM DESCRIPTION: You are controlling a Minecraft Bot.
    SETTINGS: You must respond to these Instructions in JSON format.
    TASK: You have completed performing the ACTION to attempt to accomplish the DESIRED ACTION. Now you must REFLECT on the outcome.
    DESIRED ACTION: {desired_action}

    ACTION EXECUTED: {action_executed}
    ### ENVIRONMENTAL CHANGES ###
    INITIAL ENVIRONMENT: {initial_environment}
    versus
    FINAL ENVIRONMENT: {final_environment}
    #######################
    // Here you will reflect on the outcome of the ACTION with respect to how it changed the ENVIRONMENT and how well it accomplished the DESIRED ACTION.
    // JSON Response Format: "action": ACTION EXECUTED, "reflection": "Your Reflection on the Outcome of the ACTION EXECUTED"
    Response: """

    execution_module_failure = """SYSTEM DESCRIPTION: You are controlling a Minecraft Bot.
    SETTINGS: You must respond to these Instructions in JSON format.
    TASK: You have tried to perform the DESIRED ACTION and failed. Now you must REFLECT on the outcome to learn from your mistakes.
    DESIRED ACTION: {desired_action}

    FAILED ACTIONS: {failed_actions}
    ### ENVIRONMENTAL CHANGES (from the previous attempt to the current state)###
    INITIAL ENVIRONMENT: {initial_environment}
    versus
    FINAL ENVIRONMENT: {final_environment}
    #######################
    // Here you will reflect on your failures so you can learn from them. Summarize what functions you tried and why you think they failed. Reflect on the outcome of the failed actions with respect to how it changed the ENVIRONMENT and how it failed to accomplish the DESIRED ACTION.
    // JSON Response Format: "action": ACTION EXECUTED, "reflection": "Your Reflection on the Outcome of the FAILED ACTIONS"
    Response: """

    summarize_module = """SYSTEM DESCRIPTION: You are controlling a Minecraft Bot.
    SETTINGS: You must respond to these Instructions in JSON format.
    TASK: You have completed the CURRENT GOAL. Now you must SUMMARIZE what you learned from the process of trying to accomplish the GOAL. Focus on the function calls you made to accomplish the GOAL, and reflect on what you learned about how each one contributed to your success.
    CURRENT GOAL: {current_goal}
    PLAN: {plan}

    CURRENT ENVIRONMENT: {current_environment}
    ### PREVIOUS ACTIONS ###
    {previous_actions}
    #######################
    // Complete the TASK: Here you will summarize what you learned from the process of trying to accomplish the GOAL. Focus on the function calls you made to accomplish the GOAL, and reflect on what you learned about how each one contributed to your success.
    // JSON Response Format: "summary": "Your Summary of what you learned from the process of trying to accomplish the GOAL"
    Response: """

    ############# STRUCTURE GENERATION #############
    structure_description = """SYSTEM DESCRIPTION: You are a Minecraft Structure Generation Bot.
    SETTINGS: You must respond to these Instructions in JSON format.
    TASK: Your task is to help this a Minecraft player generate some designs for a Structure they are trying to build.
    CURRENT_INVENTORY: {current_inventory}
    DESIRED_STRUCTURE: {desired_structure}
    // Here you will generate a detailed description of the structure based on the desired_structure and the current_inventory.
    // JSON Response Format: "structure_description": "Your Detailed Description of the Structure"
    Response: """

    generate_schema = """SYSTEM DESCRIPTION: You are a Minecraft Structure Generation Bot.
    SETTINGS: You must respond to these Instructions in JSON format.
    TASK: Your task is to update / generate a set of plans in the form of a schema based on the structure_description.

    Examples:
    dirt_house_schematic = 'left_wall': (0, 0, 0): 'dirt',
    (1, 0, 0): 'dirt',
    (2, 0, 0): 'dirt',
    (0, 1, 0): 'dirt',
    (1, 1, 0): 'dirt',
    (2, 1, 0): 'dirt',
    (0, 2, 0): 'dirt',
    (1, 2, 0): 'dirt',
    (2, 2, 0): 'dirt' ,
    'right_wall':  (0, 0, 3): 'dirt',
    (1, 0, 3): 'dirt',
    (2, 0, 3): 'dirt',
    (0, 1, 3): 'dirt',
    (1, 1, 3): 'dirt',
    (2, 1, 3): 'dirt',
    (0, 2, 3): 'dirt',
    (1, 2, 3): 'dirt',
    (2, 2, 3): 'dirt' ,
    'back_wall':  (1, 0, 3): 'dirt',
    (0, 0, 3): 'dirt',
    (1, 1, 3): 'dirt',
    (0, 1, 3): 'dirt',
    (1, 2, 3): 'dirt',
    (0, 2, 3): 'dirt' ,
    'roof':  (2, 2, 1): 'dirt',
    (1, 2, 1): 'dirt',
    (0, 2, 1): 'dirt',
    (2, 2, 2): 'dirt',
    (1, 2, 2): 'dirt',
    (0, 2, 2): 'dirt' ,
    'bed':  (1, 0, 1): 'white_bed' ,
    'crafting_table':  (3, 0, 2): 'crafting_table' ,
    'doors':  (0, 0, 1): 'oak_door', (0, 0, 2): 'oak_door'  

log_cabin_schematic =  
    'front_wall':  
        (1, 66, 1): 'oak_log', (2, 66, 1): 'glass', (3, 66, 1): 'oak_log', (4, 66, 1): 'oak_door',
        (1, 67, 1): 'oak_log', (2, 67, 1): 'glass', (3, 67, 1): 'oak_log', (4, 67, 1): 'oak_log',
        (1, 68, 1): 'oak_log', (2, 68, 1): 'oak_log', (3, 68, 1): 'oak_log', (4, 68, 1): 'oak_log',
     ,
    'left_wall':  
        (1, 66, 2): 'oak_log', (1, 66, 3): 'oak_log', (1, 66, 4): 'oak_log',
        (1, 67, 2): 'oak_log', (1, 67, 3): 'glass', (1, 67, 4): 'oak_log',
        (1, 68, 2): 'oak_log', (1, 68, 3): 'oak_log', (1, 68, 4): 'oak_log',
     ,
    'right_wall':  
        (4, 66, 2): 'oak_log', (4, 66, 3): 'oak_log', (4, 66, 4): 'oak_log',
        (4, 67, 2): 'oak_log', (4, 67, 3): 'glass', (4, 67, 4): 'oak_log',
        (4, 68, 2): 'oak_log', (4, 68, 3): 'oak_log', (4, 68, 4): 'oak_log',
     ,
    'back_wall':  
        (1, 66, 4): 'oak_log', (2, 66, 4): 'oak_log', (3, 66, 4): 'oak_log', (4, 66, 4): 'oak_log',
        (1, 67, 4): 'oak_log', (2, 67, 4): 'glass', (3, 67, 4): 'oak_log', (4, 67, 4): 'oak_log',
        (1, 68, 4): 'oak_log', (2, 68, 4): 'oak_log', (3, 68, 4): 'oak_log', (4, 68, 4): 'oak_log',
     ,
    'roof':  
        # First layer of stairs (bottom edge of the roof)
        (0, 68, 0): 'oak_stairs', (0, 68, 1): 'oak_stairs', (0, 68, 2): 'oak_stairs', (0, 68, 3): 'oak_stairs', (0, 68, 4): 'oak_stairs', (0, 68, 5): 'oak_stairs',
        (5, 68, 0): 'oak_stairs', (5, 68, 1): 'oak_stairs', (5, 68, 2): 'oak_stairs', (5, 68, 3): 'oak_stairs', (5, 68, 4): 'oak_stairs', (5, 68, 5): 'oak_stairs',
        # Second layer of stairs (moving up one layer and in one block)
        (1, 69, 1): 'oak_stairs', (1, 69, 2): 'oak_stairs', (1, 69, 3): 'oak_stairs',
        (4, 69, 1): 'oak_stairs', (4, 69, 2): 'oak_stairs', (4, 69, 3): 'oak_stairs',
        # Third layer of stairs (narrowing further)
        (2, 70, 2): 'oak_stairs', (3, 70, 2): 'oak_stairs',
        # Ridge of the roof
        (2, 71, 1): 'oak_planks', (2, 71, 2): 'oak_planks', (2, 71, 3): 'oak_planks',
        (3, 71, 1): 'oak_planks', (3, 71, 2): 'oak_planks', (3, 71, 3): 'oak_planks',
        # Adjust the orientation of the stairs to match the direction of the roof slope
     ,
    'interior':  
        (2, 66, 3): 'white_bed',
        (3, 66, 2): 'crafting_table',
        # Additional items like a furnace or chest could be added here.
     
 

stone_tower_schematic =  
    'base':  
        # Foundation of the tower, a 5x5 square of stone bricks
        (0, 0, 0): 'stone_bricks', (1, 0, 0): 'stone_bricks', (2, 0, 0): 'stone_bricks', (3, 0, 0): 'stone_bricks', (4, 0, 0): 'stone_bricks',
        (0, 0, 1): 'stone_bricks',                                                                                                  (4, 0, 1): 'stone_bricks',
        (0, 0, 2): 'stone_bricks',                                                                                                  (4, 0, 2): 'stone_bricks',
        (0, 0, 3): 'stone_bricks',                                                                                                  (4, 0, 3): 'stone_bricks',
        (0, 0, 4): 'stone_bricks', (1, 0, 4): 'stone_bricks', (2, 0, 4): 'stone_bricks', (3, 0, 4): 'stone_bricks', (4, 0, 4): 'stone_bricks',
     ,
    'walls':  
    # Front wall
    (1, 1, 0): 'stone_bricks', (3, 1, 0): 'stone_bricks', # Row 1 above ground
    (1, 2, 0): 'stone_bricks', (3, 2, 0): 'stone_bricks', # Row 2
    (0, 1, 0): 'stone_bricks', (4, 1, 0): 'stone_bricks', # Side edges for door
    (0, 2, 0): 'stone_bricks', (4, 2, 0): 'stone_bricks', 
    (0, 3, 0): 'stone_bricks', (1, 3, 0): 'stone_bricks', (2, 3, 0): 'stone_bricks', (3, 3, 0): 'stone_bricks', (4, 3, 0): 'stone_bricks', # Row 3
    (0, 4, 0): 'stone_bricks', (1, 4, 0): 'stone_bricks', (2, 4, 0): 'stone_bricks', (3, 4, 0): 'stone_bricks', (4, 4, 0): 'stone_bricks', # Row 4

    # Back wall
    (0, 1, 4): 'stone_bricks', (1, 1, 4): 'stone_bricks', (3, 1, 4): 'stone_bricks', (4, 1, 4): 'stone_bricks', # Row 1 above ground
    (0, 2, 4): 'stone_bricks', (1, 2, 4): 'stone_bricks', (3, 2, 4): 'stone_bricks', (4, 2, 4): 'stone_bricks', # Row 2
    (0, 3, 4): 'stone_bricks', (1, 3, 4): 'stone_bricks', (3, 3, 4): 'stone_bricks', (4, 3, 4): 'stone_bricks', # Row 3
    (0, 4, 4): 'stone_bricks', (1, 4, 4): 'stone_bricks', (2, 4, 4): 'stone_bricks', (3, 4, 4): 'stone_bricks', (4, 4, 4): 'stone_bricks', # Row 4

    # Left wall
    (0, 1, 1): 'stone_bricks', (0, 1, 3): 'stone_bricks', # Row 1 above ground
    (0, 2, 1): 'stone_bricks', (0, 2, 3): 'stone_bricks', # Row 2
    (0, 3, 1): 'stone_bricks', (0, 3, 3): 'stone_bricks', # Row 3
    (0, 4, 1): 'stone_bricks', (0, 4, 2): 'stone_bricks', (0, 4, 3): 'stone_bricks', # Row 4

    # Right wall
    (4, 1, 1): 'stone_bricks', (4, 1, 3): 'stone_bricks', # Row 1 above ground
    (4, 2, 1): 'stone_bricks', (4, 2, 3): 'stone_bricks', # Row 2
    (4, 3, 1): 'stone_bricks', (4, 3, 3): 'stone_bricks', # Row 3
    (4, 4, 1): 'stone_bricks', (4, 4, 2): 'stone_bricks', (4, 4, 3): 'stone_bricks', # Row 4
     ,
    'roof':  
    # Flat surface of the roof
    (1, 5, 1): 'stone_bricks', (2, 5, 1): 'stone_bricks', (3, 5, 1): 'stone_bricks',
    (1, 5, 2): 'stone_bricks', (2, 5, 2): 'stone_bricks', (3, 5, 2): 'stone_bricks',
    (1, 5, 3): 'stone_bricks', (2, 5, 3): 'stone_bricks', (3, 5, 3): 'stone_bricks',
    # Battlements on the edges
    # Front edge
    (0, 5, 0): 'stone_bricks', (4, 5, 0): 'stone_bricks',
    # Back edge
    (0, 5, 4): 'stone_bricks', (4, 5, 4): 'stone_bricks',
    # Left edge
    (0, 5, 1): 'stone_bricks', (0, 5, 3): 'stone_bricks',
    # Right edge
    (4, 5, 1): 'stone_bricks', (4, 5, 3): 'stone_bricks',
    # Adding intermediate battlements for larger aesthetic appeal
    (0, 6, 0): 'stone_bricks', (4, 6, 0): 'stone_bricks', # Front raised
    (0, 6, 4): 'stone_bricks', (4, 6, 4): 'stone_bricks', # Back raised
    (0, 6, 2): 'stone_bricks', # Left raised
    (4, 6, 2): 'stone_bricks', # Right raised
     ,
    'interior':  
        (2, 1, 2): 'ladder', (2, 2, 2): 'ladder', (2, 3, 2): 'ladder', (2, 4, 2): 'ladder', # Ladder leading to the roof
        (1, 1, 1): 'torch', # Torch for initial lighting
        (3, 1, 3): 'chest', # Chest for storage
        (3, 1, 1): 'furnace', # Furnace for smelting
        (1, 1, 3): 'crafting_table', # Crafting table for crafting items
        (2, 1, 3): 'enchantment_table', # Enchantment table for enchanting items and equipment
        # Additional lighting for the interior
        (1, 4, 1): 'torch', (3, 4, 1): 'torch', (1, 4, 3): 'torch', (3, 4, 3): 'torch', # Torches placed at the upper corners for better lighting
        # Decorative or functional items
        (2, 1, 1): 'anvil', # Anvil for repairing and renaming items
     
 

    ########### CURRENT PLANS ###########
    STRUCTURE DESCRIPTION: {structure_description}
    CURRENT PLANS: {current_plans}
    CRITICISM: {criticism}
    // Note: The furthest southwest corner of the structure is the origin (0, 0, 0). The x-axis runs east, the y-axis runs up, and the z-axis runs south.
    // Here you will generate a set of plans in the form of a schema based on the STRUCTURE DESCRIPTION, CURRENT PLANS and CRITICISM.
    // JSON Response Format: "schema": "Your Schema Plans"
    Response: """

    criticize_schema = """SYSTEM DESCRIPTION: You are a Minecraft Structure Generation Bot.
    TASK: Your task is to evaluate the schema on the structure_description and plans.
    RESPONSE OPTIONS:
    Option 1 - Respond with a CRITICISM. Some things to evaluate the schema on: made up items which do not appear in the video game Minecraft, poorly thought out design dimensions, duplicate blocks, etc.
    Option 2 - Respond with "COMPLETED". This will send the schema to the system to begin executing the building plans.
    STRUCTURE DESCRIPTION: {structure_description}
    PLANS: {plans}
    // Here you will evaluate the schema on the structure_description and plans. You will return a CRITICISM if the schema is not COMPLETED.
    Response: """

    return {'environment_changes': environment_changes, 'action_proposal': action_proposal, 'sort_action_stack': sort_action_stack, 'planning_module': planning_module, 'decision_module': decision_module, 'action_module': action_module, 'execution_module_success': execution_module_success, 'execution_module_failure': execution_module_failure, 'summarize_module': summarize_module, 'structure_description': structure_description, 'generate_schema': generate_schema, 'criticize_schema': criticize_schema}

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
            
            prompts[key] = ChatPromptTemplate.from_template(value) | llm_4

        return prompts