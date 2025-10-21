
import time
import sqlite3
import discord


#Sucht den Invite link der beim Join eines Useres genutzt wurde. 

async def findInviteOnUserJoin(member: discord.Member):
    inviteLink = None
    
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()
    cur.execute("SELECT InviteId, InviteUses, InviteMaxUses, InviteExpires FROM InviteLinks WHERE GuildId=?",(member.guild.id,))
    savedInviteLinks = cur.fetchall()
    
    guildInvLinksList = []
   
    for savedInviteLink in savedInviteLinks: #geht alle gespeicherten invite Links durch

        for guildInvLinks in await member.guild.invites(): #geht alle invite links von discord durch.
            guildInvLinksList.append(guildInvLinks.id)#speichert die id der Invite links in einer liste.

            #Ist der link der gleiche und passen die uses nicht zusammen 
            if guildInvLinks.id == savedInviteLink[0] and guildInvLinks.uses > savedInviteLink[1] :
                return guildInvLinks.id
                
        #Wenn kein Link gefunden wurde sucht er links die es nicht mehr gibt weil bei persönichen einladungen werden nacher die links gleich geloscht
        if not savedInviteLink[0] in guildInvLinksList:
            return savedInviteLink[0]
                
    return None






##Wenn der bot startet dann Updated er die InviteLink Databais 
async def InviteUpdateOnStartUp(bot):
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()
    guilds = bot.guilds
    
    for guild in guilds:
        
        print("update_invite_start " + str(guild.id))

        invite_list = await guild.invites() ## Holt sich alle invite links die es auf dem Server gibt.
        print(type(guild.id))
        cur.execute("SELECT InviteId FROM InviteLinks WHERE GuildId=?",(guild.id,))
        saved_invites = cur.fetchall() ## Holt sich alle gespeicherten Invite links

        saved_invite_code = []
        for saved_invite in saved_invites: ## Macht eine Liste mit allen Codes die Gespeichert sind um sie besser vergleichen zu können.
            saved_invite_code.append(str(saved_invite[0]))

        invite_list_code = []
        for invite in invite_list:  ## Macht eine Liste mita allen Codes die Gespeichert sind um sie besser vergleichen zu können.
            invite_list_code.append(str(invite.code))

        for invite in invite_list:
            inviterName = str(invite.inviter.name)
            if invite.inviter.discriminator != "0":
                inviterName = str(invite.inviter)
            if invite.code in saved_invite_code: ## Wenn der Link existiert dann Updated er die Uses
                cur.execute("UPDATE InviteLinks SET InviteUses = ?, InviteMaxUses = ?, InviteExpires = ?, InviterId= ?, InviterName= ? WHERE InviteId = ? and Guildid = ?",(invite.uses,invite.max_uses,invite.expires_at,invite.inviter.id,inviterName,invite.code,guild.id))
                con.commit()
            else: ## Wenn der Link nicht existiert dann erstellt speichert er es.
                print(invite.code)
                print(saved_invite_code)
                cur.execute("INSERT INTO InviteLinks VALUES(?, ?, ?, ?, ?, ?, ?, ?)",(guild.id, invite.code, None, invite.uses, invite.max_uses, invite.expires_at, str(invite.inviter.id), str(inviterName)))
                con.commit()

        for saved_invite in saved_invite_code:
            if not saved_invite in invite_list_code: ## Wenn der Link nicht mehr existiert löscht er den eintrag in sql.

                cur.execute("SELECT * FROM InviteLinks WHERE InviteId = '" + str(saved_invite) + "' and  GuildId = '" + str(guild.id) + "'")
                inviteLink = cur.fetchone()

                cur.execute("INSERT INTO InviteLinksArchive VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",(inviteLink[0], inviteLink[1], inviteLink[2], inviteLink[3], inviteLink[4], inviteLink[5], inviteLink[6], inviteLink[7],time.time()))
                con.commit()

                cur.execute("DELETE from InviteLinks WHERE InviteId = '" + str(saved_invite) + "' and  GuildId = '" + str(guild.id) + "'")
                con.commit()

                    

    cur.close()


#Speichert den erstellten Invite link in die SQL Tabelle return success
async def InviteUpdateOnCreate(invite: discord.Invite):
    """return success"""
    try:
        con = sqlite3.connect("fractalData.db")
        cur = con.cursor()
        guild= invite.guild
        if invite.inviter.discriminator == "0":
             cur.execute("INSERT INTO InviteLinks VALUES(?, ?, ?, ?, ?, ?, ?, ?)",(guild.id, invite.code, None, invite.uses, invite.max_uses, invite.expires_at, str(invite.inviter.id), str(invite.inviter.name)))
        else:
            cur.execute("INSERT INTO InviteLinks VALUES(?, ?, ?, ?, ?, ?, ?, ?)",(guild.id, invite.code, None, invite.uses, invite.max_uses, invite.expires_at, str(invite.inviter.id), str(invite.inviter)))
        con.commit()
        return True
    except:
        return False



#Löscht den gerade gelöschten Invite link und speichert ihn in im Archiv \nreturn success
async def InviteUpdateOnDelete(invite: discord.Invite):
    """return success"""
    try:
        con = sqlite3.connect("fractalData.db")
        cur = con.cursor()
        guild= invite.guild

        cur.execute("SELECT * FROM InviteLinks WHERE InviteId =`? and  GuildId = ?",(invite.id, guild.id))
        inviteLink = cur.fetchone()

        cur.execute("INSERT INTO InviteLinksArchive VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",(inviteLink[0], inviteLink[1], inviteLink[2], inviteLink[3], inviteLink[4], inviteLink[5], inviteLink[6], inviteLink[7], time.time()))
        con.commit()

        cur.execute("DELETE from InviteLinks WHERE InviteId = ? and  GuildId = ?",(invite.id, guild.id))
        con.commit()
        return True
    except:
        return False
    


async def InviteUpdateOnUserJoin(member: discord.Member,inviteLinkUsed):
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()
    guild = member.guild

    print("update_invite_join" + str(guild.id))

    invite_list = await guild.invites() ## Holt sich alle invite links die es auf dem Server gibt.
    print(type(guild.id))
    cur.execute("SELECT InviteId FROM InviteLinks WHERE GuildId=?",(guild.id,))
    saved_invites = cur.fetchall() ## Holt sich alle gespeicherten Invite links

    saved_invite_code = []
    for saved_invite in saved_invites: ## Macht eine Liste mit allen Codes die Gespeichert sind um sie besser vergleichen zu können.
        saved_invite_code.append(str(saved_invite[0]))

    invite_list_code = []
    for invite in invite_list:  ## Macht eine Liste mit allen Codes die Gespeichert sind um sie besser vergleichen zu können.
        invite_list_code.append(str(invite.code))

    for invite in invite_list:
        inviterName = str(invite.inviter.name)
        if invite.inviter.discriminator != "0":
            inviterName = str(invite.inviter)
        if invite.code in saved_invite_code: ## Wenn der Link existiert dann Updated er die Uses
            cur.execute("UPDATE InviteLinks SET InviteUses = ?, InviteMaxUses = ?, InviteExpires = ?, InviterId= ?, InviterName= ? WHERE InviteId = ? and Guildid = ?",(invite.uses,invite.max_uses,invite.expires_at,invite.inviter.id,inviterName,invite.code,guild.id))
            con.commit()
        else: ## Wenn der Link nicht existiert dann erstellt speichert er es.
            cur.execute("INSERT INTO InviteLinks VALUES(?, ?, ?, ?, ?, ?, ?, ?)",(guild.id, invite.code, None, invite.uses, invite.max_uses, invite.expires_at, str(invite.inviter.id), str(inviterName)))
            con.commit()

    for saved_invite in saved_invite_code:
        if not saved_invite in invite_list_code: ## Wenn der Link nicht mehr existiert löscht er den eintrag in sql.
            
            cur.execute("SELECT * FROM InviteLinks WHERE InviteId = ? and  GuildId = ?",(saved_invite, guild.id))
            inviteLink = cur.fetchone()
         
            cur.execute("INSERT INTO InviteLinksArchive VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",(inviteLink[0], inviteLink[1], inviteLink[2], inviteLink[3], inviteLink[4], inviteLink[5], inviteLink[6], inviteLink[7],time.time()))
            con.commit()

            cur.execute("DELETE from InviteLinks WHERE InviteId = ? and  GuildId = ?",(saved_invite, guild.id))
            con.commit()

    cur.close()