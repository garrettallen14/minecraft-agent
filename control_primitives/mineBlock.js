async function mineBlock(bot, name, count = 1) {
    // return if name is not string
    if (typeof name !== "string") {
        throw new Error(`name for mineBlock must be a string`);
    }
    if (typeof count !== "number") {
        throw new Error(`count for mineBlock must be a number`);
    }
    const blockByName = globalThis.mcData.blocksByName[name];
    if (!blockByName) {
        throw new Error(`No block named ${name}`);
    }
    const blocks = bot.findBlocks({
        matching: [blockByName.id],
        maxDistance: 64,
        count: count,
    });
    if (blocks.length === 0) {
        bot.chat(`No ${name} nearby, please explore first`);
        return;
    }

    const targets = [];
    for (let i = 0; i < Math.min(blocks.length, count); i++) {
        targets.push(bot.blockAt(blocks[i]));
    }
    bot.chat(`Mining ${targets.length} of ${name}`);

    // move to each target, then decide if we need to build up to mine it
    for (let i = 0; i < targets.length; i++) {
        // move to the target
        await bot.pathfinder.setGoal(new pathfinder.goals.GoalNear(targets[i].position.x, targets[i].position.y, targets[i].position.z, 10), timeout = 30000);

        if (Math.abs(bot.entity.position.y - targets[i].position.y) > 4) {
            await bot.pathfinder.setGoal(new pathfinder.goals.GoalY(targets[i].position.y, 3), timeout = 30000);
        }
        
        await bot.collectBlock.collect(targets[i], {
            ignoreNoPath: true,
            timeout: 30000,
        });

        bot.chat('Mined one block!')
    }

    
}

module.exports = { mineBlock };