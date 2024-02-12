from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

def get_prompts():

    select = """SYSTEM: You are a Minecraft Task Completion Assistant. You are given a task to complete in Minecraft.
    Select several reasoning modules that are crucial to utilize in order to solve the given Task.
All reasoning module descriptions:
1 How could I devise an experiment to help solve that problem?
2 Make a list of ideas for solving this problem, and apply them one by one to the problem to see if any progress can be made.
3 How could I measure progress on this problem?
4 How can I simplify the problem so that it is easier to solve?
5 What are the key assumptions underlying this problem?
6 What are the potential risks and drawbacks of each solution?
7 What are the alternative perspectives or viewpoints on this problem?
8 What are the long-term implications of this problem and its solutions?
9 How can I break down this problem into smaller, more manageable parts?
10 Critical Thinking: This style involves analyzing the problem from different perspectives, questioning assumptions, and evaluating
the evidence or information available. It focuses on logical reasoning, evidence-based decision-making, and identifying
potential biases or flaws in thinking.
11 Try creative thinking, generate innovative and out-of-the-box ideas to solve the problem. Explore unconventional solutions,
thinking beyond traditional boundaries, and encouraging imagination and originality.
12 Seek input and collaboration from others to solve the problem. Emphasize teamwork, open communication, and leveraging the
diverse perspectives and expertise of a group to come up with effective solutions.
13 Use systems thinking: Consider the problem as part of a larger system and understanding the interconnectedness of various elements.
Focuses on identifying the underlying causes, feedback loops, and interdependencies that influence the problem, and developing holistic
solutions that address the system as a whole.
14 Use Risk Analysis: Evaluate potential risks, uncertainties, and tradeoffs associated with different solutions or approaches to a
problem. Emphasize assessing the potential consequences and likelihood of success or failure, and making informed decisions based
on a balanced analysis of risks and benefits.
15 Use Reflective Thinking: Step back from the problem, take the time for introspection and self-reflection. Examine personal biases,
assumptions, and mental models that may influence problem-solving, and being open to learning from past experiences to improve
future approaches.
16 What is the core issue or problem that needs to be addressed?
17 What are the underlying causes or factors contributing to the problem?
18 Are there any potential solutions or strategies that have been tried before? If yes, what were the outcomes and lessons learned?
19 What are the potential obstacles or challenges that might arise in solving this problem?
20 Are there any relevant data or information that can provide insights into the problem? If yes, what data sources are available,
and how can they be analyzed?
21 Are there any stakeholders or individuals who are directly affected by the problem? What are their perspectives and needs?
22 What resources (financial, human, technological, etc.) are needed to tackle the problem effectively?
23 How can progress or success in solving the problem be measured or evaluated?
24 What indicators or metrics can be used?
25 Is the problem a technical or practical one that requires a specific expertise or skill set? Or is it more of a conceptual or
theoretical problem?
26 Does the problem involve a physical constraint, such as limited resources, infrastructure, or space?
27 Is the problem related to human behavior, such as a social, cultural, or psychological issue?
28 Does the problem involve decision-making or planning, where choices need to be made under uncertainty or with competing
objectives?
29 Is the problem an analytical one that requires data analysis, modeling, or optimization techniques?
30 Is the problem a design challenge that requires creative solutions and innovation?
31 Does the problem require addressing systemic or structural issues rather than just individual instances?
32 Is the problem time-sensitive or urgent, requiring immediate attention and action?
33 What kinds of solution typically are produced for this kind of problem specification?
34 Given the problem specification and the current best solution, have a guess about other possible solutions.
35 Let's imagine the current best solution is totally wrong, what other ways are there to think about the problem specification?
36 What is the best way to modify this current best solution, given what you know about these kinds of problem specification?
37 Ignoring the current best solution, create an entirely new solution to the problem.
38 Let's think step by step.
39 Let's make a step by step plan and implement it with good notion and explanation.

Task: {task}
# Select the top reasoning modules that are crucial to utilize in order to solve the given Task.
# Respond only with the top Relevant Reasoning Modules in their full sentences and nothing else.
Most Relevant Reasoning Modules: """

    adapt = """SYSTEM: You are a Minecraft Task Completion Assistant. You are given a task to complete in Minecraft.
Rephrase and specify the best reasoning modules to better help solving the Minecraft Task.
Task: {task}
SELECTED REASONING MODULES:
{relevant_reasoning_modules}

# Adapt each REASONING MODULE description to better solve the Task in Minecraft.
# Respond with the Minecraft adapted REASONING MODULES.
Adapted Reasoning Modules: """

    implement = """SYSTEM: You are a Minecraft Task Completion Assistant. You are given a task to complete in Minecraft.
Operationalize the reasoning modules into a step-by-step reasoning plan in JSON format:
******* EXAMPLE: *******
Task: Find if there is wood in the local area.
Adapted Reasoning Modules:
- How could I design an in-game experiment to determine if there is wood nearby?
- How could I track my progress in finding wood within the game environment?
- How can I simplify the search for wood by focusing on specific biomes or tree types?
- How can I break down the search for wood into systematic steps, such as exploring specific areas or using specific tools?
- What is the main goal, finding wood, and what are the most efficient methods to achieve this in Minecraft?
- What in-game clues or indicators can help identify areas rich in wood resources?
Operationalized Reasoning Plan:
    "Search for 'oak_log', or any other log type within a 32-block radius. This step can be repeated for different types of wood (e.g., birch_log, spruce_log) if necessary.": "",
    "Query the vision module to gather information about the local area on where there might be good resources of wood blocks.": ""
*************************
PERCEPTION FUNCTIONS:
{perception_functions}

Task: {task}
Adapted Reasoning Modules:
{adapted_reasoning_modules}

Implement a simple and efficient reasoning structure for solvers to follow step-by-step and arrive at the correct answer to the Task.
# Respond in JSON format, and remember this is in Minecraft.
# Utilize the format of the EXAMPLE to create the Operationalized Reasoning Plan. ie, "Subtask": ""
Operationalized Reasoning Plan:"""

    perceive = """Task Completion Guidance for Minecraft Assistant

Objective: You are tasked with completing a specific Task in Minecraft. Your success depends on efficiently gathering information needed to suitably complete the Task.
<i>Side note: A Task can be a question or a problem you must answer.</i>

Instructions:

Response Options:
Option 1: If you require more information to progress, request a specific perception function call. This should enhance your understanding of the Minecraft environment and assist in solving the subtasks. Format your request precisely as shown in the perception functions list.
Example: requestBlockType('oak_log', 20)
Example: vision.visionModule('Place query here.')
Option 2: If you believe you have completed the main task or if it's your final attempt, summarize your findings and solutions concisely.
Example: COMPLETED: I have successfully located and collected oak wood from the forest located to the east, approximately 30 seconds from my starting point.
Task Details:

Main Task: {task}
Helpful Subtasks: {subtasks}
Perception Functions:
{perception_functions}

Collected Information:
Environment: {environment}

Attempts:

You have a total of 3 attempts to respond.
If you are on your third attempt, you must use Option 2 to conclude your findings.
Important:

Avoid repeating responses from previous attempts.
Ensure your response is tailored to either gather more information or conclude the task based on the options provided.
Follow the examples closely for formatting your response correctly.
Current Attempt: {current_attempt}

Summary of Previous Attempts: {previous_attempts}

# Remember, when calling functions, you must adhere to the exact format as shown in the perception functions list.
RESPONSE:"""

    return {'select': select, 'adapt': adapt, 'implement': implement, 'perceive': perceive}

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