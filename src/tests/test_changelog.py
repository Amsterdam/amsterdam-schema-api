import sys
from datetime import datetime, timezone

import pytest
from django.core.management import call_command
from schematools.types import DatasetSchema

from schema_api.models import ChangelogItem

sys.path.append("..")

from schema_api.management.commands.changelog import extract_diffs_for_dataset


class TestChangelogCommand:

    @pytest.mark.django_db
    def test_changelog_command(self):
        """
        Test the full changelog command with specified start and end commit.
        Also test commit hash and commit_at timestamp,
        these cannot be tested in the following tests.
        """

        start_commit = "e339b8440466713461065365bfb70d6cb61ca959"
        end_commit = "7324aedea431e9b364ed18340a21a5f79b9bda0e"
        args = ["--start_commit", start_commit, "--end_commit", end_commit]

        call_command("changelog", *args)

        assert ChangelogItem.objects.count() == 2

        item1 = ChangelogItem.objects.get(id=1)
        assert item1.object_id == "benkagg/v1/brkkaartlaageigenaren"
        assert item1.commit_hash == end_commit
        assert item1.committed_at == datetime(2025, 11, 26, 14, 17, 15, tzinfo=timezone.utc)

        item2 = ChangelogItem.objects.get(id=2)
        assert item2.object_id == "benkagg/v1/brkkaartlaagerfpachtuitgevers"
        assert item2.commit_hash == end_commit
        assert item2.committed_at == datetime(2025, 11, 26, 14, 17, 15, tzinfo=timezone.utc)

    def test_changelog_deepdiff_field_names(
        self,
        base_dataset: DatasetSchema,
        create_table: DatasetSchema,
        update_table_create_ds: DatasetSchema,
    ):
        """
        Test if field names from DeepDiff output remain the same
        """
        diffs_1 = base_dataset.get_diffs(create_table)
        deepdiff_fields = list(diffs_1)
        diffs_2 = base_dataset.get_diffs(update_table_create_ds)
        deepdiff_fields.extend(list(diffs_2))
        assert set(deepdiff_fields) == {
            "iterable_item_added",
            "dictionary_item_added",
            "values_changed",
        }

    def test_changelog_update_table_a(
        self,
        base_dataset: DatasetSchema,
        update_table: DatasetSchema,
    ):
        """
        Update on table that is used in 2 dataset versions.
        Should result in a seperate update for both versions.
        """

        # Mimic functionality of changelog command
        diffs = base_dataset.get_diffs(update_table)
        db_updates = extract_diffs_for_dataset(diffs, update_table)

        assert len(db_updates) == 2
        assert db_updates[0] == {
            "dataset_id": "bomen",
            "lifecycle_status": "stable",
            "object_id": "bomen/v1/groeiplaatsmedebeheer",
            "label": "update",
        }
        assert db_updates[1] == {
            "dataset_id": "bomen",
            "lifecycle_status": "stable",
            "object_id": "bomen/v2/groeiplaatsmedebeheer",
            "label": "update",
        }

    def test_changelog_create_table(
        self,
        base_dataset: DatasetSchema,
        create_table: DatasetSchema,
    ):
        """ """

        # Mimic functionality of changelog command
        diffs = base_dataset.get_diffs(create_table)
        db_updates = extract_diffs_for_dataset(diffs, create_table)

        assert len(db_updates) == 2
        assert db_updates[0] == {
            "dataset_id": "bomen",
            "lifecycle_status": "stable",
            "object_id": "bomen/v1/stamgegevens",
            "label": "create",
        }
        assert db_updates[1] == {
            "dataset_id": "bomen",
            "lifecycle_status": "stable",
            "object_id": "bomen/v2/stamgegevens",
            "label": "create",
        }

    def test_changelog_create_dataset_version(
        self,
        base_dataset: DatasetSchema,
        create_dataset_version: DatasetSchema,
    ):
        """ """

        # Mimic functionality of changelog command
        diffs = base_dataset.get_diffs(create_dataset_version)
        db_updates = extract_diffs_for_dataset(diffs, create_dataset_version)

        assert len(db_updates) == 1
        assert db_updates[0] == {
            "dataset_id": "bomen",
            "lifecycle_status": "experimental",
            "object_id": "bomen/v3",
            "label": "create",
        }

    def test_changelog_status_dataset(
        self,
        base_dataset: DatasetSchema,
        status_dataset: DatasetSchema,
    ):
        """
        Different than other tests: update_ds contains experimental v2 version,
        this is 'set to' stable (default value) in the base dataset
        """

        # Mimic functionality of changelog command
        diffs = status_dataset.get_diffs(base_dataset)
        db_updates = extract_diffs_for_dataset(diffs, base_dataset)

        assert len(db_updates) == 1
        assert db_updates[0] == {
            "dataset_id": "bomen",
            "lifecycle_status": "stable",
            "object_id": "bomen/v2",
            "label": "status",
        }

    def test_changelog_update_experimental_dataset(
        self,
        status_dataset: DatasetSchema,
        update_experimental_dataset: DatasetSchema,
    ):
        """
        Different than other tests: update_ds contains experimental v2 version,
        this is 'set to' stable (default value) in the base dataset
        """

        # Mimic functionality of changelog command
        diffs = status_dataset.get_diffs(update_experimental_dataset)
        db_updates = extract_diffs_for_dataset(diffs, status_dataset)

        assert len(db_updates) == 1
        assert db_updates[0] == {
            "dataset_id": "bomen",
            "label": "update",
            "lifecycle_status": "experimental",
            "object_id": "bomen/v2/groeiplaatsmedebeheer",
        }

    def test_changelog_update_table_create_ds(
        self,
        base_dataset: DatasetSchema,
        update_table_create_ds: DatasetSchema,
    ):
        """ """

        # Mimic functionality of changelog command
        diffs = base_dataset.get_diffs(update_table_create_ds)
        db_updates = extract_diffs_for_dataset(diffs, update_table_create_ds)

        assert len(db_updates) == 3
        assert db_updates[0] == {
            "dataset_id": "bomen",
            "lifecycle_status": "stable",
            "object_id": "bomen/v1/groeiplaatsmedebeheer",
            "label": "update",
        }
        assert db_updates[1] == {
            "dataset_id": "bomen",
            "lifecycle_status": "stable",
            "object_id": "bomen/v2/groeiplaatsmedebeheer",
            "label": "update",
        }
        assert db_updates[2] == {
            "dataset_id": "bomen",
            "lifecycle_status": "experimental",
            "object_id": "bomen/v3",
            "label": "create",
        }

    def test_changelog_patch_table(
        self,
        base_dataset: DatasetSchema,
        patch_table: DatasetSchema,
    ):
        """ """

        # Mimic functionality of changelog command
        diffs = base_dataset.get_diffs(patch_table)
        db_updates = extract_diffs_for_dataset(diffs, patch_table)

        assert db_updates == []
