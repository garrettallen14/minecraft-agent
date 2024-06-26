async function craftItem(bot, name, count = 1) {
    // return if name is not string
    if (typeof name !== "string") {
        throw new TypeError("name for craftItem must be a string");
    }
    // return if count is not number
    if (typeof count !== "number") {
        throw new TypeError("count for craftItem must be a number");
    }
    const itemByName = mcData.itemsByName[name];
    if (!itemByName) {
        throw new TypeError(`No item named ${name}`);
    }
    const craftingTable = bot.findBlock({
        matching: mcData.blocksByName.crafting_table.id,
        maxDistance: 32,
    });
    // if (!craftingTable) {
    //     bot.chat("Craft without a crafting table");
    // } else {
        // await bot.pathfinder.goto(
        //     new pathfinder.goals.GoalGetToBlock(craftingTable.position.x, craftingTable.position.y, craftingTable.position.z), timeout=1000000
        // );
    // }
    const recipe = bot.recipesFor(itemByName.id, null, 1, craftingTable)[0];
    if (recipe) {
        bot.chat(`I can make ${name}`);
        try {
            if (craftingTable) {
                await bot.pathfinder.goto(new pathfinder.goals.GoalGetToBlock(craftingTable.position.x, craftingTable.position.y, craftingTable.position.z), timeout=60000);
            }
            await bot.craft(recipe, count, craftingTable);
            bot.chat(`I did the recipe for ${name} ${count} times`);
        } catch (err) {
            console.log(err);
            bot.chat(`I cannot do the recipe for ${name} ${count} times`);
        }
    } else {
        failedCraftFeedback(bot, name, itemByName, craftingTable);
    }
    return true;
}

function failedCraftFeedback(bot, name, item, craftingTable) {
    const recipes = bot.recipesAll(item.id, null, craftingTable);
    if (!recipes.length) {
        throw new TypeError(`No crafting table nearby`);
    } else {
        const recipes = bot.recipesAll(
            item.id,
            null,
            mcData.blocksByName.crafting_table.id
        );
        // find the recipe with the fewest missing ingredients
        var min = 999;
        var min_recipe = null;
        for (const recipe of recipes) {
            const delta = recipe.delta;
            var missing = 0;
            for (const delta_item of delta) {
                if (delta_item.count < 0) {
                    const inventory_item = bot.inventory.findInventoryItem(
                        mcData.items[delta_item.id].name,
                        null
                    );
                    if (!inventory_item) {
                        missing += -delta_item.count;
                    } else {
                        missing += Math.max(
                            -delta_item.count - inventory_item.count,
                            0
                        );
                    }
                }
            }
            if (missing < min) {
                min = missing;
                min_recipe = recipe;
            }
        }
        const delta = min_recipe.delta;
        let message = "";
        for (const delta_item of delta) {
            if (delta_item.count < 0) {
                const inventory_item = bot.inventory.findInventoryItem(
                    mcData.items[delta_item.id].name,
                    null
                );
                if (!inventory_item) {
                    message += ` ${-delta_item.count} more ${
                        mcData.items[delta_item.id].name
                    }, `;
                } else {
                    if (inventory_item.count < -delta_item.count) {
                        message += `${
                            -delta_item.count - inventory_item.count
                        } more ${mcData.items[delta_item.id].name}`;
                    }
                }
            }
        }
        throw new TypeError(`I cannot make ${name} because I need: ${message}`);
    }
}

module.exports = { craftItem };