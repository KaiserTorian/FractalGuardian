

import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

from typing import List
import sqlite3



#Wenn eine Log funktion dazukommt dann muss di auswahl geändert werden und die Success nachricht

class log_commands(app_commands.Group):



    #-------------------------------------------------------------------------add-----------------------------------------------------------------------------

    #Sucht alle text channel für die auswahl bei den channels
    async def channel_autocomplete_add(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        channelList = []

        for channel in interaction.guild.text_channels:
            if current in channel.name or current == None or current == "":
                
                con = sqlite3.connect("fractalData.db")
                cur = con.cursor()

                cur.execute("SELECT LogEvent FROM LogChannels WHERE GuildId=? AND ChannelId=?",(str(interaction.guild.id),channel.id))
                guildInSQL = cur.fetchall()

                con.close()

                displayText = str(channel.name) 
                if len(guildInSQL) > 0 and len(guildInSQL) < 2:
                    displayText += " ["+str(guildInSQL[0][0])+ "]"
                elif len(guildInSQL) > 1:
                    displayText += " ["+str(guildInSQL[0][0])+  " + "+str(len(guildInSQL) - 1)+" more]"
                channelList.append([displayText,str(channel.id)])

        return [app_commands.Choice(name=str(choice[0]), value=str(choice[1])) for choice in channelList]


    @app_commands.choices(event=[Choice(name="User_Join", value="User_Join"),
                                    Choice(name="User_Leave", value="User_Leave"),
                                    Choice(name="User_Ban", value="User_Ban"),
                                    Choice(name="User_Unban", value="User_Unban"),
                                    Choice(name="User_Timeout", value="User_Timeout"),
                                    Choice(name="Voice_Channel_Update", value="Voice_Channel_Update"),
                                    Choice(name="Bot_Errors",value="Bot_Errors"),
                                    Choice(name="Invite_link_Create", value="Invite_link_Create"),
                                    Choice(name="Invite_link_Delete", value="Invite_link_Delete")])
    @app_commands.autocomplete(channel=channel_autocomplete_add)
    @app_commands.command(name="add",description="Choose a channel where specific server logs are saved.")
    async def log_channel_add(self, interaction: discord.Interaction, channel: str, event: str ) -> None:
        try:
            ##Ist der angegebene channel ein #channel dann löscht er alles was er nicht braucht
            if channel[1] == "#" and channel[0] == "<" and channel[-1] == ">":
                channel = channel[2:]
                channel = channel[:-1]

            ##wenn es text ist
            if channel.isnumeric() == False:
                ##suche alle channel die so heißen
                foundChannel = []
                for channelGuild in interaction.guild.text_channels:
                    if channelGuild.name == channel:
                        foundChannel.append(channelGuild)
                #keinen gefunden
                if len(foundChannel) == 0:
                    await log_add_error_response(interaction,"No channel found")
                    return
                #mehr alls einen gefunden
                elif len(foundChannel) > 1:
                    await log_add_error_response(interaction,"Multiple channels found")
                    return

                channel = foundChannel[0].id
        

            # Ab jetzt muss es numeric sein. Ansonsten ist etwas spektakulär schief gelaufen.
            if str(channel).isnumeric():
                foundChannel = await interaction.guild.fetch_channel(int(channel))

                #wenn kein channel mit der id gefunden wurde
                if foundChannel == None:
                    await log_add_error_response(interaction,"No channel found")
                    return

                
                con = sqlite3.connect("fractalData.db")
                cur = con.cursor() 
                
                cur.execute("SELECT LogEvent FROM LogChannels WHERE GuildId=? AND LogEvent=? AND ChannelId=?",(interaction.guild.id,event,channel))
                #LogEvent = 
                if cur.fetchone() != None:
                    print()
                    con.close()
                    await log_already_active_response(interaction,event,channel)
                    return
                cur.execute("INSERT INTO LogChannels VALUES(?,?,?)",(interaction.guild.id,event,channel))
                con.commit()

                

                await log_add_success_response(interaction, event, channel)

            else:
                await log_add_error_response(interaction,None)
                print("channel is not nummeric")
            
            return
        except Exception as e:
            print(e)
            await log_add_error_response(interaction,None)





    #-------------------------------------------------------------------------remove-----------------------------------------------------------------------------

    async def channel_autocomplete_remove(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        channelList = []
        

        for channel in interaction.guild.text_channels:
            if current in channel.name or current == None or current == "":
                
                con = sqlite3.connect("fractalData.db")
                cur = con.cursor()

                cur.execute("SELECT * FROM LogChannels WHERE GuildId=? AND ChannelId=?",(interaction.guild.id,channel.id))
                eventsInSQL = cur.fetchall()
                con.close()

                if eventsInSQL != None and eventsInSQL != ():

                    if len(eventsInSQL) > 0:
                        channelList.append([f"{channel.name} | All logging events",str(channel.id)])

                    for events in eventsInSQL:
                        channelList.append([f"{channel.name} | {events[1]}",f"{channel.id}#{events[1]}"])


        return [app_commands.Choice(name=str(choice[0]), value=str(choice[1])) for choice in channelList]

 
   
    @app_commands.autocomplete(channel=channel_autocomplete_remove)
    @app_commands.command(name="remove",description="Deletes one/all logging events from a channel.")
    async def log_channel(self, interaction: discord.Interaction,channel:str) -> None:
        try:
            channelEventList = channel.split("#",1)
            channelId = int(channelEventList[0])
            event = None


            con = sqlite3.connect("fractalData.db")
            cur = con.cursor()

            if len(channelEventList) > 1:
                event =  channelEventList[1]
                cur.execute("DELETE from LogChannels WHERE GuildId=? and ChannelId = ? and LogEvent = ?", (interaction.guild.id,channelId, event))
                con.commit()
                con.close()
                await log_remove_success_response(interaction,channelId,event)

            else:
                cur.execute("DELETE from LogChannels WHERE GuildId=? and ChannelId = ?", (interaction.guild.id,channelId))
                con.commit()
                con.close()
                await log_remove_success_response(interaction,channelId,None)

            

        except Exception as e:
            print(e)
            await log_remove_error_response(interaction)

        return
    


async def setup(bot: commands.Bot) -> None:
    bot.tree.add_command(log_commands(name="logging",description="Logging commands"))





#-------------------------------------------------------------------------add_response-----------------------------------------------------------------------------

async def log_add_error_response(interaction: discord.Interaction,error):
    embed_log = discord.Embed(title="",  colour=0xf23f42)  ## Der Titel description="Beigetreten"
    if error == None:
        embed_log.add_field(name="Unexpected Error Encountered :x:",value="Error")
    elif error == "No channel found":
        embed_log.add_field(name="No channel found :x:",value="Make sure that the name of the channel is written correctly.")
    elif error == "Multipel channels found":
        embed_log.add_field(name="Multipel channels found :x:",value="You have to use the channel ID for this Channel.")
    await interaction.response.send_message(embed=embed_log,ephemeral=False)
    return


async def log_already_active_response(interaction: discord.Interaction,function: str, channel: str):

    embed_log = discord.Embed(title="",  colour=15082281)  ## Der Titel description="Beigetreten"
    embed_log.add_field(name="Same log already active",value="In <#"+channel+"> is the "+function+" log event already active.")
    await interaction.response.send_message(embed=embed_log,ephemeral=False)




async def log_add_success_response(interaction: discord.Interaction,function: str, channel: str):

 

    embed_log = discord.Embed(title="",  colour=1955439)
    
    embed_log.add_field(name="Command Success :white_check_mark:" ,value="<#" +channel + "> logs now **" + function + "** events.")
    await interaction.response.send_message(embed=embed_log,ephemeral=False)
    return





#-------------------------------------------------------------------------remove_response-----------------------------------------------------------------------------


async def log_remove_error_response(interaction: discord.Interaction):
    embed_log = discord.Embed(title="",  colour=15082281)  ## Der Titel description="Beigetreten"
   
    embed_log.add_field(name="Unexpected Error Encountered :x:",value="Error")
    

    await interaction.response.send_message(embed=embed_log,ephemeral=False)
    return


async def log_remove_success_response(interaction: discord.Interaction,channelId: int,log_event: str):

    embed_log = discord.Embed(title="",  colour=1955439)

    if log_event == None:
        embed_log.add_field(name="Command Success :white_check_mark:" ,value="All log events have been deleted from <#"+str(channelId)+">.")
        await interaction.response.send_message(embed=embed_log,ephemeral=False)
        return
    
    else:
        embed_log.add_field(name="Command Success :white_check_mark:" ,value=str(log_event) + " log event has been deleted from <#"+str(channelId)+">.")
        await interaction.response.send_message(embed=embed_log,ephemeral=False)
    


