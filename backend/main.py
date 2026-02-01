"""
Main FastAPI Application
Handles all API endpoints for the Hack2Hire platform
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from datetime import datetime

from resume_parser import ResumeParser
from jd_parser import JDParser
from interview_engine import InterviewEngine
from scoring_engine import ScoringEngine

# Initialize FastAPI app
app = FastAPI(
    title="Hack2Hire - AI Mock Interview Platform",
    description="AI-powered mock interview platform with adaptive difficulty",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
resume_parser = ResumeParser()
jd_parser = JDParser()

# Store active interview sessions
active_sessions = {}


class JobDescription(BaseModel):
    """Model for job description input"""
    text: str


class Answer(BaseModel):
    """Model for answer submission"""
    session_id: str
    answer: str
    time_taken: int  # seconds


class SessionData:
    """Store session-specific data"""
    def __init__(self):
        self.resume_data = None
        self.jd_data = None
        self.interview_engine = None
        self.scoring_engine = None
        self.questions_asked = []
        self.answers_given = []
        self.scores = []
        self.created_at = datetime.now()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Hack2Hire - AI Mock Interview Platform",
        "version": "1.0.0",
        "status": "active"
    }


@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse resume
    
    Args:
        file: Resume file (PDF or TXT)
    
    Returns:
        Parsed resume data with session_id
    """
    try:
        # Validate file type
        allowed_types = ['application/pdf', 'text/plain']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail="Only PDF and TXT files are supported"
            )
        
        # Read file content
        content = await file.read()
        
        # Parse resume
        is_pdf = file.content_type == 'application/pdf'
        resume_data = resume_parser.parse(content, is_pdf=is_pdf)
        
        # Create new session
        session_id = f"session_{datetime.now().timestamp()}"
        session = SessionData()
        session.resume_data = resume_data
        active_sessions[session_id] = session
        
        return {
            "success": True,
            "session_id": session_id,
            "resume_data": {
                "skills": resume_data['skills'],
                "total_skills": resume_data['total_skills'],
                "experience_years": resume_data['experience']['years'],
                "projects_found": len(resume_data['projects'])
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")


@app.post("/api/analyze-jd")
async def analyze_job_description(
    session_id: str = Form(...),
    jd_text: str = Form(...)
):
    """
    Analyze job description and compute skill match
    
    Args:
        session_id: Session identifier
        jd_text: Job description text
    
    Returns:
        JD analysis and skill match results
    """
    try:
        # Validate session
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        
        if not session.resume_data:
            raise HTTPException(status_code=400, detail="Resume not uploaded yet")
        
        # Parse JD
        jd_data = jd_parser.parse(jd_text)
        session.jd_data = jd_data
        
        # Compute skill match
        skill_match = jd_parser.compute_skill_match(
            session.resume_data['skills'],
            jd_data['required_skills']
        )
        
        return {
            "success": True,
            "jd_analysis": {
                "required_skills": jd_data['required_skills'],
                "total_required_skills": jd_data['total_required_skills'],
                "experience_required": jd_data['experience_required'],
                "role_level": jd_data['role_level']
            },
            "skill_match": skill_match
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing JD: {str(e)}")


@app.post("/api/start-interview")
async def start_interview(session_id: str = Form(...)):
    """
    Start the interview and get first question
    
    Args:
        session_id: Session identifier
    
    Returns:
        First interview question
    """
    try:
        # Validate session
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        
        if not session.resume_data or not session.jd_data:
            raise HTTPException(
                status_code=400, 
                detail="Resume and JD must be uploaded before starting interview"
            )
        
        # Initialize interview components
        session.interview_engine = InterviewEngine()
        session.scoring_engine = ScoringEngine()
        
        # Get first question
        question_data = session.interview_engine.conduct_interview(
            session.resume_data,
            session.jd_data
        )
        
        session.questions_asked.append(question_data)
        
        return {
            "success": True,
            "question_data": question_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting interview: {str(e)}")


@app.post("/api/submit-answer")
async def submit_answer(answer_data: Answer):
    """
    Submit answer and get next question or results
    
    Args:
        answer_data: Answer submission with session_id, answer text, and time_taken
    
    Returns:
        Score for current answer and next question (or final results)
    """
    try:
        # Validate session
        if answer_data.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[answer_data.session_id]
        
        if not session.interview_engine or not session.scoring_engine:
            raise HTTPException(status_code=400, detail="Interview not started")
        
        # Get current question
        if not session.questions_asked:
            raise HTTPException(status_code=400, detail="No question to answer")
        
        current_question = session.questions_asked[-1]
        
        # Score the answer
        score = session.scoring_engine.score_answer(
            question=current_question['question'],
            answer=answer_data.answer,
            expected_topics=current_question['expected_topics'],
            time_taken=answer_data.time_taken,
            max_time=60
        )
        
        # Store answer and score
        session.answers_given.append({
            'question_number': current_question['question_number'],
            'answer': answer_data.answer,
            'time_taken': answer_data.time_taken
        })
        session.scores.append(score)
        
        # Get recent scores for adaptive logic
        recent_overall_scores = [s['overall'] for s in session.scores]
        
        # Check for early termination
        should_terminate = session.interview_engine.should_terminate_early(recent_overall_scores)
        
        # Check if we've reached max questions
        max_questions_reached = session.interview_engine.question_count >= session.interview_engine.max_questions
        
        if should_terminate:
            # Early termination
            final_results = session.scoring_engine.calculate_final_score(session.scores)
            final_results['termination_reason'] = 'Performance below threshold'
            final_results['early_termination'] = True
            
            return {
                "success": True,
                "current_score": score,
                "interview_complete": True,
                "final_results": final_results
            }
        
        elif max_questions_reached:
            # Normal completion
            final_results = session.scoring_engine.calculate_final_score(session.scores)
            final_results['early_termination'] = False
            
            return {
                "success": True,
                "current_score": score,
                "interview_complete": True,
                "final_results": final_results
            }
        
        else:
            # Continue interview - adjust difficulty and get next question
            new_difficulty = session.interview_engine.adjust_difficulty(recent_overall_scores)
            
            next_question = session.interview_engine.conduct_interview(
                session.resume_data,
                session.jd_data
            )
            
            session.questions_asked.append(next_question)
            
            return {
                "success": True,
                "current_score": score,
                "interview_complete": False,
                "next_question": next_question,
                "difficulty_adjusted": new_difficulty != current_question['difficulty']
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing answer: {str(e)}")


@app.get("/api/session-status/{session_id}")
async def get_session_status(session_id: str):
    """
    Get current session status
    
    Args:
        session_id: Session identifier
    
    Returns:
        Session status and progress
    """
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        
        return {
            "success": True,
            "session_id": session_id,
            "resume_uploaded": session.resume_data is not None,
            "jd_analyzed": session.jd_data is not None,
            "interview_started": session.interview_engine is not None,
            "questions_answered": len(session.answers_given),
            "current_difficulty": session.interview_engine.current_difficulty if session.interview_engine else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching session status: {str(e)}")


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session
    
    Args:
        session_id: Session identifier
    
    Returns:
        Deletion confirmation
    """
    try:
        if session_id in active_sessions:
            del active_sessions[session_id]
            return {"success": True, "message": "Session deleted"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)