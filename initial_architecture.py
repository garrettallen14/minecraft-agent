# Deprecated for now

logging.info('Bot is starting up...')

# Generate some Tasks and Execute them
previous_tasks, previous_actions = [], []
while True:

    attempts = 0
    while True:
        try:
            # Create a Goal and High-Level Plan
            plan = llms['planning_module'].invoke({
                'current_environment': getPromptInfo(bot),
                'previous_tasks': previous_tasks,
                'bot_functions': bot_functions,
            }).content
            plan = findAndParseJsonLikeText(plan)[0]
            break
        except:
            print('Error loading json in Planning Module...')
            attempts += 1
            if attempts == 5: break
            continue


    logging.info(f'Planning Module: {plan}')

    # We have a current goal and a high level plan to achieve it
    current_goal = plan['current_goal']
    print(f'Current Goal: {current_goal}')
    plan = plan['high_level_steps']
    print(f'High Level Plan: {plan}')

    # Execute on this plan
    while True:
            
        while True:
            # Decide the next best action to accomplish this plan. If the GOAL is complete summarize what we learned
            try:
                decide_action = llms['decision_module'].invoke({
                    'current_goal': current_goal,
                    'plan': plan,
                    'current_environment': getPromptInfo(bot),
                    'previous_actions': previous_actions,
                    'bot_functions': bot_functions
                }).content

                decide_action = findAndParseJsonLikeText(decide_action)[0]
                break
            except:
                print('Error loading json in Decision Module...')
                continue
        
        
        # decide_action = json.loads(decide_action)
        decision = decide_action['decision']

        logging.info(f'Decision Module: {decide_action}')

        # The GOAL is complete, so we summarize what we learned
        if "COMPLETE" in decision:
            summarize_module = llms['summarize_module'].invoke({
                'current_goal': current_goal,
                'plan': plan,
                'current_environment': getPromptInfo(bot),
                'previous_actions': previous_actions
            }).content


            logging.info(f'GOAL COMPLETE: {current_goal}')
            logging.info(f'Summarize Module: {summarize_module}')

            # Add our learnings to the Bot's context window, then go get the next GOAL
            previous_tasks.append(summarize_module)
            break

        # The GOAL is incomplete, so we execute on our next best action
        else:
            # Attempt to execute this action
            previous_attempts = []
            while True:
                    
                while True:
                    try:

                        action_module = llms['action_module'].invoke({
                            'current_environment': getPromptInfo(bot),
                            'current_goal': decision,
                            'previous_attempts': previous_attempts,
                            'bot_functions': bot_functions
                        }).content

                        # This should be a function that we can execute
                        action_module = findAndParseJsonLikeText(action_module)[0]
                        break
                    except:
                        print('Error loading json in Action Module...')
                        continue
                
                action = action_module['action']

                logging.info(f'Action Module: {action_module}')
                
                # Get the environment before execution
                initial_environment = getPromptInfo(bot)
                
                # Execute the action
                try:
                    result = exec(action)
                except Exception as e:
                    # If we get an error, then we know we failed
                    print(e)
                    logging.info(f'{action} failed: {e}')
                    previous_attempts.append(f'{action} failed: {e}')
                    continue
                
                # If result = True, then our Action function completed its job, so let's summarize what we did
                if result == True:
                    # First we ensure our Bot is really done, and has stopped moving
                    timeout = 0
                    while bot.pathfinder.isMoving() and timeout < 120:
                        time.sleep(5)
                        timeout += 5
                        logging.info('Bot is still moving...')
                        if timeout == 120:
                            print('Bot may be broken...')
                            break
                    
                    # Summarize the outcome of the action
                    execution_module_success = llms['execution_module_sucess'].invoke({
                        'desired_action': decision,
                        'action_executed': action,
                        'initial_environment': initial_environment,
                        'final_environment': getPromptInfo(bot)
                    }).content                  

                    logging.info(f'Execution Module Success: {execution_module_success}')

                    # Add this summary to our decision module's context window, and move on to the next action
                    previous_actions.append(execution_module_success)
                    break

                # If result = False, then our Action function failed, so we will try again
                if result == False:
                    previous_attempts.append(f'{action} failed...')

                    # If we have tried 5 times, then we need to escalate back to the decision module
                    if len(previous_attempts) == 5:
                        execution_module_failure = llms['execution_module_failure'].invoke({
                            'desired_action': decision,
                            'failed_actions': previous_attempts,
                            'initial_environment': initial_environment,
                            'final_environment': getPromptInfo(bot)
                        }).content

                        logging.info(f'Execution Module Failure: {execution_module_failure}')

                        # Add this summary of our failures to our decision module's context window, so we can generate a better action
                        previous_actions.append(execution_module_failure)
                        break