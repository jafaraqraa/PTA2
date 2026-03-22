from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from .database import get_db, engine
from .models import Base, Patient, Session as PatientSession, Attempt, SourceType, Side, AudiogramPoint
from .patient_generator import generate_virtual_patient
from .response_engine import ResponseEngine
from .evaluation_engine import EvaluationEngine
from .protocol_adherence import check_protocol_adherence
from .scoring import aggregate_scoring
from . import schemas

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PTA Simulator API")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "PTA Simulator API is running"}

@app.post("/sessions/start", response_model=schemas.SessionStartResponse)
def start_session(db: Session = Depends(get_db)):
    # 1. Generate a new virtual patient
    patient = generate_virtual_patient(db)
    # 2. Start a session
    new_session = PatientSession(patient_id=patient.id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": new_session.id, "patient_id": patient.id}

@app.post("/sessions/{session_id}/present", response_model=schemas.PresentToneResponse)
def present_tone(
    session_id: int,
    request: schemas.PresentToneRequest,
    db: Session = Depends(get_db)
):
    session = db.query(PatientSession).filter(PatientSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    patient = session.patient
    engine = ResponseEngine(patient)

    responded = engine.simulate_response(
        side=request.side,
        test_type=request.test_type,
        frequency=request.frequency,
        intensity=request.intensity,
        masking_level=request.masking_level
    )

    # Record attempt
    new_attempt = Attempt(
        session_id=session_id,
        ear=request.side,
        test_type=request.test_type,
        frequency=request.frequency,
        intensity=request.intensity,
        masking_level=request.masking_level,
        patient_responded=responded
    )
    db.add(new_attempt)
    db.commit()

    return {"responded": responded}

@app.post("/sessions/{session_id}/store")
def store_threshold(
    session_id: int,
    request: schemas.StoreThresholdRequest,
    db: Session = Depends(get_db)
):
    # This stores the student-determined threshold in the session state
    # (For simplicity, we can use a separate table or just keep attempts as record)
    # Let's use a record of 'stored_thresholds' for easier evaluation
    # Actually, we'll just return success and the frontend will manage the chart,
    # but the final evaluation will use 'stored thresholds' provided at the end.
    return {"message": "Threshold stored locally (client-side implementation)"}

@app.post("/sessions/{session_id}/evaluate", response_model=schemas.EvaluationResponse)
def evaluate_session(
    session_id: int,
    detected_thresholds: List[schemas.StoreThresholdRequest] = Body(...),
    db: Session = Depends(get_db)
):
    session = db.query(PatientSession).filter(PatientSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    patient = session.patient

    # 1. Evaluate Threshold Accuracy
    eval_engine = EvaluationEngine(db, patient)
    threshold_results = eval_engine.evaluate_thresholds([t.model_dump() for t in detected_thresholds])

    # 2. Evaluate Protocol Adherence
    attempts = db.query(Attempt).filter(Attempt.session_id == session_id).all()
    protocol_results = check_protocol_adherence(attempts)

    # 3. Aggregate Final Scoring
    final_scoring = aggregate_scoring(threshold_results, protocol_results)

    return final_scoring

@app.get("/patients", response_model=List[schemas.PatientResponse])
def get_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    return patients
