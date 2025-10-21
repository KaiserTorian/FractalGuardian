import sqlite3

def add_column_if_not_exists(cursor, table_name, column_name, column_type):
    # Überprüfe, ob die Spalte bereits existiert
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    if column_name not in column_names:
        # Füge die Spalte hinzu, wenn sie nicht existiert
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")



def dataBaseInit():

    # Verbindung zur Datenbank herstellen (falls nicht vorhanden, wird sie erstellt)
    conn = sqlite3.connect('fractalData.db')
    cursor = conn.cursor()

    # Tabelle InviteLinks erstellen, wenn nicht vorhanden
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS InviteLinks (
            GuildId INTEGER,
            InviteId TEXT PRIMARY KEY,
            InviteName TEXT,
            InviteUses INTEGER,
            InviteMaxUses INTEGER,
            InviteExpires INTEGER,
            InviterId TEXT,
            InviterName TEXT
        )
    """)

    # Tabelle InviteLinksArchive erstellen, wenn nicht vorhanden
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS InviteLinksArchive (
            GuildId INTEGER,
            InviteId TEXT PRIMARY KEY,
            InviteName TEXT,
            InviteUses INTEGER,
            InviteMaxUses INTEGER,
            InviteExpires INTEGER,
            InviterId TEXT,
            InviterName TEXT,
            ArchiveDate INTEGER
        )
    """)

    # Tabelle AutoRoles erstellen, wenn nicht vorhanden
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AutoRoles (
            GuildId INTEGER,
            RoleId INTEGER,
            OnJoin INTEGER,
            DefaultRole INTEGER
        )
    """)


    # Alles für die Log UserData
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserData (
            UserName TEXT,
            UserId INTEGER,
            GuildId INTEGER,
            InviteLinkUsed TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserActivity (
            GuildId INTEGER,
            UserId INTEGER,
            HourTimestamp TEXT,
            Points INTEGER,
            ChannelUsed INTEGER,
            ActivityType INTEGER
        )   
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ChannelActivityMinutes (
            GuildId INTEGER,
            ChannelId INTEGER,
            ActivBegin INTEGER,
            ActivEnd INTEGER
        )   
    """)

    # Alles für die Log Channels
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS LogChannels (
            GuildId INTEGER,
            LogEvent TEXT,
            ChannelId INTEGER
        )
    """)

    # Alles für die ReactionRoles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ReactionRoles (
            RowId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            GuildId INTEGER,
            ChannelId INTEGER,
            MessageId INTEGER,
            Emoji INTEGER,
            RoleId INTEGER,
            MessageType TEXT
        )
    """)

    #Activity Rollen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ActivityRoles (
            RowId INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            GuildId TEXT,
            RoleId TEXT,
            ActivityType TEXT,
            ActivationType TEXT
            RoleId INTEGER,
            TopMin INTEGER,
            BottomMax INTEGER
        )
    """)
    

   

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()

    