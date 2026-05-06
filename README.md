# Bearcat Brain

**Institutional AI Tutoring Platform — Saint Vincent College, Computing and Information Systems Department**

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture and Technology Stack](#2-architecture-and-technology-stack)
3. [Repository Structure](#3-repository-structure)
4. [Prerequisites](#4-prerequisites)
5. [Setup and Installation](#5-setup-and-installation)
6. [Data Ingestion Pipeline](#6-data-ingestion-pipeline)
7. [Security and Authentication](#7-security-and-authentication)
8. [Development Team and License](#8-development-team-and-license)

---

## 1. Executive Summary

Bearcat Brain is a locally hosted, privacy-first AI tutoring platform engineered for the Saint Vincent College (SVC) Computing and Information Systems (CIS) Department. The system is purpose-built to support undergraduate students enrolled in C++ programming coursework, providing real-time, context-aware pedagogical assistance without reliance on external commercial AI APIs or cloud infrastructure.

The platform is grounded in a Socratic instructional philosophy. The underlying language model is constrained by a system prompt that enforces academic integrity at the inference level: the system will guide a student through debugging strategies, syntax analysis, and algorithmic reasoning, but will not generate final, compilable code solutions for any graded assignment. This design ensures that the tool functions as a learning accelerator rather than an academic integrity liability.

All computation, model inference, vector storage, and user data remain within the institution's network boundary. No student query, session token, or curriculum embedding is transmitted to a third-party service.

---

## 2. Architecture and Technology Stack

Bearcat Brain employs a decoupled, multi-tier architecture. Each layer is independently deployable and communicates over well-defined internal interfaces.

### 2.1 Frontend

| Component | Technology |
|---|---|
| UI Framework | React.js (Vite build toolchain) |
| Client-Side Routing | React Router |
| Global State Management | React Context API |
| Web Server / Reverse Proxy | Nginx |

The frontend is a single-page application (SPA) served by Nginx, which also functions as an internal reverse proxy, forwarding authenticated API requests to the FastAPI backend. Vite provides optimized production bundling and a high-performance local development server.

### 2.2 Backend

| Component | Technology |
|---|---|
| API Framework | FastAPI (Python, ASGI) |
| AI Inference Engine | Ollama (`llama3.1:8b`, local instance) |
| Vector Store (RAG) | ChromaDB (persistent local embeddings) |
| Relational Database | MySQL 8.0+ |
| Authentication Protocol | LDAP (Active Directory) with JWT |

The backend is an asynchronous Python API built on FastAPI. All AI inference is handled by a locally running Ollama instance serving the `llama3.1:8b` model. Retrieval-Augmented Generation (RAG) is implemented via ChromaDB, which stores vector embeddings of SVC curriculum materials — including syllabi, textbooks, and code examples — enabling the model to ground its responses in course-specific context.

MySQL serves as the persistent relational store for chronological conversation logs and session state. Authentication is delegated entirely to the institution's Active Directory via LDAP, with session continuity managed through stateless JSON Web Tokens.

### 2.3 System Interaction Diagram

```
+-------------------+        HTTPS / Nginx Proxy        +--------------------+
|   React Frontend  | <================================> |  FastAPI Backend   |
|   (Vite / SPA)    |                                    |  (Uvicorn / ASGI)  |
+-------------------+                                    +--------------------+
                                                               |       |       |
                                          +--------------------+       |       +-------------------+
                                          |                            |                           |
                                   +------+------+             +-------+------+           +--------+------+
                                   |   Ollama    |             |   ChromaDB   |           |     MySQL     |
                                   | llama3.1:8b |             | (RAG / Embed)|           | (Session Logs)|
                                   +-------------+             +--------------+           +---------------+
                                                                                                  |
                                                                                      +-----------+---------+
                                                                                      | Active Directory    |
                                                                                      | (LDAP Auth)         |
                                                                                      +---------------------+
```

---

## 3. Repository Structure

```text
Bearcat-Brain/
|
+-- frontend/                        # React SPA, Vite configuration, and static assets
|   +-- src/
|   |   +-- components/              # Reusable UI components
|   |   +-- context/                 # React Context API providers
|   |   +-- pages/                   # Route-level page components
|   |   +-- App.jsx                  # Root application component and router
|   |   +-- main.jsx                 # Vite entry point
|   +-- public/                      # Static public assets
|   +-- .env                         # Frontend environment variables (see Section 5.2)
|   +-- vite.config.js               # Vite build and dev server configuration
|   +-- package.json                 # Node.js dependency manifest
|
+-- backend/                         # FastAPI application, database connectors, and auth logic
|   +-- app/                         # Core API application package
|   |   +-- main.py                  # FastAPI application instance and route registration
|   |   +-- routes/                  # API endpoint definitions (chat, auth, session)
|   |   +-- middleware/              # JWT validation and LDAP auth middleware
|   |   +-- models/                  # Pydantic request/response schemas
|   +-- bearcat_sql.py               # MySQL connection pool and chat log query interface
|   +-- private.py                   # Local credential configuration (gitignored)
|   +-- aiWdb.py                     # CLI testing harness for adversarial and CoT evaluation
|   +-- .env                         # Backend environment variables (see Section 5.2)
|   +-- requirements.txt             # Python dependency manifest
|
+-- ingestion/                       # Offline data pipeline for populating ChromaDB
|   +-- ingest_pdf.py                # PDF processor: syllabi and textbooks (page metadata)
|   +-- ingest_code.py               # Code processor: C++ repositories (batched chunking)
|   +-- ingest.py                    # Plaintext processor: lecture notes and references
|   +-- source_documents/            # Staging directory for raw ingestion materials (gitignored)
|
+-- README.md                        # Project documentation (this file)
```

> **Note:** The files `backend/private.py`, `backend/.env`, `frontend/.env`, and `ingestion/source_documents/` are excluded from version control. They must be provisioned manually on each deployment target as described in Section 5.

---

## 4. Prerequisites

The following software must be installed and operational on the target host before attempting deployment. Version constraints are enforced.

| Dependency | Minimum Version | Purpose |
|---|---|---|
| Python | 3.10 | Backend runtime and ingestion scripts |
| Node.js | 18.0 (LTS) | Frontend build toolchain |
| npm | 9.0 | Frontend package management |
| MySQL Server | 8.0 | Relational session and log storage |
| Ollama | Latest stable | Local LLM inference runtime |
| Nginx | 1.18 | Frontend serving and reverse proxy |

Additionally, the `llama3.1:8b` model must be pulled to the local Ollama instance prior to starting the backend:

```bash
ollama pull llama3.1:8b
```

Active Directory access credentials and a network-reachable Domain Controller are required for LDAP authentication to function. Consult the institution's IT department for `DC_HOST` and `DC_DOMAIN` values.

---

## 5. Setup and Installation

Follow the steps below in the prescribed sequence. Deviating from this order may result in dependency or connectivity failures at runtime.

### 5.1 Database Configuration

Connect to the MySQL server and provision the application database and schema:

```sql
CREATE DATABASE bearcat_brain CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE bearcat_brain;

CREATE TABLE chat_logs (
    id            INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    username      VARCHAR(100)    NOT NULL,
    session_id    VARCHAR(255)    NOT NULL,
    role          ENUM('user', 'assistant') NOT NULL,
    content       TEXT            NOT NULL,
    created_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_session (session_id),
    INDEX idx_user (username)
);
```

Once the schema is initialized, open `backend/private.py` and populate the database credentials:

```python
# backend/private.py
DB_HOST     = "your_mysql_host"
DB_PORT     = 3306
DB_USER     = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_NAME     = "bearcat_brain"
```

### 5.2 Environment Variable Configuration

**Backend** — Create `backend/.env` with the following keys:

```env
# backend/.env

# Active Directory / LDAP Configuration
DC_HOST=your_domain_controller_ip
DC_DOMAIN=your_domain_name

# JSON Web Token
JWT_SECRET=your_cryptographically_secure_secret
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=480
```

**Frontend** — Create `frontend/.env` with the following key:

```env
# frontend/.env

VITE_API_URL=http://localhost:8000
```

> **Security Notice:** Neither `.env` file nor `private.py` should ever be committed to version control. Confirm that `.gitignore` entries for these files are present and respected before pushing to any repository.

### 5.3 Backend Initialization

Navigate to the backend directory, establish an isolated virtual environment, install all Python dependencies, and start the ASGI server:

```bash
cd backend

# Create and activate the virtual environment
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI application via Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables hot-reloading during development. Remove this flag for production deployments.

The API will be accessible at `http://localhost:8000`. Interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs`.

### 5.4 Frontend Initialization

In a separate terminal session, navigate to the frontend directory, install Node dependencies, and start the Vite development server:

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start the Vite development server
npm run dev
```

The frontend will be accessible at `http://localhost:5173` by default. For a production build suitable for Nginx deployment, execute:

```bash
npm run build
```

The compiled static assets will be written to `frontend/dist/`, which should be configured as the Nginx root directory.

---

## 6. Data Ingestion Pipeline

The RAG knowledge base is populated offline using the three ingestion scripts located in the `ingestion/` directory. These scripts process raw curriculum materials, generate vector embeddings, and persist them to the local ChromaDB instance. The knowledge base must be rebuilt any time course materials are updated for a new semester.

All source materials must be placed in the `ingestion/source_documents/` directory prior to execution.

### 6.1 PDF Ingestion (`ingest_pdf.py`)

Processes course syllabi and textbook files in PDF format. Each page is extracted as a discrete document chunk, and the originating page number is attached as metadata. This metadata enables the language model to provide precise, citable references when drawing on textbook content during a tutoring session.

```bash
cd ingestion
python ingest_pdf.py
```

### 6.2 Code Repository Ingestion (`ingest_code.py`)

Processes C++ source files (`.cpp`, `.h`) from course code repositories. To prevent ChromaDB from exceeding memory allocation limits during large batch operations, this script processes and uploads embeddings in chunks of 5,000 tokens. This approach ensures reliable ingestion of complete code repositories without runtime failures.

```bash
cd ingestion
python ingest_code.py
```

### 6.3 Plaintext Ingestion (`ingest.py`)

Processes standard plaintext files, including lecture notes, supplemental references, and instructor-authored guides. This script is suitable for any unstructured text content that does not require the specialized handling of the PDF or code processors.

```bash
cd ingestion
python ingest.py
```

> **Operational Note:** The ingestion scripts are designed to be run offline by a system administrator or designated faculty member. They do not need to be re-executed at system startup. The ChromaDB store persists to disk and remains available to the backend across restarts.

---

## 7. Security and Authentication

The security architecture of Bearcat Brain is designed around the principle of minimal data exposure. The system handles authentication credentials transiently, stores only interaction metadata, and applies defense-in-depth measures at the session and database layers.

### 7.1 Zero Credential Storage

User authentication is performed entirely through direct LDAP binding against the institution's Active Directory. The application never receives plaintext passwords in a form that could be logged or persisted. The MySQL database contains no password fields, hashed or otherwise. The only user-identifying data stored is the authenticated username, which is used to associate conversation logs with a session.

### 7.2 Session Management via JSON Web Tokens

Upon successful LDAP authentication, the backend issues a signed JSON Web Token (JWT). The token is transmitted to the client exclusively via an `HttpOnly`, `Secure`, `SameSite=Strict` cookie. This configuration provides the following protections:

- `HttpOnly`: Prevents client-side JavaScript from accessing the cookie, eliminating token theft via cross-site scripting (XSS) attacks.
- `Secure`: Enforces transmission over HTTPS only, preventing interception over unencrypted connections.
- `SameSite=Strict`: Blocks the cookie from being sent with cross-site requests, mitigating cross-site request forgery (CSRF) attack vectors.

Sessions are stateless; the backend does not maintain a server-side session store. Token validity is verified on each protected request via JWT signature validation.

### 7.3 SQL Injection Prevention

All database interactions in `bearcat_sql.py` are executed exclusively through parameterized queries. User-supplied input is never interpolated directly into a SQL string. This categorically prevents SQL injection attacks regardless of query content.

### 7.4 Adversarial Testing and Prompt Evaluation

The repository includes `backend/aiWdb.py`, a command-line interface (CLI) testing harness that enables direct interaction with the model stack outside of the frontend application. This tool was used during development for two distinct evaluation workstreams:

- **Red Team / Adversarial Testing:** Systematic attempts to circumvent the system prompt's academic integrity constraints through prompt injection, role-playing directives, and jailbreak vectors.
- **Chain-of-Thought (CoT) Evaluation:** Assessment of the model's reasoning quality, citation accuracy, and adherence to the Socratic instructional philosophy across a defined set of representative student queries.

---

## 8. Development Team and License

### Development Team

Bearcat Brain was designed and engineered as a Senior Capstone Project for the Saint Vincent College Computing and Information Systems Department.

| Name |
|---|
| Dylan Sever |
| Cameron Black |
| Owen Dzurko |
| Alex Leskovansky |
| Philo Bassous |

### License

This software is proprietary. All rights are reserved by the development team and the Saint Vincent College Computing and Information Systems Department. The source code, architecture, and associated documentation may not be reproduced, distributed, or deployed in any external or commercial context without explicit written authorization from the rights holders.

