import uuid
from datetime import datetime

from app.database.patient_repository import (
    get_ehr,
    update_ehr
)


# ============================================================
# FHIR RESOURCE CREATION
# ============================================================

def create_condition_resource(condition):
    return {
        "resourceType": "Condition",
        "id": str(uuid.uuid4()),
        "clinicalStatus": {
            "text": condition.get("status", "")
        },
        "code": {
            "text": condition.get("name", "")
        },
        **(
            {
                "onsetDateTime": condition.get("onset")
            }
            if condition.get("onset")
            else {}
        )
    }


def create_observation_resource(observation):
    resource = {
        "resourceType": "Observation",
        "id": str(uuid.uuid4()),
        "status": "final",
        "code": {
            "text": observation.get("name", "")
        }
    }

    value = observation.get("value", "")
    unit = observation.get("unit", "")

    if value != "":
        resource["valueQuantity"] = {
            "value": value,
            "unit": unit
        }

    date = observation.get("date")

    if date:
        resource["effectiveDateTime"] = date

    return resource


def create_medication_resource(medication):
    resource = {
        "resourceType": "MedicationStatement",
        "id": str(uuid.uuid4()),
        "status": medication.get(
            "status",
            "active"
        ),
        "medicationCodeableConcept": {
            "text": medication.get("name", "")
        }
    }

    dosage = medication.get("dosage", "")
    frequency = medication.get("frequency", "")

    if dosage or frequency:

        dosage_text = ""

        if dosage:
            dosage_text += dosage

        if frequency:

            if dosage:
                dosage_text += " - "

            dosage_text += frequency

        resource["dosage"] = [
            {
                "text": dosage_text
            }
        ]

    return resource


def create_encounter_resource(encounter):
    resource = {
        "resourceType": "Encounter",
        "id": str(uuid.uuid4()),
        "status": "finished",
        "class": {
            "display": encounter.get("type", "")
        }
    }

    reason = encounter.get("reason")

    if reason:
        resource["reasonCode"] = [
            {
                "text": reason
            }
        ]

    date = encounter.get("date")

    if date:
        resource["period"] = {
            "start": date
        }

    return resource


def create_procedure_resource(procedure):
    resource = {
        "resourceType": "Procedure",
        "id": str(uuid.uuid4()),
        "status": procedure.get(
            "status",
            "completed"
        ),
        "code": {
            "text": procedure.get("name", "")
        }
    }

    date = procedure.get("date")

    if date:
        resource["performedDateTime"] = date

    return resource


def create_care_plan_resource(care_plan):
    return {
        "resourceType": "CarePlan",
        "id": str(uuid.uuid4()),
        "status": "active",
        "intent": "plan",
        "description": care_plan.get(
            "description",
            ""
        )
    }


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_name(name):
    """
    Normalize a name only for duplicate comparison.
    Does not modify the stored resource.
    """

    if not name:
        return ""

    name = str(name).strip().lower()

    suffixes = [
        " (disorder)",
        " (finding)",
        " (situation)",
        " (procedure)",
        " (medication)"
    ]

    for suffix in suffixes:

        if name.endswith(suffix):
            name = name[:-len(suffix)]

    return name.strip()


def normalize_date(date):
    if not date:
        return ""

    return str(date).strip()


# ============================================================
# DUPLICATE DETECTION
# ============================================================

def resource_already_exists(
    existing_resources,
    resource_type,
    identifying_text
):
    """
    Used for:
    - Condition
    - MedicationStatement
    - Procedure
    """

    new_name = normalize_name(
        identifying_text
    )

    if not new_name:
        return False

    for resource in existing_resources:

        if resource.get(
            "resourceType"
        ) != resource_type:
            continue

        existing_name = ""

        if resource_type == "Condition":

            existing_name = (
                resource
                .get("code", {})
                .get("text", "")
            )

        elif resource_type == "MedicationStatement":

            existing_name = (
                resource
                .get(
                    "medicationCodeableConcept",
                    {}
                )
                .get("text", "")
            )

        elif resource_type == "Procedure":

            existing_name = (
                resource
                .get("code", {})
                .get("text", "")
            )

        existing_name = normalize_name(
            existing_name
        )

        if existing_name == new_name:
            return True

        # Conservative matching for conditions.
        #
        # Example:
        # "obesity"
        # matches
        # "body mass index 30+ - obesity"

        if resource_type == "Condition":

            if (
                new_name in existing_name
                or existing_name in new_name
            ):
                return True

    return False


def observation_already_exists(
    existing_resources,
    observation
):
    """
    Observation identity:
        name + value + date
    """

    new_name = normalize_name(
        observation.get("name", "")
    )

    new_value = str(
        observation.get("value", "")
    ).strip()

    new_date = normalize_date(
        observation.get("date", "")
    )

    if not new_name:
        return False

    for resource in existing_resources:

        if resource.get(
            "resourceType"
        ) != "Observation":
            continue

        existing_name = normalize_name(
            resource
            .get("code", {})
            .get("text", "")
        )

        if existing_name != new_name:
            continue

        existing_quantity = resource.get(
            "valueQuantity",
            {}
        )

        existing_value = str(
            existing_quantity.get(
                "value",
                ""
            )
        ).strip()

        existing_date = normalize_date(
            resource.get(
                "effectiveDateTime",
                ""
            )
        )

        if (
            existing_value == new_value
            and existing_date == new_date
        ):
            return True

    return False


def encounter_already_exists(
    existing_resources,
    encounter
):
    """
    Encounter identity:
        type + date
    """

    new_type = normalize_name(
        encounter.get("type", "")
    )

    new_date = normalize_date(
        encounter.get("date", "")
    )

    if not new_type:
        return False

    for resource in existing_resources:

        if resource.get(
            "resourceType"
        ) != "Encounter":
            continue

        existing_type = normalize_name(
            resource
            .get("class", {})
            .get("display", "")
        )

        existing_period = resource.get(
            "period",
            {}
        )

        existing_date = normalize_date(
            existing_period.get(
                "start",
                ""
            )
        )

        if (
            existing_type == new_type
            and existing_date == new_date
        ):
            return True

    return False


def care_plan_already_exists(
    existing_resources,
    care_plan
):
    """
    CarePlan identity:
        description
    """

    new_description = normalize_name(
        care_plan.get(
            "description",
            ""
        )
    )

    if not new_description:
        return False

    for resource in existing_resources:

        if resource.get(
            "resourceType"
        ) != "CarePlan":
            continue

        existing_description = normalize_name(
            resource.get(
                "description",
                ""
            )
        )

        if (
            existing_description
            and existing_description == new_description
        ):
            return True

    return False


# ============================================================
# MAIN EHR UPDATE AGENT
# ============================================================

def update_patient_ehr(
    patient_id,
    extracted_data,
    dry_run=True
):
    """
    Merge validated extracted medical data
    into the patient's existing FHIR Bundle.

    dry_run=True:
        Do not modify MongoDB.

    dry_run=False:
        Save the updated bundle to MongoDB.
    """

    # --------------------------------------------------------
    # 1. Get existing EHR
    # --------------------------------------------------------

    ehr_document = get_ehr(
        patient_id
    )

    if ehr_document is None:
        raise ValueError(
            f"No EHR found for patient {patient_id}"
        )

    bundle = ehr_document.get(
        "fhirBundle"
    )

    if not bundle:
        raise ValueError(
            "Patient EHR does not contain a FHIR Bundle."
        )

    # --------------------------------------------------------
    # 2. Make sure entry exists
    # --------------------------------------------------------

    bundle.setdefault(
        "entry",
        []
    )

    # --------------------------------------------------------
    # 3. Existing resources
    # --------------------------------------------------------

    existing_resources = []

    for entry in bundle["entry"]:

        resource = entry.get(
            "resource"
        )

        if resource:
            existing_resources.append(
                resource
            )

    added_resources = []
    skipped_resources = []

    # ========================================================
    # 4. CONDITIONS
    # ========================================================

    for condition in extracted_data.get(
        "conditions",
        []
    ):

        name = condition.get(
            "name",
            ""
        )

        if resource_already_exists(
            existing_resources,
            "Condition",
            name
        ):

            skipped_resources.append(
                f"Condition: {name}"
            )

            continue

        resource = create_condition_resource(
            condition
        )

        bundle["entry"].append({
            "resource": resource
        })

        existing_resources.append(
            resource
        )

        added_resources.append(
            f"Condition: {name}"
        )

    # ========================================================
    # 5. OBSERVATIONS
    # ========================================================

    for observation in extracted_data.get(
        "observations",
        []
    ):

        name = observation.get(
            "name",
            ""
        )

        if observation_already_exists(
            existing_resources,
            observation
        ):

            skipped_resources.append(
                f"Observation: {name}"
            )

            continue

        resource = create_observation_resource(
            observation
        )

        bundle["entry"].append({
            "resource": resource
        })

        existing_resources.append(
            resource
        )

        added_resources.append(
            f"Observation: {name}"
        )

    # ========================================================
    # 6. MEDICATIONS
    # ========================================================

    for medication in extracted_data.get(
        "medications",
        []
    ):

        name = medication.get(
            "name",
            ""
        )

        if resource_already_exists(
            existing_resources,
            "MedicationStatement",
            name
        ):

            skipped_resources.append(
                f"Medication: {name}"
            )

            continue

        resource = create_medication_resource(
            medication
        )

        bundle["entry"].append({
            "resource": resource
        })

        existing_resources.append(
            resource
        )

        added_resources.append(
            f"Medication: {name}"
        )

    # ========================================================
    # 7. ENCOUNTERS
    # ========================================================

    for encounter in extracted_data.get(
        "encounters",
        []
    ):

        if encounter_already_exists(
            existing_resources,
            encounter
        ):

            skipped_resources.append(
                "Encounter"
            )

            continue

        resource = create_encounter_resource(
            encounter
        )

        bundle["entry"].append({
            "resource": resource
        })

        existing_resources.append(
            resource
        )

        added_resources.append(
            "Encounter"
        )

    # ========================================================
    # 8. PROCEDURES
    # ========================================================

    for procedure in extracted_data.get(
        "procedures",
        []
    ):

        name = procedure.get(
            "name",
            ""
        )

        if resource_already_exists(
            existing_resources,
            "Procedure",
            name
        ):

            skipped_resources.append(
                f"Procedure: {name}"
            )

            continue

        resource = create_procedure_resource(
            procedure
        )

        bundle["entry"].append({
            "resource": resource
        })

        existing_resources.append(
            resource
        )

        added_resources.append(
            f"Procedure: {name}"
        )

    # ========================================================
    # 9. CARE PLANS
    # ========================================================

    for care_plan in extracted_data.get(
        "carePlans",
        []
    ):

        if care_plan_already_exists(
            existing_resources,
            care_plan
        ):

            skipped_resources.append(
                "CarePlan"
            )

            continue

        resource = create_care_plan_resource(
            care_plan
        )

        bundle["entry"].append({
            "resource": resource
        })

        existing_resources.append(
            resource
        )

        added_resources.append(
            "CarePlan"
        )

    # ========================================================
    # 10. Update timestamp
    # ========================================================

    bundle["meta"] = bundle.get(
        "meta",
        {}
    )

    bundle["meta"]["lastUpdated"] = (
        datetime.utcnow().isoformat()
        + "Z"
    )

    # ========================================================
    # 11. DRY RUN
    # ========================================================

    if dry_run:

        return {
            "patientId": patient_id,
            "addedResources": added_resources,
            "skippedResources": skipped_resources,
            "dryRun": True
        }

    # ========================================================
    # 12. SAVE TO MONGODB
    # ========================================================

    updated = update_ehr(
        patient_id,
        bundle
    )

    if not updated:
        raise ValueError(
            "MongoDB EHR update failed."
        )

    return {
        "patientId": patient_id,
        "addedResources": added_resources,
        "skippedResources": skipped_resources,
        "dryRun": False
    }