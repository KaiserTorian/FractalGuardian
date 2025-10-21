

import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

from typing import List
import sqlite3



#Wenn eine Log funktion dazukommt dann muss di auswahl geändert werden und die Success nachricht

class invite_commands(app_commands.Group):

    #Sucht alle text channel für die auswahl bei den channels
    async def inviteAutocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        inviteList = []

        for invite in await interaction.guild.invites():
            
                
            con = sqlite3.connect("fractalData.db")
            cur = con.cursor()  

            cur.execute("SELECT InviteName FROM InviteLinks WHERE GuildId=? AND InviteId=?",(str(interaction.guild.id),invite.id))
            inviteName = cur.fetchone()

            con.close()

            if inviteName[0] == None:
                inviteList.append([str(invite.id),str(invite.id)])
            else:
                inviteList.append([str(invite.id) + " [" + str(inviteName[0]) + "]",str(invite.id)])

        return [app_commands.Choice(name=str(choice[0]), value=str(choice[1])) for choice in inviteList]


    #add Channel/ function=was soll gelogt werden? / channel ist der channel in dem dasgelogt wird
    @app_commands.command(name="name",description="Add a name to a Invite link. When a user joins the you can see the invite name in the log message.")

    @app_commands.autocomplete(invite=inviteAutocomplete)
    async def invite_name_change(self, interaction: discord.Interaction, invite: str, name: str, delete: bool = False) -> None:
        try:
            inviteIsOnServer = False
            for guildInvite in await interaction.guild.invites():
                if str(guildInvite.id) == str(invite):
                    inviteIsOnServer = True
                    break
            if inviteIsOnServer == False:
                await invite_name_error_response(interaction,"Invite not Found")
                return
        
            con = sqlite3.connect("fractalData.db")
            cur = con.cursor()
            if delete == True:
                cur.execute("UPDATE InviteLinks SET InviteName = ? WHERE InviteId = ? and GuildId = ?",(None,invite,interaction.guild.id))
            else:
                cur.execute("UPDATE InviteLinks SET InviteName = ? WHERE InviteId = ? and GuildId = ?",(name,invite,interaction.guild.id))
            con.commit()

            con.close()
            await invite_name_success_response(interaction,invite,name,delete)
            return
        
        except Exception as e:
            print(e)
            await invite_name_error_response(interaction,None)

async def setup(bot: commands.Bot) -> None:
    bot.tree.add_command(invite_commands(name="invite",description="invite"))




async def invite_name_error_response(interaction: discord.Interaction,error):
    embed_log = discord.Embed(title="",  colour=15082281)  ## Der Titel description="Beigetreten"
    
    if error == "Invite not Found :x:":
        embed_log.add_field(name="Invite not Found",value="The Invite link could not be found.")
    else:
        embed_log.add_field(name="Unexpected Error Encountered :x:",value="Error")
    await interaction.response.send_message(embed=embed_log,ephemeral=False)
    return


async def invite_name_success_response(interaction: discord.Interaction,invite: str, name: str, delete: bool):

    embed_log = discord.Embed(title="",  colour=1955439)
    if delete:
        embed_log.add_field(name="Command Success :white_check_mark:" ,value="The name of "+invite+" was successfully removed.")
    else:
        embed_log.add_field(name="Command Success :white_check_mark:" ,value="The name of "+invite+" is now **"+name+"**.")
    await interaction.response.send_message(embed=embed_log,ephemeral=False)
    return

