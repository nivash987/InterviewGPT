"""backfill email_verified_at for existing users

Revision ID: 0005_backfill_email_verified
Revises: 0004_interview_sessions
Create Date: 2026-06-02

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_backfill_email_verified"
down_revision: Union[str, None] = "0004_interview_sessions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE users SET email_verified_at = NOW() WHERE email_verified_at IS NULL"
        )
    )


def downgrade() -> None:
    pass
