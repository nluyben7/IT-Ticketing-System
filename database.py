import sqlite3

DATABASE = 'IT_database.db'

seeded_database = [
    {
    "ticketer_name": "John Smith",
    "ticketer_email": "janedoe@quinndustries.com",
    "issue_type": "Hardware",
    "priority": "high",
    "summary": "office printer on floor 2 is jammed",
    "description": "The office printer on floor 2 is jammed, yada yada yada",
    "status": "unassigned",
    "resolution_details": None,
    "specialist_assigned": None,
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
    "specialist_assigned": None,
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
    "specialist_assigned": None,
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
    "specialist_assigned": None,
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
    "specialist_assigned": None,
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
    "specialist_assigned": None,
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
    "specialist_assigned": "alice",
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
    "specialist_assigned": "bob",
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
    "specialist_assigned": "alice",
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
    "specialist_assigned": None,
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
    "specialist_assigned": None,
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
    "specialist_assigned": None,
    "submission_date": "2024-06-01T10:00:00Z",
    "assignment_date": None,
    "resolution_date": None
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
            specialist_assigned TEXT,
            submission_date TEXT NOT NULL,
            assignment_date TEXT,
            resolution_date TEXT   
            )  
            ''')
    db.commit()
    db.close()


def seed_db():
    db = get_db()
    existing_ticket_count = db.execute('SELECT COUNT(*) FROM tickets').fetchone()[0]
    if existing_ticket_count > 0:
        print(f"Database already has {existing_ticket_count} tickets. Skipping seeding.")
        db.close()
        return
    for ticket in seeded_database:
        db.execute('''INSERT OR REPLACE INTO tickets (ticketer_name, ticketer_email, issue_type, priority, summary, description, status, resolution_details, specialist_assigned, submission_date, assignment_date, resolution_date)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            ticket["ticketer_name"],
            ticket["ticketer_email"],
            ticket["issue_type"],
            ticket["priority"],
            ticket["summary"],
            ticket["description"],
            ticket["status"],
            ticket.get("resolution_details"),
            ticket.get("specialist_assigned"),
            ticket.get("submission_date"),
            ticket.get("assignment_date"),
            ticket.get("resolution_date")
        ))
    db.commit()
    db.close()
    print(f"Database seeded with {len(seeded_database)} tickets.")


    