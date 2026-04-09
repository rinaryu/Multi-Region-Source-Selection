import os
import subprocess
import json
import time
import argparse

# Force execution from project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(BASE_DIR)

SSH_KEY_PATH = "~/.ssh/origin-key"
POLICIES = ["distance", "round_robin", "random"]
REGIONS = ["us-east-1", "us-west-2", "eu-central-1"]
ITERATIONS = 5

def get_terraform_outputs():
    result = subprocess.run(
        ["terraform", "output", "-json"],
        cwd="infra/multi-region",
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)

def ssh_run(ip, cmd):
    ssh_opts = ["-o", "StrictHostKeyChecking=no", "-i", SSH_KEY_PATH]
    result = subprocess.run(["ssh", *ssh_opts, f"ubuntu@{ip}", cmd], capture_output=True, text=True)
    return result.stdout

def parse_metrics(stdout):
    quality_id = "0" # Default lowest
    buffer_stalls = 0
    startup_delay = 0

    for line in stdout.split('\n'):
        if "Startup_Delay:" in line:
            parts = line.split("Startup_Delay: ")
            if len(parts) > 1:
                # remove 'ms' suffix and parse int
                try:
                    startup_delay = int(parts[1].split("ms")[0].strip())
                except:
                    pass
        if "Video Quality changed to ID:" in line and "(audio)" not in line:
            # Extract ID (0=360p, 1=480p, 2=720p)
            parts = line.split("Video Quality changed to ID: ")
            if len(parts) > 1:
                quality_id = parts[1].split()[0]
        if "WARN: Buffer empty" in line:
            buffer_stalls += 1
            
    return {"quality_id": int(quality_id), "buffer_stalls": buffer_stalls, "startup_delay": startup_delay}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help="The Ngrok URL pointing to your local Flask Controller (e.g. https://abc.ngrok.io)")
    args = parser.parse_args()

    # Pass the base URL directly to the EC2 clients
    domain = args.url

    outputs = get_terraform_outputs()
    clients = {
        "us-east-1": outputs.get("client_us_east_1_ip", {}).get("value"),
        "us-west-2": outputs.get("client_us_west_2_ip", {}).get("value"),
        "eu-central-1": outputs.get("client_eu_central_1_ip", {}).get("value")
    }

    results = []
    
    print(f"Starting {len(REGIONS) * len(POLICIES) * ITERATIONS} sequential streaming sessions...")

    for region in REGIONS:
        ip = clients[region]
        if not ip:
            print(f"Cannot find IP for {region}")
            continue

        for policy in POLICIES:
            for iteration in range(ITERATIONS):
                print(f"[{region}] [Policy: {policy}] - Iteration {iteration+1} / {ITERATIONS} ", end="", flush=True)
                
                # Execute headless puppet play
                cmd = f"node deploy/client/headless_client.js {domain} {policy} {region}"
                out = ssh_run(ip, cmd)
                
                # Parse
                if "command not found" in out or "Error:" in out:
                    print(f"\n[CRITICAL ERROR] The EC2 Node failed to execute the javascript headless client. Dependencies missing?")
                    print(f"Raw Output:\n{out}")
                    return

                metrics = parse_metrics(out)
                print(f"=> Quality ID: {metrics['quality_id']} | Stalls: {metrics['buffer_stalls']} | TTFB: {metrics['startup_delay']}ms")
                
                results.append({
                    "region": region,
                    "policy": policy,
                    "iteration": iteration + 1,
                    "quality_id": metrics['quality_id'],
                    "buffer_stalls": metrics['buffer_stalls'],
                    "startup_delay": metrics['startup_delay']
                })

    # Save to disk
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Successfully ran 45 streams. Test results written to results.json")

if __name__ == "__main__":
    main()
