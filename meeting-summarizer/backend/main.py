"""
Main FastAPI application entry point.
"""


from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

import config  # loads and validates env vars on startup
import models, database
from summarizer import summarize_transcript
from whisper_transcribe import transcribe_audio
from pdf_export import generate_pdf
from email_digest import send_digest

# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Smart Meeting Summarizer")

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummarizeRequest(BaseModel):
    transcript: str

class EmailDigestRequest(BaseModel):
    meeting_id: int
    emails: List[str]

@app.get("/")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/api/v1/summarize")
async def summarize_meeting(request: SummarizeRequest, db: Session = Depends(database.get_db)):
    """Accepts transcript, generates summary and extracts action items, then saves to DB."""
    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")
        
    result = await summarize_transcript(request.transcript)
    
    # Prioritize LLM's output for action items (no need to overwrite with HF)
    
    # Save to database
    meeting_title = "Meeting Summary"
    if result.get("summary"):
        meeting_title = result["summary"].split('.')[0][:50] + "..."
        
    db_meeting = models.Meeting(
        title=meeting_title,
        transcript=request.transcript,
        summary=result.get("summary", ""),
        decisions=result.get("decisions", []),
        action_items=result.get("action_items", [])
    )
    
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    
    return {
        "id": db_meeting.id,
        "summary": db_meeting.summary,
        "decisions": db_meeting.decisions,
        "action_items": db_meeting.action_items,
        "created_at": db_meeting.created_at
    }

@app.post("/api/v1/transcribe")
async def transcribe_meeting_audio(file: UploadFile = File(...)):
    """Accepts audio file, transcribes using Whisper, returns transcript text."""
    if not file.filename.endswith(('.mp3', '.wav', '.m4a')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
        
    content = await file.read()
    
    try:
        transcript = await transcribe_audio(content, file.filename)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/meetings")
def list_meetings(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """List all saved meetings."""
    meetings = db.query(models.Meeting).order_by(models.Meeting.created_at.desc()).offset(skip).limit(limit).all()
    return meetings

@app.get("/api/v1/meetings/{meeting_id}")
def get_meeting(meeting_id: int, db: Session = Depends(database.get_db)):
    """Get a single meeting by ID."""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@app.delete("/api/v1/meetings/{meeting_id}")
def delete_meeting(meeting_id: int, db: Session = Depends(database.get_db)):
    """Delete a meeting."""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    db.delete(meeting)
    db.commit()
    return {"status": "success"}

@app.get("/api/v1/meetings/{meeting_id}/pdf")
def download_pdf(meeting_id: int, db: Session = Depends(database.get_db)):
    """Download PDF of a meeting."""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    meeting_dict = {
        "title": meeting.title,
        "summary": meeting.summary,
        "decisions": meeting.decisions,
        "action_items": meeting.action_items,
        "created_at": meeting.created_at
    }
    
    pdf_bytes = generate_pdf(meeting_dict)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=meeting_{meeting_id}.pdf"}
    )

@app.post("/api/v1/digest/email")
def send_email_digest(request: EmailDigestRequest, db: Session = Depends(database.get_db)):
    """Send email digest with meeting summary."""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == request.meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    meeting_dict = {
        "title": meeting.title,
        "summary": meeting.summary,
        "decisions": meeting.decisions,
        "action_items": meeting.action_items,
        "created_at": meeting.created_at
    }
    
    success = send_digest(request.emails, meeting_dict)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send emails")
        
    return {"status": "success"}
