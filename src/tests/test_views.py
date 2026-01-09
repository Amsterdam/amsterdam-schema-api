from datetime import date

import pytest
from django.urls import reverse
from django.utils.dateparse import parse_datetime


def test_root_view(client):
    response = client.get("/status/")
    assert response.status_code == 200
    assert response.json() == {"status": "online"}


@pytest.mark.django_db
class TestDatasetViews:

    def test_dataset_list(self, client):
        response = client.get(reverse("dataset-list"))
        assert response.status_code == 200

    def test_dataset_detail(self, client, bomen_dataset):
        response = client.get(
            reverse("dataset-detail", kwargs={"name": "bomen"}),
        )
        assert response.status_code == 200
        assert response.data["id"] == "bomen"

    def test_dataset_detail_filter_on_tables(self, client, gebieden_dataset):
        response = client.get(
            reverse(
                "dataset-detail",
                kwargs={"name": "gebieden"},
                query={"tables": ["bouwblokken", "buurten", "wijken"]},
            ),
        )
        assert response.status_code == 200
        table_ids = {t["id"] for t in response.data["versions"]["v1"]["tables"]}
        assert table_ids == {"bouwblokken", "buurten", "wijken"}

    def test_dataset_detail_filter_on_tables_ignores_non_existent(self, client, gebieden_dataset):
        response = client.get(
            reverse(
                "dataset-detail",
                kwargs={"name": "gebieden"},
                query={"tables": ["bouwblokken", "buurten", "wijken", "huisnummerplaten"]},
            ),
        )
        assert response.status_code == 200
        table_ids = {t["id"] for t in response.data["versions"]["v1"]["tables"]}
        assert table_ids == {"bouwblokken", "buurten", "wijken"}

    def test_dataset_version(self, client, bomen_dataset):
        response = client.get(
            reverse("dataset-version", kwargs={"name": "bomen", "vmajor": "v1"}),
        )
        assert response.status_code == 200
        assert response.data["version"] == "1.3.5"

    def test_dataset_version_filter_on_tables(self, client, gebieden_dataset):
        response = client.get(
            reverse(
                "dataset-version",
                kwargs={"name": "gebieden", "vmajor": "v1"},
                query={"tables": ["bouwblokken", "buurten", "wijken"]},
            ),
        )
        assert response.status_code == 200
        table_ids = {t["id"] for t in response.data["tables"]}
        assert table_ids == {"bouwblokken", "buurten", "wijken"}

    def test_dataset_version_not_found(self, client, bomen_dataset):
        response = client.get(
            reverse("dataset-version", kwargs={"name": "bomen", "vmajor": "v3"}),
        )
        assert response.status_code == 404
        assert (
            response.data["detail"]
            == "Version v3 not found in dataset bomen. Available versions are ['v1', 'v2']"
        )

    def test_dataset_table(self, client, bomen_dataset):
        response = client.get(
            reverse(
                "dataset-table",
                kwargs={"name": "bomen", "vmajor": "v1", "table_id": "groeiplaatsmedebeheer"},
            ),
        )
        assert response.status_code == 200
        assert response.data["id"] == "groeiplaatsmedebeheer"

    def test_dataset_table_not_found(self, client, bomen_dataset):
        response = client.get(
            reverse(
                "dataset-table",
                kwargs={"name": "bomen", "vmajor": "v1", "table_id": "groeiplaats"},
            ),
        )
        assert response.status_code == 404
        assert response.data["detail"] == "Table 'groeiplaats' not found."

    def test_dataset_scope_access(self, client, bomen_dataset, scope_fixture):
        response = client.get(
            reverse(
                "dataset-detail",
                kwargs={
                    "name": "bomen",
                },
                query={
                    "scopes": "fp_mdw",
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["versions"]["v1"]["tables"][0]["schema"]["properties"]

    def test_dataset_scope_no_access(self, client, bomen_dataset, scope_fixture):
        response = client.get(
            reverse(
                "dataset-detail",
                kwargs={
                    "name": "bomen",
                },
                query={
                    "scopes": "openbaar",
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["versions"]["v1"]["tables"][0]["schema"]["properties"] == {}

    def test_dataset_multiple_scope_access(self, client, bomen_dataset, scope_fixture):
        response = client.get(
            reverse(
                "dataset-detail",
                kwargs={
                    "name": "bomen",
                },
                query={
                    "scopes": ["openbaar", "fp_mdw"],
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["versions"]["v1"]["tables"][0]["schema"]["properties"]

    def test_dataset_scope_version_access(self, client, bomen_dataset, scope_fixture):
        response = client.get(
            reverse(
                "dataset-version",
                kwargs={
                    "name": "bomen",
                    "vmajor": "v1",
                },
                query={
                    "scopes": "fp_mdw",
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["tables"][0]["schema"]["properties"]

    def test_dataset_scope_version_no_access(self, client, bomen_dataset, scope_fixture):
        response = client.get(
            reverse(
                "dataset-version",
                kwargs={
                    "name": "bomen",
                    "vmajor": "v1",
                },
                query={
                    "scopes": "openbaar",
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["tables"][0]["schema"]["properties"] == {}

    def test_dataset_scope_table_access(self, client, bomen_dataset, scope_fixture):
        response = client.get(
            reverse(
                "dataset-table",
                kwargs={
                    "name": "bomen",
                    "vmajor": "v1",
                    "table_id": "groeiplaatsmedebeheer",
                },
                query={
                    "scopes": "fp_mdw",
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["schema"]["properties"]

    def test_dataset_scope_table_no_access(self, client, bomen_dataset, scope_fixture):
        response = client.get(
            reverse(
                "dataset-table",
                kwargs={
                    "name": "bomen",
                    "vmajor": "v1",
                    "table_id": "groeiplaatsmedebeheer",
                },
                query={
                    "scopes": "openbaar",
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["schema"]["properties"] == {}

    def test_dataset_scope_table_field_access(self, client, bomen_dataset, scope_fixture):
        response = client.get(
            reverse(
                "dataset-table",
                kwargs={
                    "name": "bomen",
                    "vmajor": "v2",
                    "table_id": "groeiplaatsmedebeheer",
                },
                query={
                    "scopes": "fp_mdw",
                },
            ),
        )
        assert response.status_code == 200
        assert "guid" in response.data["schema"]["properties"]

    def test_dataset_scope_table_field_no_access(self, client, bomen_dataset, scope_fixture):
        response = client.get(
            reverse(
                "dataset-table",
                kwargs={
                    "name": "bomen",
                    "vmajor": "v2",
                    "table_id": "groeiplaatsmedebeheer",
                },
                query={
                    "scopes": "openbaar",
                },
            ),
        )
        assert response.status_code == 200
        assert "guid" not in response.data["schema"]["properties"]


@pytest.mark.django_db
class TestScopeViews:
    def test_scope_listview(self, client, scope_fixture):
        response = client.get(reverse("scope-list"))
        assert response.status_code == 200
        assert response.data["count"] == 2

    def test_scope_detailview(self, client, scope_fixture):
        response = client.get(
            reverse("scope-detail", kwargs={"pk": "fp_mdw"}),
        )
        assert response.status_code == 200
        assert response.data["id"] == "FP/MDW"


@pytest.mark.django_db
class TestPublisherViews:
    def test_publisher_listview(self, client, publisher_fixture):
        response = client.get(reverse("publisher-list"))
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_publisher_detailview(self, client, publisher_fixture):
        response = client.get(
            reverse("publisher-detail", kwargs={"pk": "benk"}),
        )
        assert response.status_code == 200
        assert response.data["id"] == "BENK"


@pytest.mark.django_db
class TestProfileViews:
    def test_profile_listview(self, client, profile_fixture):
        response = client.get(reverse("profile-list"))
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_profile_detailview(self, client, profile_fixture):
        response = client.get(
            reverse("profile-detail", kwargs={"pk": "brkdataportaalgebruiker"}),
        )
        assert response.status_code == 200
        assert response.data["id"] == "brkdataportaalgebruiker"


@pytest.mark.django_db
class TestChangelogViews:
    def test_changelog_list_view(self, client, changelog_items):
        response = client.get(reverse("changelog-list"))
        assert response.status_code == 200
        assert response.data["count"] == 3
        response = response.data["results"][0]
        assert response["object_id"] == "hrKvk/v1/functievervullingen"
        assert response["description"] == "Update table hrKvk/v1/functievervullingen."

    def test_changelog_detail_view(self, client, changelog_items):
        response = client.get(
            reverse(
                "changelog-detail",
                kwargs={"pk": "1"},
            )
        )
        assert response.status_code == 200
        assert response.data["object_id"] == "hrKvk/v1/functievervullingen"
        assert response.data["description"] == "Update table hrKvk/v1/functievervullingen."

    def test_changelog_list_from_date(self, client, changelog_items):
        from_date = "2026-01-01"

        response = client.get(
            reverse(
                "changelog-list",
                query={
                    "from_date": from_date,
                },
            )
        )
        assert response.status_code == 200
        assert response.data["count"] == 2

        iso_date = date.fromisoformat(from_date)
        for item in response.data["results"]:
            item_date = parse_datetime(item["committed_at"])
            assert item_date.date() == iso_date

    def test_changelog_list_view_dataset(self, client, changelog_items):
        response = client.get(
            reverse(
                "changelog-dataset",
                kwargs={"dataset": "hrKvk"},
            )
        )
        assert response.status_code == 200
        assert response.data["count"] == 2
        for item in response.data["results"]:
            assert item["dataset_id"] == "hrKvk"

    def test_changelog_list_view_dataset_from_date(self, client, changelog_items):
        from_date = "2026-01-01"
        response = client.get(
            reverse(
                "changelog-dataset",
                kwargs={"dataset": "hrKvk"},
                query={
                    "from_date": from_date,
                },
            )
        )
        assert response.status_code == 200
        assert response.data["count"] == 1

        iso_date = date.fromisoformat(from_date)
        for item in response.data["results"]:
            assert item["dataset_id"] == "hrKvk"
            item_date = parse_datetime(item["committed_at"])
            assert item_date.date() == iso_date
