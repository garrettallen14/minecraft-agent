gorgeous_quaint_village_home = {
    'foundation': {
        # Stone base to elevate the home slightly above ground level for flood protection and aesthetics
        (x, 64, z): 'cobblestone' for x in range(-2, 13) for z in range(-2, 13)
    },
    'walls': {
        # Main structure walls made of white wool for a clean, modern look contrasted with dark oak logs at corners for a rustic touch
        **{(x, 65, z): 'white_wool' for x in range(0, 11) for z in [0, 10]},
        **{(x, 65, z): 'white_wool' for x in [0, 10] for z in range(1, 10)},
        **{(x, y, z): 'dark_oak_log' for x in [0, 10] for y in range(65, 75) for z in [0, 10]}
    },
    'roof': {
        # A steep pitched dark oak stair roof with a glass center strip for natural lighting
        **{(x, y, z): 'dark_oak_stairs' for x in range(1, 10) for y in range(75, 85 - x) for z in [0, 10]},
        **{(x, 84-x, z): 'glass' for x in range(1, 10) for z in range(1, 10)}
    },
    'windows': {
        # Large glass pane windows for ample natural light, framed with dark oak planks
        **{(x, y, z): 'glass_pane' for x in [2, 8] for y in range(66, 72) for z in [1, 9]},
        **{(x, y, z): 'glass_pane' for x in [1, 9] for y in range(66, 72) for z in [2, 8]}
    },
    'door': {
        # Front door made of dark oak, centrally located
        (5, 65, 0): 'dark_oak_door'
    },
    'interior': {
        # Cozy living room with fireplace and comfortable seating
        (3, 65, 2): 'oak_stairs', (4, 65, 4): 'campfire',
        # Modern kitchen with stone countertops and an island
        (7, 65, 2): 'furnace', (8, 65, 2): 'crafting_table', (7, 65, 3): 'cauldron',
        # Spacious bedroom with a large bed and decorative elements
        (2, 65, 7): 'white_bed', (3, 65, 8): 'chest',
        # Functional bathroom with a toilet, sink, and bathtub
        (8, 65, 7): 'cauldron'
    },
    'garden': {
        # Surrounding garden with flowers, a small pond, and seating
        # **{(x, 64, z): 'grass_block' for x in range(-1, 12) for z in range(-1, 12)},
        # **{(1, 64, 1): 'water', (2, 64, 1): 'lily_pad'},
        # **{(-1, 64, 10): 'oak_stairs', (-1, 64, 9): 'oak_stairs'}
    },
    'pathway': {
        # Pathway leading to the front door with stone bricks
        **{(x, 64, -1): 'stone_bricks' for x in range(4, 7)}
    }
}

min_block = (-2, 64, -2)

adjusted_schematic = {}

for part_name, blocks in gorgeous_quaint_village_home.items():
    adjusted_blocks = {}
    for coords, block_type in blocks.items():
        adjusted_coords = tuple(coord - base_coord for coord, base_coord in zip(coords, min_block))
        adjusted_blocks[adjusted_coords] = block_type
    adjusted_schematic[part_name] = adjusted_blocks


orienting_position = (bot.entity.position.x, bot.entity.position.y, bot.entity.position.z)
orienting_position = (-53.5, 63, 48.5859451457858)


# Step 1: Collect all blocks into a single list
all_blocks = []
for part_name, blocks in adjusted_schematic.items():
    for coords, block_type in blocks.items():
        # Append a tuple containing the part name, coordinates, and block type
        all_blocks.append((part_name, coords, block_type))

# Step 2: Sort the list by Y position
sorted_blocks = sorted(all_blocks, key=lambda x: x[1][1])  # x[1] is the coords, x[1][1] is the Y position

# sorted_blocks



# Step 3: Iterate through the sorted list to place blocks
for part_name, coords, block_type in sorted_blocks:
    result = tuple(a + b for a, b in zip(orienting_position, coords))
    # Check if the block at the target position is already of the desired type
    # Assume bot.blockAt(Vec3(*result)).name is the way to check the block type at `result`
    # and place.placeItem(bot, block_type, bot.blockAt(Vec3(*result)), timeout=500000) is the way to place a block
    if bot.blockAt(Vec3(*result)).name == block_type:
        print(f'Block at {result} is already {block_type}')
        continue
    place.placeItem(bot, block_type, bot.blockAt(Vec3(*result)), timeout=500000)