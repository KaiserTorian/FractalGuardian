import discord
from discord import app_commands
from discord.ext import commands

import sqlite3

from datetime import datetime, timedelta, timezone


#Wenn eine Log funktion dazukommt dann muss di auswahl geändert werden und die Success nachricht

class info_commands(app_commands.Group):



    # User Info
    @app_commands.command(name="user_info",description="Shows infos about a server member.")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member) -> None:
      

      
        # Holt alle sql daten.

        con = sqlite3.connect("fractalData.db")
        cur = con.cursor()  

        cur.execute("SELECT * FROM UserData WHERE GuildId=? AND UserId=?",(interaction.guild.id,member.id))
        SQLUserData = cur.fetchone()
        
        timestampMonth = (datetime.utcnow() -  timedelta(days=30)).timestamp()
        cur.execute("SELECT * FROM UserActivity WHERE GuildId=? AND UserId=? AND HourTimestamp>?",(interaction.guild.id,member.id,timestampMonth))
        SQLUserActivity = cur.fetchall()

        usedInviteLink = None
        if SQLUserData != None:
            print(SQLUserData[3])
            cur.execute("SELECT * FROM InviteLinks WHERE GuildId=? AND InviteId=?",(interaction.guild.id,SQLUserData[3]))
            usedInviteLink = cur.fetchone()

            if usedInviteLink == None:
                cur.execute("SELECT * FROM InviteLinksArchive WHERE GuildId=? AND InviteId=?",(interaction.guild.id,SQLUserData[3]))
                usedInviteLink = cur.fetchone()


        # Verarbeitet die Daten. 


        # Accound erstellt.
        timeCreated = member.created_at
        createdText = await timestampToTextForLogs(timeCreated)
        createdDate = datetime(int(timeCreated.strftime("%Y")),int(timeCreated.strftime("%m")),int(timeCreated.strftime("%d")))
        createdEmbedText = str(createdDate.day) + "." + str(createdDate.month) + "." + str(createdDate.year) + " | " + createdText

        # Server beigetreten
        timeJoined = member.joined_at
        joinedText = await timestampToTextForLogs(timeJoined) # type: ignore
        joinedDate = datetime(int(timeJoined.strftime("%Y")),int(timeJoined.strftime("%m")),int(timeJoined.strftime("%d")))
        joinedEmbedText = str(joinedDate.day) + "." + str(joinedDate.month) + "." + str(joinedDate.year) + " | " + joinedText

        if usedInviteLink != None:
            inviteText = await inviteToText(usedInviteLink,interaction.guild)
        else:
            inviteText = "The Member has no saved invite link."

        ##Rollen
        userRoles = []
        for i in member.roles:
            if i.name != "@everyone":
                userRoles.append(i.mention)

        # Erstellt den Embed
        
        
        embedUserInfo = discord.Embed(title=member.display_name,  colour=member.colour,timestamp= datetime.utcnow())
        embedUserInfo.set_thumbnail(url=member.avatar)

        embedUserInfo.add_field(name="Account created: ", value= createdEmbedText,inline=False)
        
        embedUserInfo.add_field(name="Joined at:",value=joinedEmbedText, inline=False)
        embedUserInfo.add_field(name="Joined using:", value = inviteText, inline=False)  ##Invite link

        if len(userRoles) > 0:
            embedUserInfo.add_field(name="Roles: ", value=" , ".join(userRoles), inline=False)
        else:
            embedUserInfo.add_field(name="Roles: ", value="No roles.", inline=False)

        embedUserInfo.set_footer(text="id: " + str(member.id))

        print("why")
        await interaction.response.send_message(embed = embedUserInfo, ephemeral=True)
        

async def setup(bot: commands.Bot) -> None:
    bot.tree.add_command(info_commands(name="show",description="show"))




#-----------------------------------------------USER Info-------------------------------------------------------------

async def timestampToTextForLogs(timestamp: datetime):
    timestamp_now = datetime.now(timezone.utc)
    timestamp = timestamp.replace(tzinfo=timezone.utc)  # Füge Zeitzoneinformation hinzu

    timestamp_delta = int((timestamp_now - timestamp).total_seconds())

    units = [("year", 31536000), ("month", 2592000), ("day", 86400), ("hour", 3600), ("minute", 60), ("second", 1)]
    time_list = []

    for unit, seconds_in_unit in units:
        if timestamp_delta // seconds_in_unit > 0:
            value = timestamp_delta // seconds_in_unit
            timestamp_delta -= seconds_in_unit * value
            time_list.append((value, unit + ("s" if value != 1 else "")))

    if not time_list:
        return "--"

    return ", ".join(f"{value} {unit}" for value, unit in time_list[:-1]) + " and " + str(time_list[-1][0]) + " " + time_list[-1][1]



async def inviteToText(invite,guild):
    # try:
    
    print(invite)
    if invite == None:
        return "No Link found"  ## Wenn ein Fehler aufgetreten ist.

    if invite[2] != None:  ## Wenn der invite link mit namen gespeichert ist.

        return "Invite Name: **" + str(invite[2]) + "**\nInviter: " + invite[7]   ## Gibt eine vollwertige Antwort zurück, die man gleich verwenden kann.

    else:  ## Wenn der invite link ohne namen gespeichert ist.

        return "Invite Name: --\nLink Code: " + str(invite[1]) + "\nInviter: " + invite[7]   ## Gibt eine vollwertige Antwort zurück, die man gleich verwenden kann.
    
    # except:
    #     return "Error"

