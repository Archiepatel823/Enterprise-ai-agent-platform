# Enterprise AI Agent Platform

An end-to-end **AI engineering project** that demonstrates a multi-step enterprise agent workflow using **LangGraph**, **FastAPI**, **RAG**, and the **Model Context Protocol (MCP)**.

The system processes supported tasks, selects appropriate tools, retrieves information from an enterprise knowledge base, performs calculations, executes multi-step workflows, and returns structured responses with execution traces.

**Stack:** Python · FastAPI · LangGraph · LangChain · NVIDIA NIM · MCP · ChromaDB · Sentence Transformers · PyPDF · Docker · Pytest · GitHub Actions

---

## Overview

This project implements an agent-style workflow for enterprise tasks. It combines workflow orchestration, retrieval, tool execution, guardrails, and evaluation in a single backend application.

The workflow supports:

* Enterprise document retrieval
* PDF and UTF-8 text document ingestion
* Safe calculator execution
* Multi-step task processing
* Tool permission validation
* Prompt-injection checks
* Execution tracing
* MCP-based tool integration
* RAG-based knowledge retrieval
* Duplicate document detection
* Evaluation and testing
* Docker deployment

---

## Architecture

```text
User Request
     |
     v
Input Guardrails
     |
     v
Task Planning
     |
     v
LangGraph Orchestrator
     |
     +----------------------+----------------------+
     |                     |                      |
     v                     v                      v
Document Search        Calculator            Research
     |                     |                      |
     +---------------------+----------------------+
                           |
                           v
                    Tool Execution
                           |
                           v
                    Evidence Collection
                           |
                           v
                    Response Generation
                           |
                           v
                    Output Validation
                           |
                           v
                     Final Response
```

The LangGraph workflow manages task routing and tool execution for supported tasks. Tool outputs are collected as evidence and used to construct the final response.

---

## Example Workflow

For a request such as:

> According to the employee policy, how many annual leave days correspond to 3 months of a 20-day yearly allowance?

The workflow can:

1. Search the enterprise knowledge base for relevant leave policy information.
2. Retrieve the required policy context.
3. Perform the required calculation.
4. Collect the tool outputs.
5. Return a structured final response with execution details.

---

## Key Features

* **LangGraph orchestration** for multi-step execution
* Task routing for supported workflows
* **RAG pipeline** using ChromaDB and sentence-transformer embeddings
* PDF and UTF-8 text document ingestion
* Automatic PDF text extraction using PyPDF
* Enterprise document retrieval with source metadata
* Duplicate document detection during ingestion
* Safe calculator tool
* External research integration
* **MCP client/server integration** for enterprise tools
* Tool permission enforcement
* Prompt-injection heuristics and output validation
* Structured execution traces
* Sample enterprise knowledge base bootstrapping
* Evaluation harness for answer quality, tool accuracy, latency, and completion
* Unit tests and GitHub Actions CI
* Docker deployment

---

## Project Structure

```text
enterprise-ai-agent-platform/
│
├── app/
│   ├── agent/
│   │   ├── graph.py             # LangGraph workflow
│   │   └── state.py             # Agent state
│   │
│   ├── api/
│   │   └── routes.py            # FastAPI endpoints
│   │
│   ├── guardrails/
│   │   └── security.py          # Input/output/tool guardrails
│   │
│   ├── llm/
│   │   ├── client.py            # Shared NVIDIA NIM LLM client
│   │   └── prompts.py           # LLM prompts
│   │
│   ├── mcp/
│   │   └── client.py            # MCP client
│   │
│   ├── observability/
│   │
│   ├── rag/
│   │   └── store.py             # ChromaDB document store
│   │
│   ├── tools/
│   │   └── registry.py          # Local/external tool implementations
│   │
│   ├── config.py
│   ├── main.py
│   └── models.py
│
├── evaluation/
│   ├── dataset.json
│   └── run_evaluation.py
│
├── mcp_server/
│   └── server.py                # MCP tool server
│
├── sample_data/
│   └── employee_policy.txt
│
├── tests/
│   ├── test_guardrails.py
│   ├── test_agent_routing.py
│   └── test_tools.py
│
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repository-url>

cd enterprise-ai-agent-platform
```

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv .venv

.venv\Scripts\activate
```

**Linux/macOS:**

```bash
python -m venv .venv

source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Configure the NVIDIA NIM API:

```env
NVIDIA_API_KEY=your_nvidia_api_key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=openai/gpt-oss-20b

CHROMA_PATH=./data/chroma

LOG_LEVEL=INFO

MAX_TOOL_CALLS=5

MCP_ENABLED=true
```

> `.env` is ignored by Git and should never be committed.

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

Open:

* Swagger UI: `http://127.0.0.1:8000/docs`
* Health endpoint: `http://127.0.0.1:8000/health`

---

## API Usage

### Run the Agent

```bash
curl -X POST http://127.0.0.1:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "task": "According to the employee policy, how many annual leave days correspond to 3 months of a 20-day yearly allowance?",
    "session_id": "demo-session",
    "allowed_tools": ["document_search", "calculator"]
  }'
```

The response can include:

* Final response
* Execution plan
* Tool calls and inputs
* Tool outputs
* Execution trace
* Latency information
* Validation results

---

### Ingest a Text Document

The ingestion pipeline supports UTF-8 `.txt` files.

```bash
curl -X POST http://127.0.0.1:8000/documents/ingest \
  -F "file=@sample_data/employee_policy.txt"
```

Example response:

```json
{
  "status": "indexed",
  "source": "employee_policy.txt"
}
```

---

### Ingest a PDF Document

PDF documents are processed using PyPDF before being passed to the RAG pipeline.

```bash
curl -X POST http://127.0.0.1:8000/documents/ingest \
  -F "file=@sample_data/employee_policy.pdf"
```

The ingestion pipeline:

```text
PDF
 |
 v
PDF Text Extraction
 |
 v
Text Chunking
 |
 v
Sentence Transformer Embeddings
 |
 v
ChromaDB
```

---

### Search Documents Directly

```bash
curl -X POST http://127.0.0.1:8000/documents/search \
  -H "Content-Type: application/json" \
  -d '{"query": "employee leave policy", "k": 4}'
```

The search endpoint returns relevant document chunks along with their source and similarity distance.

---

## RAG Pipeline

The project uses ChromaDB and sentence-transformer embeddings to retrieve relevant enterprise knowledge.

```text
Enterprise Document
        |
        v
Text / PDF Processing
        |
        v
Text Chunking
        |
        v
Embedding Generation
        |
        v
ChromaDB Vector Store
        |
        v
Similarity Search
        |
        v
Relevant Context
        |
        v
Agent Workflow
```

The embedding model used by the document store is:

```text
all-MiniLM-L6-v2
```

Documents are split into overlapping chunks before being stored in ChromaDB.

Each indexed chunk stores source metadata to identify the originating document.

The ingestion layer also checks whether a source has already been indexed to avoid unnecessary duplicate ingestion.

---

## MCP Integration

The project includes both an MCP client and server for exposing enterprise capabilities through the Model Context Protocol.

```text
LangGraph Agent
      |
      v
MCP Client
      |
      v
MCP Server
      |
      +--> search_enterprise_documents
      |
      +--> calculate
```

The MCP layer provides a standardized boundary for integrating external tools with the agent workflow.

You can also run the MCP server manually:

```bash
python -m mcp_server.server
```

---

## Guardrails

The project includes basic security and validation mechanisms, including:

* Tool permission validation
* Prompt-injection detection heuristics
* Safe calculator expression handling
* Output validation
* Tool execution limits

These checks help reduce unsafe or unauthorized tool execution.

---

## Evaluation

Run:

```bash
python -m evaluation.run_evaluation
```

The evaluation reports metrics such as:

* Response keyword quality
* Required tool-call accuracy
* Task completion rate
* Average latency

The dataset includes examples involving:

1. Calculator tasks
2. Enterprise RAG retrieval tasks
3. Multi-step RAG and calculation tasks

---

## Tests

Run:

```bash
pytest -q
```

The tests cover:

* Prompt-injection guardrails
* Tool permission checks
* Agent routing
* Safe calculator execution
* Rejection of unsafe calculator expressions

GitHub Actions runs the test suite on pushes and pull requests.

---

## Docker

Build and run:

```bash
docker compose up --build
```

The API becomes available at:

```text
http://localhost:8000
```

---

## Design Decisions

### Why LangGraph?

LangGraph provides a structured way to model multi-step workflows with explicit state transitions.

The project uses LangGraph to manage:

* Agent state
* Tool execution
* Workflow routing
* Iterative task processing
* Final response generation

### Why RAG?

Enterprise applications often need answers grounded in internal knowledge.

The RAG pipeline retrieves relevant information from indexed documents and makes that information available to the agent workflow.

### Why ChromaDB?

ChromaDB provides a persistent vector store for semantic document retrieval without requiring a separate managed vector database.

### Why MCP?

MCP provides a standardized protocol boundary for exposing external capabilities as tools.

This allows enterprise capabilities to be integrated separately from the core agent workflow.

### Why Guardrails?

Tool-using systems can execute actions based on user input.

Permission checks and input validation help reduce unsafe or unauthorized tool execution.

### Why NVIDIA NIM?

The application uses NVIDIA NIM through its OpenAI-compatible API interface, allowing the LLM client to integrate with an OpenAI-compatible endpoint while keeping the application architecture provider-independent.

---

## Suggested GitHub Demo

For a strong project demonstration:

1. Start the FastAPI server.
2. Open Swagger UI.
3. Ingest the sample employee policy.
4. Ingest a PDF document.
5. Run a document retrieval task.
6. Run a calculator task.
7. Run a multi-step RAG and calculation task.
8. Inspect the execution trace.
9. Demonstrate MCP tools.
10. Test tool permission restrictions.
11. Demonstrate prompt-injection validation.
12. Run the evaluation harness.
13. Run the test suite.
14. Demonstrate Docker deployment.

---

## Future Improvements

* Add fully LLM-driven task planning with structured output
* Add LLM-based response synthesis grounded in tool evidence
* Add Redis-backed conversation memory
* Add human-in-the-loop approval for sensitive tools
* Add tool retries and timeout policies
* Add a production web-search provider
* Add DOCX document support
* Add authentication and role-based tool permissions
* Add LangSmith or OpenTelemetry tracing
* Add RAG evaluation using dedicated evaluation frameworks
* Add document versioning and deletion
* Add asynchronous document processing for large files

---

## Author

**Archie Patel**

* GitHub: `https://github.com/Archiepatel823`
* Project Repository: `https://github.com/Archiepatel823/Enterprise-ai-agent-platform`

---

## License

This project is licensed under the terms specified in the MIT(LICENSE) file.
