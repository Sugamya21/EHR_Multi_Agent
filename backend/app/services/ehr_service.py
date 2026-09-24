from app.database.patient_repository import get_ehr


def normalize_condition(resource):
    """Convert a FHIR Condition into frontend-friendly data."""

    code = resource.get("code", {})
    coding = code.get("coding", [])

    name = code.get("text", "Unknown")

    if coding and coding[0].get("display"):
        name = coding[0]["display"]

    clinical_status = resource.get("clinicalStatus", {})
    status_coding = clinical_status.get("coding", [])

    status = "Unknown"

    if status_coding:
        status = status_coding[0].get(
            "code",
            "Unknown"
        )

    return {
        "id": resource.get("id"),
        "name": name,
        "status": status,
        "onset": resource.get("onsetDateTime"),
        "recordedDate": resource.get("recordedDate"),
        "abatement": resource.get("abatementDateTime")
    }


def get_patient_ehr_sections(patient_id):
    """
    Fetch a patient's EHR and organize the FHIR
    resources into frontend-friendly sections.
    """

    ehr_document = get_ehr(patient_id)

    sections = {
        "patient": [],
        "conditions": [],
        "observations": [],
        "medications": [],
        "encounters": [],
        "procedures": [],
        "carePlans": []
    }

    if ehr_document is None:
        return {
            "patientId": patient_id,
            "version": 1,
            "sections": sections
        }

    bundle = ehr_document.get("fhirBundle", {})

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType")

        if resource_type == "Patient":
            sections["patient"].append(resource)

        elif resource_type == "Condition":
            sections["conditions"].append(
                normalize_condition(resource)
            )

        elif resource_type == "Observation":
            sections["observations"].append(
                normalize_observation(resource)
            )

        elif resource_type in [
            "MedicationRequest",
            "MedicationStatement"
        ]:
            sections["medications"].append(
                normalize_medication(resource)
            )

        elif resource_type == "Encounter":
            sections["encounters"].append(
                normalize_encounter(resource)
            )

        elif resource_type == "Procedure":
            sections["procedures"].append(
                normalize_procedure(resource)
            )

        elif resource_type == "CarePlan":
            sections["carePlans"].append(
                normalize_care_plan(resource)
            )

    return {
        "patientId": patient_id,
        "version": ehr_document.get("version", 1),
        "sections": sections
    }

def normalize_observation(resource):
    """Convert a FHIR Observation into frontend-friendly data."""

    code = resource.get("code", {})
    coding = code.get("coding", [])

    name = code.get("text", "Unknown")

    if coding and coding[0].get("display"):
        name = coding[0]["display"]

    result = {
        "id": resource.get("id"),
        "name": name,
        "status": resource.get("status"),
        "date": resource.get("effectiveDateTime"),
        "value": None,
        "unit": None
    }

    # Normal numeric observation
    value_quantity = resource.get("valueQuantity")

    if value_quantity:
        result["value"] = value_quantity.get("value")
        result["unit"] = value_quantity.get("unit")

    # Coded/text observation
    value_codeable = resource.get("valueCodeableConcept")

    if value_codeable:
        coding = value_codeable.get("coding", [])

        if coding:
            result["value"] = coding[0].get("display")

        else:
            result["value"] = value_codeable.get("text")

    # Blood pressure / component-based observation
    components = resource.get("component", [])

    if components:
        result["components"] = []

        for component in components:

            component_code = component.get("code", {})
            component_coding = component_code.get(
                "coding", []
            )

            component_name = component_code.get(
                "text",
                "Unknown"
            )

            if component_coding:
                component_name = component_coding[0].get(
                    "display",
                    component_name
                )

            component_quantity = component.get(
                "valueQuantity"
            )

            result["components"].append({
                "name": component_name,
                "value": (
                    component_quantity.get("value")
                    if component_quantity
                    else None
                ),
                "unit": (
                    component_quantity.get("unit")
                    if component_quantity
                    else None
                )
            })

    return result

def normalize_medication(resource):
    """Convert a FHIR medication resource into frontend-friendly data."""

    medication = resource.get("medicationCodeableConcept", {})

    coding = medication.get("coding", [])

    name = medication.get("text", "Unknown")

    if coding and coding[0].get("display"):
        name = coding[0]["display"]

    dosage_text = None

    dosage_instructions = resource.get("dosageInstruction", [])

    if dosage_instructions:
        dosage_text = dosage_instructions[0].get("text")

    return {
        "id": resource.get("id"),
        "name": name,
        "status": resource.get("status"),
        "intent": resource.get("intent"),
        "startDate": resource.get("authoredOn"),
        "dosage": dosage_text
    }

def normalize_encounter(resource):
    """Convert a FHIR Encounter into frontend-friendly data."""

    encounter_type = resource.get("type", [])

    encounter_name = "Unknown"

    if encounter_type:
        coding = encounter_type[0].get("coding", [])

        if coding:
            encounter_name = coding[0].get(
                "display",
                "Unknown"
            )

        else:
            encounter_name = encounter_type[0].get(
                "text",
                "Unknown"
            )

    period = resource.get("period", {})

    reason = None

    reasons = resource.get("reasonCode", [])

    if reasons:
        coding = reasons[0].get("coding", [])

        if coding:
            reason = coding[0].get("display")

        else:
            reason = reasons[0].get("text")

    return {
        "id": resource.get("id"),
        "status": resource.get("status"),
        "type": encounter_name,
        "reason": reason,
        "startDate": period.get("start"),
        "endDate": period.get("end")
    }

def normalize_procedure(resource):
    """Convert a FHIR Procedure into frontend-friendly data."""

    code = resource.get("code", {})
    coding = code.get("coding", [])

    name = code.get("text", "Unknown")

    if coding and coding[0].get("display"):
        name = coding[0]["display"]

    performed_date = resource.get("performedDateTime")

    # Some FHIR records may use performedPeriod instead
    performed_period = resource.get("performedPeriod")

    start_date = performed_date
    end_date = None

    if performed_period:
        start_date = performed_period.get("start")
        end_date = performed_period.get("end")

    return {
        "id": resource.get("id"),
        "name": name,
        "status": resource.get("status"),
        "startDate": start_date,
        "endDate": end_date
    }

def normalize_care_plan(resource):
    """Convert a FHIR CarePlan into frontend-friendly data."""

    period = resource.get("period", {})

    return {
        "id": resource.get("id"),
        "status": resource.get("status"),
        "intent": resource.get("intent"),
        "title": resource.get("title"),
        "description": resource.get("description"),
        "startDate": period.get("start"),
        "endDate": period.get("end")
    }