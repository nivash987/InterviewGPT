import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StatusBadge } from "@/components/jobs/status-badge";

describe("StatusBadge", () => {
  it("renders applied status label", () => {
    render(<StatusBadge status="applied" />);
    expect(screen.getByText("Applied")).toBeInTheDocument();
  });

  it("renders offer status label", () => {
    render(<StatusBadge status="offer" />);
    expect(screen.getByText("Offer")).toBeInTheDocument();
  });
});
