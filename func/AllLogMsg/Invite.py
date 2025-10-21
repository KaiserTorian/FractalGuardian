import sqlite3
import discord
import datetime



async def inviteCreateLog(invite):
    guild = invite.guild
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT ChannelId FROM LogChannels WHERE GuildId=? AND LogEvent = ?",(guild.id,"Invite_link_Create"))
    allLogChannelIdList = cur.fetchall()
    
    if allLogChannelIdList == None:
        con.close()
        return
    
    for logChannelId in allLogChannelIdList:
        logChannel = await guild.fetch_channel(logChannelId[0])

        if logChannel == None:
            continue
    
        embed_log = discord.Embed(title="",  colour=1955439)  ## Der Titel description="Beigetreten"
        #embed_log.set_thumbnail(url=guild.icon)  ## Das Bild
        embed_log.set_author(name="Invite created",icon_url=guild.icon)

        embed_log.add_field(name="Inviter:", value=str(invite.inviter.name)+ "#" + str(invite.inviter.discriminator))
        if invite.max_uses == 0:
            embed_log.add_field(name="Uses:", value="unlimited")
        else:
            embed_log.add_field(name="Uses:", value=invite.max_uses)
        
        embed_log.add_field(name="Expires in:", value=await format_time(invite.expires_at)) 
        embed_log.set_footer(text="id: " + str(guild.id) )  ## User ID und Datum
        
        #sende embed in channel
        ChannelToSend = guild.get_channel(logChannelId[0])
        await ChannelToSend.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.

    con.close()
    



async def InviteDeleteLog(invite):
    guild = invite.guild
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT ChannelId FROM LogChannels WHERE GuildId=? AND LogEvent = ?",(guild.id,"Invite_link_Delete"))
    allLogChannelIdList = cur.fetchall()
    
    if allLogChannelIdList == None:
        con.close()
        return
    
    for logChannelId in allLogChannelIdList:
        logChannel = await guild.fetch_channel(logChannelId[0])

        if logChannel == None:
            continue

        cur.execute("SELECT InviteId , InviteName , InviteMaxUses, InviterName, InviteExpires FROM InviteLinks WHERE GuildId=? and InviteId=?",(guild.id, invite.id, ))
        saved_invites = cur.fetchone()

        cur.close()
        print(saved_invites)
        embed_log = discord.Embed(title="",  colour=15082281)  ## Der Titel description="Beigetreten"
        #embed_log.set_thumbnail(url=guild.icon)  ## Das Bild
        embed_log.set_author(name="Invite deleted",icon_url=guild.icon)

        embed_log.add_field(name="Inviter:", value=saved_invites[3])
        if saved_invites[2] == 0:
            embed_log.add_field(name="Uses:", value="unlimited")
        else:
            embed_log.add_field(name="Uses:", value=saved_invites[2])

        embed_log.add_field(name="Expires in:", value=await format_time(datetime.datetime.fromisoformat(saved_invites[4])))
        embed_log.set_footer(text="id: " + str(guild.id) )  ## User ID und Datum
        
        #sende embed in channel
        ChannelToSend = guild.get_channel(logChannelId[0])
        await ChannelToSend.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.

    con.close()
    



async def format_time(dt):
    # Berechne die Differenz zwischen dem gegebenen Zeitpunkt und dem aktuellen Zeitpunkt
    time_difference = dt - datetime.datetime.now(datetime.timezone.utc)
    
    # Extrahiere Tage, Stunden und Minuten aus der Differenz
    days = time_difference.days
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes = round_to_nearest_5(remainder // 60)
    
    # Formatiere die Zeit als "DD hh:mm"
    formatted_time = f"{days}d {hours:02}h {minutes:02}m"
    
    return formatted_time


def round_to_nearest_5(number):
    remainder = number % 10  # Ermittle die Einerstelle der Zahl
    if remainder < 5:
        return number - remainder  # Runde auf die nächste niedrigere 5
    else:
        return number + (10 - remainder)  # Runde auf die nächste höhere 5
