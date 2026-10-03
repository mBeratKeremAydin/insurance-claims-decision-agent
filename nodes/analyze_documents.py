import json

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Command
from uipath_langchain.chat import UiPathAzureChatOpenAI

SYSTEM_PROMPT = """Sen bir sigorta hasar degerlendirme asistanisin. Sana bir sigorta basvurusuna ait belge metinleri verilecek.

Gorevin:
1. Su belge turlerinden hangilerinin eksik oldugunu belirle: "hasar tespit tutanagi", "onarim tahmini", "olay aciklamasi".
2. Belgelerde tutarsizlik, abartili/inandirici olmayan hasar tanimlari veya sahtecilik belirtisi olup olmadigini 0.0-1.0 arasi bir risk skoruyla degerlendir (0.0 = supheli degil, 1.0 = cok supheli).

Yalnizca asagidaki JSON formatinda cevap ver, baska hicbir metin ekleme:
{"missing_document_types": [...], "fraud_risk_score": <sayi>, "findings": "<kisa aciklama>"}
"""


async def analyze_documents(state) -> Command:
    llm = UiPathAzureChatOpenAI(model="gpt-4.1-mini-2025-04-14")
    documents_text = "\n---\n".join(state.document_texts) if state.document_texts else "(belge saglanmadi)"

    response = await llm.ainvoke(
        [
            SystemMessage(SYSTEM_PROMPT),
            HumanMessage(f"Basvuru belgeleri:\n{documents_text}"),
        ]
    )

    try:
        parsed = json.loads(response.content)
    except (json.JSONDecodeError, TypeError):
        parsed = {
            "missing_document_types": [],
            "fraud_risk_score": 0.0,
            "findings": "Analiz sonucu ayristirilamadi (LLM yanit formati beklenmedik).",
        }

    missing = parsed.get("missing_document_types") or []

    return Command(
        update={
            "documents_complete": len(missing) == 0,
            "missing_document_types": missing,
            "fraud_risk_score": float(parsed.get("fraud_risk_score", 0.0)),
            "document_findings": parsed.get("findings", ""),
        }
    )
