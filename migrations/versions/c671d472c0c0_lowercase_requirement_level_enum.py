"""lowercase requirement_level enum

Revision ID: c671d472c0c0
Revises: 846f1220addc
Create Date: 2026-01-27 16:28:56.586298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c671d472c0c0'
down_revision: Union[str, Sequence[str], None] = '846f1220addc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create new enum with lowercase values
    op.execute("""
        CREATE TYPE requirement_level_new AS ENUM (
            'required',
            'preferred',
            'optional'
        );
    """)

    # 2. Update column to use new enum (cast values)
    op.execute("""
        ALTER TABLE event_assignments
        ALTER COLUMN requirement_level
        TYPE requirement_level_new
        USING LOWER(requirement_level::text)::requirement_level_new;
    """)

    # 3. Drop old enum
    op.execute("DROP TYPE requirement_level;")

    # 4. Rename new enum to original name
    op.execute("""
        ALTER TYPE requirement_level_new
        RENAME TO requirement_level;
    """)



def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        CREATE TYPE requirement_level_old AS ENUM (
            'REQUIRED',
            'PREFERRED',
            'OPTIONAL'
        );
    """)

    op.execute("""
        ALTER TABLE event_assignments
        ALTER COLUMN requirement_level
        TYPE requirement_level_old
        USING UPPER(requirement_level::text)::requirementlevel_old;
    """)

    op.execute("DROP TYPE requirement_level;")

    op.execute("""
        ALTER TYPE requirement_level_old
        RENAME TO requirement_level;
    """)

