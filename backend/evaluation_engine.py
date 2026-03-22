from typing import List, Dict, Any
from .models import Session, Patient, Ear, AudiogramPoint

class EvaluationEngine:
    def __init__(self, db_session: Session, patient: Patient):
        self.db_session = db_session
        self.patient = patient
        self.true_thresholds = self._load_true_thresholds()

    def _load_true_thresholds(self):
        thresholds = {}
        for ear in self.patient.ears:
            for pt in ear.points:
                key = (ear.side, pt.test_type, pt.frequency)
                thresholds[key] = pt.threshold_db
        return thresholds

    def evaluate_thresholds(self, detected_thresholds: List[Dict[str, Any]]):
        # detected_thresholds: [{"side": "LEFT", "test_type": "AC", "frequency": 1000, "threshold_db": 45}, ...]
        results = []
        total_error = 0
        count = 0

        for det in detected_thresholds:
            side = det["side"]
            test_type = det["test_type"]
            freq = det["frequency"]
            det_val = det["threshold_db"]

            # Match against AC/BC if it's a masked test
            base_type = "AC" if "AC" in test_type else "BC"
            true_val = self.true_thresholds.get((side, base_type, freq))

            if true_val is not None:
                error = abs(det_val - true_val)
                total_error += error
                count += 1
                results.append({
                    "side": side,
                    "frequency": freq,
                    "test_type": test_type,
                    "detected": det_val,
                    "true": true_val,
                    "error": error,
                    "is_correct": error <= 10 # Standard clinical tolerance
                })
            else:
                results.append({
                    "side": side,
                    "frequency": freq,
                    "test_type": test_type,
                    "detected": det_val,
                    "true": "N/A",
                    "error": "N/A",
                    "is_correct": False
                })

        avg_error = total_error / count if count > 0 else 0
        score = max(0, 100 - (avg_error * 2)) # Simple scoring: penalty for each dB error

        return {
            "score": score,
            "average_error_db": avg_error,
            "detailed_results": results
        }

if __name__ == "__main__":
    from .database import SessionLocal
    db = SessionLocal()
    p = db.query(Patient).filter(Patient.id == 4).first()
    if p:
        eval_engine = EvaluationEngine(db, p)
        # Mock student results
        student_results = [
            {"side": "LEFT", "test_type": "AC", "frequency": 1000, "threshold_db": 45},
            {"side": "RIGHT", "test_type": "AC", "frequency": 1000, "threshold_db": 10},
        ]
        eval_results = eval_engine.evaluate_thresholds(student_results)
        print(f"Final Score: {eval_results['score']}")
        print(f"Avg Error: {eval_results['average_error_db']}")
        for res in eval_results['detailed_results']:
            print(f"  {res['side']} {res['frequency']}Hz {res['test_type']}: Student={res['detected']}, True={res['true']}, Match={res['is_correct']}")
    db.close()
