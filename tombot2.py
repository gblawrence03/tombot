# bot.py
import os
import discord
import re
import random
import asyncio
import datetime
from dotenv import load_dotenv
from discord.ext import commands, tasks

currentpath = os.path.dirname(__file__)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

global reminders
global cancelReminders
global waitingCancel 
waitingCancel = None
reminders = []
numberCap = 5
message_cache = []
        
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(
        f'{client.user} has connected to Discord, in server:\n'
        f'{guild.name}(id: {guild.id})'
        )

@client.event
async def on_message(message):
    global cancelReminders
    global waitingCancel
    message_content = message.content
    string = ""
    message_send = message_content

    #if author is loha
    if message.author.id == 260774722298576897:
        #if channel is nod channel

        if message.channel.id == 412179888733290496:
            channel = client.get_channel(351403144686862337)
            if message_send.startswith('!embed'):
                embedVar = discord.Embed(title=message_send[6:], description="Use !r [time] now", color=discord.Color.blue())
                #embedVar.add_field(name="Field1", value="hi", inline=False)
                await channel.send(embed=embedVar)
            else:
                await message.delete()
                await channel.send(message_send)
        if message_send.startswith('!nick'):
            name = message_send[5:]
            await message.guild.me.edit(nick=name)
            await message.delete()

    if message.author != client.user:
        print('Message recieved: "' + message_content + '"')

        if message.author.id == 238736842113941504:
            print("GEEM HAS SPOKEN")
            if "loli" in message_content.lower():
                await message.delete()
                print("deleted")
                
        if message.author.id == 694866284948488253:
            print("TOM HAS SPOKEN")

        elif message.author.id == 173749612589481984:
            print("JACKY HAS SPOKEN")

        global reminders
        currentTime = datetime.datetime.now()
        words = message_content.split(" ")

        if words[0] == "!r":
            print("Reminder")
            print(words)
            value = float(words[1])
            suffix = words[2]
            reason = "None"
            if len(words) >= 4:
                reason = ""
                for i in range(3, len(words)):
                    reason = reason + words[i] + " "
            print("Reason: " + reason)
            time = False
            if ('hour' in suffix) or ('hr' in suffix):
                print("Time unit: hours")
                time = datetime.timedelta(hours=value)
            elif "min" in suffix:
                print("Time unit: minutes")
                time = datetime.timedelta(minutes=value)
            elif suffix == "day" or suffix == "days":
                print("Time unit: days")
                time = datetime.timedelta(days=value)
            elif "sec" in suffix:
                print("Time unit: seconds")
                time = datetime.timedelta(seconds=value)
            if time:
                print("Length of reminder: " + str(time))
                if value>0:
                    newTime = currentTime + time
                    newReminder = [message.author.id, newTime, message.channel.id, len(reminders) - 1, reason]
                    reminders.append(newReminder)
                    print("Reminder added")
                    emoji = '\N{THUMBS UP SIGN}'
                    await message.add_reaction(emoji)
                    #await asyncio.sleep(10) 
                    #await message.delete()

        elif message_content == "!cancel":
            cancelReminders = []
            for i in range(len(reminders)):
                try:
                    if reminders[i][0] == message.author.id:
                        cancelReminders.append(reminders[i])
                except: 
                    pass
            toCancel = cancelReminders[len(cancelReminders) - 1][3]
            for i in range(len(reminders)):
                if reminders[i][3] == toCancel:
                    del reminders[i]
            newmessage = await message.channel.send("Reminder removed.")
            await message.delete()
            await asyncio.sleep(10) 
            await newmessage.delete()

        elif message_content == "!reminders":
            messagesToDelete = []
            msg = await message.channel.send("Here are your reminders: ")
            messagesToDelete.append(msg)
            num = 1
            for i in range(len(reminders)):
                try:
                    if reminders[i][0] == message.author.id:
                        msg = await message.channel.send(str(num) + ": " + reminders[i][1].strftime("%d/%m/%Y, %H:%M") + " for: " + reminders[i][4])
                        num += 1
                        messagesToDelete.append(msg)
                        print("hi")
                except Exception as e: 
                    print(e)
            await asyncio.sleep(10)
            for i in messagesToDelete:
                await i.delete()
                
        elif message_content == "!clearreminders":
            for i in message_cache:
                try:
                    await i.delete()
                except:
                    pass

    #pin messages
    if message.author.id == 316685489757487105 or message.author.id == 260774722298576897:
        if message_send.startswith("!pin"):
            pinMessageID = message_content[4:]
            print(pinMessageID)
            pinMessage = await message.channel.fetch_message(pinMessageID)
            pinMessageContent = pinMessage.content
            pinMessageLink = pinMessage.jump_url
            pinMessageAuthor = pinMessage.author.mention
            channel = client.get_channel(853761820724953149)
            embedVar = discord.Embed(title='''"{}"'''.format(pinMessageContent), description = "- {}".format(pinMessageAuthor), color=discord.Color.blue())
            embedVar.add_field(name="Message link", value="[Click here]({})".format(pinMessageLink), inline=False)
            await channel.send(embed=embedVar)
            await message.delete()

@client.event
async def on_error(event, *args, **kwargs):
    with open(os.path.join(currentpath, 'err.log'), 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

async def background_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        currentTime = datetime.datetime.now()
        time = currentTime.strftime("%d:%m:%Y:%H:%M:%S")
        for reminder in reminders:
            try:
                if time == reminder[1].strftime("%d:%m:%Y:%H:%M:%S"):
                    channel = client.get_channel(reminder[2])
                    embedVar = discord.Embed(title="Reminder", color=discord.Color.blue())
                    embedVar.add_field(name="Time", value=reminder[1].strftime("%d/%m/%Y, %H:%M"), inline=False)
                    embedVar.add_field(name="Reason", value=reminder[4])
                    await channel.send("<@"+str(reminder[0]) + ">")
                    await channel.send(embed=embedVar)
                    #msg = await channel.send("<@"+str(reminder[0]) + "> You had a reminder set for " + reminder[1].strftime("%d/%m/%Y, %H:%M") + ", reason: " + reminder[4])
                    #message_cache.append(msg)
            except: 
                pass
        await asyncio.sleep(1)

client.loop.create_task(background_loop())
client.run(TOKEN)