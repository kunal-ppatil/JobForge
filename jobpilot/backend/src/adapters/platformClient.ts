// jobpilot/backend/src/adapters/platformClient.ts

import fetch from 'node-fetch';

const ADAPTER_BASE_URL = process.env.ADAPTER_BASE_URL || 'http://localhost:8001';

export interface SearchRequest {
  keywords: string;
  location: string;
  experience: number;
  days?: number;
  platforms?: string[];
  fetchJd?: boolean;
}

export interface SearchResult {
  title: string;
  company: string;
  location: string;
  salary: string;
  apply_url: string;
  match_score: number;
  platform: string;
  description?: string;
  posted_days_ago?: number;
}

export interface ApplyRequest {
  platform: string;
  jobUrl: string;
  resumePath?: string;
}

export interface ApplyResponse {
  success: boolean;
  message: string;
  applicationId?: string;
}

export async function searchJobsViaAdapter(request: SearchRequest): Promise<SearchResult[]> {
  const resp = await fetch(`${ADAPTER_BASE_URL}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      keywords: request.keywords,
      location: request.location,
      experience: request.experience,
      days: request.days ?? 30,
      platforms: request.platforms,
      fetch_jd: request.fetchJd ?? false,
    }),
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`Adapter search failed (${resp.status}): ${text}`);
  }

  return (await resp.json()) as SearchResult[];
}

export async function applyJobViaAdapter(request: ApplyRequest): Promise<ApplyResponse> {
  const resp = await fetch(`${ADAPTER_BASE_URL}/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      platform: request.platform,
      job_url: request.jobUrl,
      resume_path: request.resumePath,
    }),
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`Adapter apply failed (${resp.status}): ${text}`);
  }

  return (await resp.json()) as ApplyResponse;
}
