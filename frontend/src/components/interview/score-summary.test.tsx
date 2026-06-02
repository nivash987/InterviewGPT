import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ScoreSummary } from "@/components/interview/score-summary";
import type { InterviewSummary } from "@/types/interview";

const sampleSummary: InterviewSummary = {
  total_score: 78,
  questions_answered: 5,
  total_questions: 5,
  average_per_category: { Technical: 80 },
  strengths: ["Strong Technical performance"],
  improvements: ["Review Behavioral topics"],
  category_breakdown: [
    { category: "Technical", average_score: 80, question_count: 3 },
    { category: "Behavioral", average_score: 70, question_count: 2 },
  ],
};

describe("ScoreSummary", () => {
  it("renders overall score and breakdown", () => {
    render(<ScoreSummary summary={sampleSummary} />);
    expect(screen.getByText("78%")).toBeInTheDocument();
    expect(screen.getByText("Technical")).toBeInTheDocument();
    expect(screen.getByText("5 of 5 questions answered")).toBeInTheDocument();
  });
});
