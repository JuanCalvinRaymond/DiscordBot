import discord
import re
from datetime import datetime, timedelta
import time
from discord.ext import commands
from discord import app_commands
from utcToTimestampConverter import *
import os

estTimeZone = (4 if time.daylight else 5)
GUILD_ID = [discord.Object(id=349618628854808576), discord.Object(id=1252654002185961482)]

def timezoneConverter(originalTime, utc = 0, format="t"):
    now_utc = datetime.now()

    clock = re.findall(r'\d+', originalTime)
    hour = int(clock[0])
    minute = int(clock[1] if len(clock) > 1 else 0)
    second = int(clock[2] if len(clock) > 2 else 0)

    timezone = re.search(r'[\+\-]\d', originalTime)
    tz = timezone.group() if timezone else 0
    tz = utc if utc != 0 else tz
    tzdiff = estTimeZone + int(tz)
    if "pm" in originalTime or hour > 12:
        # add 12 hour so 4 become 16, if condition is met
        # date = datetime(now_utc.year, now_utc.month, now_utc.day, int(clock[0]) + (0 if int(clock[0]) > 12 and int(clock[0]) != 0 else 12), minute, second)
        date = datetime(now_utc.year, now_utc.month, now_utc.day, hour + (0 if hour > 12 and hour != 0 else 12), minute, second) - timedelta(hours=tzdiff)
        
    # does it matter? if people don't specify am or pm, we just assume it's am
    # if "am" in time:
    else:
        # date = datetime(now_utc.year, now_utc.month, now_utc.day, int(clock[0]), minute, second)
        date = datetime(now_utc.year, now_utc.month, now_utc.day, hour, minute, second) - timedelta(hours=tzdiff)
    timestamp = timestampConverter(date)
    if "full" in originalTime:
        return f'<t:{timestamp}:f>'
    elif format != "":
        return f'<t:{timestamp}:{format}>'
    else:
        return f'<t:{timestamp}:t>'

# we are going at ts(hello) to ts(bye)
class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        try:
            synced = await self.tree.sync()
            if synced:
                print(f'Bot is synced') 
        except Exception as e:
            print(f'Error syncing commands: {e}')

    async def on_message(self, message):
        if "ts(" in message.content: 
            text = message.content
            replacingText = re.findall(r"ts\(\d+:?\d*:?\d*\s?[aApP]?[mM]?\s?[\+\-]?\d?\s?\w*\)", text)
            replaceDict = {}

            # supported format:
            # hh:mm am/pm
            # hh am/pm
            # hh
            # hh:mm
            # hh.mm am/pm
            # hh.mm
            for ts in replacingText:
                try:
                    replaceDict[ts] = timezoneConverter(ts)
                except Exception as e:
                    await message.channel.send(f'{e}')
                    return
            pattern = re.compile("|".join(map(re.escape, replaceDict.keys())))
            newText = pattern.sub(lambda m: replaceDict[m.group()], text)
            await message.channel.send(newText)

    # async def on_message_edit(before, after):
    # async def on_message_delete(self, message):
    # async def on_member_join(member):
    # async def on_member_remove(member):
    # async def on_member_update(before, after):
    # async def on_guild_join(guild):
    # async def on_guild_remove(guild):
    # async def on_reaction_add(reaction, user):
    # async def on_reaction_remove(reaction, user):
    # async def on_raw_message_delete(payload):
    # async def on_command_error(ctx, error):
        
intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix="!", intents=intents)
@client.tree.command(name="timestamp", description="Convert time into timestamp")
@app_commands.describe(time="Time you want to convert. Example format: 12, 12:30",
                       utc="Enter YOUR local utc timezone value (interger). Example: -4 (This is EST)",
                       format="Timestamp format you want to display")
@app_commands.choices(format=[
        app_commands.Choice(name="Short Time <t>", value="t"),
        app_commands.Choice(name="Long Time <T>", value="T"),
        app_commands.Choice(name="Short Date <d>", value="d"),
        app_commands.Choice(name="Long Date <D>", value="D"),
        app_commands.Choice(name="Short Date/Time <f>", value="f"),
        app_commands.Choice(name="Long Date/Time <F>", value="F"),
        app_commands.Choice(name="Relative Time <R>", value="R"),
        ])
async def convertTimeline(interaction: discord.Interaction, time: str, utc: int, format: app_commands.Choice[str]):
    try:
        timeString = timezoneConverter(time, utc, format.value)
    except Exception as e:
        await interaction.response.send_message(f'{e}')
        return
    await interaction.response.send_message(f'Time is: {timeString}')

client.run(os.getenv('DISCORD_TOKEN'))