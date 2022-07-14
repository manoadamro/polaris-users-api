"""Make fields nullable, add can_edit_encounter


Revision ID: 061d25d8199d
Revises: 61aa206c7e8c
Create Date: 2022-02-22 15:09:13.965737

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "061d25d8199d"
down_revision = "61aa206c7e8c"
branch_labels = None
depends_on = None


def upgrade():
    print("Making fields nullable, adding can_edit_encounter")
    op.alter_column(
        "product", "user_id", existing_type=sa.VARCHAR(length=36), nullable=True
    )
    op.drop_index("product_name_idx", table_name="product")
    op.create_index(op.f("ix_product_user_id"), "product", ["user_id"], unique=False)
    op.drop_column("product", "location_uuid")
    op.alter_column(
        "terms_agreement",
        "accepted_timestamp",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
    op.alter_column(
        "terms_agreement", "user_id", existing_type=sa.VARCHAR(length=36), nullable=True
    )
    op.create_index(
        op.f("ix_terms_agreement_user_id"), "terms_agreement", ["user_id"], unique=False
    )
    op.add_column("user", sa.Column("can_edit_encounter", sa.Boolean(), nullable=True))
    op.alter_column("user", "job_title", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("user", "first_name", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("user", "last_name", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("user", "phone_number", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column("user", "email_address", existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column(
        "user",
        "login_active",
        existing_type=sa.VARCHAR(),
        type_=sa.Boolean(),
        nullable=False,
        postgresql_using="login_active::boolean",
    )
    op.alter_column(
        "user",
        "analytics_consent",
        existing_type=sa.VARCHAR(),
        type_=sa.Boolean(),
        existing_nullable=True,
        postgresql_using="login_active::boolean",
    )
    op.drop_index("email_address_idx", table_name="user")
    op.drop_index("first_name_idx", table_name="user")
    op.drop_index("idx_bookmarked_patients", table_name="user")
    op.drop_index("idx_bookmarks", table_name="user")
    op.drop_index("idx_groups", table_name="user")
    op.drop_index("idx_locations", table_name="user")
    op.drop_index("last_name_idx", table_name="user")
    op.drop_index("modified_idx", table_name="user")
    op.drop_index("send_entry_identifier_idx", table_name="user")
    op.drop_constraint("user_email_address_key", "user", type_="unique")
    op.drop_constraint("user_send_entry_identifier_key", "user", type_="unique")
    op.create_index(
        op.f("ix_user_email_address"), "user", ["email_address"], unique=True
    )
    op.create_index(op.f("ix_user_first_name"), "user", ["first_name"], unique=False)
    op.create_index(op.f("ix_user_job_title"), "user", ["job_title"], unique=False)
    op.create_index(
        op.f("ix_user_nhs_smartcard_number"),
        "user",
        ["nhs_smartcard_number"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_send_entry_identifier"),
        "user",
        ["send_entry_identifier"],
        unique=False,
    )


def downgrade():
    print("Making fields not nullable, dropping can_edit_encounter")
    op.drop_index(op.f("ix_user_send_entry_identifier"), table_name="user")
    op.drop_index(op.f("ix_user_nhs_smartcard_number"), table_name="user")
    op.drop_index(op.f("ix_user_job_title"), table_name="user")
    op.drop_index(op.f("ix_user_first_name"), table_name="user")
    op.drop_index(op.f("ix_user_email_address"), table_name="user")
    op.create_unique_constraint(
        "user_send_entry_identifier_key", "user", ["send_entry_identifier"]
    )
    op.create_unique_constraint("user_email_address_key", "user", ["email_address"])
    op.create_index(
        "send_entry_identifier_idx", "user", ["send_entry_identifier"], unique=False
    )
    op.create_index("modified_idx", "user", ["modified"], unique=False)
    op.create_index("last_name_idx", "user", ["last_name"], unique=False)
    op.create_index("idx_locations", "user", ["locations"], unique=False)
    op.create_index("idx_groups", "user", ["groups"], unique=False)
    op.create_index("idx_bookmarks", "user", ["bookmarks"], unique=False)
    op.create_index(
        "idx_bookmarked_patients", "user", ["bookmarked_patients"], unique=False
    )
    op.create_index("first_name_idx", "user", ["first_name"], unique=False)
    op.create_index("email_address_idx", "user", ["email_address"], unique=False)
    op.alter_column(
        "user",
        "analytics_consent",
        existing_type=sa.Boolean(),
        type_=sa.VARCHAR(),
        existing_nullable=True,
    )
    op.alter_column(
        "user",
        "login_active",
        existing_type=sa.Boolean(),
        type_=sa.VARCHAR(),
        nullable=True,
    )
    op.alter_column("user", "email_address", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("user", "phone_number", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("user", "last_name", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("user", "first_name", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column("user", "job_title", existing_type=sa.VARCHAR(), nullable=False)
    op.drop_column("user", "can_edit_encounter")
    op.drop_index(op.f("ix_terms_agreement_user_id"), table_name="terms_agreement")
    op.alter_column(
        "terms_agreement",
        "user_id",
        existing_type=sa.VARCHAR(length=36),
        nullable=False,
    )
    op.alter_column(
        "terms_agreement",
        "accepted_timestamp",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
    )
    op.add_column(
        "product",
        sa.Column("location_uuid", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_index(op.f("ix_product_user_id"), table_name="product")
    op.create_index("product_name_idx", "product", ["product_name"], unique=False)
    op.alter_column(
        "product", "user_id", existing_type=sa.VARCHAR(length=36), nullable=False
    )
