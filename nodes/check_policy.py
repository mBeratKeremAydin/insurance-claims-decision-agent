from uipath.platform import UiPath
from langgraph.types import Command
from uipath_langchain.guardrails import (
    BlockAction,
    CustomValidator,
    GuardrailExecutionStage,
    guardrail,
)

POLICIES_ENTITY_ID = "fa9f8bcf-87ab-f111-9b33-000d3a64f664"


def _date_only(value) -> str:
    return str(value)[:10] if value else ""


def _invalid_claim_input(data: dict) -> bool:
    """Returns True to TRIGGER the guardrail (block the run).

    The guardrail machinery serializes the decorated function's arguments to
    plain dicts before calling this rule, so ``state`` here is a dict, not
    the live GraphState/Pydantic instance.
    """
    state = data.get("state")
    if not isinstance(state, dict):
        return False
    if (state.get("claim_amount") or 0) <= 0:
        return True
    if not state.get("policy_number") or not state.get("claimant_name") or not state.get("incident_date"):
        return True
    return False


@guardrail(
    validator=CustomValidator(rule=_invalid_claim_input),
    action=BlockAction(),
    name="Claim input sanity check",
    stage=GuardrailExecutionStage.PRE,
)
async def _validate_claim_input(state) -> None:
    return None


async def check_policy(state) -> Command:
    await _validate_claim_input(state)
    sdk = UiPath()
    records = await sdk.entities.list_records_async(entity_key=POLICIES_ENTITY_ID, limit=1000)
    policies = [r.model_dump() for r in records]
    match = next((p for p in policies if p.get("PolicyNumber") == state.policy_number), None)

    if match is None:
        return Command(
            update={
                "policy_valid": False,
                "policy_rejection_reason": f"No policy found with number {state.policy_number}",
            }
        )

    is_active = match.get("Status") == "Active"
    incident_date = _date_only(state.incident_date)
    within_coverage = _date_only(match.get("StartDate")) <= incident_date <= _date_only(match.get("EndDate"))
    coverage_amount = float(match.get("CoverageAmount") or 0)
    coverage_ok = state.claim_amount <= coverage_amount

    if not is_active:
        reason = f"Policy status is '{match.get('Status')}', not Active"
    elif not within_coverage:
        reason = "Incident date falls outside the policy coverage period"
    elif not coverage_ok:
        reason = f"Claim amount {state.claim_amount} exceeds policy coverage {coverage_amount}"
    else:
        reason = None

    return Command(
        update={
            "policy_valid": reason is None,
            "policy_rejection_reason": reason,
            "coverage_amount": coverage_amount,
        }
    )
