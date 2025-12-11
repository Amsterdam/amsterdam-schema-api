from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime, timezone

from django.core.management import BaseCommand
from django.db.utils import IntegrityError
from schematools.loaders import get_schema_loader
from schematools.types import DatasetSchema, SemVer

from schema_api.models import ChangelogItem

CHANGES_DIR = "tmp/changes/"


class Command(BaseCommand):
    help = "Write updates to Changelog table  for datasets from Amsterdam Schema."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--start_commit", nargs="*", help="Commit to start generating updates from."
        )
        parser.add_argument(
            "--end_commit",
            nargs="*",
            default=["HEAD"],
            help="Last commit to generate updates from.",
        )

    def handle(self, *args, **options):
        try:
            # Define start and end commit (if provided)
            if options["start_commit"]:
                print("Using provided start commit")
                start_commit = options["start_commit"][0]
            else:
                start_commit = _get_most_recent_commit()

            end_commit = options["end_commit"][0]

            # Clone Amsterdam Schema repo and fetch all commits into master
            subprocess.run(  # noqa: S603
                [
                    "bash",
                    "schema_api/scripts/clone_ams_schema.sh",
                    start_commit,
                    end_commit,
                ],
                check=True,
            )

            # Write updates to Changelog table
            extend_changelog_table()
        except subprocess.CalledProcessError:
            self.stdout.write(
                "Something went wrong with scripts/clone_ams_schema.sh, "
                "tmp folder will be removed. Please run ./manage.py changelog again. "
            )
            dir_path = os.path.join(os.getcwd(), "tmp")
            shutil.rmtree(dir_path)


def _get_most_recent_commit() -> str:
    """
    Gets most recent commit from the db table as a starting point
    to generate new updates from. Use the hard coded commit when
    running this command when changelog table is empty.
    """
    commits = ChangelogItem.objects.order_by("-committed_at")
    if commits:
        print("Using start commit from the db.")
        return commits[0].commit_hash
    start_commit = "418e137ff39c1d0ef9e224067627fe300ff9f4a1"
    print(f"Using fixed start commit: {start_commit}")
    return start_commit


def get_most_recent_commit():
    commits = ChangelogItem.objects.order_by("-committed_at")
    if commits:
        return commits[0].commit_hash
    return "306da010dca57c4828b7917e88089aea279452a0"


def extend_changelog_table():
    """
    Main function: writes changelog updates for all commits into Amsterdam Schema
    """

    # Load all commits and loop through them to extract info
    commits = _load_changelog_commits()

    # TODO: maybe there is a way to exit the command on this condition,
    # instead of this if/else structure?
    if len(commits) < 2:
        print("No new commits to extract updates from. Exiting command now.")

    else:
        print(f"Fetched {len(commits)} new commits.")

        base_commit = ""
        for update_commit in commits:
            if base_commit:
                print("****************************")
                print(f"Base commit: {base_commit}")
                print(f"Compare commit: {update_commit}")
                print()

                # Extract changelog updates from update commit
                process_commit(base_commit, update_commit)

                # Remove archived repos of commits
                dir_path = os.path.join(os.getcwd(), "tmp/changes")
                for commit_dir in os.listdir(dir_path):
                    full_commit_dir = os.path.join(dir_path, commit_dir)
                    shutil.rmtree(full_commit_dir)

            # Update commit will be base for next commit
            base_commit = update_commit

    # Remove the whole tmp folder
    dir_path = os.path.join(os.getcwd(), "tmp")
    shutil.rmtree(dir_path)


def _load_changelog_commits():
    """Load historical commits into master branch of Amsterdam Schema"""

    with open("tmp/commits.txt") as f:
        return [commit.strip("\n") for commit in f.readlines()]


def process_commit(base_commit, update_commit):
    """
    Check out 2 commits, extract the differences and write updates to Changelog table.
    """
    args = [str(base_commit), str(update_commit)]
    # Checkout the repo for both commits and return the commit timestamp
    output = subprocess.run(  # noqa: S603
        ["bash", "schema_api/scripts/checkout_commits.sh", *args],
        check=True,
        capture_output=True,
        text=True,
    )

    # Save the date
    timestamp = output.stdout.strip()

    # Extract differences between schemas
    dataset_diffs = compare_schemas(base_commit, update_commit)

    for ds in dataset_diffs:
        db_updates = dataset_diffs[ds]
        if db_updates:
            print(
                f"Adding {len(db_updates)} changelog update(s) for dataset {ds.id} to database..."
            )
        for update in db_updates:

            # Add commit hash and commit timestamp
            update["commit_hash"] = update_commit
            update["committed_at"] = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc
            )

            # Create db instance of update (only allow unique entries)
            try:
                item = ChangelogItem(**update)
                print(f"* {item}")
                item.save()
            except IntegrityError:
                print(f"* {update} already exists in database.")
                # Or probably log


def compare_schemas(base_commit: str, update_commit: str) -> dict[str:list]:
    """
    Extract DeepDiff differences between 2 commits for all dataset schemas.
    """

    base_path = CHANGES_DIR + base_commit + "/datasets"
    update_path = CHANGES_DIR + update_commit + "/datasets"

    base_schema = get_schema_loader(base_path).get_all_datasets()
    update_schema = get_schema_loader(update_path).get_all_datasets()

    dataset_diffs = {}

    # Extract diffs for all datasets
    for id in update_schema:
        update_ds = update_schema[id]

        # Check for diffs in existing datasets
        if id in base_schema:
            base_ds = base_schema[id]

            # Extract changelog updates from diffs
            diffs = base_ds.get_diffs(update_ds)

            if diffs:
                db_updates = extract_diffs_for_dataset(diffs, update_ds)
                dataset_diffs[update_ds] = db_updates

        # Also add update for completely new datasets?
        else:
            pass

    return dataset_diffs


def extract_diffs_for_dataset(diffs: dict[str:list], update_ds: DatasetSchema) -> list[dict]:
    """
    Parse DeepDiff output and extract info for Changelog Item instances
    """
    db_updates = []

    # Extract updates for modified tables and dataset lifecycle status updates
    modifications = diffs.get("values_changed", [])
    for field in modifications:
        field_list = _parse_deepdiff_field(field)

        # *** UPDATE TABLE UPDATE ***
        if "tables" in field_list and field_list[-1] == "version":

            # Only handle minor table updates
            version_update = modifications[field]
            old_v = SemVer(version_update["old_value"])
            new_v = SemVer(version_update["new_value"])

            # E.g. old_v = 1.0.0 and new_v = 1.1.0
            if new_v.major == old_v.major and new_v.minor > old_v.minor:
                change_dict = _extract_table_info(field_list, update_ds)
                change_dict["label"] = "update"
                db_updates.append(change_dict)

        # *** UPDATE LIFECYCLE STATUS ***
        if field_list[-1] == "lifecycleStatus":
            change_dict = _extract_dataset_info(field_list, update_ds)
            change_dict["label"] = "status"
            db_updates.append(change_dict)

    # Extract updates for added tables and added dataset versions
    additions = _get_create_updates(diffs)
    for field in additions:
        change_dict = {}
        field_list = _parse_deepdiff_field(field)

        # *** CREATE TABLE ***
        if field_list[-2] == "tables":
            change_dict = _extract_table_info(field_list, update_ds)
            change_dict["label"] = "create"
            db_updates.append(change_dict)

        # *** CREATE DATASET VERSION ***
        if field_list[-2] == "versions":
            change_dict = _extract_dataset_info(field_list, update_ds)
            change_dict["label"] = "create"
            db_updates.append(change_dict)

    return db_updates


def _load_changelog_commits():
    """
    Load historical commits into master branch of Amsterdam Schema
    """
    with open("tmp/commits.txt") as f:
        return [commit.strip("\n") for commit in f.readlines()]


def _parse_deepdiff_field(field: str) -> list[str]:
    """
    Parses a string of dict keys into a list of dict keys
    """

    # Clean off DeepDiff prefix 'root'
    if field.startswith("root"):
        field = field[4:]
    field = field.replace("]", "").replace("'", "")
    field_list = field.split("[")
    return [value for value in field_list if value]


def _extract_table_info(field_list: list, update_ds: DatasetSchema) -> dict[str:str]:
    """
    Extract necessary fields for a changelog table item
    """
    # Get table id (name)
    change_dict = {}
    tables_index = field_list.index("tables")
    table_index = int(field_list[tables_index + 1])
    table_id = update_ds.tables[table_index].id

    # Get dataset vmajor
    ds_vmajor = field_list[tables_index - 1]

    # Get lifecycle status of DatasetVersion
    dataset_vmajor = update_ds.get_version(ds_vmajor)
    dataset_id = update_ds.id
    change_dict["dataset_id"] = dataset_id
    change_dict["status"] = dataset_vmajor.lifecycle_status.value

    # Construct object id
    object_id = f"{dataset_id}/{ds_vmajor}/{table_id}"
    change_dict["object_id"] = object_id

    return change_dict


def _extract_dataset_info(field_list: list, update_ds: DatasetSchema) -> dict[str:str]:
    """
    Extract necessary fields for a changelog table item
    """
    change_dict = {}
    versions_index = field_list.index("versions")
    ds_vmajor = field_list[versions_index + 1]

    # Get lifecycle status of DatasetVersion
    dataset_vmajor = update_ds.get_version(ds_vmajor)
    dataset_id = update_ds.id
    change_dict["dataset_id"] = dataset_id
    change_dict["status"] = dataset_vmajor.lifecycle_status.value

    # Construct object id
    object_id = f"{dataset_id}/{ds_vmajor}"
    change_dict["object_id"] = object_id

    return change_dict


def _extract_dataset_info(field_list: list, update_ds: DatasetSchema) -> dict[str:str]:
    """
    Extract necessary fields for a changelog table item
    """
    change_dict = {}
    versions_index = field_list.index("versions")
    ds_vmajor = field_list[versions_index + 1]

    # Get lifecycle status of DatasetVersion
    dataset_vmajor = update_ds.get_version(ds_vmajor)
    dataset_id = update_ds.id
    change_dict["dataset_id"] = dataset_id
    change_dict["status"] = dataset_vmajor.lifecycle_status.value

    # Construct object id
    object_id = f"{dataset_id}/{ds_vmajor}"
    change_dict["object_id"] = object_id

    return change_dict


def _extract_dataset_info(field_list: list, update_ds: DatasetSchema) -> dict[str:str]:
    """
    Extract necessary fields for a changelog table item
    """
    change_dict = {}
    versions_index = field_list.index("versions")
    ds_vmajor = field_list[versions_index + 1]

    # Get lifecycle status of DatasetVersion
    dataset_vmajor = update_ds.get_version(ds_vmajor)
    dataset_id = update_ds.id
    change_dict["dataset_id"] = dataset_id
    change_dict["status"] = dataset_vmajor.lifecycle_status.value

    # Construct object id
    object_id = f"{dataset_id}/{ds_vmajor}"
    change_dict["object_id"] = object_id

    return change_dict


def _extract_dataset_info(field_list: list, update_ds: DatasetSchema) -> dict[str:str]:
    """
    Extract necessary fields for a changelog table item
    """
    change_dict = {}
    versions_index = field_list.index("versions")
    ds_vmajor = field_list[versions_index + 1]

    # Get lifecycle status of DatasetVersion
    dataset_vmajor = update_ds.get_version(ds_vmajor)
    dataset_id = update_ds.id
    change_dict["dataset_id"] = dataset_id
    change_dict["status"] = dataset_vmajor.lifecycle_status.value

    # Construct object id
    object_id = f"{dataset_id}/{ds_vmajor}"
    change_dict["object_id"] = object_id

    return change_dict


def _get_create_updates(diffs: dict[str:list]) -> list[str]:
    """
    Add all types of addition updates (and addition updates only) from DeepDiff to one list
    """
    additions = []
    for key, value in diffs.items():
        if "added" in key:
            for key in value:
                additions.append(key)
    return additions
