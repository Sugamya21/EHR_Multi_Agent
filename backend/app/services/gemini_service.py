import json

from google import genai

from app.config.settings import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# 1. Generate overall patient summary
# ============================================================

def generate_patient_summary(ehr_data):

    prompt = f"""
You are an EHR analysis assistant.

Analyze the following patient's medical record and
generate ONE final overall summary.

The summary should consider:

- Relevant medical history
- Current medical conditions
- Medications
- Important observations and laboratory results
- Significant encounters
- Procedures
- Care plans
- Relevant chronological context
- Recent changes in the patient's record

Rules:

1. Use ONLY information present in the provided EHR.
2. Do not invent information.
3. Do not provide a medical diagnosis.
4. Do not recommend treatment or medication.
5. Do not make unsupported assumptions.
6. If important information is unavailable, state that it is unavailable.
7. Keep the summary factual and understandable.
8. Return ONLY the final narrative summary.
9. Do not create numbered sections.
10. Do not add headings.

Patient EHR:

{ehr_data}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


# ============================================================
# 2. Extract structured EHR data from medical report text
# ============================================================

def extract_ehr_from_text(pdf_text):

    prompt = f"""
You are an EHR data extraction assistant.

Your task is to extract medical information from the
provided medical report and convert it into the required
JSON structure.

IMPORTANT:

The medical report may use different wording, layouts,
abbreviations, or section names.

For example:

"BP: 138/86"
"Blood Pressure: 138/86 mmHg"
"BP reading 138/86"

all represent the same type of observation.

Different report formats are VALID.

Do NOT require the report to contain every section.

If a section is not present, return an empty array.

Use ONLY information explicitly present in the report.

Do not invent information.
Do not infer medical conditions that are not stated.
Do not recommend treatment.
Do not provide a medical diagnosis.

Return ONLY valid JSON.

Do not return markdown.
Do not return explanations.
Do not wrap the JSON in ```json.

The JSON must follow EXACTLY this structure:

{{
    "patientId": "",

    "conditions": [
        {{
            "name": "",
            "status": "",
            "onset": ""
        }}
    ],

    "observations": [
        {{
            "name": "",
            "value": "",
            "unit": "",
            "date": ""
        }}
    ],

    "medications": [
        {{
            "name": "",
            "dosage": "",
            "frequency": "",
            "status": ""
        }}
    ],

    "encounters": [
        {{
            "type": "",
            "date": "",
            "reason": ""
        }}
    ],

    "procedures": [
        {{
            "name": "",
            "date": "",
            "status": ""
        }}
    ],

    "carePlans": [
        {{
            "description": ""
        }}
    ]
}}

FIELD RULES:

patientId:
- Extract the patient ID if present.
- Otherwise return an empty string.

conditions:
- Extract explicitly mentioned medical conditions.
- Each condition MUST be an object.
- "name" should contain the condition name.
- "status" should contain the status only if explicitly available.
- "onset" should contain the onset date only if explicitly available.
- If unavailable, use an empty string.

observations:
- Extract measurements, laboratory results, and vital signs.
- Each observation MUST be an object.
- "name" should contain the observation name.
- "value" should contain the measured value.
- "unit" should contain the unit when available.
- "date" should contain the observation date when available.
- If unavailable, use an empty string.

medications:
- Extract medications explicitly mentioned.
- Each medication MUST be an object.
- "name" should contain the medication name.
- "dosage" should contain dosage when available.
- "frequency" should contain frequency when available.
- "status" should contain status when available.
- If unavailable, use an empty string.

encounters:
- Extract visit or encounter information when available.
- Each encounter MUST be an object.
- "type" should contain the encounter/visit type.
- "date" should contain the encounter date.
- "reason" should contain the reason for the visit when available.
- If unavailable, use an empty string.

procedures:
- Extract procedures explicitly mentioned.
- Each procedure MUST be an object.
- "name" should contain the procedure name.
- "date" should contain the procedure date when available.
- "status" should contain the procedure status when available.
- If unavailable, use an empty string.

carePlans:
- Extract explicitly stated plans, follow-up instructions,
  or care-plan information.
- Each care plan MUST be an object.
- "description" should contain the relevant plan/instruction.

GENERAL RULES:

1. Preserve information from the medical report.
2. Do not invent missing information.
3. Do not omit explicitly stated medical information.
4. Do not require every section to contain data.
5. Empty sections must be represented as [].
6. Do not convert a missing value into a guessed value.
7. Different wording or formatting in the PDF should still be
   interpreted correctly.
8. Return valid JSON only.

For example, if the report says:

"BP: 138/86 mmHg"

return an observation similar to:

{{
    "name": "Blood Pressure",
    "value": "138/86",
    "unit": "mmHg",
    "date": ""
}}

If the report says:

"Metformin 500 mg - once daily"

return a medication similar to:

{{
    "name": "Metformin",
    "dosage": "500 mg",
    "frequency": "once daily",
    "status": ""
}}

Medical Report:

{pdf_text}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    response_text = response.text.strip()

    # Remove accidental markdown code fences if Gemini adds them
    if response_text.startswith("```json"):
        response_text = response_text[7:]

    elif response_text.startswith("```"):
        response_text = response_text[3:]

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    # Convert Gemini JSON into Python dictionary
    try:
        extracted_data = json.loads(response_text)

    except json.JSONDecodeError:
        raise ValueError(
            "Gemini returned invalid JSON."
        )

    return extracted_data