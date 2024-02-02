async function gotoPosition (bot, position) {
  bot.pathfinder.setGoal(
        new pathfinder.goals.GoalNear(position.x, position.y, position.z, 1)
    )
  return;
}

module.exports = { gotoPosition };
