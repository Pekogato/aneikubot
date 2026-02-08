import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
import random
import texts
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
    await asyncio.sleep(2 * 60 * 60)  # wait 2 hours 2 * 60 * 60

    channel = bot.get_channel(bump_channel_id)
    if channel:
        # Get the role object from this guild
        role = discord.utils.get(channel.guild.roles, name=pingRole)
        if role:
            # Ping the role
            await channel.send(f"{role.mention}")
        #  The reminder message
        embed = discord.Embed(title= "🔔 Reminder!!", description="It's time to bump again!", color=discord.Color.dark_purple())
        embed.add_field(name="How to bump?", value='Send "/bump" in this channel to bump.')

        await channel.send(embed=embed)


    timer_running = False

# -------------------- Bump command --------------------
@bot.command()
async def bump(ctx):
    global bump_channel_id
    bump_channel_id = ctx.channel.id

    embed = discord.Embed(title="Bump reminder", description= "Bump reminder has started! ✅ ", color=discord.Color.green())
    embed.add_field(name= "We'll remind you after 2 hours.", value= " The reminder will take place in this channel")
    embed.set_image(url="https://media.tenor.com/TYGaQfylEvQAAAAi/auque-7-dias-tarde.gif")

    await ctx.send(embed=embed)

    if not timer_running:
        await start_timer()  # start the 2 hours timer

# -------------------- Detect "Bump done" --------------------
@bot.event
async def on_message(message):
    global bump_channel_id, timer_running
    if message.author == bot.user:
        return

    if message.author.id == 302050872383242240:  #DISBOARD's bot's user ID 302050872383242240
        channel = bot.get_channel(bump_channel_id)
        if channel:
            embed = discord.Embed(title="Bumb is done!", description=f"✅ Bump marked done! Starting the 2-hours timer again...", color=discord.Color.green())
            embed.set_image(url="https://cdn.discordapp.com/attachments/969959668732526592/1452726925230346401/SPOILER_809c52bce47f98c54418cbc0d7a347e5.gif?ex=69897c21&is=69882aa1&hm=8cb04190ef35d983e668947e9264ff4d10e63388e9c897a56ea75f4021e828e4&")
            await channel.send(embed=embed)

        if not timer_running:
            await start_timer()  # restart the 2 hours timer automatically

    await bot.process_commands(message)

#------------- true or false -----------------
@bot.command()
async def tof(ctx, *, tof_question=None):
    #if no question provided -----------
    if not tof_question:
        await ctx.send("Please provide a question!")
        return

    tof_words = tof_question.split() # splits the message to check for true or false rig words
    true_responses = random.choice(texts.tof_true)
    false_responses = random.choice(texts.tof_false)

    await ctx.message.delete() #deletes the original message

#if rigged true -----------------
    if tof_words[0].lower().replace("||","") == 'true':
        question = " ".join(tof_words[1:]) # joins them after false

        embed = discord.Embed(title="True or False", description=f"{ctx.author}: {question}", color=discord.Color.green())
        embed.add_field(name="True", value=true_responses) #embed for true
        embed.set_image(url="https://c.tenor.com/fTLu-W-AzMUAAAAd/lie-detector-meme.gif")

        await ctx.send(embed=embed) #sends the embed

#if rigged false -----------------
    elif tof_words[0].lower().replace("||","") == 'false':
        question = " ".join(tof_words[1:]) #joins them after false

        embed = discord.Embed(title="True or False", description=f"{ctx.author}: {question}", color=discord.Color.red())
        embed.add_field(name="False", value=false_responses)  #this whole thing is the embed for false
        embed.set_image(url="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExcHY4b2VjdWI1Y2g0dWl2dmptZG9oeHh6cmxvcmdmczJta3BwejRoeSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/pbIzFMcoPJp7607u3Q/giphy.gif")

        await ctx.send(embed=embed) #sends the embed

#Normal not rigged ----------------
    else:
        question = " ".join(tof_words) #joins them back

        if random.choice([True, False]): #50/50 to choice one of them
            embed = discord.Embed(title="True or False", description=f"{ctx.author}: {question}", color=discord.Color.green())
            embed.add_field(name="True", value=true_responses) #rue embed
            embed.set_image(url="https://c.tenor.com/fTLu-W-AzMUAAAAd/lie-detector-meme.gif")
        else:
            embed = discord.Embed(title="True or False", description=f"{ctx.author}: {question}", color=discord.Color.red())
            embed.add_field(name="False", value=false_responses) #false embed
            embed.set_image(url="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExcHY4b2VjdWI1Y2g0dWl2dmptZG9oeHh6cmxvcmdmczJta3BwejRoeSZlcD12MV9pbnRlcm5hbF9naWQmY3Q9Zw/pbIzFMcoPJp7607u3Q/giphy.gif")

        await ctx.send(embed=embed) #sends the embed

# -------------------- Run the bot --------------------
webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
