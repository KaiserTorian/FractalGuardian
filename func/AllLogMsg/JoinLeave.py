import sqlite3
import discord
from datetime import datetime, timedelta, timezone 
from func.AllLogMsg import _LogHelper

#TODO: Um erlich zu sein habe ich keine ahnung was ich da genau programiert habe weil das ist noch vom alten bot (ich bin erstaut, dass das noch geht)
#   vielleicht wenn ich lust habe kann man das überarbeiten

async def JoinLogMessage(member):
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT ChannelId FROM LogChannels WHERE GuildId=? AND LogEvent = ?",(member.guild.id,"User_Join"))
    allLogChannelIdList = cur.fetchall()
    
    if allLogChannelIdList == None:
        con.close()
        return
    
    for logChannelId in allLogChannelIdList:
        logChannel = await member.guild.fetch_channel(logChannelId[0])

        if logChannel == None:
            continue
        
        #Invite Link id
        cur.execute("SELECT InviteLinkUsed FROM UserData WHERE GuildId=? and UserId=?",(member.guild.id,member.id,))
        inviteLinkId = cur.fetchone()

        #TimeDelta als nutzbaren text
        createdText = await _LogHelper.TimestampToTextForLogs(member.created_at)
        timeCreated = member.created_at
        createdDate = datetime(int(timeCreated.strftime("%Y")),int(timeCreated.strftime("%m")),int(timeCreated.strftime("%d")))
        timestampCreated = datetime.timestamp(timeCreated)

        embed_log = discord.Embed(title="",  colour=1955439,timestamp= datetime.utcnow())  ## Der Titel description="Beigetreten"
        embed_log.set_author(name=member.display_name + " joined",icon_url=member.avatar)

        ##wann er seinen Accound erstellt hat und ob er neu ist
        if timestampCreated >= datetime.now().timestamp() - 259200:  ##Neuer Accound? (3 Tage)
            embed_log.add_field(
                name=":warning:NEW ACCOUND:warning:",
                value= str(createdDate.day) + "." +
                str(createdDate.month) + "." + str(createdDate.year) + " | " + createdText,
                inline=False)
            
        else:
            embed_log.add_field(
                name="Account created: ",
                value= str(createdDate.day) + "." +
                str(createdDate.month) + "." + str(createdDate.year) + " | " + createdText,
                inline=False)


        embed_log.add_field(name="Invitelink used:", value = await _LogHelper.inviteToText(inviteLinkId,member.guild), inline=False)  ##Invite link
        embed_log.set_footer(text="id: " + str(member.id))  ## User ID und Datum
        
        #sende embed in channel
        await logChannel.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.

    con.close()
        


async def LeaveLogMessage(member):
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT ChannelId FROM LogChannels WHERE GuildId=? AND LogEvent = ?",(member.guild.id,"User_Leave"))
    allLogChannelIdList = cur.fetchall()
    
    if allLogChannelIdList == None:
        con.close()
        return
    
    for logChannelId in allLogChannelIdList:
        logChannel = await member.guild.fetch_channel(logChannelId[0])

        if logChannel == None:
            continue
    
        #Invite Link id
        cur.execute("SELECT InviteLinkUsed FROM UserData WHERE GuildId=? and UserId=?",(member.guild.id,member.id,))
        inviteLinkId = cur.fetchone()

        #TimeDelta als nutzbaren text
        joinedText = await _LogHelper.TimestampToTextForLogs(member.joined_at)
        timeJoined = member.joined_at
        joinedDate = datetime(int(timeJoined.strftime("%Y")),int(timeJoined.strftime("%m")),int(timeJoined.strftime("%d")))

        #Die liste von rollen
        userRoles = []
        for i in member.roles:
            if i.name != "@everyone":
                userRoles.append(i.mention)


        embed_log = discord.Embed(title="", colour=15082281,timestamp= datetime.utcnow())
        embed_log.set_author(name=member.display_name + " left",icon_url=member.avatar)

        embed_log.add_field(name="Joined at:",value=str(joinedDate.day) + "." + str(joinedDate.month) + "." + str(joinedDate.year) + " | " + joinedText, inline=False)
        embed_log.add_field(name="Joined using:", value = await _LogHelper.inviteToText(inviteLinkId,member.guild), inline=False)  ##Invite link
        if len(userRoles) > 0:
            embed_log.add_field(name="Roles: ", value=" , ".join(userRoles), inline=False)
        else:
            embed_log.add_field(name="Roles: ", value="No roles.", inline=False)

        embed_log.set_footer(text="id: " + str(member.id))

        #sende embed in channel
        await logChannel.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.

    con.close()
        