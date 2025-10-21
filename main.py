import discord
from discord.ext import commands

import configparser

import dataBaseInit

from func import InviteLinkManager
from func import UserDataManager
from func.AutoRolles import defaultRole

#Activity
from func.ActivityManager import TextActivity
from func.ActivityManager import VoiceActivity
from func.ActivityManager import ActivityHelperFunctions as AHF
from func.ActivityManager import ChannelActivityMinutes

#Log
from func.AllLogMsg import JoinLeave
from func.AllLogMsg import AllVoiceCall
from func.AllLogMsg import BanUnban
from func.AllLogMsg import Timeout
from func.AllLogMsg import Invite as InviteLog
from func.AllLogMsg import _LogHelper as LH

from func.AutoRolles import onJoin
from func.AutoRolles import onReaction


class Bot(commands.Bot):
    def __init__(self):

        super().__init__(command_prefix="F!", intents=discord.Intents.all())

    async def startup(self):  ##Das wird am start ausgeführt
        await bot.wait_until_ready()
        await bot.tree.sync()
        dataBaseInit.dataBaseInit()

        await InviteLinkManager.InviteUpdateOnStartUp(bot)
        await defaultRole.defaultRoleManager(bot) #Gibt jedem Server member die default rollen.

        await ChannelActivityMinutes.UpdateVoiceListOnStartup(bot)
        
        await VoiceActivity.UpdateVoiceListOnStartup(bot)
        await VoiceActivity.HourlyVoiceSave(bot)

        print('Sucessfully synced applications commands')
        print(f'Connected as {bot.user}')
        


    cogsFile = ["commands.LogCommands",
                "commands.InviteCommands",
                "commands.AutoroleCommands",
                "commands.InfoCommands",
                # "commands.ActivityShowCommands"
                ]  ##Eine Liste von allen cogs die geladen werden sollen

    async def setup_hook(self):  ##Das ladet die cogs, die in der Liste "cogsFile" stehen

        for file in self.cogsFile:
            await bot.load_extension(file)
            print(f"{file} geladen")
              
        self.loop.create_task(self.startup())


bot = Bot()




#--on_message
@bot.event
async def on_message(message):
    #wenn der bot was schreibt dann ignoriere es.
    if message.author == bot.user: 
        return
    await VoiceActivity.printList()
    await TextActivity.UserTextActivity(message)
    await ChannelActivityMinutes.printList()

#--Ban
@bot.event
async def on_member_ban(guild,member):
    await BanUnban.BanLogMessage(guild,member)# Ban log Nachricht
    return


@bot.event
async def on_member_unban(guild,member):
    await BanUnban.UnbanLogMessage(guild,member)# Unban log Nachricht
    return


#--join/Leave
@bot.event
async def on_member_join(member):
    inviteLinkUsed = await InviteLinkManager.findInviteOnUserJoin(member) # Sucht den Invite Link.
    await InviteLinkManager.InviteUpdateOnUserJoin(member,inviteLinkUsed) # Updated die InviteLink SQL Tabelle.
    await UserDataManager.SaveUserDataOnJoin(member,inviteLinkUsed) # Speichert die Userdaten in die Nutzerdaten SQL Tabelle.

    await JoinLeave.JoinLogMessage(member) # Join log Nachricht

    await onJoin.onJoin(member) # Gibt dem User die On Join und default rollen.
   

@bot.event
async def on_member_remove(member):
    await JoinLeave.LeaveLogMessage(member) # Leave log Nachricht
    await UserDataManager.DeleteUserDataOnRemove(member) # Löscht die Nutzerdaten.
    await AHF.deleteUserActivityOnRemove(member) # Löscht die Aktivität vom User.




#--Voice
# TODO: Voice activität Testen
@bot.event
async def on_voice_state_update(member,before,after):

    # Voice update log Nachrichten
    if after.channel != None and before.channel == None:
        await AllVoiceCall.VoiceChannelJoin(member,before,after)# Log
        await VoiceActivity.OnUserJoinVoice(member,before,after)# Member Aktivität
        await ChannelActivityMinutes.OnUserJoinVoice(after)# Channel Aktivität

    elif (after.channel != None and before.channel != None) and (after.channel != before.channel):
        await AllVoiceCall.VoiceChannelChange(member,before,after)# Log
        await VoiceActivity.OnUserChangeVoice(member,before,after)# Aktivität
        await ChannelActivityMinutes.OnUserChangeVoice(before,after)# Channel Aktivität

    elif after.channel == None and before.channel != None:
        await AllVoiceCall.VoiceChannelLeave(member,before,after)# Log
        await VoiceActivity.OnUserLeaveVoice(member,before,after)# Aktivität
        await ChannelActivityMinutes.OnUserLeaveVoice(before)# Channel Aktivität

    return


@bot.event
async def on_member_update(before, after):
    if after == None:
        return

    # Timeout log Nachrichten
    if after.is_timed_out() != before.is_timed_out():
        if before.is_timed_out() == False and after.is_timed_out() == True:
            await Timeout.timeout(before,after)
        elif before.is_timed_out() == True and after.is_timed_out() == False:
            await Timeout.timeoutEnd(before,after)



#--Reaction roles
@bot.event
async def  on_raw_reaction_add(payload):
    await onReaction.onReaction(payload,bot) # Gibt dem User die Rollen bei einer Reaktion.

@bot.event
async def  on_raw_reaction_remove(payload):
    await onReaction.onReactionEnd(payload,bot) # Nimmt dem User die Rollen beim löschen einer Reaktion.
    print(payload)

@bot.event
async def on_raw_message_delete(payload):
    await onReaction.onMessageDel(payload)# Löscht den reactions rollen eintrag wenn die Nachreicht gelöscht wurde.

    
#--Invite
@bot.event
async def on_invite_create(invite):
    await InviteLinkManager.InviteUpdateOnCreate(invite) # Update the SQL Tabelle
    await InviteLog.inviteCreateLog(invite=invite) # Log Nachricht
    return


@bot.event
async def on_invite_delete(invite):
    await InviteLog.InviteDeleteLog(invite=invite) # Log Nachricht
    await InviteLinkManager.InviteUpdateOnDelete(invite) # Update die SQL Tabelle
    return


#-- Channel delete
@bot.event
async def on_guild_channel_delete(channel):
    LH.deleteLogSettingOnChannelRemove(channel)
    return

config = configparser.ConfigParser()
config.read('config.ini')

api_token = config.get('API', 'API_TOKEN')

bot.run(api_token)
