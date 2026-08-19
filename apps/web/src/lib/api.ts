import { getApiBase } from "@/lib/config";

export type HealthResponse = {
  status: string;
  service: string;
  version: string;
};

export type ReadinessResponse = HealthResponse & {
  checks: {
    postgres: { status: string; detail: string };
    redis: { status: string; detail: string };
  };
};

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${getApiBase()}/api/v1/health`, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`API health check failed: ${response.status}`);
  }

  return response.json();
}

export async function fetchReadiness(): Promise<ReadinessResponse> {
  const response = await fetch(`${getApiBase()}/api/v1/health/ready`, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`API readiness check failed: ${response.status}`);
  }

  return response.json();
}
