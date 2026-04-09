#!/bin/bash
IPs=("3.236.111.53" "44.247.231.108" "52.59.229.139")
KEY=~/.ssh/origin-key

for IP in "${IPs[@]}"; do
    echo "Starting installation on Client Node $IP..."
    
    # We securely pipe these commands natively into SSH
    ssh -o StrictHostKeyChecking=no -i $KEY ubuntu@$IP << 'EOF'
mkdir -p ~/deploy/client
cd ~/deploy/client

# Update and install Node + npm + Chromium dependencies
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs npm libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2

# Install puppeteer specifically in the client directory
npm install puppeteer
EOF
    echo "✅ Finished installation on $IP."
done
