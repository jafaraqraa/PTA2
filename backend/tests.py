import unittest
from sqlalchemy.orm import Session
from .database import engine, SessionLocal, Base
from .models import Patient, SourceType
from .patient_generator import generate_virtual_patient
from .response_engine import ResponseEngine
from .evaluation_engine import EvaluationEngine
from .seed_data import seed_real_patients

class TestPTASimulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_real_patients()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_patient_generation(self):
        patient = generate_virtual_patient(self.db)
        self.assertEqual(patient.source_type, SourceType.VIRTUAL)
        self.assertEqual(len(patient.ears), 2)
        for ear in patient.ears:
            self.assertGreater(len(ear.points), 0)

    def test_response_engine_normal(self):
        # Patient 1 is Normal (10dB)
        p = self.db.query(Patient).filter(Patient.id == 1).first()
        engine = ResponseEngine(p)
        # Should respond at 20dB (threshold 10 +/- 5)
        self.assertTrue(engine.simulate_response('LEFT', 'AC', 1000, 20))
        # Should NOT respond at -10dB
        self.assertFalse(engine.simulate_response('LEFT', 'AC', 1000, -10))

    def test_evaluation_engine(self):
        p = self.db.query(Patient).filter(Patient.id == 1).first()
        eval_engine = EvaluationEngine(self.db, p)
        student_results = [
            {"side": "LEFT", "test_type": "AC", "frequency": 1000, "threshold_db": 10},
            {"side": "RIGHT", "test_type": "AC", "frequency": 1000, "threshold_db": 10},
        ]
        results = eval_engine.evaluate_thresholds(student_results)
        self.assertEqual(results["score"], 100.0)

if __name__ == "__main__":
    unittest.main()
