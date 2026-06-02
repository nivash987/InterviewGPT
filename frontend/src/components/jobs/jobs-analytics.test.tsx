import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { JobsAnalytics } from "@/components/jobs/jobs-analytics";

describe("JobsAnalytics", () => {
  it("renders dashboard metrics", () => {
    render(
      <JobsAnalytics
        analytics={{
          total_applications: 10,
          interviews_scheduled: 3,
          offers_received: 2,
          rejections: 4,
          success_rate: 33.3,
          by_status: { applied: 5, offer: 2, rejected: 3 },
        }}
      />,
    );
    expect(screen.getByText("Total Applications")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("33.3%")).toBeInTheDocument();
  });
});
