from datetime import datetime
import sqlite3


# Die globale Liste die alle User beinhaltet die gerade in einem voice chat sind.
All_Active_Voice_Channels = []


# Onjoin speichert nur die person in die globale liste
async def OnUserJoinVoice(after):
    global All_Active_Voice_Channels
    All_Active_Voice_Channels.append({"channel" : after.channel, "timeStamp" :  int(datetime.utcnow().timestamp())})
    return




# Löscht den alten Listen eintrag und speichert einen neuen, wenn die zeit von der letzten listen änderung unter 1 minute war dann macht er nichts sonst führt er UserVoiceActivity aus
async def OnUserChangeVoice(before,after):

    global All_Active_Voice_Channels
    
    found_Before_Channel = None
    found_After_Channel = None
    for active_Voice_Channel in All_Active_Voice_Channels:
        print(active_Voice_Channel["channel"].id)

        print(active_Voice_Channel["channel"].id == before.channel.id)
        if active_Voice_Channel["channel"].id == before.channel.id:
            found_Before_Channel = active_Voice_Channel

        if active_Voice_Channel["channel"].id == after.channel.id:
            found_After_Channel = active_Voice_Channel



    if len(before.channel.members) == 0:

        if int(datetime.utcnow().timestamp()) - found_Before_Channel["timeStamp"] > 60:
            await VoiceChannelActivity(found_Before_Channel["timeStamp"], datetime.utcnow().timestamp(), before.channel)

        All_Active_Voice_Channels.remove(found_Before_Channel)

    if found_After_Channel == None:
        All_Active_Voice_Channels.append({"channel" : after.channel, "timeStamp" :  int(datetime.utcnow().timestamp())})
    return



# Löscht den alten Listen eintrag, wenn die zeit von der letzten listen änderung unter 1 minute war dann macht er nichts sonst führt er UserVoiceActivity aus
async def OnUserLeaveVoice(before):

    global All_Active_Voice_Channels
    
    found_Before_Channel = None
    for active_Voice_Channel in All_Active_Voice_Channels:
        if active_Voice_Channel["channel"].id == before.channel.id:
            found_Before_Channel = active_Voice_Channel

    if len(before.channel.members) == 0:

        if int(datetime.utcnow().timestamp()) - found_Before_Channel["timeStamp"] > 60:
            await VoiceChannelActivity(found_Before_Channel["timeStamp"], int(datetime.utcnow().timestamp()), before.channel)

        All_Active_Voice_Channels.remove(found_Before_Channel)
    return



# Geht alle guilds durch und speichert alle user in einem Voice channel
async def UpdateVoiceListOnStartup(bot):

    global All_Active_Voice_Channels

    for guild in bot.guilds:
        needetVoiceChannels = guild.voice_channels
        needetStageChannels = guild.stage_channels
        allNeedetChannels = needetVoiceChannels + needetStageChannels

        for channel in allNeedetChannels:
            if len(channel.members) == 0:
                continue

            All_Active_Voice_Channels.append({"channel" : channel, "timeStamp" :  int(datetime.utcnow().timestamp())})
    
    return


async def VoiceChannelActivity(start, end, channel):
    guild = channel.guild

    with sqlite3.connect("fractalData.db") as con:
        cur = con.cursor()

        cur.execute("INSERT INTO ChannelActivityMinutes VALUES(?, ?, ?, ?)",(guild.id, channel.id, start, end))

        con.commit()
    return



async def printList():
    global All_Active_Voice_Channels
    for eintrag in All_Active_Voice_Channels:
        print(str(eintrag["channel"]))