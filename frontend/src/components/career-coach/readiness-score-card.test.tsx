import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ReadinessScoreCard } from "@/components/career-coach/readiness-score-card";

describe("ReadinessScoreCard", () => {
  it("renders score and label", () => {
    render(<ReadinessScoreCard score={72} trend="up" />);
    expect(screen.getByText("Placement Readiness")).toBeInTheDocument();
    expect(screen.getByText("72")).toBeInTheDocument();
    expect(screen.getByText("Improving")).toBeInTheDocument();
  });

  it("shows early stage for low scores", () => {
    render(<ReadinessScoreCard score={25} />);
    expect(screen.getByText("Early stage")).toBeInTheDocument();
  });
});
