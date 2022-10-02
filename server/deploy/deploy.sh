#! /bin/bash

# python 3.9.9

sudo apt install ffmpeg calibre -y

sudo apt remove calibre -y

playwright install

wget https://download.calibre-ebook.com/5.42.0/calibre-5.42.0-x86_64.txz -O /tmp/calibre-5.42.0-x86_64.txz
sudo mkdir -p /opt/calibre && sudo rm -rf /opt/calibre/* && sudo tar xvf /tmp/calibre-5.42.0-x86_64.txz -C /opt/calibre && sudo /opt/calibre/calibre_postinstall

pip install -r requirements.txt --no-dependencies

python -m pip install paddlepaddle==2.2.2 -i https://mirror.baidu.com/pypi/simple
