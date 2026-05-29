import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AtsScoreCard, CompletenessScoreCard } from "@/components/ats/score-cards";

describe("ScoreCards", () => {
  it("renders ATS score", () => {
    render(<AtsScoreCard score={85} />);
    expect(screen.getByText("ATS Score")).toBeInTheDocument();
    expect(screen.getByText("85")).toBeInTheDocument();
  });

  it("renders completeness score", () => {
    render(<CompletenessScoreCard score={90} />);
    expect(screen.getByText("Completeness Score")).toBeInTheDocument();
    expect(screen.getByText("90")).toBeInTheDocument();
  });
});
