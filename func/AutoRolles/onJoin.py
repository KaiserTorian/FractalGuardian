
import sqlite3
import discord
from func.AllLogMsg import BotErrors
async def onJoin(member):

    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()
    
    cur.execute("SELECT * FROM AutoRoles WHERE GuildId = ? and OnJoin = ? or DefaultRole = ?",(member.guild.id,1,1))
    autoRoles = cur.fetchall()

    print(autoRoles)
    for autoRole in autoRoles:
        try:

            if autoRole[2] == 1: #on join role
                role = member.guild.get_role(autoRole[1])
                try:
                    await member.add_roles(role)
                except discord.errors.Forbidden as e:
                    await BotErrors.BotErrorLog(member.guild,"The bot didn't have the permissions to add the role <@&" + str(role.id) + "> to the new members of this server.")

            elif autoRole[3] == 1: # default role
                role = member.guild.get_role(autoRole[1])
                try:
                    await member.add_roles(role)
                except discord.errors.Forbidden as e:
                    await BotErrors.BotErrorLog(member.guild,"The bot didn't have the permissions to add the default role <@&" + str(role.id) + "> to members of this server.")

        except Exception as e:
            print(str(e) + "in AutoRoles onJoin")
            
        
    return