"""
SendGrid email digest sending logic.
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import SENDGRID_API_KEY, SENDGRID_FROM_EMAIL

def send_digest(emails: list, meeting: dict) -> bool:
    """
    Sends an HTML email with the meeting summary and action items to the provided addresses.
    Uses SendGrid Python library.
    """
    if not SENDGRID_API_KEY or not SENDGRID_FROM_EMAIL:
        print("SendGrid credentials missing.")
        return False
        
    # Build HTML content
    title = meeting.get("title", "Untitled Meeting")
    summary = meeting.get("summary", "No summary.")
    decisions = meeting.get("decisions", [])
    action_items = meeting.get("action_items", [])
    
    decisions_html = "<ul>" + "".join([f"<li>{d}</li>" for d in decisions]) + "</ul>" if decisions else "<p>None</p>"
    
    actions_html = "<table border='1' cellpadding='5' cellspacing='0'><tr><th>Task</th><th>Owner</th><th>Deadline</th><th>Priority</th></tr>"
    for action in action_items:
        priority_color = "black"
        p = action.get("priority", "").lower() if action.get("priority") else ""
        if p == "high": priority_color = "red"
        elif p == "medium": priority_color = "orange"
        elif p == "low": priority_color = "green"
            
        actions_html += f"<tr><td>{action.get('task', '')}</td><td>{action.get('owner', '')}</td><td>{action.get('deadline', '')}</td><td style='color:{priority_color};'><b>{action.get('priority', '')}</b></td></tr>"
    actions_html += "</table>" if action_items else "<p>None</p>"
    
    html_content = f"""
    <h2>Meeting Summary: {title}</h2>
    <h3>Executive Summary</h3>
    <p>{summary}</p>
    
    <h3>Key Decisions</h3>
    {decisions_html}
    
    <h3>Action Items</h3>
    {actions_html}
    """
    
    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=emails,
        subject=f"Meeting Digest: {title}",
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code in (200, 201, 202)
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
