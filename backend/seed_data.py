from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Patient, Ear, AudiogramPoint, SourceType, Side, TestType

def seed_real_patients():
    db = SessionLocal()
    try:
        # Check if already seeded (we'll re-seed if we want to add more, or just add new ones)
        existing_count = db.query(Patient).filter(Patient.source_type == SourceType.REAL).count()
        if existing_count >= 5: # Assuming we already have some
            print("Real patients already seeded with sufficient variety.")
            return

        # Common Frequencies
        ac_freqs = [250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000]
        bc_freqs = [500, 750, 1000, 1500, 2000, 3000, 4000]

        # 1. Normal Hearing
        p1 = Patient(source_type=SourceType.REAL)
        db.add(p1)
        db.flush()
        for side in [Side.LEFT, Side.RIGHT]:
            ear = Ear(patient_id=p1.id, side=side, hearing_type="Normal")
            db.add(ear)
            db.flush()
            for freq in ac_freqs:
                db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=10.0, test_type=TestType.AC))
            for freq in bc_freqs:
                db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=10.0, test_type=TestType.BC))

        # 2. Sensorineural Hearing Loss (SNHL) - Symmetric Sloping
        p2 = Patient(source_type=SourceType.REAL)
        db.add(p2)
        db.flush()
        thresholds_snhl = {250: 15, 500: 20, 750: 25, 1000: 30, 1500: 40, 2000: 50, 3000: 60, 4000: 70, 6000: 80, 8000: 85}
        for side in [Side.LEFT, Side.RIGHT]:
            ear = Ear(patient_id=p2.id, side=side, hearing_type="SNHL")
            db.add(ear)
            db.flush()
            for freq, thresh in thresholds_snhl.items():
                db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=thresh, test_type=TestType.AC))
                if freq in bc_freqs:
                    db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=thresh, test_type=TestType.BC))

        # 3. Conductive Hearing Loss (CHL) - Symmetric Flat
        p3 = Patient(source_type=SourceType.REAL)
        db.add(p3)
        db.flush()
        for side in [Side.LEFT, Side.RIGHT]:
            ear = Ear(patient_id=p3.id, side=side, hearing_type="Conductive")
            db.add(ear)
            db.flush()
            for freq in ac_freqs:
                db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=45.0, test_type=TestType.AC))
            for freq in bc_freqs:
                db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=10.0, test_type=TestType.BC))

        # 4. Mixed Hearing Loss - Symmetric
        p4 = Patient(source_type=SourceType.REAL)
        db.add(p4)
        db.flush()
        # Mixed: BC is elevated (>25), AC is even higher
        bc_mixed = {500: 35, 750: 40, 1000: 40, 1500: 45, 2000: 50, 3000: 55, 4000: 60}
        ac_mixed = {250: 50, 500: 55, 750: 60, 1000: 65, 1500: 70, 2000: 75, 3000: 80, 4000: 85, 6000: 90, 8000: 95}
        for side in [Side.LEFT, Side.RIGHT]:
            ear = Ear(patient_id=p4.id, side=side, hearing_type="Mixed")
            db.add(ear)
            db.flush()
            for freq, thresh in ac_mixed.items():
                db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=thresh, test_type=TestType.AC))
            for freq, thresh in bc_mixed.items():
                db.add(AudiogramPoint(ear_id=ear.id, frequency=freq, threshold_db=thresh, test_type=TestType.BC))

        # 5. Asymmetric Hearing Loss (One side Normal, One side SNHL)
        p5 = Patient(source_type=SourceType.REAL)
        db.add(p5)
        db.flush()
        # Left: Normal
        ear_l = Ear(patient_id=p5.id, side=Side.LEFT, hearing_type="Normal")
        db.add(ear_l)
        db.flush()
        for freq in ac_freqs:
            db.add(AudiogramPoint(ear_id=ear_l.id, frequency=freq, threshold_db=10.0, test_type=TestType.AC))
        for freq in bc_freqs:
            db.add(AudiogramPoint(ear_id=ear_l.id, frequency=freq, threshold_db=10.0, test_type=TestType.BC))
        # Right: SNHL
        ear_r = Ear(patient_id=p5.id, side=Side.RIGHT, hearing_type="SNHL")
        db.add(ear_r)
        db.flush()
        for freq, thresh in thresholds_snhl.items():
            db.add(AudiogramPoint(ear_id=ear_r.id, frequency=freq, threshold_db=thresh + 20, test_type=TestType.AC))
            if freq in bc_freqs:
                db.add(AudiogramPoint(ear_id=ear_r.id, frequency=freq, threshold_db=thresh + 20, test_type=TestType.BC))

        db.commit()
        print("Real patients seeded successfully with improved variety.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_real_patients()
