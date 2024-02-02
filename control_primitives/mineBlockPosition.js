async function mineBlockPosition(bot, position) {
    // return if name is not string
    await bot.chat(`breaking block at ${position}`);
    target = bot.blockAt(position);
    bot.tool.equipForBlock(target);
    await bot.collectBlock.collect(target, {
        ignoreNoPath: true,
        timeout: 5000000
    });
}

module.exports = { mineBlockPosition };