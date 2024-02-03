async function collectDroppedItem(bot, name, maxDistance=64) {
    
    for (const entity of Object.values(bot.entities)) {
        // Check if the entity is an item
        if (entity.name === 'item') {
            const item = entity.metadata[8]; // Metadata index for item can be 7 or 8 depending on the version
            if (item && globalThis.mcData.items[item.itemId]) {
                const foundItemName = globalThis.mcData.items[item.itemId].displayName;

                // Check if the item name matches and is within the specified distance
                if (foundItemName === name && distanceTo(bot.entity.position, entity.position) < maxDistance) {
                    const goal = new pathfinder.goals.GoalGetToBlock(entity.position.x, entity.position.y, entity.position.z);
                    await bot.pathfinder.setGoal(goal);

                    bot.chat(`Navigating to ${name} at ${entity.position}`);
                    return true;
                }
            }
        }
    }

    return false;
}

function distanceTo(pos1, pos2) {
    return Math.sqrt(
        Math.pow(pos1.x - pos2.x, 2) +
        Math.pow(pos1.y - pos2.y, 2) +
        Math.pow(pos1.z - pos2.z, 2)
    );
}

module.exports = { collectDroppedItem };