from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from .database import Base
import datetime
import enum

class SourceType(str, enum.Enum):
    REAL = "REAL"
    VIRTUAL = "VIRTUAL"

class Side(str, enum.Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"

class TestType(str, enum.Enum):
    AC = "AC"
    BC = "BC"
    AC_MASKED = "AC_MASKED"
    BC_MASKED = "BC_MASKED"

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String, default=SourceType.VIRTUAL)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    ears = relationship("Ear", back_populates="patient", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="patient")

class Ear(Base):
    __tablename__ = "ears"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    side = Column(String) # LEFT or RIGHT
    hearing_type = Column(String) # e.g., Normal, Conductive, etc.

    patient = relationship("Patient", back_populates="ears")
    points = relationship("AudiogramPoint", back_populates="ear", cascade="all, delete-orphan")

class AudiogramPoint(Base):
    __tablename__ = "audiogram_points"

    id = Column(Integer, primary_key=True, index=True)
    ear_id = Column(Integer, ForeignKey("ears.id"))
    frequency = Column(Integer)
    threshold_db = Column(Float)
    test_type = Column(String) # AC, BC, AC_MASKED, BC_MASKED

    ear = relationship("Ear", back_populates="points")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="ACTIVE") # ACTIVE, COMPLETED

    patient = relationship("Patient", back_populates="sessions")
    attempts = relationship("Attempt", back_populates="session")

class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    ear = Column(String)
    test_type = Column(String)
    frequency = Column(Integer)
    intensity = Column(Integer)
    masking_level = Column(Integer, default=0)
    patient_responded = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("Session", back_populates="attempts")
