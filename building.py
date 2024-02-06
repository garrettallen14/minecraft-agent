import llm
from javascript import require, On, Once, AsyncTask, once, off, globalThis

Vec3 = require('vec3').Vec3
place = require('./control_primitives/placeItem.js')
findAndParseJsonLikeText = require('json-like-parse')

# Generating the structure plan based on a description of the desired_structure
def generateStructurePlans(bot, desired_structure, timeout=500000):

    llms = llm.get_llms()

    # Need a LLM call to get a detailed description of the structure
    structure_description = llms['structure_description'].invoke({
        'current_inventory': bot,
        'desired_structure': desired_structure
    }).invoke

    # We use the description to generate a set of initial plans in the form of a schema
    plans = llms['generate_schema'].invoke({
        'structure_description': structure_description,
        'plans': '',
        'criticism': 'No plans generated yet. You must generate some initial schema plans.'
    }).invoke

    plans = findAndParseJsonLikeText(plans)[0]

    # We then evaluate the initial schema plans, refining them, ensuring proper dimensionality and adding more detail
    for _ in range(10):
        # Things to evaluate the schema on: items not in minecraft, poorly thought out design dimensions, duplicate blocks, etc.
        criticism = llms['criticize_schema'].invoke({
            'structure_description': structure_description,
            'plans': plans
        }).invoke

        # If the criticism is COMPLETED, we are done
        if 'COMPLETED' in criticism:
            break

        plans = llms['generate_schema'].invoke({
            'structure_description': structure_description,
            'plans': plans,
            'criticism': criticism
        }).invoke
        plans = findAndParseJsonLikeText(plans)[0]

    return plans

# Executing the building plans
def execute_building_plans(bot, plans, orienting_position):

    # Step 1: Collect all blocks into a single list
    all_blocks = []
    for part_name, blocks in plans.items():
        for coords, block_type in blocks.items():
            # Append a tuple containing the part name, coordinates, and block type
            all_blocks.append((part_name, coords, block_type))
    
    # Step 2: Sort the list by Y position
    sorted_blocks = sorted(all_blocks, key=lambda x: x[1][1])  # x[1] is the coords, x[1][1] is the Y position

    # Step 3: Iterate through the sorted list to place blocks
    for part_name, coords, block_type in sorted_blocks:
        result = tuple(a + b for a, b in zip(orienting_position, coords))
        if bot.blockAt(Vec3(*result)).name == block_type:
            continue
        place.placeItem(bot, block_type, bot.blockAt(Vec3(*result)), timeout=500000)

    ################# Improve ability here ##################
    # Try one more iteration to ensure all blocks are placed
    for part_name, coords, block_type in sorted_blocks:
        result = tuple(a + b for a, b in zip(orienting_position, coords))
        if bot.blockAt(Vec3(*result)).name == block_type:
            continue
        place.placeItem(bot, block_type, bot.blockAt(Vec3(*result)), timeout=500000)

    return True