import goal_llms
import env_info
import json
from javascript import require, globalThis
findAndParseJsonLikeText = require('json-like-parse')
import perception
import memory
import vision

class Module():
    def __init__(self):
        self.llms = goal_llms.get_llms()
        self.current_goal = ''
        self.perceive = perception.Module()
        self.mem = memory.Module()
        self.prompts = goal_llms.get_prompts()

    def update_goal(self, bot, lessons_learned, proposed_goal):

        # Generate new goal based on proposed_goal, vision, prev goal + lessons learned
        prompt_input = {
            'goal': proposed_goal,
            'current_environment': env_info.getPromptInfo(bot),
            'previous_goal': self.current_goal,
            'previous_goal_lessons_learned': lessons_learned
        }
        prompt = self.prompts['create_goal'].format(**prompt_input)
        new_goal = vision.visionModule(query='', prompt=prompt)

        goal = findAndParseJsonLikeText(new_goal)[0]['new_goal']
        plan = findAndParseJsonLikeText(new_goal)[0]['plan']

        return str(goal), str(plan)

        

        # new_goal = findAndParseJsonLikeText(new_goal)[0]['new_goal']

        # # ask percept for input on new goal
        # perception_input = f'Is this new goal reasonable given the current environment? New Goal: {new_goal}'
        # perception_response = self.perceive.perceive(bot, perception_input)
        # # ask memory for input on new goal
        # memory_input = f'What information can you provide me about this new goal? New Goal: {new_goal}'
        # memory_response = self.mem.query_memories(memory_input)

        # print('Perception and Memory Response 1:')
        # print(f'{new_goal=} {memory_response=} {perception_response=}')
        
        # # Update new goal based on input, generate plan
        # updated_goal = self.llms['update_goal'].invoke({
        #     'proposed_goal': new_goal,
        #     'perception_response': perception_response,
        #     'memory_response': memory_response
        # }).content

        # new_goal = findAndParseJsonLikeText(updated_goal)[0]['new_goal']
        # plan = findAndParseJsonLikeText(updated_goal)[0]['plan']

        # # ask percept for input on plan
        # perception_input = f'Given the Goal: {new_goal}... How can I improve the current plan? Plan: {plan}'
        # perception_response = self.perceive.perceive(bot, perception_input)
        
        # # ask memory for input on plan
        # memory_input = f'Given the Goal: {new_goal}... How can I improve the current plan? Plan: {plan}'
        # memory_response = self.mem.query_memories(memory_input)

        # print('Perception and Memory Response 2:')
        # print(f'{new_goal=} {plan=} {memory_response=} {perception_response=}')

        # # Improve plan based on input, with vision
        # prompt_input = {
        #     'current_environment': env_info.getPromptInfo(bot),
        #     'goal': new_goal,
        #     'proposed_plan': plan,
        #     'perception_response': perception_response,
        #     'memory_response': memory_response
        # }
        # prompt = self.prompts['update_plan'].format(**prompt_input)
        # updated_plan = vision.visionModule(query='', prompt=prompt)

        # plan = findAndParseJsonLikeText(updated_plan)[0]['plan']

        # # return new goal, improved plan
        # self.current_goal = new_goal

        # print('Completed Goal Planning Module.')
        # print(f'{new_goal=}, {plan=}')

        # return new_goal, plan

