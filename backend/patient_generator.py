import random
from sqlalchemy.orm import Session
from .models import Patient, Ear, AudiogramPoint, SourceType, Side, TestType

def generate_virtual_patient(db: Session) -> Patient:
    # 1. Get all REAL patients to use as templates
    real_patients = db.query(Patient).filter(Patient.source_type == SourceType.REAL).all()
    if not real_patients:
        raise Exception("No REAL patients found in the database to use as templates.")

    # 2. Create a new VIRTUAL patient
    new_patient = Patient(source_type=SourceType.VIRTUAL)
    db.add(new_patient)
    db.flush()

    # 3. Choose a template patient to copy its hearing combination (Requirement 8)
    template_patient = random.choice(real_patients)

    for template_ear in template_patient.ears:
        # Create new ear
        new_ear = Ear(
            patient_id=new_patient.id,
            side=template_ear.side,
            hearing_type=template_ear.hearing_type
        )
        db.add(new_ear)
        db.flush()

        # Clone points from template ear
        for point in template_ear.points:
            new_point = AudiogramPoint(
                ear_id=new_ear.id,
                frequency=point.frequency,
                threshold_db=point.threshold_db,
                test_type=point.test_type
            )
            db.add(new_point)

    db.commit()
    return new_patient

if __name__ == "__main__":
    from .database import SessionLocal
    db = SessionLocal()
    p = generate_virtual_patient(db)
    print(f"Generated Virtual Patient ID: {p.id}")
    for ear in p.ears:
        print(f"  Ear: {ear.side}, Type: {ear.hearing_type}")
    db.close()
