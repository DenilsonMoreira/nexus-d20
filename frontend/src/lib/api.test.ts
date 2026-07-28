import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, apiFetch } from "./api";

describe("cliente da API", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("envia cookies de sessão e desserializa a resposta", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ id: "user-1" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(apiFetch<{ id: string }>("/auth/me")).resolves.toEqual({
      id: "user-1",
    });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/auth/me"),
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("preserva código, mensagem e status dos erros da API", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: { code: "invalid_credentials", message: "Acesso negado." },
          }),
          {
            status: 401,
            headers: { "Content-Type": "application/json" },
          },
        ),
      ),
    );

    const error = await apiFetch("/auth/login").catch((caught) => caught);

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({
      status: 401,
      code: "invalid_credentials",
      message: "Acesso negado.",
    });
  });

  it("aceita respostas sem conteúdo no logout", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(null, { status: 204 })),
    );

    await expect(
      apiFetch<void>("/auth/logout", { method: "POST" }),
    ).resolves.toBeUndefined();
  });
});
