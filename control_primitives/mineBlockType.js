async function mineBlockType(bot, name, count = 1) {
    // return if name is not string
    if (typeof name !== "string") {
        bot.chat(`name for mineBlock must be a string`);
        return false;
    }
    if (typeof count !== "number") {
        bot.chat(`count for mineBlock must be a number`);
        return false;
    }
    const blockByName = mcData.blocksByName[name];
    if (!blockByName) {
        bot.chat(`No block named ${name}`);
        return false;
    }
    const blocks = bot.findBlocks({
        matching: [blockByName.id],
        maxDistance: 64,
        count: count,
    });

    if (blocks.length === 0) {
        bot.chat(`No ${name} nearby, please explore first`);
        return false;
    }
    console.log(blocks.length, 'blocks found')

    bot.tool.equipForBlock(bot.blockAt(blocks[0]));

    // If stone, it glitches, so we use the offset
    if (name === 'stone') {
        off = -1;
    } else {
        off = 0;
    }

    const targets = [];
    for (let i = 0; i < Math.min(blocks.length, count); i++) {
        targets.push(bot.blockAt(blocks[i].offset(0,off,0)));
    }
    await bot.collectBlock.collect(targets, {
        ignoreNoPath: true,
        count: count,
        timeout: 5000000
    });
    bot.chat(`Mined some ${name}`)
    
    return true;
}

module.exports = { mineBlockType };