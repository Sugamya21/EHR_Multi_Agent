# backend/app/utils/ehr_validator.py


REQUIRED_SECTIONS = [
    "conditions",
    "observations",
    "medications",
    "encounters",
    "procedures",
    "carePlans"
]


def validate_ehr_data(data):
    """
    Validate the structure of EHR data extracted by Gemini.

    This validation is intentionally permissive:
    - A section may be empty.
    - Optional fields may be empty strings.
    - Different medical reports may contain different information.

    Returns:
        tuple: (is_valid, errors)
    """

    errors = []

    # --------------------------------------------------
    # 1. Top-level object
    # --------------------------------------------------

    if not isinstance(data, dict):
        return False, ["EHR data must be a JSON object."]

    # --------------------------------------------------
    # 2. Patient ID
    # --------------------------------------------------

    if "patientId" not in data:
        errors.append("Missing patientId.")

    elif not isinstance(data["patientId"], str):
        errors.append("patientId must be a string.")

    # --------------------------------------------------
    # 3. Required sections
    # --------------------------------------------------

    for section in REQUIRED_SECTIONS:

        if section not in data:
            errors.append(
                f"Missing section: {section}"
            )

            continue

        if not isinstance(data[section], list):
            errors.append(
                f"Section '{section}' must be an array."
            )

    # If the top-level structure is already invalid,
    # stop before validating individual records.
    if errors:
        return False, errors

    # --------------------------------------------------
    # 4. Validate individual sections
    # --------------------------------------------------

    validate_conditions(
        data["conditions"],
        errors
    )

    validate_observations(
        data["observations"],
        errors
    )

    validate_medications(
        data["medications"],
        errors
    )

    validate_encounters(
        data["encounters"],
        errors
    )

    validate_procedures(
        data["procedures"],
        errors
    )

    validate_care_plans(
        data["carePlans"],
        errors
    )

    return len(errors) == 0, errors


# ======================================================
# Conditions
# ======================================================

def validate_conditions(conditions, errors):

    for index, condition in enumerate(conditions):

        if not isinstance(condition, dict):
            errors.append(
                f"conditions[{index}] must be an object."
            )
            continue

        if "name" not in condition:
            errors.append(
                f"conditions[{index}] is missing 'name'."
            )

        elif not isinstance(
            condition["name"],
            str
        ):
            errors.append(
                f"conditions[{index}].name must be a string."
            )


# ======================================================
# Observations
# ======================================================

def validate_observations(observations, errors):

    for index, observation in enumerate(observations):

        if not isinstance(observation, dict):
            errors.append(
                f"observations[{index}] must be an object."
            )
            continue

        if "name" not in observation:
            errors.append(
                f"observations[{index}] is missing 'name'."
            )

        elif not isinstance(
            observation["name"],
            str
        ):
            errors.append(
                f"observations[{index}].name must be a string."
            )

        if "value" not in observation:
            errors.append(
                f"observations[{index}] is missing 'value'."
            )


# ======================================================
# Medications
# ======================================================

def validate_medications(medications, errors):

    for index, medication in enumerate(medications):

        if not isinstance(medication, dict):
            errors.append(
                f"medications[{index}] must be an object."
            )
            continue

        if "name" not in medication:
            errors.append(
                f"medications[{index}] is missing 'name'."
            )

        elif not isinstance(
            medication["name"],
            str
        ):
            errors.append(
                f"medications[{index}].name must be a string."
            )


# ======================================================
# Encounters
# ======================================================

def validate_encounters(encounters, errors):

    for index, encounter in enumerate(encounters):

        if not isinstance(encounter, dict):
            errors.append(
                f"encounters[{index}] must be an object."
            )
            continue

        if "type" not in encounter:
            errors.append(
                f"encounters[{index}] is missing 'type'."
            )


# ======================================================
# Procedures
# ======================================================

def validate_procedures(procedures, errors):

    for index, procedure in enumerate(procedures):

        if not isinstance(procedure, dict):
            errors.append(
                f"procedures[{index}] must be an object."
            )
            continue

        if "name" not in procedure:
            errors.append(
                f"procedures[{index}] is missing 'name'."
            )


# ======================================================
# Care Plans
# ======================================================

def validate_care_plans(care_plans, errors):

    for index, care_plan in enumerate(care_plans):

        if not isinstance(care_plan, dict):
            errors.append(
                f"carePlans[{index}] must be an object."
            )
            continue

        if "description" not in care_plan:
            errors.append(
                f"carePlans[{index}] is missing 'description'."
            )