# FairQuote: Agentic AI Underwriting System

## Table of Contents
1. [Problem Statement](#problem-statement)
2. [Solution Overview](#solution-overview)
3. [Architecture](#architecture)
4. [Tech Stack](#tech-stack)
5. [AWS Services](#aws-services)
6. [Setup](#setup)
7. [API Endpoints](#api-endpoints)
8. [Future Roadmap](#future-roadmap)

---

## Problem Statement

Traditional insurance underwriting is slow and manual:

- Users fill lengthy forms and upload documents repeatedly
- No real-time validation or document extraction
- Premium calculations lack transparency
- Policy generation takes days
- Poor user experience across multiple systems

**Business Need**: Reduce underwriting from days to minutes with automated processing and transparent pricing.

---

## Solution Overview

FairQuote is an AI-powered multi-agent system that handles the complete insurance workflow in a single conversation.

**Key Features**:
- Multi-agent orchestration for intake, pricing, and policy generation
- Intelligent document processing with Landing AI
- Transparent risk scoring and premium calculations
- Real-time DVLA vehicle validation via AWS Lambda
- Conversational interface with persistent memory

---

## Architecture

### Agent Hierarchy

```
ORCHESTRATOR AGENT
├── Routes requests to specialized agents
├── Manages conversation flow
└── Maintains session state

    ├── INTAKE AGENT
    │   ├── Collects vehicle and driver data
    │   ├── DVLA vehicle lookup
    │   └── Document extraction (Landing AI)
    │
    ├── PRICING AGENT
    │   ├── Risk assessment
    │   ├── Premium calculation
    │   └── Personalized recommendations
    │
    └── POLICY AGENT
        ├── RAG-based clause retrieval
        ├── Policy document generation
        └── Terms explanation
```

### Agent Responsibilities

**Orchestrator Agent**
- Analyzes user intent
- Routes to appropriate agent
- Enforces workflow order (intake → pricing → policy)
- Manages session memory

**Intake Agent**
- Conversationally collects information
- Validates vehicle via DVLA Lambda
- Extracts data from uploaded documents using Landing AI
- Returns structured intake summary

**Pricing Agent**
- Calculates risk score (0-1 scale)
- Computes premium with transparent breakdown
- Provides personalized recommendations via RAG

**Policy Agent**
- Retrieves relevant policy clauses from Bedrock Knowledge Base
- Assembles complete policy document
- Explains terms in plain English

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Agent Framework** | Strands Agents | Multi-agent orchestration |
| **LLM** | AWS Bedrock (Claude 3 Haiku) | Foundation model |
| **Memory** | Bedrock AgentCore Memory | Session management |
| **API** | FastAPI + Uvicorn | REST API backend |
| **Frontend** | Streamlit | Web interface |
| **Document Processing** | Landing AI | Agentic document extraction and OCR |
| **Vehicle Validation** | AWS Lambda | DVLA lookup |
| **RAG** | Bedrock Knowledge Base | Policy clause retrieval |

---

## AWS Services

- AWS Bedrock (Anthropic Claude sonnet 4.5 and haiku 4.5,  and Amazon Titan Text Embeddings models)
- AWS Lambda
- Bedrock Knowledge Base
- Bedrock AgentCore Memory
- CloudWatch
- IAM

---

## Setup

### Prerequisites
- Python 3.10+
- AWS Account with Bedrock and Lambda access

### Installation

```bash
# Clone repository
git clone https://github.com/krishnagopika/FairQuote.git
cd FairQuote/underwriting-agentic-service

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env file with:
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20250101-v1:0
POLICY_KNOWLEDGE_BASE_ID=your_kb_id
MEM_ID=your_memory_id
```

### Running the Service

**Option 1: FastAPI Backend**
```bash
python main.py
# Server runs on http://localhost:8000
```

**Option 2: Streamlit UI**
```bash
cd Frontend
streamlit run app.py
# UI opens on http://localhost:8501
```

---

## API Endpoints

**Base URL**: `http://localhost:8000`

### Health Check
```
GET /health
```

### Create Session
```
POST /sessions/create
Body: {"session_id": "optional-id"}
```

### Send Message
```
POST /chat
Body: {
  "session_id": "uuid",
  "message": "I have a 2020 Toyota Corolla"
}
```

### Upload Document
```
POST /chat/upload
Body (multipart):
- session_id
- message
- file (PDF/image)
```

### Get History
```
GET /sessions/{session_id}/history
```

### Delete Session
```
DELETE /sessions/{session_id}
```

---

## Future Roadmap

### Phase 1: Optimization
- AgentCore gateway patterns for improved observability
- AgentCore Runtime deployment
- Enhanced monitoring and tracing

### Phase 2: Scaling
- OAuth2 authentication
- Redis session store for multi-instance deployments
- OpenSearch for high-volume RAG queries

### Phase 3: Intelligence
- ML-based adaptive risk models
- Human-in-the-loop workflows
- Multi-language support
---

## License
MIT License


**Built with AWS Bedrock, Landing AI, and Strands Agents**
