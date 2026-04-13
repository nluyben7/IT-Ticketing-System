from flask import Flask, request, render_template, jsonify, session
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import heapq
from email_notifier import EmailNotifier



app = Flask(__name__)
app.secret_key = "supersecretkey"  # In production, use a secure random key and keep it secret

email_notifier = EmailNotifier()

IT_ACCOUNTS = {
    "alice": "password123",
    "bob": "password456",
    "charlie": "password789"
}
next_id = 11
database = [
    {
    "id": 0,
    "ticketer_name": "John Smith",
    "email": "janedoe@quinndustries.com",
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
        "id": 1,
        "ticketer_name": "Sarah Connor",
        "email": "sconnor@quinndustries.com",
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
        "id": 2,
        "ticketer_name": "Miles Dyson",
        "email": "mdyson@quinndustries.com",
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
        "id": 3,
        "ticketer_name": "Tariq Farouk",
        "email": "tfarouk@quinndustries.com",
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
        "id": 4,
        "ticketer_name": "Linda Park",
        "email": "lpark@quinndustries.com",
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
        "id": 5,
        "ticketer_name": "Doug Rattmann",
        "email": "drattmann@quinndustries.com",
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
        "id": 6,
        "ticketer_name": "Ellen Ripley",
        "email": "eripley@quinndustries.com",
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
        "id": 7,
        "ticketer_name": "Peter Weyland",
        "email": "pweyland@quinndustries.com",
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
        "id": 8,
        "ticketer_name": "Amanda Waller",
        "email": "awaller@quinndustries.com",
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
        "id": 9,
        "ticketer_name": "Marcus Fenix",
        "email": "mfenix@quinndustries.com",
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
        "id": 10,
        "ticketer_name": "Jill Valentine",
        "email": "jvalentine@quinndustries.com",
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
    "id": 9999,
    "ticketer_name": "John Smith",
    "email": "janedoe@quinndustries.com",
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



#----------------------------- SIMILAR TICKETS FINDING -----------------------------
def formatTicketText(ticket):
    text = ticket["summary"] + " " + ticket["description"]
    if ticket.get("resolution_details"):
        text += " " + ticket["resolution_details"]
    return text

def findSimilarTickets(ticket, number_of_similar=3, threshold=0.1):
    
    candidates = [ t for t in database if t["id"] != ticket["id"]]
    if not candidates:
        return []
    target_text = formatTicketText(ticket)
    candidate_texts = [formatTicketText(t) for t in candidates]

    vectorizer = TfidfVectorizer(stop_words='english')
    matrix = vectorizer.fit_transform([target_text] + candidate_texts)
    scores = cosine_similarity(matrix[0], matrix[1:]).flatten()

    closest_tickets = heapq.nlargest(number_of_similar, zip(candidates, scores), key=lambda x: x[1])
    return [ticket for ticket, score in closest_tickets if score >= threshold]

def searchTickets(query):
    pseudo_ticket = {
        "id": -1,
        "ticketer_name": "",
        "email": "",
        "issue_type": "",
        "priority": "",
        "summary": query,
        "description": "",
        "status": "",
        "resolution_details": None,
        "specialist_assigned": None,
        "submission_date": None,
    }
    return findSimilarTickets(pseudo_ticket, number_of_similar=len(database), threshold=0.05)

# ----------------------------- SIMILAR TICKETS FINDING END -----------------------------


@app.route('/')
def home():
    return render_template('ticket_submission.html')

# --------------------------------- AUTHORIZATION HANDLING ---------------------------------

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    body  = request.get_json()
    if not body or not body.get("password") or not body.get("username"):
        return jsonify({"error": "username and password are required"}), 401
    if body["username"] not in IT_ACCOUNTS or IT_ACCOUNTS[body["username"]] != body["password"]:
        return jsonify({"error": "incorrect username or password"}), 401
    
    session["is_it_department"] = True
    session["username"] = body["username"]
    return jsonify({"message": "login successful"}), 200

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "logged out"}), 200 

def it_only_check():
    if not session.get("is_it_department"):
        return jsonify({"error": "unauthorized"}), 403
    return None

# --------------------------------- AUTHORIZATION HANDLING END ---------------------------------

#----------------------------- TICKET VIEWING AND CREATION ENDPOINTS -----------------------------
@app.route('/tickets', methods=['GET'])
def getTickets():
    auth_error = it_only_check()
    if auth_error:
        return auth_error
    return jsonify(database), 200

@app.route('/tickets/view', methods=['GET'])
def viewTickets():
    auth_error = it_only_check()
    if auth_error:
        return render_template("login.html")  
    
     
    return render_template("tickets.html", tickets=database)

@app.route('/tickets/view/<int:ticket_id>', methods=['GET'])
def viewTicketById(ticket_id):
    ticket = next((t for t in database if t["id"] == ticket_id), None)
    if not ticket:
        return f"<p>Ticket #{ticket_id} not found. <a href='/tickets/view'>Go back</a></p>", 404
    ref= request.args.get("ref", "tickets")
    query = request.args.get("q", "")

    return render_template("ticket_details.html", ticket=ticket, ref=ref, query=query, related_tickets=findSimilarTickets(ticket))

@app.route('/tickets', methods=['POST'])
def createTicket():
    global next_id
    body = request.get_json()
    required_fields = ["ticketer_name","email","issue_type", "summary", "description"]

    #input checking
    if not body or not all( field in body for field in required_fields):
        return jsonify({"error": "ticketer_name, email, issue_type, priority, summary, and description are all required fields"}), 400
    if not all(body[field].strip() for field in required_fields):
        return jsonify({"error": "fields cannot be empty"}), 400
    # if body["priority"] not in ["low","medium","high", "critical"]:
    #     return jsonify({"error": "importance must be low, medium, high, or critical"}), 400

    #adding entry
    new_ticket = {
        "id": next_id,
        "ticketer_name": body["ticketer_name"],
        "email": body["email"],
        "issue_type": body["issue_type"],
        "priority": None,
        "summary": body["summary"],
        "status": "unassigned",
        "description": body["description"],
        "submission_date": datetime.now().strftime("%b %d, %Y  %H:%M"),
    }
    next_id += 1
    database.append(new_ticket)

    email_notifier.notify_async(new_ticket, "submission")
    return jsonify(new_ticket), 201

#----------------------------- TICKET VIEWING AND CREATION ENDPOINTS END -----------------------------

#----------------------------- TICKET UPDATING ENDPOINTS -----------------------------

def claimTicket(ticket_id, priority):
    if not priority:
        return jsonify({"error": "setting priority is required to claim a ticket"}), 400
    ticket = next((t for t in database if t["id"] == ticket_id), None)
    if not ticket:
        return jsonify({"error": "ticket not found"}), 404
    if ticket.get("status") == "resolved":
        return jsonify({"error": "ticket already resolved"}), 400
    if ticket.get("status") == "active":
        return jsonify({"error": "ticket is already active"}), 400
    

    ticket["status"] = "active"
    ticket["priority"] = priority 
    ticket["specialist_assigned"] = session.get("username")  
    ticket["assignment_date"] = datetime.now().strftime("%b %d, %Y  %H:%M")

    email_notifier.notify_async(ticket, "assignment")
    return jsonify({"message" : f"ticket {ticket_id} claimed and now active"}), 200
    
def resolveTicket(ticket_id, resolution_details):
    if not resolution_details:
        return jsonify({"error": "resolution_details are required to resolve a ticket"}), 400
    ticket = next((t for t in database if t["id"] == ticket_id), None)
    if not ticket:
        return jsonify({"error": "ticket not found"}), 404
    if ticket.get("status") == "resolved":
        return jsonify({"error": "ticket already resolved"}), 400
    if ticket.get("status") != "active":
        return jsonify({"error": "only active tickets can be resolved"}), 400
    
    ticket["status"] = "resolved"
    ticket["resolution_details"] = resolution_details
    ticket["resolution_date"] = datetime.now().strftime("%b %d, %Y  %H:%M")

    email_notifier.notify_async(ticket, "resolution")
    return jsonify({"message" : f"ticket {ticket_id} resolved"}), 200


def changeTicketStatus(ticket_id, new_status, resolution_details, priority):
    if new_status not in ["unassigned", "active", "resolved"]:
        return jsonify({"error": "new_status must be unassigned, active, or resolved"}), 400
    if new_status == "unassigned":
        return jsonify({"error": "ticket cant be unassigned from active or resolved"}), 400
    if new_status == "active":
        return claimTicket(ticket_id, priority)
    if new_status == "resolved":
        return resolveTicket(ticket_id, resolution_details)
    return jsonify({"error": "unhandled status"}), 400


def changePriority(ticket_id, new_priority):
    ticket = next((t for t in database if t["id"] == ticket_id), None)
    if not ticket:
        return jsonify({"error": "ticket not found"}), 404

    if not new_priority:
        return jsonify({"error" : "priority is required"}), 400
    if new_priority not in ["low","medium","high","critical"]:
        return jsonify({"error" : "priority must be low, medium, high, or critical"}), 400
    if ticket.get("status") != "active":
        return jsonify({"error": "only active tickets can have their priority updated"}), 400
    
    ticket["priority"] = new_priority
    return jsonify(ticket), 200
    

@app.route('/tickets/<int:ticket_id>', methods=['PATCH'])
def updateTicket(ticket_id):
    auth_error = it_only_check()
    if auth_error:
        return auth_error
    
    body = request.get_json()
    if not body:
        return jsonify({"error": "body is required"}), 400
    
    if "new_status" in body:
        return changeTicketStatus(ticket_id, body["new_status"], body.get("resolution_details", None), body.get("priority", None))
    if "priority" in body:
        return changePriority(ticket_id, body["priority"])
    return jsonify({"error": "need details in body to update ticket"}), 400
    #----------------------------- TICKET UPDATING ENDPOINTS END -----------------------------


#----------------------------- SEARCH ENDPOINTS -----------------------------
@app.route('/tickets/search', methods=['GET'])
def searchTicketsRoute():
    auth_error = it_only_check()
    if auth_error:
        return auth_error
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "query parameter q is required"}), 400
    results = searchTickets(query)
    return render_template("search.html", tickets=results, query=query), 200



#----------------------------- SEARCH ENDPOINTS END -----------------------------



if __name__ == '__main__':
    app.run(debug=True)
