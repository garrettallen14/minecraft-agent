import perception_llms
import json
from javascript import require, globalThis
findAndParseJsonLikeText = require('json-like-parse')
import env_info

# Perception functions: Vision, Memory, Explore, findBlockType (mcData), bot.lookAt
import memory
import vision
explore = globalThis.explore #require('./control_primitives/exploreUntil.js')
mcData = globalThis.mcData #require('minecraft-data')('1.20.2')

class Module:
    def __init__(self):
        self.llms = perception_llms.get_llms()
        self.perception_functions = json.loads(open('perception_functions.json').read())
        self.mem = memory.Module()

    def perceive(self, bot, task):
        relevant_reasoning_modules = self.llms['select'].invoke({
            'task': task
        }).content
        adapted_reasoning_modules = self.llms['adapt'].invoke({
            'task': task,
            'relevant_reasoning_modules': relevant_reasoning_modules
        }).content
        implemented_reasoning_modules = self.llms['implement'].invoke({
            'task': task,
            'adapted_reasoning_modules': adapted_reasoning_modules,
            'perception_functions': self.perception_functions
        }).content
        subtasks = implemented_reasoning_modules
        environment = {'environment': str(env_info.getPromptInfo(bot)), 'Additional Information': []}
        attempt = 1
        previous_attempts = []
        while attempt <= 3:
            response = self.llms['perceive'].invoke({
                'task': task,
                'subtasks': subtasks,
                'environment': environment,
                'current_attempt': attempt,
                'perception_functions': self.perception_functions,
                'previous_attempts': previous_attempts
            }).content
            print(f'{response=}')

            if 'COMPLETED' in response:
                print(f'Completed task: {response.split("COMPLETED")[1]}')
                break

            # revisit this portion
            if 'perception_function' in response:
                try:
                    response = findAndParseJsonLikeText(response)[0]['perception_function']
                except:
                    response = 'Invalid perception_function call format detected. Please try again.'
                try:
                    
                    global output
                    output = None

                    exec(f"global output\noutput = {response}")
                    if 'findBlockType' in response:
                        if output:
                            response = f'{response} was found in the world at: {output.position}!'
                        else:
                            response = f'{response} was not found in this location!'
                    
                    else:
                        environment['Additional Information'].append(output)
                        response += f': {output}'

                except:
                    environment['environment'] = str(env_info.getPromptInfo(bot))

            previous_attempts.append([f'Attempt Number: {attempt}', response])
            print(previous_attempts)

            attempt += 1
        
        # Store this response in the Perception Memory database collection
        self.mem.store_memory(response, 'general_perceptions')

        return response


    def findBlockType(self, bot, name, maxDistance=32):
        blocks = bot.findBlock({
            'matching': mcData.blocksByName[name].id,
            'maxDistance': maxDistance,
            'count': 5
        })

        for block in blocks:
            if bot.canSeeBlock(bot.blockAt(block)):
                return block
            
    
    def askLLM(self, question):
        return self.llms['ask'].invoke({
            'question': question
        }).content
    
    def scanEnvironment(self, bot, query):

        prompt = """You are to scan the Minecraft screenshot to find the following Query stated below.
If you find the Query you are looking for, reply: YES, and explain what you see, and how it satisfies the Query you are seeking.
If you do not find the Query you are looking for, reply: NO, but provide information which may be useful given what you see.
Query: """
        
        # North, East, South, West
        responses = []
        for pitch, direction_name in zip([180, 270, 0, 90], ['North', 'East', 'South', 'West']):
            # Look in the direction
            bot.look(pitch, 0)
            # Get information from the Vision Module
            response = vision.visionModule(prompt=prompt, query=query)

            if 'YES' in response:
                return f'{query} was found in the {direction_name}! \nResponse from the vision module: {response}'
            else:
                responses.append(f'{query} was not found in the {direction_name} direction. \nResponse from the vision module: {response}')

        return responses