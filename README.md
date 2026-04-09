# Multi-Region-Source-Selection
A smaller scale Dynamic Adaptive Streaming over HTTP (DASH) application which deploys web servers from several different geographic locations. The proxy that routes within the distributed content delivery network does so based on server proximity and geographic distance.


## Used/Required Packages
ffmpeg: Creating specific bitrate rendition(s) for content.  
Bento4 v1.6.0.640 (or higher): Used to segment media content and build initial manifest for corresponding segments.  
Flask: The controller framework that receives user requests and runs the source selector.  

## How to Run
> **Note:** Because this project auto-provisions live EC2 instances across the globe, you must have your AWS CLI configured (`aws configure`) with valid administrative credentials before beginning. 

1. **Package Media:** Transcode and DASH-package the raw MP4 videos.
   ```bash
   python3 packaging/pipeline.py
   ```
2. **Provision Infrastructure:** Deploy the global network using Terraform. Ensure you pass your public SSH key variable so the deployment scripts can interact with the nodes.
   ```bash
   cd deploy/terraform
   terraform apply -var="public_key_path=~/.ssh/origin-key.pub"
   ```
3. **Deploy Origins:** Securely copy the server code and DASH chunks to all spawned AWS instances.
   ```bash
   python3 scripts/deploy.py
   ```
4. **Setup Edge Clients:** Install Chromium and Headless node environments on the client instances.
   ```bash
   bash scripts/setup_clients.sh
   ```
5. **Start Controller:** Boot the application-layer intelligence router.
   ```bash
   python3 controller/controller_api.py
   ```
6. **Expose Controller:** In a new terminal, tunnel the API to the public internet.
   ```bash
   ngrok http 8000
   ```
7. **Execute Test Suite:** Fire the orchestrator to simulate global traffic patterns (use your exact Ngrok URL).
   ```bash
   python3 scripts/run_experiments.py --url https://<your-ngrok-url>.ngrok.app
   ```
8. **Synthesize Data:** Generate the formatted latency/stalling report.
   ```bash
   python3 scripts/analyze.py
   ```
