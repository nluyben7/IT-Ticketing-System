import sqlite3
import bcrypt

DATABASE = 'IT_database.db'

seeded_tickets = [
    {
    "ticketer_name": "John Smith",
    "ticketer_email": "janedoe@quinndustries.com",
    "issue_type": "Hardware",
    "priority": "high",
    "summary": "office printer on floor 2 is jammed",
    "description": "The office printer on floor 2 is jammed, yada yada yada",
    "status": "unassigned",
    "resolution_details": None,
    "specialist_username_assigned": None,
    "submission_date": "2024-06-01T10:00:00Z",
    "assignment_date": None,
    "resolution_date": None
    },
    {
    "ticketer_name": "Sarah Connor",
    "ticketer_email": "sconnor@quinndustries.com",
    "issue_type": "hardware",
    "priority": "critical",
    "summary": "Laptop won't turn on",
    "description": "My laptop stopped turning on this morning. I tried holding the power button, unplugging and replugging the charger, but nothing works. The charging light doesn't even come on. I have a big presentation today.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "Apr 01, 2026  09:15 AM"
    },
    {
    "ticketer_name": "Miles Dyson",
    "ticketer_email": "mdyson@quinndustries.com",
    "issue_type": "hardware",
    "priority": "high",
    "summary": "Computer not powering on at all",
    "description": "Came into the office this morning and my desktop computer will not turn on. Pressed the power button multiple times, checked the power cable is plugged in. The monitor is fine. No lights or sounds from the tower at all.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "Apr 01, 2026  09:45 AM"
    },
    {
    "ticketer_name": "Tariq Farouk",
    "ticketer_email": "tfarouk@quinndustries.com",
    "issue_type": "hardware",
    "priority": "high",
    "summary": "Machine dead after power outage",
    "description": "After the power outage yesterday my workstation will not boot. I press the power button and nothing happens, no fans, no lights, nothing. I think the power supply may have been damaged by the surge.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "Apr 01, 2026  10:00 AM"
    },
    {
    "ticketer_name": "Linda Park",
    "ticketer_email": "lpark@quinndustries.com",
    "issue_type": "printer",
    "priority": "low",
    "summary": "Floor 3 printer not showing on network",
    "description": "The printer on floor 3 has disappeared from the list of available printers on my machine. Other people on my floor have the same issue. It was working fine last week. I tried restarting my computer but it did not come back.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "Apr 01, 2026  10:30 AM"
    },
    {
    "ticketer_name": "Doug Rattmann",
    "ticketer_email": "drattmann@quinndustries.com",
    "issue_type": "printer",
    "priority": "low",
    "summary": "Cannot find printer on floor 3",
    "description": "The floor 3 network printer has vanished from my printer list. I asked around and several colleagues have the same problem. Tried removing and re-adding the printer but it does not show up when searching the network.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "Apr 01, 2026  10:45 AM"
    },
    {
    "ticketer_name": "Ellen Ripley",
    "ticketer_email": "eripley@quinndustries.com",
    "issue_type": "security",
    "priority": "critical",
    "summary": "Suspicious login attempt on my account",
    "description": "I received an email alert saying someone tried to log into my account from an IP address in another country. I did not initiate this. I have already changed my password but wanted to flag it to IT immediately in case further action is needed.",
    "status": "active",
    "specialist_username_assigned": "asmith7",
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": "Apr 01, 2026  11:00 AM",
    "submission_date": "Apr 01, 2026  11:00 AM"
    },
    {
    "ticketer_name": "Peter Weyland",
    "ticketer_email": "pweyland@quinndustries.com",
    "issue_type": "security",
    "priority": "critical",
    "summary": "Account locked after suspicious activity",
    "description": "My account was locked this morning after several failed login attempts that I did not make. I received alerts about login attempts from an unrecognized location. I suspect my credentials may have been compromised.",
    "status": "active",
    "specialist_username_assigned": "bjones",
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": "Apr 01, 2026  11:15 AM",
    "submission_date": "Apr 01, 2026  12:15 AM"
    },
    {
    "ticketer_name": "Amanda Waller",
    "ticketer_email": "awaller@quinndustries.com",
    "issue_type": "software",
    "priority": "medium",
    "summary": "Excel keeps crashing on large files",
    "description": "Whenever I open our Q3 budget spreadsheet Excel freezes after about 30 seconds and then crashes entirely. I have tried reinstalling Office but the issue persists. This is blocking me from doing my end of month reporting.",
    "status": "resolved",
    "specialist_username_assigned": "asmith7",
    "resolution_details": "Updated Microsoft Office to the latest version and cleared the Excel temp files cache. Also increased the virtual memory allocation on the machine.",
    "resolution_date": "Apr 02, 2026  02:30 PM",
    "assignment_date": "Apr 01, 2026  01:00 PM",
    "submission_date": "Apr 01, 2026  01:00 PM"
    },
    {
    "ticketer_name": "Marcus Fenix",
    "ticketer_email": "mfenix@quinndustries.com",
    "issue_type": "software",
    "priority": "medium",
    "summary": "Office applications freezing and crashing",
    "description": "Word and Excel have both been crashing repeatedly today when working with larger documents. The applications freeze for a minute then close. I have tried restarting but the problem keeps coming back. I need these applications for daily work.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "Apr 02, 2026  09:00 AM"
    },
    {
    "ticketer_name": "Jill Valentine",
    "ticketer_email": "jvalentine@quinndustries.com",
    "issue_type": "software",
    "priority": "low",
    "summary": "VPN disconnects every 20 minutes",
    "description": "Since last Tuesday my VPN connection drops every 20 minutes while working remotely. I have to manually reconnect each time which is very disruptive to my workflow. I am on Windows 11 and using the standard company VPN client.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "Apr 02, 2026  10:00 AM"
    },
    {
    "ticketer_name": "John Smith",
    "ticketer_email": "janedoe@quinndustries.com",
    "issue_type": "Software",
    "priority": "high",
    "summary": "office printer on floor 5 is jammed",
    "description": "bugger is tricky, innit bro?",
    "status": "unassigned",
    "resolution_details": None,
    "specialist_username_assigned": None,
    "submission_date": "2024-06-01T10:00:00Z",
    "assignment_date": None,
    "resolution_date": None
    },
    {
    "ticketer_name": "Ellen Ripley",
    "ticketer_email": "eripley@quinndustries.com",
    "issue_type": "software",
    "priority": "medium",
    "summary": "Email client keeps crashing",
    "description": "My email application crashes every time I try to open a new message. Restarted my computer twice but the issue persists.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "Apr 02, 2026  11:20 AM"
},
{
    "ticketer_name": "Peter Parker",
    "ticketer_email": "pparker@quinndustries.com",
    "issue_type": "other",
    "priority": "low",
    "summary": "Slow internet connection",
    "description": "Internet speed has been unusually slow since yesterday afternoon. Pages take a long time to load and video calls are laggy.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "2026-04-02T14:05:00Z"
},
{
    "ticketer_name": "Bruce Wayne",
    "ticketer_email": "bwayne@quinndustries.com",
    "issue_type": "security",
    "priority": "critical",
    "summary": "Suspicious login detected",
    "description": "Received a notification about a login attempt from an unknown location. I did not initiate this login and would like my account secured immediately.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "Apr 03, 2026  08:10 AM"
},
{
    "ticketer_name": "Diana Prince",
    "ticketer_email": "dprince@quinndustries.com",
    "issue_type": "software",
    "priority": "high",
    "summary": "Cannot access shared drive",
    "description": "Attempting to access the shared team drive results in an access denied error. I had access previously.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "2026-04-03T09:30:00Z"
},
{
    "ticketer_name": "Tony Stark",
    "ticketer_email": "tstark@quinndustries.com",
    "issue_type": "hardware",
    "priority": "medium",
    "summary": "External monitor not detected",
    "description": "My laptop does not detect the external monitor when connected via HDMI. Tried different cables and ports.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "Apr 03, 2026  01:15 PM"
},
{
    "ticketer_name": "Natasha Romanoff",
    "ticketer_email": "nromanoff@quinndustries.com",
    "issue_type": "other",
    "priority": "high",
    "summary": "VPN connection failing",
    "description": "Unable to connect to the company VPN. It times out after entering credentials. Need access to internal systems urgently.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "2026-04-04T07:55:00Z"
},
{
    "ticketer_name": "Clark Kent",
    "ticketer_email": "ckent@quinndustries.com",
    "issue_type": "software",
    "priority": "low",
    "summary": "Spellcheck not working in Word",
    "description": "The spellcheck feature in Microsoft Word is not highlighting any mistakes. Tried enabling settings but no change.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "Apr 04, 2026  10:40 AM"
},
{
    "ticketer_name": "Leia Organa",
    "ticketer_email": "lorgana@quinndustries.com",
    "issue_type": "hardware",
    "priority": "medium",
    "summary": "Keyboard keys sticking",
    "description": "Several keys on my keyboard are sticking and sometimes do not register when pressed. This is slowing down my work significantly.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "2026-04-04T13:25:00Z"
},
{
    "ticketer_name": "Michael Scott",
    "ticketer_email": "mscott@quinndustries.com",
    "issue_type": "printer",
    "priority": "high",
    "summary": "Printer printing blank pages",
    "description": "Office printer is printing completely blank pages even though the toner was recently replaced.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "Apr 05, 2026  09:05 AM"
},
{
    "ticketer_name": "Dwight Schrute",
    "ticketer_email": "dschrute@quinndustries.com",
    "issue_type": "security",
    "priority": "medium",
    "summary": "Password reset not working",
    "description": "Attempted to reset my password but never received the reset email. Checked spam folder as well.",
    "status": "unassigned",
    "specialist_username_assigned": None,
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": None,
    "submission_date": "2026-04-05T10:22:00Z"
},
{
    "ticketer_name": "Jean-Luc Picard",
    "ticketer_email": "jpicard@quinndustries.com",
    "issue_type": "software",
    "priority": "high",
    "summary": "CRM application freezing during use",
    "description": "The CRM app freezes whenever I try to update customer records. This started happening after the latest update.",
    "status": "in_progress",
    "specialist_username_assigned": "tech_jdoe",
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": "2026-04-06T10:15:00Z",
    "submission_date": "2026-04-06T09:40:00Z"
},
{
    "ticketer_name": "Hermione Granger",
    "ticketer_email": "hgranger@quinndustries.com",
    "issue_type": "hardware",
    "priority": "medium",
    "summary": "Laptop overheating frequently",
    "description": "My laptop fan is constantly running and the device gets very hot after only 15 minutes of use.",
    "status": "assigned",
    "specialist_username_assigned": "tech_asmith",
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": "Apr 06, 2026  01:05 PM",
    "submission_date": "Apr 06, 2026  12:10 PM"
},
{
    "ticketer_name": "Frodo Baggins",
    "ticketer_email": "fbaggins@quinndustries.com",
    "issue_type": "printer",
    "priority": "low",
    "summary": "Printer duplex not working",
    "description": "The printer no longer prints double-sided even when the setting is enabled.",
    "status": "resolved",
    "specialist_username_assigned": "tech_jdoe",
    "resolution_details": "Updated printer driver and reset duplex settings. Test prints successful.",
    "resolution_date": "2026-04-07T11:20:00Z",
    "assignment_date": "2026-04-07T09:00:00Z",
    "submission_date": "2026-04-07T08:30:00Z"
},
{
    "ticketer_name": "Katniss Everdeen",
    "ticketer_email": "keverdeen@quinndustries.com",
    "issue_type": "security",
    "priority": "critical",
    "summary": "Account locked after multiple login attempts",
    "description": "My account has been locked after several failed login attempts that I did not make.",
    "status": "resolved",
    "specialist_username_assigned": "sec_admin1",
    "resolution_details": "Account unlocked and password reset. Enabled multi-factor authentication for additional security.",
    "resolution_date": "Apr 07, 2026  02:45 PM",
    "assignment_date": "Apr 07, 2026  01:10 PM",
    "submission_date": "Apr 07, 2026  12:55 PM"
},
{
    "ticketer_name": "Luke Skywalker",
    "ticketer_email": "lskywalker@quinndustries.com",
    "issue_type": "other",
    "priority": "medium",
    "summary": "Unable to access internal wiki",
    "description": "Receiving a 403 error when trying to access the internal knowledge base.",
    "status": "in_progress",
    "specialist_username_assigned": "tech_mchan",
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": "2026-04-08T09:10:00Z",
    "submission_date": "2026-04-08T08:50:00Z"
},
{
    "ticketer_name": "Tony Soprano",
    "ticketer_email": "tsoprano@quinndustries.com",
    "issue_type": "hardware",
    "priority": "high",
    "summary": "Desktop randomly shutting down",
    "description": "My desktop computer shuts down without warning multiple times a day.",
    "status": "assigned",
    "specialist_username_assigned": "tech_rrossi",
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": "Apr 08, 2026  11:30 AM",
    "submission_date": "Apr 08, 2026  10:05 AM"
},
{
    "ticketer_name": "Arya Stark",
    "ticketer_email": "astark@quinndustries.com",
    "issue_type": "software",
    "priority": "low",
    "summary": "Calendar events not syncing",
    "description": "My calendar events are not syncing between desktop and mobile devices.",
    "status": "resolved",
    "specialist_username_assigned": "tech_asmith",
    "resolution_details": "Reconfigured sync settings and re-authenticated account. Sync now working across devices.",
    "resolution_date": "2026-04-09T10:05:00Z",
    "assignment_date": "2026-04-09T09:15:00Z",
    "submission_date": "2026-04-09T08:40:00Z"
},
{
    "ticketer_name": "Gordon Freeman",
    "ticketer_email": "gfreeman@quinndustries.com",
    "issue_type": "hardware",
    "priority": "medium",
    "summary": "USB ports not functioning",
    "description": "None of the USB ports on my workstation are recognizing devices.",
    "status": "in_progress",
    "specialist_username_assigned": "tech_jdoe",
    "resolution_details": None,
    "resolution_date": None,
    "assignment_date": "2026-04-09T11:25:00Z",
    "submission_date": "2026-04-09T10:50:00Z"
}
]
#dummy accounts
seeded_it_accounts = [
    {
    "username": "asmith7",
    "hashed_password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()),
    "name": "Alice Smith"
    },
    {
    "username": "bjones",
    "hashed_password": bcrypt.hashpw("password456".encode('utf-8'), bcrypt.gensalt()),
    "name": "Bob Jones"
    },
    {
    "username": "charlie.reed",
    "hashed_password": bcrypt.hashpw("password789".encode('utf-8'), bcrypt.gensalt()),
    "name": "Charlie Reed"
    }
]


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute('''DROP TABLE IF EXISTS tickets''')
    db.execute(''' CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticketer_name TEXT NOT NULL,
            ticketer_email TEXT NOT NULL,
            issue_type TEXT NOT NULL,
            priority TEXT,
            summary TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            resolution_details TEXT,
            specialist_username_assigned TEXT,
            submission_date TEXT NOT NULL,
            assignment_date TEXT,
            resolution_date TEXT   
            )  
            ''')
    db.execute('''DROP TABLE IF EXISTS it_specialists''')
    db.execute(''' CREATE TABLE IF NOT EXISTS it_specialists (
            username TEXT PRIMARY KEY,
            hashed_password TEXT NOT NULL,
            name TEXT NOT NULL,
            tickets_claimed INTEGER DEFAULT 0,
            tickets_active INTEGER DEFAULT 0,
            tickets_resolved INTEGER DEFAULT 0,
            total_resolution_time_hours REAL DEFAULT 0
            )  
            ''')
    db.execute('''CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status) ''')
    db.execute('''CREATE INDEX IF NOT EXISTS idx_tickets_specialist ON tickets(specialist_username_assigned) ''')
    db.execute('''CREATE INDEX IF NOT EXISTS idx_tickets_issue_type ON tickets(issue_type) ''')
    db.execute('''CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority) ''')
    
    #TO DO: add index on status (and other fields)
    db.commit()
    db.close()


def seed_db():
    db = get_db()
    existing_ticket_count = db.execute('SELECT COUNT(*) FROM tickets').fetchone()[0]
    if existing_ticket_count > 0:
        print(f"Database already has {existing_ticket_count} tickets. Skipping seeding.")
        db.close()
        return
    for ticket in seeded_tickets:
        db.execute('''INSERT OR REPLACE INTO tickets (ticketer_name, ticketer_email, issue_type, priority, summary, description, status, resolution_details, specialist_username_assigned, submission_date, assignment_date, resolution_date)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            ticket["ticketer_name"],
            ticket["ticketer_email"],
            ticket["issue_type"],
            ticket["priority"],
            ticket["summary"],
            ticket["description"],
            ticket["status"],
            ticket.get("resolution_details"),
            ticket.get("specialist_username_assigned"),
            ticket.get("submission_date"),
            ticket.get("assignment_date"),
            ticket.get("resolution_date")
        ))

    for it_account in seeded_it_accounts:
        db.execute('''INSERT INTO it_specialists
                   (username, hashed_password, name)
                   VALUES (?,?,?) ''',(
            it_account["username"],
            it_account["hashed_password"],
            it_account["name"]
        ))
    db.commit()
    db.close()
    print(f"Database seeded with {len(seeded_tickets)} tickets and {len(seeded_it_accounts)} accounts.")


    