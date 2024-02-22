"""Dodata kolicina

Revision ID: 0addc7395d48
Revises: bce28c7fee7d
Create Date: 2023-07-10 14:18:11.651979

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0addc7395d48'
down_revision = 'bce28c7fee7d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pripada_narudzbini', sa.Column('kolicina', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pripada_narudzbini', 'kolicina')
    # ### end Alembic commands ###
