#!/usr/bin/bash
sudo apt-get install -y python3-pip python3-numpy libatlas-base-dev libopenjp2-7 libtiff5 ttf-mscorefonts-installer python3-dev portaudio19-dev libjpeg-dev zlib1g-dev screen vim
pip install -r requirements.txt

curl -s https://get.pimoroni.com/inky | bash -s
