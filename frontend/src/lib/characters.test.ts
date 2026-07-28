import { afterEach, describe, expect, it, vi } from "vitest";
import {
  acceptCampaignInvite,
  createCampaign,
  loadAccountWorkspace,
} from "./characters";

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("jornada de campanha", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("carrega todas as fichas visíveis para troca pelo mestre", async () => {
    const campaign = {
      id: "campaign-1",
      name: "Esteren",
      ruleset_code: "dnd5e-2014",
      role: "master" as const,
    };
    const characters = [
      { id: "character-1", name: "Nox" },
      { id: "character-2", name: "Lyra" },
    ];
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ items: [campaign], next_cursor: null }))
      .mockResolvedValueOnce(
        jsonResponse({ items: characters, next_cursor: null }),
      );
    vi.stubGlobal("fetch", fetchMock);

    const workspace = await loadAccountWorkspace();

    expect(workspace.active?.campaign.role).toBe("master");
    expect(workspace.active?.character.name).toBe("Nox");
    expect(workspace.characters.map((character) => character.name)).toEqual([
      "Nox",
      "Lyra",
    ]);
  });

  it("mantém conta autenticada em onboarding quando ainda não há ficha", async () => {
    const campaign = {
      id: "campaign-1",
      name: "Esteren",
      ruleset_code: "dnd5e-2014",
      role: "player" as const,
    };
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(jsonResponse({ items: [campaign], next_cursor: null }))
        .mockResolvedValueOnce(jsonResponse({ items: [], next_cursor: null })),
    );

    await expect(loadAccountWorkspace()).resolves.toEqual({
      campaigns: [campaign],
      active: null,
      characters: [],
    });
  });

  it("envia os contratos corretos para criar campanha e aceitar convite", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({
          id: "campaign-1",
          name: "Esteren",
          ruleset_code: "dnd5e-2014",
          role: "master",
        }),
      )
      .mockResolvedValueOnce(
        jsonResponse({
          campaign: {
            id: "campaign-1",
            name: "Esteren",
            ruleset_code: "dnd5e-2014",
            role: "player",
          },
        }),
      );
    vi.stubGlobal("fetch", fetchMock);

    await createCampaign("Esteren");
    const membership = await acceptCampaignInvite("convite com espaços");

    expect(membership.campaign.role).toBe("player");
    expect(fetchMock.mock.calls[0][1]).toMatchObject({
      method: "POST",
      body: JSON.stringify({ name: "Esteren" }),
    });
    expect(fetchMock.mock.calls[1][0]).toContain(
      "/campaign-invites/convite%20com%20espa%C3%A7os/accept",
    );
  });
});
