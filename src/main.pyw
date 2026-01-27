#!/usr/bin/env pythonw
import discord
import re
from datetime import datetime, timedelta
from discord.ext import commands
from discord import app_commands
from discord_timestamp_converter import *
from raid_notif import *
import json
import os
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(filename=f'{dir_path}/../discord_bot.log', filemode="w",
                    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
try:
    logging.info(f'trying to open {dir_path}/../DiscordId.json');
    with open(f"{dir_path}/../DiscordId.json", "r") as f:
        discord_ids = json.load(f)
except (ValueError, FileNotFoundError) as e:
    print(f'Error: {e}')
    logging.exception("DiscordId.json can't be open")

GUILD_ID = [discord_ids["oreo_id"], discord_ids["dev_id"]]

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        channel = self.get_channel(discord_ids["oreo_general"])
        # dev_channel = self.get_channel(discord_ids["dev_general"])
        asyncio.create_task(execute_task(channel))
        # asyncio.create_task(test(dev_channel))
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

        # if "test" in message.content:
        #    test()

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
async def convert_timeline(interaction: discord.Interaction, time: str, utc: int, format: app_commands.Choice[str]):
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
async def change_raid_time(interaction: discord.Interaction, day: app_commands.Choice[str], time: str):
    if interaction.user == client and interaction.user.name != "fanazador":
      await interaction.response.send_message(f'Only Fanazador can use this command', ephemeral=True)
      return
    try:
      await change_time(day.value, time)
    except Exception as e:
      await interaction.response.send_message(f'{e}')
      return
    await interaction.response.send_message(f'Changed raid time {str.capitalize(day.value)} to {raiding_time[day.value]}', ephemeral=True)

@client.tree.command(name="raidrole", description="Change raiding time", guilds=[discord.Object(id=guild_id) for guild_id in GUILD_ID])
@app_commands.describe(role="Static/Ultimate")
@app_commands.choices(role=[
        app_commands.Choice(name="Static", value="1089759665853825046"),
        app_commands.Choice(name="Ultimate", value="1299176112227876954"),
        ])
async def change_role(interaction: discord.Interaction, role: app_commands.Choice[str]):
  try:
    discord_ids["role_to_ping"] = int(role.value)
    with open(f"{dir_path}/../DiscordId.json", "w") as file:
      json.dump(discord_ids, file, indent=4)
  except FileNotFoundError as e:
    await interaction.response.send_message(f'{e}', ephemeral=True)
  await interaction.response.send_message(f'Changed raid role to {role.name}', ephemeral=True)

@client.tree.command(name="raiddatacenter", description="Change raiding datacenter", guilds=[discord.Object(id=guild_id) for guild_id in GUILD_ID])
@app_commands.describe(datacenter="Which datacenter the pf will be posted")
@app_commands.choices(datacenter=[
        app_commands.Choice(name="Aether", value="Aether"),
        app_commands.Choice(name="Primal", value="Primal"),
        app_commands.Choice(name="Crystal", value="Crystal"),
        app_commands.Choice(name="Dynamis", value="Dynamis"),
        ])
async def change_role(interaction: discord.Interaction, datacenter: app_commands.Choice[str]):
  try:
    discord_ids["data_center"] = datacenter.value
    with open(f"{dir_path}/../DiscordId.json", "w") as file:
      json.dump(discord_ids, file, indent=4)
  except FileNotFoundError as e:
    await interaction.response.send_message(f'{e}', ephemeral=True)
  await interaction.response.send_message(f'Changed raid role to {datacenter.name}', ephemeral=True)
client.run(os.getenv('DISCORD_TOKEN'))
