import { describe, expect, it } from "vitest";

import { navGroups } from "@/components/sidebar";

describe("sidebar navGroups", () => {
  it("exposes four groups for Hick's Law progressive disclosure", () => {
    expect(navGroups.map((g) => g.title)).toEqual([
      "Операции",
      "Автопарк",
      "Аналитика",
      "Система",
    ]);
  });

  it("keeps operations before system settings", () => {
    const hrefs = navGroups.flatMap((g) => g.items.map((i) => i.href));
    expect(hrefs.indexOf("/dispatch")).toBeLessThan(hrefs.indexOf("/settings"));
    expect(hrefs).toContain("/dashboard");
    expect(hrefs).toContain("/routes");
    expect(hrefs).toContain("/fuel");
  });

  it("has unique hrefs", () => {
    const hrefs = navGroups.flatMap((g) => g.items.map((i) => i.href));
    expect(new Set(hrefs).size).toBe(hrefs.length);
  });
});
