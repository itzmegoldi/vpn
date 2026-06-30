"""create vpn tables

Revision ID: create_vpn_tables
Revises:
Create Date: 2026-05-31 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op


revision: str = "create_vpn_tables"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vpn_servers",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("public_ip", sa.String(), nullable=False),
        sa.Column("ssh_username", sa.String(), nullable=False),
        sa.Column("ssh_key", sa.String(), nullable=False),
        sa.Column("wireguard_interface", sa.String(), nullable=True),
        sa.Column("wireguard_port", sa.Integer(), nullable=True),
        sa.Column("vpn_subnet", sa.String(), nullable=True),
        sa.Column("server_vpn_ip", sa.String(), nullable=True),
        sa.Column("server_private_key", sa.Text(), nullable=False),
        sa.Column("server_public_key", sa.Text(), nullable=False),
        sa.Column("config_text", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "vpn_clients",
        sa.Column("server_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("client_private_key", sa.Text(), nullable=False),
        sa.Column("client_public_key", sa.Text(), nullable=False),
        sa.Column("client_ip", sa.String(), nullable=False),
        sa.Column("config_text", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["server_id"], ["vpn_servers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("vpn_clients")
    op.drop_table("vpn_servers")
