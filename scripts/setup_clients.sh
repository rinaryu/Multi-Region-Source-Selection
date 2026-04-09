#!/bin/bash
IPs=($(terraform -chdir=infra/multi-region output -raw client_us_east_1_ip) $(terraform -chdir=infra/multi-region output -raw client_us_west_2_ip) $(terraform -chdir=infra/multi-region output -raw client_eu_central_1_ip))
KEY=~/.ssh/origin-key

for IP in "${IPs[@]}"; do
    echo "Starting installation on Client Node $IP..."
    
    # We securely pipe these commands natively into SSH
    ssh -o StrictHostKeyChecking=no -i $KEY ubuntu@$IP << 'EOF'
mkdir -p ~/deploy/client
cd ~/deploy/client

# Purge default Ubuntu Node 12 packages to prevent dpkg conflicts during upgrade
sudo apt-get remove -y nodejs libnode72 npm || true
sudo apt-get autoremove -y

# Update and install Node + Chromium dependencies (Node 18 requires Nodesource setup first)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2

# Install puppeteer specifically in the client directory
npm install puppeteer
EOF
    echo "✅ Finished installation on $IP."
done
