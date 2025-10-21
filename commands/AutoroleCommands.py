from math import ceil
import discord

from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

from func.AutoRolles import defaultRole
import sqlite3

import emoji #pip install emoji

def is_emoji(input):
    return emoji.is_emoji(input)
  

#Buttons für die Reactionrole seiten
class reactionrole_sites(discord.ui.View):
    def __init__(self, max_pages,messageList,roleList):
        super().__init__()
        self.max_pages = max_pages
        self.current_page = 0
        self.messageList = messageList
        self.roleList = roleList


    async def update_embed(self, interaction):
        embed_reaction_roles = discord.Embed(title="Reactionrole list | Page " +str(self.current_page + 1) + " / "+str(self.max_pages),  colour=1955439)
        index = 0
        upperIndexLimit = self.current_page * 10 + 9
        lowerIndexLimit = self.current_page * 10 
        for message in self.messageList:
            if index < lowerIndexLimit:
                continue
            elif index > upperIndexLimit:
                break
            outputString = ""
            for role in self.roleList[str(message)]:
                outputString = outputString + str(role["emoji"]) + " = " + ",".join(role["roleList"]) +  "\n"
    
            embed_reaction_roles.add_field(name=self.messageList[str(message)].content[:20] + self.roleList[str(message)][0]["messageType"], value=outputString, inline=False)
                
        await interaction.message.edit(embed=embed_reaction_roles, view=self)


    @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray)
    async def previous_button(self, button, interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_embed(button)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.gray)
    async def next_button(self, button, interaction):
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
            await self.update_embed(button)



class autorole_commands(app_commands.Group):

    #--------------------------------INFO--------------------------------------#
    
    @app_commands.choices(selection=[Choice(name="On_Join/default",value="On_Join/default"),
                                    Choice(name="Reactionrole",value="Reactionrole")])
    @app_commands.command(name="show", description="Shows what autoroles are active.")
    async def autorole_info(self, interaction: discord.Interaction, selection: str) -> None:
        try:
            if selection == "On_Join/default":

                # Loading Embed
                calc_embed = discord.Embed(title="Autorole list",  colour=1955439)  
                calc_embed.add_field(name="Calculating ...", value="",inline=False)
                await interaction.response.send_message(embed=calc_embed)


                con = sqlite3.connect("fractalData.db")
                cur = con.cursor()

                cur.execute("SELECT * FROM AutoRoles WHERE GuildId = ?",(interaction.guild.id,))
                autoRoles = cur.fetchall()
                
                onJoinList = []
                defaultList = []

                for autoRole in autoRoles:
                    if autoRole[2] == 1:
                        onJoinList.append("<@&" + str(autoRole[1]) + ">")
                    if autoRole[3] == 1:
                        defaultList.append("<@&" + str(autoRole[1]) + ">")



                embed_log = discord.Embed(title="Autorole list",  colour=1955439)  
                if len(onJoinList) == 0:
                    embed_log.add_field(name="On Join Roles:", value="This server has no join roles",inline=False)
                else:
                    embed_log.add_field(name="On Join Roles:", value=",".join(onJoinList),inline=False)

                if len(defaultList) == 0:   
                    embed_log.add_field(name="Default Roles:", value="This server has no default roles",inline=False)
                else:
                    embed_log.add_field(name="Default Roles:", value=",".join(defaultList),inline=False)

                #sende embed in channel
                await interaction.edit_original_response(content=None,embed=embed_log)  # type: ignore ## Sendet den Embed in den Channel der Eingestellt ist.


            
            elif selection == "Reactionrole":

                # Loading Embed
                calc_embed = discord.Embed(title="Reactionrole list",  colour=1955439)  
                calc_embed.add_field(name="Calculating ...", value="",inline=False)
                await interaction.response.send_message(embed=calc_embed)
                
                guild = interaction.guild

                con = sqlite3.connect("fractalData.db")
                cur = con.cursor()

                cur.execute("SELECT * FROM ReactionRoles WHERE GuildId = ?",(guild.id,))
                reactionRolesSQL = cur.fetchall()
                
                messageList = {}
                roleList = {}
                
                # Erstellt eine sortierte liste von allen reactionroles auf dem server
                for reactionRoleSQL in reactionRolesSQL:

                    channel = guild.get_channel(int(reactionRoleSQL[2]))
                    if channel == None:
                        continue

                    partial_message = channel.get_partial_message(int(reactionRoleSQL[3]))
                    if partial_message == None:
                        continue
                    
                    message = None

                    if str(reactionRoleSQL[3]) not in messageList:
                        message = await channel.fetch_message(int(reactionRoleSQL[3]))
                        if message == None:
                            continue
                        
                    if str(reactionRoleSQL[3]) in roleList :
                        emojiAlreadySaved = False

                        for role in roleList[str(reactionRoleSQL[3])]:
                            if role["emoji"] == reactionRoleSQL[4]:
                                role["roleList"].append("<@&"+str(reactionRoleSQL[5])+">")
                                emojiAlreadySaved = True
                                break

                        if emojiAlreadySaved == False:
                            roleList[str(reactionRoleSQL[3])].append({"emoji" : reactionRoleSQL[4],"roleList":["<@&"+str(reactionRoleSQL[5])+">"],"messageType": " | Type = " + str(reactionRoleSQL[6])})
                            
                    else:
                        roleList[str(reactionRoleSQL[3])] = [{"emoji" : reactionRoleSQL[4],"roleList":["<@&"+str(reactionRoleSQL[5])+">"],"messageType": " | Type = " + str(reactionRoleSQL[6])}]

                    if message != None:
                        messageList[str(reactionRoleSQL[3])] = message
                    

                if len(messageList) == 0: # return "no reactionRolles"
                    error_embed = discord.Embed(title="Reactionrole list",  colour=15082281)  
                    error_embed.add_field(name="This server has no Reactionroles.", value="",inline=False)
                    await interaction.edit_original_response(embed=error_embed)
                    return
                

                if len(messageList) < 10: # Nur liste

                    embed_reaction_roles = discord.Embed(title="Reactionrole list",  colour=1955439)
                    for message in messageList:
                        outputString = ""
                        for role in roleList[str(message)]:
                          outputString = outputString + str(role["emoji"]) + " = " + ",".join(role["roleList"]) +  "\n"
                
                        embed_reaction_roles.add_field(name=messageList[str(message)].content[:20] + roleList[str(message)][0]["messageType"], value=outputString, inline=False)
                    await interaction.edit_original_response(content=None, embed=embed_reaction_roles)

                else: # liste + seiten logik
                    print(ceil(len(messageList) / 10))
                    view = reactionrole_sites(ceil(len(messageList) / 10), messageList, roleList)
                
                    embed_reaction_roles = discord.Embed(title="Reactionrole list | Page 1 / " + str(ceil(len(messageList) / 10)),  colour=1955439)
                    index = 0
                    upperIndexLimit = 9
                    lowerIndexLimit = 0
                    for message in messageList:
                        if index < lowerIndexLimit:
                            continue
                        elif index > upperIndexLimit:
                            break

                        outputString = ""
                        for role in roleList[str(message)]:
                          outputString = outputString + str(role["emoji"]) + " = " + ",".join(role["roleList"]) +  "\n"

                        embed_reaction_roles.add_field(name=messageList[str(message)].content[:20] + roleList[str(message)][0]["messageType"], value=outputString, inline=False)
                        index + 1
                    

                    await interaction.edit_original_response(content=None, embed=embed_reaction_roles,view=view)


        except:

            error_embed = discord.Embed(title="",  colour=1955439)  
            error_embed.add_field(name="An Error occured", value="",inline=False)
            await interaction.edit_original_response(embed=error_embed)
 


    #-----------------------------------------------------On_join--------------------------------------------------------------#
        

    @app_commands.command(name="on_join", description="Automatically adds a role to every NEW member.")
    async def on_join(self, interaction: discord.Interaction, role: discord.Role) -> None:
        #print("Invite List " + filters)  ## Log für den Server.

        try:
            con = sqlite3.connect("fractalData.db")
            cur = con.cursor()

            cur.execute("SELECT OnJoin FROM AutoRoles WHERE GuildId = ? and RoleId = ?",(interaction.guild.id, role.id))
            onJoin = cur.fetchone()
            
            if onJoin != None:

                if onJoin[0] == 1:
                    cur.execute("UPDATE AutoRoles SET OnJoin = 0 WHERE RoleId = ? and GuildId = ?",(role.id, interaction.guild.id))
                    con.commit()
                    await on_join_success_response(interaction,role,False)
                else:
                    cur.execute("UPDATE AutoRoles SET OnJoin = 1 WHERE RoleId = ? and GuildId = ?",(role.id, interaction.guild.id))
                    con.commit()
                    await on_join_success_response(interaction,role,True)
            else:
                
                cur.execute("INSERT INTO AutoRoles VALUES(?, ?, ?, ?)",(interaction.guild.id, int(role.id), 1,0))
                con.commit()

                await on_join_success_response(interaction,role,True)

        except Exception as e:
            print(e)
            await on_join_error_response(interaction,e)



    #-----------------------------------------------------Default--------------------------------------------------------------#


    @app_commands.command(name="default_role", description="Automatically adds a role to every member.")
    async def default_role(self, interaction: discord.Interaction, role: discord.Role) -> None:
        #print("Invite List " + filters)  ## Log für den Server.

        try:
            con = sqlite3.connect("fractalData.db")
            cur = con.cursor()

            cur.execute("SELECT DefaultRole FROM AutoRoles WHERE GuildId = ? and RoleId = ?",(interaction.guild.id, role.id))
            onJoin = cur.fetchone()
            
            if onJoin != None:

                if onJoin[0] == 1:
                    cur.execute("UPDATE AutoRoles SET DefaultRole = 0 WHERE RoleId = ? and GuildId = ?",(role.id, interaction.guild.id))
                    con.commit()
                    await default_role_success_response(interaction,role,False)
                else:
                    cur.execute("UPDATE AutoRoles SET DefaultRole = 1 WHERE RoleId = ? and GuildId = ?",(role.id, interaction.guild.id))
                    con.commit()
                    await default_role_success_response(interaction,role,True)
            else:
                
                cur.execute("INSERT INTO AutoRoles VALUES(?, ?, ?, ?)",(interaction.guild.id, role.id, 0, 1))
                con.commit()

                await default_role_success_response(interaction,role,True)
            defaultRole.defaultRoleManagerOnCommand(interaction.guild)

        except Exception as e:
            print(e)
            await default_role_error_response(interaction,e)



    
    #-----------------------------------------------------reactionrole_add--------------------------------------------------------------#


    @app_commands.choices(message_type=[Choice(name="Normal",value="Normal"),
                                    Choice(name="Toggle",value="Toggle")])
    @app_commands.command(name="reactionrole_add", description="Adds reactions to a message that give the user a role.")
    async def reactionrole_add(self, interaction: discord.Interaction, message_id: str, emoji: str, role: discord.Role, message_type: str) -> None:
        try:
            emoji = emoji.strip()

            if is_emoji(emoji) == False:
                await reactionrole_error_response(interaction,"error Emoji add")
                return

            if message_id.isnumeric() == False: 
                await reactionrole_error_response(interaction,"no Message")
                return
            
            guild = interaction.guild
            discordMessage = None

            for channel in guild.text_channels:
                try:
                    if await channel.fetch_message(int(message_id)) != None:
                        discordMessage = await channel.fetch_message(int(message_id))
                        break
                except:
                    continue

            if discordMessage == None:
                await reactionrole_error_response(interaction,"no Message")
                return
            
            con = sqlite3.connect("fractalData.db")
            cur = con.cursor()
            
            cur.execute("SELECT RowId FROM ReactionRoles WHERE GuildId=? and MessageId=? and Emoji=? and RoleId=?",(guild.id,message_id,emoji,role.id))
            if cur.fetchone() != None:
                    print()
                    con.close()
                    await reactionroll_already_active_response(interaction,emoji,role)
                    return

            cur.execute("INSERT INTO ReactionRoles VALUES(?,?,?,?,?,?,?)",(None,guild.id,discordMessage.channel.id,message_id,emoji,role.id,message_type))
            cur.execute("UPDATE ReactionRoles SET MessageType = ? WHERE MessageId = ? and GuildId = ?",(message_type,int(message_id),guild.id))
            con.commit()

            
            con.close

            try:
                await discordMessage.add_reaction(emoji)
            except:
                await reactionrole_error_response(interaction,"error Emoji")

            await reactionrole_add_response(interaction,emoji,role)
        except Exception as e:
            print(e)
            await reactionrole_error_response(interaction)




    @app_commands.command(name="reactionrole_remove", description="Delete one/all reactionroles from a message.")
    async def reactionrole_remove(self, interaction: discord.Interaction, message_id: str, emoji: str = "All", role: discord.Role = None) -> None:
        try:
            emoji = emoji.strip()

            if is_emoji(emoji) == False:
                await reactionrole_error_response(interaction,"error Emoji add")
                return
    
            if message_id.isnumeric() == False: 
                await reactionrole_error_response(interaction,"no Message")
                return
            
            guild = interaction.guild
            discordMessage = None


            for channel in guild.text_channels:
                try:
                    if await channel.fetch_message(int(message_id)) != None:
                        discordMessage = await channel.fetch_message(int(message_id))
                        break
                except:
                    continue

            if discordMessage == None:
                await reactionrole_error_response(interaction, "no Message")
                return
            

            con = sqlite3.connect("fractalData.db")
            cur = con.cursor()

            if role == None:
                cur.execute("DELETE FROM ReactionRoles WHERE GuildId=? and MessageId=? and Emoji=?",(guild.id,message_id,emoji))
            elif role is None and emoji == "All":
                cur.execute("DELETE FROM ReactionRoles WHERE GuildId=? and MessageId=?",(guild.id,message_id))
            else:
                cur.execute("DELETE FROM ReactionRoles WHERE GuildId=? and MessageId=? and Emoji=? and RoleId=?",(guild.id,message_id,emoji,role.id))
            con.commit()


            if con.total_changes == 0:
                await reactionrole_error_response(interaction, "error Delete")
                return
            
            cur.execute("SELECT RowId FROM ReactionRoles WHERE GuildId=? and MessageId=? and Emoji=?",(guild.id,message_id,emoji))
            ReactionRoles = cur.fetchall()
            if ReactionRoles != None:
                if len(ReactionRoles) < 1:
                    try:
                        await discordMessage.clear_reaction(emoji)
                    except:
                        await reactionrole_error_response(interaction,"error Emoji")


            con.close
            await reactionrole_del_response(interaction,emoji,role)
        except Exception as e:
            print(e)
            await reactionrole_error_response(interaction)

    

async def setup(bot: commands.Bot) -> None:
    bot.tree.add_command(autorole_commands(name="autorole",description="Autorole commands."))




#-----------------------------------------------------On_join_response--------------------------------------------------------------#
    
async def on_join_success_response(interaction,role,add):

    embed_log = discord.Embed(title="",  colour=1955439)  ## Der Titel description="Beigetreten"
    if add == True:
        embed_log.add_field(name="Command Success :white_check_mark:" ,value="Every new member gets this role: <@&" + str(role.id) + ">")
    else:
        embed_log.add_field(name="Command Success :white_check_mark:",value="<@&" + str(role.id) + "> is no longer a Autoroll. ")
    await interaction.response.send_message(embed=embed_log,ephemeral=False)


async def on_join_error_response(interaction,error):

    embed_log = discord.Embed(title="",  colour=15082281)  ## Der Titel description="Beigetreten"
    print()
    if error == "No Role Found":
        embed_log.add_field(name="Command Error :x:" ,value="The Role was not Found")
    else:
        embed_log.add_field(name="Unexpected Error Encountered :x:",value="If the error persists please open a support ticket.")
    await interaction.response.send_message(embed=embed_log,ephemeral=False)





#-----------------------------------------------------Default--------------------------------------------------------------#


async def default_role_success_response(interaction,role,add):

    embed_log = discord.Embed(title="",  colour=1955439)  ## Der Titel description="Beigetreten"
    if add == True:
        embed_log.add_field(name="Command Success :white_check_mark:" ,value="Every member gets this role: <@&" + str(role.id) + ">")
    else:
        embed_log.add_field(name="Command Success :white_check_mark:",value="<@&" + str(role.id) + "> is no longer the default role. ")
    await interaction.response.send_message(embed=embed_log,ephemeral=False)
    

async def default_role_error_response(interaction,error):

    embed_log = discord.Embed(title="",  colour=15082281)  ## Der Titel description="Beigetreten"
    print()
    if error == "No Role Found":
        embed_log.add_field(name="Command Error :x:" ,value="The Role was not Found")
    else:
        embed_log.add_field(name="Unexpected Error Encountered :x:",value="If the error persists please open a support ticket.")
    await interaction.response.send_message(embed=embed_log,ephemeral=False)




#-------------------------------------reactionrole--------------------------------------------------

async def reactionrole_error_response(interaction, error = None):
    embed_log = discord.Embed(title="",  colour=15082281)  ## Der Titel description="Beigetreten"
   
    if error=="no Message":
        embed_log.add_field(name="Error Encountered :x:",value="The text message was not found.")
    elif error=="error Emoji add":
        embed_log.add_field(name="Error Encountered :x:",value="Unable to add the emoji.")
    elif error=="error Delete":
        embed_log.add_field(name="Error Encountered :x:",value="Unable to delete the reacton_role.")
    elif error=="error Role":
        embed_log.add_field(name="Error Encountered :x:",value="The role was not found.")
    else:
        embed_log.add_field(name="Unexpected Error Encountered :x:",value="Unexpected Error Encountered")
    await interaction.response.send_message(embed=embed_log,ephemeral=False)
    return


async def reactionroll_already_active_response(interaction: discord.Interaction, emoji: str, role: discord.Role):

    embed_log = discord.Embed(title="",  colour=15082281)  ## Der Titel description="Beigetreten"
    embed_log.add_field(name="Already present",value=emoji+" already gives the user the role: <@&"+ str(role.id)+">")
    await interaction.response.send_message(embed=embed_log,ephemeral=False)


async def reactionrole_del_response(interaction: discord.Interaction, emoji: str,  role: discord.Role):
    if role != "":
        discordRole = interaction.guild.get_role(int(role))
    else:
        discordRole = None
    embed_log = discord.Embed(title="",  colour=1955439)

    if discordRole != None:
        embed_log.add_field(name="Command Success :white_check_mark:" ,value="Successfully deleted <@&"+ str(role.id) + "> from " + emoji + ".")
    else:
        embed_log.add_field(name="Command Success :white_check_mark:" ,value="Successfully deleted:" + emoji)
    await interaction.response.send_message(embed=embed_log,ephemeral=False)
    return

 
async def reactionrole_add_response(interaction: discord.Interaction, emoji: str,  role: discord.Role):
    
    embed_log = discord.Embed(title="",  colour=1955439)  
    
    if role != None:
        embed_log.add_field(name="Command Success :white_check_mark:" ,value="Successfully addet <@&"+ str(role.id) + "> to " + emoji + ".")

    await interaction.response.send_message(embed=embed_log,ephemeral=False)
    return

    