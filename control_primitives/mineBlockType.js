async function mineBlockType(bot, name, count = 1) {
    // return if name is not string
    if (typeof name !== "string") {
        throw new Error(`name for mineBlock must be a string`);
    }
    if (typeof count !== "number") {
        throw new Error(`count for mineBlock must be a number`);
    }
    const blockByName = mcData.blocksByName[name];
    if (!blockByName) {
        throw new Error(`No block named ${name}`);
    }
    const blocks = bot.findBlocks({
        matching: [blockByName.id],
        maxDistance: 64,
        count: count,
    });

    // const visibleBlocks = [];
    // // Check each found block to see if the bot can see it
    // for (const block of blocks) {
    //     if (bot.canSeeBlock(bot.blockAt(block))) {
    //         visibleBlocks.push(block);
    //         if (visibleBlocks.length >= count) {
    //             break; // Stop once we have enough visible blocks
    //         }
    //     }
    // }

    if (blocks.length === 0) {
        bot.chat(`No ${name} nearby, please explore first`);
        return;
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
}

module.exports = { mineBlockType };