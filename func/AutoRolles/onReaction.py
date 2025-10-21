import sqlite3
import discord
from func.AllLogMsg import BotErrors


async def onReaction(payload,bot):
    try:

        if payload.user_id == bot.user.id:
            return
        
        guildId = payload.guild_id
        discordGuild = bot.get_guild(guildId)


        con = sqlite3.connect("fractalData.db")
        cur = con.cursor()

        cur.execute("SELECT * FROM ReactionRoles WHERE GuildId=? and MessageId=? and Emoji=?",(int(payload.guild_id),int(payload.message_id),str(payload.emoji)))
        ReactionRoles = cur.fetchall()



        
        if ReactionRoles == None:
            return
        # print(ReactionRoles)
        if ReactionRoles[0][6] == "Normal":

            for Role in ReactionRoles:
                
                discordRole = discordGuild.get_role(Role[5])
                discordMember = discordGuild.get_member(int(payload.user_id))
                try:
                    await discordMember.add_roles(discordRole)
                except discord.errors.Forbidden as e:
                    await BotErrors.BotErrorLog(discordMember.guild,"The bot doesn't have the permissions to add the reaction role <@&" + str(discordRole.id) + "> to members of this server.")
                
        elif  ReactionRoles[0][6] == "Toggle":
            for Role in ReactionRoles:

                discordRole = discordGuild.get_role(Role[5])
                discordMember = discordGuild.get_member(int(payload.user_id))

                try:
                    await discordMember.add_roles(discordRole)
                except discord.errors.Forbidden as e:
                    await BotErrors.BotErrorLog(discordMember.guild,"The bot doesn't have the permissions to add the role <@&" + str(discordRole.id) + "> to members of this server.")

            message = await discordGuild.get_channel(payload.channel_id).fetch_message(payload.message_id)
            for reaction in message.reactions:
                users = [user.id async for user in reaction.users()]
                if (payload.user_id in users) and (str(payload.emoji) !=str(reaction.emoji)):
                    await reaction.remove(discordMember)
   

        return
    
    

    except Exception as e:
        print(e)
        return
    

async def onReactionEnd(payload,bot):
    try:
        if payload.user_id == bot.user.id:
            return
        
        guildId = payload.guild_id
        discordGuild = bot.get_guild(guildId)


        con = sqlite3.connect("fractalData.db")
        cur = con.cursor()

        cur.execute("SELECT * FROM ReactionRoles WHERE GuildId=? and MessageId=? and Emoji=?",(int(payload.guild_id),int(payload.message_id),str(payload.emoji)))
        ReactionRoles = cur.fetchall()

        if ReactionRoles == None:
            return

        for Role in ReactionRoles:
            
            discordRole = discordGuild.get_role(Role[5])
            discordMember = discordGuild.get_member(int(payload.user_id))

            await discordMember.remove_roles(discordRole)
            # await reactRoleDelLog(discordMember,discordRole)
            
        return
    except Exception as e:
        print(e)
        return


async def onMessageDel(payload):
    try:
        con = sqlite3.connect("fractalData.db")
        cur = con.cursor()

        cur.execute("DELETE FROM ReactionRoles WHERE GuildId=? and MessageId=?",(payload.guild_id,payload.message_id))
        con.commit()
        con.close()
    except:
        print("Error onMessageDel in onReaction")
    #---------------------------LOG------------------------------------------

async def reactRoleAddLog(member,role):

    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT AutoRoleLog FROM LogChannels WHERE GuildId=?",(member.guild.id,))
    logChannelId = cur.fetchone()

    if logChannelId[0] == None :
        con.close()
        return
    elif await member.guild.fetch_channel(logChannelId[0]) == None:
        con.close()
        return

    con.close()

    guild = member.guild

    embed_log = discord.Embed(title="",  colour=1955439)  ## Der Titel description="Beigetreten"
    embed_log.set_author(name="Reactionrole added",icon_url=member.avatar)

    embed_log.add_field(name="Member:", value=str(member.name)+ "#" + str(member.discriminator))
    embed_log.add_field(name="Role", value="Added <@&" + str(role.id) + ">")
    
    embed_log.set_footer(text="id: " + str(member.id) )  ## User ID und Datum

    ChannelToSend = await member.guild.fetch_channel(logChannelId[0])
    await ChannelToSend.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.

    return


async def reactRoleDelLog(member,role):

    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    #LogChannel
    cur.execute("SELECT AutoRoleLog FROM LogChannels WHERE GuildId=?",(member.guild.id,))
    logChannelId = cur.fetchone()

    if logChannelId[0] == None :
        con.close()
        return
    elif await member.guild.fetch_channel(logChannelId[0]) == None:
        con.close()
        return

    con.close()

    embed_log = discord.Embed(title="",  colour=0xf23f42)  ## Der Titel description="Beigetreten"
    embed_log.set_author(name="Reactionrole removed",icon_url=member.avatar)

    embed_log.add_field(name="Member:", value=str(member.name)+ "#" + str(member.discriminator))
    embed_log.add_field(name="Role", value="Removed <@&" + str(role.id) + ">")
    
    embed_log.set_footer(text="id: " + str(member.id) )  ## User ID und Datum

    ChannelToSend = await member.guild.fetch_channel(logChannelId[0])
    await ChannelToSend.send(embed=embed_log)  ## Sendet den Embed in den Channel der Eingestellt ist.

    return