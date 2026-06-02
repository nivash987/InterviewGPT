"""add interview session tables

Revision ID: 0004_interview_sessions
Revises: 0003_ats_analysis
Create Date: 2026-06-02

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_interview_sessions"
down_revision: Union[str, None] = "0003_ats_analysis"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interview_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(128), nullable=False),
        sa.Column("difficulty", sa.String(32), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="in_progress"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_interview_sessions_user_id", "interview_sessions", ["user_id"])
    op.create_index("ix_interview_sessions_resume_id", "interview_sessions", ["resume_id"])

    op.create_table(
        "interview_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("interview_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("difficulty", sa.String(32), nullable=False),
        sa.Column("expected_keywords", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_interview_questions_session_id", "interview_questions", ["session_id"])

    op.create_table(
        "interview_answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("interview_questions.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("feedback", sa.Text(), nullable=False),
    )
    op.create_index("ix_interview_answers_question_id", "interview_answers", ["question_id"])


def downgrade() -> None:
    op.drop_table("interview_answers")
    op.drop_table("interview_questions")
    op.drop_table("interview_sessions")
