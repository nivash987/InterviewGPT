import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ApplicationTimeline } from "@/components/jobs/application-timeline";

describe("ApplicationTimeline", () => {
  it("renders empty state", () => {
    render(<ApplicationTimeline events={[]} />);
    expect(screen.getByText("No timeline events yet.")).toBeInTheDocument();
  });

  it("renders status events", () => {
    render(
      <ApplicationTimeline
        events={[
          {
            id: "1",
            from_status: null,
            to_status: "applied",
            note: "Application created",
            created_at: "2026-06-01T12:00:00Z",
          },
        ]}
      />,
    );
    expect(screen.getByText("Application created")).toBeInTheDocument();
    expect(screen.getByText("Applied")).toBeInTheDocument();
  });
});
