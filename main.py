import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
import webserver

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------- Global state --------------------
bump_channel_id = None
timer_running = False  # True if the 2 hours timer is active
pingRole = "Bump Ping"

# -------------------- Bot ready --------------------
@bot.event
async def on_ready():
    print("Anteiku Bot Online.")

# -------------------- Roles add / remove --------------------
@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=pingRole)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.name} Assign the role {pingRole}.")
    else:
        await ctx.send(f"Role dose not exist.")

@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=pingRole)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.name} has had {pingRole} removed.")
    else:
        await ctx.send(f"Role dose not exist.")

# -------------------- Timer function --------------------
async def start_timer():
    global timer_running, bump_channel_id
    if bump_channel_id is None:
        return

    timer_running = True
    await asyncio.sleep(2 * 60 * 60)  # wait 2 hours

    channel = bot.get_channel(bump_channel_id)
    if channel:
        # Get the role object from this guild
        role = discord.utils.get(channel.guild.roles, name=pingRole)
        if role:
            # Ping the role
            await channel.send(f"{role.mention}")
        #  The reminder message
        await channel.send("🔔 Reminder: It's time to bump again!")

    timer_running = False

# -------------------- Bump command --------------------
@bot.command()
async def bump(ctx):
    global bump_channel_id
    bump_channel_id = ctx.channel.id

    await ctx.send("✅ Server bumped! Timer started...")

    if not timer_running:
        await start_timer()  # start the 2 hours timer

# -------------------- Detect "Bump done" --------------------
@bot.event
async def on_message(message):
    global bump_channel_id, timer_running
    if message.author == bot.user:
        return

    if message.author.id == 302050872383242240:  #DISBOARD's bot's user ID
        channel = bot.get_channel(bump_channel_id)
        if channel:
            await channel.send("✅ Bump marked done! Starting the 2-hours timer again...")
        if not timer_running:
            await start_timer()  # restart the 2 hours timer automatically

    await bot.process_commands(message)

# -------------------- Run the bot --------------------
webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
