from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
from datetime import datetime

class AudiogramPointBase(BaseModel):
    frequency: int
    threshold_db: float
    test_type: str

class EarBase(BaseModel):
    side: str
    hearing_type: str
    points: List[AudiogramPointBase]

    @field_validator('points')
    @classmethod
    def validate_points(cls, v, info):
        # Mandatory frequencies for AC: 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000
        # Mandatory frequencies for BC: 500, 750, 1000, 1500, 2000, 3000, 4000
        ac_freqs = {250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000}
        bc_freqs = {500, 750, 1000, 1500, 2000, 3000, 4000}

        present_ac = {p.frequency for p in v if p.test_type == 'AC'}
        present_bc = {p.frequency for p in v if p.test_type == 'BC'}

        if not ac_freqs.issubset(present_ac):
            missing = ac_freqs - present_ac
            raise ValueError(f"Missing mandatory AC frequencies: {missing}")
        if not bc_freqs.issubset(present_bc):
            missing = bc_freqs - present_bc
            raise ValueError(f"Missing mandatory BC frequencies: {missing}")
        return v

class PatientResponse(BaseModel):
    id: int
    source_type: str
    ears: List[EarBase]

    @field_validator('ears')
    @classmethod
    def validate_ears(cls, v):
        if len(v) != 2:
            raise ValueError("Patient must have exactly two ears.")
        sides = {e.side for e in v}
        if sides != {"LEFT", "RIGHT"}:
            raise ValueError("Patient must have one LEFT ear and one RIGHT ear.")
        return v

    class Config:
        from_attributes = True

class SessionStartResponse(BaseModel):
    session_id: int
    patient_id: int

class PresentToneRequest(BaseModel):
    side: str
    test_type: str
    frequency: int
    intensity: int
    masking_level: int = 0

class PresentToneResponse(BaseModel):
    responded: bool

class StoreThresholdRequest(BaseModel):
    side: str
    test_type: str
    frequency: int
    threshold_db: int
    is_nr: bool = False

class EvaluationResponse(BaseModel):
    final_score: float
    threshold_accuracy_score: float
    protocol_adherence_score: float
    feedback: List[str]
    details: List[dict]
