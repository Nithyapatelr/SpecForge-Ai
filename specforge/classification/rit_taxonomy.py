"""
Requirement Intent Taxonomy (RIT) v1 — core research contribution.

RIT_CATEGORIES is the canonical list of category definitions.
Two independent annotators classifying the same requirement sentence
should agree ≥80% of the time — this agreement rate is what we defend
in the evaluation chapter.

Each category has:
  - label_id:         unique machine-readable key
  - label_name:       human-readable name shown in reports and the UI
  - label_definition: precise definition (the test for inter-annotator agreement)
  - parent_category:  None for top-level; label_id of parent for sub-categories

Sub-categories (up to 3 per top-level) are included where the distinction
materially affects how a MAS framework should handle the requirement.
"""

RIT_CATEGORIES: list[dict] = [
    # ------------------------------------------------------------------
    # 1. Behavioral Rule
    # ------------------------------------------------------------------
    {
        "label_id": "BEHAVIORAL_RULE",
        "label_name": "Behavioral Rule",
        "label_definition": (
            "A requirement that specifies what the system must do in response to a "
            "specific condition, event, or input. It takes the form 'if/when [condition] "
            "then [system action]', explicitly or implicitly. The condition and the "
            "action must both be identifiable. Pure capability statements ('the system "
            "shall support X') without a triggering condition are NOT behavioral rules."
        ),
        "parent_category": None,
        # Example: "When a patient cancels an appointment less than 24 hours in advance,
        # the system shall charge the cancellation fee and notify the doctor."
    },
    {
        "label_id": "BEHAVIORAL_RULE_CONSTRAINT",
        "label_name": "Behavioral Rule — Constraint",
        "label_definition": (
            "A behavioral rule that imposes a hard constraint on system behaviour "
            "(e.g. rate limits, timeouts, retry counts). The system must not exceed "
            "or violate the stated boundary."
        ),
        "parent_category": "BEHAVIORAL_RULE",
        # Example: "If a user fails to log in three consecutive times, the account
        # shall be locked for 30 minutes."
    },

    # ------------------------------------------------------------------
    # 2. State Transition
    # ------------------------------------------------------------------
    {
        "label_id": "STATE_TRANSITION",
        "label_name": "State Transition",
        "label_definition": (
            "A requirement that describes how a named entity (e.g. order, appointment, "
            "user account) moves from one discrete state to another, including the "
            "triggering event and the resulting state. Both the source state and the "
            "destination state must be nameable. Generic CRUD descriptions without "
            "named states are NOT state transitions."
        ),
        "parent_category": None,
        # Example: "An appointment moves from 'Scheduled' to 'Confirmed' once the
        # doctor accepts it; it moves to 'Cancelled' if either party withdraws."
    },
    {
        "label_id": "STATE_TRANSITION_LIFECYCLE",
        "label_name": "State Transition — Full Lifecycle",
        "label_definition": (
            "A state transition requirement that describes the complete set of valid "
            "states and all allowed transitions for an entity, rather than a single "
            "transition pair."
        ),
        "parent_category": "STATE_TRANSITION",
        # Example: "A prescription request can be in states: Draft, Submitted,
        # Under Review, Approved, Dispensed, Rejected. From Submitted it can go to
        # Under Review or Rejected only."
    },

    # ------------------------------------------------------------------
    # 3. Actor Permission
    # ------------------------------------------------------------------
    {
        "label_id": "ACTOR_PERMISSION",
        "label_name": "Actor Permission",
        "label_definition": (
            "A requirement that explicitly states which role, user type, or external "
            "actor is authorised (or explicitly prohibited) to perform a specific "
            "action or access a specific resource. The actor and the action must both "
            "be named. Vague statements like 'users can view reports' without "
            "specifying which users are NOT actor permissions."
        ),
        "parent_category": None,
        # Example: "Only users with the 'Senior Doctor' role shall be permitted to
        # approve prescription requests for controlled substances."
    },
    {
        "label_id": "ACTOR_PERMISSION_DELEGATION",
        "label_name": "Actor Permission — Delegation",
        "label_definition": (
            "An actor permission requirement where one role can grant or revoke "
            "permissions for another role."
        ),
        "parent_category": "ACTOR_PERMISSION",
        # Example: "A Hospital Administrator may grant the 'Scheduling' permission
        # to any staff member in the Outpatient department."
    },

    # ------------------------------------------------------------------
    # 4. Data Contract
    # ------------------------------------------------------------------
    {
        "label_id": "DATA_CONTRACT",
        "label_name": "Data Contract",
        "label_definition": (
            "A requirement that specifies a data field's name, type, format, allowed "
            "values, constraints, or validation rule. The requirement is primarily "
            "about the shape or validity of data rather than about system behaviour. "
            "A measurable threshold (e.g. 'max 500 characters') must be present for "
            "the requirement to be unambiguous."
        ),
        "parent_category": None,
        # Example: "The patient's date of birth field must be stored as ISO 8601
        # (YYYY-MM-DD) and must not be a future date."
    },
    {
        "label_id": "DATA_CONTRACT_SCHEMA",
        "label_name": "Data Contract — Schema Definition",
        "label_definition": (
            "A data contract requirement that defines the structure of a complete "
            "entity or message (multiple fields at once), rather than a single field."
        ),
        "parent_category": "DATA_CONTRACT",
        # Example: "Each Appointment record must contain: appointment_id (UUID),
        # patient_id (UUID), doctor_id (UUID), slot_datetime (ISO 8601),
        # status (enum: Scheduled | Confirmed | Cancelled | Completed)."
    },

    # ------------------------------------------------------------------
    # 5. Integration Constraint
    # ------------------------------------------------------------------
    {
        "label_id": "INTEGRATION_CONSTRAINT",
        "label_name": "Integration Constraint",
        "label_definition": (
            "A requirement about how the system interacts with an external system, "
            "third-party API, hardware device, or communication protocol. It specifies "
            "what is sent, received, or coordinated across a system boundary. "
            "Internal module-to-module interactions are NOT integration constraints."
        ),
        "parent_category": None,
        # Example: "The system shall send appointment confirmation SMSes via the
        # Twilio REST API within 60 seconds of status change to 'Confirmed'."
    },
    {
        "label_id": "INTEGRATION_CONSTRAINT_SLA",
        "label_name": "Integration Constraint — SLA",
        "label_definition": (
            "An integration constraint that additionally specifies a service-level "
            "agreement (timeout, retry policy, availability) for the external interaction."
        ),
        "parent_category": "INTEGRATION_CONSTRAINT",
        # Example: "Calls to the pharmacy stock API must complete within 3 seconds;
        # if the API is unavailable, the system shall retry twice and then surface
        # an error to the prescribing doctor."
    },

    # ------------------------------------------------------------------
    # 6. Acceptance Condition
    # ------------------------------------------------------------------
    {
        "label_id": "ACCEPTANCE_CONDITION",
        "label_name": "Acceptance Condition",
        "label_definition": (
            "A requirement that states a testable, measurable criterion for when a "
            "feature or behaviour is considered correctly implemented. It must include "
            "a concrete, verifiable threshold, observable output, or pass/fail "
            "criterion. Vague statements of desired quality ('the system should be "
            "fast') without a measurable threshold are NOT acceptance conditions."
        ),
        "parent_category": None,
        # Example: "The appointment booking page must load in under 2 seconds for
        # 95% of requests when tested with 100 concurrent users."
    },
    {
        "label_id": "ACCEPTANCE_CONDITION_PERFORMANCE",
        "label_name": "Acceptance Condition — Performance",
        "label_definition": (
            "An acceptance condition specifically about response time, throughput, "
            "or resource usage under defined load."
        ),
        "parent_category": "ACCEPTANCE_CONDITION",
        # Example: "Report generation for a 12-month patient history must complete
        # in under 5 seconds on a dataset of 10,000 appointments."
    },
]
