export function initialize() {
    console.log('initializing');
    const mineflayer = require('mineflayer');
    const mc = require('minecraft-protocol');
    const forgeHandshake = require('minecraft-protocol-forge').forgeHandshake;

    // Configuration for your Minecraft client
    const host = 'localhost'; // Replace with your server's host
    const port = 22222; // Replace with your server's port
    const username = `poo_bucket${Math.floor(Math.random() * 1000)}`; // Random username
    const password = ''; // Add password if needed, leave empty for offline servers

    // Create a Minecraft protocol client
    var client = mc.createClient({
        host: host,
        port: port,
        username: username,
        password: password
    });

    // Perform Forge handshake to support Forge mods
    forgeHandshake(client, {
        forgeMods: [
            { modid: 'mcp', version: '9.18' },
            { modid: 'FML', version: '8.0.99.99' },
            { modid: 'Forge', version: '11.15.0.1715' },
            { modid: 'IronChest', version: '6.0.121.768' }
        ]
    });

    // Create a Mineflayer bot using the Minecraft protocol client
    const bot = mineflayer.createBot({
        client: client, // Use the existing Minecraft protocol client
        username: username, // Use the same username
        host: host, 
        port: port,
        hideErrors: false
    });

    bot.once('login', () => {
        console.log('Bot has logged in.');
        bot.chat('I spawned');
    });

    return bot;
}