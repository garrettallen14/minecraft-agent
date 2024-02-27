async function mineBlockType(bot, name, count = 1) {
    // return if name is not string
    if (typeof name !== "string") {
        throw new TypeError(`name for mineBlock must be a string`);
    }
    if (typeof count !== "number") {
        throw new TypeError(`count for mineBlock must be a number`);
    }
    const blockByName = mcData.blocksByName[name];
    if (!blockByName) {
        throw new TypeError(`No block named ${name}`);
    }
    const blocks = bot.findBlocks({
        matching: [blockByName.id],
        maxDistance: 64,
        count: count,
    });

    const viewable_blocks = [];
    for (let i = 0; i < blocks.length; i++) {
        if (bot.canSeeBlock(bot.blockAt(blocks[i]))) {
            viewable_blocks.push(blocks[i]);
        }
    }

    if (viewable_blocks.length === 0) {
        throw new TypeError(`No ${name} nearby, please explore first`);
    }
    console.log(viewable_blocks.length, 'blocks found')

    bot.tool.equipForBlock(bot.blockAt(viewable_blocks[0]));

    // If stone, it glitches, so we use the offset
    if (name === 'stone') {
        off = -1;
    } else {
        off = 0;
    }

    const targets = [];
    for (let i = 0; i < Math.min(viewable_blocks.length, count); i++) {
        targets.push(bot.blockAt(viewable_blocks[i].offset(0,off,0)));
    }

    // await bot.collectBlock.collect(targets, {
    //     ignoreNoPath: true,
    //     count: count,
    //     timeout: 5000000
    // });

    bot.chat(`I can see ${targets.length} of ${name}.`)
    for (let i = 0; i < targets.length; i++) {
        const target = targets[i];
        let attempts = 0;
        while (attempts < 5) {
            console.log('attempting to mine')
            try {
                await bot.collectBlock.collect(target, {
                    ignoreNoPath: false,
                    count: 1,
                    timeout: 10000
                });
                break;
            } catch (err) {
                bot.pathfinder.stop()
                attempts++;
                console.log(err);
                continue;
            }
        }
    }
    bot.chat(`Mined some ${name}`)
    
    return true;
}

module.exports = { mineBlockType };