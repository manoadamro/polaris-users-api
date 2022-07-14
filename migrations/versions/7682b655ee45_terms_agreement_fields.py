"""terms agreement fields

Revision ID: 7682b655ee45
Revises: 061d25d8199d
Create Date: 2022-02-23 13:26:52.604221

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7682b655ee45"
down_revision = "061d25d8199d"
branch_labels = None
depends_on = None


def upgrade():
    print("Add extra terms agreement fields")
    op.add_column(
        "terms_agreement", sa.Column("tou_version", sa.Integer(), nullable=True)
    )
    op.add_column(
        "terms_agreement",
        sa.Column("tou_accepted_timestamp", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "terms_agreement",
        sa.Column("patient_notice_version", sa.Integer(), nullable=True),
    )
    op.add_column(
        "terms_agreement",
        sa.Column(
            "patient_notice_accepted_timestamp",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.alter_column(
        "terms_agreement", "version", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "terms_agreement",
        "accepted_timestamp",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )


def downgrade():
    print("Drop extra terms agreement fields")
    op.alter_column(
        "terms_agreement",
        "accepted_timestamp",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
    )
    op.alter_column(
        "terms_agreement", "version", existing_type=sa.INTEGER(), nullable=False
    )
    op.drop_column("terms_agreement", "patient_notice_accepted_timestamp")
    op.drop_column("terms_agreement", "patient_notice_version")
    op.drop_column("terms_agreement", "tou_accepted_timestamp")
    op.drop_column("terms_agreement", "tou_version")
