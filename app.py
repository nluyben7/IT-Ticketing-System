from flask import Flask, request, render_template, jsonify, session, redirect
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import heapq
import bcrypt
import logging
from email_notifier import EmailNotifier

from database import get_db, init_db, seed_db


TICKETS_PER_PAGE = 15
app = Flask(__name__)
app.secret_key = "supersecretkey"  # In production, use a secure random key and keep it secret

email_notifier = EmailNotifier()
init_db()
seed_db()



#----------------------------- SIMILAR TICKETS FINDING -----------------------------

tf_idf_cache = {
    "vectorizer": None,
    "matrix": None,
    "tickets": [],
}

def formatTicketText(ticket):
    text = ticket["summary"] + " " + ticket["description"]
    if ticket["resolution_details"]:
        text += " " + ticket["resolution_details"]
    return text

def rebuild_tfidf_cache():
    db = get_db()
    all_tickets = [dict(row) for row in db.execute('SELECT id, summary, description, resolution_details FROM tickets').fetchall()]
    if not all_tickets:
        logging.error("Error rebuilding tf_idf_cache")
    texts = [formatTicketText(t) for t in all_tickets]
    matrix = tf_idf_cache["vectorizer"].fit_transform(texts)
    tf_idf_cache["matrix"] = matrix
    tf_idf_cache["tickets"] = all_tickets

def findSimilarTickets(ticket, number_of_similar=3, threshold=0.1):
    
    target_text = formatTicketText(ticket)
    query_vector = tf_idf_cache["vectorizer"].transform([target_text]) 
    scores = cosine_similarity(query_vector, tf_idf_cache["matrix"]).flatten()

    closest_tickets = heapq.nlargest(number_of_similar + 1, zip(tf_idf_cache["tickets"], scores), key=lambda x: x[1])
    similar_ids = [t["id"] for t, score in closest_tickets if t["id"] != ticket["id"] and score >= threshold]
    if not similar_ids:
        return []
    db = get_db()
    placeholders = ','.join('?' * len(similar_ids))
    similar_tickets = [dict(t) for t in db.execute(f'SELECT * from tickets WHERE id IN ({placeholders}) ', similar_ids).fetchall()]
    db.close()
    return similar_tickets

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
        "specialist_username_assigned": None,
        "submission_date": None,
    }
    return findSimilarTickets(pseudo_ticket, number_of_similar=total_count, threshold=0.05)

def init_tf_idf_cache():
    tf_idf_cache["vectorizer"] = TfidfVectorizer(stop_words='english')
    rebuild_tfidf_cache()
init_tf_idf_cache()


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
        return jsonify({"error": "username and password are required to login"}), 401
    db = get_db()
    row = db.execute('''SELECT hashed_password FROM it_specialists WHERE username = ? ''', (body.get("username"),)).fetchone()
    db.close()
    if not row:
        return jsonify({"message": "username or password is incorrect"}), 401
    submitted_password = body.get("password")
    if not bcrypt.checkpw(body.get("password").encode('utf-8'),row["hashed_password"]):
        return jsonify({"message": "username or password is incorrect"}), 401
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
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab','all') 
    if page < 1:
        return jsonify({"error": "invalid page number"}), 400 
    if not tab in ['unassigned','active','resolved', 'all']:
        return jsonify({"error": "invalid tab type"}), 400
    db = get_db()
    if tab == 'all':
        total = db.execute('SELECT COUNT(*) FROM tickets').fetchone()[0]
        tickets = db.execute('SELECT * FROM tickets LIMIT ? OFFSET ?', (TICKETS_PER_PAGE, (page-1) * TICKETS_PER_PAGE,)).fetchall()
    else:
        total = db.execute('SELECT COUNT(*) FROM tickets WHERE status = ?', (tab,)).fetchone()[0]
        tickets = db.execute('SELECT * FROM tickets WHERE status = ? LIMIT ? OFFSET ?', (tab, TICKETS_PER_PAGE, (page-1) * TICKETS_PER_PAGE,)).fetchall()
    db.close()
    max_page = max(1, -(-total // TICKETS_PER_PAGE))
    if page > max_page:
        return redirect(f'/tickets/view?tab={tab}&page={max_page}')
    return render_template("tickets.html", tickets=[dict(t) for t in tickets], tab=tab, page_num = page, has_next=(page * TICKETS_PER_PAGE) < total)

@app.route('/tickets/view/<int:ticket_id>', methods=['GET'])
def viewTicketById(ticket_id):
    auth_error = it_only_check()
    if auth_error:
        return auth_error
    db = get_db()
    ticket = dict(db.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone())
    if not ticket:
        return f"<p>Ticket #{ticket_id} not found. <a href='/tickets/view'>Go back</a></p>", 404
    print(ticket["specialist_username_assigned"])
    specialist = None
    specialist_row =  db.execute('SELECT username, name FROM it_specialists WHERE username = ?', (ticket["specialist_username_assigned"],)).fetchone()
    db.close()
    if specialist_row:
        specialist = dict(specialist_row)
        print(specialist["name"])
    
    return render_template("ticket_details.html", ticket=ticket, related_tickets=findSimilarTickets(ticket),
                            specialist = specialist, username=session.get("username"))

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
    try:
        cursor = db.execute('''INSERT INTO tickets (ticketer_name, ticketer_email, issue_type, summary, description, status, submission_date)
                VALUES (?, ?, ?, ?, ?, 'unassigned', ?)''', (body["ticketer_name"], body["ticketer_email"], body["issue_type"], body["summary"], body["description"], datetime.now().strftime("%b %d, %Y  %H:%M")))
        db.commit()
        new_ticket = dict(db.execute('SELECT * FROM tickets WHERE id = ?', (cursor.lastrowid,)).fetchone())
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating ticket: {e}")
        return jsonify({"error" : "internal server error"}), 500
    finally:
        db.close()

    email_notifier.notify_async(new_ticket, "submission")
    return jsonify(new_ticket), 201 

#----------------------------- TICKET VIEWING AND CREATION ENDPOINTS END -----------------------------

#----------------------------- TICKET UPDATING ENDPOINTS -----------------------------

def claimTicket(ticket_id, priority):
    if not priority:
        return jsonify({"error": "setting priority is required to claim a ticket"}), 400
    try:
        db = get_db()
        row = db.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
        if not row:
            db.close()
            return jsonify({"error": "ticket not found"}), 404
        ticket = dict(row)
        if ticket.get("status") == "resolved":
            db.close()
            return jsonify({"error": "ticket already resolved"}), 400
        if ticket.get("status") == "active":
            db.close()
            return jsonify({"error": "ticket is already active"}), 400
        
        db.execute('''UPDATE tickets
                    SET status = 'active', priority = ?, specialist_username_assigned = ?, assignment_date = ?
                    WHERE id = ?''',
                    (priority, session.get("username"), datetime.now().strftime("%b %d, %Y  %H:%M"), ticket_id))
        db.execute('''UPDATE it_specialists SET tickets_claimed = tickets_claimed + 1, tickets_active = tickets_active + 1 WHERE username = ? ''', (session.get("username"),))
        db.commit()
        ticket = dict(db.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone())
        
        email_notifier.notify_async(ticket, "assignment")
        return jsonify({"message" : f"ticket {ticket_id} claimed and now active"}), 200
    except Exception as e:
        db.rollback()
        #todo: error logging
        return jsonify({"error":"internal server error"}), 500
    finally:
        db.close()

    
def resolveTicket(ticket_id, resolution_details):
    if not resolution_details:
        return jsonify({"error": "resolution_details are required to resolve a ticket"}), 400
    
    db = get_db()
    try:
        row = db.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
        if not row:
            db.close()
            return jsonify({"error": "ticket not found"}), 404
        ticket = dict(row)
        if ticket.get("status") != "active":
            db.close()
            return jsonify({"error": "only active tickets can be resolved"}), 400
        if ticket.get("specialist_username_assigned") != session.get("username"):
            db.close()
            return jsonify({"error": "you can only resolve tickets assigned to you"}), 403
        
        db.execute('''UPDATE tickets 
                SET status = 'resolved', resolution_details = ?, resolution_date = ?
                WHERE id = ?''',
                (resolution_details, datetime.now().strftime("%b %d, %Y  %H:%M"), ticket_id))
        db.execute('''UPDATE it_specialists SET tickets_resolved = tickets_resolved + 1, tickets_active = tickets_active - 1 WHERE username = ? ''', (session.get("username"),))
        resolution_time_hours = (datetime.now() - datetime.strptime(ticket["assignment_date"], "%b %d, %Y  %H:%M")).total_seconds() / 3600
        db.execute('''UPDATE it_specialists SET total_resolution_time_hours = total_resolution_time_hours + ? 
                WHERE username = ? ''', (resolution_time_hours, session.get("username"),))
        db.commit()
        ticket = dict(db.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone())
        email_notifier.notify_async(ticket, "resolution")
        return jsonify({"message" : f"ticket {ticket_id} resolved"}), 200
    except Exception as e:
        db.rollback()
        #todo: error logging
        return jsonify({"error":"internal server error"}), 500
    finally:
        db.close()


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
    try:
        row = db.execute('SELECT * from tickets WHERE id=?', (ticket_id,)).fetchone()
        if not row:
            return jsonify({"error": "ticket not found"}), 404
        ticket = dict(row)
        if ticket.get("status") != "active":
            return jsonify({"error": "only active tickets can have their priority updated"}), 400
        if ticket.get("specialist_username_assigned") != session.get("username"):
            return jsonify({"error": "you can only update the priority of tickets assigned to you"}), 403
        db.execute('''UPDATE tickets
                SET priority = ?
                WHERE id = ?''',
                (new_priority, ticket_id))
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Error changing ticket priority for ticket #{ticket_id}: {e}")
        return jsonify({"error": "internal server error"}),500
    finally:
        db.close()
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

