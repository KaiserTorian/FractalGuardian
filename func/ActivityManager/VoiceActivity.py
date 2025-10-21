from datetime import datetime
from math import floor
import sqlite3
import asyncio
from unittest import skip
from func.ActivityManager import ActivityHelperFunctions as AHT


# Die globale Liste die alle User beinhaltet die gerade in einem voice chat sind.
AllActiveVoiceUsers = []


# Onjoin speichert nur die person in die globale liste
async def OnUserJoinVoice(member,before,after):
    global AllActiveVoiceUsers
    AllActiveVoiceUsers.append({"member" : member, "channel" : after.channel, "timeStamp" :  int(datetime.utcnow().timestamp())})
    return




# Löscht den alten Listen eintrag und speichert einen neuen, wenn die zeit von der letzten listen änderung unter 1 minute war dann macht er nichts sonst führt er UserVoiceActivity aus
async def OnUserChangeVoice(member,before,after):

    global AllActiveVoiceUsers
    
    foundUser = None
    for ActiveVoiceUser in AllActiveVoiceUsers:
        
        if ActiveVoiceUser["member"] == member:
            foundUser = ActiveVoiceUser
            break  # Beende die Schleife, wenn der den richtigen User Eintrag gefunden wurde
    
    if foundUser == None:
        print("ERROR: OnUserChangeVoice in VoiceActivity kein user gefunden.")
        return
    
    if int(datetime.utcnow().timestamp()) - foundUser["timeStamp"] > 60:
        await UserVoiceActivity(member,foundUser["timeStamp"],foundUser["channel"])


    AllActiveVoiceUsers.remove(foundUser)
    AllActiveVoiceUsers.append({"member" : member, "channel" : after.channel, "timeStamp" :  int(datetime.utcnow().timestamp())})
    return



# Löscht den alten Listen eintrag, wenn die zeit von der letzten listen änderung unter 1 minute war dann macht er nichts sonst führt er UserVoiceActivity aus
async def OnUserLeaveVoice(member,before,after):

    global AllActiveVoiceUsers
    
    foundUser = None
    for ActiveVoiceUser in AllActiveVoiceUsers:
        if ActiveVoiceUser["member"] == member:
            foundUser = ActiveVoiceUser
            break  # Beende die Schleife, wenn der Eintrag gefunden wurde
    
    if foundUser == None:
        print("ERROR: OnUserLeaveVoice in VoiceActivity kein user gefunden.")
        return
    
    if  int(datetime.utcnow().timestamp()) - foundUser["timeStamp"] > 60:
        await UserVoiceActivity(member,foundUser["timeStamp"],foundUser["channel"])

    AllActiveVoiceUsers.remove(foundUser)
    return



# Alle stunden speichert er alle voice user in der liste in die SQL Tabelle
async def HourlyVoiceSave(bot):
    global AllActiveVoiceUsers

    while not bot.is_closed():
        
        for eintrag in AllActiveVoiceUsers:
            

            if  int(datetime.utcnow().timestamp()) - eintrag["timeStamp"] > 60:
                await UserVoiceActivity(eintrag["member"],eintrag["timeStamp"],eintrag["channel"])

            eintrag = {"member" : eintrag["member"], "channel" : eintrag["channel"], "timeStamp" :  int(datetime.utcnow().timestamp())}
        await asyncio.sleep(await AHT.utc_timestamp_beginning_of_hour(hourOffset=1) - int(datetime.utcnow().timestamp()))





# Geht alle guilds durch und speichert alle user in einem Voice channel
async def UpdateVoiceListOnStartup(bot):

    global AllActiveVoiceUsers

    for guild in bot.guilds:
        needetVoiceChannels = guild.voice_channels
        needetStageChannels = guild.stage_channels
        allNeedetChannels = needetVoiceChannels + needetStageChannels

        for channel in allNeedetChannels:
            if len(channel.members) == 0:
                continue

            for member in channel.members:
                AllActiveVoiceUsers.append({"member" : member, "channel" : channel, "timeStamp" :  int(datetime.utcnow().timestamp())})
    
    return




# Speichert die Voice activität in der SQL Tabelle.
async def UserVoiceActivity(member,voiceTimeStart,channel):
    
    voiceMinutes =  floor((int(datetime.utcnow().timestamp()) - voiceTimeStart) / 60)
    print(voiceMinutes)
    guild = member.guild

    hourTimestamp = await AHT.utc_timestamp_beginning_of_hour()
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    cur.execute("SELECT Points FROM UserActivity WHERE GuildId=? and UserId=? and HourTimestamp=? and ChannelUsed=? and ActivityType=?",(guild.id, member.id, hourTimestamp,channel.id, 2))
    userVoicePoints = cur.fetchone()


    if userVoicePoints != None:
        cur.execute("UPDATE UserActivity SET Points=? WHERE GuildId=? and UserId=? and HourTimestamp=? and ChannelUsed=? and ActivityType=?",(userVoicePoints[0] + voiceMinutes,guild.id, member.id, hourTimestamp,channel.id, 2))
        
    else:
        cur.execute("INSERT INTO UserActivity VALUES(?, ?, ?, ?, ?, ?)",(guild.id, member.id, hourTimestamp, voiceMinutes,channel.id,2))
       
    con.commit()
    con.close
    return



async def printList():
    global AllActiveVoiceUsers
    for eintrag in AllActiveVoiceUsers:
        print(str(eintrag["member"]))