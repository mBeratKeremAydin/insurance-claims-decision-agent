from uipath.platform import UiPath
from langgraph.types import Command

CLAIMS_HISTORY_ENTITY_ID = "99e828dc-87ab-f111-9b33-000d3a64f664"


def _date_only(value) -> str:
    return str(value)[:10] if value else ""


async def check_duplicate(state) -> Command:
    sdk = UiPath()
    records = await sdk.entities.list_records_async(entity_key=CLAIMS_HISTORY_ENTITY_ID, limit=1000)
    claims = [r.model_dump() for r in records]
    incident_date = _date_only(state.incident_date)

    duplicate = any(
        c.get("PolicyNumber") == state.policy_number and _date_only(c.get("IncidentDate")) == incident_date
        for c in claims
    )

    return Command(update={"is_duplicate": duplicate})
