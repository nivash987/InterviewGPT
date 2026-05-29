import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SkillsPanel } from "@/components/ats/skills-panel";

describe("SkillsPanel", () => {
  it("renders found and missing skills", () => {
    render(
      <SkillsPanel
        skillsFound={["Python", "React"]}
        missingSkills={["Docker"]}
      />,
    );

    expect(screen.getByText("Skills Found")).toBeInTheDocument();
    expect(screen.getByText("Missing Skills")).toBeInTheDocument();
    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("Docker")).toBeInTheDocument();
  });

  it("shows empty states", () => {
    render(<SkillsPanel skillsFound={[]} missingSkills={[]} />);
    expect(screen.getByText("No skills detected yet.")).toBeInTheDocument();
    expect(screen.getByText("No critical skill gaps identified.")).toBeInTheDocument();
  });
});
