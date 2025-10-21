from math import ceil
from datetime import datetime, timedelta, timezone
import sqlite3

import discord

from discord import Button, app_commands
from discord.ext import commands
from discord.app_commands import Choice

  

#Buttons für die Reactionrole seiten
class user_activity_embed(discord.ui.View):
    def __init__(self, max_pages,sorted_member_dict,timeframe,index_pos,filter):
        super().__init__()
        self.max_pages = max_pages
        self.current_page = 0
        self.sorted_member_dict = sorted_member_dict
        self.timeframe = timeframe
        self.filter = filter
    
    async def update_embed(self, interaction):
        embed_reaction_roles = discord.Embed(title="Activity list | "+ self.timeframe +" | Page " +str(self.current_page + 1) + " / "+str(self.max_pages),  colour=1955439)
        index = 0
        index_pos = 1
        last_member_points = None 
        upperIndexLimit = self.current_page * 15 + 14
        lowerIndexLimit = self.current_page * 15 
        for member_dict in self.sorted_member_dict:
            if last_member_points != None:
                if self.filter == "Messages":
                    if last_member_points["TextPoints"] == self.sorted_member_dict[member_dict]["TextPoints"]:
                        index_pos -= 1
                elif self.filter == "Voice Minutes":
                     if last_member_points["TextPoints"] == self.sorted_member_dict[member_dict]["TextPoints"]:
                        index_pos -= 1
            last_member_points = {"> TextPoints" : self.sorted_member_dict[member_dict]["TextPoints"], "> VoicePoints" : self.sorted_member_dict[member_dict]["VoicePoints"]}
            if index < lowerIndexLimit:
                index += 1
                index_pos += 1
                continue
            elif index > upperIndexLimit:
                index += 1
                index_pos += 1
                break


           

            outputName = str(index_pos) + ". " + str(self.interaction.guild.get_member(int(member_dict)).display_name)
            if index_pos == 1:
                outputName = ":first_place_medal: " + str(self.interaction.guild.get_member(int(member_dict)).display_name)
            elif index_pos == 2:
                outputName = ":second_place_medal: " + str(self.interaction.guild.get_member(int(member_dict)).display_name)
            elif index_pos == 3:
                outputName = ":third_place_medal: " + str(self.interaction.guild.get_member(int(member_dict)).display_name)

            voice_points_time_calc = self.sorted_member_dict[member_dict]["VoicePoints"]
            voice_points_time_calc_type = "min"
            if voice_points_time_calc > 1440:
                voice_points_time_calc = round(voice_points_time_calc / 1440, 1)
                voice_points_time_calc_type = "days"
            elif voice_points_time_calc > 60:
                voice_points_time_calc = round(voice_points_time_calc / 60, 1)
                voice_points_time_calc_type = "hours"
            outputValue = f"> Text: {self.sorted_member_dict[member_dict]['TextPoints']} \n> Voice: {voice_points_time_calc} {voice_points_time_calc_type}\n"

            embed_reaction_roles.add_field(name=outputName, value=outputValue, inline=True)
            index_pos += 1 
            index += 1

        await interaction.response.edit_message(embed=embed_reaction_roles, view=self)


    async def update_buttons(self):
        if self.current_page == 0:
           for child in self.children:
                if (type(child) == discord.ui.Button and child.custom_id == "first_site") or (type(child) == discord.ui.Button and child.custom_id == "previous_site"):
                    child.disabled = True
                if (type(child) == discord.ui.Button and child.custom_id == "next_site") or (type(child) == discord.ui.Button and child.custom_id == "last_site"):
                    child.disabled = False

        elif self.current_page == self.max_pages - 1:
             for child in self.children:
                if (type(child) == discord.ui.Button and child.custom_id == "first_site") or (type(child) == discord.ui.Button and child.custom_id == "previous_site"):
                    child.disabled = False
                if (type(child) == discord.ui.Button and child.custom_id == "next_site") or (type(child) == discord.ui.Button and child.custom_id == "last_site"):
                    child.disabled = True
                    
        else:
             for child in self.children:
                    child.disabled = False
    

    @discord.ui.button(label="<<<-", style=discord.ButtonStyle.gray, custom_id="first_site", disabled = True)
    async def first_button(self, interaction, button):
        self.current_page = 0
        await self.update_buttons()
        await self.update_embed(interaction)

    @discord.ui.button(label="<-", style=discord.ButtonStyle.gray, custom_id="previous_site", disabled = True)
    async def previous_button(self, interaction, button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_buttons()
            await self.update_embed(interaction)

    @discord.ui.button(label="->", style=discord.ButtonStyle.gray, custom_id="next_site")
    async def next_button(self, interaction, button):
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
            await self.update_buttons()
            await self.update_embed(interaction)

    @discord.ui.button(label="->>>", style=discord.ButtonStyle.gray, custom_id="last_site")
    async def last_button(self, interaction, button):
        self.current_page = self.max_pages - 1
        await self.update_buttons()
        await self.update_embed(interaction)


class channel_activity_embed(discord.ui.View):
    def __init__(self, max_pages,sortet_activity_dict,timeframe,filter):
        super().__init__()
        self.max_pages = max_pages
        self.current_page = 0
        self.sortet_activity_dict = sortet_activity_dict
        self.timeframe = timeframe
        self.filter = filter


    async def update_embed(self, interaction):
        embed_channel_activity = discord.Embed(title="Activity list | "+ self.timeframe +" | Page " +str(self.current_page + 1) + " / "+str(self.max_pages),  colour=1955439)
        index = 0
        index_pos = 1
        upperIndexLimit = self.current_page * 15 + 14
        lowerIndexLimit = self.current_page * 15 
        last_channel_points = None
        for channel_activity in self.sortet_activity_dict:

            if last_channel_points != None:
                if self.filter == "Text Channel":
                    if last_channel_points["TextPoints"] == self.sortet_activity_dict[channel_activity]["TextPoints"]:
                        index_pos -= 1
                elif self.filter == "Voice Channel":
                    if last_channel_points["VoicePoints"] == channel_activity[1]:
                        index_pos = index_pos - 1

            if self.filter == "Text Channel":
                last_channel_points = {"TextPoints" : self.sortet_activity_dict[channel_activity]["TextPoints"]}
            elif self.filter == "Voice Channel":
                last_channel_points = { "VoicePoints" : channel_activity[1]}


            if index < lowerIndexLimit:
                index += 1
                index_pos += 1
                
                continue
            elif index > upperIndexLimit:
                index += 1
                index_pos += 1
                break
           
        

            outputName = str(index_pos) + ". " + str(interaction.guild.get_channel(int(channel_activity)).name)
            if index_pos == 1:
                outputName = ":first_place_medal: " + str(interaction.guild.get_channel(int(channel_activity)).name)
            elif index_pos == 2:
                outputName = ":second_place_medal: " + str(interaction.guild.get_channel(int(channel_activity)).name)
            elif index_pos == 3:
                outputName = ":third_place_medal: " + str(interaction.guild.get_channel(int(channel_activity)).name)

            if self.filter == "Text Channel":
                outputValue = "> Text: " + str(self.sortet_activity_dict[channel_activity]["TextPoints"])
            else:
                voice_points_time_calc = channel_activity[1]
                voice_points_time_calc_type = "min"
                if voice_points_time_calc > 1440:
                    voice_points_time_calc = round(voice_points_time_calc / 1440, 1)
                    voice_points_time_calc_type = "days"
                elif voice_points_time_calc > 60:
                    voice_points_time_calc = round(voice_points_time_calc / 60, 1)
                    voice_points_time_calc_type = "hours"
                outputValue += f"> Voice: {voice_points_time_calc} {voice_points_time_calc_type}"

            embed_channel_activity.add_field(name=outputName, value=outputValue, inline=True)
            index_pos += 1   
            index += 1

        await interaction.response.edit_message(embed=embed_channel_activity, view=self)
    
    async def update_buttons(self):
        if self.current_page == 0:
           for child in self.children:
                if (type(child) == discord.ui.Button and child.custom_id == "first_site") or (type(child) == discord.ui.Button and child.custom_id == "previous_site"):
                    child.disabled = True
                if (type(child) == discord.ui.Button and child.custom_id == "next_site") or (type(child) == discord.ui.Button and child.custom_id == "last_site"):
                    child.disabled = False

        elif self.current_page == self.max_pages - 1:
             for child in self.children:
                if (type(child) == discord.ui.Button and child.custom_id == "first_site") or (type(child) == discord.ui.Button and child.custom_id == "previous_site"):
                    child.disabled = False
                if (type(child) == discord.ui.Button and child.custom_id == "next_site") or (type(child) == discord.ui.Button and child.custom_id == "last_site"):
                    child.disabled = True
        else:
             for child in self.children:
                    child.disabled = False

    @discord.ui.button(label="<<<-", style=discord.ButtonStyle.gray, custom_id="first_site", disabled = True)
    async def first_button(self, interaction, button):
        self.current_page = 0
        await self.update_buttons()
        await self.update_embed(interaction)

    @discord.ui.button(label="<-", style=discord.ButtonStyle.gray, custom_id="previous_site", disabled = True)
    async def previous_button(self, interaction, button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_buttons()
            await self.update_embed(interaction)

    @discord.ui.button(label="->", style=discord.ButtonStyle.gray, custom_id="next_site")
    async def next_button(self, interaction, button):
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
            await self.update_buttons()
            await self.update_embed(interaction)

    @discord.ui.button(label="->>>", style=discord.ButtonStyle.gray, custom_id="last_site")
    async def last_button(self, interaction, button):
        self.current_page = self.max_pages - 1
        await self.update_buttons()
        await self.update_embed(interaction)


class activity_commands(app_commands.Group):


    @app_commands.choices(sort_by=[Choice(name="Messages", value="Messages"),
                                    Choice(name="Voice Minutes", value="Voice Minutes")])
    @app_commands.choices(timeframe=[Choice(name="Last 30 Days", value="Last 30 Days"),
                                    Choice(name="Last 7 Days", value="Last 7 Days"),
                                    Choice(name="Today", value="Today"),
                                    Choice(name="Last Month", value="Last Month"),
                                    Choice(name="Last Week", value="Last Week"),
                                    Choice(name="This Month", value="This Month"),
                                    Choice(name="This Week", value="This Week"),])
    @app_commands.command(name="members", description="Shows the most active members on your server.")
    async def member_activity(self, interaction: discord.Interaction, timeframe: str = "Last 30 Days", sort_by: str = "Messages") -> None:

        # Loading Embed
        calc_embed = discord.Embed(title="Member activiy | " + timeframe,  colour=1955439)
        calc_embed.add_field(name="Calculating ...", value="",inline=False)
        await interaction.response.send_message(embed=calc_embed)


        # Berechne das Zeitfenster
        timeframe_start ,timeframe_end = convertTimeCommandFrames(timeframe)
        timeframe_start_timestamp = timeframe_start.timestamp()
        timeframe_end_timestamp = timeframe_end.timestamp()


        # Hole alle user aus der activity table.
        con = sqlite3.connect("fractalData.db")
        cur = con.cursor()

        cur.execute("SELECT * FROM UserActivity WHERE GuildId=? AND HourTimestamp>? AND HourTimestamp<?",(interaction.guild.id, timeframe_start_timestamp,timeframe_end_timestamp))
        allUsersSQL = cur.fetchall()

        if allUsersSQL == None or len(allUsersSQL) == 0:
            print("allUsersSQL")
            no_user_saved_embed = discord.Embed(title="Member activiy | " + timeframe,  colour=15082281)
            no_user_saved_embed.add_field(name="No user was active "+ timeframe , value="No saved user activity was found.",inline=False)
            await interaction.edit_original_response(embed=no_user_saved_embed)
            return 
        

        # Berechnet alle user Activity und speichert sie in einer dict.
        userActivity = {}
        for user in allUsersSQL:
            if str(user[1]) not in userActivity:
                if user[5] == 1:
                    userActivity[str(user[1])] = {"TextPoints" : int(user[3]), "VoicePoints" : 0}
                elif user[5] == 2:
                    userActivity[str(user[1])] = {"TextPoints" : 0, "VoicePoints" : int(user[3])}
            else:
                if user[5] == 1:
                    userActivity[str(user[1])]["TextPoints"] = int(userActivity[str(user[1])]["TextPoints"]) + int(str(user[3]))
                elif user[5] == 2:
                    userActivity[str(user[1])]["VoicePoints"] = int(userActivity[str(user[1])]["VoicePoints"]) + int(str(user[3]))
            
        if len(userActivity) == 0:
            print("userActivity 0")
            error_embed = discord.Embed(title="Member activiy | " + timeframe,  colour=15082281)
            error_embed.add_field(name="ERROR "+ timeframe , value="An error occurred while the Bot was calculating.",inline=False)
            await interaction.edit_original_response(embed=error_embed)
            return

        sortet_activity_dict = None
        if sort_by == "Messages":
            # Sortiere das Dictionary basierend auf "TextPoints"
            sortet_activity_dict = dict(sorted(userActivity.items(), key=lambda x: x[1]["TextPoints"], reverse=True))

        elif sort_by == "Voice Minutes":
            # Sortiere das Dictionary basierend auf "VoicePoints"
            sortet_activity_dict = dict(sorted(userActivity.items(), key=lambda x: x[1]["VoicePoints"], reverse=True))
        
        if sortet_activity_dict == None:
            print("sortet_activity_dict")
            error_embed = discord.Embed(title="Member activiy | " + timeframe,  colour=15082281)
            error_embed.add_field(name="ERROR "+ timeframe , value="An error occurred while the Bot was calculating.",inline=False)
            await interaction.edit_original_response(embed=error_embed)
            return


        if len(sortet_activity_dict) / 15 > 1:
            view = user_activity_embed(ceil(len(sortet_activity_dict) / 15), sortet_activity_dict,timeframe,sort_by)
            
            embed_reaction_roles = discord.Embed(title="Activity list | " + timeframe +" | Page 1 / " + str(ceil(len(sortet_activity_dict) / 15)),  colour=1955439)
            index = 0
            index_pos = 1
            last_member_points = None
            upperIndexLimit = 15
            lowerIndexLimit = 0
            for member_dict in sortet_activity_dict:
                if index < lowerIndexLimit:
                    index += 1
                    continue
                elif index > upperIndexLimit:
                    index += 1
                    break

                if last_member_points != None:
                    if sort_by == "Messages":
                        if last_member_points["TextPoints"] == sortet_activity_dict[member_dict]["TextPoints"]:
                            index_pos -= 1
                    elif sort_by == "Voice Minutes":
                        if last_member_points["TextPoints"] == sortet_activity_dict[member_dict]["TextPoints"]:
                            index_pos -= 1

                last_member_points = {"TextPoints" : sortet_activity_dict[member_dict]["TextPoints"], "VoicePoints" : sortet_activity_dict[member_dict]["VoicePoints"]}

                outputName = str(index_pos) + ". " + str(interaction.guild.get_member(int(member_dict)).display_name)
                if index_pos == 1:
                    outputName = ">:first_place_medal: " + str(interaction.guild.get_member(int(member_dict)).display_name)
                elif index_pos == 2:
                    outputName = ":second_place_medal: " + str(interaction.guild.get_member(int(member_dict)).display_name)
                elif index_pos == 3:
                    outputName = ":third_place_medal: " + str(interaction.guild.get_member(int(member_dict)).display_name)
                outputValue = "> Text: " + str(sortet_activity_dict[member_dict]["TextPoints"]) + "\n" + "> Voice: " + str(sortet_activity_dict[member_dict]["VoicePoints"])+ " min\n"

                embed_reaction_roles.add_field(name=outputName, value=outputValue, inline=True)
                index_pos += 1   
                index += 1
            await interaction.edit_original_response(embed=embed_reaction_roles, view=view)

            
        else:
            embed_reaction_roles = discord.Embed(title="Activity list | " + timeframe,  colour=1955439)
            index = 0
            index_pos = 1
            last_member_points = None
            upperIndexLimit = 15
            lowerIndexLimit = 0 
            for member_dict in sortet_activity_dict:
                if index < lowerIndexLimit:
                    index += 1
                    continue
                elif index > upperIndexLimit:
                    index += 1
                    break

                if last_member_points != None:
                    if sort_by == "Messages":
                        if last_member_points["TextPoints"] == sortet_activity_dict[member_dict]["TextPoints"]:
                            index_pos -= 1
                    elif sort_by == "Voice Minutes":
                        if last_member_points["VoicePoints"] == sortet_activity_dict[member_dict]["VoicePoints"]:
                            index_pos -= 1
            
                last_member_points = {"TextPoints" : sortet_activity_dict[member_dict]["TextPoints"], "VoicePoints" : sortet_activity_dict[member_dict]["VoicePoints"]}
                outputName = f"{str(index_pos)}. {interaction.guild.get_member(int(member_dict)).display_name}"
                if index_pos == 1:
                    outputName = f":first_place_medal: {interaction.guild.get_member(int(member_dict)).display_name}"
                elif index_pos == 2:
                    outputName = f":second_place_medal: {interaction.guild.get_member(int(member_dict)).display_name}"
                elif index_pos == 3:
                    outputName = f":third_place_medal: {interaction.guild.get_member(int(member_dict)).display_name}"

                voice_points_time_calc = sortet_activity_dict[member_dict]["VoicePoints"]
                voice_points_time_calc_type = "min"
                if voice_points_time_calc > 1440:
                    voice_points_time_calc = round(voice_points_time_calc / 1440, 1)
                    voice_points_time_calc_type = "days"
                elif voice_points_time_calc > 60:
                    voice_points_time_calc = round(voice_points_time_calc / 60, 1)
                    voice_points_time_calc_type = "hours"
                outputValue = f"> Text: {sortet_activity_dict[member_dict]['TextPoints']} \n> Voice: {voice_points_time_calc} {voice_points_time_calc_type}\n"

                embed_reaction_roles.add_field(name=outputName, value=outputValue, inline=True)
                index_pos += 1   
                index += 1
            await interaction.edit_original_response(embed=embed_reaction_roles)



    @app_commands.choices(filter=[Choice(name="Text,", value="Text Channel"),
                                    Choice(name="Voice Channel", value="Voice Channel")])
    @app_commands.choices(timeframe=[Choice(name="Last 30 Days", value="Last 30 Days"),
                                    Choice(name="Last 7 Days", value="Last 7 Days"),
                                    Choice(name="Today", value="Today"),
                                    Choice(name="Last Month", value="Last Month"),
                                    Choice(name="Last Week", value="Last Week"),
                                    Choice(name="This Month", value="This Month"),
                                    Choice(name="This Week", value="This Week"),])
    @app_commands.command(name="channels", description="Shows the most active channels on your server.")
    async def channel_activity(self, interaction: discord.Interaction, timeframe: str = "Last 30 Days", filter: str = "Text Channel") -> None:
        
        # Loading Embed
        calc_embed = discord.Embed(title="Channel activiy | " + timeframe,  colour=1955439)
        calc_embed.add_field(name="Calculating ...", value="",inline=False)
        await interaction.response.send_message(embed=calc_embed)


        # Berechne das Zeitfenster
        timeframe_start ,timeframe_end = convertTimeCommandFrames(timeframe)
        timeframe_start_timestamp = timeframe_start.timestamp()
        timeframe_end_timestamp = timeframe_end.timestamp()

        # Hole alle user aus der activity table.
        con = sqlite3.connect("fractalData.db")
        cur = con.cursor()
        if filter == "Text Channel":
            cur.execute("SELECT * FROM UserActivity WHERE GuildId=? AND HourTimestamp>? AND HourTimestamp<? AND ActivityType=1",(interaction.guild.id, timeframe_start_timestamp,timeframe_end_timestamp))
        else:
            cur.execute("SELECT * FROM UserActivity WHERE GuildId=? AND HourTimestamp>? AND HourTimestamp<? AND ActivityType=2",(interaction.guild.id, timeframe_start_timestamp,timeframe_end_timestamp))
        allUsersSQL = cur.fetchall()

        if allUsersSQL == None or len(allUsersSQL) == 0:
            print("allUsersSQL")
            no_user_saved_embed = discord.Embed(title="Channel activiy | " + timeframe,  colour=15082281)
            no_user_saved_embed.add_field(name="No channel was active "+ timeframe , value="No saved channel activity was found.",inline=False)
            await interaction.edit_original_response(embed=no_user_saved_embed)
            return 
        

        channel_activity = {}
        for channel in allUsersSQL:
            if str(channel[4]) not in channel_activity:
                if channel[5] == 1:
                    channel_activity[str(channel[4])] = {"TextPoints" : int(channel[3]), "VoicePoints" : 0}
                elif channel[5] == 2:
                    channel_activity[str(channel[4])] = {"TextPoints" : 0, "VoicePoints" : int(channel[3])}
            else:
                if channel[5] == 1:
                    channel_activity[str(channel[4])]["TextPoints"] = int(channel_activity[str(channel[4])]["TextPoints"]) + int(str(channel[3]))
                elif channel[5] == 1:
                    channel_activity[str(channel[4])]["VoicePoints"] = int(channel_activity[str(channel[4])]["VoicePoints"]) + int(str(channel[3]))


        # Error wenn etwas schief geht
        if len(channel_activity) == 0:
            print("userActivity 0")
            error_embed = discord.Embed(title="Member activiy | " + timeframe,  colour=15082281)
            error_embed.add_field(name="ERROR" , value="An error occurred while the Bot was calculating.",inline=False)
            await interaction.edit_original_response(embed=error_embed)
            return

        # Sortiert die dict
        sortet_activity_dict = None
        if filter == "Text Channel":
            # Sortiere das Dictionary basierend auf "TextPoints"
            sortet_activity_dict = dict(sorted(channel_activity.items(), key=lambda x: x[1]["TextPoints"], reverse=True))

        elif filter == "Voice Channel":
            # Sortiere das Dictionary basierend auf "VoicePoints"
            sortet_activity_dict = getAndCalcVoiceChannel(interaction, timeframe)


        if sortet_activity_dict == None:
            print("sortet_activity_dict")
            error_embed = discord.Embed(title="Member activiy | " + timeframe,  colour=15082281)
            error_embed.add_field(name="ERROR "+ timeframe , value="An error occurred while the Bot was calculating.",inline=False)
            await interaction.edit_original_response(embed=error_embed)
            return
        
        if len(sortet_activity_dict) < 15:
            embed_channel_activity = discord.Embed(title="Activity list | "+ timeframe,  colour=1955439)
            index = 0
            index_pos = 1
            upperIndexLimit = 14
            lowerIndexLimit = 0
            last_channel_points = None
            for channel_activity in sortet_activity_dict:
                if index < lowerIndexLimit:
                    index += 1
                    continue
                elif index > upperIndexLimit:
                    index += 1
                    break
            
                if last_channel_points != None:
                    if filter == "Text Channel":
                        if last_channel_points["TextPoints"] == sortet_activity_dict[channel_activity]["TextPoints"]:
                            index_pos -= 1
                    elif filter == "Voice Channel":
                        if last_channel_points["VoicePoints"] == channel_activity[1]:
                            index_pos = index_pos - 1

                outputName = None
                if filter == "Text Channel":
                    last_channel_points = {"TextPoints" : sortet_activity_dict[channel_activity]["TextPoints"]}

                    outputName = str(index_pos) + ". " + str(interaction.guild.get_channel(int(channel_activity)).name)
                    if index_pos == 1:
                        outputName = ":first_place_medal: " + str(interaction.guild.get_channel(int(channel_activity)).name)
                    elif index_pos == 2:
                        outputName = ":second_place_medal: " + str(interaction.guild.get_channel(int(channel_activity)).name)
                    elif index_pos == 3:
                        outputName = ":third_place_medal: " + str(interaction.guild.get_channel(int(channel_activity)).name)

                elif filter == "Voice Channel":
                    last_channel_points = { "VoicePoints" : channel_activity[1]}

                    outputName = str(index_pos) + ". " + str(interaction.guild.get_channel(int(channel_activity[0])).name)
                    if index_pos == 1:
                        outputName = ":first_place_medal: " + str(interaction.guild.get_channel(int(channel_activity[0])).name)
                    elif index_pos == 2:
                        outputName = ":second_place_medal: " + str(interaction.guild.get_channel(int(channel_activity[0])).name)
                    elif index_pos == 3:
                        outputName = ":third_place_medal: " + str(interaction.guild.get_channel(int(channel_activity[0])).name)
        
                    outputValue = ""
                if filter == "Text Channel":
                    outputValue = "> Text: " + str(sortet_activity_dict[channel_activity]["TextPoints"])

                else:
                    voice_points_time_calc = channel_activity[1]
                    voice_points_time_calc_type = "min"
                    if voice_points_time_calc > 1440:
                        voice_points_time_calc = round(voice_points_time_calc / 1440, 1)
                        voice_points_time_calc_type = "days"
                    elif voice_points_time_calc > 60:
                        voice_points_time_calc = round(voice_points_time_calc / 60, 1)
                        voice_points_time_calc_type = "hours"
                    outputValue += f"> Voice: {voice_points_time_calc} {voice_points_time_calc_type}"

                embed_channel_activity.add_field(name=outputName, value=outputValue, inline=True)
                index_pos += 1   
                index += 1

            await interaction.edit_original_response(embed=embed_channel_activity)

        else:
            view = channel_activity_embed(ceil(len(sortet_activity_dict) / 15), sortet_activity_dict,timeframe,filter)
        
            embed_channel_activity = discord.Embed(title="Activity list | " + timeframe +" | Page 1 / " + str(ceil(len(sortet_activity_dict) / 15)),  colour=1955439)
            index = 0
            index_pos = 1
            upperIndexLimit = 20
            lowerIndexLimit = 0
            last_channel_points = None
            for channel_activity in sortet_activity_dict:
                if index < lowerIndexLimit:
                    index += 1
                    continue
                elif index > upperIndexLimit:
                    index += 1
                    break

                if last_channel_points != None:
                    if filter == "Text Channel":
                        if last_channel_points["TextPoints"] == sortet_activity_dict[channel_activity]["TextPoints"]:
                            index_pos = index_pos - 1
                    elif filter == "Voice Channel":
                        if last_channel_points["VoicePoints"] == channel_activity[1]:
                            index_pos = index_pos - 1

                if filter == "Text Channel":
                    last_channel_points = {"TextPoints" : sortet_activity_dict[channel_activity]["TextPoints"]}
                elif filter == "Voice Channel":
                    last_channel_points = { "VoicePoints" : channel_activity[1]}

                outputName = str(index_pos) + ". " + str(interaction.guild.get_channel(int(channel_activity)).name)
                if index_pos == 1:
                    outputName = ":first_place_medal: " + str(interaction.guild.get_channel(int(channel_activity)).name)
                elif index_pos == 2:
                    outputName = ":second_place_medal: " + str(interaction.guild.get_channel(int(channel_activity)).name)
                elif index_pos == 3:
                    outputName = ":third_place_medal: " + str(interaction.guild.get_channel(int(channel_activity)).name)
                if filter == "Text Channel":
                    outputValue = "> Text: " + str(sortet_activity_dict[channel_activity]["TextPoints"])
                else:
                    voice_points_time_calc = channel_activity[1]
                    voice_points_time_calc_type = "min"
                    if voice_points_time_calc > 1440:
                        voice_points_time_calc = round(voice_points_time_calc / 1440, 1)
                        voice_points_time_calc_type = "days"
                    elif voice_points_time_calc > 60:
                        voice_points_time_calc = round(voice_points_time_calc / 60, 1)
                        voice_points_time_calc_type = "hours"
                    outputValue += f"> Voice: {voice_points_time_calc} {voice_points_time_calc_type}"
                 
                embed_channel_activity.add_field(name=outputName, value=outputValue, inline=True)
                index_pos += 1   
                index += 1
            
            await interaction.edit_original_response(embed=embed_channel_activity, view=view)
            return  



    @app_commands.choices(timeframe=[Choice(name="Last 30 Days", value="Last 30 Days"),
                                    Choice(name="Last 7 Days", value="Last 7 Days"),
                                    Choice(name="Today", value="Today"),
                                    Choice(name="Last Month", value="Last Month"),
                                    Choice(name="Last Week", value="Last Week"),
                                    Choice(name="This Month", value="This Month"),
                                    Choice(name="This Week", value="This Week"),])
    @app_commands.command(name="overview", description="Shows an overview of all the activities on your server.")
    async def overview(self, interaction: discord.Interaction,timeframe: str = "Last 30 Days") -> None:
        guild = interaction.guild

        # Loading Embed
        calc_embed = discord.Embed(title=f"{guild.name} activity",  colour=1955439)
        calc_embed.add_field(name="Calculating ...", value="",inline=False)
        await interaction.response.send_message(embed=calc_embed)

        
        # Berechne das Zeitfenster
        timeframe_start ,timeframe_end = convertTimeCommandFrames(timeframe)
        timeframe_start_timestamp = timeframe_start.timestamp()
        timeframe_end_timestamp = timeframe_end.timestamp()

        # Hole alle user aus der activity table.
        con = sqlite3.connect("fractalData.db")
        cur = con.cursor()

        cur.execute("SELECT * FROM UserActivity WHERE GuildId=? AND HourTimestamp>? AND HourTimestamp<?",(interaction.guild.id, timeframe_start_timestamp,timeframe_end_timestamp))
        allUsersSQL = cur.fetchall()
        con.close()

        if allUsersSQL == None or len(allUsersSQL) == 0:
            no_user_saved_embed = discord.Embed(title=f"{guild.name} activity",  colour=15082281)
            no_user_saved_embed.add_field(name="No channel was active "+ timeframe , value="No saved channel activity was found.",inline=False)
            await interaction.edit_original_response(embed=no_user_saved_embed)
            return 
        
        # Berechnet alle user Activity und speichert sie in einer dict.
        channel_activity = {}
        user_activity = {}
        for activity in allUsersSQL:
            if str(activity[1]) not in user_activity:
                if activity[5] == 1:
                    user_activity[str(activity[1])] = {"TextPoints" : int(activity[3]), "VoicePoints" : 0}
                elif activity[5] == 2:
                    user_activity[str(activity[1])] = {"TextPoints" : 0, "VoicePoints" : int(activity[3])}
            else:
                if activity[5] == 1:
                    user_activity[str(activity[1])]["TextPoints"] = int(user_activity[str(activity[1])]["TextPoints"]) + int(str(activity[3]))
                elif activity[5] == 2:
                    user_activity[str(activity[1])]["VoicePoints"] = int(user_activity[str(activity[1])]["VoicePoints"]) + int(str(activity[3]))

            if str(activity[4]) not in channel_activity:
                if activity[5] == 1:
                    channel_activity[str(activity[4])] = {"TextPoints" : int(activity[3]), "VoicePoints" : 0}
                elif activity[5] == 2:
                    channel_activity[str(activity[4])] = {"TextPoints" : 0, "VoicePoints" : int(activity[3])}
            else:
                if activity[5] == 1:
                    channel_activity[str(activity[4])]["TextPoints"] = int(channel_activity[str(activity[4])]["TextPoints"]) + int(str(activity[3]))
                elif activity[5] == 2:
                    channel_activity[str(activity[4])]["VoicePoints"] = int(channel_activity[str(activity[4])]["VoicePoints"]) + int(str(activity[3]))

        if len(user_activity) == 0 or len(channel_activity) == 0:
            error_embed = discord.Embed(title=f"{guild.name} activity",  colour=15082281)
            error_embed.add_field(name="ERROR "+ timeframe , value="An error occurred while the Bot was calculating.",inline=False)
            await interaction.edit_original_response(embed=error_embed)
            return

        sorted_text_user = list(sorted(user_activity.items(), key=lambda x: x[1]["TextPoints"], reverse=True))
        sortet_voice_user = list(sorted(user_activity.items(), key=lambda x: x[1]["VoicePoints"], reverse=True))
        sortet_text_channel = list(sorted(channel_activity.items(), key=lambda x: x[1]["TextPoints"], reverse=True))
        sortet_voice_channel = getAndCalcVoiceChannel(interaction,timeframe)

        user_text_str = ""
        user_voice_str = ""
        channel_text_str = ""
        channel_voice_str = ""

      

        index = 0
        while index < 3:
            if index == 0:
                user_text_str += "> :first_place_medal: "
            elif index == 1:
                user_text_str += "> :second_place_medal: "
            elif index == 2:
                user_text_str += "> :third_place_medal: "
            
            try:
                if str(sorted_text_user[index][1]['TextPoints']) == "0":
                    user_text_str += "-----\n"
                    index += 1
                    continue
                member = guild.get_member(int(sorted_text_user[index][0]))
                user_text_str += str(member.display_name) + " | " + str(sorted_text_user[index][1]['TextPoints']) + "\n"
            except Exception as e:
                user_text_str += "-----\n"
            index += 1

        index = 0
        while index < 3:
            if index == 0:
                user_voice_str += "> :first_place_medal: "
            elif index == 1:
                user_voice_str += "> :second_place_medal: "
            elif index == 2:
                user_voice_str += "> :third_place_medal: "
            
            try:
                if str(sortet_voice_user[index][1]['VoicePoints']) == "0":
                    user_voice_str += "-----\n"
                    index += 1
                    continue
                member = guild.get_member(int(sortet_voice_user[index][0]))
                voice_points_time_calc = sortet_voice_user[index][1]['VoicePoints']
                voice_points_time_calc_type = "min"
                if voice_points_time_calc > 1440:
                    voice_points_time_calc = round(voice_points_time_calc / 1440, 1)
                    voice_points_time_calc_type = "days"
                elif voice_points_time_calc > 60:
                    voice_points_time_calc = round(voice_points_time_calc / 60, 1)
                    voice_points_time_calc_type = "hours"
                user_voice_str += f"{member.display_name} | {voice_points_time_calc} {voice_points_time_calc_type}\n "
            except:
                user_voice_str += "-----\n"
            index += 1

        index = 0
        while index < 3:
            if index == 0:
                channel_text_str += "> :first_place_medal: "
            elif index == 1:
                channel_text_str += "> :second_place_medal: "
            elif index == 2:
                channel_text_str += "> :third_place_medal: "
            
            try:
                if str(sortet_text_channel[index][1]['TextPoints']) == "0":
                    channel_text_str += "-----\n"
                    index += 1
                    continue
                channel = guild.get_channel(int(sortet_text_channel[index][0]))
                channel_text_str += str(channel.name) + " | " + str(sortet_text_channel[index][1]['TextPoints']) + "\n"
            except:
                channel_text_str += "-----\n"
            index += 1
 
        index = 0
        while index < 3:
            if index == 0:
                channel_voice_str += "> :first_place_medal: "
            elif index == 1:
                channel_voice_str += "> :second_place_medal: "
            elif index == 2:
                channel_voice_str += "> :third_place_medal: "
            
            try:
                if str(sortet_voice_channel[index][1]) == 0:
                    channel_voice_str += "-----\n"
                    index += 1
                    continue
                channel = guild.get_channel(int(sortet_voice_channel[index][0]))

                voice_points_time_calc = sortet_voice_channel[index][1]
                voice_points_time_calc_type = "min"
                if voice_points_time_calc > 1440:
                    voice_points_time_calc = round(voice_points_time_calc / 1440, 1)
                    voice_points_time_calc_type = "days"
                elif voice_points_time_calc > 60:
                    voice_points_time_calc = round(voice_points_time_calc / 60, 1)
                    voice_points_time_calc_type = "hours"
                channel_voice_str += f"{channel.name} | {voice_points_time_calc} {voice_points_time_calc_type}\n "
            except Exception as e:
                channel_voice_str += "-----\n"
            index += 1
            
        
        embed = discord.Embed(title=str(guild.name)+" activity",
                      description=f"Overview {timeframe}",
                      colour=0x51ff00,
                      timestamp=datetime.now())
        
        embed.add_field(name="Top User | Text Messages",
                        value=user_text_str,
                        inline=True)
        embed.add_field(name="|",
                        value="|\n|\n|",
                        inline=True)
        embed.add_field(name="Top Channel | Text Messages",
                        value=channel_text_str,
                        inline=True)
        embed.add_field(name="-----------------------------------------------------------------------------------",
                        value="",
                        inline=False)
        embed.add_field(name="Top User | Voice minutes",
                        value=user_voice_str,
                        inline=True)
        embed.add_field(name="|",
                        value="|\n|\n|",
                        inline=True)
        embed.add_field(name="Top Channel | Voice minutes",
                        value=channel_voice_str,
                        inline=True)
        await interaction.edit_original_response(embed=embed)

     
        
      

        return

async def setup(bot: commands.Bot) -> None:
    bot.tree.add_command(activity_commands(name="activity",description="activity"))

#-----------------------HELPER----------------------#

def convertTimeCommandFrames(timeframe : str):
    # Berechne das Zeitfenster
    timeframe_start = datetime.utcnow()
    timeframe_end = datetime.utcnow()
    if timeframe == "Last 30 Days":
        timeframe_start = (datetime.utcnow() -  timedelta(days=30))
    elif timeframe == "Last 3 Days":
        timeframe_start = (datetime.utcnow() -  timedelta(days=30))
    elif timeframe == "Last 24 Hours":
        timeframe_start = (datetime.utcnow() -  timedelta(hours=24))
    elif timeframe == "Last Month":
        today = datetime.now()
        first_day_of_this_month = datetime(today.year, today.month, 1)
        last_day_of_last_month = first_day_of_this_month - timedelta(days=1)
        first_day_of_last_month = datetime(last_day_of_last_month.year, last_day_of_last_month.month, 1)

        timeframe_start = first_day_of_last_month
        timeframe_end = first_day_of_this_month

    elif timeframe == "Last Week":
        today = datetime.now()
        some_day_of_last_week = today - timedelta(days=today.weekday(), weeks=1)
        first_day_of_last_week = datetime(some_day_of_last_week.year, some_day_of_last_week.month, some_day_of_last_week.day)

        timeframe_start = first_day_of_last_week
        timeframe_end = (first_day_of_last_week + timedelta(weeks=1))

    elif timeframe == "This Month":
        today = datetime.now()
        first_day_of_this_month = datetime(today.year, today.month, 1)
        timeframe_start = first_day_of_this_month

    elif timeframe == "This Week":
        today = datetime.now()
        first_day_of_this_week = today - timedelta(days=today.weekday())
        timeframe_start = datetime(first_day_of_this_week.year, first_day_of_this_week.month, first_day_of_this_week.day)
    elif timeframe == "Today":
        today = datetime.now()
        timeframe_start = datetime(today.year, today.month, today.day)

    return timeframe_start, timeframe_end


def getAndCalcVoiceChannel(interaction, timeframe):

    # Berechne das Zeitfenster
    timeframe_start ,timeframe_end = convertTimeCommandFrames(timeframe)
    timeframe_start_timestamp = timeframe_start.timestamp()
    timeframe_end_timestamp = timeframe_end.timestamp()

    all_Voice_Channels = None
    with sqlite3.connect("fractalData.db") as con:

        cur = con.cursor()

        cur.execute("SELECT * FROM ChannelActivityMinutes WHERE GuildId=? AND ActivBegin>? AND ActivBegin<?",(interaction.guild.id, timeframe_start_timestamp,timeframe_end_timestamp))
        print(timeframe_start_timestamp)
        print(timeframe_end_timestamp)
        all_Voice_Channels = cur.fetchall()

    if all_Voice_Channels == None:
        return None

    output_dict = {}
    for voice_Channel in all_Voice_Channels:
        if str(voice_Channel[1]) not in output_dict:
            output_dict[str(voice_Channel[1])] = voice_Channel[3] - voice_Channel[2]
        else:
            output_dict[str(voice_Channel[1])] += voice_Channel[3] - voice_Channel[2]
    
    print(list(sorted(output_dict.items(), key=lambda item: item[1],reverse=True)))
    return list(sorted(output_dict.items(), key=lambda item: item[1],reverse=True))