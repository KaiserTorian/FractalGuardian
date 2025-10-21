import math
import datetime

import sqlite3


async def TimestampToTextForLogs(timestamp: datetime.datetime):
    timestampnow = datetime.datetime.now(datetime.timezone.utc)
    timestampDelta = int((timestampnow - timestamp).total_seconds())

    tag = 0
    monat = 0
    jahr = 0
    stunde = 0
    minute = 0
    sekunde = 0


    #jahr
    if timestampDelta / 31536000  > 0:
        jahr = math.trunc(timestampDelta / 31536000)
        timestampDelta = timestampDelta - 31536000 * jahr

    #monat
    if timestampDelta / 2592000 > 0:
        monat = math.trunc(timestampDelta / 2592000)
        timestampDelta = timestampDelta - 2592000 * monat

    #tage
    if timestampDelta / 86400 > 0:
        tag = math.trunc(timestampDelta / 86400)
        timestampDelta = timestampDelta - 86400 * tag

    #stunden
    if timestampDelta / 3600 > 0:
        stunde = math.trunc(timestampDelta / 3600)
        timestampDelta = timestampDelta - 3600 * stunde

    #minuten
    if math.trunc(timestampDelta / 60) > 0:
        minute = math.trunc(timestampDelta / 60)
        timestampDelta = timestampDelta - 60 * minute

    #sekunden
    if timestampDelta > 0:
        sekunde = round(timestampDelta)
        timestampDelta = timestampDelta - sekunde


    timeList = (jahr, monat, tag, stunde, minute, sekunde)


    #-------------------TEXT-----------------------#
 
    timedate = ""

    ##Jahr, Monat, Tag
    if timeList[0] > 0:
        if timeList[0] == 1:
            timedate = timedate + str(timeList[0]) + " year, "
        else:
            timedate = timedate + str(timeList[0]) + " years, "

    if timeList[1] > 0:
        if timeList[1] == 1:
            timedate = timedate + str(timeList[1]) + " month, "
        else:
            timedate = timedate + str(timeList[1]) + " months, "

    if timeList[2] > 0:
        if timeList[2] == 1:
            timedate = timedate + str(timeList[2]) + " day "
        else:
            timedate = timedate + str(timeList[2]) + " days "



    ## Wenn Jahr, Monat, Tag = 0 dann zeigt er Stunden + Minuten an
    if timeList[0] == 0 and timeList[1] == 0 and timeList[2] == 0:

        if timeList[3] > 0:
            if timeList[3] == 1:
                timedate = timedate + str(timeList[3]) + " hour, "
            else:
                timedate = timedate + str(timeList[3]) + " hours, "

            if timeList[4] > 0:
                    if timeList[4] == 1:
                        timedate = timedate + str(timeList[4]) + " minute, "
                    else:
                        timedate = timedate + str(timeList[4]) + " minutes, "


        ## Wenn die Stunden 0 sind dann zeigt er Minuten und sekunden an
        elif timeList[3] == 0:
            if timeList[4] > 0:
                if timeList[4] == 1:
                    timedate = timedate + str(timeList[4]) + " minute, "
                else:
                    timedate = timedate + str(timeList[4]) + " minutes, "

            if timeList[5] > 0:
                if timeList[5] == 1:
                        timedate = timedate + str(timeList[5]) + " second "
                else:
                        timedate = timedate + str(timeList[5]) + " seconds "

    if timedate == "":
        timedate = "--"

    return timedate


## Gibt einen vollstendigen text aus, welcher invite link genutzt wurde. Er verlässt sich auf invite_used() (also ist es nur gut wenn wer den server joint).
async def inviteToText(invite,guild):
        
    if invite == None or guild == None :
        return "No Link found"  ## Wenn eines von beiden None ist

    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #Full Invite Link
    cur.execute("SELECT InviteId, InviteName, InviterId, InviterName FROM InviteLinks WHERE GuildId=? and InviteId=? ",(guild.id,invite[0]))
    inviteLink = cur.fetchone()

    if inviteLink == None:
        cur.execute("SELECT InviteId, InviteName, InviterId, InviterName FROM InviteLinksArchive WHERE GuildId=? and InviteId=?",(guild.id,invite[0]))
        inviteLink = cur.fetchone()
    
    if inviteLink == None:
        return "No Link found"  ## Wenn ein Fehler aufgetreten ist.

    if inviteLink[1] != None:  ## Wenn der invite link mit namen gespeichert ist.

        return "Invite Name: **" + str(inviteLink[1]) + "**\nInviter: " + inviteLink[3]   ## Gibt eine vollwertige Antwort zurück, die man gleich verwenden kann.

    else:  ## Wenn der invite link ohne namen gespeichert ist.

        return "Invite Name: --\nLink Code: " + str(inviteLink[0]) + "\nInviter: " + inviteLink[3]   ## Gibt eine vollwertige Antwort zurück, die man gleich verwenden kann.



async def deleteLogSettingOnChannelRemove(channel):

    guild = channel.guild

    con = sqlite3.connect("fractalData.db")
    cur = con.cursor

    cur.execute("DELETE from UserActivity WHERE ChannelId = ? and GuildId = ?",(channel.id,guild.id))
    con.commit()

    con.close()
    return
