import discord
import re
from datetime import datetime, timedelta
from discord.ext import commands
from discord import app_commands
from discord_timestamp_converter import *
from raid_notif import *
import json
import os

try:
    with open("DiscordId.json", "r") as f:
        discord_ids = json.load(f)
except (ValueError, FileNotFoundError) as e:
    print(f'Error: {e}')

GUILD_ID = [discord_ids["oreo_id"], discord_ids["dev_id"]]

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        channel = self.get_channel(discord_ids["oreo_general"])
        asyncio.create_task(execute_task(channel, discord_ids["oreo_role_static"]))
        try:
            synced = await self.tree.sync(guild=discord.Object(discord_ids["oreo_id"]))
            synced = await self.tree.sync(guild=discord.Object(discord_ids["dev_id"]))
            if synced:
                print(f'Bot is synced')
        except Exception as e:
            print(f'Error syncing commands: {e}')

    async def on_message(self, message):
        if message.author == client.user:
            return
        # we are going at ts(hello) to ts(bye)
        if "ts(" in message.content:
            text = message.content
            text_to_replace = re.findall(r"ts\(\d+:?\d*:?\d*\s?[aApP]?[mM]?\s?[\+\-]?\d?\s?\w*\)", text)
            text_replace_dict = {}

            # supported format:
            # hh:mm am/pm
            # hh am/pm
            # hh
            # hh:mm
            # hh.mm am/pm
            # hh.mm
            for ts in text_to_replace:
                try:
                    text_replace_dict[ts] = timezone_converter(ts)
                except Exception as e:
                    await message.channel.send(f'{e}')
                    return
            pattern = re.compile("|".join(map(re.escape, text_replace_dict.keys())))
            new_text = pattern.sub(lambda m: text_replace_dict[m.group()], text)
            await message.channel.send(new_text)
            return
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
    if interaction.user == client:
      return
    try:
        timeString = timezone_converter(time, utc, format.value)
    except Exception as e:
        await interaction.response.send_message(f'{e}')
        return
    await interaction.response.send_message(f'Time is: {timeString}', ephemeral=True)

@client.tree.command(name="raidtime", description="Change raiding time", guilds=[discord.Object(id=guild_id) for guild_id in GUILD_ID])
@app_commands.describe(day="Sat/Sun",
                       time="New raiding time using ISO 8601 format. Example format: 17, 17:30")
@app_commands.choices(day=[
        app_commands.Choice(name="Sat", value=calendar.SATURDAY.name),
        app_commands.Choice(name="Sun", value=calendar.SUNDAY.name),
        ])
async def changeRaidTime(interaction: discord.Interaction, day: app_commands.Choice[str], time: str):
    if interaction.user == client and interaction.user.name != "fanazador":
      await interaction.response.send_message(f'Only Fanazador can use this command', ephemeral=True)
      return
    try:
      await change_time(day.value, time)
    except Exception as e:
      await interaction.response.send_message(f'{e}')
      return
    await interaction.response.send_message(f'Changed raid time {str.capitalize(day.value)} to {raiding_time[day.value]}', ephemeral=True)

client.run(os.getenv('DISCORD_TOKEN'))
