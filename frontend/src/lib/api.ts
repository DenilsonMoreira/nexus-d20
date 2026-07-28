const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as
      | { error?: { code?: string; message?: string } }
      | null;
    throw new ApiError(
      payload?.error?.message ?? `Falha na API: ${response.status}`,
      response.status,
      payload?.error?.code,
    );
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
