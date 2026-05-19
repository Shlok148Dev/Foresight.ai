import { describe, it, expect } from "vitest";
import { cn } from "./utils";

describe("cn() — class merge utility", () => {
  it("merges simple classes", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("handles conditional classes", () => {
    expect(cn("base", false && "hidden", "extra")).toBe("base extra");
  });

  it("deduplicates conflicting Tailwind classes", () => {
    expect(cn("text-red-500", "text-blue-500")).toBe("text-blue-500");
  });

  it("handles undefined and null", () => {
    expect(cn("base", undefined, null, "end")).toBe("base end");
  });

  it("returns empty string for no args", () => {
    expect(cn()).toBe("");
  });
});
