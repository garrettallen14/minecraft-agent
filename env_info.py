from javascript import require, On, Once, AsyncTask, once, off, globalThis

mcData = globalThis.mcData
bot = globalThis.bot

CHESTS = [mcData.blocksByName[name]['id'] for name in mcData.blocksByName if 'chest' in name]
BEDS = [mcData.blocksByName[name]['id'] for name in mcData.blocksByName if 'bed' in name]
CHAT_MESSAGES = []


@On(bot, 'chat')
def handleMsg(this, sender, message, *args):
    if sender == bot.username:
        sender = 'Minecraft Bot (You)'
    CHAT_MESSAGES.append(f'{sender} said {message}')


def getEnvironmentInfo(bot):
    def distanceTo(pos1, pos2):
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2 + (pos1.z - pos2.z) ** 2) ** 0.5

    def nearbyEntities(bot, max_distance={'mobs': 32, 'items': 16, 'players': 128}):
        nearby_mobs, nearby_droppeditems, nearby_players = [], [], []
        for entity in bot.entities:
            if bot.entities[entity]:
                # Mob
                if bot.entities[entity].type not in ['other', 'player', 'projectile'] and distanceTo(bot.entities[entity].position, bot.entity.position) < max_distance['mobs']:
                    if bot.canSeeBlock(bot.blockAt(bot.entities[entity].position)):
                        nearby_mobs.append(f'{bot.entities[entity].name} is {int(distanceTo(bot.entities[entity].position, bot.entity.position))} blocks away.')
                # Item
                elif bot.entities[entity].displayName == 'Item' and distanceTo(bot.entities[entity].position, bot.entity.position) < max_distance['items']:
                    if bot.canSeeBlock(bot.blockAt(bot.entities[entity].position)):

                        nearby_droppeditems.append(f'DroppedItem {mcData.items[bot.entities[entity].metadata[8].itemId].displayName} is {int(distanceTo(bot.entities[entity].position, bot.entity.position))} blocks away.')
                # Player
                elif bot.entities[entity].type == 'player' and bot.entities[entity].username != bot.username and distanceTo(bot.entities[entity].position, bot.entity.position) < max_distance['players']:
                    if bot.canSeeBlock(bot.blockAt(bot.entities[entity].position)):

                        nearby_players.append(f'Player: {bot.entities[entity].username} is {int(distanceTo(bot.entities[entity].position, bot.entity.position))} blocks away.')
        
        return nearby_mobs, nearby_droppeditems, nearby_players


    def nearbyBeds(bot, beds, max_distance=24, count=1):
        beds = bot.findBlocks({'matching': beds, 'maxDistance': max_distance, 'count': count})
        return [f'Bed at Vec3{bed.x, bed.y, bed.z} is {int(distanceTo(bed, bot.entity.position))} blocks away.' for bed in beds]

    def nearbyChests(bot, chests, max_distance=24, count=1):
        chests = bot.findBlocks({'matching': chests, 'maxDistance': max_distance, 'count': count})
        return [f'Chest at Vec3{chest.x, chest.y, chest.z} is {int(distanceTo(chest, bot.entity.position))} blocks away.' for chest in chests]
    
    nearby_mobs, nearby_droppeditems, nearby_players = nearbyEntities(bot, max_distance={'mobs': 64, 'items': 32, 'players': 128})

    nearby_beds = nearbyBeds(bot, BEDS, 24)
    nearby_chests = nearbyChests(bot, CHESTS, 24)

    return {
        'mobs': nearby_mobs,
        'droppedItems': nearby_droppeditems,
        'players': nearby_players,
        'beds': nearby_beds,
        'chests': nearby_chests
    }

def getWorldInfo(bot):
    # Time
    time = bot.time.timeOfDay
    if 0 <= time < 9000:
        time_description = 'in the Morning'
    elif 9000 <= time < 12000:
        time_description = 'at Dusk'
    else:
        time_description = 'at Night'
    
    # Weather
    weather = 'It is clear.' 
    if bot.rainState:
        weather = 'It is raining and thundering!' if bot.thunderState else 'It is raining!'
    
    return {
        'time': f'It is currently {time} {time_description}',
        'weather': weather,
        'biome': mcData.biomes[bot.blockAt(bot.entity.position).biome.id].displayName
    }

def getPlayerState(bot):
    # Inventory
    inventory = []
    for item in bot.inventory.items():
        inventory.append(f'{item.displayName} x{item.count}')
    if len(inventory) == 0: 
        inventory = 'Empty'

    # Held Item
    heldItem = 'Nothing'
    if bot.heldItem:
        heldItem = bot.heldItem.displayName

    return {
        'position': f'Vec3{bot.entity.position.x, bot.entity.position.y, bot.entity.position.z}',
        'pitch': bot.entity.pitch,
        'yaw': bot.entity.yaw,
        'health': bot.health,
        'hunger': bot.food,
        'heldItem': heldItem,
        'inventory': inventory
    }

def getPromptInfo(bot):
    world_info = getWorldInfo(bot)
    player_state = getPlayerState(bot)

    # Ensure that the bot gives a response
    while True:
        try:
            environment_info = getEnvironmentInfo(bot)
            break
        except:
            continue


    return {
        'world_info': world_info,
        'environment_info': environment_info,
        'player_state': player_state,
        'recent_chat_messages': CHAT_MESSAGES[::-1][:5]
    }