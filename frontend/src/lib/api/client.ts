import type { ValidationErrorItem } from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly validationErrors: ValidationErrorItem[] = [],
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function readableMessage(status: number): string {
  if (status === 401) return "Your session has expired. Please sign in again.";
  if (status === 403) return "You do not have permission to do that.";
  if (status === 404) return "The requested record was not found.";
  if (status === 409) return "That change conflicts with an existing record.";
  if (status === 422) return "Please review the highlighted information.";
  return status >= 500
    ? "The server could not complete the request."
    : "The request could not be completed.";
}

type ApiRequestInit = Omit<RequestInit, "body"> & { body?: unknown };

export async function apiFetch<T>(
  path: string,
  options: ApiRequestInit = {},
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      body: options.body === undefined ? undefined : typeof options.body === "string" ? options.body : JSON.stringify(options.body),
      credentials: "include",
      headers: {
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new ApiError("Unable to reach StationStock. Check that the backend is running.", 0);
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const validationErrors = Array.isArray(body?.detail) ? body.detail : [];
    const message =
      typeof body?.detail === "string" ? body.detail : readableMessage(response.status);
    if (response.status === 401 && typeof window !== "undefined") {
      window.dispatchEvent(new Event("stationstock:unauthorized"));
    }
    throw new ApiError(message, response.status, validationErrors);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export function queryString(values: Record<string, string | number | boolean | null | undefined>) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(values)) {
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, String(value));
    }
  }
  const query = params.toString();
  return query ? `?${query}` : "";
}
