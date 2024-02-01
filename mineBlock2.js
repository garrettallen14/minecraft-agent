Vec3 = require('vec3').Vec3;

async function mineBlock(bot, name, count = 1) {
    const toolPlugin = require('mineflayer-tool').plugin
    bot.loadPlugin(toolPlugin);
    // Error checks for input parameters
    if (typeof name !== "string") {
        throw new Error("name for mineBlock must be a string");
    }
    if (typeof count !== "number") {
        throw new Error("count for mineBlock must be a number");
    }

    const blockByName = globalThis.mcData.blocksByName[name];
    if (!blockByName) {
        throw new Error(`No block named ${name}`);
    }

    // Find blocks
    const blocks = bot.findBlocks({
        matching: [blockByName.id],
        maxDistance: 32,
        count: count,
    });
    if (blocks.length === 0) {
        bot.chat(`No ${name} nearby, please explore first`);
        return;
    }

    // Prepare target blocks
    const targets = blocks.slice(0, count).map(blockPos => bot.blockAt(blockPos));
    bot.chat(`Mining ${targets.length} of ${name}`);

    await bot.tool.equipForBlock(bot.blockAt(targets[0].position));
    const distanceTo = ((pos1, pos2) => {
        return Math.sqrt(
            Math.pow(pos1.x - pos2.x, 2) +
            Math.pow(pos1.y - pos2.y, 2) +
            Math.pow(pos1.z - pos2.z, 2)
        );
    });
    

    for (const target of targets) {
        if (target == null) continue;

        bot.pathfinder.setMovements(bot.pathfinder.movements);
        await bot.pathfinder.setGoal(new pathfinder.goals.GoalGetToBlock(
            target.position.x, target.position.y, target.position.z
        ));

        await bot.dig(target);
        // collect dropped items;
        let list = [];
        for (const entity of bot.entities) {
            console.log(entity)
            if (entity.displayName === 'Item' && distanceTo(bot.entity.position, entity.position) < 10) {
                console.log(entity)
                list.push(entity.position);
            }
        }
        for (let i = 0; i < list.length; i++) {
            await bot.pathfinder.setGoal(new pathfinder.goals.GoalGetToBlock(list[i].x, list[i].y, list[i].z));
        }
    }

    bot.chat(`Mined ${targets.length} of ${name}`);
}


module.exports = { mineBlock };