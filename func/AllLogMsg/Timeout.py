import sqlite3
import discord
from datetime import datetime, timedelta, timezone 

async def timeout(bofore,after):

    timeoutReason = "None"
    async for entry in after.guild.audit_logs(limit=5):
        if entry.target.id == after.id:
            timeoutReason = entry.reason
            break


    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT ChannelId FROM LogChannels WHERE GuildId=? AND LogEvent = ?",(after.guild.id,"User_Timeout"))
    allLogChannelIdList = cur.fetchall()
    
    if allLogChannelIdList == None:
        con.close()
        return
    
    for logChannelId in allLogChannelIdList:
        logChannel = await after.guild.fetch_channel(logChannelId[0])

        if logChannel == None:
            continue
    
        embed_log = discord.Embed(title=str(bofore.display_name) + " timeout",  colour=15082281,timestamp= datetime.utcnow())  ## Der Titel description="Beigetreten"
        embed_log.set_thumbnail(url=after.avatar)  ## Das Bild

        embed_log.add_field(name="Timeout length:  ", value= format_time(after.timed_out_until))
        embed_log.add_field(name="Reason:", value= timeoutReason)
            
        embed_log.set_footer(text="id: " + str(after.id))  ## User ID und Datum

        ChannelToSend = await after.guild.fetch_channel(logChannelId[0])
        await ChannelToSend.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.

    con.close() 



def format_time(dt):
    # Berechne die Differenz zwischen dem gegebenen Zeitpunkt und dem aktuellen Zeitpunkt
    time_difference = dt - datetime.now(timezone.utc)
    
    #There is prob a better way but who cares?
    if time_difference.seconds > 0 and time_difference.seconds <= 60:
        return "60 secs"
    elif time_difference.seconds > 60 and time_difference.seconds <= 300:
        return "5 mins"
    elif time_difference.seconds > 300 and time_difference.seconds <= 600:
        return "10 mins"
    elif time_difference.seconds > 600 and time_difference.seconds <= 3600:
        return "1 hour"
    elif time_difference.days > 1 and time_difference.days <= 7:
        return "1 Week"
    elif time_difference.seconds > 3600 and time_difference.seconds <= 86400:
        return "1 day"
    else:
        return "None"
    

async def timeoutEnd(bofore,after):
   
    ##Timeout grund
    timeoutEndUser = "None"
    async for entry in after.guild.audit_logs(limit=5):
        if entry.target.id == after.id:
            timeoutEndUser = entry.user
            break
        

    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT ChannelId FROM LogChannels WHERE GuildId=? AND LogEvent = ?",(after.guild.id,"User_Timeout"))
    allLogChannelIdList = cur.fetchall()


    if allLogChannelIdList == None: 
        con.close()
        return
    
    for logChannelId in allLogChannelIdList:
        logChannel = await after.guild.fetch_channel(logChannelId[0])

        if logChannel == None:
            continue
        
        embed_log = discord.Embed(title=str(bofore.display_name) + " timeout removed",  colour=1955439,timestamp= datetime.utcnow())  ## Der Titel description="Beigetreten"
        embed_log.set_thumbnail(url=after.avatar)  ## Das Bild

        print(timeoutEndUser)
        if timeoutEndUser != None:
            embed_log.add_field(name="Timeout canceled by:",value=timeoutEndUser)
        else:
            embed_log.add_field(name="Timeout canceled by:",value="None")

        embed_log.set_footer(text="id: " + str(after.id))  ## User ID und Datum

        ChannelToSend = await after.guild.fetch_channel(logChannelId[0])
        await ChannelToSend.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.
    
        con.close()
   