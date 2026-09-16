# ⚒️ jobForge

### AI-Powered Job Discovery, Resume Tailoring, Application & Tracking Platform

**jobForge** is a personal AI-powered job-search automation platform that helps streamline the complete job application lifecycle — from discovering relevant opportunities to tailoring resumes, validating them, preparing applications, and tracking application outcomes.

The project integrates **multi-platform job discovery**, **LLM-powered resume tailoring**, **ATS analysis**, **truth/fact validation**, **application automation**, and a centralized **application tracking dashboard** into one workflow.

> **Goal:** Turn job searching from a repetitive manual process into an organized, intelligent, and auditable workflow.

---

## 🚀 What jobForge Does

jobForge follows a complete job-search pipeline:

```text
Candidate Profile
       │
       ▼
┌─────────────────────┐
│   Job Discovery     │
│ LinkedIn / Naukri   │
│ Indeed / Wellfound  │
│ Instahyre / etc.    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ JD Retrieval &      │
│ Normalization       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Job Deduplication   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Match Analysis      │
│ & Eligibility Gate  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Resume Tailoring    │
│ GPT / Claude /      │
│ Gemini              │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Truth + ATS         │
│ Validation          │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Review / Approval   │
│ Queue               │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Application Adapter │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Application Ledger  │
│ & Analytics         │
└─────────────────────┘
```

---

## ✨ Key Features

### 🔎 Multi-Platform Job Discovery

Discover relevant jobs through platform-specific adapters.

Supported platforms from the integrated source repositories include:

* LinkedIn
* Naukri
* Indeed
* Wellfound
* Hirist
* Glassdoor
* Instahyre
* Cutshort

Platform availability depends on the capabilities and permitted automation routes of each connector.

---

### 📄 Job Description Intelligence

jobForge converts raw job listings into a canonical job representation.

It can extract:

* Job title
* Company
* Location
* Experience requirements
* Must-have skills
* Nice-to-have skills
* Education requirements
* Work mode
* Employment type
* Salary information
* Application constraints
* Relevant keywords

Raw JD information is preserved where possible for auditability.

---

### 🧠 Explainable Job Matching

Instead of relying on a black-box recommendation, jobForge breaks down candidate-job compatibility.

Default matching dimensions include:

| Dimension                  | Weight |
| -------------------------- | -----: |
| Role / Title Alignment     |    25% |
| Must-Have Skill Coverage   |    30% |
| Experience Fit             |    15% |
| Location / Work Mode       |    10% |
| Education / Certification  |     5% |
| Domain / Project Relevance |    10% |
| Nice-to-Have Coverage      |     5% |

The weights are configurable, and missing critical requirements can trigger an eligibility failure even when the overall score is high.

---

### 🤖 Multi-LLM Resume Tailoring

Generate a job-specific resume from:

* Candidate master profile
* Master resume
* Job description
* Match analysis
* Selected resume template

Supported provider abstraction:

* OpenAI
* Anthropic
* Google Gemini

The provider interface is designed so the resume pipeline remains independent of a specific LLM provider.

---

### 🛡️ AI Truth & No-Fabrication Guard

One of the core principles of jobForge is:

> **Tailor the resume — never fabricate the candidate.**

Generated resumes cannot introduce unsupported:

* Skills
* Employers
* Job titles
* Dates
* Certifications
* Projects
* Metrics
* Responsibilities
* Achievements

Every material claim should be traceable to candidate evidence.

For example:

```text
JD:
AWS required

Candidate Profile:
No AWS experience

Result:
❌ Do not add AWS to resume
⚠️ Report AWS as a skill gap
```

---

### 📊 ATS Validation

Before an application reaches the approval stage, jobForge can evaluate:

* Keyword coverage
* Missing requirements
* Resume section structure
* Contact information
* Chronology
* Parsing friendliness
* File integrity

Importantly, a missing keyword is distinguished from a missing candidate skill — the system does not simply insert keywords to inflate an ATS score.

---

### 👤 Human Approval Workflow

Applications are **review-gated by default**.

The user can inspect:

* Job description
* Match analysis
* Missing requirements
* Tailored resume
* ATS results
* Evidence behind resume claims
* Application route

Only after approval can an irreversible application submission proceed.

---

### 📋 Application Tracking

Every application is stored in a centralized application ledger.

Tracked information includes:

* Company
* Position
* Platform
* Job URL
* Resume version
* Application status
* Submission timestamp
* Confirmation ID
* Errors
* State transitions
* Notes
* Follow-up information

Duplicate applications are prevented unless the user explicitly retries after a failed attempt.

---

## 🔄 Application Lifecycle

```text
DISCOVERED
    │
    ▼
ELIGIBLE
    │
    ▼
RESUME_GENERATED
    │
    ▼
RESUME_VALIDATED
    │
    ▼
READY_FOR_REVIEW
    │
    ▼
APPROVED
    │
    ▼
SUBMITTING
    │
    ▼
APPLIED
    │
    ├──► FOLLOW_UP
    ├──► INTERVIEW
    ├──► REJECTED
    └──► WITHDRAWN
```

Failure states are explicitly tracked:

```text
RESUME_FAILED
APPLICATION_FAILED
AUTH_REQUIRED
CAPTCHA_REQUIRED
EXTERNAL_SITE
UNSUPPORTED
```

---

# 🏗️ Architecture

jobForge uses a modular architecture with a primary web application layer and isolated platform/application adapters.

```text
                    ┌─────────────────────┐
                    │    Web Dashboard    │
                    │ React / Vite /      │
                    │ Tailwind            │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Application API   │
                    │ Express / TypeScript│
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │     Job     │ │   Resume    │ │ Application │
       │ Orchestrator│ │ Orchestrator│ │ Orchestrator│
       └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
              │                │                │
              ▼                ▼                ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │  Platform   │ │ LLM Router  │ │    Apply    │
       │  Adapters   │ │             │ │   Adapters  │
       └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │   Canonical Data    │
                    │   Prisma + SQLite   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Resumes / Data /    │
                    │ Audit / Sessions    │
                    └─────────────────────┘
```

The architecture keeps platform-specific logic isolated from the core job, matching, resume, and application domain models.

---

# 🧩 Tech Stack

### Frontend

* React
* Vite
* Tailwind CSS

### Backend

* Node.js
* Express
* TypeScript

### Database

* Prisma
* SQLite

### AI / LLM

* OpenAI
* Anthropic Claude
* Google Gemini

### Automation

* Playwright
* MCP
* Platform-specific adapters

### Resume / ATS

* Resume parsing
* Resume generation
* DOCX / PDF generation
* ATS keyword analysis
* Evidence mapping

### Infrastructure

* Docker
* Environment-based configuration
* Configurable scheduler
* Structured logging

---

# 📁 Project Structure

The target integrated repository follows a modular structure:

```text
jobForge/
│
├── backend/
│   ├── src/
│   │   ├── routes/
│   │   ├── services/
│   │   │   ├── jobs/
│   │   │   ├── ai/
│   │   │   ├── resume/
│   │   │   ├── matching/
│   │   │   ├── applications/
│   │   │   ├── orchestration/
│   │   │   └── scheduler/
│   │   │
│   │   ├── adapters/
│   │   │   ├── linkedin/
│   │   │   ├── naukri/
│   │   │   ├── indeed/
│   │   │   ├── wellfound/
│   │   │   ├── hirist/
│   │   │   ├── glassdoor/
│   │   │   ├── instahyre/
│   │   │   └── cutshort/
│   │   │
│   │   ├── db/
│   │   └── lib/
│   │
│   └── prisma/
│
├── frontend/
│
├── mcp/
│   ├── server.py
│   └── tools/
│
├── resumes/
│   ├── master/
│   ├── generated/
│   └── templates/
│
├── data/
├── scripts/
├── docs/
│
├── .env.example
├── docker-compose.yml
└── README.md
```

---

# 🔐 Security & Credentials

For the MVP, jobForge uses **local `.env` configuration** for credentials and secrets.

Example:

```env
# Runtime
NODE_ENV=development
PORT=3001
DATABASE_URL=file:./dev.db
DATA_DIR=./data

# Security
ENCRYPTION_SECRET=<strong-random-secret>

# LLM
LLM_PROVIDER=anthropic
LLM_MODEL=<provider-specific-model>

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=

# Job portals
LINKEDIN_EMAIL=
LINKEDIN_PASSWORD=

NAUKRI_EMAIL=
NAUKRI_PASSWORD=

INDEED_EMAIL=
INDEED_PASSWORD=

FOUNDIT_EMAIL=
FOUNDIT_PASSWORD=

INSTAHYRE_EMAIL=
INSTAHYRE_PASSWORD=

# Browser
PLAYWRIGHT_HEADLESS=false
SESSION_DIR=./data/sessions
```

### ⚠️ Never commit `.env`

The repository should contain:

```text
.env.example
```

but never:

```text
.env
```

Credentials, API keys, cookies, browser sessions, and other secrets must not appear in logs, prompts, API responses, screenshots, or Git history.

---

# ⚙️ Getting Started

## 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd jobForge
```

## 2. Configure environment variables

```bash
cp .env.example .env
```

Then configure the required LLM and platform credentials.

> On Windows, manually copy `.env.example` to `.env` if `cp` is unavailable.

---

## 3. Install dependencies

```bash
npm install
```

If the project contains separate frontend/backend packages:

```bash
cd backend
npm install

cd ../frontend
npm install
```

---

## 4. Configure the database

Run the Prisma migration:

```bash
npx prisma migrate dev
```

---

## 5. Start the application

Development:

```bash
npm run dev
```

The exact startup commands may vary depending on the final integrated repository structure.

---

# 🧪 Core Smoke Test

The recommended first end-to-end test is:

### Candidate

```text
Role:
Generative AI Engineer

Skills:
Python
LLM
RAG
LangChain
FastAPI
Docker
```

### Test Job Description

```text
Required:
Python
LLM
RAG
AWS
FastAPI
```

### Expected behavior

```text
✓ Match score calculated
✓ AWS identified as a missing requirement
✓ Resume generated
✓ AWS NOT added to resume
✓ ATS report generated
✓ Application remains READY_FOR_REVIEW
```

After user approval:

```text
READY_FOR_REVIEW
        ↓
APPROVED
        ↓
APPLICATION ADAPTER
        ↓
SUBMISSION
        ↓
APPLICATION LEDGER
```

---

# 🛡️ Responsible Automation

jobForge is designed around **controlled automation**, not bypassing platform security.

The project does **not** implement:

* CAPTCHA bypass
* Anti-bot evasion
* Stealth automation
* Login challenge circumvention
* Platform restriction bypass
* Mass scraping designed to overload services

When automation is not permitted or a platform requires additional user interaction, the workflow should fall back to a user-assisted process.

Platform capabilities can be represented as:

```text
SEARCH_ONLY
REVIEW_ONLY
DIRECT_APPLY
UNSUPPORTED
```

---

# 📊 Dashboard

The dashboard is designed around several major views:

### Job Inbox

* Job discovery
* Match scores
* Filters
* Sources
* Locations
* Application state
* Deduplication indicators

### Job Details

* Complete JD
* Structured requirements
* Match explanation
* Missing skills
* Application route

### Resume Review

* Tailored resume
* Highlighted changes
* Evidence links
* ATS score
* Validation status

### Approval Queue

* Approve
* Reject
* Regenerate
* Edit
* Review exact resume version

### Applications

* Application status
* Company
* Role
* Platform
* Resume version
* Timeline
* Notes

### Analytics

* Applications by platform
* Applications by role
* Applications by company
* Response rate
* Resume version outcomes
* Frequently requested skills

---

# 🗺️ Development Roadmap

| Milestone | Goal                         |
| --------- | ---------------------------- |
| **M1**    | Integrated shell             |
| **M2**    | Multi-platform job discovery |
| **M3**    | AI match analysis            |
| **M4**    | Resume generation            |
| **M5**    | Truth + ATS validation       |
| **M6**    | Application adapters         |
| **M7**    | Centralized tracking         |
| **M8**    | Scheduler + automation       |
| **M9**    | Testing + hardening          |

---

# 🎯 Design Principles

jobForge is built around several core principles:

### 1. One Candidate Profile

The candidate master profile remains the source of truth.

### 2. Evidence-Bound AI

LLMs can rewrite and optimize existing information, but cannot invent candidate facts.

### 3. Explainability

Job matches and resume changes should be understandable and traceable.

### 4. Human-in-the-Loop

Irreversible application submissions require user approval by default.

### 5. Canonical Data

Jobs, applications, resumes, and events use a unified data model.

### 6. Idempotency

Restarting a workflow should not create duplicate jobs or applications.

### 7. Modular Adapters

Platform-specific logic remains isolated so individual platform failures do not bring down the entire system.

### 8. Auditability

Every application should be traceable back to:

```text
Job
  ↓
Match Analysis
  ↓
Resume Version
  ↓
Approval
  ↓
Application
  ↓
Application Events
```

---

# 📈 Long-Term Vision

jobForge is intended to evolve into a complete **personal recruiting operations platform**.

Future iterations can build on the foundation to provide:

```text
        JOB MARKET
             │
             ▼
      ┌──────────────┐
      │ Job Discovery│
      └──────┬───────┘
             │
             ▼
       AI MATCHING
             │
             ▼
     RESUME OPTIMIZATION
             │
             ▼
       ATS VALIDATION
             │
             ▼
       HUMAN REVIEW
             │
             ▼
        APPLICATION
             │
             ▼
       TRACKING & DATA
             │
             ▼
      CAREER ANALYTICS
```

The objective is not simply to automate applications, but to create a **structured feedback loop between job-market requirements, candidate skills, resumes, and application outcomes**.

---

# 📚 Source Projects

jobForge's integration architecture is based on capabilities from:

* `job-apply-mcp`
* `JobPilot`

The integration specification identifies JobPilot as the primary application/dashboard shell and `job-apply-mcp` as the primary source for additional platform and application adapters.

---

# ⚠️ Disclaimer

jobForge is intended for personal productivity and controlled job-search automation.

Users are responsible for ensuring their use of job platforms, browser automation, credentials, and application workflows complies with the applicable platform rules, terms, and policies.

---

# ⭐ Project Status

**Status:** 🚧 Active Development

jobForge is currently being developed as an integrated AI job-search and application automation platform.

The current implementation follows the integration specification defined for the project, with incremental development preferred over a large-scale rewrite.

---

## 🤝 Contributing

Contributions, suggestions, issues, and improvements are welcome.

If you find a bug or have an idea for improving jobForge:

1. Open an issue.
2. Describe the problem or proposed improvement.
3. Include relevant logs or reproduction steps.
4. Submit a pull request where appropriate.

---

## 📄 License

Add your chosen license here.

```text
© 2026 jobForge
```
