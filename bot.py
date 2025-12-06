# bot.py
import os
import discord
from discord.ext import commands
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import aiosqlite
from dotenv import load_dotenv

# load .env for local dev
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kuala_Lumpur")
DB_PATH = os.getenv("DB_PATH", "voice_sessions.db")

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True  # helpful for display names

bot = commands.Bot(command_prefix="!", intents=intents)

def fmt(dt: datetime) -> str:
    # format with timezone abbreviation
    return dt.strftime("%d/%m/%Y %H:%M:%S %Z")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                guild_id INTEGER,
                member_id INTEGER,
                channel_id INTEGER,
                join_ts TEXT,
                PRIMARY KEY (guild_id, member_id)
            );
        """)
        await db.commit()

@bot.event
async def on_ready():
    await init_db()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot ready — logging voice events.")

async def save_join(guild_id: int, member_id: int, channel_id: int, join_ts_iso: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO sessions (guild_id, member_id, channel_id, join_ts)
            VALUES (?, ?, ?, ?);
        """, (guild_id, member_id, channel_id, join_ts_iso))
        await db.commit()

async def pop_join(guild_id: int, member_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT channel_id, join_ts FROM sessions WHERE guild_id = ? AND member_id = ?;
        """, (guild_id, member_id))
        row = await cursor.fetchone()
        if row:
            await db.execute("DELETE FROM sessions WHERE guild_id = ? AND member_id = ?;", (guild_id, member_id))
            await db.commit()
            return row[0], row[1]
        return None

@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    guild = member.guild
    # Try to find configured log channel in this guild by ID first
    log_channel = guild.get_channel(LOG_CHANNEL_ID) or bot.get_channel(LOG_CHANNEL_ID)
    # If not found, do nothing
    if log_channel is None:
        print(f"[WARN] Log channel {LOG_CHANNEL_ID} not found for guild {guild.name} ({guild.id}).")
        return

    now = datetime.now(tz=ZoneInfo(TIMEZONE))
    now_iso = now.isoformat()

    # JOIN
    if before.channel is None and after.channel is not None:
        # save join to DB
        await save_join(guild.id, member.id, after.channel.id, now_iso)
        await log_channel.send(f":green_circle: **{member.display_name}** joined **{after.channel.name}** at `{fmt(now)}`.")
        return

    # LEAVE
    if before.channel is not None and after.channel is None:
        popped = await pop_join(guild.id, member.id)
        if popped:
            chan_id, join_iso = popped
            join_dt = datetime.fromisoformat(join_iso).astimezone(ZoneInfo(TIMEZONE))
            duration = now - join_dt
            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            dur_str = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"
            await log_channel.send(
                f":red_circle: **{member.display_name}** left **{before.channel.name}** at `{fmt(now)}`\n"
                f"Duration: `{dur_str}` (joined at `{fmt(join_dt)}`)."
            )
        else:
            await log_channel.send(
                f":red_circle: **{member.display_name}** left **{before.channel.name}** at `{fmt(now)}` (join time unknown)."
            )
        return

    # MOVE (channel change)
    if before.channel is not None and after.channel is not None and before.channel != after.channel:
        popped = await pop_join(guild.id, member.id)
        # We'll log spent time in old channel if we have it, then insert new join
        if popped:
            old_chan_id, join_iso = popped
            join_dt = datetime.fromisoformat(join_iso).astimezone(ZoneInfo(TIMEZONE))
            duration = now - join_dt
            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            dur_str = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"
            await log_channel.send(
                f":arrows_counterclockwise: **{member.display_name}** moved from **{before.channel.name}** "
                f"to **{after.channel.name}** at `{fmt(now)}` (spent `{dur_str}` in {before.channel.name})."
            )
        else:
            await log_channel.send(
                f":arrows_counterclockwise: **{member.display_name}** moved from **{before.channel.name}** to **{after.channel.name}** at `{fmt(now)}`."
            )

        # Save new join
        await save_join(guild.id, member.id, after.channel.id, now_iso)
        return

# Optional admin command to set log channel at runtime
@bot.command()
@commands.has_guild_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    global LOG_CHANNEL_ID
    LOG_CHANNEL_ID = channel.id
    await ctx.send(f"Log channel set to {channel.mention} (ID: {LOG_CHANNEL_ID})")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Please set DISCORD_TOKEN in environment or .env")
    else:
        bot.run(DISCORD_TOKEN)
