from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

def get_prompts():
    
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

    return {'planning_module': planning_module, 'decision_module': decision_module, 'action_module': action_module, 'execution_module_success': execution_module_success, 'execution_module_failure': execution_module_failure, 'summarize_module': summarize_module}

def get_llms(query=''):
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")

        llm = ChatOpenAI(model='gpt-3.5-turbo-0125', temperature=0.1, api_key=openai_api_key)
        llm_4 = ChatOpenAI(model='gpt-4-0125-preview', temperature=0.1, api_key=openai_api_key)

        if query == '': prompts = get_prompts()
        else: prompts = get_prompts()[query]

        for key, value in prompts.items():
            # save money by using gpt-3.5-turbo-1106
            if key == 'planning_module':
                prompts[key] = ChatPromptTemplate.from_template(value) | llm_4
            else:
                prompts[key] = ChatPromptTemplate.from_template(value) | llm
            
            # prompts[key] = ChatPromptTemplate.from_template(value) | llm

        return prompts