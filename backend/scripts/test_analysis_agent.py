import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from app.agents.ehr_analysis_agent import analyze_patient


if __name__ == "__main__":

    patient_id = "PAT0001"

    print("\nGenerating EHR analysis...")
    print("Please wait...\n")

    try:

        summary = analyze_patient(patient_id)

        print("=" * 60)
        print("AI GENERATED PATIENT REPORT")
        print("=" * 60)

        print(summary)

        print("\n" + "=" * 60)

    except Exception as e:

        print("Error:", e)