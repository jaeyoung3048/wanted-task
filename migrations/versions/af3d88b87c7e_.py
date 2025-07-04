# ruff: noqa
# mypy: ignore-errors
"""
empty message

Revision ID: af3d88b87c7e
Revises: bf1f83bcc53e
Create Date: 2025-06-25 15:34:53.345302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af3d88b87c7e'
down_revision: Union[str, Sequence[str], None] = 'bf1f83bcc53e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_companyname_lang_code', 'company_name', ['lang_code'], unique=False)
    op.create_index('ix_companyname_name', 'company_name', ['name'], unique=False)
    op.create_index('ix_companyname_name_fulltext', 'company_name', ['name'], unique=False, mysql_prefix='FULLTEXT', mysql_with_parser='ngram')
    op.create_index('ix_companytag_company_id', 'company_tag', ['company_id'], unique=False)
    op.create_index('ix_companytag_tag_id', 'company_tag', ['tag_id'], unique=False)
    op.create_index('ix_tagname_lang_code', 'tag_name', ['lang_code'], unique=False)
    op.create_index('ix_tagname_name', 'tag_name', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_tagname_name', table_name='tag_name')
    op.drop_index('ix_tagname_lang_code', table_name='tag_name')
    op.drop_index('ix_companytag_tag_id', table_name='company_tag')
    op.drop_index('ix_companytag_company_id', table_name='company_tag')
    op.drop_index('ix_companyname_name_fulltext', table_name='company_name', mysql_prefix='FULLTEXT', mysql_with_parser='ngram')
    op.drop_index('ix_companyname_name', table_name='company_name')
    op.drop_index('ix_companyname_lang_code', table_name='company_name')
    # ### end Alembic commands ###
