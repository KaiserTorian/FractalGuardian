import sqlite3


from func.ActivityManager import ActivityHelperFunctions as AHT

#Gibt dem Mmeber ein Text Point wenn er eine nachricht schreibt.
async def UserTextActivity(message):
    if message.content == None or message.content == "":
        return
    member = message.author
    guild = member.guild

    hourTimestamp = await AHT.utc_timestamp_beginning_of_hour()
    con = sqlite3.connect("fractalData.db")
    cur = con.cursor()

    cur.execute("SELECT Points FROM UserActivity WHERE GuildId=? and UserId=? and HourTimestamp=? and ChannelUsed=? and ActivityType=?",(guild.id, member.id, hourTimestamp, message.channel.id, 1))
    userTextPoints = cur.fetchone()
    print(userTextPoints)

    if userTextPoints != None:
        cur.execute("UPDATE UserActivity SET Points=? WHERE GuildId=? and UserId=? and HourTimestamp=? and ChannelUsed=? and ActivityType=?",(int(userTextPoints[0]) + 1,guild.id, member.id, hourTimestamp,message.channel.id, 1))
        
    else:
        cur.execute("INSERT INTO UserActivity VALUES(?, ?, ?, ?, ?, ?)",(guild.id, member.id, hourTimestamp, 1, message.channel.id, 1))
       
    con.commit()
    con.close
    return