**PRODUCT REQUIREMENTS DOCUMENT**

**AI Job Discovery, Resume Tailoring, Application & Tracking System**

Integration PRD for JobPilot + job-apply-mcp

Implementation handoff for an AI coding agent  
Version 1.1 \| 9 September 2026

*Objective: clone both repositories, place them in one workspace, and use this document as the authoritative integration specification.*

Revision 1.1: MVP credential and secret management is explicitly .env-only (Method A).

# 1. Executive Summary

The target product is a personal AI job-search and application system that discovers relevant jobs across supported job platforms, retrieves and normalizes job descriptions (JDs), evaluates fit against a candidate master profile, generates a job-specific resume with an LLM such as OpenAI GPT, Anthropic Claude, or Google Gemini, validates the generated resume for ATS quality and factual consistency, submits applications through permitted automation paths, and records every job/application event for later review.

The recommended implementation is a deliberate integration of two repositories rather than a wholesale merge. job-apply-mcp should be treated as the platform-search/application execution layer, while JobPilot should contribute the web dashboard, resume management, ATS functionality, multi-provider AI abstractions, job-facing APIs, and application analytics. The final system should have one canonical data model, one application ledger, one candidate profile, and one orchestration workflow.

| **Area**              | **Primary source**       | **Integration role**                                                    |
|-----------------------|--------------------------|-------------------------------------------------------------------------|
| Job discovery/search  | job-apply-mcp            | Reuse and adapt platform connectors and search/filter logic.            |
| JD retrieval          | job-apply-mcp + JobPilot | Normalize full JD into canonical Job object.                            |
| Match scoring         | job-apply-mcp / JobPilot | Unify into one explainable 0-100 score.                                 |
| LLM providers         | JobPilot                 | Retain OpenAI, Anthropic, Gemini provider abstraction.                  |
| Resume tailoring      | JobPilot                 | Extend to per-job output with evidence-bound generation.                |
| ATS validation        | JobPilot                 | Use ATS scanner and add factual/no-fabrication guard.                   |
| Application execution | job-apply-mcp            | Reuse platform-specific Playwright workflows where permitted.           |
| Tracking/database     | JobPilot + job-apply-mcp | Consolidate into one Prisma/SQLite ledger; migrate MCP tracking fields. |
| Dashboard             | JobPilot                 | Use as the primary UI and add integrated review/approval queue.         |

## 1.1 Authoritative implementation decision

Do not choose one repository and throw the other away. Clone both. Preserve the strongest parts of each and make the integration layer the new source of truth. The coding agent should first inventory both codebases, map equivalent capabilities, and then implement the target architecture defined below.

## 1.2 Critical platform/compliance principle

The integration must not include anti-detection, CAPTCHA bypass, stealth evasion, or other mechanisms designed to defeat platform controls. Where a platform or application route does not permit automation, the system must switch to a user-assisted/manual approval flow. The codebase should expose platform capability states such as SEARCH_ONLY, REVIEW_ONLY, DIRECT_APPLY, and UNSUPPORTED.

# 2. Source Repository Assessment

The assessment below is based on the current repository READMEs and repository structure available at the time of this PRD.

| **Repository**          | **Observed strengths**                                                                                                                                                                           | **Observed gaps for target product**                                                                                                                                                      |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| pulkit017/job-apply-mcp | 8 job portals; Playwright browser automation; search/filter/JD fetch; skill/role/location scoring; application tools; SQLite tracking; persistent sessions; CLI + MCP use.                       | No full integrated resume-tailoring/ATS workflow; profile/config is relatively simple; direct-apply focus; skips external application sites by default.                                   |
| Harshitsk7/jobpilot     | React/Vite/Tailwind dashboard; Express/TypeScript; Prisma/SQLite; LinkedIn + Naukri discovery; match scoring; resume tailoring; ATS; LaTeX editor; multi-LLM support; apply tracking; analytics. | Fewer platform connectors than MCP; integration breadth must come from MCP-style adapters; resume guardrails need strengthening; orchestration is not yet the target autonomous pipeline. |

job-apply-mcp documents eight supported platforms - LinkedIn, Naukri, Wellfound, Indeed, Hirist, Glassdoor, Instahyre, and Cutshort - and exposes tools including search_jobs, filter_jobs, apply_job, bulk_apply, get_application_status, and save_session. (Source: job-apply-mcp GitHub repository/README, accessed 9 Sep 2026.)

JobPilot documents LinkedIn and Naukri scraping, AI match scoring, resume tailoring, ATS scanning, multi-provider AI via Anthropic/OpenAI/Gemini/Copilot, LinkedIn Easy Apply automation, application tracking, dashboard analytics, and a Prisma/SQLite backend. (Source: JobPilot GitHub repository/README, accessed 9 Sep 2026.)

# 3. Product Vision and Scope

The product should behave like a controlled personal recruiting operations system, not merely a scraper or a resume generator.

> Candidate Master Profile  
> \|  
> v  
> Scheduled Job Discovery ---\> Canonical Job Store ---\> De-duplication  
> \| \|  
> v v  
> Full JD retrieval ---\> Match Analysis ---\> Eligibility Gate  
> \|  
> v  
> Resume Tailoring Agent  
> GPT / Claude / Gemini  
> \|  
> v  
> Factual + ATS Validation  
> \|  
> v  
> Review / Apply Queue  
> \|  
> v  
> Platform/ATS Application Adapter  
> \|  
> v  
> Application Ledger  
> \|  
> v  
> Dashboard / Analytics

## 3.1 In scope

- Unified candidate profile and master resume.

- Job discovery from the connectors available in the combined codebase, subject to each platform's permitted automation capabilities.

- Canonical extraction and storage of complete JDs.

- Job normalization and de-duplication across platforms.

- Explainable job-to-candidate match scoring.

- LLM-driven per-job resume tailoring using OpenAI, Anthropic, or Gemini.

- Evidence-bound resume generation: no fabricated experience, metrics, employers, certifications, dates, or skills.

- ATS-oriented validation and keyword coverage reporting.

- Generation of PDF/DOCX (and optionally LaTeX) resume artifacts.

- Application preparation and permitted submission automation.

- Human approval before irreversible submissions by default.

- Centralized application tracking and duplicate-application prevention.

- Dashboard for discovered jobs, tailored resumes, applications, statuses, and analytics.

- Audit trail showing which JD produced which resume and which resume was submitted.

## 3.2 Out of scope for MVP

- Circumventing login challenges, CAPTCHAs, anti-bot controls, paywalls, or platform restrictions.

- Automatic fabrication of answers to application questions.

- Autonomous submission without an approval policy configured by the user.

- Mass scraping at a frequency likely to violate platform policies or overload services.

- Enterprise multi-tenant user management.

- Training a custom LLM.

- Guaranteeing interview outcomes or ATS pass rates.

# 4. Functional Requirements

## FR-01 Candidate Master Profile

The system shall maintain a structured, source-of-truth profile separate from generated resumes.

| **Field group** | **Required contents**                                                                                    |
|-----------------|----------------------------------------------------------------------------------------------------------|
| Identity        | Name, email, phone, current location, LinkedIn/portfolio/GitHub URLs.                                    |
| Targeting       | Target roles, preferred cities/remote, employment types, minimum/maximum experience, salary constraints. |
| Skills          | Canonical skill list with optional proficiency/years, aliases, evidence references.                      |
| Experience      | Employer, title, dates, location, responsibilities, achievements, technologies, measurable outcomes.     |
| Education       | Degree, institution, dates, location, relevant coursework if explicitly provided.                        |
| Certifications  | Name, issuer, date, credential ID if applicable.                                                         |
| Projects        | Project name, description, tech stack, role, outcomes, links.                                            |
| Preferences     | Excluded roles/keywords, companies, notice period, work authorization, relocation preferences.           |

## FR-02 Job Discovery

A scheduler or on-demand workflow shall call platform adapters to retrieve new jobs. Adapters must return a common JobListing schema. The system must support incremental discovery and should avoid re-fetching known listings unnecessarily.

Minimum canonical job fields:

> JobListing {  
> id  
> source  
> source_job_id  
> url  
> title  
> company  
> location  
> posted_at  
> discovered_at  
> external_apply_url?  
> jd_raw  
> jd_normalized  
> job_type?  
> experience_min?  
> experience_max?  
> salary_text?  
> source_status  
> }

## FR-03 JD Retrieval & Normalization

- Preserve raw JD text exactly as retrieved whenever possible for auditability.

- Normalize whitespace, sections, bullet styles, and repeated boilerplate without altering meaning.

- Extract structured requirements: must-have skills, nice-to-have skills, experience, education, location, work authorization, employment type, salary when present.

- Record retrieval timestamp and source URL.

- If the source only provides a summary, mark jd_completeness as PARTIAL and do not falsely claim the full JD was retrieved.

## FR-04 De-duplication

The same role may appear on several platforms. Create a canonical job identity using a deterministic key plus similarity matching.

> Primary dedupe keys (ordered):  
> 1. source + source_job_id  
> 2. normalized external_apply_url  
> 3. company + normalized title + normalized location  
> 4. semantic similarity of JD text above configured threshold  
>   
> The system must keep source_occurrences\[\] so that one canonical job can retain all discovered platform URLs.

## FR-05 Match Scoring

Scoring must be explainable and deterministic enough for debugging.

| **Dimension**            | **Default weight** | **Example**                                    |
|--------------------------|--------------------|------------------------------------------------|
| Role/title alignment     | 25%                | Target title and adjacent-role mapping.        |
| Must-have skill coverage | 30%                | Required skills present in candidate evidence. |
| Experience fit           | 15%                | Years and seniority range.                     |
| Location/work mode       | 10%                | Preferred location/remote fit.                 |
| Education/certification  | 5%                 | Only when explicitly required.                 |
| Domain/project relevance | 10%                | Similarity of prior projects/industry.         |
| Nice-to-have coverage    | 5%                 | Optional skill overlap.                        |

All weights must be configurable. A missing must-have requirement should reduce the score and may trigger an ineligible state even when the overall numeric score is high.

## FR-06 LLM Provider Abstraction

Use one provider interface so the resume pipeline is provider-agnostic.

> LLMProvider  
> - generate_structured(prompt, schema)  
> - generate_text(prompt)  
> - get_model_metadata()  
>   
> Providers:  
> OpenAIProvider  
> AnthropicProvider  
> GeminiProvider  
>   
> Configuration:  
> active_provider  
> model  
> temperature  
> max_output_tokens  
> retry_policy

Provider fallback must be explicit and logged. A fallback must never silently change model policy for regulated or sensitive data.

## FR-07 Resume Tailoring

For each eligible job, the system shall create a job-specific resume variant from the master profile and a selected resume template. Tailoring may reorder, compress, clarify, or rephrase authentic evidence. It may not create unsupported claims.

> Inputs:  
> - Master candidate profile  
> - Master resume content / template  
> - Canonical JD  
> - Match analysis  
> - User formatting preferences  
>   
> Outputs:  
> - tailored_resume_structured  
> - tailored_resume_docx  
> - tailored_resume_pdf  
> - tailoring_rationale  
> - keyword_coverage  
> - evidence_map

## FR-08 Truth / No-Fabrication Guard

Every generated claim that could materially affect hiring must be traceable to a candidate source record.

| **Claim class**          | **Allowed behavior**                                             | **Validation**                         |
|--------------------------|------------------------------------------------------------------|----------------------------------------|
| Skills                   | Use only skills in candidate profile/evidence.                   | Exact/alias match + evidence ID.       |
| Years of experience      | May calculate from dated records; never inflate.                 | Derived from employment/project dates. |
| Metrics                  | May restate source metrics; never invent new percentages/counts. | Evidence reference required.           |
| Employer/title/date      | Never change factual identity.                                   | Exact source match.                    |
| Education/certifications | Never invent credentials.                                        | Exact source match.                    |
| Project scope            | Can summarize provided project details.                          | Evidence reference.                    |
| Keywords                 | Can include truthful equivalents/aliases.                        | Must map to an existing capability.    |

## FR-09 ATS Validation

- Compute keyword coverage against the canonical JD.

- Identify missing must-have terms, but distinguish 'missing from resume' from 'candidate does not possess'.

- Check section headings, parsing friendliness, chronology, contact details, and file integrity.

- Provide a score and a list of actionable edits.

- Never add an unsupported keyword solely to improve the numeric score.

## FR-10 Application Preparation

The application workflow shall choose the correct adapter based on source and application route. The application record must be created before submission so that failures remain visible.

> Application lifecycle:  
> DISCOVERED  
> -\> ELIGIBLE  
> -\> RESUME_GENERATED  
> -\> RESUME_VALIDATED  
> -\> READY_FOR_REVIEW  
> -\> APPROVED  
> -\> SUBMITTING  
> -\> APPLIED  
> -\> FOLLOW_UP / INTERVIEW / REJECTED / WITHDRAWN  
>   
> Failure states:  
> RESUME_FAILED  
> APPLICATION_FAILED  
> AUTH_REQUIRED  
> CAPTCHA_REQUIRED  
> EXTERNAL_SITE  
> UNSUPPORTED

## FR-11 Human Approval

Default policy: no irreversible submission without user approval. The approval object should capture the exact resume version and job occurrence being approved.

> Approval {  
> application_id  
> approved_by = "user"  
> approved_at  
> approved_resume_version_id  
> approved_source_occurrence_id  
> policy_version  
> }

## FR-12 Application Tracking

- Prevent duplicate application to the same canonical job unless the user explicitly retries after a failed attempt.

- Store platform, company, role, URL, submission timestamp, resume version, status, and error details.

- Track confirmation/application IDs when available.

- Keep a timeline of state transitions.

- Support notes, recruiter contact, interview date, and next action as optional fields.

- Export CSV/JSON.

# 5. Target Architecture

> +-----------------------------+  
> \| Web Dashboard \|  
> \| Job Search / Review / Apps \|  
> +-------------+---------------+  
> \|  
> v  
> +-----------------------------+  
> \| Application API \|  
> \| Express/TypeScript layer \|  
> +-------------+---------------+  
> \|  
> +--------------------------+--------------------------+  
> \| \| \|  
> v v v  
> Job Orchestrator Resume Orchestrator Application Orchestrator  
> \| \| \|  
> v v v  
> Platform Adapters LLM Router Apply Adapters  
> / search / JD GPT/Claude/Gemini MCP/Playwright  
> \| \| \|  
> +--------------------------+--------------------------+  
> \|  
> v  
> +-------------------------+  
> \| Canonical Data Store \|  
> \| Prisma + SQLite \|  
> +-------------------------+  
> \|  
> v  
> Files / Resumes / Audit

## 5.1 Component ownership

| **Component**        | **Owner after integration**           | **Notes**                                                                                                              |
|----------------------|---------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| Frontend             | JobPilot                              | Keep React/Vite/Tailwind dashboard.                                                                                    |
| Primary API          | JobPilot backend                      | Keep Express/TypeScript as system API.                                                                                 |
| Primary DB           | JobPilot Prisma + SQLite              | Canonical store; migrate MCP application tables/data.                                                                  |
| AI provider layer    | JobPilot services/ai                  | Wrap behind a stable provider interface.                                                                               |
| Resume/ATS           | JobPilot services/resume + ats routes | Extend with evidence mapping and claim validation.                                                                     |
| Job adapters         | New integration module; port from MCP | Do not call MCP as a black box for every internal operation unless useful; prefer reusable adapter/service boundaries. |
| Application adapters | New integration module; port from MCP | Preserve platform-specific flows but return canonical application events.                                              |
| MCP server exposure  | Optional integration boundary         | Keep server.py as an adapter if agent clients need MCP tools.                                                          |
| Scheduler            | New                                   | Cron/worker; frequency configurable.                                                                                   |
| Observability        | New                                   | Structured logging, error codes, run IDs.                                                                              |

## 5.2 Recommended repository layout after integration

> integrated-job-agent/  
> ├── backend/  
> │ ├── src/  
> │ │ ├── routes/  
> │ │ ├── services/  
> │ │ │ ├── jobs/  
> │ │ │ ├── ai/  
> │ │ │ ├── resume/  
> │ │ │ ├── matching/  
> │ │ │ ├── applications/  
> │ │ │ ├── orchestration/  
> │ │ │ └── scheduler/  
> │ │ ├── adapters/  
> │ │ │ ├── linkedin/  
> │ │ │ ├── naukri/  
> │ │ │ ├── indeed/  
> │ │ │ ├── wellfound/  
> │ │ │ ├── hirist/  
> │ │ │ ├── glassdoor/  
> │ │ │ ├── instahyre/  
> │ │ │ └── cutshort/  
> │ │ ├── db/  
> │ │ └── lib/  
> │ └── prisma/  
> ├── frontend/  
> ├── mcp/  
> │ ├── server.py  
> │ └── tools/  
> ├── resumes/  
> │ ├── master/  
> │ ├── generated/  
> │ └── templates/  
> ├── data/  
> ├── scripts/  
> ├── docs/  
> └── docker-compose.yml

# 6. Integration Plan for the Coding AI

The coding AI should execute these phases in order. Do not perform a large rewrite before the inventory and tests are established.

## Phase 0 - Freeze and inventory

1.  Verify both clones build independently before integration.

2.  Record Node/Python versions, package managers, lockfiles, DB schemas, env vars, platform adapter files, routes, and LLM code.

3.  Create a capability matrix mapping duplicate features.

4.  Tag original commits or create git branches so source behavior can be recovered.

## Phase 1 - Choose canonical runtime

5.  Use JobPilot backend/frontend as the main application shell.

6.  Keep MCP in a dedicated Python process/module until platform code is successfully ported.

7.  Define the cross-language contract using JSON/HTTP, subprocess RPC, or a thin adapter. Prefer a clear contract over shared mutable state.

## Phase 2 - Canonical data model

8.  Design Prisma models for CandidateProfile, CandidateEvidence, Job, JobOccurrence, JobRequirement, MatchAnalysis, ResumeVersion, ResumeEvidence, Application, ApplicationEvent, ProviderConfig, and AutomationRun.

9.  Migrate/port MCP tracker data into Application/ApplicationEvent.

10. Add unique constraints for duplicate protection.

## Phase 3 - Job discovery integration

11. Port platform search/JD retrieval from MCP into adapters.

12. Normalize results into Job + JobOccurrence.

13. Keep source-specific logic isolated.

14. Add retries and source capability flags.

## Phase 4 - AI/matching integration

15. Create canonical MatchAnalysis schema.

16. Reuse JobPilot provider interfaces and prompt infrastructure.

17. Add structured LLM outputs with schema validation.

18. Log provider/model/prompt-version metadata without storing unnecessary secrets.

## Phase 5 - Resume pipeline

19. Create master resume parser.

20. Create job-specific tailoring service.

21. Create evidence map and claim validator.

22. Connect ATS scoring.

23. Render DOCX/PDF and store immutable ResumeVersion records.

## Phase 6 - Application integration

24. Port application adapters from MCP.

25. Before apply, require READY_FOR_REVIEW/APPROVED according to policy.

26. Use the selected ResumeVersion artifact, not a mutable master resume path.

27. Record every transition.

## Phase 7 - Dashboard

28. Add pages/widgets for Job Inbox, Match Analysis, Resume Review, Approval Queue, Applications, Application Detail, Settings, and Run History.

29. Show why a job was matched and why a resume claim exists.

## Phase 8 - Scheduler and automation

30. Run discovery at configurable intervals.

31. Use idempotent workflows so restarts do not duplicate jobs/applications.

32. Add per-platform rate limits and backoff.

## Phase 9 - Hardening

33. Unit tests, adapter contract tests, end-to-end smoke tests, database migration tests, resume generation fixtures, and failure injection.

34. Security review, secret handling review, and platform compliance review.

# 7. Canonical Data Model

The merged system must have one logical source of truth even if different services use different languages.

## CandidateProfile

> id, name, email, phone, location, target_roles\[\], preferred_locations\[\],  
> work_modes\[\], employment_types\[\], salary_target, notice_period,  
> work_authorization, excluded_keywords\[\], version, created_at, updated_at

## CandidateEvidence

> id, profile_id, type, title, content, source, source_ref, valid_from, valid_to,  
> verified, tags\[\], metadata_json

## Job

> id, canonical_key, title, company, normalized_company, location, source_count,  
> jd_raw, jd_normalized, posted_at, discovered_at, first_seen_at, last_seen_at,  
> job_type, experience_min, experience_max, salary_text, status

## JobOccurrence

> id, job_id, platform, source_job_id, url, external_apply_url, source_status,  
> retrieved_at, application_capability, raw_json

## MatchAnalysis

> id, job_id, profile_version, score, eligible, role_score, skill_score,  
> experience_score, location_score, education_score, domain_score,  
> must_have_missing\[\], nice_to_have_missing\[\], rationale, model, prompt_version

## ResumeVersion

> id, job_id, profile_version, template_id, provider, model, resume_json,  
> docx_path, pdf_path, ats_score, keyword_coverage, validation_status,  
> created_at

## ResumeEvidence

> id, resume_version_id, candidate_evidence_id, claim_text, section,  
> source_confidence, validation_status

## Application

> id, job_id, occurrence_id, resume_version_id, platform, company, title,  
> url, status, approved_at, submitted_at, confirmation_id, failure_code,  
> failure_message, created_at, updated_at

## ApplicationEvent

> id, application_id, event_type, timestamp, actor, details_json

# 8. LLM Prompt & Agent Design

Prompts must be versioned and treated as product code. Never embed raw application credentials or secrets in prompts.

## 8.1 JD analysis prompt contract

> SYSTEM:  
> You are a job-description analyst. Extract only facts stated or strongly implied by the JD.  
> Return JSON matching the schema. Do not infer unstated requirements.  
>   
> USER:  
> Candidate target roles:  
> {target_roles}  
>   
> Job description:  
> {jd}  
>   
> Return:  
> - normalized_title  
> - seniority  
> - must_have_skills\[\]  
> - nice_to_have_skills\[\]  
> - experience_requirement  
> - education_requirement  
> - location_requirement  
> - work_mode  
> - application_constraints\[\]  
> - keywords\[\]

## 8.2 Resume tailoring prompt contract

> SYSTEM:  
> You are a truthful resume editor. You may rewrite and reorder only information supported  
> by the candidate evidence set. Never invent employers, projects, dates, certifications,  
> skills, metrics, responsibilities, or achievements. If the JD asks for something unsupported,  
> leave it out and report it as a gap.  
>   
> INPUTS:  
> 1. Candidate evidence set  
> 2. Current master resume  
> 3. Canonical JD  
> 4. Match analysis  
> 5. Target resume template  
>   
> OUTPUT:  
> - resume_sections\[\]  
> - changed_claims\[\]  
> - omitted_requirements\[\]  
> - evidence_map\[\]  
> - unsupported_claims\[\] \# must be empty to pass

## 8.3 Application question policy

- Questions about known factual candidate profile data may be filled from the profile.

- Questions requiring judgment, legal declarations, demographic data, eligibility, compensation expectations, or ambiguous free-text should be review-gated.

- The system must never infer a certification, years of experience, authorization, or other fact solely because it appears in the JD.

- Store the answer source (profile, derived, user-entered, or manual) in the audit log.

# 9. Dashboard / UX Requirements

| **Screen**         | **Required capabilities**                                                                            |
|--------------------|------------------------------------------------------------------------------------------------------|
| Job Inbox          | Filters by source, score, location, role, recency, application state; dedupe indicators.             |
| Job Detail         | Full JD, structured requirements, source links, match rationale, missing skills, application route.  |
| Resume Review      | Tailored resume preview/download; highlighted changes; evidence links; ATS score; validation status. |
| Approval Queue     | Approve, reject, regenerate, edit; exact resume version shown before approval.                       |
| Applications       | Kanban/list, filters, status transitions, dates, resume version, source, notes.                      |
| Application Detail | Full timeline, submitted artifact, confirmation ID, errors, retries.                                 |
| Analytics          | Applications by platform/role/company; response rate; resume version outcomes; top matched skills.   |
| Settings           | Profile, target roles, AI provider/model, thresholds, platform sessions, schedule, approval policy.  |
| Run History        | Scheduled runs, counts, errors, duration, jobs discovered, jobs deduped, applications attempted.     |

# 10. Security, Privacy, and Reliability

## 10.1 Credential strategy: Method A - local .env configuration

For the MVP, credential and secret management shall use Method A only: environment variables loaded from a local .env file. No credential-management UI, secret-vault UI, or account-settings screen is required for credential entry in MVP. The user manually creates and maintains the local .env file before starting the application.

## 10.2 Secrets that must be configurable through .env

- Job portal credentials, where the corresponding connector requires authentication: LinkedIn username/email and password; Naukri username/email and password; Indeed username/email and password; Foundit username/email and password; Instahyre username/email and password; plus any additional connector-specific credentials required by enabled adapters.

- LLM provider API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, and GEMINI_API_KEY.

- LLM selection/configuration: LLM_PROVIDER, LLM_MODEL, temperature, max output tokens, retry settings, and provider-specific configuration as applicable.

- Application/runtime secrets and paths such as encryption secret, database URL, session directory, browser configuration, and other environment-specific values.

## 10.3 Canonical .env example

\# Runtime  
NODE_ENV=development  
PORT=3001  
DATABASE_URL=file:./dev.db  
DATA_DIR=./data  
  
\# Security / encryption  
ENCRYPTION_SECRET=\<strong-random-secret\>  
  
\# LLM provider  
LLM_PROVIDER=anthropic  
LLM_MODEL=\<provider-specific-model\>  
OPENAI_API_KEY=  
ANTHROPIC_API_KEY=  
GEMINI_API_KEY=  
  
\# Job portal credentials  
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
  
\# Browser / session configuration  
PLAYWRIGHT_HEADLESS=false  
SESSION_DIR=./data/sessions

## 10.4 .env handling rules

- The real .env file must never be committed to Git, uploaded to the repository, or included in generated artifacts. Add .env and local environment variants to .gitignore.

- The project must ship a .env.example file containing only variable names, safe placeholders, comments, and no real credentials.

- The application must validate required environment variables at startup and report missing variable names without printing secret values.

- Secrets must not be printed in logs, API responses, telemetry, screenshots, prompts, exception messages, or other user-visible output.

- Each connector should consume only the configuration variables required for that connector. The LLM provider client should receive its API key directly from configuration and the secret value must never be included in prompt content.

- Browser session and cookie state must be treated as secret-equivalent, stored under the configured local session directory, excluded from Git, and never logged or surfaced in the UI.

- If required credentials are missing, the affected connector must fail closed and report AUTH_REQUIRED or NOT_CONFIGURED instead of attempting unintended anonymous/fallback actions.

## 10.5 Credential lifecycle under Method A

35. User manually creates or edits the local .env file.

36. Application loads environment variables at startup. A restart is the supported method for picking up credential changes unless an explicit safe reload mechanism is implemented.

37. Connector health checks may validate authentication when explicitly requested by the user or during a controlled application flow.

38. Changing a portal password or LLM API key requires editing .env and restarting/reloading the service.

39. Removing a required credential disables the corresponding connector until the credential is restored.

## 10.6 Security boundary

Portal credentials are infrastructure secrets used only by the relevant portal connector. The LLM layer must never receive portal usernames, passwords, cookies, session tokens, API keys, encryption keys, or other secret material as prompt input. Resume/JD agents receive only candidate and job information required for their task.

# 11. Testing & Acceptance Criteria

## 11.1 Build acceptance

- Both original repositories can be checked out and built from clean environments before integration.

- Integrated project starts with one documented command path.

- Database migrations run from an empty database.

- No required credentials are committed.

## 11.2 Functional acceptance

- A sample search can discover jobs from at least two adapters and persist them.

- The system can fetch/store a full JD or clearly mark a partial JD.

- Duplicate jobs from two sources collapse into one canonical job with multiple occurrences.

- Match score and rationale are stored.

- A tailored resume can be generated with at least one of GPT/Claude/Gemini.

- Unsupported claims cause validation failure.

- ATS score and keyword coverage are shown.

- An approved job can be sent to the correct application adapter.

- The exact resume version submitted is recorded.

- Application status remains visible after restart.

- A failed application can be retried without duplicating a successful prior submission.

## 11.3 Resume safety acceptance

- Given a JD that requests AWS but the candidate evidence contains no AWS, the generated resume must not claim AWS experience.

- Given a JD asking for 5 years when the profile supports 2 years, the system must report the gap and must not change dates.

- Given a JD requiring a certification the candidate does not have, the system must not add it.

- Every material changed claim must map to candidate evidence.

## 11.4 Failure-state acceptance

| **Scenario**              | **Expected behavior**                                                                 |
|---------------------------|---------------------------------------------------------------------------------------|
| LLM timeout               | Retry with bounded attempts; retain job; mark resume generation failed if unresolved. |
| JD unavailable            | Store partial JD; disable auto-apply unless user reviews.                             |
| CAPTCHA / login challenge | Pause adapter; status AUTH_REQUIRED/CAPTCHA_REQUIRED; no bypass.                      |
| Platform markup changes   | Adapter failure is isolated; other platforms continue.                                |
| Duplicate application     | Reject before submission; show existing application.                                  |
| Resume render failure     | Do not submit; keep validation failure visible.                                       |
| App submission timeout    | Do not blindly retry; check application status/idempotency first.                     |

# 12. Exact Handoff Instructions to the AI Coding Agent

The following block is intentionally written so it can be given directly to an AI coding agent working in the folder containing both cloned repositories.

> ROLE  
> You are the lead integration engineer. You have two cloned repositories in the same  
> workspace:  
> - job-apply-mcp  
> - jobpilot  
>   
> GOAL  
> Integrate them into one maintainable personal AI job application system that:  
> 1. discovers jobs,  
> 2. retrieves and normalizes JDs,  
> 3. scores candidate-job fit,  
> 4. generates a job-specific resume with GPT, Claude, or Gemini,  
> 5. validates the resume for ATS quality and factual truth,  
> 6. prepares/submits applications through permitted platform flows,  
> 7. records every application and state transition,  
> 8. exposes the entire workflow in a dashboard.  
>   
> IMPORTANT  
> - Do not delete working capabilities before mapping them.  
> - Do not copy entire repositories into one another.  
> - First inventory both repos and produce a file/module mapping.  
> - JobPilot is the primary web app shell and canonical backend/data model.  
> - job-apply-mcp is the primary reference/source for additional job-board and  
> application adapters.  
> - Port reusable logic behind clean adapter/service interfaces.  
> - Keep Python-specific browser automation isolated from the TypeScript API unless  
> a stable API/IPC boundary is demonstrably simpler.  
> - Keep MCP support available as an optional interface for agent clients.  
> - Do not implement anti-detection, CAPTCHA bypass, stealth, or policy-evasion logic.  
> - Default to human approval before irreversible application submission.  
> - Never fabricate candidate facts to improve matching or ATS score.  
> - Do not silently change the selected LLM provider/model.  
>   
> EXECUTION ORDER  
> 1. Inspect both repositories and confirm current build/run commands.  
> 2. Produce a capability matrix and dependency conflict report.  
> 3. Create integration branch and preserve original repo history.  
> 4. Define canonical data model and migration plan.  
> 5. Establish JobPilot as the primary application shell.  
> 6. Introduce adapter interfaces for search/JD/apply.  
> 7. Port/reuse MCP platform connectors incrementally.  
> 8. Unify job normalization, dedupe, and match analysis.  
> 9. Unify LLM provider interface.  
> 10. Implement resume tailoring with structured output and evidence mapping.  
> 11. Implement truth validation and ATS validation.  
> 12. Implement approval queue and application state machine.  
> 13. Port application automation adapters.  
> 14. Consolidate application tracking into one database.  
> 15. Add scheduler/run history.  
> 16. Add tests and end-to-end smoke workflows.  
> 17. Update README and .env.example with exact startup instructions.  
>   
> DO NOT MARK THE TASK COMPLETE UNTIL  
> - clean install works,  
> - empty database migration works,  
> - sample candidate profile can be loaded,  
> - one sample JD can generate a tailored resume,  
> - unsupported claims are rejected,  
> - an application record can move through the full state machine,  
> - platform adapter failures do not crash the whole app,  
> - restart preserves job/application state,  
> - the dashboard shows the same canonical data used by the API,  
> - documentation explains how to run in SEARCH_ONLY and REVIEW_ONLY modes.

# 13. Configuration Requirements

\# Copy this file to .env and fill in real values.  
\# NEVER commit .env. Keep only .env.example in source control.  
  
\# Core  
NODE_ENV=development  
PORT=3001  
DATABASE_URL=file:./dev.db  
DATA_DIR=./data  
  
\# Security  
ENCRYPTION_SECRET=\<strong-random-secret\>  
  
\# LLM  
LLM_PROVIDER=anthropic  
LLM_MODEL=\<provider-specific-model\>  
ANTHROPIC_API_KEY=  
OPENAI_API_KEY=  
GEMINI_API_KEY=  
  
\# Job portal credentials  
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
  
\# Browser/session configuration  
PLAYWRIGHT_HEADLESS=false  
SESSION_DIR=./data/sessions  
  
\# Additional connector-specific variables may be appended using \<PLATFORM\>\_\<SETTING\>.

MVP credential policy: Method A (.env) is authoritative. Do not build a credential settings UI, secret-vault integration, or alternative credential-management workflow unless a future PRD revision explicitly changes this requirement.

# 14. Delivery Milestones

| **Milestone**         | **Deliverable**                        | **Definition of done**                                                    |
|-----------------------|----------------------------------------|---------------------------------------------------------------------------|
| M1 - Integrated shell | JobPilot UI/API + MCP adapters visible | Both projects build; dashboard loads; adapter health endpoints work.      |
| M2 - Discovery        | Multi-platform canonical job store     | Jobs searchable, normalized, deduped, persisted.                          |
| M3 - AI matching      | MatchAnalysis                          | Score/rationale/gaps shown in UI.                                         |
| M4 - Resume engine    | Per-job resume variants                | GPT/Claude/Gemini works; DOCX/PDF generated.                              |
| M5 - Validation       | Truth + ATS gates                      | Unsupported claims block approval; ATS report shown.                      |
| M6 - Application      | Adapter-based apply flow               | Approved application creates/submits with correct resume and logs events. |
| M7 - Tracking         | Centralized ledger                     | Applications searchable, deduped, exportable.                             |
| M8 - Automation       | Scheduler + run history                | Repeated discovery is idempotent and observable.                          |
| M9 - Hardening        | Tests + docs                           | Clean install, migration, smoke tests, recovery procedures documented.    |

# 15. Risks and Mitigations

| **Risk**                                 | **Impact** | **Mitigation**                                              |
|------------------------------------------|------------|-------------------------------------------------------------|
| Platform UI changes                      | High       | Isolate adapters; add selector health tests; fail closed.   |
| Platform terms / automation restrictions | High       | Capability flags; manual approval; no evasion.              |
| LLM hallucination                        | High       | Evidence map + deterministic validator + human review.      |
| Duplicate application                    | High       | Canonical job IDs + unique constraints + idempotency.       |
| Cross-platform data inconsistency        | Medium     | Canonical schemas and normalization layer.                  |
| LLM cost explosion                       | Medium     | Eligibility gate, caching, batch analysis, model selection. |
| Credential/session loss                  | High       | Persistent encrypted storage; explicit re-auth state.       |
| Resume formatting errors                 | Medium     | Automated render/parse checks and test fixtures.            |
| Database migration conflicts             | Medium     | One canonical schema; explicit migration scripts.           |

# 16. Definition of Done

The integration is complete when a user can start with one master profile and one master resume, run a job discovery cycle, inspect a canonical JD and match explanation, generate a tailored resume with a selected LLM, see ATS and truth-validation results, approve an application, submit through the supported adapter, and later find the exact application plus the exact resume artifact that was submitted - all from one dashboard and one database.

The system must remain understandable to another engineer. Platform-specific logic must not leak into the core matching/resume/application domain model.

# 17. Source References

Repository references used for this PRD:

- https://github.com/pulkit017/job-apply-mcp

- https://github.com/Harshitsk7/jobpilot

# Appendix A - Initial Capability Matrix

| **Capability**           | **MCP**              | **JobPilot**                   | **Target**                        |
|--------------------------|----------------------|--------------------------------|-----------------------------------|
| Multi-platform discovery | Strong (8 portals)   | LinkedIn + Naukri              | Unified adapter layer             |
| JD fetch                 | Strong               | Supported in scraping workflow | Canonical JD service              |
| Filtering/ranking        | Strong               | Strong                         | Single MatchAnalysis              |
| LLM provider abstraction | Limited/agent-driven | Strong                         | Shared provider service           |
| Resume tailoring         | Limited              | Strong                         | Evidence-bound per-job generation |
| ATS scanning             | Limited              | Strong                         | ATS + truth gate                  |
| Application automation   | Strong               | LinkedIn-focused               | Adapter-based, policy-aware       |
| Application tracking     | Strong               | Strong                         | Single canonical ledger           |
| Dashboard                | CLI/MCP oriented     | Strong                         | JobPilot UI                       |
| MCP interface            | Native               | Not primary                    | Optional retained interface       |
| Scheduler                | Basic run model      | Not core                       | New idempotent scheduler          |

# Appendix B - Recommended First Smoke Test

> 1\. Create candidate profile:  
> Role = Generative AI Engineer  
> Skills = Python, LLM, RAG, LangChain, FastAPI, Docker  
>   
> 2. Load a test JD that requests:  
> Python, LLM, RAG, AWS, FastAPI  
>   
> 3. Expect:  
> - match score calculated,  
> - AWS flagged as missing,  
> - tailored resume generated,  
> - AWS NOT claimed in the resume,  
> - ATS report generated,  
> - application remains READY_FOR_REVIEW.  
>   
> 4. Approve the application in UI.  
>   
> 5. Adapter prepares/submits according to source capability.  
>   
> 6. Application page shows:  
> - company  
> - title  
> - source  
> - URL  
> - match score  
> - submitted timestamp  
> - exact resume version  
> - status timeline.
