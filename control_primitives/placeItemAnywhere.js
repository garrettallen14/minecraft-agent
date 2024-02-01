Vec3 = require('vec3').Vec3;

async function placeItemAnywhere(bot, name, originalPos, maxAttempts = 8) {

    let position = new Vec3(originalPos.x, originalPos.y, originalPos.z);

    // const mineblock = require('./mineBlock.js');

    if (typeof name !== "string") {
        throw new Error(`name for placeItem must be a string`);
    }
    if (!(position instanceof Vec3)) {
        throw new Error(`position for placeItem must be a Vec3`);
    }

    const itemByName = globalThis.mcData.itemsByName[name];
    if (!itemByName) {
        throw new Error(`No item named ${name}`);
    }

    let attempts = 0;
    while (attempts < maxAttempts) {
        try {
            const item = bot.inventory.findInventoryItem(itemByName.id);
            if (!item) {
                bot.chat(`No ${name} in inventory`);
                return;
            }

            // Adjust the position slightly for each attempt
            const offset = attempts === 0 ? new Vec3(0, 0, 0) : new Vec3(Math.floor(Math.random() * 3) - 1, 0, Math.floor(Math.random() * 3) - 1);
            const tryPosition = position.add(offset);

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
                const block = bot.blockAt(tryPosition.minus(vector));
                if (block?.name !== "air") {
                    referenceBlock = block;
                    faceVector = vector;
                    break;
                }
            }

            if (!referenceBlock) {
                throw new Error(`No block to place ${name} on. You cannot place a floating block.`);
            }

            await bot.pathfinder.setGoal(new pathfinder.goals.GoalGetToBlock(new Vec3(referenceBlock.position.x, referenceBlock.position.y, referenceBlock.position.z), bot.world, {'range': 2}));
            await bot.equip(item, "hand");
            await bot.placeBlock(referenceBlock, faceVector);
            bot.chat(`Placed ${name} at ${tryPosition}`);
            return true; // Exit the function after successful placement
        } catch (err) {
            attempts++;
            if (attempts >= maxAttempts) {
                bot.chat(`Error placing ${name}: ${err.message}. Maximum attempts reached. It seems no blocks are open around me.`);
                return false;
            }
        }
    }
}

module.exports = { placeItemAnywhere }
