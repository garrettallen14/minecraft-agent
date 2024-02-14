// shoot 1 pig with a bow: shoot(bot, "bow", "pig");
async function shoot(bot, weapon, target) {
    const validWeapons = [
        "bow",
        "crossbow",
        "snowball",
        "ender_pearl",
        "egg",
        "splash_potion",
        "trident",
    ];
    if (!validWeapons.includes(weapon)) {
        throw new TypeError(`${weapon} is not a valid weapon for shooting`);
    }

    const weaponItem = mcData.itemsByName[weapon];
    if (!bot.inventory.findInventoryItem(weaponItem.id, null)) {
        throw new TypeError(`No ${weapon} in inventory for shooting`);
    }

    const targetEntity = bot.nearestEntity(
        (entity) =>
            entity.name === target
    );
    if (!targetEntity) {
        throw new TypeError(`No ${target} nearby`);
    }
    bot.hawkEye.autoAttack(targetEntity, "bow");
    bot.on('auto_shot_stopped', (target) => {
    })
    return true;
}

module.exports = { shoot };