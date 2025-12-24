import datetime
import asyncio
import json
import calendar

try:
  with open("raidtime.json", "r") as f:
    raiding_time = json.load(f);
except (ValueError, FileNotFoundError) as e:
  raiding_time = {calendar.SATURDAY.name: datetime.time(16, 45), calendar.SUNDAY.name: datetime.time(17, 45)}

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
  last_ping = 0
  while True:
    now_utc = datetime.datetime.now()
    try:
      saturday_time = now_utc.weekday() == calendar.SATURDAY.value and now_utc.hour == raiding_time[calendar.SATURDAY.name].hour and now_utc.minute == raiding_time[calendar.SATURDAY.name].minute
      sunday_time = now_utc.weekday() == calendar.SUNDAY.value and now_utc.hour == raiding_time[calendar.SUNDAY.name].hour and now_utc.minute == raiding_time[calendar.SUNDAY.name].minute
      if saturday_time or sunday_time:
        try:
          with open("DiscordId.json", "r") as file:
            ids = json.load(file)
          if (last_ping == 0 or ((last_ping - datetime.datetime.now()) > datetime.timedelta(minutes=1))):
            await channel.send(f'<@&{ids["role_to_ping"]}> Let\'s start hopping in VC. PF is up, pw is in pinned message. We are on Aether')
            last_ping = datetime.datetime.now()
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
  try:
    time_object = datetime.time.fromisoformat(time)
    datetime_object = datetime.datetime.combine(datetime.date.today(), time_object)
    raiding_time[day] = (datetime_object - datetime.timedelta(minutes=15)).time()
    with open("raidtime.json", "w") as file:
      json.dump(raiding_time, file, default=_json_serial, indent=4)
  except ValueError:
    print("Please enter a valid date/time format!. ex. 17, 17:30")
  except FileNotFoundError:
    print("File does not exist")
