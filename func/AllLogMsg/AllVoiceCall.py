import sqlite3
import discord
from datetime import datetime, timedelta, timezone 



async def VoiceChannelJoin(member,before,after):
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT ChannelId FROM LogChannels WHERE GuildId=? AND LogEvent = ?",(member.guild.id,"Voice_Channel_Update"))
    allLogChannelIdList = cur.fetchall()
    
    if allLogChannelIdList == None:
        con.close()
        return
    
    for logChannelId in allLogChannelIdList:
        logChannel = await member.guild.fetch_channel(logChannelId[0])

        if logChannel == None:
            continue
    
        embed_log = discord.Embed(title=member.display_name + "\njoined voice chat",  colour=1955439,timestamp=datetime.utcnow())  ## Der Titel description="Beigetreten"
        embed_log.set_thumbnail(url=member.avatar)  ## Das Bild

        embed_log.add_field(name="Joined:", value="**"+after.channel.name+"**")
            
        embed_log.set_footer(text="id: " + str(member.id))  ## User ID und Datum

        #sende embed in channel
        await logChannel.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.

    con.close()
    




async def VoiceChannelChange(member,before,after):
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT ChannelId FROM LogChannels WHERE GuildId=? AND LogEvent = ?",(member.guild.id,"Voice_Channel_Update"))
    allLogChannelIdList = cur.fetchall()
    
    if allLogChannelIdList == None:
        con.close()
        return
    
    for logChannelId in allLogChannelIdList:
        logChannel = await member.guild.fetch_channel(logChannelId[0])

        if logChannel == None:
            continue

        embed_log = discord.Embed(title=member.display_name + "\nchanged voice chat",  colour=12281600,timestamp=datetime.utcnow())  ## Der Titel description="Beigetreten"
        embed_log.set_thumbnail(url=member.avatar)  ## Das Bild

        embed_log.add_field(name="Changed:", value= "form: **" + before.channel.name +"** to: **"+after.channel.name+"**")
            
        embed_log.set_footer(text="id: " + str(member.id))  ## User ID und Datum

        #sende embed in channel
        await logChannel.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.

    con.close()




async def VoiceChannelLeave(member,before,after):
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT ChannelId FROM LogChannels WHERE GuildId=? AND LogEvent = ?",(member.guild.id,"Voice_Channel_Update"))
    allLogChannelIdList = cur.fetchall()
    
    if allLogChannelIdList == None:
        con.close()
        return
    
    for logChannelId in allLogChannelIdList:
        logChannel = await member.guild.fetch_channel(logChannelId[0])

        if logChannel == None:
            continue

        embed_log = discord.Embed(title=member.display_name + "\nleft voice chat",  colour=15082281,timestamp=datetime.utcnow())  ## Der Titel description="Beigetreten"
        embed_log.set_thumbnail(url=member.avatar)  ## Das Bild

        embed_log.add_field(name="Left:", value="**"+before.channel.name+"**")
            
        embed_log.set_footer(text="id: " + str(member.id))  ## User ID und Datum

        #sende embed in channel
        await logChannel.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.

    con.close()
    