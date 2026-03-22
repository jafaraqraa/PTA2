from .database import SessionLocal
from .models import Patient, Ear, AudiogramPoint, SourceType

def verify():
    db = SessionLocal()
    patients = db.query(Patient).all()
    print(f"Total Patients: {len(patients)}")
    for p in patients:
        print(f"Patient ID: {p.id}, Source: {p.source_type}")
        for ear in p.ears:
            print(f"  Ear: {ear.side}, Type: {ear.hearing_type}, Points: {len(ear.points)}")
    db.close()

if __name__ == "__main__":
    verify()
