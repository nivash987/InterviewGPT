import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SkillGapChart } from "@/components/career-coach/skill-gap-chart";

describe("SkillGapChart", () => {
  it("renders empty state", () => {
    render(<SkillGapChart analysis={null} />);
    expect(screen.getByText("No skill gap data yet.")).toBeInTheDocument();
  });

  it("renders missing skills", () => {
    render(
      <SkillGapChart
        analysis={{
          target_role: "Software Engineer",
          required_skills: ["python", "docker"],
          user_skills: ["python"],
          missing_skills: [
            { skill_name: "docker", priority: "high", reason: "Required" },
          ],
          coverage_percent: 50,
        }}
      />,
    );
    expect(screen.getByText("50% match for Software Engineer")).toBeInTheDocument();
    expect(screen.getByText("docker")).toBeInTheDocument();
  });
});
