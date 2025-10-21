import discord
import sqlite3 
from datetime import datetime, timedelta, timezone 


async def BanLogMessage(guild: discord.Guild, member: discord.Member):
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT ChannelId FROM LogChannels WHERE GuildId=? AND LogEvent = ?",(guild.id,"User_Ban"))
    allLogChannelIdList = cur.fetchall()
    
    if allLogChannelIdList == None:
        con.close()
        return
    
    for logChannelId in allLogChannelIdList:
        logChannel = await guild.fetch_channel(logChannelId[0])

        if logChannel == None:
            continue

        banReason = "None"
        banInitiator = "None"
        async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.ban):
            if entry.target.id == member.id:
                banReason = entry.reason
                banInitiator = entry.user
                break
        
        embed_log = discord.Embed(title="", colour=15082281, timestamp= datetime.utcnow())  ## Der Titel description="Beigetreten"
        embed_log.set_author(name=member.display_name + " Ban",icon_url=member.avatar)


        if banReason != None:
            embed_log.add_field(name="Reason:", value=banReason)
        else :
            embed_log.add_field(name="Reason:", value="No reason was addet.")

        embed_log.add_field(name="Initiator:", value=banInitiator)
            
        embed_log.set_footer(text="id: " + str(member.id))  ## User ID und Datum

        #sende embed in channel
        await logChannel.send(embed=embed_log)  # type: ignore ## Sendet den Embed in den Channel der Eingestellt ist.

    con.close()


async def UnbanLogMessage(guild: discord.Guild, member: discord.Member):
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT ChannelId FROM LogChannels WHERE GuildId=? AND LogEvent = ?",(guild.id,"User_Unban"))
    allLogChannelIdList = cur.fetchall()
    
    if allLogChannelIdList == None:
        con.close()
        return
    
    for logChannelId in allLogChannelIdList:
        logChannel = await guild.fetch_channel(logChannelId[0])

        if logChannel == None:
            continue

        banReason = "None"
        banInitiator = "None"
        async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.unban):
            if entry.target.id == member.id:
                banReason = entry.reason
                banInitiator = entry.user
                break
        
        embed_log = discord.Embed(title="",  colour=1955439,timestamp= datetime.utcnow())  ## Der Titel description="Beigetreten"
        embed_log.set_author(name=member.display_name  + " Unban",icon_url=member.avatar)
        embed_log.add_field(name="Initiator:", value=banInitiator)
            
        embed_log.set_footer(text="id: " + str(member.id))  ## User ID und Datum

        #sende embed in channel
        await logChannel.send(embed=embed_log)  # type: ignore ## Sendet den Embed in den Channel der Eingestellt ist.

    con.close()

