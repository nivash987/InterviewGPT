"""add ATS analysis tables

Revision ID: 0003_ats_analysis
Revises: 0002_resume_management
Create Date: 2026-05-30

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_ats_analysis"
down_revision: Union[str, None] = "0002_resume_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SKILL_TAXONOMY_SEED = [
    ("Python", "Programming"),
    ("JavaScript", "Programming"),
    ("TypeScript", "Programming"),
    ("Java", "Programming"),
    ("C++", "Programming"),
    ("Go", "Programming"),
    ("Rust", "Programming"),
    ("SQL", "Database"),
    ("PostgreSQL", "Database"),
    ("MySQL", "Database"),
    ("MongoDB", "Database"),
    ("Redis", "Database"),
    ("React", "Frontend"),
    ("Next.js", "Frontend"),
    ("Vue.js", "Frontend"),
    ("Angular", "Frontend"),
    ("HTML", "Frontend"),
    ("CSS", "Frontend"),
    ("Tailwind CSS", "Frontend"),
    ("Node.js", "Backend"),
    ("FastAPI", "Backend"),
    ("Django", "Backend"),
    ("Flask", "Backend"),
    ("Spring Boot", "Backend"),
    ("Express.js", "Backend"),
    ("Docker", "DevOps"),
    ("Kubernetes", "DevOps"),
    ("AWS", "Cloud"),
    ("Azure", "Cloud"),
    ("GCP", "Cloud"),
    ("Git", "Tools"),
    ("CI/CD", "DevOps"),
    ("Linux", "Tools"),
    ("REST API", "Backend"),
    ("GraphQL", "Backend"),
    ("Microservices", "Architecture"),
    ("Machine Learning", "Data Science"),
    ("TensorFlow", "Data Science"),
    ("PyTorch", "Data Science"),
    ("Pandas", "Data Science"),
    ("Communication", "Soft Skills"),
    ("Leadership", "Soft Skills"),
    ("Problem Solving", "Soft Skills"),
    ("Agile", "Methodology"),
    ("Scrum", "Methodology"),
]

JOB_PROFILES_SEED = [
    {
        "role_name": "Backend Developer",
        "required_skills": ["Python", "SQL", "REST API", "Git"],
        "preferred_skills": ["FastAPI", "Docker", "PostgreSQL", "Redis"],
    },
    {
        "role_name": "Frontend Developer",
        "required_skills": ["JavaScript", "HTML", "CSS", "React"],
        "preferred_skills": ["TypeScript", "Next.js", "Tailwind CSS", "Git"],
    },
    {
        "role_name": "Full Stack Developer",
        "required_skills": ["JavaScript", "Python", "React", "SQL", "REST API"],
        "preferred_skills": ["TypeScript", "Next.js", "FastAPI", "PostgreSQL", "Docker"],
    },
    {
        "role_name": "DevOps Engineer",
        "required_skills": ["Linux", "Docker", "Git", "CI/CD"],
        "preferred_skills": ["Kubernetes", "AWS", "Python", "Azure"],
    },
    {
        "role_name": "Data Scientist",
        "required_skills": ["Python", "SQL", "Machine Learning", "Pandas"],
        "preferred_skills": ["TensorFlow", "PyTorch", "PostgreSQL", "Communication"],
    },
    {
        "role_name": "Software Engineer",
        "required_skills": ["Python", "JavaScript", "Git", "Problem Solving"],
        "preferred_skills": ["Java", "SQL", "Agile", "REST API", "Docker"],
    },
]


def upgrade() -> None:
    op.create_table(
        "skill_taxonomy",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("skill_name", sa.String(length=128), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("skill_name"),
    )

    op.create_table(
        "job_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("role_name", sa.String(length=128), nullable=False),
        sa.Column("required_skills", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("preferred_skills", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_name"),
    )

    op.create_table(
        "ats_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ats_score", sa.Integer(), nullable=False),
        sa.Column("completeness_score", sa.Integer(), nullable=False),
        sa.Column("section_scores", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("skills_found", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("missing_skills", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("keyword_coverage", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("strengths", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("weaknesses", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("suggestions", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("recommended_roles", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ats_analyses_user_id", "ats_analyses", ["user_id"])
    op.create_index("ix_ats_analyses_resume_id", "ats_analyses", ["resume_id"])
    op.create_index("ix_ats_analyses_user_id_created_at", "ats_analyses", ["user_id", "created_at"])

    skill_table = sa.table(
        "skill_taxonomy",
        sa.column("skill_name", sa.String),
        sa.column("category", sa.String),
    )
    op.bulk_insert(
        skill_table,
        [{"skill_name": name, "category": category} for name, category in SKILL_TAXONOMY_SEED],
    )

    job_table = sa.table(
        "job_profiles",
        sa.column("role_name", sa.String),
        sa.column("required_skills", postgresql.JSONB),
        sa.column("preferred_skills", postgresql.JSONB),
    )
    op.bulk_insert(
        job_table,
        [
            {
                "role_name": profile["role_name"],
                "required_skills": profile["required_skills"],
                "preferred_skills": profile["preferred_skills"],
            }
            for profile in JOB_PROFILES_SEED
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_ats_analyses_user_id_created_at", table_name="ats_analyses")
    op.drop_index("ix_ats_analyses_resume_id", table_name="ats_analyses")
    op.drop_index("ix_ats_analyses_user_id", table_name="ats_analyses")
    op.drop_table("ats_analyses")
    op.drop_table("job_profiles")
    op.drop_table("skill_taxonomy")
