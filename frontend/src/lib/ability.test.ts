import { describe, expect, it } from "vitest";

function modifier(score: number): number { return Math.floor((score - 10) / 2); }

describe("modificador de atributo", () => {
  it("calcula valores positivos e negativos", () => {
    expect(modifier(16)).toBe(3);
    expect(modifier(8)).toBe(-1);
    expect(modifier(10)).toBe(0);
  });
});
