from alembic import op
import sqlalchemy as sa


revision = "7c2a91b4d6e8"
down_revision = "94019e50c840"
branch_labels = None
depends_on = None


def upgrade() -> None:
    platforms = sa.table(
        "platforms",
        sa.column("name", sa.String),
        sa.column("code", sa.String),
        sa.column("color", sa.String),
    )

    op.bulk_insert(
        platforms,
        [
            {
                "name": "Uber",
                "code": "uber",
                "color": "#FFFFFF",
            },
            {
                "name": "99",
                "code": "99",
                "color": "#FFD500",
            },
            {
                "name": "inDrive",
                "code": "indrive",
                "color": "#20C978",
            },
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM platforms "
            "WHERE code IN ('uber', '99', 'indrive')"
        )
    )
