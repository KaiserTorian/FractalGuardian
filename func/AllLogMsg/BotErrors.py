import sqlite3
import discord
from datetime import datetime, timedelta

async def BotErrorLog(guild,errorMessage):
   
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT ChannelId FROM LogChannels WHERE GuildId=? AND LogEvent = ?",(guild.id,"Bot_Errors"))
    allLogChannelIdList = cur.fetchall()
    
    if allLogChannelIdList == None:
        con.close()
        return
    
    for logChannelId in allLogChannelIdList:
        logChannel = await guild.fetch_channel(logChannelId[0])

        if logChannel == None:
            continue
    
        embed_log = discord.Embed(title="",  colour=15082281)  ## Der Titel description="Beigetreten"

        embed_log.set_author(name="Bot encountered an error",icon_url=guild.icon)

        embed_log.add_field(name="Error:", value=errorMessage)

        embed_log.set_footer(text="id: " + str(guild.id) +" |-| " + str(datetime.now().date()))  
        
        ChannelToSend = guild.get_channel(logChannelId[0])
        await ChannelToSend.send(embed=embed_log)  

    con.close()
    
