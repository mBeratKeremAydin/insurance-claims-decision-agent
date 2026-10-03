from langgraph.types import Command


async def recommend_decision(state) -> Command:
    if not state.policy_valid:
        decision = "reject"
        rationale = f"Police gecersiz: {state.policy_rejection_reason}"
    elif state.is_duplicate:
        decision = "manual_review"
        rationale = "Bu police ve hasar tarihiyle daha once bir basvuru bulundu (mukerrer basvuru suphesi)."
    elif not state.documents_complete:
        decision = "manual_review"
        rationale = f"Eksik evrak: {', '.join(state.missing_document_types)}"
    elif state.fraud_risk_score >= 0.5:
        decision = "manual_review"
        rationale = f"Sahte hasar suphesi (risk skoru: {state.fraud_risk_score}). {state.document_findings}"
    else:
        decision = "approve"
        rationale = f"Police gecerli, mukerrer basvuru yok, evraklar eksiksiz, sahtecilik suphesi dusuk. {state.document_findings}"

    return Command(
        update={
            "decision": decision,
            "rationale": rationale,
            # the runtime only captures the terminal node's update as final output,
            # so re-surface fields GraphOutput needs even though earlier nodes set them
            "policy_valid": state.policy_valid,
            "is_duplicate": state.is_duplicate,
            "fraud_risk_score": state.fraud_risk_score,
        }
    )
