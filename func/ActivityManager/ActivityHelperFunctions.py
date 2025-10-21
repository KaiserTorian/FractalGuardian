from datetime import datetime, timedelta
import sqlite3



async def utc_timestamp_beginning_of_hour(hourOffset = 0):
    # Aktuellen UTC-Zeitstempel erhalten
    current_utc_timestamp = datetime.utcnow()

    # Beginn der aktuellen Stunde berechnen
    beginning_of_hour = current_utc_timestamp.replace(minute=0, second=0, microsecond=0) + timedelta(hours=hourOffset)

    # UTC-Zeitstempel für den Beginn der Stunde zurückgeben
    return int(beginning_of_hour.timestamp())




async def deleteUserActivityOnRemove(member):
    guild = member.guild

    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    cur.execute("DELETE from UserActivity WHERE UserId = ? and GuildId = ?",(member.id,guild.id))
    con.commit()

    con.close()

    return