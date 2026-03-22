from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Patient, Ear, AudiogramPoint, SourceType, Side, TestType

def seed_real_patients():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Patient).filter(Patient.source_type == SourceType.REAL).first():
            print("Real patients already seeded.")
            return

        # Define some common hearing patterns
        # 1. Normal Hearing
        p1 = Patient(source_type=SourceType.REAL)
        db.add(p1)
        db.flush()

        for side in [Side.LEFT, Side.RIGHT]:
            ear = Ear(patient_id=p1.id, side=side, hearing_type="Normal")
            db.add(ear)
            db.flush()
            # AC points
            for freq in [250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000]:
                db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=10.0, test_type=TestType.AC))
            # BC points
            for freq in [500, 750, 1000, 1500, 2000, 3000, 4000]:
                db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=10.0, test_type=TestType.BC))

        # 2. Sensorineural Hearing Loss (SNHL) - High Frequency
        p2 = Patient(source_type=SourceType.REAL)
        db.add(p2)
        db.flush()

        for side in [Side.LEFT, Side.RIGHT]:
            ear = Ear(patient_id=p2.id, side=side, hearing_type="SNHL")
            db.add(ear)
            db.flush()
            # AC points (sloping)
            thresholds = {250: 15, 500: 20, 750: 25, 1000: 30, 1500: 40, 2000: 50, 3000: 60, 4000: 70, 6000: 80, 8000: 85}
            for freq, thresh in thresholds.items():
                db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=thresh, test_type=TestType.AC))
            # BC points (same as AC for SNHL)
            for freq in [500, 750, 1000, 1500, 2000, 3000, 4000]:
                db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=thresholds[freq], test_type=TestType.BC))

        # 3. Conductive Hearing Loss (CHL)
        p3 = Patient(source_type=SourceType.REAL)
        db.add(p3)
        db.flush()

        for side in [Side.LEFT, Side.RIGHT]:
            ear = Ear(patient_id=p3.id, side=side, hearing_type="Conductive")
            db.add(ear)
            db.flush()
            # AC points (elevated)
            for freq in [250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000]:
                db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=45.0, test_type=TestType.AC))
            # BC points (normal)
            for freq in [500, 750, 1000, 1500, 2000, 3000, 4000]:
                db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=10.0, test_type=TestType.BC))

        db.commit()
        print("Real patients seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_real_patients()
