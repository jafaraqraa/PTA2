from .database import SessionLocal
from .models import Patient
from .response_engine import ResponseEngine

def test():
    db = SessionLocal()
    # Patient 4: Left Conductive (AC 45, BC 10), Right Normal (AC 10, BC 10)
    p = db.query(Patient).filter(Patient.id == 4).first()
    if p:
        engine = ResponseEngine(p)
        print("Test: LEFT AC 55dB (Crossover expected because 55-40=15 > 10)")
        # Without masking on RIGHT ear
        print(f"  No masking: {engine.simulate_response('LEFT', 'AC', 1000, 55, 0)}")
        # With masking on RIGHT ear (e.g. 30dB)
        print(f"  Masking (30dB) on RIGHT: {engine.simulate_response('LEFT', 'AC', 1000, 55, 30)}")
        # 55 - 40 = 15. 15 < 30 (masking level). So the RIGHT ear shouldn't hear it now.
        # But the LEFT ear (test ear) still has threshold 45 (+/- 5).
        # So it might still respond if intensity 55 >= effective threshold (which is max 50).
        # Let's test a case where intensity < test ear threshold but > crossover
        print("Test: LEFT AC 30dB (True thresh 45. 30 < 45. 30-40=-10. No crossover.)")
        print(f"  Should be False: {engine.simulate_response('LEFT', 'AC', 1000, 30, 0)}")

    db.close()

if __name__ == "__main__":
    test()
