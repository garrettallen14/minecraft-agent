import action_llms
import env_info
import json
from javascript import require, globalThis
findAndParseJsonLikeText = require('json-like-parse')
import memory
import perception
import vision
import time

craft = globalThis.craft
explore = globalThis.explore
move = globalThis.move
kill = globalThis.kill
collectPosition = globalThis.collectPosition
collectType = globalThis.collectType
pickupDroppedItem = globalThis.pickupDroppedItem
place = globalThis.place
shoot = globalThis.shoot
smelt = globalThis.smelt
chest = globalThis.chest

Vec3 = globalThis.Vec3
mineflayer = globalThis.mineflayer
pathfinder = globalThis.pathfinder
mcData = globalThis.mcData
armorManager = globalThis.armorManager
autoeat = globalThis.autoeat
collectblock = globalThis.collectblock
hawkeye = globalThis.hawkeye
toolPlugin = globalThis.toolPlugin


class Module:
    def __init__(self):
        self.llms = action_llms.get_llms()
        self.previous_action_outcomes = []
        self.current_goal_progress = ''
        self.mem = memory.Module()
        self.percept = perception.Module()
        self.bot_functions = json.loads(open('bot_functions.json').read())
        self.specific_prompts = action_llms.get_prompts()
        self.next_best_action = ''

    def reset_actions(self):
        self.previous_action_outcomes = []
        self.current_goal_progress = ''

    def perform_action(self, bot, goal):

        # Generate a question to ask the perception module, so we can gather some useful information about the environment
        perception_query = self.llms['generate_perception_query'].invoke({
            'goal': goal,
            'current_environment': env_info.getPromptInfo(bot),
            'previous_action_outcomes': self.previous_action_outcomes,
            'current_goal_progress': self.current_goal_progress
        }).content

        # prompt_input = {
        #     'goal': goal,
        #     'current_environment': env_info.getPromptInfo(bot),
        #     'previous_action_outcomes': self.previous_action_outcomes,
        #     'current_goal_progress': self.current_goal_progress,
        # }
        # prompt = self.specific_prompts['generate_perception_query'].format(**prompt_input)
        # perception_query = vision.visionModule(query='', prompt=prompt)

        perception_query = findAndParseJsonLikeText(perception_query)[0]['question']

        print(f'{perception_query=}')

        # Ask the perception module the question, and get the answer. Should enlighten us about the environment
        answer = self.percept.perceive(bot, perception_query)
        
        start_time = time.time()
        failed_action_proposal = []
        while time.time() - start_time < 120:
            try:
                # Generate the next best action to take, given the current environment and the goal
                # new_action = self.llms['generate_next_best_action'].invoke({
                #     'goal': goal,
                #     'current_environment': env_info.getPromptInfo(bot),
                #     'previous_action_outcomes': self.previous_action_outcomes,
                #     'current_goal_progress': self.current_goal_progress,
                #     'question': perception_query,
                #     'answer': answer,
                #     'proposed_action': failed_action_proposal,
                #     'additional_information': additional_info,
                #     'bot_functions': self.bot_functions
                # }).content
                
                # Use GPT-4 Vision model to generate the next best action. This will provide additional grounding for the Agent within the environment
                prompt_input = {
                    'goal': goal,
                    'current_environment': env_info.getPromptInfo(bot),
                    'previous_action_outcomes': self.previous_action_outcomes,
                    'current_goal_progress': self.current_goal_progress,
                    'question': perception_query,
                    'answer': answer,
                    'proposed_action': failed_action_proposal,
                    'bot_functions': self.bot_functions
                
                }
                prompt = self.specific_prompts['generate_next_best_action'].format(**prompt_input)
                new_action = vision.visionModule(query='', prompt=prompt)

                print(f'{new_action=}')

                self.next_best_action = findAndParseJsonLikeText(new_action)[0]['next_best_action']

                print(f'{new_action=}')

                # Ensure this action is proper syntax, makes legitimate sense for our situation, is not a duplicate of the last action or a duplicate of the last 3 actions
                gate = self.llms['gate_action'].invoke({
                    'goal': goal,
                    'current_environment': env_info.getPromptInfo(bot),
                    'previous_action_outcomes': self.previous_action_outcomes,
                    'current_goal_progress': self.current_goal_progress,
                    'next_best_action': new_action
                }).content

                gate = findAndParseJsonLikeText(gate)[0]['gate']

                print(f'{gate=}')

                if 'false' in gate.lower():
                    raise Exception(f"Gate check failed: {gate['description']}")

                # Get before
                previous_environment = env_info.getPromptInfo(bot)

                # Execute action
                try:
                    # If the action is placing an Item, we need a special function to ensure that the bot has successfully placed it afterwards
                    if 'placeItem' in self.next_best_action:
                        self.execute_place_item(bot, self.next_best_action)
                        
                    else:
                        exec(self.next_best_action)
                except Exception as e:
                    raise Exception(str(e))
                
                break
            except Exception as e:
                failed_action_proposal.append([f'Failed attempt number {len(failed_action_proposal)}:', 'Failed action proposal:', self.next_best_action, 'Reason:', str(e)[:300]])
                print(f'{failed_action_proposal=}')
                continue

        changes_json = self.llms['summarize_environment_changes'].invoke({
            'goal': goal,
            'action': self.next_best_action,
            'previous_environment': previous_environment,
            'current_environment': env_info.getPromptInfo(bot),
            'previous_goal_progress': self.current_goal_progress
        }).content

        changes = findAndParseJsonLikeText(changes_json)[0]

        print(f'{changes=}')

        self.current_goal_progress = changes['new_goal_progress']
        self.environment_changes = changes['environment_changes']
        self.previous_action_outcomes.append([f'Action Number {len(self.previous_action_outcomes)}', new_action, 'Outcome:', self.environment_changes])

        # Try to gather any new memories
        new_memories = self.llms['gather_new_memories'].invoke({
            'current_environment': env_info.getPromptInfo(bot),
            'action': new_action,
            'environment_changes': self.environment_changes,
            'new_goal_progress': self.current_goal_progress
        }).content

        print(f'{new_memories=}')

        new_memories = findAndParseJsonLikeText(new_memories)[0]
        try:
            collection_name, memory = new_memories['memory1'].split(': ')[0], new_memories['memory1'].split(': ')[1]
            self.mem.store_memory(memory, collection_name)
            collection_name, memory = new_memories['memory2'].split(': ')[0], new_memories['memory2'].split(': ')[1]
            self.mem.store_memory(memory, collection_name)
        except:
            pass
        
        # Wait for the bot to finish its action. Sometimes it can get stuck in a loop, so we need to set a timeout
        start_time = time.time()
        while bot.pathfinder.isMoving() and time.time() - start_time < 15:
            time.sleep(1)

        return self.previous_action_outcomes, self.current_goal_progress
    

    # Naive approach to placing an item, we need to ensure that the bot has successfully placed the item
    def execute_place_item(self, bot, next_best_action):

        # Get the name of the item being placed
        parts = next_best_action.split(',')
        item_variable = parts[1].strip().strip("'")

        # Execute the placing action
        exec(next_best_action)

        # Check if the item was successfully placed
        print('Checking item variable:', item_variable, 'was successfully placed...')

        block = bot.findBlock({
            'matching': mcData.blocksByName[item_variable].id,
            'maxDistance': 10
        })

        if block:
            print(f'{item_variable} was successfully placed at {block.position}!')
        else:
            raise Exception(f'{item_variable} was not successfully placed!')