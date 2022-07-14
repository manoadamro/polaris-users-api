"""field default

Revision ID: e66d175c24d5
Revises: 7682b655ee45
Create Date: 2022-05-06 16:06:58.104559

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import false

revision = "e66d175c24d5"
down_revision = "7682b655ee45"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "user",
        "can_edit_ews",
        existing_type=sa.BOOLEAN(),
        nullable=False,
        server_default=false(),
    )


def downgrade():
    op.alter_column("user", "can_edit_ews", existing_type=sa.BOOLEAN(), nullable=True)
