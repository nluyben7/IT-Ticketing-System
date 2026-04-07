import smtplib
import os
from email.mime.text import MIMEText


from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

class EmailNotifier:

    def __init__(self):
        print("EmailNotifier initialized")

    def _send_email(self, to, subject, body):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = GMAIL_ADDRESS
        msg['To'] = to
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
                server.send_message(msg)
                print(f"Email sent to {to} with subject: {subject}")
        except Exception as e:
            print(f"Failed to send email: {e}")


    #TODO: Implement a more robust message queue
    def _queue_email(self, email_content):
        self._send_email(email_content["to"], email_content["subject"], email_content["body"])

    # Email Content Formatting Methods
    def _form_ticket_submission_email(self, recipient_name, recipient_email, ticket_id):
        subject = f"Ticket {ticket_id} Submitted Successfully"
        body = f"Hello {recipient_name},\n\nYour ticket with ID {ticket_id} has been submitted successfully. We will review it and get back to you shortly."
        self._queue_email({"to": recipient_email, "subject": subject, "body": body})
    
    def _form_ticket_assignment_email(self, recipient_name, recipient_email, ticket_id, specialist_name):
        subject = f"Ticket {ticket_id} Assigned"
        body = f"Hello {recipient_name},\n\nOur IT specialist {specialist_name} has claimed your ticket with ID {ticket_id}. {specialist_name} will review it and get back to you shortly."
        self._queue_email({"to": recipient_email, "subject": subject, "body": body})

    def _form_ticket_resolution_email(self, recipient_name, recipient_email, ticket_id, specialist_name):
        subject = f"Ticket {ticket_id} Resolved"
        body = f"Hello {recipient_name},\n\nOur IT specialist {specialist_name} has marked your ticket with ID {ticket_id} as resolved. if you have any further issues or questions, please feel free to reach out or submit a new ticket."
        self._queue_email({"to": recipient_email, "subject": subject, "body": body})

    # def _form_ticket_priority_change_email(self, recipient_name, recipient_email, ticket_id, new_priority):
    #     subject = f"Ticket {ticket_id} Priority Updated"
    #     body = f"Hello {recipient_name},\n\nThe priority of your ticket with ID {ticket_id} has been updated to {new_priority}. We will continue to work on resolving your issue as quickly as possible."
    #     self._queue_email({"to": recipient_email, "subject": subject, "body": body})

    
    #
    def notify_ticketer(self, ticket, notification_type):
        dispatch = {
            "submission": lambda : self._form_ticket_submission_email(ticket["ticketer_name"], ticket["email"], ticket["id"]),
            "assignment": lambda : self._form_ticket_assignment_email(ticket["ticketer_name"], ticket["email"], ticket["id"], ticket["specialist_assigned"]),
            "resolution": lambda : self._form_ticket_resolution_email(ticket["ticketer_name"], ticket["email"], ticket["id"], ticket["specialist_assigned"])
        }
        handler = dispatch.get(notification_type)
        if not handler:
            raise ValueError(f"Unknown notification type: {notification_type}")
        handler()
    