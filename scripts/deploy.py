import os
import subprocess
import json
import time

# Automatically switch to project root so the script works from any folder
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(BASE_DIR)

SSH_KEY_PATH = "~/.ssh/origin-key"

def get_terraform_outputs():
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd="infra/multi-region",
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        print("Terraform output failed. Make sure you ran 'terraform apply' inside infra/multi-region.")
        return {}

def ssh_run(ip, cmd):
    ssh_opts = ["-o", "StrictHostKeyChecking=no", "-i", SSH_KEY_PATH]
    subprocess.run(["ssh", *ssh_opts, f"ubuntu@{ip}", cmd], check=False)

def scp_run(ip, src, dest, is_dir=False):
    ssh_opts = ["-o", "StrictHostKeyChecking=no", "-i", SSH_KEY_PATH]
    cmd = ["scp", *ssh_opts]
    if is_dir:
        cmd.append("-r")
    cmd.extend([src, f"ubuntu@{ip}:{dest}"])
    subprocess.run(cmd, check=False)

def build_origins_json(outputs):
    origins = {
        "us-east-1": outputs.get("us_east_1_ip", {}).get("value"),
        "us-west-2": outputs.get("us_west_2_ip", {}).get("value"),
        "eu-central-1": outputs.get("eu_central_1_ip", {}).get("value")
    }

    controller_origins = {}
    for region, ip in origins.items():
        if ip:
            controller_origins[region] = f"http://{ip}:8001"
            
    with open("origins.json", "w") as f:
        json.dump(controller_origins, f, indent=2)
    print(f"Generated origins.json mapping: {controller_origins}")
    return origins

def deploy_to_origins(origins):
    for region, ip in origins.items():
        if not ip:
            print(f"Skipping Origin {region} - No IP found.")
            continue
            
        print(f"Deploying to Origin {region} ({ip})...")
        ssh_run(ip, "mkdir -p deploy/dash deploy/origins")
        scp_run(ip, "dash/test_run", "deploy/dash/", is_dir=True)
        scp_run(ip, "origins/origin_server.py", "deploy/origins/")
        
        # Kill any existing server, run in background via nohup
        start_cmd = "sudo fuser -k 8001/tcp || true; nohup python3 deploy/origins/origin_server.py --port 8001 --dir deploy/dash/test_run </dev/null >/dev/null 2>&1 &"
        ssh_run(ip, start_cmd)
        print(f"=> Completed Origin {region}")

def deploy_to_clients(outputs):
    clients = {
        "us-east-1": outputs.get("client_us_east_1_ip", {}).get("value"),
        "us-west-2": outputs.get("client_us_west_2_ip", {}).get("value"),
        "eu-central-1": outputs.get("client_eu_central_1_ip", {}).get("value")
    }

    for region, ip in clients.items():
        if not ip:
            print(f"Skipping Client {region} - No IP found.")
            continue
            
        print(f"Deploying to Client Node {region} ({ip})...")
        ssh_run(ip, "mkdir -p deploy/client")
        scp_run(ip, "client", "deploy/", is_dir=True)
        
        print(f"=> Completed Client {region}. Remember to install Node/Puppeteer dependencies on it!")

def main():
    if SSH_KEY_PATH == "AWS_KEY.pem":
        print("ERROR: Please edit scripts/deploy.py and set SSH_KEY_PATH to your actual AWS .pem key path.")
        return

    outputs = get_terraform_outputs()
    if not outputs:
        return
        
    print("--- 1. Building origins.json for Controller ---")
    origins = build_origins_json(outputs)
    
    print("\n--- 2. Deploying content to Origin Servers ---")
    deploy_to_origins(origins)

    print("\n--- 3. Deploying code to Client Nodes ---")
    deploy_to_clients(outputs)

    print("\n✅ Deployment complete!")

if __name__ == "__main__":
    main()
