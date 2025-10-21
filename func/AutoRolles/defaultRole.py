
import sqlite3
import discord
from func.AllLogMsg import BotErrors

async def defaultRoleManager(bot):

    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()
    guilds = bot.guilds

    for guild in guilds:
        

            cur.execute("SELECT RoleId FROM AutoRoles WHERE GuildId = ? and DefaultRole = ?",(guild.id,1))
            defaultRoles = cur.fetchall() ## Holt sich alle gespeicherten Invite links
            

            for member in guild.members:
                allMemberRoles = [memberRole.id for memberRole in member.roles]

                for defaultRole in defaultRoles:
                    if defaultRole[0] not in allMemberRoles:
                        try:
                            await member.add_roles(guild.get_role(int(defaultRole[0])), reason = "Give the member the default roles.")
                        except discord.errors.Forbidden as e:
                            await BotErrors.BotErrorLog(guild,"The bot didn't have the permissions to add the default role <@&" + str(defaultRole[0]) + "> to members of this server. The bot didn't proceed with giving server members their respective roles.")
                            break
                else:
                    # Wird ausgeführt wenn die for loop ohne break beendet wird.
                    continue  # Mit dem nächsten member weiter machen

                # Wird ausgeführt wenn die for loop mit einem break beendet wird.
                break  # Stopt mit dem jetztigen server macht mit dem nächsten weiter.
                            
        
    cur.close()
   

async def defaultRoleManagerOnCommand(guild):

    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()
  
    cur.execute("SELECT RoleId FROM AutoRoles WHERE GuildId = ? and DefaultRole = ?",(guild.id,1))
    defaultRoles = cur.fetchall() ## Holt sich alle gespeicherten Invite links
    

    for member in guild.members:
        allMemberRoles = [memberRole.id for memberRole in member.roles]

        for defaultRole in defaultRoles:
            if defaultRole[0] not in allMemberRoles:
                try:
                    await member.add_roles(guild.get_role(int(defaultRole[0])), reason = "Give the member the default roles.")
                except discord.errors.Forbidden as e:
                    await BotErrors.BotErrorLog(guild,"The bot didn't have the permissions to add the default role <@&" + str(defaultRole[0]) + "> to members of this server. The bot didn't proceed with giving server members their respective roles.")
                    break
        else:
            # Wird ausgeführt wenn die for loop ohne break beendet wird.
            continue  # Mit dem nächsten member weiter machen

        # Wird ausgeführt wenn die for loop mit einem break beendet wird.
        break  # Stopt mit dem jetztigen server macht mit dem nächsten weiter.
                            
        
    cur.close()
   