"""baseline data

Revision ID: 61aa206c7e8c
Revises: 
Create Date: 2021-07-19 15:24:32.251868

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

# revision identifiers, used by Alembic.
revision = "61aa206c7e8c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("created_by_", sa.String(), nullable=False),
        sa.Column("modified", sa.DateTime(), nullable=False),
        sa.Column("modified_by_", sa.String(), nullable=False),
        sa.Column("nhs_smartcard_number", sa.String(), nullable=True),
        sa.Column("send_entry_identifier", sa.String(), nullable=True),
        sa.Column("job_title", sa.String(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("phone_number", sa.String(), nullable=False),
        sa.Column("email_address", sa.String(), nullable=False),
        sa.Column("can_edit_ews", sa.Boolean(), nullable=True),
        sa.Column("professional_registration_number", sa.String(), nullable=True),
        sa.Column("agency_name", sa.String(), nullable=True),
        sa.Column("agency_staff_employee_number", sa.String(), nullable=True),
        sa.Column("booking_reference", sa.String(), nullable=True),
        sa.Column("contract_expiry_eod_date", sa.Date(), nullable=True),
        sa.Column("password_hash", sa.String(), nullable=True),
        sa.Column("password_salt", sa.String(), nullable=True),
        sa.Column("login_active", sa.String(), nullable=True),
        sa.Column("analytics_consent", sa.String(), nullable=True),
        sa.Column("groups", ARRAY(sa.String()), nullable=True),
        sa.Column("locations", ARRAY(sa.String()), nullable=True),
        sa.Column("bookmarks", ARRAY(sa.String()), nullable=True),
        sa.Column("bookmarked_patients", ARRAY(sa.String()), nullable=True),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("uuid"),
        sa.UniqueConstraint("email_address"),
        sa.UniqueConstraint("send_entry_identifier"),
    )
    op.execute('CREATE INDEX idx_groups on "user" USING GIN ("groups");')
    op.execute('CREATE INDEX idx_locations on "user" USING GIN ("locations");')
    op.execute('CREATE INDEX idx_bookmarks on "user" USING GIN ("bookmarks");')
    op.execute(
        'CREATE INDEX idx_bookmarked_patients on "user" USING GIN ("bookmarked_patients");'
    )

    op.create_index("modified_idx", "user", ["modified"], unique=False)
    op.create_index("first_name_idx", "user", ["first_name"], unique=False)
    op.create_index("last_name_idx", "user", ["last_name"], unique=False)
    op.create_index(
        "send_entry_identifier_idx", "user", ["send_entry_identifier"], unique=False
    )
    op.create_index("email_address_idx", "user", ["email_address"], unique=False)

    op.create_table(
        "product",
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("created_by_", sa.String(), nullable=False),
        sa.Column("modified", sa.DateTime(), nullable=False),
        sa.Column("modified_by_", sa.String(), nullable=False),
        sa.Column("product_name", sa.String(), nullable=False),
        sa.Column("opened_date", sa.Date(), nullable=False),
        sa.Column("closed_date", sa.Date(), nullable=True),
        sa.Column("location_uuid", sa.String(), nullable=True),
        sa.Column("closed_reason", sa.String(), nullable=True),
        sa.Column("closed_reason_other", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.uuid"]),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index("product_name_idx", "product", ["product_name"], unique=False)

    op.create_table(
        "terms_agreement",
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("created_by_", sa.String(), nullable=False),
        sa.Column("modified", sa.DateTime(), nullable=False),
        sa.Column("modified_by_", sa.String(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("product_name", sa.String(), nullable=False),
        sa.Column("accepted_timestamp", sa.DateTime(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.uuid"]),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("uuid"),
    )


def downgrade():
    op.drop_table("product")
    op.drop_table("terms_agreement")
    op.drop_table("user")
