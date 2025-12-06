"# discord-bot-time-keeper" 

Note - I use AWS EC2 (Amazon Linux) to host the bot. Make sure to set up your instance first.

This is basically how you host this bot and run the script on AWS EC2:

1. Connect to the EC2 Instance
Open git bash on your folder that cointains your key pair (.pem key). Then write these:
chmod 400 YOUR_KEY.pem
ssh -i YOUR_KEY.pem ec2-user@YOUR_PUBLIC_IP

2. Update System Packages
sudo dnf update -y

3. Install Python, pip, git
sudo dnf install python3 python3-pip git -y

4. Clone This Repository (cd to your desired directory first)
cd ~/discord-bot (In my case)
git clone https://github.com/afnanhafidz/discord-bot-time-keeper.git discord-bot-time-keeper
cd discord-bot-time-keeper

5. Create and Activate a Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

6. Install Dependencies
pip install discord.py python-dotenv aiosqlite tzdata

7. Create the .env file
nano .env

Add this in .env :
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
LOG_CHANNEL_ID=YOUR_LOG_CHANNEL_ID
TIMEZONE=Asia/Kuala_Lumpur 

(You can also change the time zone)

Save:
CTRL + O -> Enter
CTRL + X -> Exit

8. Test the Bot (Optional)
python bot.py

9. Run the Bot 24/7 with systemd (Remember to change your directory. This example is mine)
sudo nano /etc/systemd/system/discordbot.service (You can also change the service name. Example: mybot.service)

Paste this in the discordbot.service:
[Unit]
Description=Discord Voice Logger Bot
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/discord-bot/discord-bot-time-keeper
EnvironmentFile=/home/ec2-user/discord-bot/discord-bot-time-keeper/.env
ExecStart=/home/ec2-user/discord-bot/discord-bot-time-keeper/venv/bin/python /home/ec2-user/discord-bot/discord-bot-time-keeper/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

Save:
CTRL + O -> Enter
CTRL + X -> Exit

10. Reload and enable service:
sudo systemctl daemon-reload
sudo systemctl enable discordbot
sudo systemctl start discordbot

11. Check status:
sudo systemctl status discordbot

12. Follow logs:
sudo journalctl -u discordbot -f

CTRL + C to exit from the logs / status

This bot is now running 24/7 on AWS EC2! やった＼(^_^)／


=================================
How to pull update from github
=================================
ssh -i YOUR_KEY.pem ec2-user@YOUR_PUBLIC_IP
cd to your directory that cointains this bot
git pull
sudo systemctl restart discordbot

