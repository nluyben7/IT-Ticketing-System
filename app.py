from flask import Flask, request, render_template, jsonify, session
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import heapq
from email_notifier import EmailNotifier

from database import get_db, init_db, seed_db


app = Flask(__name__)
app.secret_key = "supersecretkey"  # In production, use a secure random key and keep it secret

email_notifier = EmailNotifier()
init_db()
seed_db()
IT_ACCOUNTS = {
    "alice": "password123",
    "bob": "password456",
    "charlie": "password789"
}


#----------------------------- SIMILAR TICKETS FINDING -----------------------------
def formatTicketText(ticket):
    text = ticket["summary"] + " " + ticket["description"]
    if ticket["resolution_details"]:
        text += " " + ticket["resolution_details"]
    return text

def findSimilarTickets(ticket, number_of_similar=3, threshold=0.1):
    db = get_db()
    candidates = db.execute('SELECT * FROM tickets WHERE id != ?', (ticket["id"],)).fetchall()
    db.close()
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
    db = get_db()
    total_count = db.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    db.close()
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
    return findSimilarTickets(pseudo_ticket, number_of_similar=total_count, threshold=0.05)

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
    db = get_db()
    tickets = db.execute('SELECT * FROM tickets').fetchall()
    db.close()
    return jsonify([dict(t) for t in tickets]), 200

@app.route('/tickets/view', methods=['GET'])
def viewTickets():
    auth_error = it_only_check()
    if auth_error:
        return render_template("login.html")  
    db = get_db()
    tickets = db.execute('SELECT * FROM tickets').fetchall()
    db.close()
    return render_template("tickets.html", tickets=[dict(t) for t in tickets])

@app.route('/tickets/view/<int:ticket_id>', methods=['GET'])
def viewTicketById(ticket_id):
    auth_error = it_only_check()
    if auth_error:
        return auth_error
    db = get_db()
    ticket = db.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    db.close()
    if not ticket:
        return f"<p>Ticket #{ticket_id} not found. <a href='/tickets/view'>Go back</a></p>", 404

    return render_template("ticket_details.html", ticket=dict(ticket), related_tickets=findSimilarTickets(dict(ticket)))

@app.route('/tickets', methods=['POST'])
def createTicket():
    body = request.get_json()
    required_fields = ["ticketer_name","ticketer_email","issue_type", "summary", "description"]

    #input checking
    if not body or not all( field in body for field in required_fields):
        return jsonify({"error": "ticketer_name, ticketer_email, issue_type, summary, and description are all required fields"}), 400
    if not all(body[field].strip() for field in required_fields):
        return jsonify({"error": "fields cannot be empty"}), 400

    db = get_db()
    cursor = db.execute('''INSERT INTO tickets (ticketer_name, ticketer_email, issue_type, summary, description, status, submission_date)
               VALUES (?, ?, ?, ?, ?, 'unassigned', ?)''', (body["ticketer_name"], body["ticketer_email"], body["issue_type"], body["summary"], body["description"], datetime.now().strftime("%b %d, %Y  %H:%M")))
    db.commit()
    new_ticket = dict(db.execute('SELECT * FROM tickets WHERE id = ?', (cursor.lastrowid,)).fetchone())

    email_notifier.notify_async(new_ticket, "submission")
    return jsonify(new_ticket), 201 

#----------------------------- TICKET VIEWING AND CREATION ENDPOINTS END -----------------------------

#----------------------------- TICKET UPDATING ENDPOINTS -----------------------------

def claimTicket(ticket_id, priority):
    if not priority:
        return jsonify({"error": "setting priority is required to claim a ticket"}), 400
    
    db = get_db()
    ticket = dict(db.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone())

    if not ticket:
        db.close()
        return jsonify({"error": "ticket not found"}), 404
    if ticket.get("status") == "resolved":
        db.close()
        return jsonify({"error": "ticket already resolved"}), 400
    if ticket.get("status") == "active":
        db.close()
        return jsonify({"error": "ticket is already active"}), 400
    
    db.execute('''UPDATE tickets
                SET status = 'active', priority = ?, specialist_assigned = ?, assignment_date = ?
                WHERE id = ?''',
                (priority, session.get("username"), datetime.now().strftime("%b %d, %Y  %H:%M"), ticket_id))
    db.commit()

    email_notifier.notify_async(ticket, "assignment")
    return jsonify({"message" : f"ticket {ticket_id} claimed and now active"}), 200
    
def resolveTicket(ticket_id, resolution_details):
    if not resolution_details:
        return jsonify({"error": "resolution_details are required to resolve a ticket"}), 400
    db = get_db()
    ticket = dict(db.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone())
    if not ticket:
        db.close()
        return jsonify({"error": "ticket not found"}), 404
    if ticket.get("status") != "active":
        db.close()
        return jsonify({"error": "only active tickets can be resolved"}), 400
    db.execute('''UPDATE tickets 
               SET status = 'resolved', resolution_details = ?, resolution_date = ?
               WHERE id = ?''',
               (resolution_details, datetime.now().strftime("%b %d, %Y  %H:%M"), ticket_id))
    db.commit()

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
    if not new_priority:
        return jsonify({"error" : "priority is required"}), 400
    if new_priority not in ["low","medium","high","critical"]:
        return jsonify({"error" : "priority must be low, medium, high, or critical"}), 400
    
    db = get_db()
    ticket = dict(db.execute('SELECT * from tickets WHERE id=?', (ticket_id,)).fetchone())
    if not ticket:
        db.close()
        return jsonify({"error": "ticket not found"}), 404
    if ticket.get("status") != "active":
        db.close()
        return jsonify({"error": "only active tickets can have their priority updated"}), 400
    db.execute('''UPDATE tickets
               SET priority = ?
               WHERE id = ?''',
               (new_priority, ticket_id))
    db.commit()

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
