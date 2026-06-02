import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ProgressTracker } from "@/components/interview/progress-tracker";

describe("ProgressTracker", () => {
  it("renders progress fraction and percent", () => {
    render(<ProgressTracker current={3} total={10} />);
    expect(screen.getByText("3 / 10 (30%)")).toBeInTheDocument();
    expect(screen.getByText("Interview progress")).toBeInTheDocument();
  });

  it("supports custom label", () => {
    render(<ProgressTracker current={1} total={5} label="Questions done" />);
    expect(screen.getByText("Questions done")).toBeInTheDocument();
  });
});
