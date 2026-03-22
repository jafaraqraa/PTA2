import random
from sqlalchemy.orm import Session
from .models import Patient, Ear, AudiogramPoint, SourceType, Side, TestType

def generate_virtual_patient(db: Session) -> Patient:
    """
    Generates a virtual patient using a Data-Driven Sampling approach.
    It selects a 'REAL' patient template to preserve:
    1. Inter-aural correlation (Left/Right ear relationship)
    2. Inter-frequency correlation (Audiogram shape)
    3. Clinical realism (Hearing loss types combination)

    Then it applies Clinical Perturbation and enforces medical constraints.
    """
    # 1. Get all REAL patients to use as templates
    real_patients = db.query(Patient).filter(Patient.source_type == SourceType.REAL).all()
    if not real_patients:
        raise Exception("No REAL patients found in the database to use as templates.")

    # 2. Create a new VIRTUAL patient
    new_patient = Patient(source_type=SourceType.VIRTUAL)
    db.add(new_patient)
    db.flush()

    # 3. Ear Pair Sampling: Choose a template patient
    template_patient = random.choice(real_patients)

    # 4. Patient-level shift (General shift across both ears)
    # This simulates different severities within the same clinical pattern
    # We use random.choice to avoid needing numpy
    patient_severity_shift = random.choice([-10, -5, 0, 5, 10])

    for template_ear in template_patient.ears:
        # Create new ear
        new_ear = Ear(
            patient_id=new_patient.id,
            side=template_ear.side,
            hearing_type=template_ear.hearing_type
        )
        db.add(new_ear)
        db.flush()

        # Extract points to dictionaries
        points_by_type = {}
        for pt in template_ear.points:
            if pt.test_type not in points_by_type:
                points_by_type[pt.test_type] = {}
            points_by_type[pt.test_type][pt.frequency] = pt.threshold_db

        # 5. Apply Perturbation & Enforce Constraints
        # We focus on AC and BC as the primary "true" thresholds
        ac_pts = points_by_type.get(TestType.AC, {})
        bc_pts = points_by_type.get(TestType.BC, {})

        # Ear-level shift
        ear_shift = random.choice([-5, 0, 5])

        new_ac_pts = {}
        new_bc_pts = {}

        # First, perturb all points
        all_freqs = set(list(ac_pts.keys()) + list(bc_pts.keys()))
        for freq in all_freqs:
            # Frequency-specific jitter
            jitter = random.choice([-5, 0, 5])
            total_shift = patient_severity_shift + ear_shift + jitter

            if freq in ac_pts:
                new_ac_pts[freq] = _clamp_threshold(ac_pts[freq] + total_shift)
            if freq in bc_pts:
                new_bc_pts[freq] = _clamp_threshold(bc_pts[freq] + total_shift)

        # 6. Enforce Clinical Integrity (Medical Logic)
        _enforce_clinical_rules(new_ear.hearing_type, new_ac_pts, new_bc_pts)

        # 7. Persist points
        for freq, val in new_ac_pts.items():
            db.add(AudiogramPoint(ear_id=new_ear.id, frequency=freq, threshold_db=val, test_type=TestType.AC))
            # Also copy masked if they existed in template, but shifted
            if freq in points_by_type.get(TestType.AC_MASKED, {}):
                db.add(AudiogramPoint(ear_id=new_ear.id, frequency=freq, threshold_db=val, test_type=TestType.AC_MASKED))

        for freq, val in new_bc_pts.items():
            db.add(AudiogramPoint(ear_id=new_ear.id, frequency=freq, threshold_db=val, test_type=TestType.BC))
            if freq in points_by_type.get(TestType.BC_MASKED, {}):
                db.add(AudiogramPoint(ear_id=new_ear.id, frequency=freq, threshold_db=val, test_type=TestType.BC_MASKED))

    db.commit()
    return new_patient

def _clamp_threshold(val: float) -> float:
    """Clamps to clinical range [0, 120] and rounds to nearest 5dB."""
    val = max(0, min(120, round(val / 5) * 5))
    return float(val)

def _enforce_clinical_rules(hearing_type: str, ac_pts: dict, bc_pts: dict):
    """
    Applies medical knowledge to ensure the generated thresholds are realistic.
    """
    for freq in ac_pts:
        ac = ac_pts[freq]
        bc = bc_pts.get(freq)

        # Universal Rule: Bone is never worse than Air (physically impossible)
        if bc is not None:
            if bc > ac:
                bc = ac

        # Type-specific clinical constraints
        if hearing_type == "Normal":
            # Normal: Thresholds <= 25dB, Air-Bone Gap <= 10dB
            ac = min(ac, 25.0)
            if bc is not None:
                bc = min(bc, 25.0)
                if ac - bc > 10:
                    bc = ac - 5 # Reduced ABG

        elif hearing_type == "SNHL":
            # Sensorineural: Thresholds > 25 (usually), Air-Bone Gap <= 10dB
            if bc is not None:
                if ac - bc > 10:
                    bc = ac - random.choice([0, 5, 10])

        elif hearing_type == "Conductive":
            # Conductive: BC Normal (<= 25), AC Elevated, ABG > 10dB
            if bc is not None:
                bc = min(bc, 25.0)
                if ac - bc <= 10:
                    ac = bc + 30.0 # Force a significant ABG
            else:
                # If no BC at this freq, assume AC is elevated
                ac = max(ac, 30.0)

        elif hearing_type == "Mixed":
            # Mixed: BC Elevated (> 25), AC even higher, ABG > 10dB
            if bc is not None:
                bc = max(bc, 30.0)
                if ac - bc <= 10:
                    ac = bc + 20.0
            else:
                ac = max(ac, 45.0)

        ac_pts[freq] = ac
        if bc is not None:
            bc_pts[freq] = bc

if __name__ == "__main__":
    from .database import SessionLocal
    db = SessionLocal()
    try:
        p = generate_virtual_patient(db)
        print(f"Generated Virtual Patient ID: {p.id}")
        for ear in p.ears:
            print(f"  Ear: {ear.side}, Type: {ear.hearing_type}")
    finally:
        db.close()
