from typing import List, Dict, Any
from .models import Attempt

def check_protocol_adherence(attempts: List[Attempt]) -> Dict[str, Any]:
    if not attempts:
        return {"protocol_score": 0, "feedback": ["No attempts recorded."]}

    feedback = []
    score = 100

    # 1. Started with 1000Hz (most common clinical standard)
    if attempts[0].frequency != 1000:
        score -= 10
        feedback.append(f"Standard protocol suggests starting at 1000Hz, but you started at {attempts[0].frequency}Hz.")

    # 2. Check for "Up 5, Down 10" technique (Hughson-Westlake)
    # Group attempts by frequency and ear
    trials = {}
    for att in attempts:
        key = (att.ear, att.frequency, att.test_type)
        if key not in trials: trials[key] = []
        trials[key].append(att)

    for key, trial_attempts in trials.items():
        if len(trial_attempts) < 2: continue

        for i in range(1, len(trial_attempts)):
            prev = trial_attempts[i-1]
            curr = trial_attempts[i]

            # If responded, intensity should decrease (standard: down 10)
            if prev.patient_responded:
                if curr.intensity >= prev.intensity:
                    score -= 1
                    feedback.append(f"After a response at {key[1]}Hz, you should typically decrease intensity.")
                elif prev.intensity - curr.intensity > 15:
                    score -= 1
                    feedback.append(f"After a response at {key[1]}Hz, you decreased by more than 10dB.")

            # If no response, intensity should increase (standard: up 5)
            else:
                if curr.intensity <= prev.intensity:
                    score -= 1
                    feedback.append(f"After no response at {key[1]}Hz, you should increase intensity.")
                elif curr.intensity - prev.intensity > 10:
                    score -= 1
                    feedback.append(f"After no response at {key[1]}Hz, you increased by more than 5dB.")

    # 3. Check for masking protocol
    for attempt in attempts:
        if "MASKED" in attempt.test_type and attempt.masking_level == 0:
            score -= 5
            feedback.append(f"Used {attempt.test_type} but masking level was 0 at {attempt.frequency}Hz.")

    return {
        "protocol_score": max(0, score),
        "feedback": list(set(feedback))
    }

if __name__ == "__main__":
    # Mock
    class MockAttempt:
        def __init__(self, frequency, intensity, test_type, masking_level, responded):
             self.ear = "RIGHT"
             self.frequency = frequency
             self.intensity = intensity
             self.test_type = test_type
             self.masking_level = masking_level
             self.patient_responded = responded

    attempts = [
        MockAttempt(1000, 30, "AC", 0, True),
        MockAttempt(1000, 40, "AC", 0, True) # Responded but increased intensity
    ]
    results = check_protocol_adherence(attempts)
    print(f"Protocol Score: {results['protocol_score']}")
    for f in results['feedback']:
        print(f"  Feedback: {f}")
