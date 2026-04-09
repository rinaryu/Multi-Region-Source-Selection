/**
 * Headless script for AWS Client Nodes to automatically request videos and log metrics.
 * Pre-requisite: npm install puppeteer
 * Run with: node headless_client.js <controller_ip> <policy> <client_region>
 */
const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
    const args = process.argv.slice(2);
    if (args.length < 3) {
        console.log("Usage: node headless_client.js <controller_ip> <policy> <client_region>");
        process.exit(1);
    }
    
    const [controllerIp, policy, region] = args;
    console.log(`Starting Headless Client Simulator [Region: ${region}, Policy: ${policy}]`);
    
    const browser = await puppeteer.launch({ 
        headless: 'new', // new headless mode
        args: [
            '--no-sandbox', 
            '--autoplay-policy=no-user-gesture-required',
            '--disable-web-security' // Ignore CORS just in case for local File UI interactions
        ] 
    });
    const page = await browser.newPage();

    // Intercept console logs from dash.js
    page.on('console', msg => {
        const text = msg.text();
        if (text.includes('METRIC:') || text.includes('WARN:') || text.includes('ERROR:')) {
            console.log(text);
        }
    });

    const indexUrl = 'file://' + path.resolve(__dirname, 'index.html');
    console.log("Loading UI:", indexUrl);
    await page.goto(indexUrl);
    
    // Inject the controller IP and auto-start the player
    await page.evaluate((ctrlIp, p, r) => {
        window.CONTROLLER_IP = ctrlIp;
        window.autoload(p, r);
    }, controllerIp, policy, region);
    
    // Monitor playback for 90 seconds to observe ABR behavior and rebuffering
    console.log("Stream initiated. Capturing telemetry for 60 seconds...");
    await new Promise(r => setTimeout(r, 60000));
    
    console.log("Test duration complete. Shutting down.");
    await browser.close();
})();
