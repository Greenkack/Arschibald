"""
Example Migration: Migrate User Data
Demonstrates data transformation with progress tracking.
"""

from migration_manager import MigrationStep, MigrationType
from data_transformer import DataTransformer
from progress_tracker import ProgressTracker
import logging

logger = logging.getLogger(__name__)


def create_migration() -> MigrationStep:
    """Create migration step for transforming user data"""
    
    def up_function(session):
        """Transform user data"""
        transformer = DataTransformer(session)
        tracker = ProgressTracker(total_steps=3)
        
        # Step 1: Normalize usernames
        tracker.start_step("Normalizing usernames")
        rows_normalized = transformer.normalize_text(
            table='users',
            column='username',
            lowercase=True,
            strip=True,
            remove_extra_spaces=True
        )
        tracker.complete_step()
        
        # Step 2: Split full_name into first_name and last_name
        tracker.start_step("Splitting names")
        rows_split = transformer.split_column(
            table='users',
            source_column='full_name',
            target_columns=['first_name', 'last_name'],
            separator=' '
        )
        tracker.complete_step()
        
        # Step 3: Convert status codes
        tracker.start_step("Converting status codes")
        status_map = {
            '0': 'inactive',
            '1': 'active',
            '2': 'suspended',
            '3': 'deleted'
        }
        rows_converted = transformer.map_values(
            table='users',
            column='status',
            value_map=status_map,
            default_value='inactive'
        )
        tracker.complete_step()
        
        logger.info(f"Migration complete: {rows_normalized + rows_split + rows_converted} rows affected")
        
        return rows_normalized + rows_split + rows_converted
    
    def down_function(session):
        """Rollback user data transformation"""
        transformer = DataTransformer(session)
        
        # Merge names back
        rows_merged = transformer.merge_columns(
            table='users',
            source_columns=['first_name', 'last_name'],
            target_column='full_name',
            separator=' '
        )
        
        # Revert status codes
        status_map = {
            'inactive': '0',
            'active': '1',
            'suspended': '2',
            'deleted': '3'
        }
        rows_reverted = transformer.map_values(
            table='users',
            column='status',
            value_map=status_map
        )
        
        return rows_merged + rows_reverted
    
    return MigrationStep(
        id="002_migrate_user_data",
        name="Transform User Data",
        description="Normalize usernames, split names, and convert status codes",
        type=MigrationType.DATA,
        up_function=up_function,
        down_function=down_function,
        dependencies=["001_add_user_columns"]
    )
