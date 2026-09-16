# adapters/migrate_db.py

"""
Migration script to port historical tracking data from job-apply-mcp's applications.db
into JobPilot's SQLite (Prisma) database.
"""

import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Paths
HOME_MCP_DB = Path.home() / ".job-apply-mcp" / "applications.db"
LOCAL_MCP_DB = Path(__file__).parent.parent / "job-apply-mcp" / "applications.db"
PRISMA_DB = Path(__file__).parent.parent / "jobpilot" / "backend" / "prisma" / "dev.db"

def get_mcp_db_path() -> Path:
    if HOME_MCP_DB.exists():
        return HOME_MCP_DB
    if LOCAL_MCP_DB.exists():
        return LOCAL_MCP_DB
    return HOME_MCP_DB  # default even if missing

def normalize_dedupe_key(title: str, company: str) -> str:
    return f"{title.lower().strip()}_{company.lower().strip()}"

def map_status(mcp_status: str) -> tuple[str, str]:
    """Returns (job_status, application_status)"""
    m = mcp_status.lower()
    if m == 'applied':
        return ('applied', 'success')
    elif m == 'failed':
        return ('not_applied', 'failed')
    elif m == 'rejected':
        return ('rejected', 'failed')
    else:
        return ('applied', 'success')

def run_migration():
    mcp_path = get_mcp_db_path()
    if not mcp_path.exists():
        print(f"[Migration] No MCP database found at {mcp_path}. Skipping data import.")
        return

    if not PRISMA_DB.exists():
        print(f"[Migration] JobPilot SQLite DB not found at {PRISMA_DB}. Ensure 'npx prisma db push' or server has initialized dev.db.")
        return

    print(f"[Migration] Reading MCP data from {mcp_path}...")
    mcp_conn = sqlite3.connect(mcp_path)
    mcp_conn.row_factory = sqlite3.Row
    mcp_cur = mcp_conn.cursor()

    try:
        mcp_cur.execute("SELECT * FROM applications")
        rows = mcp_cur.fetchall()
    except sqlite3.OperationalError as e:
        print(f"[Migration] Could not query applications table: {e}")
        return

    print(f"[Migration] Found {len(rows)} MCP application records.")
    if not rows:
        return

    prisma_conn = sqlite3.connect(PRISMA_DB)
    prisma_cur = prisma_conn.cursor()

    now_iso = datetime.now(timezone.utc).isoformat()
    migrated_count = 0

    for row in rows:
        title = row['job_title']
        company = row['company']
        platform = row['platform']
        job_url = row['job_url']
        mcp_status = row['status']
        applied_at = row['applied_at'] or now_iso
        match_score = row['match_score']

        dedupe_key = normalize_dedupe_key(title, company)
        job_status, app_status = map_status(mcp_status)

        # Check if job already exists by dedupeKey or url
        prisma_cur.execute("SELECT id FROM Job WHERE dedupeKey = ? OR url = ?", (dedupe_key, job_url))
        existing_job = prisma_cur.fetchone()

        if existing_job:
            job_id = existing_job[0]
            prisma_cur.execute(
                "UPDATE Job SET status = ?, updatedAt = ? WHERE id = ?",
                (job_status, now_iso, job_id)
            )
        else:
            job_id = str(uuid.uuid4())
            score_val = int(match_score * 100) if match_score and match_score <= 1.0 else (int(match_score) if match_score else None)
            prisma_cur.execute(
                """
                INSERT INTO Job (
                    id, platform, title, company, url, status, dedupeKey, matchScore, createdAt, updatedAt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (job_id, platform, title, company, job_url, job_status, dedupe_key, score_val, applied_at, now_iso)
            )

        # Check if Application already exists for this job
        prisma_cur.execute("SELECT id FROM Application WHERE jobId = ?", (job_id,))
        if not prisma_cur.fetchone():
            app_id = str(uuid.uuid4())
            prisma_cur.execute(
                """
                INSERT INTO Application (
                    id, jobId, platform, status, appliedAt
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (app_id, job_id, platform, app_status, applied_at)
            )
            migrated_count += 1

    prisma_conn.commit()
    mcp_conn.close()
    prisma_conn.close()

    print(f"[Migration] Successfully migrated/synced {migrated_count} application records into JobPilot DB.")

if __name__ == "__main__":
    run_migration()
