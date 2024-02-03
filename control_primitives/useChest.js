const Vec3 = require("vec3").Vec3;

async function getItemFromChest(bot, chestPos, itemsToGet, count) {
    const chestPosition = new Vec3(chestPos.x, chestPos.y, chestPos.z);
    // return if chestPosition is not Vec3
    if (!(chestPosition instanceof Vec3)) {
        bot.chat("chestPosition for getItemFromChest must be a Vec3");
    }
    await moveToChest(bot, chestPosition);
    const chestBlock = bot.blockAt(chestPosition);
    const chest = await bot.openContainer(chestBlock);
    for (i = 0; i < itemsToGet.length; i++) {
        console.log(itemsToGet[i], count[i])
        const itemByName = mcData.itemsByName[itemsToGet[i]];
        if (!itemByName) {
            bot.chat(`No item named ${itemByName.name}`);
            continue;
        }

        const item = chest.findContainerItem(itemByName.id);
        if (!item) {
            bot.chat(`I don't see ${itemByName.name} in this chest`);
            continue;
        }
        try {
            await chest.withdraw(item.type, null, count[i], itemsToGet[itemByName]);
        } catch (err) {
            bot.chat(`Not enough ${itemByName.name} in chest.`);
        }
    }
    await closeChest(bot, chestBlock);
}

async function depositItemIntoChest(bot, chestPos, itemsToDeposit, count) {
    const chestPosition = new Vec3(chestPos.x, chestPos.y, chestPos.z);
    // return if chestPosition is not Vec3
    if (!(chestPosition instanceof Vec3)) {
        throw new Error(
            "chestPosition for depositItemIntoChest must be a Vec3"
        );
    }
    await moveToChest(bot, chestPosition);
    const chestBlock = bot.blockAt(chestPosition);
    const chest = await bot.openContainer(chestBlock);
    for (i = 0; i < itemsToDeposit.length; i++) {
        console.log(itemsToDeposit[i], count[i])
        const itemByName = mcData.itemsByName[itemsToDeposit[i]];
        if (!itemByName) {
            bot.chat(`No item named ${itemByName.name}`);
            continue;
        }
        const item = findInventoryItem(bot.inventory, itemByName.name);
        if (!item) {
            bot.chat(`No ${itemByName.name} in inventory`);
            continue;
        }
        try {
            await chest.deposit(item.type, null, count[i], itemsToDeposit[itemByName]);
        } catch (err) {
            bot.chat(`Not enough ${itemByName.name} in inventory.`);
        }
    }
    await closeChest(bot, chestBlock);
    return true;
}

// async function checkItemInsideChest(bot, chestPos) {
//     const chestPosition = new Vec3(chestPos.x, chestPos.y, chestPos.z);
//     // return if chestPosition is not Vec3
//     if (!(chestPosition instanceof Vec3)) {
//         throw new Error(
//             "chestPosition for depositItemIntoChest must be a Vec3"
//         );
//     }
//     await moveToChest(bot, chestPosition);
//     const chestBlock = bot.blockAt(chestPosition);
//     await bot.openContainer(chestBlock);
//     await closeChest(bot, chestBlock);
// }

async function moveToChest(bot, chestPos) {
    const chestPosition = new Vec3(chestPos.x, chestPos.y, chestPos.z);
    if (!(chestPosition instanceof Vec3)) {
        throw new Error(
            "chestPosition for depositItemIntoChest must be a Vec3"
        );
    }
    if (chestPosition.distanceTo(bot.entity.position) > 32) {
        bot.chat(
            `/tp ${chestPosition.x} ${chestPosition.y} ${chestPosition.z}`
        );
        await bot.waitForTicks(20);
    }
    const chestBlock = bot.blockAt(chestPosition);
    if (chestBlock.name !== "chest") {
        bot.emit("removeChest", chestPosition);
        throw new Error(
            `No chest at ${chestPosition}, it is ${chestBlock.name}`
        );
    }
    await bot.pathfinder.goto(
        new pathfinder.goals.GoalLookAtBlock(chestBlock.position, bot.world, {})
    );
    return chestBlock;
}

async function listItemsInChest(bot, chestBlock) {
    const chest = await bot.openContainer(chestBlock);
    const items = chest.containerItems();
    if (items.length > 0) {
        const itemNames = items.reduce((acc, obj) => {
            if (acc[obj.name]) {
                acc[obj.name] += obj.count;
            } else {
                acc[obj.name] = obj.count;
            }
            return acc;
        }, {});
        bot.emit("closeChest", itemNames, chestBlock.position);
    } else {
        bot.emit("closeChest", {}, chestBlock.position);
    }
    return chest;
}

async function closeChest(bot, chestBlock) {
    try {
        const chest = await listItemsInChest(bot, chestBlock);
        await chest.close();
    } catch (err) {
        await bot.closeWindow(chestBlock);
    }
}

function findInventoryItem(inventory, name) {
    for (let i = 0; i < inventory.slots.length; ++i) {
        const item = inventory.slots[i];
        if (item && item.name === name) return item;
    }
    return null;
}

// function itemByName(items, name) {
//     for (let i = 0; i < items.length; ++i) {
//         const item = items[i];
//         if (item && item.name === name) return item;
//     }
//     return null;
// }

module.exports = { getItemFromChest, depositItemIntoChest };