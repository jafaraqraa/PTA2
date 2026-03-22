from .database import SessionLocal
from .models import Patient, SourceType

def show_patients():
    db = SessionLocal()
    try:
        patients = db.query(Patient).all()
        print(f"{'ID':<4} | {'Source':<10} | {'Side':<6} | {'Hearing Type':<15}")
        print("-" * 45)
        for p in patients:
            for ear in p.ears:
                print(f"{p.id:<4} | {p.source_type:<10} | {ear.side:<6} | {ear.hearing_type:<15}")
                # Optional: Show points
                # for pt in sorted(ear.points, key=lambda x: (x.test_type, x.frequency)):
                #    print(f"  {pt.test_type} {pt.frequency}Hz: {pt.threshold_db}dB")
    finally:
        db.close()

if __name__ == "__main__":
    show_patients()
