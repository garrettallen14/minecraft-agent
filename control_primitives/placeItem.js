Vec3 = require('vec3').Vec3;

async function placeItem(bot, name, target) {

    position = new Vec3(target.x, target.y, target.z);
    
    // return if name is not string
    if (typeof name !== "string") {
        throw new TypeError(`name for placeItem must be a string`);
    }
    // return if position is not Vec3
    if (!(position instanceof Vec3)) {
        throw new TypeError(`position for placeItem must be a Vec3`);
    }
    const itemByName = mcData.itemsByName[name];
    if (!itemByName) {
        throw new TypeError(`No item named ${name}`);
    }
    const item = bot.inventory.findInventoryItem(itemByName.id);
    if (!item) {
        throw new TypeError(`No ${name} in inventory`);
    }
    const item_count = item.count;
    // find a reference block
    const faceVectors = [
        new Vec3(0, 1, 0),
        new Vec3(0, -1, 0),
        new Vec3(1, 0, 0),
        new Vec3(-1, 0, 0),
        new Vec3(0, 0, 1),
        new Vec3(0, 0, -1),
    ];
    let referenceBlock = null;
    let faceVector = null;
    for (const vector of faceVectors) {
        const block = bot.blockAt(position.minus(vector));
        if (block?.name !== "air") {
            referenceBlock = block;
            faceVector = vector;
            bot.chat(`Placing ${name} on ${block.name} at ${block.position}`);
            break;
        }
    }
    if (!referenceBlock) {
        throw new TypeError(
            `No block to place ${name} on. You cannot place a floating block.`
        );
    }

    // You must use try catch to placeBlock
    try {
        // You must first go to the block position you want to place
        await bot.pathfinder.goto(new pathfinder.goals.GoalPlaceBlock(position, bot.world, {}));
        // You must equip the item right before calling placeBlock
        bot.setControlState('sneak', true) // Sneak to place block
        await bot.equip(item, "hand");
        await bot.placeBlock(referenceBlock, faceVector);
        bot.setControlState('sneak', false) // UnSneak
        
        // Check to ensure the item was placed
        if (bot.blockAt(referenceBlock.position.plus(faceVector)).name !== name) {
            throw new Error(`Failed to place block ${name}. Perhaps try placing it in a better location.`);
        }

        bot.chat(`Placed ${name}`);
    } catch (err) {
        const item = bot.inventory.findInventoryItem(itemByName.id);
        if (item?.count === item_count) {
            bot.chat(
                `Error placing ${name}: ${err.message}, please find another position to place`
            );
        } else {
            bot.chat(`Placed ${name}`);
        }
    }
}

module.exports = { placeItem }
