"""corrected typo in isbeingverified

Revision ID: 8aa6e11347b2
Revises: 49092dba9ecf
Create Date: 2022-06-14 23:34:41.528683

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8aa6e11347b2'
down_revision = '49092dba9ecf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_being_verified', sa.Boolean(), nullable=True))
    op.drop_column('user', 'id_being_verified')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('id_being_verified', sa.BOOLEAN(), nullable=True))
    op.drop_column('user', 'is_being_verified')
    # ### end Alembic commands ###