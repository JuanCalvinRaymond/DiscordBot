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
  """
  Custom json serialization for datetime object.

  :param obj: json value
  """
  if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
    return obj.isoformat()
  raise TypeError(f"Type {type(obj)} not serializable")

async def ExecuteTask(channel: int, role: int):
  """
  Every minute check if time is raiding time and ping role accordingly.

  :param channel: int message channel to send message to
  :param role: int tagging specific role
  """
  while True:
    try:
      now_utc = datetime.datetime.now()
      SaturdayTime = now_utc.weekday() == calendar.SATURDAY.value and now_utc.hour == raiding_time[calendar.SATURDAY.name].hour and now_utc.minute == raiding_time[calendar.SATURDAY.name].minute
      SundayTime = now_utc.weekday() == calendar.SUNDAY.value and now_utc.hour == raiding_time[calendar.SUNDAY.name].hour and now_utc.minute == raiding_time[calendar.SUNDAY.name].minute
      if SaturdayTime or SundayTime:
        await channel.send(f'<@&{role}> Let\'s start hopping in VC. PF is up, pw is in pinned message. We are on Aether')
      await asyncio.sleep(60)
    except KeyError as e:
      print(f"Key error: {e}")

async def ChangeTime(day: str, time: str):
  """
  Change raiding time and save it to a json file for persistency.

  :param day: str using calendar Day enum
  :param time: str ISO 8601 compliant formating
  """
  try:
    timeObject = datetime.time.fromisoformat(time)
    datetimeObject = datetime.datetime.combine(datetime.date.today(), timeObject)
    raiding_time[day] = (datetimeObject - datetime.timedelta(minutes=15)).time()
    with open("raidtime.json", "w") as f:
      json.dump(raiding_time, f, default=_json_serial, indent=4)
  except ValueError:
    print("Please enter a valid date/time format!. ex. 17, 17:30")
  except FileNotFoundError:
    print("File does not exist")
