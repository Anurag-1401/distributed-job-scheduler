import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusBadge } from "../components/StatusBadge";

describe("StatusBadge", () => {
  it("renders normalized status text", () => {
    render(<StatusBadge status="DEAD_LETTER" />);
    expect(screen.getByText("DEAD LETTER")).toBeInTheDocument();
  });
});
