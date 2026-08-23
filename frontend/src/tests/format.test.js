import { describe, expect, it } from "vitest";
import { unwrapList, formatDuration } from "../utils/format";

describe("format utilities", () => {
  it("normalizes paginated and array responses", () => {
    expect(unwrapList([1, 2]).total).toBe(2);
    expect(unwrapList({ items: [1], total: 9 }).total).toBe(9);
  });
  it("formats durations", () => {
    expect(formatDuration(420)).toBe("420 ms");
    expect(formatDuration(1500)).toBe("1.50 s");
  });
});
