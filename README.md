Note - I use AWS EC2 (Amazon Linux) to host the bot. Make sure to set up your instance first.<br>

This is basically how you host this bot and run the script on AWS EC2:<br>

1. Connect to the EC2 Instance <br>
Open git bash on your folder that cointains your key pair (.pem key). Then write these:<br>
chmod 400 YOUR_KEY.pem<br>
ssh -i YOUR_KEY.pem ec2-user@YOUR_PUBLIC_IP<br>

2. Update System Packages<br>
sudo dnf update -y<br>

3. Install Python, pip, git<br>
sudo dnf install python3 python3-pip git -y<br>

4. Clone This Repository (cd to your desired directory first)<br>
cd ~/discord-bot (In my case)<br>
git clone https://github.com/afnanhafidz/discord-bot-time-keeper.git discord-bot-time-keeper<br>
cd discord-bot-time-keeper<br>

5. Create and Activate a Virtual Environment<br>
python3 -m venv venv<br>
source venv/bin/activate<br>
pip install --upgrade pip<br>

6. Install Dependencies<br>
pip install discord.py python-dotenv aiosqlite tzdata<br>

7. Create the .env file<br>
nano .env<br>

Add this in .env :<br>
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN<br>
LOG_CHANNEL_ID=YOUR_LOG_CHANNEL_ID<br>
TIMEZONE=Asia/Kuala_Lumpur <br>

(You can also change the time zone)<br>

Save:<br>
CTRL + O -> Enter<br>
CTRL + X -> Exit<br>

8. Test the Bot (Optional)<br>
python bot.py<br>

9. Run the Bot 24/7 with systemd (Remember to change your directory. This example is mine)<br>
sudo nano /etc/systemd/system/discordbot.service (You can also change the service name. Example: mybot.service)<br>

Paste this in the discordbot.service:<br>
[Unit]<br>
Description=Discord Voice Logger Bot<br>
After=network.target<br>

[Service]<br>
User=ec2-user<br>
WorkingDirectory=/home/ec2-user/discord-bot/discord-bot-time-keeper<br>
EnvironmentFile=/home/ec2-user/discord-bot/discord-bot-time-keeper/.env<br>
ExecStart=/home/ec2-user/discord-bot/discord-bot-time-keeper/venv/bin/python /home/ec2-user/discord-bot/discord-bot-time-keeper/bot.py<br>
Restart=always<br>
RestartSec=5<br>

[Install]<br>
WantedBy=multi-user.target<br>

Save:<br>
CTRL + O -> Enter<br>
CTRL + X -> Exit<br>

10. Reload and enable service:<br>
sudo systemctl daemon-reload<br>
sudo systemctl enable discordbot<br>
sudo systemctl start discordbot<br>

11. Check status:<br>
sudo systemctl status discordbot<br>

12. Follow logs:<br>
sudo journalctl -u discordbot -f<br>

CTRL + C to exit from the logs / status<br>

This bot is now running 24/7 on AWS EC2! やった＼(^_^)／<br>


=================================<br>
How to pull update from github<br>
=================================<br>
ssh -i YOUR_KEY.pem ec2-user@YOUR_PUBLIC_IP<br>
cd to your directory that cointains this bot<br>
git pull<br>
sudo systemctl restart discordbot<br>

