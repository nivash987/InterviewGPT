"""add career coach and placement readiness tables

Revision ID: 0007_career_coach
Revises: 0006_job_application_tracker
Create Date: 2026-06-02

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_career_coach"
down_revision: Union[str, None] = "0006_job_application_tracker"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_goals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_role", sa.String(128), nullable=False),
        sa.Column("target_timeline_months", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_user_goals_user_id", "user_goals", ["user_id"])
    op.create_index("ix_user_goals_user_active", "user_goals", ["user_id", "is_active"])

    op.create_table(
        "user_skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_name", sa.String(128), nullable=False),
        sa.Column("proficiency_level", sa.String(32), nullable=False, server_default="beginner"),
        sa.Column("source", sa.String(32), nullable=False, server_default="manual"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_user_skills_user_id", "user_skills", ["user_id"])
    op.create_index("ix_user_skills_user_skill", "user_skills", ["user_id", "skill_name"], unique=True)

    op.create_table(
        "career_roadmaps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("goal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_goals.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("target_role", sa.String(128), nullable=False),
        sa.Column("milestones", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_career_roadmaps_user_id", "career_roadmaps", ["user_id"])
    op.create_index("ix_career_roadmaps_goal_id", "career_roadmaps", ["goal_id"])

    op.create_table(
        "progress_tracking",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "roadmap_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("career_roadmaps.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("milestone_id", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_progress_tracking_user_id", "progress_tracking", ["user_id"])
    op.create_index("ix_progress_tracking_roadmap_id", "progress_tracking", ["roadmap_id"])
    op.create_index(
        "ix_progress_tracking_roadmap_milestone",
        "progress_tracking",
        ["roadmap_id", "milestone_id"],
        unique=True,
    )

    op.create_table(
        "readiness_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("overall_score", sa.Integer(), nullable=False),
        sa.Column("category_scores", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("weak_areas", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("missing_skills", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("recommendations", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_readiness_scores_user_id", "readiness_scores", ["user_id"])
    op.create_index("ix_readiness_scores_computed_at", "readiness_scores", ["computed_at"])


def downgrade() -> None:
    op.drop_table("readiness_scores")
    op.drop_table("progress_tracking")
    op.drop_table("career_roadmaps")
    op.drop_table("user_skills")
    op.drop_table("user_goals")
