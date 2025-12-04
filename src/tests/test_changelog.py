import sys

from schematools.types import DatasetSchema

sys.path.append("..")

from schema_api.management.commands.changelog import extract_diffs_for_dataset


class TestChangelogCommand:

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
            "lifecyclestatus": "stable",
            "object_id": "bomen/v1/groeiplaatsmedebeheer",
            "label": "modify",
        }
        assert db_updates[1] == {
            "dataset_id": "bomen",
            "lifecyclestatus": "stable",
            "object_id": "bomen/v2/groeiplaatsmedebeheer",
            "label": "modify",
        }

    def test_changelog_create_table(
        self,
        base_dataset: DatasetSchema,
        create_table: DatasetSchema,
    ):
        """
        Response does not contain commit id and date.
        Decide: add mock values or don't compare in these tests
        """

        # Mimic functionality of changelog command
        diffs = base_dataset.get_diffs(create_table)
        db_updates = extract_diffs_for_dataset(diffs, create_table)

        assert len(db_updates) == 2
        assert db_updates[0] == {
            "dataset_id": "bomen",
            "lifecyclestatus": "stable",
            "object_id": "bomen/v1/stamgegevens",
            "label": "create",
        }
        assert db_updates[1] == {
            "dataset_id": "bomen",
            "lifecyclestatus": "stable",
            "object_id": "bomen/v2/stamgegevens",
            "label": "create",
        }

    def test_changelog_create_dataset_version(
        self,
        base_dataset: DatasetSchema,
        create_dataset: DatasetSchema,
    ):
        """
        Response does not contain commit id and date.
        Decide: add mock values or don't compare in these tests
        """

        # Mimic functionality of changelog command
        diffs = base_dataset.get_diffs(create_dataset)
        db_updates = extract_diffs_for_dataset(diffs, create_dataset)

        assert len(db_updates) == 1
        assert db_updates[0] == {
            "dataset_id": "bomen",
            "lifecyclestatus": "experimental",
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
            "lifecyclestatus": "stable",
            "object_id": "bomen/v2",
            "label": "status",
        }

    def test_changelog_update_table_create_ds(
        self,
        base_dataset: DatasetSchema,
        update_table_create_ds: DatasetSchema,
    ):
        """
        Response does not contain commit id and date.
        Decide: add mock values or don't compare in these tests
        """

        # Mimic functionality of changelog command
        diffs = base_dataset.get_diffs(update_table_create_ds)
        db_updates = extract_diffs_for_dataset(diffs, update_table_create_ds)

        assert len(db_updates) == 3
        assert db_updates[0] == {
            "dataset_id": "bomen",
            "lifecyclestatus": "stable",
            "object_id": "bomen/v1/groeiplaatsmedebeheer",
            "label": "modify",
        }
        assert db_updates[1] == {
            "dataset_id": "bomen",
            "lifecyclestatus": "stable",
            "object_id": "bomen/v2/groeiplaatsmedebeheer",
            "label": "modify",
        }
        assert db_updates[2] == {
            "dataset_id": "bomen",
            "lifecyclestatus": "experimental",
            "object_id": "bomen/v3",
            "label": "create",
        }

    def test_changelog_patch_table(
        self,
        base_dataset: DatasetSchema,
        patch_table: DatasetSchema,
    ):
        """
        Response does not contain commit id and date.
        Decide: add mock values or don't compare in these tests
        """

        # Mimic functionality of changelog command
        diffs = base_dataset.get_diffs(patch_table)
        db_updates = extract_diffs_for_dataset(diffs, patch_table)

        assert db_updates == []
