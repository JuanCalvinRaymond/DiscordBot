import datetime
import asyncio
import json
import calendar
import logging
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(filename=f"{dir_path}/../discord_bot.log", filemode="w",
                    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
try:
  with open(f"{dir_path}/../raidtime.json", "r") as f:
    raiding_time = json.load(f);
except (ValueError, FileNotFoundError) as e:
  raiding_time = {calendar.SATURDAY.name: datetime.time(16, 45), calendar.SUNDAY.name: datetime.time(17, 45)}
  logging.error("raidingtime.json can't be open")
def _json_serial(obj):
  """Custom json serialization for datetime object.

  Args:
    obj: JSON value
  """
  if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
    return obj.isoformat()
  raise TypeError(f"Type {type(obj)} not serializable")

async def execute_task(channel: int):
  """Every minute check if time is raiding time and ping role accordingly.

  Args:
    channel: Message channel to send message to
    role: Specific role to tag if provided.
  """
  last_ping = None
  while True:
    now_utc = datetime.datetime.now()
    try:
      saturday_time = now_utc.weekday() == calendar.SATURDAY.value and now_utc.hour == datetime.time.fromisoformat(raiding_time[calendar.SATURDAY.name]).hour and now_utc.minute == datetime.time.fromisoformat(raiding_time[calendar.SATURDAY.name]).minute
      sunday_time = now_utc.weekday() == calendar.SUNDAY.value and now_utc.hour == datetime.time.fromisoformat(raiding_time[calendar.SUNDAY.name]).hour and now_utc.minute == datetime.time.fromisoformat(raiding_time[calendar.SUNDAY.name]).minute
      logging.info(f"current time: {now_utc.hour}:{now_utc.minute} saturday: {datetime.time.fromisoformat(raiding_time[calendar.SATURDAY.name]).hour} {datetime.time.fromisoformat(raiding_time[calendar.SATURDAY.name]).minute} {saturday_time}")
      if saturday_time or sunday_time:
        try:
          with open(f"{dir_path}/../DiscordId.json", "r") as file:
            ids = json.load(file)
            ping_delta = datetime.datetime.now() - last_ping
            if (last_ping is None or (ping_delta > datetime.timedelta(hours=1))):
              await channel.send(f'<@&{ids["role_to_ping"]}> Let\'s start hopping in VC. PF is up, pw is in pinned message. We are on {ids["data_center"]}')
              last_ping = datetime.datetime.now()
              logging.info(f"Discord pinged at:  {last_ping}")
          logging.debug(f"Trying to ping: {ping_delta}")
        except (ValueError, FileNotFoundError) as e:
          await channel.send(f'Let\'s start hopping in VC. PF is up, pw is in pinned message. We are on Aether. Role is broken btw')
    except KeyError as e:
      print(f"Key error: {e}")
    await asyncio.sleep(60)

async def test(channel: int):
  last_ping = None
  while True:
    now_utc = datetime.datetime.now()
    try:
      saturday_time = now_utc.hour == datetime.time.fromisoformat(raiding_time[calendar.SATURDAY.name]).hour and now_utc.minute == datetime.time.fromisoformat(raiding_time[calendar.SATURDAY.name]).minute
      sunday_time = now_utc.hour == datetime.time.fromisoformat(raiding_time[calendar.SUNDAY.name]).hour and now_utc.minute == datetime.time.fromisoformat(raiding_time[calendar.SUNDAY.name]).minute
      logging.info(f"current time: {now_utc.hour}:{now_utc.minute} {datetime.time.fromisoformat(raiding_time[calendar.SATURDAY.name]).hour} {datetime.time.fromisoformat(raiding_time[calendar.SATURDAY.name]).minute} {saturday_time}")
      if saturday_time or sunday_time:
        try:
          with open(f"{dir_path}/../DiscordId.json", "r") as file:
            ids = json.load(file)
            if (last_ping is None or ((datetime.datetime.now() - last_ping) > datetime.timedelta(hours=1))):
              await channel.send(f'<@&{ids["role_to_ping"]}> Let\'s start hopping in VC. PF is up, pw is in pinned message. We are on {ids["data_center"]}')
              last_ping = datetime.datetime.now()
              logging.info(f"Discord pinged at:  {last_ping}")
          logging.debug(f"Trying to ping: {datetime.datetime.now() - last_ping}")
        except (ValueError, FileNotFoundError) as e:
          await channel.send(f'Let\'s start hopping in VC. PF is up, pw is in pinned message. We are on Aether. Role is broken btw')
    except KeyError as e:
      print(f"Key error: {e}")
    await asyncio.sleep(60)

async def change_time(day: str, time: str):
  """Change raiding time and save it to a json file for persistency.

  Args:
    day: Using calendar.Day enum
    time: ISO 8601 compliant formating
  """
  assert day != "" and time != ""
  try:
    time_object = datetime.time.fromisoformat(time)
    datetime_object = datetime.datetime.combine(datetime.date.today(), time_object)
    raiding_time[day] = (datetime_object - datetime.timedelta(minutes=15)).time()
    with open(f"{dir_path}/../raidtime.json", "w") as file:
      json.dump(raiding_time, file, default=_json_serial, indent=4)
  except ValueError:
    logging.exception("Please enter a valid date/time format!. ex. 17, 17:30")
  except FileNotFoundError:
    logging.exception("File does not exist")
