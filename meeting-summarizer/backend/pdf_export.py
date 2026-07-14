"""
PDF generation using ReportLab.
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_pdf(meeting: dict) -> bytes:
    """
    Generates a PDF digest of the meeting using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    body_style = styles['Normal']
    
    # Priority color coding: High=red, Medium=orange, Low=green
    def get_priority_color(priority):
        p = priority.lower() if priority else ""
        if p == "high":
            return colors.red
        elif p == "medium":
            return colors.orange
        elif p == "low":
            return colors.green
        return colors.black

    elements = []
    
    # Title
    date_str = meeting.get("created_at", datetime.now()).strftime("%Y-%m-%d %H:%M") if isinstance(meeting.get("created_at"), datetime) else str(meeting.get("created_at", "Unknown Date"))
    title = f"Meeting Summary - {date_str}"
    if meeting.get("title") and meeting.get("title") != "Untitled Meeting":
        title = f"{meeting.get('title')} - {date_str}"
        
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    elements.append(Paragraph(meeting.get("summary", "No summary provided."), body_style))
    elements.append(Spacer(1, 12))
    
    # Key Decisions
    elements.append(Paragraph("Key Decisions", heading_style))
    decisions = meeting.get("decisions", [])
    if decisions:
        decision_items = [ListItem(Paragraph(d, body_style)) for d in decisions]
        elements.append(ListFlowable(decision_items, bulletType='bullet'))
    else:
        elements.append(Paragraph("No key decisions recorded.", body_style))
    elements.append(Spacer(1, 12))
    
    # Action Items
    elements.append(Paragraph("Action Items", heading_style))
    action_items = meeting.get("action_items", [])
    
    if action_items:
        data = [["Task", "Owner", "Deadline", "Priority"]]
        for item in action_items:
            data.append([
                Paragraph(item.get("task", ""), body_style),
                item.get("owner", ""),
                item.get("deadline", ""),
                item.get("priority", "")
            ])
            
        t = Table(data, colWidths=[200, 100, 100, 68])
        t_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A5F")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8FAFC")),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ])
        
        # Color code priorities
        for i, item in enumerate(action_items):
            priority = item.get("priority", "")
            color = get_priority_color(priority)
            t_style.add('TEXTCOLOR', (3, i+1), (3, i+1), color)
            
        t.setStyle(t_style)
        elements.append(t)
    else:
        elements.append(Paragraph("No action items recorded.", body_style))
        
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
