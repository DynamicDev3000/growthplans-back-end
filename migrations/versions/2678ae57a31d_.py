"""empty message

Revision ID: 2678ae57a31d
Revises: 5a3baafda6cb
Create Date: 2021-11-01 16:12:21.006128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2678ae57a31d'
down_revision = '5a3baafda6cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('goal', sa.Column('id', sa.Integer(), nullable=False))
    op.add_column('goal', sa.Column('title', sa.String(), nullable=True))
    op.drop_column('goal', 'goal_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('goal', sa.Column('goal_id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.drop_column('goal', 'title')
    op.drop_column('goal', 'id')
    # ### end Alembic commands ###