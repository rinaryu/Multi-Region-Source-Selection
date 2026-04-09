document.addEventListener("DOMContentLoaded", () => {
    const video = document.querySelector("#videoPlayer");
    const loadBtn = document.querySelector("#loadBtn");
    const policySelect = document.querySelector("#policySelect");
    const regionSelect = document.querySelector("#regionSelect");
    const metricsDiv = document.querySelector("#metrics");
    const logList = document.querySelector("#logList");

    function logMetric(msg) {
        console.log("METRIC:", msg);
        metricsDiv.style.display = "block";
        const li = document.createElement("li");
        li.textContent = `[${new Date().toISOString()}] ${msg}`;
        logList.appendChild(li);
    }

    let hasStarted = false;
    let requestTime = 0;

    let player = dashjs.MediaPlayer().create();
    
    // Force Dash.js to only buffer 2 seconds of video at a time (Low-Latency mode). 
    // Since our video is only 9 seconds, if we don't restrict this, Dash.js will download the entire 
    // video into RAM instantly, making stalls physically impossible. This makes the player highly sensitive to lag!
    player.updateSettings({
        streaming: {
            buffer: {
                stableBufferTime: 2,
                bufferTimeAtTopQuality: 2,
                bufferTimeAtTopQualityLongForm: 2
            }
        }
    });
    
    player.initialize(video, null, true); // Initialize but don't load URL yet

    // Listen for QOE Events
    player.on(dashjs.MediaPlayer.events.PLAYBACK_PLAYING, () => {
        if (!hasStarted) {
            logMetric(`Startup_Delay: ${Date.now() - requestTime}ms`);
            hasStarted = true;
        }
        logMetric("Playback started smoothly");
    });
    
    player.on(dashjs.MediaPlayer.events.BUFFER_EMPTY, () => {
        logMetric("WARN: Buffer empty - Rebuffering event triggered!");
    });
    
    player.on(dashjs.MediaPlayer.events.QUALITY_CHANGE_RENDERED, (e) => {
        logMetric(`Video Quality changed to ID: ${e.newQuality} (${e.mediaType})`);
    });

    player.on(dashjs.MediaPlayer.events.ERROR, (e) => {
        logMetric(`ERROR: Dash.js encountered an error: ${JSON.stringify(e)}`);
    });

    loadBtn.addEventListener("click", () => {
        hasStarted = false;
        requestTime = Date.now();
        
        const policy = policySelect.value;
        const region = regionSelect.value;
        const sessionId = Math.random().toString(36).substring(7);
        
        // Read Controller IP from global window scope (for headless testing) or fallback to local
        const controllerIp = window.CONTROLLER_IP || "localhost";
        
        // Ask Controller API to dynamically rewrite and serve MPD for this specific user
        let controllerBase = window.CONTROLLER_IP || "http://localhost:8000";
        if (!controllerBase.startsWith("http")) { controllerBase = "http://" + controllerBase + ":8000"; }
        const controllerUrl = `${controllerBase}/stream.mpd?session=${sessionId}&policy=${policy}&client_region=${region}`;
        
        logMetric(`Loading stream using policy [${policy}] from controller [${controllerIp}]`);
        logMetric(`Manifest URL Request: ${controllerUrl}`);
        
        player.attachSource(controllerUrl);
    });
    
    // Webdriver hook
    window.autoload = function(policy, region) {
        policySelect.value = policy;
        regionSelect.value = region;
        loadBtn.click();
    };
});
