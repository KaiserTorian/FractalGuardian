import sqlite3

## Speichert die User daten in der SqlFile wenn der user beitrit

async def SaveUserDataOnJoin(member,InviteUsed):
    
    try:
        con = sqlite3.connect("fractalData.db")
        cur = con.cursor()
        cur.execute("SELECT UserId FROM UserData WHERE GuildId=? and UserId=?",(member.guild.id,member.id))
        if cur.fetchone()!= None:
            cur.execute("UPDATE UserData SET InviteLinkUsed=? WHERE GuildId=? and UserId=?",(InviteUsed, member.guild.id, member.id))
            con.commit()
            con.close

            return #True
        
        cur.execute("INSERT INTO UserData VALUES(?, ?, ?, ?)",(member.name, member.id, member.guild.id, InviteUsed))
        con.commit()
        con.close

        return #True
    except Exception as e:
        print(e)
        print("Some thing went wrong while saving the User data.")
        return #False
    

## Löscht die UserData aus der sqlite3 File wenn der user den server verlässt

async def DeleteUserDataOnRemove(member):
    try:
        con = sqlite3.connect("fractalData.db")
        cur = con.cursor()
        
        cur.execute("DELETE from UserData WHERE UserId=? and GuildId=? ", (member.id, member.guild.id))
        con.commit()
        con.close
        
        return True
    except Exception as e:
        print(e)
        return False