from __future__ import annotations

import subprocess

from django.core.management import BaseCommand
from schematools.loaders import get_schema_loader
from schematools.types import DatasetSchema

CHANGES_DIR = "tmp/changes/"


class Command(BaseCommand):

    def handle(self, *args, **options):

        # Generate change folders for each commit to master
        # output = subprocess.run(
        # ["bash", "schema_api/scripts/clone_ams_schema.sh"],
        # capture_output=True,
        # )
        # print(output.stdout.decode("utf-8"))

        # Parse change folders into database entries
        # TODO: create changelog model + migration for table

        extend_changelog_table()


def extend_changelog_table():
    """
    Docstring
    """

    # Load commits into master
    commits = _load_changelog_commits()

    base_commit = ""
    for c in commits:

        # Temp just processing this one change
        if base_commit and base_commit == "306da010":

            print(f"Base commit: {base_commit}")
            print(f"Compare commit: {c}")
            print()

            # Extract changelog updates from update commit
            process_commit(base_commit, c)

        # Update commit will be base for next commit
        base_commit = c


def _load_changelog_commits():
    """Load historical commits into master branch of Amsterdam Schema"""

    with open("tmp/commits.txt") as f:
        return [commit.strip("\n") for commit in f.readlines()]


def process_commit(base_commit, update_commit):
    """
    Docstring
    """

    # Checkout the repo for both commits
    output = subprocess.check(
        ["bash", "schema_api/scripts/checkout_commits.sh", base_commit, update_commit],
        capture_output=True,
    )

    # Save the date
    date = output.stdout.decode("utf-8").strip()
    print(f"Date: {date}")

    commit_updates = []

    # Extract differences between schemas
    dataset_diffs = compare_schemas(base_commit, update_commit)
    for ds in dataset_diffs:
        diffs = dataset_diffs[ds]

        # Misschien lijst met database updates teruggeven? Datum is hetzelfde voor allemaal.
        # Of datum meegeven
        # Maybe extend the updates in this list instead of creating a new one
        # Maybe add this in compare schemas, now we're looping through the datasets twice
        db_updates = extract_diffs_for_dataset(diffs, ds)

        for change in db_updates:
            change["hash"] = update_commit
            change["date"] = date

            commit_updates.append(change)

    print(commit_updates)


def compare_schemas(base_commit, update_commit):
    """
    Docstring
    """

    base_path = CHANGES_DIR + base_commit + "/datasets"
    update_path = CHANGES_DIR + update_commit + "/datasets"

    base_schema = get_schema_loader(base_path).get_all_datasets()
    update_schema = get_schema_loader(update_path).get_all_datasets()

    dataset_diffs = {}

    # Loop through all datasets to get the diffs
    for id in update_schema:
        update_ds = update_schema[id]

        # This checks for added/modified tables in datasets
        if id in base_schema:
            base_ds = base_schema[id]

            # Make this a function that can be tested
            diffs = base_ds.get_diffs(update_ds)

            # Save diffs (if there are any)
            if diffs:
                dataset_diffs[update_ds] = diffs

    return dataset_diffs


def extract_diffs_for_dataset(diffs: dict, update_ds: DatasetSchema) -> list[dict]:
    """ """
    db_updates = []

    modifications = diffs.get("values_changed", [])
    for field in modifications:
        change_dict = {}
        field_list = _parse_deepdiff_field(field)

        # *** TABLE UPDATE ***
        # Maybe paste example of deepdiff change here
        if "tables" in field_list and field_list[-1] == "version":

            # Only handle minor table updates
            # Check schema tools if is there is a tool for this
            version_update = modifications[field]
            new_v = version_update["new_value"].split(".")
            old_v = version_update["old_value"].split(".")

            # E.g. old_v = 1.0.0 and new_v = 1.1.0
            if new_v[0] == old_v[0] and new_v[1] != old_v[1]:
                change_dict = _extract_table_info(field_list, update_ds, change_dict)
                change_dict["label"] = "modify"

        # *** LIFECYCLE STATUS UPDATE ***
        if "lifecycleStatus" in field_list:
            change_dict = _extract_dataset_info(field_list, update_ds, change_dict)

            # Set label to 'modify'
            change_dict["label"] = "status"

        # Add change to list of updates
        if change_dict:
            db_updates.append(change_dict)

    # Additions update
    additions = get_create_updates(diffs)

    for field in additions:
        change_dict = {}
        field_list = _parse_deepdiff_field(field)

        # Better check if it's table update (may come up when checking all commits)
        # *** CREATE TABLE ***
        if "tables" in field_list and len(field_list) < 7:

            change_dict = _extract_table_info(field_list, update_ds, change_dict)
            change_dict["label"] = "create"

        # Added version has just ['versions']['v2'] as items
        # Maybe a better check?
        # *** CREATE DATASET VERSION ***
        if len(field_list) == 2:
            change_dict = _extract_dataset_info(field_list, update_ds, change_dict)
            change_dict["label"] = "create"

        # Add change to list of updates
        if change_dict:
            db_updates.append(change_dict)

    return db_updates


def _extract_table_info(field_list, update_ds, change_dict):
    # From here can be made a function, exactly reused by create table
    # Check which variables are needed
    # Get table id (name)
    tables_index = field_list.index("tables")
    table_index = int(field_list[tables_index + 1])
    table_id = update_ds.tables[table_index].id

    # Get dataset vmajor
    ds_vmajor = field_list[tables_index - 1]

    # Get lifecycle status of DatasetVersion
    dataset_vmajor = update_ds.get_version(ds_vmajor)
    dataset_id = update_ds.id
    change_dict["dataset_id"] = dataset_id
    change_dict["lifecyclestatus"] = dataset_vmajor.lifecycle_status.value

    # Construct object id
    object_id = f"{dataset_id}/{ds_vmajor}/{table_id}"
    change_dict["object_id"] = object_id

    return change_dict


def _extract_dataset_info(field_list, update_ds, change_dict):
    versions_index = field_list.index("versions")
    ds_vmajor = field_list[versions_index + 1]

    # Get lifecycle status of DatasetVersion
    dataset_vmajor = update_ds.get_version(ds_vmajor)
    dataset_id = update_ds.id
    change_dict["dataset_id"] = dataset_id
    change_dict["lifecyclestatus"] = dataset_vmajor.lifecycle_status.value

    # Construct object id
    object_id = f"{dataset_id}/{ds_vmajor}"
    change_dict["object_id"] = object_id

    return change_dict


def get_create_updates(diffs):
    additions = []
    for key, value in diffs.items():
        if "added" in key:
            for key in value:
                additions.append(key)
    return additions


def _parse_deepdiff_field(field):
    """
    Parses a string of dict keys into a list of dict keys
    """
    if field.startswith("root"):
        field = field[4:]
    field = field.replace("]", "").replace("'", "")
    field_list = field.split("[")
    return [value for value in field_list if value]
