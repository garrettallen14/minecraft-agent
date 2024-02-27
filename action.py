import os
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
        self.action_outcome_file = './action_outcomes.txt'

    def reset_actions(self):
        self.previous_action_outcomes = []
        self.current_goal_progress = ''


    def store_action_outcome(self, action_record):
        # Append the action record string to the file
        with open(self.action_outcome_file, 'a') as file:
            file.write(str(action_record))
        return

    def perform_action(self, bot, goal):

        start_time = time.time()
        failed_action_proposal = []
        while time.time() - start_time < 120:
            try:
                # Store the action outcome record for future training
                action_record = {}

                # Use GPT-4 Vision model to generate the next best action. This will provide additional grounding for the Agent within the environment
                prompt_input = {
                    'goal': goal,
                    'current_environment': env_info.getPromptInfo(bot),
                    'previous_action_outcomes': self.previous_action_outcomes,
                    'current_goal_progress': self.current_goal_progress,
                    'proposed_action': failed_action_proposal,
                    'bot_functions': self.bot_functions
                }
                prompt = self.specific_prompts['generate_next_best_action'].format(**prompt_input)
                new_action = vision.visionModule(query='', prompt=prompt)
                
                self.next_best_action = findAndParseJsonLikeText(new_action)[0]['next_best_action']
                reasoning = findAndParseJsonLikeText(new_action)[0]['reasoning']

                print(f'{new_action=}')

                # Get before
                previous_environment = env_info.getPromptInfo(bot)

                # Store our environment before, plus reasoning and action
                action_record['previous_environment'] = previous_environment
                action_record['reasoning'] = reasoning
                action_record['proposed action'] = self.next_best_action

                # Execute action
                try:
                    # If the action is placing an Item, we need a special function to ensure that the bot has successfully placed it afterwards
                    if 'placeItem' in self.next_best_action:
                        self.execute_place_item(bot, self.next_best_action)
                    else:
                        exec(self.next_best_action)

                except Exception as e:
                    # Store the action outcome record for future training
                    action_record['outcome'] = str(e)
                    self.store_action_outcome(action_record)

                    raise Exception(str(e))
                
                break
            except Exception as e:
                failed_action_proposal.append([f'Failed attempt number {len(failed_action_proposal) + 1}:', 'Failed action proposal:', self.next_best_action, 'Reason:', str(e)[:300]])
                print(f'{failed_action_proposal=}')
                continue

        # Use GPT-4V to analyze changes
        prompt_input = {
            'goal': goal,
            'action': self.next_best_action,
            'previous_environment': previous_environment,
            'current_environment': env_info.getPromptInfo(bot),
            'previous_goal_progress': self.current_goal_progress
        }
        prompt = self.specific_prompts['summarize_environment_changes'].format(**prompt_input)
        changes_json = vision.visionModule(query='', prompt=prompt)

        changes = findAndParseJsonLikeText(changes_json)[0]

        print(f'{changes=}')

        self.current_goal_progress = changes['new_goal_progress']
        self.environment_changes = changes['action_outcome']
        self.previous_action_outcomes.append([f'Action Number {len(self.previous_action_outcomes)}', new_action, 'Outcome:', self.environment_changes])

        # Try to gather any new memories
        new_memories = self.llms['gather_new_memories'].invoke({
            'current_environment': env_info.getPromptInfo(bot),
            'action': new_action,
            'environment_changes': self.environment_changes,
            'new_goal_progress': self.current_goal_progress
        }).content

        # Store the action outcome record for future training
        action_record['outcome'] = self.environment_changes
        self.store_action_outcome(action_record)

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
        

    # After a goal is completed or determined to be finished, we need to gather key insights from the bot's actions and the environment
    def save_key_lessons(self, goal):

        # Get key lessons from the bot's actions and the environment
        key_lessons = self.llms['key_lessons'].invoke({
            'goal': goal,
            'previous_action_outcomes': self.previous_action_outcomes,
            'previous_goal_progress': self.current_goal_progress
        }).content

        # Store the key lessons in the memory module
        self.mem.store_memory(key_lessons, 'goal_lessons')

        self.reset_actions()

        return key_lessons