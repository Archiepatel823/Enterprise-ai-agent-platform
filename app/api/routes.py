from time import perf_counter

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.agent.graph import run_agent
from app.guardrails.security import validate_input, validate_output
from app.models import AgentRequest, AgentResponse, SearchRequest
from app.rag.store import document_store

from pathlib import Path
import tempfile

from langchain_community.document_loaders import PyPDFLoader

router = APIRouter()


@router.post("/agent/run", response_model=AgentResponse)
async def run_agent_endpoint(request: AgentRequest):
    guardrail = validate_input(request.task)
    if not guardrail.allowed:
        raise HTTPException(status_code=400, detail=guardrail.reason)

    start = perf_counter()
    try:
        state = await run_agent(
            {
                "task": request.task,
                "session_id": request.session_id,
                "allowed_tools": request.allowed_tools,
                "context": request.context,
                "tool_calls": [],
                "evidence": [],
                "trace": [],
                "iterations": 0,
            }
        )
    except RuntimeError as exc:
        # Missing LLM configuration should be explicit rather than silently falling
        # back to a fake rule-based planner.
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    latency_ms = (perf_counter() - start) * 1000
    output_check = validate_output(state.get("answer", ""))

    return AgentResponse(
        answer=state.get("answer", ""),
        task=request.task,
        plan=state.get("plan", []),
        tool_calls=state.get("tool_calls", []),
        trace=state.get("trace", []),
        latency_ms=round(latency_ms, 2),
        validation_passed=output_check.allowed,
    )


@router.post("/documents/ingest")
async def ingest_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    suffix = Path(file.filename).suffix.lower()

    if suffix not in {".txt", ".pdf"}:
        raise HTTPException(
            status_code=400,
            detail="Only UTF-8 text and PDF files are supported.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Document is empty.")

    try:
        if suffix == ".txt":
            text = content.decode("utf-8")

        else:  # PDF
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name

            try:
                loader = PyPDFLoader(temp_path)
                pages = loader.load()
                text = "\n".join(page.page_content for page in pages)
            finally:
                Path(temp_path).unlink(missing_ok=True)

    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Text files must be UTF-8 encoded.",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read document: {exc}",
        ) from exc

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Document contains no readable text.",
        )

    document_store.add_document(text, file.filename)

    return {
        "status": "indexed",
        "source": file.filename,
    }


@router.post("/documents/search")
async def search_documents(request: SearchRequest):
    return {"results": document_store.search(request.query, request.k)}
