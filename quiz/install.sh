#!/bin/bash

# Ensure the script is run as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Update package list and upgrade packages
echo "Updating package list and upgrading packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Nginx and Git
echo "Installing Nginx and Git..."
sudo apt-get install -y nginx git

# Start and enable Nginx service
echo "Starting and enabling Nginx..."
sudo systemctl start nginx
sudo systemctl enable nginx

# Clone the web app repository from GitHub
echo "Cloning the web app repository..."
repo_url='https://github.com/Lektro4440/techmylife.git'
git clone $repo_url /var/www/html/quiz-app

# Configure Nginx to serve the quiz app
echo "Configuring Nginx to serve the quiz app..."
sudo ln -s /var/www/html/quiz-app/quiz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Complete
echo "Quiz App installation complete. Access it at http://your_server_ip/quiz"