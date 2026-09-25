import json
from google import genai

from app.config.settings import GEMINI_API_KEY

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def analyze_trends(relevant_data):
    compact_data = {
        "patient": relevant_data.get("patient", [])[:1],
        "conditions": relevant_data.get("conditions", []),
        "medications": relevant_data.get("medications", []),
        "observations": relevant_data.get("observations", [])[-50:],
        "encounters": relevant_data.get("encounters", [])[-20:],
        "procedures": relevant_data.get("procedures", [])[-20:],
        "carePlans": relevant_data.get("carePlans", [])
    }

    prompt = f"""
You are an EHR clinical report generation assistant.

Generate a concise hospital-style clinical report using ONLY
the documented information provided in the patient's EHR.

The report must contain ONLY clinically relevant information
that is actually present in the EHR.

Return EXACTLY this JSON structure:

{{
    "reasonForVisit": "",
    "clinicalFindings": [],
    "assessment": [],
    "investigations": [],
    "medications": [],
    "procedures": [],
    "clinicalImpression": "",
    "plan": [],
    "importantNotes": []
}}

FIELD RULES:

reasonForVisit:
- Keep the documented reason for the current visit or encounter.
- Do not infer a reason from diagnoses, medications, observations, or procedures.
- If no documented reason exists, return an empty string.

clinicalStatus:
- Include only the most clinically relevant current patient status information.
- Prioritize current vital signs and other clinically meaningful current status information.
- Include only information that materially helps understand the patient's current clinical state.
- Do not dump all observations.
- Do not include every laboratory measurement.
- Do not repeat information that belongs under RESULTS.
- Do not include historical or irrelevant observations.
- Prefer a small, clinically meaningful selection over a comprehensive list.

assessment:
- Include only currently relevant documented diagnoses or clinical assessments.
- Do not dump the patient's complete diagnosis history.
- Organize assessment items in this order:
  1. Explicitly documented history, past conditions, or situation/context items.
  2. Explicitly documented active/current diagnoses.
  3. Other relevant clinical assessments.
- A documented history or situation item must appear before its corresponding
  active/current diagnosis when both are present.
- Do not place an active diagnosis before its documented historical context.
- Do not classify a condition as historical unless the EHR explicitly
  indicates this.
- Do not create diagnoses from symptoms, observations, medications, or
  laboratory values.
- Avoid duplicate representations of the same clinical condition unless
  both entries provide distinct clinically relevant information.
- Prioritize clinically relevant active conditions rather than reproducing
  the entire diagnosis list.

results:
- Include only clinically relevant recent investigation or laboratory results.
- Select the results that materially support the current assessment or clinical impression.
- Do not dump the complete observation or laboratory dataset.
- Do not repeat the same result multiple times.
- Include the value and unit when documented.
- Do not invent reference ranges or interpretations.
- Do not convert an observation into a diagnosis.

medications:
- Include only medications explicitly documented as active/current.
- Exclude discontinued, stopped, completed, cancelled, or historical medications.
- Include medication name and documented dosage/frequency when available.
- Do not infer that a medication is active when its status is unclear.

procedures:
- Include only procedures that are explicitly documented and clinically relevant to the current report.
- Do not dump the patient's complete historical procedure list.
- Exclude unrelated historical procedures.
- Do not invent procedure indications or outcomes.

clinicalImpression:
- Provide a concise factual synthesis of the current clinically relevant information.
- Focus on active assessments, relevant clinical status, and relevant results.
- Do not repeat the entire EHR.
- Do not include historical information unless directly relevant to the current clinical picture.
- Do not introduce diagnoses, interpretations, or information not documented in the EHR.

plan:
- Include only currently documented and relevant care-plan or follow-up information.
- Exclude historical, completed, or irrelevant plans when their status is documented.
- Do not create recommendations.
- Do not recommend medications, tests, or treatment that are not documented.

importantNotes:
- Include only currently important documented information that materially matters to understanding the patient's clinical situation.
- Do not repeat information already adequately represented in other sections.
- Exclude historical or irrelevant notes.
- Do not create warnings, diagnoses, or recommendations.

STRICT RULES:

- Use ONLY the supplied EHR data.
- Do not invent information.
- Do not infer missing information.
- Do not invent allergies.
- Do not invent reference ranges.
- Do not invent reasons for visits.
- Do not invent symptoms.
- Do not invent diagnoses.
- Do not recommend medication.
- Do not recommend treatment.
- Do not make predictions.
- Do not turn a single observation into a clinical trend.
- Do not include historical information unless it is relevant to the
  current documented clinical report.
- Keep the report concise.
- Do not dump the entire EHR.
- If a field has no supported information, return an empty string
  or empty array.
- Never write "No data available".
- Never write "Not available".
- Never create placeholder text.
- Return ONLY valid JSON.
- Do not return markdown.
- Do not use code fences.

PATIENT EHR:

{json.dumps(compact_data, ensure_ascii=False)}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    response_text = response.text.strip()

    if response_text.startswith("```json"):
        response_text = response_text[7:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        raise ValueError(
            "Gemini returned invalid clinical report JSON."
        )

    return {
        "reasonForVisit": result.get("reasonForVisit", ""),
        "clinicalFindings": result.get("clinicalFindings", []),
        "assessment": result.get("assessment", []),
        "investigations": result.get("investigations", []),
        "medications": result.get("medications", []),
        "procedures": result.get("procedures", []),
        "clinicalImpression": result.get("clinicalImpression", ""),
        "plan": result.get("plan", []),
        "importantNotes": result.get("importantNotes", [])
    }