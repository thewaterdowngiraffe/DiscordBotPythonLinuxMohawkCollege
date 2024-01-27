#!/bin/sh

#makes the service
echo "[Unit]\
Description=discrod bot\
After=network-online.target\
Wants=network-online.target\
\
\
[Service]\
ExecStart=/usr/bin/python3 /home/root/python/bot.py\
\
[Install]\
WantedBy=multi-user.target" >> /etc/systemd/system/discordBot.service

#enabale and start the service
systemctl start discrodBot
systemctl enable diacordBot

#install the python required stuff
apt-get update && apt-get install python3-pip
python3 -m pip install -U discord.py
pip install python-dotenv
