# DiscordBot
Parse message and replace frequent used time format into a timestamp.
Add 'TS()' around the time that you want to convert and bot will parse it and return with the message containing timestamp.
Supported format: hh, hh:mm, hh:mm:ss, hh am/pm. hh:mm am/pm, hh:mm:ss am/pm

Argument:
Timezone: Enter you local timezone. Ex. -5 (EST)/ -4(ET). If this is not passed in bot will use EST as default timezone
Format: Add the word 'Full' for a full date/time format.

Example: TS(16:00:00 -5 Full), TS(15), TS(06 PM -5), TS(3 -5 Full)
