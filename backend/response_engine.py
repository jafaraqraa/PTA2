import random
from .models import Patient, Ear, AudiogramPoint, Side, TestType

class ResponseEngine:
    def __init__(self, patient: Patient):
        self.patient = patient
        self.true_thresholds = self._load_thresholds()

    def _load_thresholds(self):
        thresholds = {}
        for ear in self.patient.ears:
            for pt in ear.points:
                key = (ear.side, pt.test_type, pt.frequency)
                thresholds[key] = pt.threshold_db
        return thresholds

    def simulate_response(self, side: str, test_type: str, frequency: int, intensity: float, masking_level: float = 0):
        # 1. Get True Threshold for the target ear
        # If test_type is MASKED, we still use the underlying AC/BC threshold
        base_test_type = "AC" if "AC" in test_type else "BC"
        true_thresh = self.true_thresholds.get((side, base_test_type, frequency))

        if true_thresh is None:
             return False

        # 2. Consider human-like variability (+/- 5dB)
        variability = random.choice([-5, 0, 5])
        effective_threshold = true_thresh + variability

        # 3. Simulate Clinical Masking Necessity
        # Interaural Attenuation (IA) for Air Conduction: approx 40dB
        # Interaural Attenuation (IA) for Bone Conduction: approx 0-10dB
        ia_ac = 40.0
        ia_bc = 0.0

        other_side = Side.LEFT if side == Side.RIGHT else Side.RIGHT
        other_true_bc = self.true_thresholds.get((other_side, "BC", frequency))
        if other_true_bc is None: # if no BC, assume same as AC
             other_true_bc = self.true_thresholds.get((other_side, "AC", frequency), 0)

        # Cross-over logic
        crossed_over = False
        if "AC" in test_type:
            # Crosses to non-test ear BC
            if intensity - ia_ac >= other_true_bc:
                crossed_over = True
        elif "BC" in test_type:
            # Crosses immediately
            if intensity - ia_bc >= other_true_bc:
                crossed_over = True

        # 4. If student applied MASKING to the non-test ear
        # Calculate effective masking on the non-test ear
        if masking_level > 0:
            # Effective masking raises the threshold in the non-test ear
            # For simplicity: effective_other_bc = max(other_true_bc, masking_level - clinical_reserve)
            # Simplest model: if masking_level > other_true_bc, the other ear is "busy"
            # and cannot hear the tone until intensity - IA > masking_level
            if crossed_over:
                # Does the tone beat the masking?
                if "AC" in test_type:
                     if intensity - ia_ac < masking_level:
                         crossed_over = False
                elif "BC" in test_type:
                     if intensity - ia_bc < masking_level:
                         crossed_over = False

        # 5. Result: Responds if (intensity >= effective_threshold) OR (crossed_over)
        return intensity >= effective_threshold or crossed_over

if __name__ == "__main__":
    from .database import SessionLocal
    from .models import Patient
    db = SessionLocal()
    # Let's pick a patient (e.g., patient 4 generated before)
    p = db.query(Patient).filter(Patient.id == 4).first()
    if p:
        engine = ResponseEngine(p)
        print(f"Testing Patient {p.id} (Left: Conductive, Right: Normal)")
        # Left ear (Conductive, AC thresh = 45dB)
        print(f"L 1000Hz 30dB: {engine.simulate_response('LEFT', 'AC', 1000, 30)}")
        print(f"L 1000Hz 45dB: {engine.simulate_response('LEFT', 'AC', 1000, 45)}")
        print(f"L 1000Hz 55dB: {engine.simulate_response('LEFT', 'AC', 1000, 55)}")
        # Right ear (Normal, AC thresh = 10dB)
        print(f"R 1000Hz 15dB: {engine.simulate_response('RIGHT', 'AC', 1000, 15)}")
    db.close()
