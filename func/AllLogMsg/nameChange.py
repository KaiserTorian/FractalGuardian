import sqlite3
import discord
from datetime import datetime, timedelta, timezone 

async def nameChange(before, after):
    try:
        con = sqlite3.connect("fractalG.db")
        cur = con.cursor()
        
        cur.execute("SELECT NameChangeLog FROM LogChannels WHERE GuildId=?",(after.guild.id,))
        logChannelId = cur.fetchone()

        con.close()
        
        embed_log = discord.Embed(title="Name change",  colour=12281600)  ## Der Titel description="Beigetreten"
        embed_log.set_thumbnail(url=after.avatar)  ## Das Bild

        embed_log.add_field(name="Brfore:", value= before.name)
        embed_log.add_field(name="After:", value= after.name)
            
        embed_log.set_footer(text="id: " + str(after.id) + " |-| " +str(datetime.now().date()))  ## User ID und Datum

        ChannelToSend = await after.guild.fetch_channel(logChannelId[0])
        await ChannelToSend.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.
    
        return
    except:
        print("Error")
        return
    



async def display_nameChange(before, after):
    try:
        con = sqlite3.connect("fractalG.db")
        cur = con.cursor()
        
        cur.execute("SELECT NameChangeLog FROM LogChannels WHERE GuildId=?",(after.guild.id,))
        logChannelId = cur.fetchone()

        con.close()
        
        embed_log = discord.Embed(title="Display name change",  colour=12281600)  ## Der Titel description="Beigetreten"
        embed_log.set_thumbnail(url=after.avatar)  ## Das Bild

        embed_log.add_field(name="Brfore:", value= before.name)
        embed_log.add_field(name="After:", value= after.name)
            
        embed_log.set_footer(text="id: " + str(after.id) + " |-| " +str(datetime.now().date()))  ## User ID und Datum

        ChannelToSend = await after.guild.fetch_channel(logChannelId[0])
        await ChannelToSend.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.
    
        return
    except:
        print("Error")
        return
    


async def nickChange(before, after):
    try:
        con = sqlite3.connect("fractalG.db")
        cur = con.cursor()
        
        cur.execute("SELECT NameChangeLog FROM LogChannels WHERE GuildId=?",(after.guild.id,))
        logChannelId = cur.fetchone()

        con.close()
        
        embed_log = discord.Embed(title="Nick change",  colour=12281600)  ## Der Titel description="Beigetreten"
        embed_log.set_thumbnail(url=after.avatar)  ## Das Bild

        embed_log.add_field(name="Brfore:", value= before.name)
        embed_log.add_field(name="After:", value= after.name)
            
        embed_log.set_footer(text="id: " + str(after.id) + " |-| " +str(datetime.now().date()))  ## User ID und Datum

        ChannelToSend = await after.guild.fetch_channel(logChannelId[0])
        await ChannelToSend.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.
    
        return
    except:
        print("Error")
        return