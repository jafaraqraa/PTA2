from typing import Dict, Any

def aggregate_scoring(threshold_results: Dict[str, Any], protocol_results: Dict[str, Any]) -> Dict[str, Any]:
    # Final Score Calculation: 70% threshold accuracy, 30% protocol adherence
    final_score = (threshold_results["score"] * 0.7) + (protocol_results["protocol_score"] * 0.3)
    return {
        "final_score": round(final_score, 2),
        "threshold_accuracy_score": threshold_results["score"],
        "protocol_adherence_score": protocol_results["protocol_score"],
        "feedback": protocol_results["feedback"],
        "details": threshold_results["detailed_results"]
    }

if __name__ == "__main__":
    threshold_results = {"score": 90, "detailed_results": []}
    protocol_results = {"protocol_score": 80, "feedback": ["Started at 250Hz instead of 1000Hz."]}
    final = aggregate_scoring(threshold_results, protocol_results)
    print(f"Final Aggregate Score: {final['final_score']}")
