"""Migration Templates for Common Database Operations

This module provides templates for common migration operations to ensure
consistency and best practices across all migrations.
"""

from typing import Any


class MigrationTemplates:
    """Templates for common migration operations"""

    @staticmethod
    def add_column_template(
        table_name: str,
        column_name: str,
        column_type: str,
        nullable: bool = True,
        default: Any = None,
        comment: str = None,
    ) -> dict[str, str]:
        """
        Template for adding a column to a table

        Args:
            table_name: Name of the table
            column_name: Name of the column to add
            column_type: SQLAlchemy column type (e.g., 'sa.String(255)')
            nullable: Whether column can be NULL
            default: Default value for the column
            comment: Column comment/description

        Returns:
            Dictionary with upgrade and downgrade SQL
        """
        default_clause = f", server_default={repr(default)}" if default else ""
        comment_clause = f", comment={repr(comment)}" if comment else ""

        upgrade = f"""
    # Add {column_name} column to {table_name}
    op.add_column(
        '{table_name}',
        sa.Column(
            '{column_name}',
            {column_type},
            nullable={nullable}{default_clause}{comment_clause}
        )
    )
"""

        downgrade = f"""
    # Remove {column_name} column from {table_name}
    op.drop_column('{table_name}', '{column_name}')
"""

        return {"upgrade": upgrade, "downgrade": downgrade}

    @staticmethod
    def add_index_template(
        table_name: str,
        column_names: list[str],
        unique: bool = False,
        index_name: str = None,
    ) -> dict[str, str]:
        """
        Template for adding an index to a table

        Args:
            table_name: Name of the table
            column_names: List of column names to index
            unique: Whether index should be unique
            index_name: Optional custom index name

        Returns:
            Dictionary with upgrade and downgrade SQL
        """
        columns_str = ", ".join([f"'{col}'" for col in column_names])
        index_type = "unique index" if unique else "index"

        if not index_name:
            prefix = "uix" if unique else "ix"
            index_name = f"{prefix}_{table_name}_{'_'.join(column_names)}"

        upgrade = f"""
    # Add {index_type} on {table_name}({', '.join(column_names)})
    op.create_index(
        '{index_name}',
        '{table_name}',
        [{columns_str}],
        unique={unique}
    )
"""

        downgrade = f"""
    # Remove {index_type} from {table_name}
    op.drop_index('{index_name}', table_name='{table_name}')
"""

        return {"upgrade": upgrade, "downgrade": downgrade}

    @staticmethod
    def add_foreign_key_template(
        table_name: str,
        column_name: str,
        ref_table: str,
        ref_column: str = "id",
        constraint_name: str = None,
        ondelete: str = "CASCADE",
    ) -> dict[str, str]:
        """
        Template for adding a foreign key constraint

        Args:
            table_name: Name of the table
            column_name: Name of the foreign key column
            ref_table: Referenced table name
            ref_column: Referenced column name (default: 'id')
            constraint_name: Optional custom constraint name
            ondelete: ON DELETE action (CASCADE, SET NULL, RESTRICT)

        Returns:
            Dictionary with upgrade and downgrade SQL
        """
        if not constraint_name:
            constraint_name = f"fk_{table_name}_{column_name}_{ref_table}"

        upgrade = f"""
    # Add foreign key constraint
    op.create_foreign_key(
        '{constraint_name}',
        '{table_name}',
        '{ref_table}',
        ['{column_name}'],
        ['{ref_column}'],
        ondelete='{ondelete}'
    )
"""

        downgrade = f"""
    # Remove foreign key constraint
    op.drop_constraint(
        '{constraint_name}',
        '{table_name}',
        type_='foreignkey'
    )
"""

        return {"upgrade": upgrade, "downgrade": downgrade}

    @staticmethod
    def create_table_template(
        table_name: str,
        columns: list[dict[str, Any]],
        with_timestamps: bool = True,
        with_soft_delete: bool = True,
    ) -> dict[str, str]:
        """
        Template for creating a new table

        Args:
            table_name: Name of the table to create
            columns: List of column definitions
            with_timestamps: Add created_at/updated_at columns
            with_soft_delete: Add deleted_at column for soft deletes

        Returns:
            Dictionary with upgrade and downgrade SQL
        """
        column_defs = []

        # Add primary key
        column_defs.append(
            "        sa.Column('id', sa.String(36), primary_key=True)"
        )

        # Add custom columns
        for col in columns:
            col_def = f"        sa.Column('{col['name']}', {col['type']}"
            if not col.get("nullable", True):
                col_def += ", nullable=False"
            if "default" in col:
                col_def += f", server_default={repr(col['default'])}"
            if "comment" in col:
                col_def += f", comment={repr(col['comment'])}"
            col_def += ")"
            column_defs.append(col_def)

        # Add timestamp columns
        if with_timestamps:
            column_defs.append(
                "        sa.Column('created_at', sa.DateTime(), "
                "nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))"
            )
            column_defs.append(
                "        sa.Column('updated_at', sa.DateTime(), "
                "nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), "
                "onupdate=sa.text('CURRENT_TIMESTAMP'))"
            )

        # Add soft delete column
        if with_soft_delete:
            column_defs.append(
                "        sa.Column('deleted_at', sa.DateTime(), nullable=True)"
            )

        columns_str = ",\n".join(column_defs)

        upgrade = f"""
    # Create {table_name} table
    op.create_table(
        '{table_name}',
{columns_str}
    )
"""

        downgrade = f"""
    # Drop {table_name} table
    op.drop_table('{table_name}')
"""

        return {"upgrade": upgrade, "downgrade": downgrade}

    @staticmethod
    def rename_column_template(
        table_name: str, old_name: str, new_name: str
    ) -> dict[str, str]:
        """
        Template for renaming a column

        Args:
            table_name: Name of the table
            old_name: Current column name
            new_name: New column name

        Returns:
            Dictionary with upgrade and downgrade SQL
        """
        upgrade = f"""
    # Rename column {old_name} to {new_name}
    op.alter_column(
        '{table_name}',
        '{old_name}',
        new_column_name='{new_name}'
    )
"""

        downgrade = f"""
    # Rename column {new_name} back to {old_name}
    op.alter_column(
        '{table_name}',
        '{new_name}',
        new_column_name='{old_name}'
    )
"""

        return {"upgrade": upgrade, "downgrade": downgrade}

    @staticmethod
    def add_check_constraint_template(
        table_name: str,
        constraint_name: str,
        condition: str,
    ) -> dict[str, str]:
        """
        Template for adding a check constraint

        Args:
            table_name: Name of the table
            constraint_name: Name of the constraint
            condition: SQL condition for the check

        Returns:
            Dictionary with upgrade and downgrade SQL
        """
        upgrade = f"""
    # Add check constraint
    op.create_check_constraint(
        '{constraint_name}',
        '{table_name}',
        '{condition}'
    )
"""

        downgrade = f"""
    # Remove check constraint
    op.drop_constraint(
        '{constraint_name}',
        '{table_name}',
        type_='check'
    )
"""

        return {"upgrade": upgrade, "downgrade": downgrade}

    @staticmethod
    def data_migration_template(
        description: str,
        upgrade_sql: str,
        downgrade_sql: str = None,
    ) -> dict[str, str]:
        """
        Template for data migrations

        Args:
            description: Description of the data migration
            upgrade_sql: SQL for upgrading data
            downgrade_sql: SQL for downgrading data (optional)

        Returns:
            Dictionary with upgrade and downgrade SQL
        """
        upgrade = f"""
    # Data migration: {description}
    op.execute('''
{upgrade_sql}
    ''')
"""

        if downgrade_sql:
            downgrade = f"""
    # Rollback data migration: {description}
    op.execute('''
{downgrade_sql}
    ''')
"""
        else:
            downgrade = """
    # Data migration rollback not implemented
    pass
"""

        return {"upgrade": upgrade, "downgrade": downgrade}


def generate_migration_code(template_name: str, **kwargs) -> dict[str, str]:
    """
    Generate migration code from a template

    Args:
        template_name: Name of the template to use
        **kwargs: Template-specific arguments

    Returns:
        Dictionary with upgrade and downgrade code

    Raises:
        ValueError: If template name is invalid
    """
    templates = MigrationTemplates()

    template_map = {
        "add_column": templates.add_column_template,
        "add_index": templates.add_index_template,
        "add_foreign_key": templates.add_foreign_key_template,
        "create_table": templates.create_table_template,
        "rename_column": templates.rename_column_template,
        "add_check_constraint": templates.add_check_constraint_template,
        "data_migration": templates.data_migration_template,
    }

    if template_name not in template_map:
        raise ValueError(
            f"Unknown template: {template_name}. "
            f"Available templates: {list(template_map.keys())}"
        )

    return template_map[template_name](**kwargs)
