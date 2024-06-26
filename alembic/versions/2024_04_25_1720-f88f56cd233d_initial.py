"""Initial

Revision ID: f88f56cd233d
Revises: 
Create Date: 2024-04-25 17:20:06.619622

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f88f56cd233d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('host',
    sa.Column('host_id', sa.String(), nullable=False),
    sa.Column('biosreleasedate', sa.String(), nullable=False),
    sa.Column('host_bios_version', sa.String(), nullable=False),
    sa.Column('host_cpu_arch', sa.String(), nullable=False),
    sa.Column('host_cpu_core', sa.Integer(), nullable=False),
    sa.Column('host_cpu_socket', sa.Integer(), nullable=False),
    sa.Column('host_cpu_type', sa.String(), nullable=False),
    sa.Column('host_ram', sa.Integer(), nullable=False),
    sa.Column('swap_memory_size', sa.Integer(), nullable=False),
    sa.Column('host_serial_number', sa.String(), nullable=False),
    sa.Column('host_vendor', sa.String(), nullable=False),
    sa.Column('hostname', sa.String(), nullable=False),
    sa.Column('host_os_family_lu', sa.String(), nullable=False),
    sa.Column('host_os_kernel', sa.String(), nullable=False),
    sa.Column('host_os_kernel_full', sa.String(), nullable=False),
    sa.Column('host_os_name', sa.String(), nullable=False),
    sa.Column('host_os_release', sa.String(), nullable=False),
    sa.Column('host_os_version', sa.String(), nullable=False),
    sa.Column('host_dns_name', sa.String(), nullable=False),
    sa.Column('host_ip_address', sa.String(), nullable=False),
    sa.Column('host_model', sa.String(), nullable=False),
    sa.Column('old_cache_hash', sa.String(), nullable=False),
    sa.Column('new_hash', sa.String(), nullable=False),
    sa.Column('host_dns_server', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('host_ip_addresses', postgresql.ARRAY(sa.String()), nullable=False),
    sa.PrimaryKeyConstraint('host_id')
    )
    op.create_table('host_disk2stor_map',
    sa.Column('disk_id', sa.Integer(), nullable=False),
    sa.Column('host_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('serial', sa.String(), nullable=False),
    sa.Column('vendor', sa.String(), nullable=False),
    sa.Column('model', sa.String(), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('kname', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('mountpoint', sa.String(), nullable=False),
    sa.Column('pkname', sa.String(), nullable=False),
    sa.Column('children', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['host_id'], ['host.host_id'], ),
    sa.PrimaryKeyConstraint('disk_id')
    )
    op.create_table('host_netadapter_html',
    sa.Column('neadapter_id', sa.Integer(), nullable=False),
    sa.Column('host_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('mac_address', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['host_id'], ['host.host_id'], ),
    sa.PrimaryKeyConstraint('neadapter_id')
    )
    op.create_table('host_pkgs_list',
    sa.Column('host_pkg_id', sa.Integer(), nullable=False),
    sa.Column('host_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('version', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['host_id'], ['host.host_id'], ),
    sa.PrimaryKeyConstraint('host_pkg_id')
    )
    op.create_table('host_users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('host_id', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('uid', sa.Integer(), nullable=False),
    sa.Column('gid', sa.Integer(), nullable=False),
    sa.Column('home_dir', sa.String(), nullable=False),
    sa.Column('shell', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['host_id'], ['host.host_id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('ips_info',
    sa.Column('ips_id', sa.Integer(), nullable=False),
    sa.Column('host_id_netadapter_html', sa.Integer(), nullable=False),
    sa.Column('ip', sa.String(), nullable=False),
    sa.Column('netmask', sa.String(), nullable=False),
    sa.Column('network', sa.String(), nullable=False),
    sa.Column('alias', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['host_id_netadapter_html'], ['host_netadapter_html.neadapter_id'], ),
    sa.PrimaryKeyConstraint('ips_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ips_info')
    op.drop_table('host_users')
    op.drop_table('host_pkgs_list')
    op.drop_table('host_netadapter_html')
    op.drop_table('host_disk2stor_map')
    op.drop_table('host')
    # ### end Alembic commands ###
