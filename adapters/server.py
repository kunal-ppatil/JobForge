# adapters/server.py

"""FastAPI micro‑service exposing Job‑Apply‑MCP functionality.

Endpoints:
- POST /search  -> body: SearchRequest, returns list of JobResult
- POST /apply   -> body: ApplyRequest, returns success status

The service re‑uses the existing MCP modules from `job-apply-mcp/tools/`.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

# Ensure the MCP package is on the import path
import sys
from pathlib import Path

MCP_ROOT = Path(__file__).parent.parent / "job-apply-mcp"
sys.path.append(str(MCP_ROOT))

# Import MCP functions
from tools.search import _scrape_linkedin, _scrape_naukri, _scrape_wellfound, _scrape_indeed, _scrape_hirist, _scrape_glassdoor, _scrape_instahyre, _scrape_cutshort
from tools.apply import apply_job  # Assume a function apply_job(platform, url, resume_path)

app = FastAPI()
logger = logging.getLogger("uvicorn.error")

class SearchRequest(BaseModel):
    keywords: str
    location: str
    experience: int = Field(..., ge=0)
    days: Optional[int] = 30
    platforms: Optional[List[str]] = None  # e.g., ["linkedin", "naukri"]
    fetch_jd: Optional[bool] = False

class JobResult(BaseModel):
    title: str
    company: str
    location: str
    salary: str
    apply_url: str
    match_score: float
    platform: str
    description: Optional[str] = None
    posted_days_ago: Optional[int] = None

class ApplyRequest(BaseModel):
    platform: str
    job_url: str
    resume_path: Optional[str] = None

class ApplyResponse(BaseModel):
    success: bool
    message: str
    application_id: Optional[str] = None

# Helper to map platform name to scraper function
SCRAPERS = {
    "linkedin": _scrape_linkedin,
    "naukri": _scrape_naukri,
    "wellfound": _scrape_wellfound,
    "indeed": _scrape_indeed,
    "hirist": _scrape_hirist,
    "glassdoor": _scrape_glassdoor,
    "instahyre": _scrape_instahyre,
    "cutshort": _scrape_cutshort,
}

@app.post("/search", response_model=List[JobResult])
async def search(request: SearchRequest):
    # Build URLs for each platform using the same logic as MCP's URL builders
    from tools.search import PLATFORM_BUILDERS
    results: List[JobResult] = []
    selected = request.platforms or list(PLATFORM_BUILDERS.keys())
    for platform in selected:
        builder = PLATFORM_BUILDERS.get(platform)
        if not builder:
            logger.warning(f"Unsupported platform requested: {platform}")
            continue
        url = builder(request.keywords, request.location, request.experience, request.days or 30)
        scraper = SCRAPERS.get(platform)
        if not scraper:
            logger.warning(f"No scraper for platform: {platform}")
            continue
        try:
            platform_results = await scraper(url) if hasattr(scraper, "__code__") else []
            # The scraper functions return List[JobResult] dataclasses; convert to dicts
            for r in platform_results:
                results.append(JobResult(**r.to_dict()))
        except Exception as exc:
            logger.error(f"Error scraping {platform}: {exc}")
            continue
    # Optionally fetch full JD for top results (already handled by MCP scrapers if fetch_jd=True)
    return results

@app.post("/apply", response_model=ApplyResponse)
async def apply(request: ApplyRequest):
    try:
        # Assume apply_job is an async function; adapt if sync
        result = await apply_job(request.platform, request.job_url, request.resume_path)
        return ApplyResponse(success=True, message="Applied successfully", application_id=result.get("application_id"))
    except Exception as exc:
        logger.error(f"Apply failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))
