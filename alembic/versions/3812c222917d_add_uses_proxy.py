"""Add uses_proxy

Revision ID: 3812c222917d
Revises: 76668d91d087
Create Date: 2019-02-19 12:30:01.251441

"""

# revision identifiers, used by Alembic.
revision = '3812c222917d'
down_revision = '76668d91d087'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(u'SiWaySAMLUsers')
    op.add_column('EmbedApplications', sa.Column('uses_proxy', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('EmbedApplications', 'uses_proxy')
    op.create_table(u'SiWaySAMLUsers',
    sa.Column(u'id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column(u'email', mysql.VARCHAR(length=255), nullable=False),
    sa.Column(u'uid', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column(u'employee_type', mysql.VARCHAR(length=255), nullable=False),
    sa.Column(u'full_name', mysql.VARCHAR(length=255), nullable=False),
    sa.Column(u'short_name', mysql.VARCHAR(length=255), nullable=False),
    sa.Column(u'school_name', mysql.VARCHAR(length=255), nullable=False),
    sa.Column(u'group', mysql.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint(u'id'),
    mysql_default_charset=u'latin1',
    mysql_engine=u'InnoDB'
    )
    ### end Alembic commands ###
